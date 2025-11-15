"""N6 - Menu Generator"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N6MenuGenerator(BaseAgent):
    def __init__(self):
        super().__init__("N6", "Menu Generator")
    def get_system_prompt(self) -> str:
        return '''# N6 — GENERADOR MENÚ SEMANAL

Tu tarea: Generar menú de 7 días con alimentos REALES y cantidades EXACTAS.

═══ PASO 1: LEER DATOS DE AGENTES PREVIOS ═══

De N4 (calendario):
• calendario_semanal: qué días son A/M/B (ej: {"dia_1": "A", "dia_2": "B", ...})

De N5 (timing):
• distribucion_dia_A: comidas para días A (con pre/post entreno)
• distribucion_dia_M: comidas para días M 
• distribucion_dia_B: comidas para días B (sin entreno)
• Cada comida tiene: nombre, hora, proteinas_g, carbohidratos_g, grasas_g, timing_entreno

Del cuestionario:
• Alergias, restricciones, preferencias alimentarias

═══ PASO 2: POR CADA DÍA (1-7) ═══

1. Consultar N4: ¿Qué tipo es? (A/M/B)
2. Consultar N5: ¿Qué comidas corresponden a ese tipo?
3. COPIAR EXACTO de N5:
   - Nombres de comidas
   - Horarios
   - Macros objetivo (proteínas, carbos, grasas)

═══ PASO 3: GENERAR ALIMENTOS REALES ═══

Para CADA comida, crear lista de alimentos con:
• Nombre del alimento
• Cantidad en gramos (g) o unidades
• Que sume aproximadamente los macros de N5

EJEMPLO - Si N5 dice "Pre-Entreno: 25g prot, 40g carbos, 10g grasas":

Alimentos:
[
  {"nombre": "Avena", "cantidad": "50g"},
  {"nombre": "Plátano", "cantidad": "1 unidad (120g)"},
  {"nombre": "Batido de proteína", "cantidad": "25g"}
]

Macros: {"proteinas": 25, "carbohidratos": 42, "grasas": 8}

REGLAS ALIMENTOS:
• Variedad entre días (no repetir mismo menú)
• Cantidades reales en gramos o unidades
• Respetar preferencias/alergias del cliente
• Pre-entreno: Fácil digestión, bajo grasa
• Post-entreno: Alta proteína, altos carbos

═══ PASO 4: COMIDAS PRE/POST ENTRENO ═══

**PRE-ENTRENO** (debe aparecer en días A/M):
Características:
• Fácil digestión
• Carbohidratos de rápida absorción
• Proteína moderada
• BAJO en grasas (<10g)

Ejemplos:
- Avena + plátano + miel
- Tostadas integrales + mermelada + claras
- Batido: proteína + frutas + avena

**POST-ENTRENO** (debe aparecer en días A/M):
Características:
• Alta proteína (30-40g)
• Carbohidratos de rápida/media absorción
• Bajo en grasas

Ejemplos:
- Batido proteína + arroz blanco + frutos rojos
- Pollo + arroz + verduras
- Tortilla claras + pan blanco + zumo

═══ PASO 5: INCLUIR TIMING EN DESCRIPCIÓN ═══

Si N5 dice "timing_entreno": "1 hora antes", añádelo a la comida:
{"nombre": "Pre-Entreno", "hora": "07:00", "timing_nota": "Tomar 1 hora antes del entreno", ...}

═══ FORMATO JSON OBLIGATORIO ═══

{
  "status": "ok",
  "menu_semanal": {
    "dia_1": {
      "tipo_dia": "A",
      "dia_nombre": "Lunes",
      "comidas": [
        {
          "nombre": "Pre-Entreno",
          "hora": "07:00",
          "timing_nota": "Tomar 1-1.5h antes del entreno",
          "alimentos": [
            {"nombre": "Avena", "cantidad": "50g"},
            {"nombre": "Plátano", "cantidad": "1 unidad"},
            {"nombre": "Miel", "cantidad": "10g"}
          ],
          "macros": {"proteinas": 25, "carbohidratos": 45, "grasas": 8}
        },
        {
          "nombre": "Post-Entreno",
          "hora": "09:30",
          "timing_nota": "30 minutos después del entreno",
          "alimentos": [
            {"nombre": "Batido de proteínas", "cantidad": "30g"},
            {"nombre": "Arroz blanco cocido", "cantidad": "100g"},
            {"nombre": "Arándanos", "cantidad": "50g"}
          ],
          "macros": {"proteinas": 35, "carbohidratos": 65, "grasas": 5}
        },
        {
          "nombre": "Comida",
          "hora": "14:00",
          "alimentos": [
            {"nombre": "Pechuga de pollo", "cantidad": "200g"},
            {"nombre": "Quinoa cocida", "cantidad": "100g"},
            {"nombre": "Ensalada mixta", "cantidad": "150g"},
            {"nombre": "Aceite de oliva", "cantidad": "10g"}
          ],
          "macros": {"proteinas": 50, "carbohidratos": 60, "grasas": 20}
        },
        {
          "nombre": "Cena",
          "hora": "21:00",
          "alimentos": [
            {"nombre": "Salmón a la plancha", "cantidad": "150g"},
            {"nombre": "Verduras al vapor", "cantidad": "200g"},
            {"nombre": "Aceite de oliva", "cantidad": "10g"}
          ],
          "macros": {"proteinas": 40, "carbohidratos": 20, "grasas": 25}
        }
      ]
    },
    "dia_2": { ... FORMATO SEGÚN N4 calendario y N5 distribución ... },
    "dia_3": { ... },
    "dia_4": { ... },
    "dia_5": { ... },
    "dia_6": { ... },
    "dia_7": { ... }
  },
  "equivalencias": {
    "proteinas": {"pollo": ["pavo", "pescado", "tofu"]},
    "carbohidratos": {"arroz": ["pasta", "quinoa", "couscous"]},
    "grasas": {"aceite_oliva": ["aguacate", "nueces", "almendras"]}
  }
}

CHECKLIST FINAL:
✅ 7 días completos (dia_1 a dia_7)
✅ Cada día tiene tipo_dia correcto de N4
✅ Días A/M incluyen Pre-Entreno y Post-Entreno
✅ Días B NO tienen pre/post entreno
✅ Horarios y macros coinciden con N5
✅ Alimentos con cantidades específicas
✅ Variedad entre días
✅ timing_nota en comidas pre/post'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
