"""
E9 - Bridge hacia Nutrición
"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class E9NutritionBridge(BaseAgent):
    def __init__(self):
        super().__init__("E9", "Bridge hacia Nutrición")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 E9 — BRIDGE DE COHERENCIA HACIA NUTRICIÓN

## 🎯 Misión
Convertir los datos técnicos del entrenamiento en un mapa energético cuantificable para nutricionistas (bloque N).
Objetivo: transformar esfuerzo físico en requerimiento calórico.

## ⚙️ Cálculos principales

### Gasto Semanal Estimado (GSE)
```
GSE = (CIT × 6.5) + (minutos_totales_entreno × 7) + (pasos_promedio × 0.04)
```

Ajustes:
- +10% si NEAT alto (>12k pasos/día)
- -10% si recuperación baja o IRG <5
- +5% si KPI principal es fuerza pura

### Clasificación de días A/M/B

| Tipo | Criterios | Ajuste energético |
|------|-----------|-------------------|
| **A (Alta)** | RIR 1-2, volumen >14 series o sesión >75 min | +10-15% kcal / +0.5-1 g/kg CH |
| **M (Media)** | RIR 2-3, sesión estándar | ±0% kcal |
| **B (Baja)** | RIR 3-4 o descanso | -10-15% kcal / ↓ CH |

## 📤 Output (JSON estandarizado)
```json
{
  "status": "ok",
  "bridge_output": {
    "tdee_estimado": 2550,
    "gasto_semanal_estimado": 17800,
    "mapa_intensidad": {
      "dias_duros": 2,
      "dias_medios": 3,
      "dias_ligeros": 2
    },
    "distribucion_energetica": {
      "A": "+12%",
      "M": "0%",
      "B": "-12%"
    },
    "prioridad_metabolica": "hipertrofia"
  },
  "contrato_para_N0": {
    "estado_fisiologico": "carga_controlada",
    "tdee": 2550,
    "delta_dias_A": "+12%",
    "delta_dias_B": "-12%",
    "prioridad": "hipertrofia"
  }
}
```
'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
