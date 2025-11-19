"""
E8 - Auditor Técnico
Verifica coherencia, seguridad y calidad del plan completo

ARQUITECTURA NUEVA (Fase 2):
- Recibe client_context completo
- Lee de: training.safe_sessions, training.mesocycle, training.capacity, training.constraints
- Llena SOLO: training.audit
- Devuelve client_context completo actualizado
"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class E8TechnicalAuditor(BaseAgent):
    """
    E8 - Auditor Técnico
    
    RESPONSABILIDADES (según documento oficial):
    - Verifica equilibrio, volumen, seguridad, coherencia
    - Llena: audit con validaciones y recomendaciones
    - NO modifica otros campos de client_context
    """
    
    def __init__(self):
        super().__init__("E8", "Auditor Técnico")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 E8 — AUDITOR TÉCNICO

## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `training.safe_sessions`: Sesiones finales de E6
   - `training.mesocycle`: Estructura de E4
   - `training.capacity`: Capacidad de E2
   - `training.constraints`: Restricciones de E1

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `training.audit`: Resultado de auditoría completa

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- NO cambies sesiones, mesociclo ni nada más
- SOLO audita y llena training.audit

---

## 🎯 Misión
Verificar la coherencia global del programa de entrenamiento.
El E8 aprueba, detecta problemas y genera recomendaciones.

## ⚙️ Validaciones

### 0️⃣ VOLUMEN MÍNIMO POR DÍA (NUEVO - CRÍTICO)

**VALIDACIÓN OBLIGATORIA:**
- Cada día de entrenamiento debe tener **MÍNIMO 5 ejercicios**
- Si algún día tiene <5 ejercicios → **BLOQUEAR PLAN** y solicitar regeneración

**Contar ejercicios:**
- Solo contar ejercicios principales (no calentamiento)
- No contar ejercicios de movilidad o estiramiento
- Contar ejercicios preventivos (face pull, plancha, etc.)

**Si se detecta <5 ejercicios en algún día:**
```json
{
  "status": "bloqueado",
  "razon_bloqueo": "volumen_insuficiente",
  "detalles": {
    "dia_problema": "Lunes",
    "ejercicios_actuales": 2,
    "ejercicios_minimos_requeridos": 5,
    "deficit": 3
  },
  "accion_requerida": "E5 debe regenerar el día con más ejercicios para alcanzar volumen mínimo"
}
```

### 1️⃣ Biomecánica estructural
- Push/Pull ratio: 0.9-1.1
- Cadera/Rodilla ratio: 0.8-1.2
- Asimetría <10%
- Volumen total dentro del rango del nivel
- **NUEVO:** Mínimo 5 ejercicios por día

### 2️⃣ Temporal y energética
- Cada sesión ≤90 minutos
- Volumen total por semana ≤25% superior al promedio previo
- Si CIT >65 y sesión >85 min → bloquea intensificación

### 3️⃣ Fisiológica
```
if IRG <5 and CIT >60 → status "fatiga_acumulada"
if IRG <4.5 → status "riesgo_sobreentrenamiento"
if IRG >=5 and push_pull_ratio ≈1.0 → status "optimo"
```

### 4️⃣ Progresiva
- Semanas 1→3: aumento gradual de intensidad (RIR ↓)
- Semana 4: reducir volumen (-40-50%) y RIR ↑

## 📤 Output (JSON estandarizado)
```json
{
  "status": "ok",
  "auditoria_final": {
    "estado_general": "aprobado",
    "biomecanica": {
      "push_pull_ratio": 1.02,
      "cadera_rodilla_ratio": 0.93,
      "veredicto": "equilibrado"
    },
    "fisiologia": {
      "CIT": 54,
      "IRG": 6.8,
      "estado_recuperacion": "carga_controlada"
    },
    "clinica": {
      "lesiones_controladas": true,
      "correctivos_aplicados": 3,
      "banderas_activas": []
    }
  },
  "contrato_para_N0": {
    "split": "Upper/Lower",
    "mapa_intensidad": {"duros": 2, "medios": 2, "ligeros": 1},
    "duracion_total": "4 semanas",
    "estado_fisiologico": "carga_controlada"
  }
}
```

---

## 🔄 FORMATO DE SALIDA (CRÍTICO)

Devuelve el `client_context` COMPLETO con tu campo lleno:

```json
{
  "client_context": {
    "meta": { ... },  // Sin cambios
    "raw_inputs": { ... },  // Sin cambios
    "training": {
      // Todos los campos anteriores sin cambios
      "profile": { ... },
      "constraints": { ... },
      "prehab": { ... },
      "progress": { ... },
      "capacity": { ... },
      "adaptation": { ... },
      "mesocycle": { ... },
      "sessions": { ... },
      "safe_sessions": { ... },
      "formatted_plan": { ... },
      // TU CAMPO - el único que debes llenar
      "audit": {
        "status": "aprobado | con_warnings | bloqueado",
        "checks": { ... },
        "warnings": [ ... ],
        "recomendaciones": [ ... ]
      },
      // Mantener el resto
      "bridge_for_nutrition": null
    }
  }
}
```
'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Valida que el input contenga client_context con safe_sessions
        
        NUEVO (Fase 2): Validamos client_context
        """
        if "training" not in input_data:
            return False
        
        training = input_data["training"]
        
        # Debe tener safe_sessions (de E6), mesocycle (E4), capacity (E2), constraints (E1)
        required_fields = ["safe_sessions", "mesocycle", "capacity", "constraints"]
        return all(training.get(field) is not None for field in required_fields)
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        """
        Valida que devuelva client_context con audit lleno
        
        NUEVO (Fase 2): Validamos estructura de salida
        """
        try:
            output = self._extract_json_from_response(raw_output)
            
            if "client_context" not in output:
                raise ValueError("Output no contiene client_context")
            
            client_context = output["client_context"]
            training = client_context.get("training", {})
            
            # Validar que E8 llenó audit
            if training.get("audit") is None:
                raise ValueError("E8 no llenó training.audit")
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error procesando output de E8: {str(e)}")
