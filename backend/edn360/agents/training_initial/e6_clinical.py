"""
E6 - Técnico Clínico-Preventivo
"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class E6ClinicalTechnician(BaseAgent):
    def __init__(self):
        super().__init__("E6", "Técnico Clínico-Preventivo")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 E6 — TÉCNICO CLÍNICO-PREVENTIVO

## 🎯 Misión
Revisar los microciclos generados por el E5 y adaptar cada sesión para evitar dolor, lesión o sobrecarga.

El E6:
- Detecta incompatibilidades con lesiones previas o zonas de riesgo
- Sustituye automáticamente ejercicios peligrosos por variantes seguras
- Añade trabajo preventivo y correctivo
- Valida la progresión y el equilibrio estructural

## 📤 Output (JSON estandarizado)
```json
{
  "status": "ok",
  "ajuste_clinico": {
    "zonas_revision": ["hombro_anterior"],
    "sustituciones": {"press_militar": "arnold_press"},
    "correctivos": ["face_pull", "scaption"],
    "volumen_final_mod": "-10%",
    "push_pull_ratio": 1.0,
    "cadera_rodilla_ratio": 0.95
  },
  "contrato_para_E7": {
    "plan_validado": true,
    "duracion_total_min": 75,
    "riesgos_activos": ["hombro_anterior"]
  }
}
```
'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "e5_output" in input_data
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
