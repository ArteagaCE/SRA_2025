"""
SRA 2025 - Trabajo Práctico de Laboratorio N°4: Filtros Activos
Diseño del pasabanda Chebyshev como cascada Sallen-Key pasabajos + pasaaltos.

Diseño principal (método de Daryanani visto en clase):
    Sallen-Key de componentes iguales (R1 = R2 = R, C1 = C2 = C) y ganancia k = 1 + r2/r1.
Agregado (comparación de topologías):
    Sallen-Key de ganancia unitaria (k = 1).

La aproximación se calcula en aproximacion_tp4.m (MATLAB); acá se repite con SciPy
para tener los mismos números en Python.

Ejecutar:  python TP4/scripts/diseno_tp4.py
"""
from pathlib import Path

import numpy as np
import scipy.signal as sg

FIGS = Path(__file__).resolve().parents[1] / "figs"

# ----------------------------------------------------------------------------
# 1.1  Aproximación (idéntica a aproximacion_tp4.m)
# ----------------------------------------------------------------------------
fp = np.array([800, 1250]); fs = np.array([200, 5000]); Ap = 0.25; As = 30
n, Wn = sg.cheb1ord(2*np.pi*fp, 2*np.pi*fs, Ap, As, analog=True)
num, den = sg.cheby1(n, Ap, Wn, "bandpass", analog=True)
K_total = num[0]

pares = sorted([p for p in np.roots(den) if p.imag > 0], key=abs, reverse=True)
# Como en la guía: sección 1 (par alto) -> pasabajos, sección 2 (par bajo) -> pasaaltos
w_pb, w_pa = (abs(p) for p in pares)
Q = abs(pares[0])/(-2*pares[0].real)
# T(s) = [H_pb w_pb^2 / D_pb] [H_pa s^2 / D_pa]  con  H_pb*H_pa*w_pb^2 = K_total
H_pa = 0.5
H_pb = K_total/(H_pa*w_pb**2)

# ----------------------------------------------------------------------------
# 1.2  Síntesis: Sallen-Key de componentes iguales
#   T_V = k N_FF / (D - k N_FB)
#   PB:  wp = 1/(RC),  wp/Qp = (3 - k)/(RC),  ganancia en continua = k
#   PA:  wp = 1/(RC),  wp/Qp = (3 - k)/(RC),  ganancia en alta frecuencia = k
#   => k = 3 - 1/Qp  (igual en ambas etapas)
# ----------------------------------------------------------------------------
E12 = np.array([1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2])
E96 = np.round(10**(np.arange(96)/96), 2)


def serie(base, dec_min, dec_max):
    return np.concatenate([base*10.0**d for d in range(dec_min, dec_max)])


R_E96 = serie(E96, 2, 6)          # 100 ohm .. 976 kohm
C_E12 = serie(E12, -10, -6)       # 100 pF .. 820 nF


def mas_cercano(x, valores):
    return valores[np.argmin(abs(valores - x))]


k_ideal = 3 - 1/Q

# Ganancia k = 1 + r2/r1 con resistencias E96 (se busca el par de menor error)
r1, r2 = min(((a, b) for a in serie(E96, 3, 5) for b in serie(E96, 3, 5)),
             key=lambda p: abs(1 + p[1]/p[0] - k_ideal))
k = 1 + r2/r1

# Atenuaciones de entrada para obtener la ganancia pedida por cada bicuadrática
alfa_pb = H_pb/k      # divisor Ra-Rb en lugar de R1 del PB
alfa_pa = H_pa/k      # divisor Rc-Rd + seguidor antes del PA


def vecinos(x, valores, m=3):
    return valores[np.argsort(abs(valores - x))[:m]]


def bicuad_pb(R1, R2, C1, C2, k, a=1.0):
    """PB Sallen-Key genérico (Daryanani). R1 = resistencia de entrada."""
    return ([a*k/(R1*R2*C1*C2)],
            [1, 1/(R1*C1) + 1/(R2*C1) + (1 - k)/(R2*C2), 1/(R1*R2*C1*C2)])


def bicuad_pa(R1, R2, C1, C2, k, a=1.0):
    """PA Sallen-Key genérico. R1 = resistencia a la salida, R2 = a masa, C1 = entrada."""
    return ([a*k, 0, 0],
            [1, 1/(R2*C1) + 1/(R2*C2) + (1 - k)/(R1*C1), 1/(R1*R2*C1*C2)])


def wq(d):
    w = np.sqrt(d[2]); return w, w/d[1]


def candidatos_pb(m=250):
    """C1 = C2 = C (E12); R2, Ra, Rb (E96) con Ra||Rb ~ R2. Ordenados por error en wp, Qp y alfa."""
    lista = []
    for C in C_E12:
        R = 1/(w_pb*C)
        if not 2e3 <= R <= 100e3:
            continue
        for R2 in vecinos(R, R_E96, 4):
            for Ra in vecinos(R/alfa_pb, R_E96, 4):
                for Rb in vecinos(R/(1 - alfa_pb), R_E96, 4):
                    R1 = Ra*Rb/(Ra + Rb)
                    w, q = wq(bicuad_pb(R1, R2, C, C, k)[1])
                    a = Rb/(Ra + Rb)
                    err = max(abs(w/w_pb - 1), abs(q/Q - 1), abs(a/alfa_pb - 1)/5)
                    lista.append((err, Ra, Rb, R2, C))
    return sorted(lista)[:m]


def candidatos_pa(m=250):
    """C1 = C2 = C (E12); R1, R2 (E96) cercanos a 1/(wp C)."""
    lista = []
    for C in C_E12:
        R = 1/(w_pa*C)
        if not 2e3 <= R <= 100e3:
            continue
        for R1 in vecinos(R, R_E96, 4):
            for R2 in vecinos(R, R_E96, 4):
                w, q = wq(bicuad_pa(R1, R2, C, C, k)[1])
                lista.append((max(abs(w/w_pa - 1), abs(q/Q - 1)), R1, R2, C))
    return sorted(lista)[:m]


Rd = 10e3                                     # divisor del PA (alimenta un seguidor)
Rc = mas_cercano(Rd*(1 - alfa_pa)/alfa_pa, R_E96)
_f_bp = 2*np.pi*np.linspace(800, 1250, 400)


def rizado(cpb, cpa):
    _, Ra, Rb, R2, C = cpb
    _, R1p, R2p, Cp = cpa
    H = (sg.freqs(*bicuad_pb(Ra*Rb/(Ra + Rb), R2, C, C, k, Rb/(Ra + Rb)), _f_bp)[1]
         * sg.freqs(*bicuad_pa(R1p, R2p, Cp, Cp, k, Rd/(Rc + Rd)), _f_bp)[1])
    return np.ptp(20*np.log10(abs(H)))


# Se elige la combinación de ambas etapas que minimiza el rizado total en la banda de paso
_cpb, _cpa = min(((x, y) for x in candidatos_pb() for y in candidatos_pa()), key=lambda c: rizado(*c))
_, Ra, Rb, R_pb, C_pb = _cpb
_, R1_pa, R2_pa, C_pa = _cpa


Rth = Ra*Rb/(Ra + Rb)
pb = bicuad_pb(Rth, R_pb, C_pb, C_pb, k, Rb/(Ra + Rb))
pa = bicuad_pa(R1_pa, R2_pa, C_pa, C_pa, k, Rd/(Rc + Rd))

# ----------------------------------------------------------------------------
# Agregado 1: misma función con Sallen-Key de ganancia unitaria (k = 1)
#   PB: C1/C2 = 4Q^2 ; PA: R2/R1 = 4Q^2
# ----------------------------------------------------------------------------
UG = dict(  # valores elegidos en el diseño alternativo (ver informe)
    pb_C1=None, pb_C2=None, pb_R=None, pa_C=None, pa_R1=None, pa_R2=None)


def disenar_ganancia_unitaria():
    mejor = None
    for C1 in C_E12:
        for C2 in C_E12:
            if not 20 < C1/C2 < 32:
                continue
            R = 1/(w_pb*np.sqrt(C1*C2))
            if not 2e3 < R < 50e3:
                continue
            Rn = mas_cercano(R, R_E96)
            w, q = wq(bicuad_pb(Rn, Rn, C1, C2, 1)[1])
            err = max(abs(w/w_pb - 1), abs(q/Q - 1))
            if mejor is None or err < mejor[0]:
                mejor = (err, Rn, C1, C2)
    _, Rpb, C1, C2 = mejor
    mejor = None
    for C in C_E12:
        r = 1/(w_pa*C)            # sqrt(R1 R2)
        R1 = mas_cercano(r/(2*Q), R_E96)
        if not 1e3 < R1 < 20e3 or r**2/R1 > 100e3:
            continue
        R2 = mas_cercano(r**2/R1, R_E96)
        w, q = wq(bicuad_pa(R1, R2, C, C, 1)[1])
        err = max(abs(w/w_pa - 1), abs(q/Q - 1))
        if mejor is None or err < mejor[0]:
            mejor = (err, C, R1, R2)
    _, Cpa, R1pa, R2pa = mejor
    return dict(pb_R=Rpb, pb_C1=C1, pb_C2=C2, pa_C=Cpa, pa_R1=R1pa, pa_R2=R2pa)


UG = disenar_ganancia_unitaria()
# Ganancia unitaria: toda la atenuación (H_pb*H_pa = 0.2476) en un divisor a la entrada del PB
UG["alfa"] = H_pb*H_pa
UG["Ra"] = mas_cercano(UG["pb_R"]/UG["alfa"], R_E96)
UG["Rb"] = mas_cercano(UG["pb_R"]/(1 - UG["alfa"]), R_E96)

# ----------------------------------------------------------------------------
# 1.4  Sensibilidades de wp y wp/Qp (expresiones generales, evaluadas)
#   BW_PB = 1/(R1C1) + 1/(R2C1) + (1-k)/(R2C2)
#   BW_PA = 1/(R2C1) + 1/(R2C2) + (1-k)/(R1C1)
# ----------------------------------------------------------------------------


def sens_pb(R1, R2, C1, C2, k):
    bw = 1/(R1*C1) + 1/(R2*C1) + (1 - k)/(R2*C2)
    return {"R1": (-0.5, -(1/(R1*C1))/bw),
            "R2": (-0.5, -(1/(R2*C1) + (1 - k)/(R2*C2))/bw),
            "C1": (-0.5, -(1/(R1*C1) + 1/(R2*C1))/bw),
            "C2": (-0.5, -((1 - k)/(R2*C2))/bw),
            "k":  (0.0, -(k/(R2*C2))/bw)}


def sens_pa(R1, R2, C1, C2, k):
    bw = 1/(R2*C1) + 1/(R2*C2) + (1 - k)/(R1*C1)
    return {"R1": (-0.5, -((1 - k)/(R1*C1))/bw),
            "R2": (-0.5, -(1/(R2*C1) + 1/(R2*C2))/bw),
            "C1": (-0.5, -(1/(R2*C1) + (1 - k)/(R1*C1))/bw),
            "C2": (-0.5, -(1/(R2*C2))/bw),
            "k":  (0.0, -(k/(R1*C1))/bw)}


S_ci = {"PB": sens_pb(R_pb, R_pb, C_pb, C_pb, k_ideal), "PA": sens_pa(R1_pa, R2_pa, C_pa, C_pa, k_ideal)}
S_ug = {"PB": sens_pb(UG["pb_R"], UG["pb_R"], UG["pb_C1"], UG["pb_C2"], 1),
        "PA": sens_pa(UG["pa_R1"], UG["pa_R2"], UG["pa_C"], UG["pa_C"], 1)}


def sens_numerica(f_bicuad, args, idx, h=1e-7):
    """S^wp y S^(wp/Qp) por diferencias finitas respecto del argumento idx."""
    w0, q0 = wq(f_bicuad(*args)[1])
    a = list(args); a[idx] *= 1 + h
    w1, q1 = wq(f_bicuad(*a)[1])
    return (w1/w0 - 1)/h, ((w1/q1)/(w0/q0) - 1)/h


# ----------------------------------------------------------------------------
# 1.5  Peor desviación (primer orden):  |dy/y| <= delta * sum |S|
# ----------------------------------------------------------------------------
DELTA = 0.10


def peor_caso(S, con_k=False):
    claves = [c for c in S if c != "k" or con_k]
    return (DELTA*sum(abs(S[c][0]) for c in claves), DELTA*sum(abs(S[c][1]) for c in claves))


if __name__ == "__main__":
    print(f"Orden n = {n}; T(s) = {K_total:.6g} s^2 / D(s)")
    print(f"PB: fp = {w_pb/2/np.pi:.2f} Hz (wp = {w_pb:.2f}), ganancia en continua {H_pb:.4f}")
    print(f"PA: fp = {w_pa/2/np.pi:.2f} Hz (wp = {w_pa:.2f}), ganancia en alta frecuencia {H_pa:.4f}")
    print(f"Qp = {Q:.4f}  ->  k ideal = 3 - 1/Qp = {k_ideal:.4f}")

    print("\n=== Diseño principal: componentes iguales ===")
    print(f"k = 1 + r2/r1: r1 = {r1:.4g}, r2 = {r2:.4g} -> k = {k:.4f} ({(k/k_ideal-1)*100:+.3f} %)")
    print(f"PB: C1 = C2 = {C_pb*1e9:.3g} nF, R ideal = {1/(w_pb*C_pb):.1f}, R2 = {R_pb:.4g}")
    print(f"    alfa_PB = H_pb/k = {alfa_pb:.4f}: Ra = {R_pb/alfa_pb:.1f} -> {Ra:.4g},"
          f" Rb = {R_pb/(1-alfa_pb):.1f} -> {Rb:.4g}  (Ra||Rb = {Rth:.1f}, alfa = {Rb/(Ra+Rb):.4f})")
    print(f"PA: C1 = C2 = {C_pa*1e9:.3g} nF, R ideal = {1/(w_pa*C_pa):.1f}, R1 = {R1_pa:.4g} (a la salida), R2 = {R2_pa:.4g}")
    print(f"    alfa_PA = H_pa/k = {alfa_pa:.4f}: Rc = {Rc:.4g}, Rd = {Rd:.4g} (alfa = {Rd/(Rc+Rd):.4f}) + seguidor")
    for nombre, H, wi in (("PB", pb, w_pb), ("PA", pa, w_pa)):
        w, q = wq(H[1])
        print(f"  {nombre}: fp = {w/2/np.pi:.2f} Hz ({(w/wi-1)*100:+.2f} %), Qp = {q:.4f} ({(q/Q-1)*100:+.2f} %)")
    num_r = np.polymul(pb[0], pa[0]); den_r = np.polymul(pb[1], pa[1])
    f = np.linspace(800, 1250, 2000)
    g = 20*np.log10(abs(sg.freqs(num_r, den_r, 2*np.pi*f)[1]))
    a200, a5k = -20*np.log10(abs(sg.freqs(num_r, den_r, 2*np.pi*np.array([200, 5000]))[1]))
    print(f"  Con AO ideal: banda de paso [{g.min():.3f}, {g.max():.3f}] dB (rizado {np.ptp(g):.3f} dB),"
          f" atenuación 200 Hz {a200:.2f} dB, 5 kHz {a5k:.2f} dB")

    print("\n=== Agregado: ganancia unitaria (mismos polos) ===")
    print(f"PB: R1 = R2 = {UG['pb_R']:.4g}, C1 = {UG['pb_C1']*1e9:.3g} nF (a la salida), C2 = {UG['pb_C2']*1e9:.3g} nF")
    print(f"PA: C1 = C2 = {UG['pa_C']*1e9:.3g} nF, R1 = {UG['pa_R1']:.4g} (a la salida), R2 = {UG['pa_R2']:.4g}")
    print(f"Divisor de entrada (alfa = {UG['alfa']:.4f}): Ra = {UG['Ra']:.4g}, Rb = {UG['Rb']:.4g}"
          f" (Ra||Rb = {UG['Ra']*UG['Rb']/(UG['Ra']+UG['Rb']):.1f} en lugar de R1 = {UG['pb_R']:.4g})")
    for nombre, H, wi in (("PB", bicuad_pb(UG["pb_R"], UG["pb_R"], UG["pb_C1"], UG["pb_C2"], 1), w_pb),
                          ("PA", bicuad_pa(UG["pa_R1"], UG["pa_R2"], UG["pa_C"], UG["pa_C"], 1), w_pa)):
        w, q = wq(H[1])
        print(f"  {nombre}: fp = {w/2/np.pi:.2f} Hz ({(w/wi-1)*100:+.2f} %), Qp = {q:.4f} ({(q/Q-1)*100:+.2f} %)")

    print("\n=== Sensibilidades  S^wp / S^(wp/Qp)  (analítica | numérica) ===")
    for titulo, S, fpb, apb, fpa, apa in (
            ("Componentes iguales", S_ci, bicuad_pb, (R_pb, R_pb, C_pb, C_pb, k_ideal),
             bicuad_pa, (R1_pa, R2_pa, C_pa, C_pa, k_ideal)),
            ("Ganancia unitaria", S_ug, bicuad_pb, (UG["pb_R"], UG["pb_R"], UG["pb_C1"], UG["pb_C2"], 1.0),
             bicuad_pa, (UG["pa_R1"], UG["pa_R2"], UG["pa_C"], UG["pa_C"], 1.0))):
        print(f"  {titulo}")
        for etapa, f_b, args in (("PB", fpb, apb), ("PA", fpa, apa)):
            for i, (elem, (sw, sbw)) in enumerate(S[etapa].items()):
                nw, nb = sens_numerica(f_b, args, i)
                print(f"    {etapa} {elem:2s}: {sw:+.3f} / {sbw:+.3f}   |   {nw:+.3f} / {nb:+.3f}")
            dw, dbw = peor_caso(S[etapa])
            print(f"    {etapa} peor caso (10 %, sin k): |dwp/wp| <= {dw*100:.1f} %, |dBW/BW| <= {dbw*100:.1f} %")
