# src/utils.py
import json
from datetime import datetime

def validar_fecha(fecha_str):
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def cargar_datos(ruta):
    try:
        with open(ruta, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_datos(ruta, datos):
    with open(ruta, "w") as f:
        json.dump(datos, f, indent=4)