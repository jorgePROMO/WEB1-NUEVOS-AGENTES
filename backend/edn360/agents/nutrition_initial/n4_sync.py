"""N4 - A/M/B Synchronizer"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N4AMBSynchronizer(BaseAgent):
    def __init__(self):
        super().__init__("N4", "A/M/B Synchronizer")
    def get_system_prompt(self) -> str:
        return '''# N4 — SINCRONIZADOR A/M/B
Crear calendario semanal A/M/B sincronizado con DÍAS REALES de entrenamiento del cliente.

CRÍTICO - LEE training_bridge DE E9:
- E9 tiene "dias_entrenamiento_semana": número de días (ej: 3)
- E9 tiene "calendario_sugerido": distribución A/M/B ya calculada
- E9 tiene "justificacion_calendario": explicación de cada día

USA EL CALENDARIO SUGERIDO DE E9:
- Si E9 ya propone calendario_sugerido → ÚSALO DIRECTAMENTE
- Si no existe, genera uno basado en días_entrenamiento_semana

REGLAS SI GENERAS CALENDARIO:
- 3 días/semana: 1 día A (más intenso) + 2 días M + 4 días B
- 4 días/semana: 2 días A + 2 días M + 3 días B
- 5 días/semana: 2 días A + 3 días M + 2 días B

TIPOS DE DÍA:
- Día A (Alto): Día con MAYOR volumen/intensidad de la semana
- Día M (Medio): Días de entrenamiento estándar/moderado
- Día B (Bajo/Descanso): Días SIN entrenamiento

PRIORIDAD: Usa E9.calendario_sugerido si existe

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
