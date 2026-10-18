"""
SRA 2025 - TP4: todas las simulaciones del trabajo, automatizadas con spicelib.

Toma los esquemáticos base de LTspice, los convierte en netlist, cambia los valores desde
Python y corre LTspice en modo batch. Los resultados se guardan en TP4/resultados/*.pkl
para que graficos_tp4.py genere las figuras sin volver a simular.

Esquemáticos base (los únicos que hay que dibujar):
    sim/filtro_ci_ideal.asc       Sallen-Key de componentes iguales, AO ideal
    sim/filtro_ci_lm324.asc       el mismo con LM324
    sim/filtro_ug_ideal.asc       Sallen-Key de ganancia unitaria, AO ideal
    oscilador/sim/oscilador_wien.asc

Ejecutar:  python TP4/scripts/simular_tp4.py            (todo, ~3 min)
           python TP4/scripts/simular_tp4.py mc osc     (solo algunos estudios)
"""
import pickle
import re
import sys
import time

import numpy as np

from spice_tp4 import TP4, eje, leer_ac, leer_tran, netlist_desde_asc, nuevo_runner
from spicelib import RawRead
from spicelib.log.ltsteps import LTSpiceLogReader

RES = TP4 / "resultados"
SEMILLA = 2026
N_MC = 500

# Componentes pasivos de cada topología (nombres de la netlist normalizada)
PASIVOS_CI = ["RA", "RB", "R2", "C1", "C2", "RK1", "RK2", "RC", "RD", "C3", "C4", "R3", "R4", "RK3", "RK4"]
PASIVOS_UG = ["RA", "RB", "R2", "C1", "C2", "C3", "C4", "R3", "R4"]

# Signo del desvío de cada componente que AUMENTA el ancho de banda wp/Qp de su etapa
# (opuesto al signo de la sensibilidad S^(wp/Qp); ver diseno_tp4.py). Rc y Rd no afectan la forma.
SIGNO_BW_CI = {"RA": -1, "RB": -1, "R2": +1, "C1": -1, "C2": +1, "RK1": +1, "RK2": -1,
               "C3": +1, "C4": -1, "R3": +1, "R4": -1, "RK3": +1, "RK4": -1}

runner = nuevo_runner(1)


def guardar(nombre, datos):
    with open(RES / f"{nombre}.pkl", "wb") as f:
        pickle.dump(datos, f)
    print(f"   -> resultados/{nombre}.pkl")


def nominales(ed, nombres):
    return {c: ed.get_component_floatvalue(c) for c in nombres}


def quitar(ed, patron):
    """Borra las directivas que coinciden con el patrón, solo si existen
    (spicelib informa un error cuando no encuentra ninguna)."""
    regex = re.compile(patron, re.IGNORECASE)
    lineas = (getattr(x, "obj", x) for x in ed.netlist)
    if any(isinstance(x, str) and regex.match(x) for x in lineas):
        ed.remove_Xinstruction(patron)


def fijar_analisis(ed, *instrucciones):
    """Reemplaza el análisis (.ac/.tran) y agrega directivas."""
    for patron in (r"\.ac\s", r"\.tran\s", r"\.step\s", r"\.save\s"):
        quitar(ed, patron)
    for ins in instrucciones:
        ed.add_instruction(ins)


def correr_lote(ed, valores, nombre, analisis, guardar_trazas=("V(out)",), meas=("gmax", "gmin", "g200", "g5k")):
    """Corre N simulaciones en una sola ejecución de LTspice.
    valores = {componente: array de N valores}. Cada componente pasa a valer {table(run, 1, v1, 2, v2, ...)}."""
    n = len(next(iter(valores.values())))
    for comp, v in valores.items():
        ed.set_component_value(comp, "{table(run," + ",".join(f"{i + 1},{x:.7g}" for i, x in enumerate(v)) + ")}")
    fijar_analisis(ed, analisis, f".step param run 1 {n} 1", ".save " + " ".join(guardar_trazas))
    t0 = time.time()
    raw, log = runner.run_now(ed, run_filename=f"{nombre}.net", timeout=3600)
    if raw is None:
        raise RuntimeError(f"LTspice no generó resultados para {nombre}; ver resultados/corridas/{nombre}.log")
    r = RawRead(str(raw))
    x = eje(r)
    trazas = {t: np.array([r.get_trace(t).get_wave(i) for i in range(n)]) for t in guardar_trazas}
    lr = LTSpiceLogReader(str(log))
    m = {k: a_db(lr.get_measure_values_at_steps(k, None), k) for k in meas}
    print(f"   {nombre}: {n} corridas en {time.time() - t0:.1f} s")
    return x, trazas, m


def a_db(valores, nombre):
    """LTspice informa las .meas de magnitud AC en dB, pero spicelib las devuelve como número complejo lineal.
    Las mediciones de transitorio (frec, vmax, ...) se dejan como están."""
    v = np.array([complex(x) for x in valores])
    return 20*np.log10(np.abs(v)) if nombre.startswith("g") else np.real(v)


# ----------------------------------------------------------------------------- polos analíticos
def polos_ci(v):
    """Coeficientes del denominador de cada etapa de componentes iguales (arrays sobre las corridas)."""
    R1 = v["RA"]*v["RB"]/(v["RA"] + v["RB"])
    k1 = 1 + v["RK2"]/v["RK1"]
    k3 = 1 + v["RK4"]/v["RK3"]
    bw_pb = 1/(R1*v["C1"]) + 1/(v["R2"]*v["C1"]) + (1 - k1)/(v["R2"]*v["C2"])
    bw_pa = 1/(v["R4"]*v["C3"]) + 1/(v["R4"]*v["C4"]) + (1 - k3)/(v["R3"]*v["C3"])
    w_pb = 1/np.sqrt(R1*v["R2"]*v["C1"]*v["C2"])
    w_pa = 1/np.sqrt(v["R3"]*v["R4"]*v["C3"]*v["C4"])
    return dict(w_pb=w_pb, q_pb=w_pb/bw_pb, w_pa=w_pa, q_pa=w_pa/bw_pa, k1=k1, k3=k3,
                inestable=(bw_pb <= 0) | (bw_pa <= 0))


def polos_ug(v):
    R1 = v["RA"]*v["RB"]/(v["RA"] + v["RB"])
    bw_pb = 1/(R1*v["C1"]) + 1/(v["R2"]*v["C1"])
    bw_pa = 1/(v["R3"]*v["C3"]) + 1/(v["R3"]*v["C4"])      # R3 a masa, R4 a la salida (k = 1)
    w_pb = 1/np.sqrt(R1*v["R2"]*v["C1"]*v["C2"])
    w_pa = 1/np.sqrt(v["R3"]*v["R4"]*v["C3"]*v["C4"])
    return dict(w_pb=w_pb, q_pb=w_pb/bw_pb, w_pa=w_pa, q_pa=w_pa/bw_pa,
                inestable=(bw_pb <= 0) | (bw_pa <= 0))


# ----------------------------------------------------------------------------- estudios
def estudio_nominal():
    print("1.3 / agregados 1 y 3: simulaciones nominales")
    for asc, nombre, trazas in (("sim/filtro_ci_ideal.asc", "nominal_ci_ideal", ("V(in)", "V(pb)", "V(pa_in)", "V(out)")),
                                ("sim/filtro_ci_lm324.asc", "nominal_ci_lm324", ("V(in)", "V(pb)", "V(pa_in)", "V(out)")),
                                ("sim/filtro_ug_ideal.asc", "nominal_ug_ideal", ("V(in)", "V(pb)", "V(out)"))):
        ed = netlist_desde_asc(TP4/asc, nombre)
        hasta = "1Meg" if "lm324" in nombre else "100k"
        fijar_analisis(ed, f".ac dec 500 10 {hasta}")
        raw, log = runner.run_now(ed, run_filename=f"{nombre}.net")
        f, tr = leer_ac(raw, trazas)
        lr = LTSpiceLogReader(str(log))
        m = {k: float(a_db([lr.get_measure_value(k)], k)[0]) for k in ("gmax", "gmin", "g200", "g5k")}
        print(f"   {nombre}: rizado {m['gmax'] - m['gmin']:.3f} dB, A200 {-m['g200']:.2f} dB, A5k {-m['g5k']:.2f} dB")
        guardar(nombre, dict(f=f, trazas=tr, meas=m))


def estudio_peor_caso():
    print("1.5: peor desviación (tolerancia 10 %)")
    ed = netlist_desde_asc(TP4/"sim/filtro_ci_ideal.asc", "peor_caso")
    nom = nominales(ed, list(SIGNO_BW_CI))
    tol = 0.10
    s = np.array([-1.0, 0.0, 1.0])
    casos = {
        # todos los componentes en el mismo sentido: corre la frecuencia del polo
        "wp": {c: v*(1 + s*tol) for c, v in nom.items()},
        # cada componente en el sentido que aumenta (s=+1) o reduce (s=-1) el ancho de banda
        "bw": {c: v*(1 + s*tol*SIGNO_BW_CI[c]) for c, v in nom.items()},
    }
    salida = {}
    for clave, valores in casos.items():
        f, tr, m = correr_lote(ed, valores, f"peor_caso_{clave}", ".ac dec 500 10 100k", ("V(out)",))
        salida[clave] = dict(f=f, out=tr["V(out)"], meas=m, s=s, valores=valores, polos=polos_ci(valores))
        p = salida[clave]["polos"]
        for i, si in enumerate(s):
            print(f"     s={si:+.0f}: Qpb={p['q_pb'][i]:+.2f} Qpa={p['q_pa'][i]:+.2f} k={p['k1'][i]:.3f}"
                  f"{'  INESTABLE' if p['inestable'][i] else ''}")
    guardar("peor_caso", salida)

    print("   transitorio del caso inestable (s = -1, ancho de banda)")
    ed = netlist_desde_asc(TP4/"sim/filtro_ci_ideal.asc", "inestable")
    for c, v in nom.items():
        ed.set_component_value(c, f"{v*(1 - tol*SIGNO_BW_CI[c]):.7g}")
    fijar_analisis(ed, ".tran 0 20m 0 2u", ".ic V(pb)=1m")
    quitar(ed, r"\.meas")
    raw, _ = runner.run_now(ed, run_filename="inestable.net")
    t, tr = leer_tran(raw, ("V(out)",))
    guardar("inestable", dict(t=t, out=tr["V(out)"]))


def estudio_montecarlo():
    print("1.6 / agregados 1 y 2: Montecarlo (distribución uniforme)")
    rng = np.random.default_rng(SEMILLA)
    salida = {}
    for asc, topo, pasivos, polos, tols in (("sim/filtro_ci_ideal.asc", "ci", PASIVOS_CI, polos_ci, (0.10, 0.05, 0.01)),
                                            ("sim/filtro_ug_ideal.asc", "ug", PASIVOS_UG, polos_ug, (0.10, 0.05, 0.01))):
        ed = netlist_desde_asc(TP4/asc, f"mc_{topo}")
        nom = nominales(ed, pasivos)
        for tol in tols:
            valores = {c: v*(1 + tol*rng.uniform(-1, 1, N_MC)) for c, v in nom.items()}
            f, tr, m = correr_lote(ed, valores, f"mc_{topo}_{round(tol*100):02d}", ".ac dec 200 10 100k")
            p = polos(valores)
            rip = m["gmax"] - m["gmin"]
            a200, a5k = m["gmax"] - m["g200"], m["gmax"] - m["g5k"]
            estable = ~p["inestable"]
            cumple = (rip <= 0.25) & (a200 >= 30) & (a5k >= 30) & estable
            print(f"     tol {tol*100:4.1f} %: rizado medio {rip[estable].mean():.2f} dB, inestables {p['inestable'].sum()},"
                  f" cumplen {100*cumple.mean():.1f} %")
            salida[(topo, tol)] = dict(f=f, out_db=(20*np.log10(np.abs(tr["V(out)"]))).astype(np.float32),
                                       meas=m, valores=valores, polos=p, rizado=rip, a200=a200, a5k=a5k,
                                       cumple=cumple)
    guardar("montecarlo", salida)


def estudio_oscilador():
    print("Ejercicio adicional: oscilador de Wien")
    salida = {}

    def ajustar_thd(t, v, f0, n=9):
        A = np.column_stack([np.ones_like(t)] + [fn(2*np.pi*k*f0*t) for k in range(1, n + 1)
                                                 for fn in (np.sin, np.cos)])
        c = np.linalg.lstsq(A, v, rcond=None)[0]
        h = np.hypot(c[1::2], c[2::2])
        return h, np.sqrt((h[1:]**2).sum())/h[0]

    def analizar(t, v):
        orden = np.argsort(t); t, v = t[orden], v[orden]
        m = t > 30e-3
        cr = t[1:][(v[:-1] < 0) & (v[1:] >= 0) & (t[1:] > 30e-3)]
        f0 = (len(cr) - 1)/(cr[-1] - cr[0])
        h, thd = ajustar_thd(t[m], v[m], f0)
        return dict(t=t, v=v, f=f0, vp=v[m].max(), armonicos=h, thd=thd)

    # Barrido de R (serie E96) para ajustar la frecuencia
    R_E96 = np.array([7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09])*1e3
    ed = netlist_desde_asc(TP4/"oscilador/sim/oscilador_wien.asc", "osc_barrido")
    quitar(ed, r"\.param")
    ed.set_parameter("C", "1.5n")
    fijar_analisis(ed, ".tran 0 40m 0 0.2u", ".step param R list " + " ".join(f"{r:.0f}" for r in R_E96),
                   ".save V(out)")
    t0 = time.time()
    raw, log = runner.run_now(ed, run_filename="osc_barrido.net")
    r = RawRead(str(raw))
    barrido = []
    for i, R in enumerate(R_E96):
        res = analizar(np.abs(eje(r, i)), np.real(r.get_trace("V(out)").get_wave(i)))
        barrido.append(dict(R=R, f=res["f"], thd=res["thd"], vp=res["vp"]))
        print(f"     R = {R/1e3:.2f}k: f = {res['f']:.1f} Hz ({res['f'] - 12e3:+.1f} Hz), THD {100*res['thd']:.2f} %")
    print(f"   barrido en {time.time() - t0:.1f} s")
    salida["barrido"] = barrido
    salida["R_teorico"] = 1/(2*np.pi*12e3*1.5e-9)

    # Diseño final y prueba de slew rate
    for clave, rf1, rf2 in (("final", "15k", "6.8k"), ("slew", "18k", "4.7k")):
        ed = netlist_desde_asc(TP4/"oscilador/sim/oscilador_wien.asc", f"osc_{clave}")
        ed.set_component_value("RF1", rf1)
        ed.set_component_value("RF2", rf2)
        fijar_analisis(ed, ".tran 0 40m 0 0.2u")
        raw, _ = runner.run_now(ed, run_filename=f"osc_{clave}.net")
        t, tr = leer_tran(raw, ("V(out)",))
        res = analizar(t, tr["V(out)"])
        orden = np.argsort(t)
        dv = np.diff(tr["V(out)"][orden])/np.diff(t[orden])
        res["dvdt_max"] = np.abs(dv[t[orden][1:] > 30e-3]).max()
        salida[clave] = res
        print(f"     {clave}: f = {res['f']:.1f} Hz, Vp = {res['vp']:.2f} V, THD = {100*res['thd']:.2f} %,"
              f" |dV/dt| máx = {res['dvdt_max']*1e-6:.3f} V/us")

    guardar("oscilador", salida)


def estudio_oscilador_mc():
    """Montecarlo de la frecuencia del oscilador: R al 1 %, C al 5 %. Justifica el preset de ajuste."""
    print("Ejercicio adicional: Montecarlo de la frecuencia del oscilador")
    with open(RES / "oscilador.pkl", "rb") as f:
        salida = pickle.load(f)
    rng = np.random.default_rng(SEMILLA)
    ed = netlist_desde_asc(TP4/"oscilador/sim/oscilador_wien.asc", "osc_mc")
    quitar(ed, r"\.meas")
    quitar(ed, r"\.four")
    # 50 ciclos medidos entre 5 y 9 ms (el arranque termina antes de 1 ms)
    ed.add_instruction(".meas TRAN t1 WHEN V(out)=0 RISE=60")
    ed.add_instruction(".meas TRAN t2 WHEN V(out)=0 RISE=110")
    ed.add_instruction(".meas TRAN frec PARAM 50/(t2-t1)")
    n = 100
    valores = {"R1": 8250*(1 + 0.01*rng.uniform(-1, 1, n)), "R2": 8250*(1 + 0.01*rng.uniform(-1, 1, n)),
               "C1": 1.5e-9*(1 + 0.05*rng.uniform(-1, 1, n)), "C2": 1.5e-9*(1 + 0.05*rng.uniform(-1, 1, n))}
    _, _, m = correr_lote(ed, valores, "osc_mc", ".tran 0 10m 0 0.5u", ("V(out)",), meas=("frec",))
    salida["mc"] = dict(valores=valores, f=m["frec"])
    dentro = np.mean(np.abs(m["frec"] - 12e3) <= 100)*100
    print(f"     f = {m['frec'].mean():.0f} ± {m['frec'].std():.0f} Hz (rango {m['frec'].min():.0f}-{m['frec'].max():.0f}),"
          f" dentro de ±100 Hz: {dentro:.0f} %")
    guardar("oscilador", salida)


ESTUDIOS = {"nominal": estudio_nominal, "peor": estudio_peor_caso, "mc": estudio_montecarlo, "osc": estudio_oscilador, "oscmc": estudio_oscilador_mc}

if __name__ == "__main__":
    elegidos = sys.argv[1:] or list(ESTUDIOS)
    t0 = time.time()
    for e in elegidos:
        ESTUDIOS[e]()
    print(f"Listo en {time.time() - t0:.0f} s")
