"""N4 - A/M/B Synchronizer"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N4AMBSynchronizer(BaseAgent):
    def __init__(self):
        super().__init__("N4", "A/M/B Synchronizer")
    def get_system_prompt(self) -> str:
        return '''# N4 — SINCRONIZADOR A/M/B
Crear calendario semanal A/M/B sincronizado con DÍAS REALES de entrenamiento del cliente.

CRÍTICO - LEE E9 Y CUESTIONARIO:

**DE E9 (training_bridge)**:
- "dias_entrenamiento_semana": cuántos días entrena
- "calendario_sugerido": distribución A/M/B si existe
- "justificacion_calendario": explicación de cada día

**DEL CUESTIONARIO**:
- "dias_entrenamiento": qué días específicos (ej: "Lunes, Miércoles, Viernes")
- "horario_entrenamiento": cuándo entrena (mañana/tarde/noche)
- "tipo_entrenamiento": si hace pesas, cardio, mixto

USA EL CALENDARIO SUGERIDO DE E9:
- Si E9 ya propone calendario_sugerido → ÚSALO DIRECTAMENTE
- Valida que coincida con días del cuestionario

TIPOS DE DÍA (según E9):
- Día A (Alto): Días de PESAS/FUERZA/HIPERTROFIA
- Día M (Medio): Días de CARDIO/CORE/MOVILIDAD
- Día B (Bajo/Descanso): Días SIN entrenamiento

IMPORTANTE: Respeta días específicos del cliente en cuestionario

DEVUELVE JSON:
{
  "status": "ok",
  "dias_entrenamiento_semana": 3,
  "calendario_semanal": {
    "dia_1": "M",
    "dia_2": "B",
    "dia_3": "A",
    "dia_4": "B",
    "dia_5": "M",
    "dia_6": "B",
    "dia_7": "B"
  },
  "descripcion_dias": {
    "dia_1": "Lunes - Entrenamiento moderado",
    "dia_2": "Martes - Descanso",
    "dia_3": "Miércoles - Entrenamiento intenso",
    "dia_4": "Jueves - Descanso",
    "dia_5": "Viernes - Entrenamiento moderado",
    "dia_6": "Sábado - Descanso",
    "dia_7": "Domingo - Descanso"
  },
  "ajuste_calorico": {
    "A": "+15% sobre base",
    "M": "+5% sobre base",
    "B": "-10% bajo base"
  }
}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
