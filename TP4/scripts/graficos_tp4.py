"""
Genera todas las figuras del informe del TP4 a partir de las simulaciones de LTspice.
Lee TP4/sim/*.raw|.log y TP4/oscilador/sim/*.raw|.log; escribe en TP4/figs/.

Ejecutar:  python TP4/scripts/graficos_tp4.py
"""
from pathlib import Path

import numpy as np
import scipy.signal as sg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ltspice_raw import leer_raw, leer_meas
from diseno_tp4 import num, den, fp, fs, Ap, As

TP4 = Path(__file__).resolve().parents[1]
SIM, OSC, FIGS = TP4 / "sim", TP4 / "oscilador" / "sim", TP4 / "figs"
FIGS.mkdir(exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.3})

AZUL, NARANJA, VERDE, ROJO, GRIS = "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "0.4"


def db(x):
    return 20*np.log10(np.abs(x))


def fase(x):
    return np.unwrap(np.angle(x))*180/np.pi


def plantilla(ax, ganancia=True, ymin=-80, ymax=10):
    """Dibuja la plantilla de requerimientos (zonas prohibidas sombreadas)."""
    s = 1 if ganancia else -1
    kw = dict(color=ROJO, alpha=0.12, lw=0)
    ax.fill_between([1, fs[0]], s*-As, s*ymax if ganancia else -ymax*s, **kw)
    ax.fill_between([fs[1], 1e7], s*-As, s*ymax if ganancia else -ymax*s, **kw)
    ax.fill_between(fp, s*-Ap, s*ymin if ganancia else -ymin*s, **kw)
    ax.set_xscale("log")
    ax.set_xlabel("Frecuencia [Hz]")
    ax.set_ylabel("Ganancia [dB]" if ganancia else "Atenuación [dB]")


def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(FIGS / nombre, dpi=200)
    plt.close(fig)
    print("  ", nombre)


def stats_mc(nombre):
    m = leer_meas(SIM / f"{nombre}.log")
    rip = m["gmax"] - m["gmin"]
    a200, a5k = m["gmax"] - m["g200"], m["gmax"] - m["g5k"]
    ok = (rip <= Ap) & (a200 >= As) & (a5k >= As)
    return dict(rip=rip, a200=a200, a5k=a5k, ok=ok)


print("Figuras:")

# ---------------------------------------------------------------- aproximación
f = np.logspace(1, 5, 4000)
T = sg.freqs(num, den, 2*np.pi*f)[1]
fig, ax = plt.subplots(figsize=(8, 4.2))
plantilla(ax)
ax.plot(f, db(T), color=AZUL, lw=1.8, label="Aproximación de Chebyshev ($n = 2$)")
ax.set_xlim(10, 1e5); ax.set_ylim(-80, 10); ax.legend(loc="lower center")
guardar(fig, "aproximacion_chebyshev.png")

# ---------------------------------------------------------------- 1.3 nominal (AO ideal)
_, d, _ = leer_raw(SIM / "filtro_ci_ideal.raw")
f = d["frequency"][0].real
vin, vpb, vpa, vout = (d[k][0] for k in ("v(in)", "v(pb)", "v(pa_in)", "v(out)"))
T = sg.freqs(num, den, 2*np.pi*f)[1]

etapas = [(vpb/vin, "Etapa 1: pasabajos", AZUL),
          (vpa/vpb, "Ajuste de ganancia (divisor + seguidor)", GRIS),
          (vout/vpa, "Etapa 2: pasaaltos", VERDE)]
for x, nombre, color in etapas:
    archivo = {"Etapa 1: pasabajos": "sim_ci_etapa_pb.png", "Etapa 2: pasaaltos": "sim_ci_etapa_pa.png"}.get(nombre)
    if not archivo:
        continue
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)
    a1.semilogx(f, db(x), color=color); a1.set_ylabel("Módulo [dB]"); a1.set_title(nombre)
    a2.semilogx(f, fase(x), color=color); a2.set_ylabel("Fase [°]"); a2.set_xlabel("Frecuencia [Hz]")
    a1.set_xlim(10, 1e5)
    guardar(fig, archivo)

fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6.5), sharex=True)
plantilla(a1)
a1.plot(f, db(T), color=ROJO, lw=3, alpha=0.35, label="Teórica")
a1.plot(f, db(vout/vin), color=AZUL, label="LTspice: filtro completo")
a1.plot(f, db(vpb/vin), "--", color=NARANJA, lw=1, label="Etapa 1 (pasabajos)")
a1.plot(f, db(vout/vpa), "--", color=VERDE, lw=1, label="Etapa 2 (pasaaltos)")
a1.set_xlim(10, 1e5); a1.set_ylim(-80, 25); a1.legend(loc="lower center", fontsize=8); a1.set_xlabel("")
a2.semilogx(f, fase(T), color=ROJO, lw=3, alpha=0.35, label="Teórica")
a2.semilogx(f, fase(vout/vin), color=AZUL, label="LTspice")
a2.set_ylabel("Fase [°]"); a2.set_xlabel("Frecuencia [Hz]"); a2.legend(fontsize=8)
guardar(fig, "sim_ci_total.png")

fig, ax = plt.subplots(figsize=(8, 4.2))
plantilla(ax, ganancia=False, ymin=-80, ymax=10)
ax.plot(f, -db(vout/vin), color=AZUL, label="LTspice")
ax.set_xlim(10, 1e5); ax.set_ylim(-5, 80); ax.legend(loc="upper center")
ax.annotate(f"{-db(np.interp(200, f, abs(vout))):.2f} dB", (200, -db(np.interp(200, f, abs(vout)))),
            textcoords="offset points", xytext=(10, -15), fontsize=8)
ax.annotate(f"{-db(np.interp(5000, f, abs(vout))):.2f} dB", (5000, -db(np.interp(5000, f, abs(vout)))),
            textcoords="offset points", xytext=(-55, -15), fontsize=8)
guardar(fig, "sim_ci_atenuacion.png")

fig, ax = plt.subplots(figsize=(8, 4))
plantilla(ax, ymin=-2)
ax.plot(f, db(T), color=ROJO, lw=3, alpha=0.35, label="Teórica")
ax.plot(f, db(vout/vin), color=AZUL, label="LTspice (AO ideal)")
ax.set_xlim(600, 1600); ax.set_ylim(-1, 0.6); ax.legend()
ax.set_title("Detalle de la banda de paso")
guardar(fig, "sim_ci_banda_paso.png")

# ---------------------------------------------------------------- agregado 3: LM324
_, dl, _ = leer_raw(SIM / "filtro_ci_lm324.raw")
fl = dl["frequency"][0].real
vl, vlpb = dl["v(out)"][0]/dl["v(in)"][0], dl["v(pb)"][0]/dl["v(in)"][0]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
plantilla(a1)
a1.plot(f, db(vout/vin), color=AZUL, label="AO ideal")
a1.plot(fl, db(vl), "--", color=NARANJA, label="LM324")
a1.set_xlim(10, fl.max()); a1.set_ylim(-80, 10); a1.legend(loc="lower center")
plantilla(a2, ymin=-2)
a2.plot(f, db(vout/vin), color=AZUL, label="AO ideal")
a2.plot(fl, db(vl), "--", color=NARANJA, label="LM324")
a2.set_xlim(600, 1600); a2.set_ylim(-1, 0.6); a2.set_title("Banda de paso", fontsize=9)
guardar(fig, "sim_ci_ideal_vs_lm324.png")

# ---------------------------------------------------------------- 1.5 peor desviación
for nombre, archivo, titulo, etiquetas in (
        ("filtro_ci_peor_caso_wp", "sim_peor_caso_wp.png", "Todos los componentes $\\pm 10\\,\\%$",
         ["$-10\\,\\%$", "Nominal", "$+10\\,\\%$"]),
        ("filtro_ci_peor_caso", "sim_peor_caso_bw.png", "Peor caso del ancho de banda ($\\delta = 10\\,\\%$)",
         ["$s = -1$ (inestable: curva sin validez física)", "Nominal", "$s = +1$ ($Q_p$ mínimo)"])):
    _, dw, _ = leer_raw(SIM / f"{nombre}.raw")
    fw = dw["frequency"][0].real
    fig, ax = plt.subplots(figsize=(8, 4.2))
    plantilla(ax)
    for i, (et, est, color) in enumerate(zip(etiquetas, (":", "-", "--"), (NARANJA, AZUL, VERDE))):
        ax.plot(fw, db(dw["v(out)"][i]/dw["v(in)"][i]), est, color=color, label=et)
    ax.set_xlim(100, 1e4); ax.set_ylim(-60, 10); ax.legend(loc="lower center", fontsize=8); ax.set_title(titulo)
    guardar(fig, archivo)

_, di, _ = leer_raw(SIM / "filtro_ci_inestable.raw")
ti, vi = di["time"][0], di["v(out)"][0]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
m = ti < 2e-3
a1.plot(ti[m]*1e3, vi[m], color=ROJO)
a1.set_xlabel("Tiempo [ms]"); a1.set_ylabel("$V_{out}$ [V]"); a1.set_title("Primeros 2 ms")
a2.semilogy(ti*1e3, np.abs(vi) + 1e-12, color=ROJO, lw=0.5)
a2.set_xlabel("Tiempo [ms]"); a2.set_ylabel("$|V_{out}|$ [V]"); a2.set_title("Crecimiento exponencial")
guardar(fig, "sim_inestable.png")

# ---------------------------------------------------------------- 1.6 Montecarlo y agregados 1 y 2
fnom = f
for nombre, titulo in (("filtro_ci_mc_10", "Componentes iguales, tolerancia 10 %"),
                       ("filtro_ci_mc_05", "Componentes iguales, tolerancia 5 %"),
                       ("filtro_ci_mc_01", "Componentes iguales, tolerancia 1 %"),
                       ("filtro_ug_mc_10", "Ganancia unitaria, tolerancia 10 %")):
    _, dm, runs = leer_raw(SIM / f"{nombre}.raw")
    fm = dm["frequency"][0].real
    g = db(dm["v(out)"])
    fig, ax = plt.subplots(figsize=(8, 4.2))
    plantilla(ax)
    ax.plot(fm, g.T, color=AZUL, lw=0.4, alpha=0.12)
    ax.plot(fnom, db(vout/vin), color="k", lw=1.2, label="Nominal")
    ax.set_xlim(100, 1e4); ax.set_ylim(-60, 15); ax.legend(loc="lower center")
    ax.set_title(f"Montecarlo: {titulo} ({runs} corridas)")
    guardar(fig, f"sim_{nombre[7:]}.png")

ci, ug = stats_mc("filtro_ci_mc_10"), stats_mc("filtro_ug_mc_10")
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
bins = np.logspace(np.log10(0.1), np.log10(40), 40)
a1.hist(ci["rip"], bins=bins, alpha=0.6, color=NARANJA, label="Componentes iguales")
a1.hist(ug["rip"], bins=bins, alpha=0.6, color=AZUL, label="Ganancia unitaria")
a1.axvline(Ap, color=ROJO, ls="--", label="$A_p = 0.25$ dB")
a1.set_xscale("log"); a1.set_xlabel("Rizado en la banda de paso [dB]"); a1.set_ylabel("Corridas"); a1.legend(fontsize=8)
bins = np.linspace(25, 42, 35)
a2.hist(np.minimum(ci["a200"], ci["a5k"]), bins=bins, alpha=0.6, color=NARANJA, label="Componentes iguales")
a2.hist(np.minimum(ug["a200"], ug["a5k"]), bins=bins, alpha=0.6, color=AZUL, label="Ganancia unitaria")
a2.axvline(As, color=ROJO, ls="--", label="$A_s = 30$ dB")
a2.set_xlabel("Atenuación mínima en rechazo [dB]"); a2.set_ylabel("Corridas"); a2.legend(fontsize=8)
fig.suptitle("Montecarlo con tolerancia del 10 % (500 corridas por topología)", fontsize=10)
guardar(fig, "sim_mc_comparacion.png")

_, du, _ = leer_raw(SIM / "filtro_ug_ideal.raw")
fu = du["frequency"][0].real
fig, ax = plt.subplots(figsize=(8, 4))
plantilla(ax, ymin=-2)
ax.plot(f, db(vout/vin), color=NARANJA, label="Componentes iguales")
ax.plot(fu, db(du["v(out)"][0]/du["v(in)"][0]), "--", color=AZUL, label="Ganancia unitaria")
ax.set_xlim(600, 1600); ax.set_ylim(-1, 0.6); ax.legend(); ax.set_title("Banda de paso nominal de ambas topologías")
guardar(fig, "sim_ug_vs_ci_nominal.png")

# ---------------------------------------------------------------- oscilador
def armonicos(t, v, f0, n=9):
    A = np.column_stack([np.ones_like(t)] + [fn(2*np.pi*k*f0*t) for k in range(1, n + 1)
                                             for fn in (np.sin, np.cos)])
    c = np.linalg.lstsq(A, v, rcond=None)[0]
    return np.hypot(c[1::2], c[2::2])


def analizar_osc(nombre):
    _, do, _ = leer_raw(OSC / f"{nombre}.raw")
    t, v = do["time"][0], do["v(out)"][0]
    orden = np.argsort(t); t, v = t[orden], v[orden]
    m = t > 30e-3
    cr = t[1:][(v[:-1] < 0) & (v[1:] >= 0) & (t[1:] > 30e-3)]
    f0 = (len(cr) - 1)/(cr[-1] - cr[0])
    h = armonicos(t[m], v[m], f0)
    return t, v, f0, h, np.sqrt((h[1:]**2).sum())/h[0]


t, v, f0, h, thd = analizar_osc("oscilador_wien")
ts, vs, f0s, hs, thds = analizar_osc("oscilador_wien_slew")

fig, ax = plt.subplots(figsize=(8, 3.5))
m = t < 3e-3
ax.plot(t[m]*1e3, v[m], color=AZUL, lw=0.7)
ax.set_xlabel("Tiempo [ms]"); ax.set_ylabel("$V_{out}$ [V]"); ax.set_title("Arranque del oscilador")
guardar(fig, "osc_arranque.png")

fig, ax = plt.subplots(figsize=(8, 3.5))
m = t > 39.75e-3
ax.plot((t[m] - t[m][0])*1e6, v[m], color=AZUL)
ax.set_xlabel("Tiempo [µs]"); ax.set_ylabel("$V_{out}$ [V]")
ax.set_title(f"Régimen permanente: $f$ = {f0:.0f} Hz, $V_p$ = {v[t > 30e-3].max():.2f} V")
guardar(fig, "osc_permanente.png")

fig, ax = plt.subplots(figsize=(8, 3.5))
ax.bar(np.arange(1, 10), 20*np.log10(h/h[0]), color=AZUL, width=0.5, bottom=0)
ax.set_xticks(range(1, 10)); ax.set_xlabel("Armónico"); ax.set_ylabel("Amplitud relativa [dB]")
ax.set_ylim(-90, 5); ax.set_title(f"Contenido armónico (THD = {100*thd:.1f} %)")
guardar(fig, "osc_espectro.png")

fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
for tt, vv, et, color in ((t, v, f"$R_{{f1}}$ = 15k, $R_{{f2}}$ = 6.8k ({f0:.0f} Hz)", AZUL),
                          (ts, vs, f"$R_{{f1}}$ = 18k, $R_{{f2}}$ = 4.7k ({f0s:.0f} Hz)", NARANJA)):
    m = tt > 39.75e-3
    x = (tt[m] - tt[m][0])*1e6
    a1.plot(x, vv[m], color=color, label=et)
    a2.plot(x[1:], np.diff(vv[m])/np.diff(tt[m])*1e-6, color=color)
for y in (0.5, -0.5):
    a2.axhline(y, color=ROJO, ls="--", lw=1)
a2.text(2, 0.53, "SR = 0.5 V/µs", color=ROJO, fontsize=8)
a1.set_ylabel("$V_{out}$ [V]"); a1.legend(fontsize=8, loc="upper right")
a2.set_ylabel("$dV_{out}/dt$ [V/µs]"); a2.set_xlabel("Tiempo [µs]")
guardar(fig, "osc_slew_rate.png")

# ---------------------------------------------------------------- resumen numérico
print("\nResumen:")
print(f"  Nominal AO ideal: rizado {np.ptp(db(vout[(f>=800)&(f<=1250)])):.3f} dB")
for nombre in ("filtro_ci_mc_10", "filtro_ci_mc_05", "filtro_ci_mc_01", "filtro_ug_mc_10"):
    s = stats_mc(nombre)
    print(f"  {nombre}: rizado medio {s['rip'].mean():.2f} dB, máx {s['rip'].max():.2f} dB, "
          f"rechazo OK {100*np.mean((s['a200']>=As)&(s['a5k']>=As)):.1f} %, cumplen {100*s['ok'].mean():.1f} %")
print(f"  Oscilador: f = {f0:.1f} Hz, THD = {100*thd:.2f} %, Vp = {v[t>30e-3].max():.3f} V")
print(f"  Oscilador (slew): f = {f0s:.1f} Hz, THD = {100*thds:.2f} %, Vp = {vs[ts>30e-3].max():.3f} V, "
      f"dV/dt máx = {np.max(np.abs(np.diff(vs[ts>30e-3])/np.diff(ts[ts>30e-3])))*1e-6:.3f} V/µs")
