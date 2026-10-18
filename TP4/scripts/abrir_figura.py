"""
Abre una figura guardada por graficos_tp4.py como ventana interactiva de matplotlib
(zoom, desplazamiento, cambio de ejes y guardado en otro formato), sin volver a simular.

Uso:  python TP4/scripts/abrir_figura.py                    (muestra la lista y pregunta cuál abrir)
      python TP4/scripts/abrir_figura.py sim_ci_total       (abre esa figura directamente)
      python TP4/scripts/abrir_figura.py osc_arranque osc_espectro   (varias a la vez)
"""
import pickle
import sys
from pathlib import Path

import matplotlib.pyplot as plt

PKL = Path(__file__).resolve().parents[1] / "figs" / "pkl"

disponibles = sorted(p.stem for p in PKL.glob("*.pkl"))
if not disponibles:
    sys.exit(f"No hay figuras en {PKL}. Corré primero graficos_tp4.py.")

nombres = sys.argv[1:]
if not nombres:
    for i, n in enumerate(disponibles, 1):
        print(f"{i:3d}  {n}")
    eleccion = input("\nNúmero(s) de figura separados por espacio: ").split()
    nombres = [disponibles[int(x) - 1] for x in eleccion if x.isdigit() and 0 < int(x) <= len(disponibles)]

for nombre in nombres:
    archivo = PKL / f"{Path(nombre).stem}.pkl"
    if not archivo.exists():
        print(f"No existe la figura '{nombre}'.")
        continue
    with open(archivo, "rb") as f:
        pickle.load(f)          # al cargarla, matplotlib la registra como una figura más de pyplot

plt.show()
