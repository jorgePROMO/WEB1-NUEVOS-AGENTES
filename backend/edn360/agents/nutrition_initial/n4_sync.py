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
- E9 tiene "dias_entrenamiento": número de días que entrena/semana (ej: 3)
- E9 tiene "intensidad_entrenamiento": info sobre intensidad

REGLAS DISTRIBUCIÓN SEMANAL:
- Si entrena 3 días/semana: 2-3 días A/M + 4-5 días B
- Si entrena 4 días/semana: 3-4 días A/M + 3 días B
- Si entrena 5 días/semana: 4-5 días A/M + 2 días B

TIPOS DE DÍA:
- Día A (Alto): Días de entrenamiento MÁS INTENSO (ej: pierna, full-body pesado)
- Día M (Medio): Días de entrenamiento moderado
- Día B (Bajo/Descanso): Días SIN entrenamiento

EJEMPLO para 3 días/semana:
Lun→M (entreno), Mar→B (descanso), Mie→A (entreno), Jue→B, Vie→M (entreno), Sáb→B, Dom→B

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
