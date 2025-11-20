"""N7 - Coach de Adherencia

ARQUITECTURA NUEVA (Fase N3):
- Recibe client_context completo
- Lee de: nutrition.menu_plan, nutrition.profile
- Llena SOLO: nutrition.adherence_report
- Devuelve client_context completo actualizado
"""

from typing import Dict, Any
from ..base_agent import BaseAgent


class N7AdherenceCoach(BaseAgent):
    """N7 - Coach de Adherencia"""
    
    def __init__(self):
        super().__init__("N7", "Coach de Adherencia")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 N7 — COACH DE ADHERENCIA

## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `nutrition.menu_plan`: Menú completo de N6
   - `nutrition.profile`: Perfil y contexto de N0

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `nutrition.adherence_report`: Consejos y estrategias de adherencia

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- NO toques training.*
- SOLO llena nutrition.adherence_report

---

## 🎯 Misión

Eres el PSICÓLOGO NUTRICIONAL. Anticipas barreras y das soluciones:

1. **Identificar riesgos** de abandono
2. **Proponer estrategias** concretas
3. **Flexibilidad inteligente** (cuándo permitir variaciones)
4. **Consejos prácticos** para situaciones comunes
5. **Seguimiento recomendado** (frecuencia de pesaje, fotos, etc.)

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
      "timing_plan": { ... },
      "menu_plan": { ... },
      "adherence_report": {
        "factores_riesgo": [
          "Historial de abandono tras 2-3 meses",
          "Trabajo estresante con deadlines"
        ],
        "factores_protectores": [
          "Apoyo familiar",
          "Motivación alta inicial"
        ],
        "probabilidad_adherencia": "media-alta",
        "estrategias_recomendadas": [
          "Preparar comidas batch los domingos",
          "Usar tupper para llevar al trabajo",
          "Permitir 1 comida libre semanal"
        ],
        "situaciones_comunes": {
          "comida_social": "Elegir opción proteica + verduras. Evitar pan y postres.",
          "viaje_trabajo": "Llevar snacks proteicos. Buscar restaurantes con opciones saludables.",
          "ansiedad_nocturna": "Yogur griego 0% con canela. No supera macros."
        },
        "flexibilidad": {
          "intercambios_permitidos": "Pollo ↔ Pavo ↔ Pescado blanco (mismo peso crudo)",
          "margen_error_kcal": "+/- 10%",
          "comidas_libres": "1 por semana, preferible sábado"
        },
        "seguimiento_recomendado": {
          "pesaje": "Lunes en ayunas, misma báscula",
          "fotos_progreso": "Cada 2 semanas",
          "ajustes_plan": "Cada 4 semanas según resultados"
        }
      },
      "audit": null
    }
  }
}
```

**FORMATO OBLIGATORIO**:
- Tu respuesta DEBE comenzar con `{"client_context": {`
- SIEMPRE incluye todos los campos del client_context

Procesa el client_context y devuelve el objeto completo con nutrition.adherence_report lleno.'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        if "nutrition" not in input_data:
            return False
        
        nutrition = input_data["nutrition"]
        return (nutrition.get("menu_plan") is not None and
                nutrition.get("profile") is not None)
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        try:
            output = self._extract_json_from_response(raw_output)
            
            if "client_context" not in output:
                raise ValueError("Output no contiene client_context")
            
            client_context = output["client_context"]
            nutrition = client_context.get("nutrition", {})
            
            if nutrition.get("adherence_report") is None:
                raise ValueError("N7 no llenó nutrition.adherence_report")
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error procesando output de N7: {e}")
