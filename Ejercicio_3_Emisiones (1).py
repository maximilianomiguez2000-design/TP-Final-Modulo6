# -*- coding: utf-8 -*-
"""
Trabajo Final IPAP - Módulo 6 (Python)
Ejercicio 3: Pruebas unitarias e integración web (40 puntos)

Contiene:
  - calcular_emisiones_carbono(consumo_kwh, factor_emision=0.4)
  - TestCalculoEmisiones(unittest.TestCase)
  - obtener_metricas_consumo(registros)
  - vista_panel_sustentabilidad(request)   (vista Django basada en función)

Ejecución directa:  python Ejercicio_3_Emisiones.py
  -> corre las pruebas unitarias y una demostración de las métricas.

Uso dentro de Django:
  - Copiar las funciones a views.py de la app (o importarlas desde allí).
  - Guardar panel.html en  <app>/templates/sustentabilidad/panel.html
  - Registrar la vista en urls.py:
        path("sustentabilidad/", vista_panel_sustentabilidad)
"""

import unittest

# Django solo es necesario para la vista. Si no está instalado (por ejemplo,
# al ejecutar este archivo como script suelto), se usa un reemplazo mínimo de
# render() para que las pruebas y la demostración sigan funcionando.
try:
    from django.shortcuts import render
except ImportError:  # pragma: no cover
    def render(request, plantilla, contexto=None):
        return plantilla, contexto


# ---------------------------------------------------------------------------
# APARTADO A: Cálculo de emisiones
# ---------------------------------------------------------------------------
def calcular_emisiones_carbono(consumo_kwh, factor_emision=0.4):
    """Emisiones de carbono (kg CO2) = consumo en kWh * factor de emisión."""
    if consumo_kwh < 0:
        raise ValueError("El consumo no puede ser negativo.")
    return consumo_kwh * factor_emision


class TestCalculoEmisiones(unittest.TestCase):
    """Pruebas unitarias de calcular_emisiones_carbono."""

    # --- Cálculos nominales -------------------------------------------------
    def test_calculo_con_factor_predeterminado(self):
        self.assertAlmostEqual(calcular_emisiones_carbono(100), 40.0)

    def test_calculo_con_factor_personalizado(self):
        self.assertAlmostEqual(calcular_emisiones_carbono(250, 0.5), 125.0)

    def test_consumo_cero(self):
        self.assertEqual(calcular_emisiones_carbono(0), 0)

    def test_consumo_decimal(self):
        self.assertAlmostEqual(calcular_emisiones_carbono(12.5), 5.0)

    # --- Entradas inválidas -------------------------------------------------
    def test_consumo_negativo_lanza_value_error(self):
        with self.assertRaises(ValueError):
            calcular_emisiones_carbono(-10)

    def test_consumo_negativo_con_factor_personalizado(self):
        with self.assertRaises(ValueError):
            calcular_emisiones_carbono(-0.01, 0.3)


# ---------------------------------------------------------------------------
# APARTADO B: Integración con Django
# ---------------------------------------------------------------------------
def obtener_metricas_consumo(registros):
    """Procesa el historial de consumo de varias plantas.

    registros puede ser (la consigna no fija el formato, se aceptan ambos):
      - una lista de diccionarios {"planta": str, "consumo_kwh": número}
        (una planta puede aparecer varias veces: se acumula), o
      - un diccionario {planta: [consumos]} o {planta: consumo_total}.

    Devuelve un diccionario con:
      - emisiones_totales: emisiones globales (kg CO2)
      - planta_mayor_consumo: nombre de la planta con más kWh (None si no hay datos)
      - detalle_plantas: lista de {"planta", "consumo_kwh", "emisiones"}
    """
    consumo_por_planta = {}
    if isinstance(registros, dict):
        for planta, valores in registros.items():
            if not isinstance(valores, (list, tuple)):
                valores = [valores]
            consumo_por_planta[planta] = sum(valores)
    else:
        for registro in registros:
            planta = registro["planta"]
            consumo_por_planta[planta] = (
                consumo_por_planta.get(planta, 0) + registro["consumo_kwh"]
            )

    detalle_plantas = []
    emisiones_totales = 0.0
    for planta, consumo in consumo_por_planta.items():
        emisiones = calcular_emisiones_carbono(consumo)
        emisiones_totales += emisiones
        detalle_plantas.append(
            {"planta": planta, "consumo_kwh": consumo, "emisiones": emisiones}
        )

    planta_mayor_consumo = None
    if detalle_plantas:
        planta_mayor_consumo = max(
            detalle_plantas, key=lambda fila: fila["consumo_kwh"]
        )["planta"]

    return {
        "emisiones_totales": emisiones_totales,
        "planta_mayor_consumo": planta_mayor_consumo,
        "detalle_plantas": detalle_plantas,
    }


def vista_panel_sustentabilidad(request):
    """Vista Django (FBV): arma el contexto y renderiza la plantilla."""
    # En un proyecto real, estos datos vendrían de la base de datos (modelos).
    registros = [
        {"planta": "Planta Norte", "consumo_kwh": 1200},
        {"planta": "Planta Sur", "consumo_kwh": 850.5},
        {"planta": "Planta Este", "consumo_kwh": 2100},
        {"planta": "Planta Norte", "consumo_kwh": 300},
        {"planta": "Planta Oeste", "consumo_kwh": 640},
    ]

    metricas = obtener_metricas_consumo(registros)

    contexto = {
        "emisiones_totales": metricas["emisiones_totales"],
        "planta_mayor_consumo": metricas["planta_mayor_consumo"],
        "detalle_plantas": metricas["detalle_plantas"],
    }
    return render(request, "sustentabilidad/panel.html", contexto)


# ---------------------------------------------------------------------------
# EJECUCIÓN DIRECTA: pruebas + demostración
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("EJERCICIO 3 - PRUEBAS UNITARIAS")
    print("=" * 60)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCalculoEmisiones)
    resultado = unittest.TextTestRunner(verbosity=2).run(suite)

    print("\n" + "=" * 60)
    print("DEMOSTRACIÓN: obtener_metricas_consumo")
    print("=" * 60)
    datos = [
        {"planta": "Planta Norte", "consumo_kwh": 1200},
        {"planta": "Planta Sur", "consumo_kwh": 850.5},
        {"planta": "Planta Este", "consumo_kwh": 2100},
        {"planta": "Planta Norte", "consumo_kwh": 300},
        {"planta": "Planta Oeste", "consumo_kwh": 640},
    ]
    metricas = obtener_metricas_consumo(datos)
    print(f"Emisiones globales : {metricas['emisiones_totales']:.2f} kg CO2")
    print(f"Mayor consumo      : {metricas['planta_mayor_consumo']}")
    for fila in metricas["detalle_plantas"]:
        print(
            f"  {fila['planta']:<14} {fila['consumo_kwh']:>8.1f} kWh  "
            f"{fila['emisiones']:>8.2f} kg CO2"
        )

    print("\nResultado de las pruebas:",
          "TODAS APROBADAS" if resultado.wasSuccessful() else "HAY FALLOS")
