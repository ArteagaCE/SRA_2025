# TP4 – Filtros Activos

Pasabanda Chebyshev: banda de paso 800–1250 Hz con Ap = 0,25 dB; banda de rechazo en 200 Hz y 5 kHz con As = 30 dB.

## Cómo regenerar todo

```bash
pip install spicelib numpy scipy matplotlib
python TP4/scripts/simular_tp4.py       # corre todas las simulaciones en LTspice (~5 min) -> resultados/*.pkl
python TP4/scripts/graficos_tp4.py      # genera las figuras desde los .pkl (segundos) -> figs/*.png y figs/pkl/
python TP4/scripts/abrir_figura.py sim_ci_total   # abre una figura guardada, interactiva
```

`simular_tp4.py` acepta estudios sueltos: `nominal`, `peor`, `mc`, `osc` y `oscmc` (por ejemplo, `python simular_tp4.py mc`).

## Archivos

| Archivo | Qué hace |
|---|---|
| `sim/filtro_ci_ideal.asc`, `filtro_ci_lm324.asc`, `filtro_ug_ideal.asc`, `oscilador/sim/oscilador_wien.asc` | **Esquemáticos base** dibujados en LTspice. Son la única fuente del circuito. |
| `scripts/simular_tp4.py` | Agregado de automatización: convierte los esquemáticos en netlist, cambia los valores desde Python (peor caso, Montecarlo, barrido de R) y corre LTspice en modo batch con **spicelib** |
| `scripts/spice_tp4.py` | Funciones auxiliares: generación y normalización de la netlist, lectura de `.raw` y `.log` |
| `scripts/graficos_tp4.py` | Figuras del informe a partir de `resultados/*.pkl`; cada figura se guarda también como pickle |
| `scripts/abrir_figura.py` | Reabre una figura guardada como ventana interactiva de matplotlib |
| `scripts/aproximacion_tp4.m` | 1.1: aproximación de Chebyshev y bicuadráticas en MATLAB (basado en el anexo de la guía) |
| `scripts/diseno_tp4.py` | 1.2, 1.4, 1.5: componentes, sensibilidades y peor caso analítico, para las dos topologías |
| `sim/*_mc_*.asc`, `*_peor_caso*.asc`, `*_inestable.asc` | Versiones manuales (con `mc()` y `.step`) usadas para validar el script: dan los mismos resultados |
| `GUIA_SIMULACIONES.md` | Paso a paso de las simulaciones manuales en LTspice |
| `informe/` | Informe en LaTeX |

## Diseño principal: Sallen-Key de componentes iguales (método de Daryanani)

Sección 1 → pasabajos en 1296,12 Hz; sección 2 → pasaaltos en 771,53 Hz. Las dos tienen Qp = 2,557, así que k = 3 − 1/Qp = 2,609.

| | Pasabajos (U1) | Divisor + seguidor (U2) | Pasaaltos (U3) |
|---|---|---|---|
| Componentes | Ra = 76,8k, Rb = 18,7k, R2 = 15k, C1 = C2 = 8,2n | Rc = 42,2k, Rd = 10k | C1 = C2 = 18n, R1 = R2 = 11,5k |
| Ganancia | r1 = 6,65k, r2 = 10,7k → k = 2,609 | 0,1916 | r1 = 6,65k, r2 = 10,7k → k = 2,609 |

Con AO ideal y valores normalizados el ripple da 0,27 dB: no alcanza a cumplir los 0,25 dB exactos con valores comerciales.

## Agregados
1. **Comparación con Sallen-Key de ganancia unitaria.** Las sensibilidades de ωp/Qp son ≤ 1, contra hasta 5,1 en la de componentes iguales (y 6,7 respecto de k).
2. **Cuantificar el cumplimiento:** qué porcentaje de las corridas de Montecarlo cumple la plantilla, para 10 %, 5 % y 1 % de tolerancia.
3. **Efectos del LM324 real frente al AO ideal.**
4. **Ejercicio adicional:** oscilador puente de Wien de 12 kHz.
