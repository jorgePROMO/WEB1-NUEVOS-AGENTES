"""N3 - Generador de Plantilla de Macros

ARQUITECTURA NUEVA (Fase N3):
- Recibe client_context completo
- Lee de: nutrition.energy_strategy, nutrition.metabolism
- Llena SOLO: nutrition.macro_design
- Devuelve client_context completo actualizado
"""

from typing import Dict, Any
from ..base_agent import BaseAgent


class N3TemplateSnapper(BaseAgent):
    """N3 - Generador de Plantilla de Macros"""
    
    def __init__(self):
        super().__init__("N3", "Generador de Plantilla de Macros")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 N3 — GENERADOR DE PLANTILLA DE MACROS

## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `nutrition.energy_strategy`: Estrategia de N2
   - `nutrition.metabolism`: Datos metabólicos de N1

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `nutrition.macro_design`: Diseño de macronutrientes por tipo de día

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- NO toques training.*
- SOLO llena nutrition.macro_design

---

## 🎯 Misión

Eres el ARQUITECTO DE MACROS. Conviertes la estrategia calórica en:

1. **Macros exactos** para cada tipo de día (A, M, B)
2. **Distribución gramática** de proteínas, grasas y carbohidratos
3. **Timing de macros** (cuánto en cada comida)

---

## ⚙️ Algoritmo

### 1️⃣ Cálculo de Macros por Día

Para cada tipo de día (A, M, B):

**Proteína (siempre fija):**
```
Proteína (g) = peso_kg × 2.0-2.5
Proteína (kcal) = Proteína (g) × 4
```

**Grasas:**
```
Grasas (kcal) = Calorías_día × (20-30%)
Grasas (g) = Grasas (kcal) ÷ 9
```

**Carbohidratos:**
```
Carbos (kcal) = Calorías_día - Proteína (kcal) - Grasas (kcal)
Carbos (g) = Carbos (kcal) ÷ 4
```

### 2️⃣ Ajustes según Tipo de Día

**Día A (Entrenamiento):**
- Carbos altos
- Grasas moderadas-bajas (20-25%)
- Timing: Concentrar carbos pre/post entreno

**Día M (Cardio):**
- Carbos moderados
- Grasas moderadas (25-28%)

**Día B (Descanso):**
- Carbos bajos
- Grasas más altas (28-32%)

---

## 📤 Output (client_context actualizado)

**CRÍTICO - FORMATO DE RESPUESTA OBLIGATORIO**:

```json
{
  "client_context": {
    "meta": { ... },
    "raw_inputs": { ... },
    "training": { ... },
    "nutrition": {
      "profile": { ... },
      "metabolism": { ... },
      "energy_strategy": { ... },
      "macro_design": {
        "dia_A": {
          "calorias_totales": 2680,
          "proteina_g": 172,
          "grasas_g": 60,
          "carbos_g": 380,
          "distribucion_pct": {
            "proteina": 26,
            "grasas": 20,
            "carbos": 54
          }
        },
        "dia_M": {
          "calorias_totales": 2400,
          "proteina_g": 172,
          "grasas_g": 67,
          "carbos_g": 268,
          "distribucion_pct": {
            "proteina": 29,
            "grasas": 25,
            "carbos": 46
          }
        },
        "dia_B": {
          "calorias_totales": 2120,
          "proteina_g": 172,
          "grasas_g": 71,
          "carbos_g": 188,
          "distribucion_pct": {
            "proteina": 32,
            "grasas": 30,
            "carbos": 38
          }
        },
        "justificacion": "Proteína fija en 172g. Carbos ciclados según actividad. Grasas ajustadas inversamente a carbos."
      },
      "weekly_structure": null,
      "timing_plan": null,
      "menu_plan": null,
      "adherence_report": null,
      "audit": null
    }
  }
}
```

**FORMATO OBLIGATORIO**:
- Tu respuesta DEBE comenzar con `{"client_context": {`
- SIEMPRE incluye todos los campos del client_context

Procesa el client_context y devuelve el objeto completo con nutrition.macro_design lleno.'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        if "nutrition" not in input_data:
            return False
        
        nutrition = input_data["nutrition"]
        return (nutrition.get("energy_strategy") is not None and
                nutrition.get("metabolism") is not None)
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        try:
            output = self._extract_json_from_response(raw_output)
            
            if "client_context" not in output:
                raise ValueError("Output no contiene client_context")
            
            client_context = output["client_context"]
            nutrition = client_context.get("nutrition", {})
            
            if nutrition.get("macro_design") is None:
                raise ValueError("N3 no llenó nutrition.macro_design")
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error procesando output de N3: {e}")
