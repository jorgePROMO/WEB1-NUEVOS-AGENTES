"""N6 - Menu Generator"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N6MenuGenerator(BaseAgent):
    def __init__(self):
        super().__init__("N6", "Menu Generator")
    def get_system_prompt(self) -> str:
        return '''# N6 — GENERADOR MENÚ SEMANAL
Crear menú semanal (7 días) con alimentos específicos para cada comida.

REGLAS:
- 7 días completos (dia_1 a dia_7)
- Cada día: tipo_dia (A/M/B) + todas las comidas del plan
- Alimentos con cantidades exactas en gramos
- Variar alimentos entre días
- Respetar macros de N5 (±5g tolerancia)

EJEMPLO (SIMPLIFICADO):
dia_1: Tipo A, 4 comidas (desayuno: 3 huevos+80g avena+plátano, pre: arroz+pollo, post: pasta+salmón, cena: pescado+verduras)

DEVUELVE SOLO JSON VÁLIDO (sin explicaciones):
{
  "status": "ok",
  "menu_semanal": {
    "dia_1": {
      "tipo_dia": "A",
      "comidas": [
        {
          "nombre": "Desayuno",
          "hora": "08:00",
          "alimentos": [
            {"nombre": "Huevos enteros", "cantidad": "3 unidades", "cantidad_g": 180},
            {"nombre": "Avena", "cantidad": "80g", "cantidad_g": 80},
            {"nombre": "Plátano", "cantidad": "1 unidad", "cantidad_g": 120}
          ],
          "macros": {"proteinas": 40, "carbohidratos": 65, "grasas": 22},
          "preparacion": "Huevos revueltos, avena con canela"
        },
        {
          "nombre": "Pre-Entreno",
          "hora": "11:30",
          "alimentos": [
            {"nombre": "Arroz blanco", "cantidad": "100g cocido", "cantidad_g": 100},
            {"nombre": "Pechuga pollo", "cantidad": "150g", "cantidad_g": 150}
          ],
          "macros": {"proteinas": 35, "carbohidratos": 68, "grasas": 8}
        },
        {
          "nombre": "Post-Entreno",
          "hora": "14:30",
          "alimentos": [
            {"nombre": "Pasta integral", "cantidad": "150g cocida", "cantidad_g": 150},
            {"nombre": "Salmón", "cantidad": "180g", "cantidad_g": 180}
          ],
          "macros": {"proteinas": 48, "carbohidratos": 82, "grasas": 18}
        },
        {
          "nombre": "Cena",
          "hora": "21:00",
          "alimentos": [
            {"nombre": "Merluza", "cantidad": "200g", "cantidad_g": 200},
            {"nombre": "Boniato", "cantidad": "150g", "cantidad_g": 150},
            {"nombre": "Almendras", "cantidad": "20g", "cantidad_g": 20}
          ],
          "macros": {"proteinas": 45, "carbohidratos": 42, "grasas": 24}
        }
      ]
    },
    "dia_2": {"tipo_dia": "M", "comidas": [...]},
    "dia_3": {"tipo_dia": "A", "comidas": [...]},
    "dia_4": {"tipo_dia": "B", "comidas": [...]},
    "dia_5": {"tipo_dia": "M", "comidas": [...]},
    "dia_6": {"tipo_dia": "A", "comidas": [...]},
    "dia_7": {"tipo_dia": "B", "comidas": [...]}
  },
  "equivalencias": {
    "proteinas": {"pollo": ["pavo", "pescado blanco"], "huevos": ["claras", "proteína polvo"]},
    "carbohidratos": {"arroz": ["pasta", "quinoa"], "avena": ["pan integral"]},
    "grasas": {"aceite_oliva": ["aceite aguacate"], "almendras": ["nueces"]}
  }
}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
