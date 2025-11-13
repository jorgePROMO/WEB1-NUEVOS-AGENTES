"""N2 - Energy Selector"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class N2EnergySelector(BaseAgent):
    def __init__(self):
        super().__init__("N2", "Energy Selector")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 N2 — SELECTOR ENERGÉTICO

## 🎯 PROPÓSITO
Calcular calorías objetivo y macros basados en TDEE, perfil metabólico y rango permitido.

## 📤 OUTPUT JSON REQUERIDO:
```json
{
  "status": "ok",
  "kcal_objetivo": 2200,
  "deficit_pct": -15,
  "macros": {
    "proteinas_g": 176,
    "proteinas_gkg": 2.2,
    "carbohidratos_g": 220,
    "grasas_g": 64
  },
  "distribucion": {
    "proteinas_pct": 32,
    "carbohidratos_pct": 40,
    "grasas_pct": 28
  }
}
```

## ⚙️ CÁLCULOS:
- Proteínas: 1.8-2.5 g/kg
- Grasas: 0.7-1.0 g/kg
- Carbohidratos: resto
'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
