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

**CRÍTICO**: Analiza el plan E4/E5 para identificar qué días son más intensos:

| Tipo | Criterios | Ajuste energético |
|------|-----------|-------------------|
| **A (Alta)** | RIR 1-2, volumen >14 series, sesión >75 min, semanas intensificación (S3), ejercicios compuestos pesados | +10-15% kcal / +0.5-1 g/kg CH |
| **M (Media)** | RIR 2-4, sesión estándar 45-60 min, semanas adaptación/acumulación (S1-S2), volumen moderado | ±0% kcal |
| **B (Baja)** | Descanso completo, deload (S4), o RIR >4 | -10-15% kcal / ↓ CH |

**Ejemplo para Full-Body 3 días/semana**:
- Día 1 (Lunes): M (Adaptación, volumen moderado)
- Día 2 (Miércoles): A (Día con mayor volumen/intensidad en semana, ejercicios más pesados)
- Día 3 (Viernes): M (Volumen moderado, cierre de semana)

## 📤 Output (JSON estandarizado)
```json
{
  "status": "ok",
  "bridge_output": {
    "tdee_estimado": 2550,
    "gasto_semanal_estimado": 17800,
    "dias_entrenamiento_semana": 3,
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
    "calendario_sugerido": {
      "dia_1": "M",
      "dia_2": "B",
      "dia_3": "A",
      "dia_4": "B",
      "dia_5": "M",
      "dia_6": "B",
      "dia_7": "B"
    },
    "justificacion_calendario": {
      "dia_1": "Lunes: Entrenamiento moderado - Inicio de semana, adaptación",
      "dia_3": "Miércoles: Entrenamiento INTENSO - Mayor volumen/carga de la semana",
      "dia_5": "Viernes: Entrenamiento moderado - Cierre de microciclo"
    },
    "prioridad_metabolica": "hipertrofia"
  },
  "contrato_para_N0": {
    "estado_fisiologico": "carga_controlada",
    "tdee": 2550,
    "dias_entrenamiento": 3,
    "delta_dias_A": "+12%",
    "delta_dias_B": "-12%",
    "prioridad": "hipertrofia"
  }
}
```

CRÍTICO: DEBES incluir "dias_entrenamiento_semana" y "calendario_sugerido" basado en el plan de entrenamiento real.
'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
