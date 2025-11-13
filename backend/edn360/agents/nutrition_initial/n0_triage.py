"""N0 - Triage Analyst"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class N0TriageAnalyst(BaseAgent):
    def __init__(self):
        super().__init__("N0", "Triage Analyst")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 N0 — TRIAGE DE RAPIDEZ / IMPACIENCIA

## 🎯 PROPÓSITO
Convertir la percepción emocional del cliente (urgencia, impaciencia) y condiciones fisiológicas 
en una decisión estratégica sobre el rango calórico permitido.

## 📤 OUTPUT JSON REQUERIDO:
```json
{
  "status": "ok",
  "decision": {
    "permitido": ["leve_20_25", "moderada_15_20"],
    "prohibido": ["agresiva_10_15"],
    "prioridad": "moderada_15_20"
  },
  "factores": {
    "impaciencia": 4,
    "tolerancia": 4,
    "sueno_h": 6.3,
    "estres": 3,
    "adherencia_prevista_pct": 82
  },
  "condiciones": {
    "moderada_15_20": ["Recomendada"],
    "agresiva_10_15": ["Rechazada: sueño <6.5h"]
  }
}
```

## 🚨 REGLAS:
- Sueño <6h → SOLO "leve"
- Estrés ≥4 → SOLO "leve"
- Agresiva SOLO si: sueño ≥6.5h + estrés ≤3 + adherencia ≥85%
'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
