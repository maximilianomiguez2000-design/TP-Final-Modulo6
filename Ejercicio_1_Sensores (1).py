# -*- coding: utf-8 -*-
"""
Trabajo Final IPAP - Módulo 6 (Python)
Ejercicio 1: Sanitización y análisis estadístico de sensores (20 puntos)

Contiene:
  - limpiar_registro_sensor(registro_raw)                       -> Apartado A
  - generar_resumen_sensores(lista_sensores_limpios, umbral)    -> Apartado B
  - Demostración completa al ejecutar el archivo.
"""

import re

UBICACION_PREDETERMINADA = "Sin ubicación"


# ---------------------------------------------------------------------------
# APARTADO A: Limpieza de datos
# ---------------------------------------------------------------------------
def limpiar_registro_sensor(registro_raw):
    """Recibe un diccionario 'sucio' y devuelve un diccionario limpio.

    - sensor_id: sin espacios al inicio/final (y sin espacios repetidos adentro).
    - temperatura: float, sin unidades (°C, C, grados, etc.).
    - ubicacion: si falta o viene vacía, se usa un valor predeterminado.
    """
    # 1) Identificador: quitar espacios innecesarios
    #    (la clave de entrada es "sensor_id", según el ejemplo de la consigna)
    id_sensor = str(registro_raw.get("sensor_id", "")).strip()
    id_sensor = re.sub(r"\s+", " ", id_sensor)

    # 2) Temperatura: convertir a float eliminando unidades
    temp_raw = registro_raw.get("temperatura")
    if isinstance(temp_raw, (int, float)):
        temperatura = float(temp_raw)
    else:
        texto = str(temp_raw).strip().replace(",", ".")  # "23,5" -> "23.5"
        # Se conserva solo el primer número (con signo y decimales opcionales)
        coincidencia = re.search(r"-?\d+(?:\.\d+)?", texto)
        if coincidencia is None:
            raise ValueError(
                f"Temperatura no válida en el sensor '{id_sensor}': {temp_raw!r}"
            )
        temperatura = float(coincidencia.group())

    # 3) Ubicación: valor seguro cuando falta el dato
    ubicacion = registro_raw.get("ubicacion")
    if ubicacion is None or str(ubicacion).strip() == "":
        ubicacion = UBICACION_PREDETERMINADA
    else:
        ubicacion = str(ubicacion).strip()

    return {"sensor_id": id_sensor, "temperatura": temperatura, "ubicacion": ubicacion}


# ---------------------------------------------------------------------------
# APARTADO B: Análisis estadístico
# ---------------------------------------------------------------------------
def generar_resumen_sensores(lista_sensores_limpios, umbral_temperatura):
    """Devuelve la tupla (ids_en_alerta, promedio_general).

    - ids_en_alerta: lista con los sensor_id de sensores cuya temperatura SUPERA
      el umbral (estrictamente mayor).
    - promedio_general: promedio de temperatura de todos los sensores
      (0.0 si la lista está vacía).
    """
    ids_en_alerta = [
        sensor["sensor_id"]
        for sensor in lista_sensores_limpios
        if sensor["temperatura"] > umbral_temperatura
    ]

    if lista_sensores_limpios:
        total = sum(sensor["temperatura"] for sensor in lista_sensores_limpios)
        promedio = total / len(lista_sensores_limpios)
    else:
        promedio = 0.0

    return ids_en_alerta, promedio


# ---------------------------------------------------------------------------
# DEMOSTRACIÓN
# ---------------------------------------------------------------------------
def main():
    registros_originales = [
        {"sensor_id": " SENSOR-001 ", "temperatura": "24.5C", "ubicacion": "Planta Norte"},
        {"sensor_id": "SENSOR-002", "temperatura": "31,2C", "ubicacion": None},
        {"sensor_id": " SENSOR-003  ", "temperatura": 45, "ubicacion": "Sala de máquinas"},
        {"sensor_id": "SENSOR-004", "temperatura": " 38.7 grados ", "ubicacion": "   "},
        {"sensor_id": "SENSOR-005", "temperatura": "-4.5°C", "ubicacion": "Cámara fría"},
        {"sensor_id": "SENSOR-006", "temperatura": "27.0"},  # sin clave 'ubicacion'
    ]
    umbral = 35.0

    print("=" * 60)
    print("EJERCICIO 1 - SENSORES: LIMPIEZA Y ANÁLISIS")
    print("=" * 60)

    print("\n[1] REGISTROS ORIGINALES (sin limpiar)")
    for registro in registros_originales:
        print("   ", registro)

    print("\n[2] LIMPIEZA DE REGISTROS")
    sensores_limpios = []
    for registro in registros_originales:
        try:
            limpio = limpiar_registro_sensor(registro)
            sensores_limpios.append(limpio)
            print("   ", limpio)
        except ValueError as error:
            print("    Registro descartado:", error)

    # Caso inválido a propósito, para mostrar el manejo de errores
    print("\n    Prueba con un dato inválido:")
    try:
        limpiar_registro_sensor({"sensor_id": "SENSOR-999", "temperatura": "sin dato"})
    except ValueError as error:
        print("    Error capturado correctamente ->", error)

    print(f"\n[3] ANÁLISIS ESTADÍSTICO (umbral = {umbral} °C)")
    en_alerta, promedio = generar_resumen_sensores(sensores_limpios, umbral)
    print("    Tupla devuelta:", (en_alerta, promedio))

    print("\n[4] REPORTE FINAL")
    print("-" * 60)
    print(f"{'Sensor':<12}{'Temp. (°C)':>12}  {'Ubicación':<20}{'Estado':<8}")
    print("-" * 60)
    for sensor in sensores_limpios:
        estado = "ALERTA" if sensor["sensor_id"] in en_alerta else "OK"
        print(
            f"{sensor['sensor_id']:<12}{sensor['temperatura']:>12.1f}  "
            f"{sensor['ubicacion']:<20}{estado:<8}"
        )
    print("-" * 60)
    print(f"Sensores analizados : {len(sensores_limpios)}")
    print(f"Sensores en alerta  : {len(en_alerta)} -> {', '.join(en_alerta) or 'ninguno'}")
    print(f"Temperatura promedio: {promedio:.2f} °C")


if __name__ == "__main__":
    main()
