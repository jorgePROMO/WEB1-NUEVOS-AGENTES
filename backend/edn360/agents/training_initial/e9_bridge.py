"""
E9 - Bridge hacia Nutrición
"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class E9NutritionBridge(BaseAgent):
    def __init__(self):
        super().__init__("E9", "Bridge hacia Nutrición")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 E9 — BRIDGE DE COHERENCIA HACIA NUTRICIÓN

## 🎯 Misión
Convertir los datos técnicos del entrenamiento en un mapa energético cuantificable para nutricionistas (bloque N).
Objetivo: transformar esfuerzo físico en requerimiento calórico.

## ⚙️ Cálculos principales

### Gasto Semanal Estimado (GSE)
```
GSE = (CIT × 6.5) + (minutos_totales_entreno × 7) + (pasos_promedio × 0.04)
```

Ajustes:
- +10% si NEAT alto (>12k pasos/día)
- -10% si recuperación baja o IRG <5
- +5% si KPI principal es fuerza pura

### Clasificación de días A/M/B

**CRÍTICO**: Analiza el TIPO DE ENTRENAMIENTO en el plan E4/E5:

| Tipo | Criterios | Ajuste energético |
|------|-----------|-------------------|
| **A (Alta)** | Días de PESAS/FUERZA/HIPERTROFIA: Sentadillas, press banca, peso muerto, máquinas, trabajo con resistencia | +10-15% kcal / +0.5-1 g/kg CH |
| **M (Media)** | Días de CARDIO/CORE/MOVILIDAD: Cardio steady-state, HIIT, abdominales, estiramientos, yoga, trabajo funcional | ±0% kcal |
| **B (Baja)** | Descanso completo sin actividad física programada | -10-15% kcal / ↓ CH |

**REGLA**: 
- Si el día incluye entrenamiento de FUERZA con PESO (barras, mancuernas, máquinas) → Día A
- Si el día es solo CARDIO, CORE, MOVILIDAD, flexibilidad → Día M
- Si no hay entrenamiento → Día B

**Ejemplo típico**:
- Lun: Full-body con pesas → A
- Mar: Descanso → B
- Mié: Cardio + Core → M
- Jue: Descanso → B
- Vie: Full-body con pesas → A
- Sáb/Dom: Descanso → B

## 📤 Output (JSON estandarizado)
```json
{
  "status": "ok",
  "bridge_output": {
    "tdee_estimado": 2550,
    "gasto_semanal_estimado": 17800,
    "dias_entrenamiento_semana": 3,
    "tipos_dia_presentes": {
      "usa_dia_A": true,
      "usa_dia_M": true,
      "usa_dia_B": true,
      "count_A": 2,
      "count_M": 2,
      "count_B": 3
    },
    "distribucion_energetica": {
      "A": "+12%",
      "M": "0%",
      "B": "-12%"
    },
    "calendario_sugerido": {
      "dia_1": "M",
      "dia_2": "B",
      "dia_3": "A",
      "dia_4": "B",
      "dia_5": "M",
      "dia_6": "B",
      "dia_7": "B"
    },
    "justificacion_calendario": {
      "dia_1": "Lunes: Entrenamiento moderado - Inicio de semana, adaptación",
      "dia_3": "Miércoles: Entrenamiento INTENSO - Mayor volumen/carga de la semana",
      "dia_5": "Viernes: Entrenamiento moderado - Cierre de microciclo"
    },
    "prioridad_metabolica": "hipertrofia"
  },
  "contrato_para_N0": {
    "estado_fisiologico": "carga_controlada",
    "tdee": 2550,
    "dias_entrenamiento": 3,
    "delta_dias_A": "+12%",
    "delta_dias_B": "-12%",
    "prioridad": "hipertrofia",
    "restricciones_nutricionales": {
      "alergias": [],
      "intolerancias": ["lactosa"],
      "alimentos_no_soportados": ["patata", "coliflor", "cerdo"],
      "restricciones_medicas": ["hipotiroidismo_medicado"],
      "notas": "Extraído de E1. N0-N8 deben excluir estos alimentos del plan."
    }
  }
}
```

## ✅ CHECKLIST OBLIGATORIO:

1. **Extraer restricciones nutricionales de E1:**
   - Alergias alimentarias
   - Intolerancias (lactosa, gluten, etc.)
   - Alimentos que el cliente no soporta/no quiere comer
   - Restricciones médicas (hipotiroidismo, diabetes, etc.)
   
   **IMPORTANTE:** Estas restricciones DEBEN pasarse a N0 para que los agentes de nutrición NO incluyan esos alimentos en el plan.

2. **Analizar el plan de entrenamiento E4/E5:**
   - Contar cuántos días tienen entrenamiento de FUERZA/PESAS → Días A
   - Contar cuántos días tienen solo CARDIO/CORE → Días M
   - Contar cuántos días son DESCANSO → Días B

3. **Generar tipos_dia_presentes:**
   ```json
   {
     "usa_dia_A": true/false,  // true si hay al menos 1 día A
     "usa_dia_M": true/false,  // true si hay al menos 1 día M
     "usa_dia_B": true/false,  // true si hay al menos 1 día B
     "count_A": 3,  // número exacto de días A
     "count_M": 0,  // número exacto de días M
     "count_B": 4   // número exacto de días B
   }
   ```

3. **Generar calendario_sugerido:**
   - Día por día (dia_1 a dia_7)
   - Asignar A/M/B según el tipo de entrenamiento de ese día
   - Ejemplo: Si Lunes tiene Full Body con pesas → "dia_1": "A"

4. **IMPORTANTE:** Si NO hay días M (solo pesas y descanso):
   - usa_dia_M = false
   - count_M = 0
   - calendario_sugerido solo tendrá "A" y "B"
   
   Los agentes de nutrición usarán esto para generar SOLO los sets de macros necesarios.

CRÍTICO: "tipos_dia_presentes" es la fuente de verdad para nutrición.
'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
