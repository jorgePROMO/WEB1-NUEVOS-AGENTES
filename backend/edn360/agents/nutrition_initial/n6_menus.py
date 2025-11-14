"""N6 - Menu Generator"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N6MenuGenerator(BaseAgent):
    def __init__(self):
        super().__init__("N6", "Menu Generator")
    def get_system_prompt(self) -> str:
        return '''# N6 — GENERADOR MENÚ SEMANAL
Crear menú semanal (7 días) con alimentos específicos SINCRONIZADO con calendario de entrenamiento.

CRÍTICO - CONSULTA N4 Y N5:
- N4 tiene "calendario_semanal": {"dia_1": "M", "dia_2": "B", "dia_3": "A", ...}
- N5 tiene distribuciones diferentes para A/M/B
- RESPETA el tipo de día y número de comidas:
  * Días A/M: 5 comidas (Desayuno, Pre-Entreno, Post-Entreno, Merienda, Cena)
  * Días B: 4 comidas (Desayuno, Comida, Merienda, Cena) - SIN pre/post entreno

REGLAS:
- Genera 7 días según calendario N4
- Cada día usa macros de N5 según tipo (A/M/B)
- Días B: 4 comidas (Desayuno, Comida, Merienda, Cena) - SIN pre/post entreno
- Días A/M: 5 comidas (Desayuno, Pre, Post, Merienda, Cena) - CON pre/post entreno
- Alimentos específicos con cantidades exactas
- Variar alimentos entre días

IMPORTANTE - EVITAR GAP NUTRICIONAL:
- En días de entreno: Merienda a las 18:00 entre post-entreno (13:30) y cena (21:00)
- En días descanso: Merienda a las 18:00 entre comida (14:00) y cena (21:00)

EJEMPLO:
Si N4 dice dia_1="B" (descanso) → 4 comidas, sin pre/post entreno
Si N4 dice dia_3="A" (entreno) → 5 comidas, con pre/post entreno

ESTRUCTURA JSON:
{
  "status": "ok",
  "menu_semanal": {
    "dia_1": {
      "tipo_dia": "B",
      "comidas": [
        {"nombre": "Desayuno", "hora": "08:00", "alimentos": [...], "macros": {...}},
        {"nombre": "Comida", "hora": "14:00", "alimentos": [...], "macros": {...}},
        {"nombre": "Cena", "hora": "21:00", "alimentos": [...], "macros": {...}}
      ]
    },
    "dia_2": {
      "tipo_dia": "M",
      "comidas": [
        {"nombre": "Desayuno", ...},
        {"nombre": "Pre-Entreno", ...},
        {"nombre": "Post-Entreno", ...},
        {"nombre": "Cena", ...}
      ]
    },
    "dia_3": {"tipo_dia": "A", "comidas": [4 comidas con pre/post]},
    "dia_4": {"tipo_dia": "B", "comidas": [3 comidas sin pre/post]},
    "dia_5": {"tipo_dia": "M", "comidas": [4 comidas con pre/post]},
    "dia_6": {"tipo_dia": "B", "comidas": [3 comidas sin pre/post]},
    "dia_7": {"tipo_dia": "B", "comidas": [3 comidas sin pre/post]}
  },
  "equivalencias": {
    "proteinas": {"pollo": ["pavo", "pescado"]},
    "carbohidratos": {"arroz": ["pasta", "quinoa"]},
    "grasas": {"aceite_oliva": ["aguacate"]}
  }
}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
