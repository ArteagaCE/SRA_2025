"""
Utilidades para correr las simulaciones del TP4 desde Python con spicelib.

Flujo:  esquemático .asc (LTspice)  ->  netlist .net  ->  copia normalizada  ->  SpiceEditor
        ->  cambio de valores desde Python  ->  LTspice en modo batch  ->  lectura de .raw/.log
"""
import re
import shutil
from pathlib import Path

import numpy as np
from spicelib import RawRead, SimRunner, SpiceEditor
from spicelib.log.ltsteps import LTSpiceLogReader
from spicelib.simulators.ltspice_simulator import LTspice

TP4 = Path(__file__).resolve().parents[1]
CORRIDAS = TP4 / "resultados" / "corridas"     # archivos temporales de cada simulación
CORRIDAS.mkdir(parents=True, exist_ok=True)

# Nombres del esquemático que spicelib no acepta (minúsculas o una sola letra) -> nombre en la netlist.
# Se usan los nombres del informe para que el script sea legible.
RENOMBRAR = {
    "R": "R2",          # PB: resistencia serie al terminal + (15k)
    "r1": "Rk1", "r2": "Rk2",       # PB: k = 1 + Rk2/Rk1
    "r1b": "Rk3", "r2b": "Rk4",     # PA: k = 1 + Rk4/Rk3
    "Res1": "R3", "R8": "R4",       # PA: R3 a la salida, R4 a masa
}


def netlist_desde_asc(asc, nombre=None):
    """Genera la netlist del esquemático con LTspice y devuelve un SpiceEditor sobre una copia normalizada."""
    asc = Path(asc)
    nombre = nombre or asc.stem
    copia = CORRIDAS / f"{nombre}.asc"
    shutil.copy(asc, copia)
    net = Path(LTspice.create_netlist(copia))
    lineas = []
    for linea in net.read_text(encoding="utf-8", errors="replace").splitlines():
        partes = linea.split(maxsplit=1)
        if partes and partes[0] in RENOMBRAR:
            linea = RENOMBRAR[partes[0]] + (" " + partes[1] if len(partes) > 1 else "")
        # spicelib no acepta "/" en el nombre del modelo (LM324/NS): se usa una copia de la librería sin la barra
        linea = linea.replace("LM324/NS", "LM324_NS")
        if linea.lower().startswith(".include") and "LM324_NS.lib" in linea:
            lib = Path(linea.split(maxsplit=1)[1].strip().strip('"'))
            copia_lib = CORRIDAS / "LM324_NS_sin_barra.lib"
            copia_lib.write_text(lib.read_text(encoding="latin1").replace("LM324/NS", "LM324_NS").rstrip() + "\n",
                                 encoding="latin1")
            linea = f".include {copia_lib}"
        lineas.append(linea)
    net.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    return SpiceEditor(str(net))


def nuevo_runner(paralelas=8):
    return SimRunner(simulator=LTspice, output_folder=str(CORRIDAS), parallel_sims=paralelas)


def leer_meas(log, nombres=("gmax", "gmin", "g200", "g5k")):
    """Mediciones .meas de una corrida, en dB cuando LTspice las informa en dB."""
    lr = LTSpiceLogReader(str(log))
    res = {}
    for n in nombres:
        v = lr.get_measure_value(n)
        if isinstance(v, complex) or hasattr(v, "mag_db"):
            v = v.mag_db() if hasattr(v, "mag_db") else 20*np.log10(abs(v))
        res[n] = float(v)
    return res


def eje(r, paso=0):
    """Eje de frecuencia o tiempo. spicelib no siempre lo reconoce en archivos sin .step."""
    try:
        return np.real(r.get_axis(paso))
    except RuntimeError:
        nombre = next(n for n in r.get_trace_names() if n.lower() in ("frequency", "time"))
        return np.real(np.asarray(r.get_trace(nombre).get_wave(paso)))


def leer_ac(raw, trazas=("V(out)",)):
    r = RawRead(str(raw))
    f = eje(r)
    return f, {t: np.asarray(r.get_trace(t).get_wave(0)) for t in trazas}


def leer_tran(raw, trazas=("V(out)",)):
    r = RawRead(str(raw))
    t = np.abs(eje(r))
    return t, {n: np.real(np.asarray(r.get_trace(n).get_wave(0))) for n in trazas}


def borrar(*archivos):
    for a in archivos:
        if a:
            for ext in ("", ".raw", ".log", ".op.raw", ".net"):
                p = Path(str(a))
                cand = p.with_suffix(ext) if ext else p
                cand.unlink(missing_ok=True)
