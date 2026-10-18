"""
Genera todas las figuras del informe del TP4 a partir de los resultados de simular_tp4.py.
Lee TP4/resultados/*.pkl (no vuelve a simular) y escribe:
    TP4/figs/<nombre>.png         imagen para el informe
    TP4/figs/pkl/<nombre>.pkl     figura de matplotlib completa (se abre interactiva con abrir_figura.py)

Ejecutar:  python TP4/scripts/graficos_tp4.py
"""
import pickle
from pathlib import Path

import numpy as np
import scipy.signal as sg
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from diseno_tp4 import num, den, fp, fs, Ap, As

TP4 = Path(__file__).resolve().parents[1]
RES, FIGS = TP4 / "resultados", TP4 / "figs"
(FIGS / "pkl").mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.3})

AZUL, NARANJA, VERDE, ROJO, GRIS = "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "0.4"


def cargar(nombre):
    with open(RES / f"{nombre}.pkl", "rb") as f:
        return pickle.load(f)


def db(x):
    return 20*np.log10(np.abs(x))


def fase(x):
    return np.unwrap(np.angle(x))*180/np.pi


def plantilla(ax, ganancia=True, ymin=-80, ymax=10):
    """Plantilla de requerimientos: zonas prohibidas sombreadas."""
    kw = dict(color=ROJO, alpha=0.12, lw=0)
    if ganancia:
        ax.fill_between([1, fs[0]], -As, ymax, **kw)
        ax.fill_between([fs[1], 1e7], -As, ymax, **kw)
        ax.fill_between(fp, -Ap, ymin, **kw)
    else:
        ax.fill_between([1, fs[0]], As, -ymax, **kw)
        ax.fill_between([fs[1], 1e7], As, -ymax, **kw)
        ax.fill_between(fp, Ap, -ymin, **kw)
    ax.set_xscale("log")
    ax.set_xlabel("Frecuencia [Hz]")
    ax.set_ylabel("Ganancia [dB]" if ganancia else "Atenuación [dB]")


def guardar(fig, nombre):
    fig.tight_layout()
    fig.savefig(FIGS / f"{nombre}.png", dpi=200)
    with open(FIGS / "pkl" / f"{nombre}.pkl", "wb") as f:
        pickle.dump(fig, f)
    plt.close(fig)
    print("  ", nombre)


print("Figuras:")

# ---------------------------------------------------------------- 1.1 aproximación
f = np.logspace(1, 5, 4000)
fig, ax = plt.subplots(figsize=(8, 4.2))
plantilla(ax)
ax.plot(f, db(sg.freqs(num, den, 2*np.pi*f)[1]), color=AZUL, lw=1.8, label="Aproximación de Chebyshev ($n = 2$)")
ax.set_xlim(10, 1e5); ax.set_ylim(-80, 10); ax.legend(loc="lower center")
guardar(fig, "aproximacion_chebyshev")

# ---------------------------------------------------------------- 1.3 simulación nominal (AO ideal)
d = cargar("nominal_ci_ideal")
f, tr = d["f"], d["trazas"]
vin, vpb, vpa, vout = tr["V(in)"], tr["V(pb)"], tr["V(pa_in)"], tr["V(out)"]
T = sg.freqs(num, den, 2*np.pi*f)[1]

for x, titulo, color, archivo in ((vpb/vin, "Etapa 1: pasabajos (incluye el divisor $R_a$-$R_b$)", AZUL, "sim_ci_etapa_pb"),
                                  (vout/vpa, "Etapa 2: pasaaltos", VERDE, "sim_ci_etapa_pa")):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 5.5), sharex=True)
    a1.semilogx(f, db(x), color=color); a1.set_ylabel("Módulo [dB]"); a1.set_title(titulo)
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
guardar(fig, "sim_ci_total")

fig, ax = plt.subplots(figsize=(8, 4.2))
plantilla(ax, ganancia=False)
ax.plot(f, -db(vout/vin), color=AZUL, label="LTspice")
for fx, dx in ((200, 10), (5000, -60)):
    a = -db(np.interp(fx, f, np.abs(vout/vin)))
    ax.annotate(f"{a:.2f} dB", (fx, a), textcoords="offset points", xytext=(dx, -15), fontsize=8)
ax.set_xlim(10, 1e5); ax.set_ylim(-5, 80); ax.legend(loc="upper center")
guardar(fig, "sim_ci_atenuacion")

fig, ax = plt.subplots(figsize=(8, 4))
plantilla(ax, ymin=-2)
ax.plot(f, db(T), color=ROJO, lw=3, alpha=0.35, label="Teórica")
ax.plot(f, db(vout/vin), color=AZUL, label=f"LTspice (rizado {d['meas']['gmax'] - d['meas']['gmin']:.3f} dB)")
ax.set_xlim(600, 1600); ax.set_ylim(-1, 0.6); ax.legend(); ax.set_title("Detalle de la banda de paso")
guardar(fig, "sim_ci_banda_paso")

# ---------------------------------------------------------------- agregado 3: LM324
dl = cargar("nominal_ci_lm324")
fl, vl = dl["f"], dl["trazas"]["V(out)"]/dl["trazas"]["V(in)"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
plantilla(a1)
a1.plot(f, db(vout/vin), color=AZUL, label="AO ideal")
a1.plot(fl, db(vl), "--", color=NARANJA, label="LM324")
a1.set_xlim(10, fl.max()); a1.set_ylim(-90, 10); a1.legend(loc="lower center")
plantilla(a2, ymin=-2)
a2.plot(f, db(vout/vin), color=AZUL, label=f"AO ideal ({d['meas']['gmax'] - d['meas']['gmin']:.3f} dB)")
a2.plot(fl, db(vl), "--", color=NARANJA, label=f"LM324 ({dl['meas']['gmax'] - dl['meas']['gmin']:.3f} dB)")
a2.set_xlim(600, 1600); a2.set_ylim(-1, 0.6); a2.set_title("Banda de paso (rizado)", fontsize=9); a2.legend(fontsize=8)
guardar(fig, "sim_ci_ideal_vs_lm324")

# ---------------------------------------------------------------- 1.5 peor desviación
pc = cargar("peor_caso")
for clave, archivo, titulo, etiquetas in (
        ("wp", "sim_peor_caso_wp", "Todos los componentes $\\pm 10\\,\\%$ (corrimiento de $\\omega_p$)",
         ["$-10\\,\\%$", "Nominal", "$+10\\,\\%$"]),
        ("bw", "sim_peor_caso_bw", "Peor caso del ancho de banda ($\\delta = 10\\,\\%$)",
         ["$s = -1$: inestable (curva AC sin validez física)", "Nominal", "$s = +1$: $Q_p$ mínimo"])):
    c = pc[clave]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    plantilla(ax)
    for i, (et, est, color) in enumerate(zip(etiquetas, (":", "-", "--"), (NARANJA, AZUL, VERDE))):
        ax.plot(c["f"], db(c["out"][i]), est, color=color, label=et)
    ax.set_xlim(100, 1e4); ax.set_ylim(-60, 10); ax.legend(loc="lower center", fontsize=8); ax.set_title(titulo)
    guardar(fig, archivo)

di = cargar("inestable")
ti, vi = di["t"], di["out"]
orden = np.argsort(ti); ti, vi = ti[orden], vi[orden]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
m = ti < 2e-3
a1.plot(ti[m]*1e3, vi[m], color=ROJO)
a1.set_xlabel("Tiempo [ms]"); a1.set_ylabel("$V_{out}$ [V]"); a1.set_title("Primeros 2 ms")
a2.semilogy(ti*1e3, np.abs(vi) + 1e-12, color=ROJO, lw=0.5)
a2.set_xlabel("Tiempo [ms]"); a2.set_ylabel("$|V_{out}|$ [V]"); a2.set_title("Crecimiento exponencial")
guardar(fig, "sim_inestable")

# ---------------------------------------------------------------- 1.6 Montecarlo y agregados 1 y 2
mc = cargar("montecarlo")
nombres = {"ci": "Componentes iguales", "ug": "Ganancia unitaria"}
for (topo, tol), r in mc.items():
    fig, ax = plt.subplots(figsize=(8, 4.2))
    plantilla(ax)
    inest = r["polos"]["inestable"]
    ax.plot(r["f"], r["out_db"][~inest].T, color=AZUL, lw=0.4, alpha=0.12)
    if inest.any():
        ax.plot(r["f"], r["out_db"][inest].T, color=ROJO, lw=0.4, alpha=0.3)
        ax.plot([], [], color=ROJO, label=f"Inestables ({inest.sum()} corridas)")
    ref = d if topo == "ci" else cargar("nominal_ug_ideal")
    ax.plot(ref["f"], db(ref["trazas"]["V(out)"]/ref["trazas"]["V(in)"]), color="k", lw=1.2, label="Nominal")
    ax.set_xlim(100, 1e4); ax.set_ylim(-60, 15); ax.legend(loc="lower center", fontsize=8)
    ax.set_title(f"Montecarlo: {nombres[topo]}, tolerancia {tol*100:.0f} % ({len(inest)} corridas)")
    guardar(fig, f"sim_mc_{topo}_{round(tol*100):02d}")

fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
bins = np.logspace(np.log10(0.1), np.log10(40), 40)
for topo, color in (("ci", NARANJA), ("ug", AZUL)):
    r = mc[(topo, 0.10)]
    est = ~r["polos"]["inestable"]
    a1.hist(r["rizado"][est], bins=bins, alpha=0.6, color=color, label=nombres[topo])
    a2.hist(np.minimum(r["a200"], r["a5k"])[est], bins=np.linspace(20, 45, 40), alpha=0.6, color=color,
            label=nombres[topo])
a1.axvline(Ap, color=ROJO, ls="--", label="$A_p = 0.25$ dB")
a1.set_xscale("log"); a1.set_xlabel("Rizado en la banda de paso [dB]"); a1.set_ylabel("Corridas"); a1.legend(fontsize=8)
a2.axvline(As, color=ROJO, ls="--", label="$A_s = 30$ dB")
a2.set_xlabel("Atenuación mínima en rechazo [dB]"); a2.set_ylabel("Corridas"); a2.legend(fontsize=8)
fig.suptitle("Montecarlo con tolerancia del 10 % (corridas estables)", fontsize=10)
guardar(fig, "sim_mc_comparacion")

fig, ax = plt.subplots(figsize=(7, 4))
tols = sorted({t for _, t in mc})
for topo, color, marca in (("ci", NARANJA, "o"), ("ug", AZUL, "s")):
    med = [np.median(mc[(topo, t)]["rizado"][~mc[(topo, t)]["polos"]["inestable"]]) for t in tols]
    p95 = [np.percentile(mc[(topo, t)]["rizado"][~mc[(topo, t)]["polos"]["inestable"]], 95) for t in tols]
    ax.plot(np.array(tols)*100, med, marca + "-", color=color, label=f"{nombres[topo]}: mediana")
    ax.plot(np.array(tols)*100, p95, marca + "--", color=color, alpha=0.6, label=f"{nombres[topo]}: percentil 95")
ax.axhline(Ap, color=ROJO, ls=":", label="$A_p = 0.25$ dB")
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xticks([1, 5, 10]); ax.set_xticklabels(["1", "5", "10"])
ax.set_xlabel("Tolerancia de los componentes [%]"); ax.set_ylabel("Rizado en la banda de paso [dB]")
ax.legend(fontsize=8)
guardar(fig, "sim_mc_rizado_vs_tolerancia")

du = cargar("nominal_ug_ideal")
fig, ax = plt.subplots(figsize=(8, 4))
plantilla(ax, ymin=-2)
ax.plot(f, db(vout/vin), color=NARANJA, label="Componentes iguales")
ax.plot(du["f"], db(du["trazas"]["V(out)"]/du["trazas"]["V(in)"]), "--", color=AZUL, label="Ganancia unitaria")
ax.set_xlim(600, 1600); ax.set_ylim(-1, 0.6); ax.legend(); ax.set_title("Banda de paso nominal de ambas topologías")
guardar(fig, "sim_ug_vs_ci_nominal")

# ---------------------------------------------------------------- oscilador
try:
    osc = cargar("oscilador")
except FileNotFoundError:
    osc = None
if osc:
    fin, sl = osc["final"], osc["slew"]
    t, v = fin["t"], fin["v"]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    m = t < 3e-3
    ax.plot(t[m]*1e3, v[m], color=AZUL, lw=0.7)
    ax.set_xlabel("Tiempo [ms]"); ax.set_ylabel("$V_{out}$ [V]"); ax.set_title("Arranque del oscilador")
    guardar(fig, "osc_arranque")

    fig, ax = plt.subplots(figsize=(8, 3.5))
    m = t > 39.75e-3
    ax.plot((t[m] - t[m][0])*1e6, v[m], color=AZUL)
    ax.set_xlabel("Tiempo [µs]"); ax.set_ylabel("$V_{out}$ [V]")
    ax.set_title(f"Régimen permanente: $f$ = {fin['f']:.0f} Hz, $V_p$ = {fin['vp']:.2f} V")
    guardar(fig, "osc_permanente")

    fig, ax = plt.subplots(figsize=(8, 3.5))
    h = fin["armonicos"]
    ax.bar(np.arange(1, len(h) + 1), 20*np.log10(h/h[0]), color=AZUL, width=0.5)
    ax.set_xticks(range(1, len(h) + 1)); ax.set_xlabel("Armónico"); ax.set_ylabel("Amplitud relativa [dB]")
    ax.set_ylim(-90, 5); ax.set_title(f"Contenido armónico (THD = {100*fin['thd']:.1f} %)")
    guardar(fig, "osc_espectro")

    fig, ax = plt.subplots(figsize=(7, 4))
    b = osc["barrido"]
    R = np.array([x["R"] for x in b])/1e3; fr = np.array([x["f"] for x in b])
    ax.fill_between([R.min() - 0.1, R.max() + 0.1], 11900, 12100, color=VERDE, alpha=0.15, label="12 kHz $\\pm$ 100 Hz")
    ax.plot(R, fr, "o-", color=AZUL, label="Simulación (LM324)")
    ax.plot(R, 1/(2*np.pi*R*1e3*1.5e-9), "--", color=GRIS, label="$1/(2\\pi RC)$")
    ax.set_xlabel("$R$ [k$\\Omega$]"); ax.set_ylabel("Frecuencia de oscilación [Hz]"); ax.legend(fontsize=8)
    ax.set_xlim(R.min() - 0.1, R.max() + 0.1)
    guardar(fig, "osc_ajuste_R")

    fig, (a1, a2) = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
    for res, et, color in ((fin, "$R_{f1}$ = 15k, $R_{f2}$ = 6.8k", AZUL), (sl, "$R_{f1}$ = 18k, $R_{f2}$ = 4.7k", NARANJA)):
        tt, vv = res["t"], res["v"]
        m = tt > 39.75e-3
        x = (tt[m] - tt[m][0])*1e6
        a1.plot(x, vv[m], color=color, label=f"{et} ({res['f']:.0f} Hz, $V_p$ = {res['vp']:.2f} V)")
        a2.plot(x[1:], np.diff(vv[m])/np.diff(tt[m])*1e-6, color=color)
    for y in (0.5, -0.5):
        a2.axhline(y, color=ROJO, ls="--", lw=1)
    a2.text(2, 0.53, "SR = 0.5 V/µs", color=ROJO, fontsize=8)
    a1.set_ylabel("$V_{out}$ [V]"); a1.legend(fontsize=8, loc="upper right")
    a2.set_ylabel("$dV_{out}/dt$ [V/µs]"); a2.set_xlabel("Tiempo [µs]")
    guardar(fig, "osc_slew_rate")

    fig, ax = plt.subplots(figsize=(7, 3.8))
    fm = osc["mc"]["f"]
    ax.hist(fm, bins=20, color=AZUL, alpha=0.7)
    ax.axvspan(11900, 12100, color=VERDE, alpha=0.15, label="12 kHz $\\pm$ 100 Hz")
    ax.set_xlabel("Frecuencia de oscilación [Hz]"); ax.set_ylabel("Corridas")
    ax.set_title(f"Montecarlo: $R$ al 1 %, $C$ al 5 % ({len(fm)} corridas)"); ax.legend(fontsize=8)
    guardar(fig, "osc_montecarlo")
