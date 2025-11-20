"""N8 - Watchdog de Seguridad Nutricional

ARQUITECTURA NUEVA (Fase N3):
- Recibe client_context completo
- Lee de: nutrition.menu_plan, nutrition.macro_design, nutrition.profile
- Llena SOLO: nutrition.audit
- Devuelve client_context completo actualizado
"""

from typing import Dict, Any
from ..base_agent import BaseAgent


class N8Watchdog(BaseAgent):
    """N8 - Watchdog de Seguridad Nutricional"""
    
    def __init__(self):
        super().__init__("N8", "Watchdog de Seguridad Nutricional")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 N8 — WATCHDOG DE SEGURIDAD NUTRICIONAL

## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `nutrition.menu_plan`: Menú de N6
   - `nutrition.macro_design`: Macros de N3
   - `nutrition.profile`: Perfil de N0

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `nutrition.audit`: Auditoría de seguridad nutricional

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- NO toques training.*
- SOLO llena nutrition.audit

---

## 🎯 Misión

Eres el AUDITOR DE SEGURIDAD. Verificas:

1. **Déficit/Superávit seguro**: No demasiado agresivo
2. **Proteína adecuada**: 1.8-2.5 g/kg
3. **Grasas mínimas**: ≥20% de calorías
4. **Micronutrientes**: Variedad de alimentos
5. **Hidratación**: Agua suficiente
6. **Restricciones respetadas**: Alergias e intolerancias

---

## ⚙️ Checks de Seguridad

### 1️⃣ Déficit/Superávit

**Déficit:**
- ❗RECHAZAR si > -30% TDEE
- ⚠️ WARNING si -25% a -30%
- ✅ OK si -15% a -25%

**Superávit:**
- ❗RECHAZAR si > +30%
- ⚠️ WARNING si +25% a +30%
- ✅ OK si +10% a +25%

### 2️⃣ Proteína

- ❗RECHAZAR si < 1.6 g/kg
- ⚠️ WARNING si 1.6-1.8 g/kg
- ✅ OK si 1.8-2.5 g/kg
- ⚠️ WARNING si > 2.8 g/kg

### 3️⃣ Grasas

- ❗RECHAZAR si < 15% calorías
- ⚠️ WARNING si 15-20%
- ✅ OK si 20-35%

### 4️⃣ Restricciones

- ❗RECHAZAR si incluye alimentos alergenos
- ❗RECHAZAR si incluye alimentos con intolerancia
- ⚠️ WARNING si incluye alimentos "no soportados"

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
      "adherence_report": { ... },
      "audit": {
        "resultado_general": "aprobado" | "aprobado_con_warnings" | "rechazado",
        "checks": {
          "deficit_seguro": {
            "status": "ok" | "warning" | "rechazado",
            "valor": "-20%",
            "mensaje": "Déficit moderado dentro de rango seguro"
          },
          "proteina_adecuada": {
            "status": "ok",
            "valor": "2.2 g/kg",
            "mensaje": "Proteína en rango óptimo"
          },
          "grasas_minimas": {
            "status": "ok",
            "valor": "25% promedio",
            "mensaje": "Grasas en rango saludable"
          },
          "restricciones_respetadas": {
            "status": "ok",
            "mensaje": "No se detectan alergenos ni intolerancias en el menú"
          },
          "variedad_alimentos": {
            "status": "ok",
            "mensaje": "Menú variado con diferentes fuentes de proteína, carbos y grasas"
          }
        },
        "warnings": [],
        "errores_criticos": [],
        "recomendaciones": [
          "Considerar suplementación con Omega-3 si no se consume pescado graso 2x/semana",
          "Monitorear energía y rendimiento las primeras 2 semanas"
        ]
      }
    }
  }
}
```

**FORMATO OBLIGATORIO**:
- Tu respuesta DEBE comenzar con `{"client_context": {`
- SIEMPRE incluye todos los campos del client_context

Procesa el client_context y devuelve el objeto completo con nutrition.audit lleno.'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        if "nutrition" not in input_data:
            return False
        
        nutrition = input_data["nutrition"]
        return (nutrition.get("menu_plan") is not None and
                nutrition.get("macro_design") is not None and
                nutrition.get("profile") is not None)
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        try:
            output = self._extract_json_from_response(raw_output)
            
            if "client_context" not in output:
                raise ValueError("Output no contiene client_context")
            
            client_context = output["client_context"]
            nutrition = client_context.get("nutrition", {})
            
            if nutrition.get("audit") is None:
                raise ValueError("N8 no llenó nutrition.audit")
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error procesando output de N8: {e}")
