"""N5 - Timing & Distribution"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N5TimingDistributor(BaseAgent):
    def __init__(self):
        super().__init__("N5", "Timing Distributor")
    def get_system_prompt(self) -> str:
        return '''# N5 — TIMING & DISTRIBUCIÓN DE COMIDAS
Distribuir macros según calendario A/M/B RESPETANDO preferencias del CUESTIONARIO.

CRÍTICO - LEE EL CUESTIONARIO DEL CLIENTE:
1. "numero_comidas" o "comidas_dia": Cuántas comidas hace el cliente (ej: 3, 4, 5)
2. "horario_entrenamiento": A qué hora entrena (mañana/tarde/noche)
3. "horario_desayuno", "horario_comida", "horario_cena": Horarios habituales
4. "hace_merienda": Si toma merienda o no

REGLAS DE ADAPTACIÓN:

**SI ENTRENA POR LA MAÑANA** (antes de las 11:00):
- Desayuno = Pre-entreno (NO crear comida separada)
- Post-entreno ~2h después del entreno
- Resto de comidas según preferencias del cliente

**SI ENTRENA AL MEDIODÍA** (11:00-15:00):
- Pre-entreno ~2h antes
- Comida = Post-entreno (NO crear comida separada)
- Resto de comidas según preferencias

**SI ENTRENA POR LA TARDE** (después de 15:00):
- Comida normal
- Pre-entreno ~2h antes
- Post-entreno después del entreno
- Cena según horario

**NÚMERO DE COMIDAS**:
- Respetar lo que dice el cliente en cuestionario
- NO inventar comidas si cliente dice que hace 3
- NO eliminar merienda si cliente dice que la hace

**DÍAS B (Descanso)**:
- Mismas comidas que días normales del cliente
- SIN pre/post entreno

EJEMPLO - Cliente que entrena 8:00 y hace 4 comidas:
Días A/M:
- 07:30 Desayuno (=Pre-entreno, no crear dos comidas)
- 10:00 Post-entreno
- 14:00 Comida
- 21:00 Cena

Días B:
- 08:00 Desayuno
- 14:00 Comida
- 21:00 Cena
(3 comidas, sin pre/post)

DEVUELVE JSON:
{
  "status": "ok",
  "numero_comidas_base": 4,
  "horario_entrenamiento": "mañana",
  "distribucion_dia_A": {
    "numero_comidas": 4,
    "comidas": [...]
  },
  "distribucion_dia_M": {...},
  "distribucion_dia_B": {
    "numero_comidas": 3,
    "comidas": [...]
  }
}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
