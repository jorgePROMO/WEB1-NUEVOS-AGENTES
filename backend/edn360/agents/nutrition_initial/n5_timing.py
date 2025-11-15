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
• "horario_desayuno", "horario_comida", "horario_cena": Sus horarios habituales del cliente
• Busca también: "desayuno", "comida", "cena" con valores de hora

**CRÍTICO - LEER HORARIOS DEL CLIENTE:**
Si el input contiene horarios específicos (ej: "horario_desayuno": "07:00"), ÚSALOS tal cual.
NO inventes horarios si el cliente ya especificó los suyos.

═══ PASO 2: DETERMINAR HORARIO DE ENTRENO ═══

Si dice "mañana" o hora < 11:00 → ENTRENA MAÑANA
Si dice "mediodía" o 11:00-15:00 → ENTRENA MEDIODÍA  
Si dice "tarde"/"noche" o > 15:00 → ENTRENA TARDE

═══ PASO 3: CREAR DISTRIBUCIONES SEGÚN HORARIO ═══

**ENTRENA MAÑANA** (Ejemplo: entrena 8:00-9:00):

PASO 3A: Identificar horarios del cliente del cuestionario:
- horario_desayuno (ej: "07:00")
- horario_comida (ej: "14:00")  
- horario_cena (ej: "21:00")

PASO 3B: Calcular GAPS entre comidas:
- Gap1: Post-entreno (09:30) → Comida (14:00) = 4.5 horas
- Gap2: Comida (14:00) → Cena (21:00) = 7 horas

REGLA DE GAPS: Si hay un gap > 4 horas, AÑADIR comida intermedia (media mañana o merienda)

Días A/M (con entreno) - EJEMPLO con gaps corregidos:
1. Pre-Entreno: 1-1.5h antes del entreno (07:00) - 18% kcal
   {"nombre": "Pre-Entreno", "hora": "07:00", "timing_entreno": "1h antes del entreno", "proteinas_g": XX, "carbohidratos_g": XX, "grasas_g": XX}
2. Post-Entreno: 30-60min después (09:30) - 25% kcal
   {"nombre": "Post-Entreno", "hora": "09:30", "timing_entreno": "30min después del entreno", "proteinas_g": XX, "carbohidratos_g": XX, "grasas_g": XX}
3. Media Mañana: mitad del gap (11:45) - 12% kcal (SOLO si gap > 4h)
   {"nombre": "Media Mañana", "hora": "11:45", "proteinas_g": XX, "carbohidratos_g": XX, "grasas_g": XX}
4. Comida: horario habitual cliente (14:00) - 25% kcal
5. Merienda: mitad del gap (17:30) - 10% kcal (SOLO si gap > 4h)
   {"nombre": "Merienda", "hora": "17:30", "proteinas_g": XX, "carbohidratos_g": XX, "grasas_g": XX}
6. Cena: horario habitual (21:00) - 20% kcal

Días B (descanso) - CON comidas intermedias si hay gaps:
1. Desayuno: hora habitual (07:00) - 25% kcal
2. Media Mañana: si gap > 4h (10:30) - 15% kcal
3. Comida: hora habitual (14:00) - 30% kcal
4. Merienda: si gap > 4h (17:30) - 15% kcal
5. Cena: hora habitual (21:00) - 25% kcal

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

Usa los macros totales de N2 y distribúyelos según % de calorías por comida:

**Días A/M (entreno):**
• Pre-entreno: 18% kcal → Bajo grasas (5-10g), carbos medios, proteína moderada
• Post-entreno: 25% kcal → Alto carbos, alta proteína, bajo grasas
• Media Mañana: 12% kcal → Snack ligero, proteína + carbos
• Comida: 25% kcal → Balanceado
• Merienda: 10% kcal → Snack ligero
• Cena: 20% kcal → Proteína + verduras, bajo carbos

**Días B (descanso):**
Distribuir equitativamente entre las comidas (sin pre/post entreno)
Si 5 comidas: 25% + 15% + 30% + 15% + 25%
Si 4 comidas: 30% + 20% + 25% + 25%
Si 3 comidas: 35% + 35% + 30%

**IMPORTANTE:** La suma de todos los porcentajes DEBE ser 100%

═══ PASO 5: ESPECIFICAR TIMING EXPLÍCITO ═══

CADA comida pre/post debe incluir:
"timing_entreno": "1.5 horas antes del entreno" o "30 minutos después del entreno"

═══ FORMATO JSON OBLIGATORIO ═══

{
  "status": "ok",
  "horario_entrenamiento": "mañana|tarde|noche",
  "hora_entreno_detectada": "08:00",
  "numero_comidas_base": 6,
  "distribucion_dia_A": {
    "numero_comidas": 6,
    "comidas": [
      {"nombre": "Pre-Entreno", "hora": "07:00", "timing_entreno": "1 hora antes", "proteinas_g": 30, "carbohidratos_g": 45, "grasas_g": 8},
      {"nombre": "Post-Entreno", "hora": "09:30", "timing_entreno": "30min después", "proteinas_g": 40, "carbohidratos_g": 65, "grasas_g": 6},
      {"nombre": "Media Mañana", "hora": "11:45", "proteinas_g": 20, "carbohidratos_g": 25, "grasas_g": 5},
      {"nombre": "Comida", "hora": "14:00", "proteinas_g": 40, "carbohidratos_g": 55, "grasas_g": 15},
      {"nombre": "Merienda", "hora": "17:30", "proteinas_g": 18, "carbohidratos_g": 20, "grasas_g": 4},
      {"nombre": "Cena", "hora": "21:00", "proteinas_g": 32, "carbohidratos_g": 40, "grasas_g": 22}
    ]
  },
  "distribucion_dia_M": {
    "numero_comidas": 6,
    "comidas": [
      {"nombre": "Pre-Entreno", "hora": "07:00", "timing_entreno": "1 hora antes", "proteinas_g": 30, "carbohidratos_g": 45, "grasas_g": 8},
      {"nombre": "Post-Entreno", "hora": "09:30", "timing_entreno": "30min después", "proteinas_g": 40, "carbohidratos_g": 65, "grasas_g": 6},
      {"nombre": "Media Mañana", "hora": "11:45", "proteinas_g": 20, "carbohidratos_g": 25, "grasas_g": 5},
      {"nombre": "Comida", "hora": "14:00", "proteinas_g": 40, "carbohidratos_g": 55, "grasas_g": 15},
      {"nombre": "Merienda", "hora": "17:30", "proteinas_g": 18, "carbohidratos_g": 20, "grasas_g": 4},
      {"nombre": "Cena", "hora": "21:00", "proteinas_g": 32, "carbohidratos_g": 40, "grasas_g": 22}
    ]
  },
  "distribucion_dia_B": {
    "numero_comidas": 5,
    "comidas": [
      {"nombre": "Desayuno", "hora": "08:00", "proteinas_g": 40, "carbohidratos_g": 50, "grasas_g": 18},
      {"nombre": "Media Mañana", "hora": "11:00", "proteinas_g": 22, "carbohidratos_g": 28, "grasas_g": 8},
      {"nombre": "Comida", "hora": "14:00", "proteinas_g": 45, "carbohidratos_g": 60, "grasas_g": 20},
      {"nombre": "Merienda", "hora": "17:30", "proteinas_g": 22, "carbohidratos_g": 28, "grasas_g": 8},
      {"nombre": "Cena", "hora": "21:00", "proteinas_g": 41, "carbohidratos_g": 54, "grasas_g": 16}
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
