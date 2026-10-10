"""Lector mínimo de archivos .raw binarios de LTspice (análisis AC y transitorio, con .step)."""
from pathlib import Path

import numpy as np


def leer_raw(ruta):
    """Devuelve (variables, datos, runs).
    datos[nombre] es un array de forma (n_runs, n_puntos); runs = cantidad de corridas."""
    crudo = Path(ruta).read_bytes()
    marca = "Binary:\n".encode("utf-16-le")
    fin = crudo.index(marca) + len(marca)
    header = crudo[:fin].decode("utf-16-le")

    campos, variables, en_vars = {}, [], False
    for linea in header.splitlines():
        if en_vars:
            partes = linea.split()
            if len(partes) >= 3 and partes[0].isdigit():
                variables.append(partes[1])
                continue
            en_vars = False
        if linea.startswith("Variables:"):
            en_vars = True
        elif ":" in linea:
            k, v = linea.split(":", 1)
            campos[k.strip()] = v.strip()

    n_vars = len(variables)
    n_pts = int(campos["No. Points"])
    flags = campos.get("Flags", "")
    cuerpo = crudo[fin:]

    if "complex" in flags:
        arr = np.frombuffer(cuerpo, dtype=np.complex128, count=n_pts*n_vars).reshape(n_pts, n_vars)
    else:
        # transitorio: el tiempo es double y el resto float32
        dt = np.dtype([("t", "<f8")] + [(f"v{i}", "<f4") for i in range(1, n_vars)])
        rec = np.frombuffer(cuerpo, dtype=dt, count=n_pts)
        arr = np.column_stack([np.abs(rec["t"])] + [rec[f"v{i}"] for i in range(1, n_vars)])

    eje = arr[:, 0].real
    inicios = np.r_[0, np.where(np.diff(eje) < 0)[0] + 1]
    runs = len(inicios)
    largo = n_pts // runs
    datos = {v.lower(): arr[:runs*largo, i].reshape(runs, largo) for i, v in enumerate(variables)}
    return variables, datos, runs


def leer_meas(ruta_log):
    """Lee las tablas de .meas de un .log con .step. Devuelve {nombre: array de valores en dB}."""
    import re
    texto = Path(ruta_log).read_bytes()
    try:
        texto = texto.decode("utf-16-le") if texto[1:2] == b"\x00" else texto.decode("latin1")
    except UnicodeDecodeError:
        texto = texto.decode("latin1")
    res, actual = {}, None
    for linea in texto.splitlines():
        m = re.match(r"Measurement:\s*(\w+)", linea)
        if m:
            actual = m.group(1).lower(); res[actual] = []
            continue
        m = re.match(r"\s*\d+\s+\(([-\d.eE+]+)dB", linea)
        if actual and m:
            res[actual].append(float(m.group(1)))
    return {k: np.array(v) for k, v in res.items()}
