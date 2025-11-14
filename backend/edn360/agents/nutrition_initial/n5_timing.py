"""N5 - Timing & Distribution"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N5TimingDistributor(BaseAgent):
    def __init__(self):
        super().__init__("N5", "Timing Distributor")
    def get_system_prompt(self) -> str:
        return '''# N5 — TIMING & DISTRIBUCIÓN DE COMIDAS
Distribuir macros diarios en comidas según calendario A/M/B.

CRÍTICO - LEE EL CALENDARIO N4:
- Consulta el campo "calendario_semanal" de N4 para saber qué días son A/M/B
- SOLO incluye Pre/Post entreno en días A y M (entrenamiento)
- En días B (descanso) SOLO: Desayuno, Comida, Cena (3 comidas)

DISTRIBUCIÓN POR TIPO DE DÍA:

DÍAS A/M (Entrenamiento) - 5 comidas:
{
  "tipo_dia": "A" o "M",
  "numero_comidas": 5,
  "comidas": [
    {"nombre": "Desayuno", "hora": "08:00", "tipo": "comida_principal", "proteinas_g": 35, "carbohidratos_g": 45, "grasas_g": 15},
    {"nombre": "Pre-Entreno", "hora": "11:30", "tipo": "pre_entreno", "proteinas_g": 25, "carbohidratos_g": 70, "grasas_g": 8, "timing_entreno": "90-120 min antes"},
    {"nombre": "Post-Entreno", "hora": "13:30", "tipo": "post_entreno", "proteinas_g": 40, "carbohidratos_g": 85, "grasas_g": 10, "timing_entreno": "inmediato"},
    {"nombre": "Merienda", "hora": "18:00", "tipo": "comida_secundaria", "proteinas_g": 30, "carbohidratos_g": 35, "grasas_g": 12},
    {"nombre": "Cena", "hora": "21:00", "tipo": "comida_principal", "proteinas_g": 40, "carbohidratos_g": 25, "grasas_g": 20}
  ]
}

DÍAS B (Descanso) - 4 comidas:
{
  "tipo_dia": "B",
  "numero_comidas": 4,
  "comidas": [
    {"nombre": "Desayuno", "hora": "08:00", "tipo": "comida_principal", "proteinas_g": 45, "carbohidratos_g": 40, "grasas_g": 20},
    {"nombre": "Comida", "hora": "14:00", "tipo": "comida_principal", "proteinas_g": 50, "carbohidratos_g": 45, "grasas_g": 18},
    {"nombre": "Merienda", "hora": "18:00", "tipo": "comida_secundaria", "proteinas_g": 25, "carbohidratos_g": 20, "grasas_g": 15},
    {"nombre": "Cena", "hora": "21:00", "tipo": "comida_principal", "proteinas_g": 45, "carbohidratos_g": 30, "grasas_g": 20}
  ]
}

DEVUELVE JSON CON DISTRIBUCIONES PARA A, M y B:
{
  "status": "ok",
  "distribucion_dia_A": {...},
  "distribucion_dia_M": {...},
  "distribucion_dia_B": {...},
  "timing_entreno": {
    "pre_entreno": "90-120 min antes",
    "post_entreno": "0-30 min después"
  }
}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
