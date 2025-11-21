"""
E9 - Puente a Nutrición
Genera información para agentes de nutrición

ARQUITECTURA NUEVA (Fase 2):
- Recibe client_context completo
- Lee de: training.safe_sessions, training.mesocycle, training.profile
- Llena SOLO: training.bridge_for_nutrition
- Devuelve client_context completo actualizado
"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class E9NutritionBridge(BaseAgent):
    def __init__(self):
        super().__init__("E9", "Bridge hacia Nutrición")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 E9 — BRIDGE DE COHERENCIA HACIA NUTRICIÓN

## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `training.safe_sessions`: Sesiones de E6
   - `training.mesocycle`: Estructura de E4
   - `training.profile`: Perfil de E1

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `training.bridge_for_nutrition`: Puente para nutrición

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- SOLO llena training.bridge_for_nutrition

---

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

**CRÍTICO**: Analiza el TIPO DE ENTRENAMIENTO en el plan E4/E5:

| Tipo | Criterios | Ajuste energético |
|------|-----------|-------------------|
| **A (Alta)** | Días de PESAS/FUERZA/HIPERTROFIA: Sentadillas, press banca, peso muerto, máquinas, trabajo con resistencia | +10-15% kcal / +0.5-1 g/kg CH |
| **M (Media)** | Días de CARDIO/CORE/MOVILIDAD: Cardio steady-state, HIIT, abdominales, estiramientos, yoga, trabajo funcional | ±0% kcal |
| **B (Baja)** | Descanso completo sin actividad física programada | -10-15% kcal / ↓ CH |

**REGLA**: 
- Si el día incluye entrenamiento de FUERZA con PESO (barras, mancuernas, máquinas) → Día A
- Si el día es solo CARDIO, CORE, MOVILIDAD, flexibilidad → Día M
- Si no hay entrenamiento → Día B

**Ejemplo típico**:
- Lun: Full-body con pesas → A
- Mar: Descanso → B
- Mié: Cardio + Core → M
- Jue: Descanso → B
- Vie: Full-body con pesas → A
- Sáb/Dom: Descanso → B

## 📤 Output (client_context actualizado)

**CRÍTICO - FORMATO DE RESPUESTA OBLIGATORIO**:

Tu respuesta DEBE ser un JSON con esta estructura EXACTA:

```json
{
  "client_context": {
    "meta": { ... },
    "raw_inputs": { ... },
    "training": {
      // Campos anteriores sin cambios
      "profile": { ... },
      "constraints": { ... },
      "capacity": { ... },
      "adaptation": { ... },
      "mesocycle": { ... },
      "sessions": { ... },
      "safe_sessions": { ... },
      "formatted_plan": { ... },
      "audit": { ... },
      // TU CAMPO - el único que debes llenar:
      "bridge_for_nutrition": {
        "tdee_estimado": 2550,
        "gasto_semanal_estimado": 17800,
        "dias_entrenamiento_semana": 3,
        "tipos_dia": {
    "tdee_estimado": 2550,
    "gasto_semanal_estimado": 17800,
    "dias_entrenamiento_semana": 3,
    "tipos_dia_presentes": {
      "usa_dia_A": true,
      "usa_dia_M": true,
      "usa_dia_B": true,
      "count_A": 2,
      "count_M": 2,
      "count_B": 3
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
    "prioridad": "hipertrofia",
    "restricciones_nutricionales": {
      "alergias": [],
      "intolerancias": ["lactosa"],
      "alimentos_no_soportados": ["patata", "coliflor", "cerdo"],
      "restricciones_medicas": ["hipotiroidismo_medicado"],
      "notas": "Extraído de E1. N0-N8 deben excluir estos alimentos del plan."
    }
  }
}
```

## ✅ CHECKLIST OBLIGATORIO:

1. **Extraer restricciones nutricionales de E1:**
   - Alergias alimentarias
   - Intolerancias (lactosa, gluten, etc.)
   - Alimentos que el cliente no soporta/no quiere comer
   - Restricciones médicas (hipotiroidismo, diabetes, etc.)
   
   **IMPORTANTE:** Estas restricciones DEBEN pasarse a N0 para que los agentes de nutrición NO incluyan esos alimentos en el plan.

2. **Analizar el plan de entrenamiento E4/E5:**
   - Contar cuántos días tienen entrenamiento de FUERZA/PESAS → Días A
   - Contar cuántos días tienen solo CARDIO/CORE → Días M
   - Contar cuántos días son DESCANSO → Días B

3. **Generar tipos_dia_presentes:**
   ```json
   {
     "usa_dia_A": true/false,  // true si hay al menos 1 día A
     "usa_dia_M": true/false,  // true si hay al menos 1 día M
     "usa_dia_B": true/false,  // true si hay al menos 1 día B
     "count_A": 3,  // número exacto de días A
     "count_M": 0,  // número exacto de días M
     "count_B": 4   // número exacto de días B
   }
   ```

3. **Generar calendario_sugerido:**
   - Día por día (dia_1 a dia_7)
   - Asignar A/M/B según el tipo de entrenamiento de ese día
   - Ejemplo: Si Lunes tiene Full Body con pesas → "dia_1": "A"

4. **IMPORTANTE:** Si NO hay días M (solo pesas y descanso):
   - usa_dia_M = false
   - count_M = 0
   - calendario_sugerido solo tendrá "A" y "B"
   
   Los agentes de nutrición usarán esto para generar SOLO los sets de macros necesarios.

      }
    }
  }
}
```

**CRÍTICO**: 
- Devuelve SIEMPRE el `client_context` completo
- "bridge_for_nutrition" es la fuente de verdad para los agentes de nutrición N0-N8


---

**⚠️ FORMATO DE SALIDA OBLIGATORIO ⚠️**

Tu respuesta DEBE ser EXACTAMENTE:

```json
{
  "client_context": {
    // TODO el objeto completo aquí
  }
}
```

**NO devuelvas**:
- ❌ `{"status": "ok", ...}`
- ❌ Solo el contenido de training
- ❌ Texto explicativo fuera del JSON

**SÍ devuelve**:
- ✅ `{"client_context": { "meta": {...}, "raw_inputs": {...}, "training": {...} }}`

**CRÍTICO:** JSON válido sin texto adicional, comenzando con `{"client_context":`

'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Valida que el input contenga campos necesarios - BLOQUE 2"""
        if "training" not in input_data:
            return False
        
        training = input_data["training"]
        
        # E9 requiere: client_summary, formatted_plan
        return (training.get("client_summary") is not None and
                training.get("formatted_plan") is not None)
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        """
        Valida que devuelva client_context con bridge_for_nutrition lleno
        
        NUEVO (Fase 2): Validamos estructura de salida
        """
        try:
            output = self._extract_json_from_response(raw_output)
            
            if "client_context" not in output:
                raise ValueError("Output no contiene client_context")
            
            client_context = output["client_context"]
            training = client_context.get("training", {})
            
            # Validar que E9 llenó bridge_for_nutrition
            if training.get("bridge_for_nutrition") is None:
                raise ValueError("E9 no llenó training.bridge_for_nutrition")
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error procesando output de E9: {e}")