"""N4 - Sincronizador A-M-B

ARQUITECTURA NUEVA (Fase N3):
- Recibe client_context completo
- Lee de: nutrition.macro_design, nutrition.energy_strategy, training.bridge_for_nutrition
- Llena SOLO: nutrition.weekly_structure
- Devuelve client_context completo actualizado
"""

from typing import Dict, Any
from ..base_agent import BaseAgent


class N4AMBSynchronizer(BaseAgent):
    """N4 - Sincronizador A-M-B"""
    
    def __init__(self):
        super().__init__("N4", "Sincronizador A-M-B")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 N4 — SINCRONIZADOR A-M-B

## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `nutrition.macro_design`: Macros por tipo de día de N3
   - `nutrition.energy_strategy`: Calendario semanal de N2
   - `training.bridge_for_nutrition`: Calendario de entrenamiento de E9

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `nutrition.weekly_structure`: Estructura semanal completa con macros por día

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- NO toques training.*
- SOLO llena nutrition.weekly_structure

---

## 🎯 Misión

Eres el SINCRONIZADOR. Mapeas el calendario semanal real:

1. **Asignar tipo de día** (A, M, B) a cada día de la semana
2. **Aplicar macros** correspondientes de nutrition.macro_design
3. **Sincronizar** con calendario de training.bridge_for_nutrition
4. **Verificar coherencia** (días A = días de entrenamiento)

---

## ⚙️ Lógica

### 1️⃣ Mapeo de Días

De `nutrition.energy_strategy.calendario_semanal`:
```json
{
  "lunes": "A",
  "martes": "A",
  "miercoles": "B",
  ...
}
```

Para cada día:
- Si tipo = "A" → usar `macro_design.dia_A`
- Si tipo = "M" → usar `macro_design.dia_M`
- Si tipo = "B" → usar `macro_design.dia_B`

### 2️⃣ Verificación

- Días A deben coincidir con días de entrenamiento de `training.bridge_for_nutrition`
- Si no coinciden, marcar warning

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
      "macro_design": { ... },
      "weekly_structure": {
        "lunes": {
          "tipo": "A",
          "calorias": 2680,
          "proteina_g": 172,
          "grasas_g": 60,
          "carbos_g": 380,
          "entrena": true
        },
        "martes": {
          "tipo": "A",
          "calorias": 2680,
          "proteina_g": 172,
          "grasas_g": 60,
          "carbos_g": 380,
          "entrena": true
        },
        "miercoles": {
          "tipo": "B",
          "calorias": 2120,
          "proteina_g": 172,
          "grasas_g": 71,
          "carbos_g": 188,
          "entrena": false
        },
        "jueves": {
          "tipo": "M",
          "calorias": 2400,
          "proteina_g": 172,
          "grasas_g": 67,
          "carbos_g": 268,
          "entrena": false
        },
        "viernes": {
          "tipo": "A",
          "calorias": 2680,
          "proteina_g": 172,
          "grasas_g": 60,
          "carbos_g": 380,
          "entrena": true
        },
        "sabado": {
          "tipo": "B",
          "calorias": 2120,
          "proteina_g": 172,
          "grasas_g": 71,
          "carbos_g": 188,
          "entrena": false
        },
        "domingo": {
          "tipo": "B",
          "calorias": 2120,
          "proteina_g": 172,
          "grasas_g": 71,
          "carbos_g": 188,
          "entrena": false
        }
      },
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

Procesa el client_context y devuelve el objeto completo con nutrition.weekly_structure lleno.'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        if "nutrition" not in input_data:
            return False
        
        nutrition = input_data["nutrition"]
        return (nutrition.get("macro_design") is not None and
                nutrition.get("energy_strategy") is not None)
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        try:
            output = self._extract_json_from_response(raw_output)
            
            if "client_context" not in output:
                raise ValueError("Output no contiene client_context")
            
            client_context = output["client_context"]
            nutrition = client_context.get("nutrition", {})
            
            if nutrition.get("weekly_structure") is None:
                raise ValueError("N4 no llenó nutrition.weekly_structure")
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error procesando output de N4: {e}")
