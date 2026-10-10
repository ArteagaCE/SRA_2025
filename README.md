# SRA_2025
Archivos utilizados para el desarrollo de los trabajos prácticos de la asignatura Síntesis de Redes Activas 2025.

## Estructura

```
docs/                      Guía de trabajos prácticos (PDF y versión .md para buscar)
lib/                       Modelos SPICE compartidos
  LM324_2polos.lib           LM324 simplificado de 2 polos (Ad0 = 100 dB, F1 = 10 Hz, F2 = 5,06 MHz)
  LM324_NS.lib               Macromodelo LM324/NS de National
  lmx24.lib, LM6181_CFA.lib
TP3/                       Compensación (VFA y CFA)
  circuito1/a_VFA-VFA/       {sim, scripts, figs}
  circuito1/b_VFA-CFA/
  circuito1/c_VFA-CFA_comp/
  circuito2/                 Fuente de tensión CC (informe entregado)
  marco_teorico/figs/
  informe/
TP4/                       Filtros activos (ver TP4/README.md)
  {sim, scripts, figs, informe}
```

Los `.asc` incluyen las librerías con rutas relativas a `lib/`, así que hay que abrirlos desde su carpeta dentro del repo.
