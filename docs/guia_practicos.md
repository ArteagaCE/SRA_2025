Universidad Nacional de Córdoba
Facultad de Ciencias Exactas, Físicas y Naturales
Escuela de Ingeniería Electrónica
Cátedra de
Síntesis de Redes Activas
Guía de Diseño y Trabajos Prácticos de
Laboratorio
Año 2022
Rev 2.1
Profesor Titular:
Ing. Pablo Ferreyra
Profesor Adjunto:
Ing. César Reale
Profesores Adscriptos:
Ings. Fabián Gómez, Daniel Sánchez
Ayudante alumno:
Lucas Duarte

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio
METODOLOGÍA GENERAL
a) Realizar una sintética introducción teórica del tema a tratar.
b) Analizar los circuitos propuestos, todos los cálculos analíticos y su desarrollo
numérico.
c) Simulación en PSPICE.
d) Analizar las condiciones de operación límite.
e) Armar el circuito y hacer las mediciones en laboratorio.
f) Finalmente comparar los valores calculados, simulados y medidos, y extraer
conclusiones a cerca de las diferencias. Analizar las causas.
g) Presentar un informe digital, bien redactado, inicializado con la propuesta del
problema presentado por la Cátedra, los responsables del trabajo y un análisis
profesional de cada ítem. La redacción debe ser acorde a un informe de un futuro
ingeniero.
LABORATORIOS PROPUESTOS
? Laboratorio N°1: AO Ideal: Circuitos Analógicos Lineales y No Lineales.
? Laboratorio N°2: AO Real: Errores.
? Proyecto N°1: Proyecto Balanza (Ing. Reale)
? Laboratorio N°3: Compensación
? Laboratorio N°4: Filtros Activos
? Proyecto N°2: Sistema de Osciladores y Filtros (Ing. Ferreyra)
El enunciado de los proyectos se entregará por separado.
Para promocionar se requieren los 4 practicos y los dos proyectos y dos parciales
aprobados o un parcial y el recuperatorio.
Para regularizar se requieren los 4 prácticos y los dos proyectos y un parcial
aprobado o unrecuperatorio.
. Los ejercicios adicionales son optativos (Ing. Sánchez).
- 2 -
Año 2020 Rev2.1

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio

Trabajo Práctico de Laboratorio Nº1
AO Ideal: Circuitos Analógicos Lineales y No Lineales

OBJETIVOS

Familiarizarse con el armado y análisis de circuitos analógicos lineales y no lineales. En este
Trabajo Práctico debe considerar para los cálculos iniciales el amplificador como ideal.

DESARROLLO

CIRCUITO I: AMPLIFICADOR DIFERENCIAL

  Datos: Amplificador Operacional LM324
             Vcc = 10V Vss = -10V
              R1 = R2 = R3 = R4 = R5 = R

PARÁMETROS/RELACIONES A ANALIZAR:
| ANALÍTICO:   (  V |                 | =( V + V       | )/2      V |  =( V  | - V )  )  |     |
| ----------------- | --------------- | -------------- | ---------- | ------ | --------- | --- |
|                   |                 | C 1            | 2          | D 2    | 1         |     |
|                   | 1.1.  Vo1 = f(V | V ); Vo1 = f(V |            | ,V )   |           |     |
|                   |                 | 1, 2           |            | C      |           |     |
D
|     | 1.2.  Vo2 = f(V | V ); Vo2 = f(V |     | ,V )   |     |     |
| --- | --------------- | -------------- | --- | ------ | --- | --- |
|     |                 | 1, 2           |     | D C    |     |     |
1.3.  Impedancia vista por las fuentes de señal.

MEDICIÓN - SIMULACIÓN:

  1.4. Gráfico Entrada/Salida: Vo1=f(V1) y Vo1 = f(V2)   Vss < V1,V2 < Vcc
  1.5. Gráfico Entrada/Salida: Vo1=f(V ) y Vo2 = f(V )    Vss < V  < Vcc
|     |     |     |     | C   | C   | C   |
| --- | --- | --- | --- | --- | --- | --- |

|     |     |     |     | - 3 -  |     |     |
| --- | --- | --- | --- | ------ | --- | --- |

|     |     |     |     |                         | Año 2020 Rev2.1  |     |
| --- | --- | --- | --- | ----------------------- | ---------------- | --- |

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio
CIRCUITO II: FUENTE DE CORRIENTE CONTROLADA POR TENSIÓN
Datos: Amplificador Operacional LM324
Vcc = 10V y Vss = -10V
R1 = 100?; R2 = 10K?; R3 = 1K? y R4 = 100K?
Vo
1
R1 4 11 R2
Vcc + - Vss
R3
Vin 3 2
RL R4
I
L
PARÁMETROS/RELACIONES A ANALIZAR:
2.1. I = f(R ,V ) ; Vo = f(V ,R ); RL =f(V )
RL L IN IN L MAX IN
2.2. Complete la siguiente tabla con Mediciones/Simulaciones
- 4 -
Año 2020 Rev2.1

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio
CIRCUITO III: RECTIFICADOR DE PRECISIÓN
Datos: Amplificador Operacional LM324
Vcc = 10V Vss = -10V
D1 = D2 = 1N4148
R1 = R3 = R4 = 10K? 1% y R2 = 5K? 1%
PARÁMETROS/RELACIONES A ANALIZAR:
ANALÍTICO:
3.1. Vo1 = f(Vin); Vo2 = f(Vin) con 0V < Vin (Ignorar Rd del diodo)
3.2. Vo1 = f(Vin); Vo2 = f(Vin) con Vin < 0V (Ignorar Rd del diodo)
MEDICIÓN - SIMULACIÓN:
3.3. Gráfico Entrada/Salida: Vo1=f(Vin) y Vo2 = f(Vin) Vss < Vin < Vcc
- 5 -
Año 2020 Rev2.1

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio
CIRCUITO IV: COMPARADOR CON HISTÉRISIS
Datos: Amplificador Operacional LM324
V+ = 10V V- = 0V
R1 = R2 = R4 = 10K? y R3 = 2K?
Vref=2V
*
PARÁMETROS/RELACIONES A ANALIZAR:
ANALÍTICO:
4.1. Umbral de conmutación cuando Vo=V+
4.2. Umbral de conmutación cuando Vo=V-
MEDICIÓN - SIMULACIÓN:
4.3. Gráfico Entrada/Salida: Vo=f(Vi) V- < Vi < V+
EJERCICIO ADICIONAL I:
Diseñar un regulador de carga de bateria, que corte cuando se alcanzan los 12.8V y
reinicie la carga cuando baja a 10.5V.
Materiales:
? AO ideal con saturación.
? Resistencias
? 1 Rele 12V, Normal Abierto, 20mA de corriente de bobina.
? 1 Transistor NPN B548 o 1 Transistor PNP BC558.
? 1 Diodo 1N4148
? 1 Referencia de Tensión: TL431
? Bateria 12V (Rango 8V a 13V) – Rinterna=0.5?
? Celda Fotovoltaica: 15V Tension Sin Carga, 1A de Corriente de Carga
EJERCICIO ADICIONAL II:
Diseñar un oscilador de relajación que oscile a 1kHz.
Materiales:
? AO ideal con saturación. Vcc=10V Vss=-10V
? Resistencias
? Capcitor de 1uF
- 6 -
Año 2020 Rev2.1

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio
Trabajo Práctico de Laboratorio Nº2
AO Real: Errores.
OBJETIVOS
Introducir al estudiante en el diseño, armado, medición y análisis de circuitos
amplificadores lineales, teniendo en cuenta las fuentes de error del AO real, y como se
relacionan con las condiciones de entorno del circuito.
DESARROLLO
CIRCUITO I: El circuito sumador siguiente debe ser diseñado para las siguientes
condiciones de contorno:
Rf
Zi1
R
-
Vo
+ R +
v
1-
+
v Zi2
2-
? Amplificador Operacional LM741 o LM324
? Alimentación Vcc = 10V, Vss = -10V
? Ganancia en banda media A=Vo/V1 y A=Vo/V2 debe ser igual a 30 veces.
? Zi del amplificador no puede alterar o cargar la fuente de señal, es decir, Ri << Zi1 y
Zi2. (al menos 10 veces)
? Usar Resistencias <=1M?
Las fuentes V1 y V2 deben considerarse en las condiciones 1.A y 1.B
Ri
v v
y
1.A.- Ri = 50? + 1 2
1.B.- Ri = 100K? v
i -
- 7 -
Año 2020 Rev2.1

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio
PARÁMETROS/RELACIONES A ANALIZAR:
ANALÍTICO:
1.1. Vo = f(V V )
1, 2
1.2. Errores DC
1.3. Errores AC: Ancho de Banda Plena Potencia f (10Vpap)
HP
1.4. Errores AC: Ancho de banda de Pequeña Señal f
H
1.5. Errores AC: Tabla de Error Vectorial Normalizado
MEDICIÓN - SIMULACIÓN:
1.6 Gráfico Entrada/Salida: Vo=f(V1) Vss < V1 < Vcc
1.7 Errores DC
1.8 Errores AC: Medicion del Slew Rate
1.9 Errores AC: Diagrama BODE
- 8 -
Año 2020 Rev2.1

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio
EJERCICIO ADICIONAL I:
Analizar la operación del circuito de la figura siguiente
Vp
Rp bRp
Vd U1 R2 aR2
+
-
Rp Rp Zp
R1
- Vout
-Vp aR1 + U2
? Amplificador Operacional LM324
? Alimentación Vcc = 5V, Vss = -5V
? Rp =3,3K?;
? Considerar b del circuito es ?. Entonces ?Rp es un potenciómetro multivuelta 5K?;
? R1 = R2 = 2,2K?
? Considerar a del circuito es ?. Hacer ?R1 = ?R2 = 47K?
Calcular y Evaluar:
1. Calcular los siguientes parámetros: Vo/Vd (ganancia del amplificador);
Vo=f(?) ; sensibilidad nominal del puente + amplificador (v.gr. : dVo/d? para
?=1).
2. Calcular los errores de DC debido a: Tensiones de offset, corrientes de bias,
ganancia diferencial finita y CMRR finita. Calcular según datos de manual del AO
el fondo de escala FS permisible en cada arquitectura y a partir de allí la máxima
precisión alcanzable en bits.
3. Simular la operación del circuito con SPICE y estimar los valores
anteriormente calculados.
4. Armar el circuito en laboratorio utilizando el operacional indicado junto a
cada figura. Trabajar con resistencias al 1% de tolerancia.
5. Cotejar resultados teóricos y experimentales. Particularmente verificar
ganancia, sensibilidad, máxima excursión de salida sin distorsión (y por lo tanto
máximo ? permisible), errores DC, rechazo al modo común. Para esto último
hacer ?=1 y variar Vp lentamente (v.gr.: Vp=10V+1V sen(2?50t)) verificando que
la salida Vo permanece esencialmente invariante.
- 9 -
Año 2020 Rev2.1

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio
Trabajo Práctico de Laboratorio Nº3
OBJETIVOS
Diseñar amplificadores utilizando tecnologías VFA y CFA, aplicando conceptos de
compensación.
METODOLOGÍA
En general, para cada uno de los casos particulares solicitados, se debe:
a) Realizar una sintética introducción teórica.
b) Analizar el circuito propuesto, su desarrollo numérico, todos los cálculos
analíticos.
c) Realizar simulación en PSPICE.
d) Armar el circuito y hacer las mediciones en laboratorio.
e) Finalmente comparar los valores calculados, simulados y medidos, y extraer
conclusiones a cerca de las diferencias. Analizar las causas.
f) Presentar un informe digital y en papel.
- 10 -
Año 2020 Rev2.1

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio

Rf
DESARROLLO
CIRCUITO 1
|     |     |     |     |     | Ri  |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- |

|     |     |     |     |     |     | -   | A02 |
| --- | --- | --- | --- | --- | --- | --- | --- |
Vout
|   Las  | figuras  | muestran  | un  amplificador  |     |     |     | +   |
| ------ | -------- | --------- | ----------------- | --- | --- | --- | --- |
+
|     |     |     |     |     |     | A01 | -   |
| --- | --- | --- | --- | --- | --- | --- | --- |
compuesto que deberá ser diseñado para obtener
|     |     |     |     |     |     |     | R2  |
| --- | --- | --- | --- | --- | --- | --- | --- |
una ganancia global Avf = 20dB, compensándolo
|                |      |         |             |     | Vin |     |     |
| -------------- | ---- | ------- | ----------- | --- | --- | --- | --- |
| para  obtener  | una  | máxima  | planicidad  | de  |     |     |     |

| módulo (M? = 65º o Qp = 0,707).  |     |     |     |     |     |     | R1  |
| -------------------------------- | --- | --- | --- | --- | --- | --- | --- |
|                                  |     |     |     |     |     |     |     |

VFA-VFA:
a. Utilizando tecnologías VFA + VFA. Como amplificador VFA se utilizará un LM324,
de 2(dos) polos (Ad  = 100dB, F  = 1MHz, F  = 10Hz y F  = 5,06MHz).
|     |     | 0   | T   | 1   | 2   |     |     |
| --- | --- | --- | --- | --- | --- | --- | --- |

a.1. Diseñar el amplificador compuesto VFA + VFA.
a.2.  Calcular  el  ancho  de  banda  potencial,  la  frecuencia  del  polo  de  la  función  de
transferencia a lazo cerrado y ancho de banda a -3dB.
a.3  Medir el ancho de banda a -3dB.
a.4. Estimar el margen de fase obtenido en base a la respuesta al escalón del amplificador
| compuesto.  |     |     |     |     |     |     |     |
| ----------- | --- | --- | --- | --- | --- | --- | --- |

VFA-CFA:
b. Utilizando tecnologías VFA + CFA. Se sugiere como amplificador VFA un LM324, de
2(dos) polos (Ad0  = 100dB, FT = 1MHz, F1 = 10Hz y F2 = 5,06MHz) y como CFA un
LM6181 con RT = 2,37M?, CT = 4,8pF, cuya transimpedancia ZT presenta también 2(dos)
polos (F1 = 14KHz, F2 = 82,3MHz).

b.1. Diseñar el amplificador compuesto VFA + CFA para máxima planicidad de módulo y que
además cumpla con un ancho de banda potencial aproximado de fg = 2MHz. Tener en cuenta la
presencia del segundo polo del VFA.
b.2.  Calcular  el  ancho  de  banda  potencial,  la  frecuencia  del  polo  de  la  función  de
transferencia a lazo cerrado y ancho de banda a -3dB.
b.3  Medir el ancho de banda a -3dB.
b.4. Estimar el margen de fase obtenido en base a la respuesta al escalón del amplificador
compuesto.

VFA-CFA II:
c. Insertar en la configuración anterior una red de compensación cero – polo (a la
salida del VFA) de tal modo que el cero de la red cancele el segundo polo del VFA. Ubicar el
polo de la red a una octava de su cero. Retocar la ganancia del CFA realimentado para
compensar la atenuación introducida por la red. Constatar la mejora del margen de fase
a través de la respuesta al escalón.

c.1. Calcular y medir el margen de fase, el ancho de banda potencial, la frecuencia del polo
de la función de transferencia a lazo cerrado y ancho de banda a -3dB.
 c.2.  Calcular  el  ancho  de  banda  potencial,  la  frecuencia  del  polo  de  la  función  de
transferencia a lazo cerrado y ancho de banda a -3dB.
 c.3 Medir el ancho de banda a -3dB.
          c.4. Estimar el margen de fase obtenido en base a la respuesta al escalón del amplificador
compuesto.

|     |     |     | - 11 -                  |     |                  |     |     |
| --- | --- | --- | ----------------------- | --- | ---------------- | --- | --- |
|     |     |     |                         |     |                  |     |     |
|     |     |     |                         |     | Año 2020 Rev2.1  |     |     |

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio
CIRCUITO 2
Diseñar una Fuente de Tensión CC.
Elementos:
? Capacitores y resistores
? Fuente CC 12V
? AO LM324
? Referencia de Tensión 2,5V (TL431 o LT1004-2.5)
? Transistor BJT (2N3019)
Especificaciones:
? Fuente 5V/500mA
? Tolerancia de Tensión regulada: 0,1V.
? La variación (ripple) máxima admitida es de 1%.
? La carga puede variar entre 50% (250mA) y 100% (500mA) abruptamente.
Se pide:
? Agregar los componentes necesarios para alcanzar las especificaciones.
? Simular el transitorio de los primeros 50ms, medir valor medio y ripple de estado
estable.
- 12 -
Año 2020 Rev2.1

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio
Trabajo Práctico de Laboratorio Nº4
OBJETIVOS
En base a la planilla de requerimientos suministrada, sintetizar un circuito basado en
amplificadores operacionales que satisfaga esos requisitos.
METODOLOGÍA
a) Realizar una sintética introducción teórica.
b) Analizar el problema propuesto, su desarrollo numérico, todos los cálculos analíticos
y la simulación en PSPICE.
c) Analizar las condiciones de operación límite.
d) Armar el circuito y hacer las mediciones en laboratorio.
e) Finalmente comparar los valores calculados, simulados y medidos, y extraer
conclusiones a cerca de las diferencias. Analizar las causas.
f) Presentar un informe digital y en papel.
DESARROLLO
1. En base a la planilla de requerimientos de la figura 5.1, se pide:
1.1. Aproximar la función de atenuación mediante polinomios de Chebychev,
utilizando Matlab o aplicación similar.
1.2. Sintetizar un circuito que satisfaga los requerimientos del punto anterior
utilizando topologías bicuadráticas de realimentación positiva o negativa, a elección.
1.3. Simular cada etapa y el filtro total con Pspice o similar.
1.4. Calcular la sensibilidad de la frecuencia del polo de cada bicuadrática (?p) y del
ancho de banda (?p/Qp).
1.5. Analizar la peor desviación si todos los elementos tienen una tolerancia del 10%.
1.6. Realizar una simulación de Montecarlo de las desviaciones con Pspice o similar.
1.7. Armar el circuito, medir experimentalmente las curvas de atenuación y desfasaje.
Contrastarlas con las predicciones teóricas y las simulaciones.
EJERCICIO ADICIONAL:
Diseñar un oscilador de f=12kHz. Simular y ajustar a una tolerancia de +/- 100Hz.
Elementos:
? Capacitores y resistores
? Fuente CC +/- 12V
? AO LM324
- 13 -
Año 2020 Rev2.1

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio

|     | - 14 -  |     |
| --- | ------- | --- |

|     |                         | Año 2020 Rev2.1  |
| --- | ----------------------- | ---------------- |

Cátedra de Síntesis de Redes Activas
Trabajos Prácticos de Laboratorio
Anexo: Script MATLAB
%SRA - Trabajo Practico de Laboratorio N°4
clc;
clear;
close all;
%% Parametros de Entrada
fp=[800 1250]; %Banda de Paso [Hz]
fs=[200 5000]; %Banda de Rechazo [Hz]
Wp=2*pi*fp; %Banda de Paso [rad/s]
Ws=2*pi*fs; %Banda de Rechazo [rad/s]
Ap=0.25; %Atenuacion maxima en Banda de Paso [dB]
As=30; %Atenuacion minima en Banda de Rechazo [dB]
%% Calculo de FT
[n,Wp]=cheb1ord(Wp,Ws,Ap,As,'s');
[num,den]=cheby1(n,Ap,Wp,'s');
Filtro=tf(num,den) %Funcion de transferencia calculada
[sos,g] = tf2sos(num,den); %Descomponemos en bicuadrativas
%Implementacion como PasaAlto/PasaBajo
PasaBajo=tf(2*g*sos(1,1:3),sos(1,4:6))
PasaAlto=tf(1/2*sos(2,1:3),sos(2,4:6))
%% Graficos
figure;
hold on;
%Especificaciones Filtro
plot([fs(1)/10 fs(1) fs(1)],[-As -As -Ap],'Color','r','LineWidth',3);
plot([fs(2) fs(2) fs(2)*10],[-Ap -As -As],'Color','r','LineWidth',3);
plot([fp(1) fp(1) fp(2) fp(2)],[-As -Ap -Ap -As],'Color','g','LineWidth',3);
%Filtro
h = bodeplot(Filtro);
p = getoptions(h);
p.PhaseVisible='off';
p.FreqUnits='Hz';
p.Grid='on';
setoptions(h,p);
bode(PasaBajo);
bode(PasaAlto);
- 15 -
Año 2020 Rev2.1
