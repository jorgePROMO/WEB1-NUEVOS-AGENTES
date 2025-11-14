"""N5 - Timing & Distribution"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N5TimingDistributor(BaseAgent):
    def __init__(self):
        super().__init__("N5", "Timing Distributor")
    def get_system_prompt(self) -> str:
        return '''# N5 — TIMING & DISTRIBUCIÓN DE COMIDAS
Distribuir macros en 4-5 comidas con timing pre/post entreno.

INSTRUCCIONES:
- Genera 4-5 comidas según macros totales disponibles
- OBLIGATORIO: Desayuno, Pre-entreno, Post-entreno, Cena
- Pre-entreno: 25-30g proteína, 60-80g carbos, 5-10g grasas (90-120min antes)
- Post-entreno: 35-50g proteína, 70-100g carbos, 10-15g grasas (inmediato)
- Distribución realista de horarios
- Los macros deben sumar el total diario

DEVUELVE SOLO JSON (sin texto adicional):
{
  "status": "ok",
  "numero_comidas": 4,
  "comidas": [
    {
      "nombre": "Desayuno",
      "hora": "08:00",
      "tipo": "comida_principal",
      "proteinas_g": 40,
      "carbohidratos_g": 60,
      "grasas_g": 20,
      "descripcion": "Primera comida del día"
    },
    {
      "nombre": "Pre-Entreno",
      "hora": "11:30",
      "tipo": "pre_entreno",
      "proteinas_g": 28,
      "carbohidratos_g": 75,
      "grasas_g": 8,
      "timing_entreno": "90-120 min antes"
    },
    {
      "nombre": "Post-Entreno",
      "hora": "14:30",
      "tipo": "post_entreno",
      "proteinas_g": 45,
      "carbohidratos_g": 90,
      "grasas_g": 12,
      "timing_entreno": "inmediato"
    },
    {
      "nombre": "Cena",
      "hora": "21:00",
      "tipo": "comida_principal",
      "proteinas_g": 45,
      "carbohidratos_g": 35,
      "grasas_g": 28
    }
  ],
  "timing_entreno": {
    "pre_entreno": "90-120 min antes",
    "post_entreno": "0-30 min después"
  }
}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
