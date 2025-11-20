"""
E7 - Visualizador de Carga
Formatea plan para presentación al cliente

ARQUITECTURA NUEVA (Fase 2):
- Recibe client_context completo
- Lee de: training.safe_sessions, training.mesocycle
- Llena SOLO: training.formatted_plan
- Devuelve client_context completo actualizado
"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class E7LoadAnalyst(BaseAgent):
    def __init__(self):
        super().__init__("E7", "Analista de Carga Interna")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 E7 — VISUALIZADOR DE PLAN

## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `training.safe_sessions`: Sesiones finales de E6
   - `training.mesocycle`: Estructura de E4

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `training.formatted_plan`: Plan formateado para presentación

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- SOLO llena training.formatted_plan

---

## 🎯 Misión
Formatear el plan de entrenamiento para presentación al cliente.
Transformas datos técnicos en formato comprensible y visual.

## ⚙️ Cálculos principales

### Carga Interna Total (CIT)
```
CIT = Σ (series_totales × (10 − RIR_real)) / dias_entrenados
```

**Escala:**
- <35: Estímulo insuficiente → ↑ Volumen 5-10%
- 35-55: Óptimo → Mantener
- 56-65: Alta carga controlada → Monitorizar
- >65: Riesgo de fatiga crónica → Reducir 10-15%

### Índice de Recuperación Global (IRG)
```
IRG = (sueno_h + energia + adherencia%/20 − estres − dolor/2)
```

**Interpretación:**
- ≥7: Excelente → Mantener progresión
- 5-6.9: Aceptable → No intensificar
- <5: Comprometido → Reducir volumen
- <4: Riesgo sobreentrenamiento → Pausa obligatoria

## 📤 Output (JSON estandarizado)
```json
{
  "status": "ok",
  "cit_semanal": 52,
  "irg_score": 6.8,
  "estado": "carga_alta_controlada",
  "analisis_semana": {
    "carga_interna_total": 52,
    "indice_recuperacion_global": 6.8,
    "recomendaciones": [
      "Mantener volumen actual pero no intensificar.",
      "Añadir un día de descanso pasivo."
    ],
    "ajustes_propuestos": {
      "volumen_total": "mantener",
      "frecuencia": "mantener",
      "intensidad": "-5% accesorios"
    }
  },
  "contrato_para_E8": {
    "estado_general": "estable",
    "riesgos_detectados": [],
    "senal_metabolica": "alta_carga_controlada"
  }
}
```

---

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
      // TU CAMPO:
      "formatted_plan": {
        "resumen": "Plan de 4 semanas para hipertrofia...",
        "plan_visual": "...",
        "instrucciones": [...]
      },
      // Resto sin cambios:
      "audit": null,
      "bridge_for_nutrition": null
    }
  }
}
```

**FORMATO OBLIGATORIO**:
- Tu respuesta DEBE comenzar con `{"client_context": {`
- NUNCA devuelvas el JSON directamente sin este wrapper
- SIEMPRE incluye todos los campos del client_context, no solo training


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
        """
        Valida que el input contenga client_context con campos necesarios
        
        NUEVO (Fase 2): Validamos client_context
        """
        if "training" not in input_data:
            return False
        
        training = input_data["training"]
        
        # Debe tener campos requeridos
        return (training.get("safe_sessions") is not None and
                training.get("mesocycle") is not None)
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        """
        Valida que devuelva client_context con formatted_plan lleno
        
        NUEVO (Fase 2): Validamos estructura de salida
        """
        try:
            output = self._extract_json_from_response(raw_output)
            
            if "client_context" not in output:
                raise ValueError("Output no contiene client_context")
            
            client_context = output["client_context"]
            training = client_context.get("training", {})
            
            # Validar que E7 llenó formatted_plan
            if training.get("formatted_plan") is None:
                raise ValueError("E7 no llenó training.formatted_plan")
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error procesando output de E7: {e}")