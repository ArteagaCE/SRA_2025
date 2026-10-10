# TP4 – Filtros Activos

Pasabanda Chebyshev: banda de paso 800–1250 Hz con Ap = 0,25 dB; banda de rechazo en 200 Hz y 5 kHz con As = 30 dB.

## Archivos

| Archivo | Qué hace |
|---|---|
| `scripts/aproximacion_tp4.m` | 1.1: aproximación de Chebyshev y bicuadráticas en MATLAB (basado en el anexo de la guía) |
| `scripts/diseno_tp4.py` | 1.2, 1.4, 1.5: componentes, sensibilidades y peor caso analítico, para las dos topologías |
| `GUIA_SIMULACIONES.md` | Paso a paso de cada simulación en LTspice (1.3, 1.5, 1.6, agregados y oscilador) |
| `scripts/ltspice_raw.py`, `scripts/graficos_*.py` | Leen los `.raw` y `.log` de LTspice y generan figuras y estadísticas |
| `informe/` | Informe en LaTeX (se reescribe con el método de componentes iguales) |

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
