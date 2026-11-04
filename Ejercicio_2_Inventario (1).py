# -*- coding: utf-8 -*-
"""
Trabajo Final IPAP - Módulo 6 (Python)
Ejercicio 2: Modelo de productos, excepciones y persistencia (40 puntos)

Contiene:
  - StockInvalidoError          -> excepción personalizada
  - DispositivoEcológico        -> clase base (stock encapsulado)
  - PanelSolar                  -> clase derivada
  - GestorInventario            -> persistencia en JSON
  - Demostración completa al ejecutar el archivo (genera catalogo_ecotech.json).
"""

import json
import os


# ---------------------------------------------------------------------------
# APARTADO A: Programación orientada a objetos
# ---------------------------------------------------------------------------
class StockInvalidoError(Exception):
    """Se lanza cuando se intenta asignar un stock inválido (negativo)."""


class DispositivoEcológico:
    """Clase base de los dispositivos de EcoTech."""

    def __init__(self, nombre, precio, stock):
        self.nombre = nombre
        self.precio = precio
        self.stock = stock  # pasa por el setter, que valida el valor

    # --- Encapsulamiento del stock -----------------------------------------
    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, valor):
        if valor < 0:
            raise StockInvalidoError(
                f"El stock no puede ser negativo (se recibió {valor})."
            )
        self._stock = valor

    # --- Polimorfismo: cada clase redefine estos métodos -------------------
    def ficha_comercial(self):
        return (
            f"{self.nombre} | Precio: ${self.precio:,.2f} | "
            f"Stock disponible: {self.stock} unidades"
        )

    def ficha_tecnica(self):
        return f"{self.nombre} | Dispositivo ecológico genérico"

    # --- Conversión a datos serializables ----------------------------------
    def to_dict(self):
        return {
            "tipo": self.__class__.__name__,
            "nombre": self.nombre,
            "precio": self.precio,
            "stock": self.stock,
        }


class PanelSolar(DispositivoEcológico):
    """Panel solar: hereda nombre, precio y stock y agrega atributos propios."""

    def __init__(self, nombre, precio, stock, potencia_w, eficiencia):
        super().__init__(nombre, precio, stock)
        self.potencia_w = potencia_w      # potencia nominal en watts
        self.eficiencia = eficiencia      # porcentaje (ej. 21.5)

    def ficha_comercial(self):
        return (
            f"PANEL SOLAR {self.nombre} - {self.potencia_w} W | "
            f"Precio: ${self.precio:,.2f} | Stock: {self.stock} unidades"
        )

    def ficha_tecnica(self):
        return (
            f"Panel solar {self.nombre} | Potencia: {self.potencia_w} W | "
            f"Eficiencia: {self.eficiencia}%"
        )

    def to_dict(self):
        datos = super().to_dict()
        datos["potencia_w"] = self.potencia_w
        datos["eficiencia"] = self.eficiencia
        return datos


# ---------------------------------------------------------------------------
# APARTADO B: Persistencia de datos
# ---------------------------------------------------------------------------
class GestorInventario:
    """Administra el guardado del catálogo de dispositivos."""

    def guardar_catalogo_json(self, lista_dispositivos, ruta_archivo):
        """Guarda la lista de dispositivos como JSON en ruta_archivo."""
        catalogo = [dispositivo.to_dict() for dispositivo in lista_dispositivos]
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            json.dump(catalogo, archivo, ensure_ascii=False, indent=4)
        return ruta_archivo


# ---------------------------------------------------------------------------
# DEMOSTRACIÓN
# ---------------------------------------------------------------------------
def main():
    print("=" * 60)
    print("EJERCICIO 2 - INVENTARIO ECOTECH")
    print("=" * 60)

    # 1) Producto con stock negativo -> debe fallar de forma controlada
    print("\n[1] Intento de crear un producto con stock negativo")
    try:
        PanelSolar("PS-Defectuoso", 100000, -5, 400, 20.0)
        print("    ERROR: no debería haberse creado.")
    except StockInvalidoError as error:
        print("    StockInvalidoError capturada ->", error)
    print("    El programa continúa funcionando con normalidad.")

    # 2) Productos válidos
    print("\n[2] Creación de productos válidos")
    panel_1 = PanelSolar("SunPower X400", 185000.50, 25, 400, 22.8)
    panel_2 = PanelSolar("EcoPanel Mono 550", 242500.00, 12, 550, 21.5)
    generico = DispositivoEcológico("Cargador solar portátil", 38900.00, 40)
    productos = [panel_1, panel_2, generico]
    print(f"    Se crearon {len(productos)} productos.")

    # 3) Fichas (polimorfismo: mismo método, distinta salida)
    print("\n[3] Fichas comercial y técnica (polimorfismo)")
    for producto in productos:
        print("    Comercial:", producto.ficha_comercial())
        print("    Técnica  :", producto.ficha_tecnica())
        print()

    # El setter también protege las modificaciones posteriores
    print("[4] Intento de poner stock negativo a un producto existente")
    try:
        panel_1.stock = -1
    except StockInvalidoError as error:
        print("    StockInvalidoError capturada ->", error)
    print(f"    El stock sigue siendo {panel_1.stock}.")

    # 4) Exportación JSON
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catalogo_ecotech.json")
    print("\n[5] Exportación del catálogo a JSON")
    GestorInventario().guardar_catalogo_json(productos, ruta)
    print("    Archivo generado:", ruta)

    # 5) Comprobación: el archivo existe y se puede leer
    print("\n[6] Comprobación del archivo generado")
    if os.path.exists(ruta) and os.path.getsize(ruta) > 0:
        with open(ruta, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
        print(f"    El archivo existe y contiene {len(datos)} productos legibles:")
        for item in datos:
            print(f"      - {item['tipo']}: {item['nombre']} (stock {item['stock']})")
    else:
        print("    ERROR: el archivo no se generó correctamente.")


if __name__ == "__main__":
    main()
