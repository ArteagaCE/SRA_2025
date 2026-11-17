# TP4 – Guía de simulaciones en LTspice

Todos los valores salen de `python TP4/scripts/diseno_tp4.py`. Guardá cada `.asc` en la carpeta indicada **con el nombre exacto**: los scripts de Python leen los `.raw` y `.log` que genera LTspice al lado de cada archivo.

## Convenciones para todos los circuitos

- **Etiquetas de nodos** (con *Label Net*, tecla F4): `in`, `pb`, `x`, `pa_in`, `out`. Los scripts buscan esos nombres.
- **Fuente de entrada:** `V1` entre `in` y masa, con *Small signal AC analysis* → AC Amplitude = 1.
- **AO ideal:** símbolo `OpAmps → opamp` y la directiva `.lib opamp.sub`. Por defecto tiene Aol = 100k y GBW = 10Meg. No necesita alimentación.
- **LM324:** símbolo `OpAmps → opamp2`, Value = `LM324/NS`, directiva `.include ../../lib/LM324_NS.lib`. Alimentación de ±12 V con dos fuentes: nodo `VCC` = +12 V y nodo `VEE` = −12 V.
- **Ganancia k de cada Sallen-Key:** k = 1 + r2/r1, con `r1` del terminal − a masa y `r2` del terminal − a la salida. Cada AO lleva su propio par.

---

## 1. Filtro principal: Sallen-Key de componentes iguales (consignas 1.2 y 1.3)

**Archivo:** `TP4/sim/filtro_ci_ideal.asc` (AO ideal)

### Etapa 1: pasabajos (U1)
| Componente | Conexión | Valor |
|---|---|---|
| Ra | `in` → nodo A | 76.8k |
| Rb | nodo A → masa | 18.7k |
| R2 | nodo A → + de U1 | 15k |
| C1 | nodo A → `pb` (realimentación positiva) | 8.2n |
| C2 | + de U1 → masa | 8.2n |
| r1 | − de U1 → masa | 6.65k |
| r2 | − de U1 → `pb` | 10.7k |

La salida de U1 es el nodo `pb`. Ra y Rb forman el divisor que reemplaza a R1: Ra‖Rb ≈ 15k y atenuación 0,196.

### Ajuste de ganancia entre etapas (divisor + seguidor, U2)
| Componente | Conexión | Valor |
|---|---|---|
| Rc | `pb` → `x` | 42.2k |
| Rd | `x` → masa | 10k |
| U2 | seguidor: + en `x`, − unido a la salida | — |

La salida de U2 es el nodo `pa_in`.

### Etapa 2: pasaaltos (U3)
| Componente | Conexión | Valor |
|---|---|---|
| C1 | `pa_in` → nodo B | 18n |
| C2 | nodo B → + de U3 | 18n |
| R1 | nodo B → `out` (realimentación positiva) | 11.5k |
| R2 | + de U3 → masa | 11.5k |
| r1 | − de U3 → masa | 6.65k |
| r2 | − de U3 → `out` | 10.7k |

### Directivas
```
.lib opamp.sub
.ac dec 500 10 100k
.meas AC Gmax MAX mag(V(out)) FROM 800 TO 1250
.meas AC Gmin MIN mag(V(out)) FROM 800 TO 1250
.meas AC G200 FIND mag(V(out)) AT 200
.meas AC G5k FIND mag(V(out)) AT 5k
```

### Qué mirar
- Graficá `V(pb)`, `V(pa_in)/V(pb)`, `V(out)/V(pa_in)` y `V(out)` (cada etapa y el total), en módulo y fase.
- **Resultado esperado con AO ideal:** banda de paso entre +0,03 y +0,30 dB (ripple ≈ 0,27 dB), 34,5 dB de atenuación en 200 Hz y 34,6 dB en 5 kHz. Si te da muy distinto, revisá las conexiones antes de seguir.
- Los resultados de `.meas` aparecen en *View → SPICE Error Log*.

---

## 2. Agregado 3: el mismo filtro con LM324

**Archivo:** `TP4/sim/filtro_ci_lm324.asc`

Copiá el circuito 1 y cambiá los tres AO por `opamp2` con Value `LM324/NS`, agregá la alimentación de ±12 V y reemplazá `.lib opamp.sub` por:
```
.include ../../lib/LM324_NS.lib
.ac dec 500 10 1Meg
```
Dejá las mismas cuatro `.meas`. Esta simulación muestra:
- La diferencia de ripple respecto del AO ideal.
- La atenuación por encima de 20 kHz: la impedancia de salida del LM324 deja pasar señal a través de C1 del pasabajos.
- El sobrepico de `V(pb)`, que fija la máxima amplitud de entrada antes de que la salida sature.

---

## 3. Peor desviación (consigna 1.5)

**Archivo:** `TP4/sim/filtro_ci_peor_caso.asc`

Copiá el circuito 1 (AO ideal) y reemplazá cada valor por la expresión de la tabla. Agregá:
```
.param tol=0.10
.step param s list -1 0 1
```
- `s = 0` es el circuito nominal.
- `s = +1` desplaza los componentes en el sentido que **aumenta** el ancho de banda ωp/Qp. Es la combinación de peor caso según el signo de cada sensibilidad.
- `s = −1` lo **disminuye**.

| Etapa | Componente | Expresión |
|---|---|---|
| PB | Ra | `{76.8k*(1-s*tol)}` |
| PB | Rb | `{18.7k*(1-s*tol)}` |
| PB | R2 | `{15k*(1+s*tol)}` |
| PB | C1 (realim.) | `{8.2n*(1-s*tol)}` |
| PB | C2 (a masa) | `{8.2n*(1+s*tol)}` |
| PB | r1 | `{6.65k*(1+s*tol)}` |
| PB | r2 | `{10.7k*(1-s*tol)}` |
| PA | C1 (entrada) | `{18n*(1+s*tol)}` |
| PA | C2 | `{18n*(1-s*tol)}` |
| PA | R1 (realim.) | `{11.5k*(1+s*tol)}` |
| PA | R2 (a masa) | `{11.5k*(1-s*tol)}` |
| PA | r1 | `{6.65k*(1+s*tol)}` |
| PA | r2 | `{10.7k*(1-s*tol)}` |

Rc y Rd quedan fijos, porque solo cambian la ganancia y no la forma.

Hacé también la versión que se ve en clase, con **todos** los componentes +10 % y −10 % (corre la frecuencia del polo). Guardala como `TP4/sim/filtro_ci_peor_caso_wp.asc`: cada valor `{V*(1+s*tol)}` con el mismo `.step`.

---

## 4. Montecarlo (consigna 1.6) y agregado 2

**Archivos:** `TP4/sim/filtro_ci_mc_10.asc`, `filtro_ci_mc_05.asc`, `filtro_ci_mc_01.asc`

Copiá el circuito 1 (AO ideal) y reemplazá **cada** R, C, r1 y r2 por `{mc(VALOR,tol)}`, por ejemplo `{mc(76.8k,tol)}`. `mc()` reparte el valor uniformemente entre ±tol. Directivas:
```
.lib opamp.sub
.ac dec 200 10 100k
.param tol=0.10
.step param run 1 500 1
.save V(out)
.meas AC Gmax MAX mag(V(out)) FROM 800 TO 1250
.meas AC Gmin MIN mag(V(out)) FROM 800 TO 1250
.meas AC G200 FIND mag(V(out)) AT 200
.meas AC G5k FIND mag(V(out)) AT 5k
```
Corré tres copias cambiando solo `tol` (0.10, 0.05 y 0.01). Con los `.log`, el script calcula qué porcentaje de las corridas cumple la plantilla. Eso es el agregado 2.

---

## 5. Agregado 1: Sallen-Key de ganancia unitaria (comparación)

**Archivos:** `TP4/sim/filtro_ug_ideal.asc` y `TP4/sim/filtro_ug_mc_10.asc`

Tiene los mismos polos y la misma ganancia total, pero cada AO es un seguidor: el − unido a la salida, sin r1 ni r2. No necesita divisor ni seguidor entre etapas.

| Etapa | Componente | Conexión | Valor |
|---|---|---|---|
| PB | Ra | `in` → nodo A | 53.6k |
| PB | Rb | nodo A → masa | 17.8k |
| PB | R2 | nodo A → + de U1 | 13.3k |
| PB | C1 | nodo A → `pb` (realim.) | 47n |
| PB | C2 | + de U1 → masa | 1.8n |
| PA | C1 | `pb` → nodo B | 27n |
| PA | C2 | nodo B → + de U2 | 27n |
| PA | R1 | nodo B → `out` (realim.) | 1.5k |
| PA | R2 | + de U2 → masa | 39.2k |

Primero corré la versión ideal con las directivas del punto 1. Después hacé la versión Montecarlo con tol = 0.10, igual que en el punto 4. Comparándola con `filtro_ci_mc_10` se ve cuánto más robusta es esta topología.

---

## 6. Ejercicio adicional: oscilador de 12 kHz

**Archivo:** `TP4/oscilador/sim/oscilador_wien.asc` (LM324 con ±12 V)

Puente de Wien:
- **Red RC:** R1 serie con C1 desde la salida hasta el nodo `p`, que va al + del AO. R2 en paralelo con C2, de `p` a masa. Usá `R1 = R2 = {R}` y `C1 = C2 = {C}`.
- **Realimentación negativa:** Rg = 10k del − a masa. Desde el − hasta `out`, Rf1 = 15k en serie con Rf2 = 6.8k, y Rf2 con dos diodos 1N4148 en antiparalelo.

Directivas:
```
.include ../../../lib/LM324_NS.lib
.param C=1.5n R=8.84k
.tran 0 40m 0 0.2u
.ic V(p)=10m
.meas TRAN t1 WHEN V(out)=0 RISE=200
.meas TRAN t2 WHEN V(out)=0 RISE=400
.meas TRAN frec PARAM 200/(t2-t1)
.meas TRAN vmax MAX V(out) FROM 30m TO 40m
.four 12k 9 1 V(out)
```

- **Valor teórico:** R = 1/(2π·12 kHz·1,5 nF) = 8,84k. Fijate qué frecuencia da: debería salir por debajo de 12 kHz por el desfasaje del LM324.
- **Ajuste a ±100 Hz:** reemplazá `R=8.84k` por `.step param R list 8.06k 8.25k 8.45k 8.66k` y elegí el valor E96 que deje `frec` dentro de 12 kHz ± 100 Hz.
- **Prueba de slew rate:** cambiá Rf1 a 18k y Rf2 a 4.7k. La amplitud crece por encima de ~6,6 V, el LM324 queda limitado por slew rate y la distorsión del `.four` sube mucho. Esa comparación va en el informe.

---

## Cuando termines

Avisame y, si querés, mandame capturas de los esquemáticos. Yo corro los scripts sobre tus `.raw` y `.log` para generar las figuras y tablas del informe.

---

## 7. Capturas para el informe

### Cómo sacarlas
- **Captura:** con la ventana de gráficos activa, `Win + Shift + S` → *Ventana* o *Rectángulo*. Pegá en Paint y guardá como PNG en `TP4/figs/ltspice/`, con el nombre de la tabla.
- **Agregar curvas:** clic derecho en el gráfico → *Add Traces* y escribís la expresión (por ejemplo `V(out)/V(pa_in)`).
- **Varios paneles:** clic derecho → *Add Plot Pane*. Sirve para poner módulo y fase o dos señales una arriba de otra.
- **Ejes:** clic derecho sobre un eje → *Manual Limits*, para hacer zoom en la banda de paso (por ejemplo, 600–1600 Hz y −1 a +0,6 dB).
- **Fase:** clic derecho sobre el eje derecho → *Don't plot phase* o *Phase*.
- **Cursores:** clic en el nombre de la curva → aparece un cursor con frecuencia y dB. Sirve para mostrar el valor en 200 Hz y 5 kHz.
- **Fondo blanco** (queda mejor impreso): *Tools → Color Preferences → WaveForm → Background* en blanco y *Grid* en gris claro.

### Lista
| Archivo PNG | Simulación | Qué graficar |
|---|---|---|
| `esq_ci.png` | `filtro_ci_ideal.asc` | Captura del **esquemático** completo con las directivas |
| `ci_etapa_pb.png` | `filtro_ci_ideal` | `V(pb)` (módulo y fase) |
| `ci_etapa_pa.png` | `filtro_ci_ideal` | `V(out)/V(pa_in)` |
| `ci_total.png` | `filtro_ci_ideal` | `V(out)` (módulo y fase) |
| `ci_atenuacion.png` | `filtro_ci_ideal` | `1/V(out)` en dB (atenuación), con cursores en 200 Hz y 5 kHz |
| `ci_banda_paso.png` | `filtro_ci_ideal` | `V(out)` con zoom en 600–1600 Hz |
| `ci_lm324.png` | `filtro_ci_lm324` | `V(out)` y `V(pb)`; además, una captura con zoom en la banda de paso |
| `esq_peor_caso.png` | `filtro_ci_peor_caso.asc` | Esquemático con las expresiones `{...*(1±s*tol)}` |
| `peor_caso_wp.png` | `filtro_ci_peor_caso_wp` | `V(out)`: aparecen las 3 curvas del `.step` |
| `peor_caso_bw.png` | `filtro_ci_peor_caso` | `V(out)`: las 3 curvas |
| `inestable.png` | `filtro_ci_inestable` | `V(out)` en función del tiempo (crece sin límite) |
| `esq_mc.png` | `filtro_ci_mc_10.asc` | Esquemático con los `{mc(...)}` |
| `ci_mc_10.png`, `_05`, `_01` | `filtro_ci_mc_*` | `V(out)`: las 500 curvas superpuestas |
| `esq_ug.png` | `filtro_ug_ideal.asc` | Esquemático |
| `ug_total.png` | `filtro_ug_ideal` | `V(out)` |
| `ug_mc_10.png` | `filtro_ug_mc_10` | `V(out)`: las 500 curvas |
| `esq_osc.png` | `oscilador_wien.asc` | Esquemático |
| `osc_arranque.png` | `oscilador_wien` | `V(out)` de 0 a 3 ms |
| `osc_permanente.png` | `oscilador_wien` | `V(out)` con zoom en 39,75–40 ms |
| `osc_fft.png` | `oscilador_wien` | En el gráfico: *View → FFT* → `V(out)`, eje X lineal de 0 a 120 kHz |
| `osc_slew.png` | `oscilador_wien_slew` | Dos paneles: `V(out)` y `d(V(out))` (derivada, en V/s). Hacé lo mismo con `oscilador_wien` para comparar: con 18k/4,7k la derivada se aplana en ±500 kV/s = 0,5 V/µs |

`d()` es la derivada en LTspice: `d(V(out))` da dV/dt.

### Lo que queda en Python (y se aclara en el informe)
- Histogramas de ripple y atenuación del Montecarlo, comparando las dos topologías (agregado 1).
- Porcentaje de corridas que cumplen la plantilla (agregado 2). Sale de las tablas de `.meas` del `.log`, que LTspice no resume.
- Estimación del porcentaje de circuitos inestables, con el modelo analítico.
