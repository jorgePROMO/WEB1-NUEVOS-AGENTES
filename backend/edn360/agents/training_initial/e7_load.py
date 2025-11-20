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
        return '''# 🧠 E7 — ANALISTA DE CARGA INTERNA Y RECUPERACIÓN

## 🎯 Misión
Evaluar semanalmente la respuesta fisiológica del atleta frente al entrenamiento ejecutado.
El E7 decide si se puede apretar más, mantener o aflojar el estímulo.

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

**CRÍTICO:** Los campos "cit_semanal" e "irg_score" DEBEN estar en el root level del JSON.
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
            raise ValueError(f"Error procesando output de E7: {{str(e)}}")