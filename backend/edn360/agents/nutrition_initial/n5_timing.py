"""N5 - Timing & Distribution"""
from typing import Dict, Any
from ..base_agent import BaseAgent
import logging

logger = logging.getLogger(__name__)

class N5TimingDistributor(BaseAgent):
    def __init__(self):
        super().__init__("N5", "Timing Distributor")
    def get_system_prompt(self) -> str:
        return '''# N5 — TIMING & DISTRIBUCIÓN DE COMIDAS

Tu tarea: Crear distribución de comidas con horarios y macros ESPECÍFICOS adaptados al horario de entrenamiento del cliente.

═══ PASO 1: LEER CUESTIONARIO DEL CLIENTE ═══

Busca en el input estos campos clave:
• "horario_entrenamiento" o "horario_entreno": CUANDO entrena (ej: "mañana", "8:00", "tarde")
• "numero_comidas": Cuántas comidas hace (3, 4, 5)
• "horario_desayuno", "horario_comida", "horario_cena": Sus horarios habituales
• Busca también: "desayuno", "comida", "cena" con valores de hora

═══ PASO 2: DETERMINAR HORARIO DE ENTRENO ═══

Si dice "mañana" o hora < 11:00 → ENTRENA MAÑANA
Si dice "mediodía" o 11:00-15:00 → ENTRENA MEDIODÍA  
Si dice "tarde"/"noche" o > 15:00 → ENTRENA TARDE

═══ PASO 3: CREAR DISTRIBUCIONES SEGÚN HORARIO ═══

**ENTRENA MAÑANA** (Ejemplo: entrena 8:00-9:00):
Días A/M (con entreno):
1. Pre-entreno: 1-1.5h antes del entreno (ej: 07:00) - 20-25% kcal
   {"nombre": "Pre-Entreno", "hora": "07:00", "timing_entreno": "1h antes del entreno", "proteinas_g": XX, "carbohidratos_g": XX, "grasas_g": XX}
2. Post-entreno: 30-60min después (ej: 09:30) - 25-30% kcal
   {"nombre": "Post-Entreno", "hora": "09:30", "timing_entreno": "30min después del entreno", "proteinas_g": XX, "carbohidratos_g": XX, "grasas_g": XX}
3. Comida: horario habitual cliente (ej: 14:00) - 30% kcal
4. Cena: horario habitual (ej: 21:00) - 25% kcal

Días B (descanso):
1. Desayuno: hora habitual - 30% kcal
2. Comida: hora habitual - 35% kcal
3. Cena: hora habitual - 35% kcal

**ENTRENA TARDE** (Ejemplo: entrena 18:00-19:00):
Días A/M (con entreno):
1. Desayuno: hora habitual - 25% kcal
2. Comida: hora habitual - 30% kcal
3. Pre-entreno: 1.5-2h antes (ej: 16:00) - 20% kcal
   {"nombre": "Pre-Entreno", "hora": "16:00", "timing_entreno": "2h antes del entreno", ...}
4. Post-entreno: inmediato (ej: 19:15) - 25% kcal
   {"nombre": "Post-Entreno", "hora": "19:15", "timing_entreno": "Inmediato post-entreno", ...}

Días B:
(sin pre/post entreno, distribuir en comidas normales)

═══ PASO 4: CALCULAR MACROS POR COMIDA ═══

Usa los macros totales de N2 y distribúyelos:
• Pre-entreno: Bajo grasas (5-10g), carbos medios, proteína moderada
• Post-entreno: Alto carbos, alta proteína, bajo grasas
• Resto: Balanceado según % de calorías

═══ PASO 5: ESPECIFICAR TIMING EXPLÍCITO ═══

CADA comida pre/post debe incluir:
"timing_entreno": "1.5 horas antes del entreno" o "30 minutos después del entreno"

═══ FORMATO JSON OBLIGATORIO ═══

{
  "status": "ok",
  "horario_entrenamiento": "mañana|tarde|noche",
  "hora_entreno_detectada": "08:00",
  "numero_comidas_base": 4,
  "distribucion_dia_A": {
    "numero_comidas": 4,
    "comidas": [
      {"nombre": "Pre-Entreno", "hora": "07:00", "timing_entreno": "1 hora antes", "proteinas_g": 25, "carbohidratos_g": 40, "grasas_g": 10},
      {"nombre": "Post-Entreno", "hora": "09:30", "timing_entreno": "30min después", "proteinas_g": 35, "carbohidratos_g": 60, "grasas_g": 5},
      {"nombre": "Comida", "hora": "14:00", "proteinas_g": 50, "carbohidratos_g": 60, "grasas_g": 20},
      {"nombre": "Cena", "hora": "21:00", "proteinas_g": 40, "carbohidratos_g": 40, "grasas_g": 25}
    ]
  },
  "distribucion_dia_M": { ... MISMO FORMATO ... },
  "distribucion_dia_B": {
    "numero_comidas": 3,
    "comidas": [
      {"nombre": "Desayuno", "hora": "08:00", "proteinas_g": 35, "carbohidratos_g": 50, "grasas_g": 20},
      {"nombre": "Comida", "hora": "14:00", "proteinas_g": 45, "carbohidratos_g": 55, "grasas_g": 25},
      {"nombre": "Cena", "hora": "21:00", "proteinas_g": 40, "carbohidratos_g": 45, "grasas_g": 20}
    ]
  }
}

CRÍTICO: 
✅ SIEMPRE incluir Pre-Entreno y Post-Entreno en días A/M
✅ SIEMPRE calcular macros específicos (no "N/A")
✅ SIEMPRE incluir "timing_entreno" en pre/post
✅ Horarios basados en cuestionario del cliente'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Valida que el input contenga datos de horario de entrenamiento"""
        if not input_data or len(input_data) == 0:
            return False
        
        # Verificar que tenga al menos uno de estos campos de horario
        has_training_schedule = any([
            "horario_entrenamiento" in input_data,
            "horario_preferido" in input_data,
            "hora_entreno" in input_data,
            "entrena_manana_tarde" in input_data
        ])
        
        if not has_training_schedule:
            logger.warning(f"⚠️ N5: Input no contiene información de horario de entrenamiento")
        
        # Aún así retornar True para no bloquear (usar defaults)
        return True
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
