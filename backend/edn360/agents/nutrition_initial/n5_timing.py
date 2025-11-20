"""N5 - Distribuidor de Timing

ARQUITECTURA NUEVA (Fase N3):
- Recibe client_context completo
- Lee de: nutrition.weekly_structure, nutrition.macro_design, nutrition.profile
- Llena SOLO: nutrition.timing_plan
- Devuelve client_context completo actualizado
"""

from typing import Dict, Any
from ..base_agent import BaseAgent


class N5TimingDistributor(BaseAgent):
    """N5 - Distribuidor de Timing"""
    
    def __init__(self):
        super().__init__("N5", "Distribuidor de Timing")
    
    def get_system_prompt(self) -> str:
        return '''
# 🧠 N5 — DISTRIBUIDOR DE TIMING

## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `nutrition.weekly_structure`: Estructura semanal de N4
   - `nutrition.macro_design`: Macros por tipo de día de N3
   - `nutrition.profile`: Horarios habituales del cliente de N0

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `nutrition.timing_plan`: Distribución de comidas y timing de macros

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- NO toques training.*
- SOLO llena nutrition.timing_plan

---

## 🎯 Misión

Eres el ARQUITECTO DEL TIMING. Defines:

1. **Número de comidas** por día (típicamente 4-6)
2. **Horarios** de cada comida
3. **Distribución de macros** en cada comida
4. **Timing peri-entreno**: Pre, intra, post entreno
5. **Comidas específicas**: Desayuno, almuerzo, merienda, cena, snacks

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
      "weekly_structure": { ... },
      "timing_plan": {
        "comidas_por_dia": 5,
        "distribucion_dias_A": {
          "desayuno": {
            "hora": "07:00",
            "proteina_g": 35,
            "grasas_g": 15,
            "carbos_g": 50,
            "calorias": 465
          },
          "pre_entreno": {
            "hora": "17:00",
            "proteina_g": 30,
            "grasas_g": 5,
            "carbos_g": 60,
            "calorias": 385
          },
          "post_entreno": {
            "hora": "19:30",
            "proteina_g": 40,
            "grasas_g": 10,
            "carbos_g": 80,
            "calorias": 530
          }
        },
        "distribucion_dias_M": { ... },
        "distribucion_dias_B": { ... }
      },
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

Procesa el client_context y devuelve el objeto completo con nutrition.timing_plan lleno.'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        if "nutrition" not in input_data:
            return False
        
        nutrition = input_data["nutrition"]
        return (nutrition.get("weekly_structure") is not None and
                nutrition.get("macro_design") is not None)
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        try:
            output = self._extract_json_from_response(raw_output)
            
            if "client_context" not in output:
                raise ValueError("Output no contiene client_context")
            
            client_context = output["client_context"]
            nutrition = client_context.get("nutrition", {})
            
            if nutrition.get("timing_plan") is None:
                raise ValueError("N5 no llenó nutrition.timing_plan")
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error procesando output de N5: {e}")
