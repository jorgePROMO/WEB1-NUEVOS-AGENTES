"""N0 - Analista de Triaje Nutricional

ARQUITECTURA NUEVA (Fase N3):
- Recibe client_context completo
- Lee de: raw_inputs, training.bridge_for_nutrition
- Llena SOLO: nutrition.profile
- Devuelve client_context completo actualizado
"""

from typing import Dict, Any
from ..base_agent import BaseAgent


class N0TriageAnalyst(BaseAgent):
    """N0 - Analista de Triaje Nutricional"""
    
    def __init__(self):
        super().__init__("N0", "Analista de Triaje Nutricional")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 N0 — ANALISTA DE TRIAJE NUTRICIONAL

## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `raw_inputs`: Cuestionario del cliente
   - `training.bridge_for_nutrition`: Nexo de E9 con calendario de entrenamiento

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `nutrition.profile`: Perfil nutricional del cliente

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- NO toques training.*
- SOLO llena nutrition.profile

---

## 🎯 Misión

Eres el INTÉRPRETE NUTRICIONAL. Tu trabajo es extraer del cuestionario y del bridge de entrenamiento:

1. **Objetivos nutricionales**: Qué quiere lograr (pérdida de grasa, ganancia muscular, recomposición)
2. **Restricciones alimentarias**: Alergias, intolerancias, alimentos no soportados
3. **Preferencias dietéticas**: Vegano, vegetariano, paleo, sin restricciones
4. **Contexto de vida**: Horarios de comidas, trabajo, estrés, sueño
5. **Calendario de entrenamiento**: Extraído de training.bridge_for_nutrition

---

## 📥 Input (de client_context)

Recibes el client_context completo. Debes leer:
- `raw_inputs.cuestionario_inicial`: JSON string con datos del cliente
- `training.bridge_for_nutrition`: Objeto de E9 con TDEE, días de entrenamiento, calendario

---

## 📤 Output (client_context actualizado)

**CRÍTICO - FORMATO DE RESPUESTA OBLIGATORIO**:

Tu respuesta DEBE ser un JSON con esta estructura EXACTA:

```json
{
  "client_context": {
    "meta": { ... },
    "raw_inputs": { ... },
    "training": { ... },  // NO MODIFICAR
    "nutrition": {
      "profile": {
        "objetivo_principal": "perdida_grasa" | "ganancia_muscular" | "recomposicion" | "mantenimiento",
        "objetivo_secundario": "...",
        "plazo": "3_meses" | "6_meses" | "12_meses",
        "motivacion": "alta" | "media" | "baja",
        "restricciones_alimentarias": {
          "alergias": ["lactosa", "gluten", ...],
          "intolerancias": [...],
          "alimentos_no_soportados": ["patata", "coliflor", ...],
          "restricciones_medicas": ["diabetes", "hipotiroidismo", ...]
        },
        "preferencias_dieteticas": {
          "tipo": "omnivoro" | "vegetariano" | "vegano" | "paleo" | "flexitariano",
          "notas": "..."
        },
        "contexto_vida": {
          "trabajo": "sedentario" | "activo" | "muy_activo",
          "horas_trabajo": 8,
          "nivel_estres": "bajo" | "medio" | "alto",
          "horas_sueno": 7.0,
          "calidad_sueno": "buena" | "regular" | "mala"
        },
        "horarios_habituales": {
          "desayuno": "07:00",
          "almuerzo": "14:00",
          "cena": "21:00",
          "snacks": ["11:00", "18:00"]
        },
        "calendario_entrenamiento": {
          "dias_semana": 4,
          "horario_entrenamiento": "18:00-19:00",
          "dias_entrenamiento": ["lunes", "martes", "jueves", "viernes"],
          "extraido_de_bridge": true
        },
        "adherencia_prevista": {
          "nivel": "alta" | "media" | "baja",
          "factores_riesgo": [...],
          "factores_protectores": [...]
        }
      },
      // Resto de campos de nutrition (null por ahora):
      "metabolism": null,
      "energy_strategy": null,
      "macro_design": null,
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
- NUNCA devuelvas el JSON directamente sin este wrapper
- SIEMPRE incluye todos los campos del client_context, no solo nutrition

---

## ✅ Criterios de éxito

- Objetivo nutricional claramente identificado
- Restricciones alimentarias completas y específicas
- Horarios de comidas extraídos del cuestionario
- Calendario de entrenamiento sincronizado con training.bridge_for_nutrition
- Adherencia prevista evaluada según historial del cliente

---

Procesa el client_context y devuelve el objeto completo con nutrition.profile lleno.'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Valida que el input contenga client_context con datos necesarios
        
        NUEVO (Fase N3): Validamos client_context
        """
        # Debe tener raw_inputs y training.bridge_for_nutrition
        if "raw_inputs" not in input_data:
            return False
        
        if "training" not in input_data:
            return False
        
        training = input_data.get("training", {})
        if training.get("bridge_for_nutrition") is None:
            return False
        
        return True
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        """
        Valida que devuelva client_context con nutrition.profile lleno
        
        NUEVO (Fase N3): Validamos estructura de salida
        """
        try:
            output = self._extract_json_from_response(raw_output)
            
            if "client_context" not in output:
                raise ValueError("Output no contiene client_context")
            
            client_context = output["client_context"]
            nutrition = client_context.get("nutrition", {})
            
            # Validar que N0 llenó nutrition.profile
            if nutrition.get("profile") is None:
                raise ValueError("N0 no llenó nutrition.profile")
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error procesando output de N0: {e}")
