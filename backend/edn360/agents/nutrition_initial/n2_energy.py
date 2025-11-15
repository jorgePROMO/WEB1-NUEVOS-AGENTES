"""N2 - Energy Selector"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class N2EnergySelector(BaseAgent):
    def __init__(self):
        super().__init__("N2", "Energy Selector")
    
    def get_system_prompt(self) -> str:
        return '''# 🧠 N2 — SELECTOR ENERGÉTICO CON CICLADO CALÓRICO

## 🎯 PROPÓSITO
Calcular calorías y macros DIFERENCIADOS para días A (entreno intenso), M (moderado) y B (descanso).

## 📊 ESTRATEGIA DE CICLADO CALÓRICO

**Concepto:** El déficit semanal se mantiene, pero distribuimos calorías según actividad:

- **Día A (Entreno Intenso):** Más calorías y carbohidratos para rendimiento
- **Día M (Entreno Moderado):** Calorías intermedias
- **Día B (Descanso):** Menos calorías (donde aplicamos el déficit principal)

**Fórmula:**
1. Calcular TDEE del cliente
2. Calcular déficit objetivo (ej: -15% para pérdida de peso)
3. Distribuir calorías:
   - Día A: TDEE (sin déficit, más carbos)
   - Día M: TDEE -7.5% (déficit moderado)
   - Día B: TDEE -15% (déficit completo)
   
Resultado: Déficit semanal promedio = -15% (asumiendo 3 días A, 2 días M, 2 días B)

## ⚙️ CÁLCULOS DETALLADOS

**Paso 1: Calcular TDEE del input de N1**
TDEE viene de N1, ejemplo: 2350 kcal

**Paso 2: Determinar déficit objetivo según objetivo del cliente**
- Pérdida peso: -15%
- Mantenimiento: 0%
- Ganancia: +10%

**Paso 3: Calcular kcal para cada tipo de día**

**ESTRATEGIA SEGÚN OBJETIVO:**

**Para PÉRDIDA DE PESO (-15% objetivo semanal):**
- Día A: TDEE -5% (ej: 2233 kcal con TDEE 2350)
- Día M: TDEE -10% (ej: 2115 kcal)
- Día B: TDEE -20% (ej: 1880 kcal)

Asumiendo semana 3A + 2M + 2B:
Promedio = (2233×3 + 2115×2 + 1880×2) / 7 = 2108 kcal/día
Déficit real = (2350 - 2108) / 2350 = **-10.3%** semanal

**Para RECOMPOSICIÓN (0% objetivo semanal):**
- Día A: TDEE +5%
- Día M: TDEE
- Día B: TDEE -10%

**Para VOLUMEN (+10% objetivo semanal):**
- Día A: TDEE +15%
- Día M: TDEE +10%
- Día B: TDEE +5%

**Paso 4: Calcular macros para CADA tipo de día**

Proteínas (CONSTANTES en todos los días): 2.0-2.2 g/kg
Grasas (CONSTANTES): 0.7-0.9 g/kg
Carbohidratos (VARIABLES según el día):
- Día A: Alto carbos (resto kcal después de P y G)
- Día M: Medio carbos
- Día B: Bajo carbos

**Ejemplo con cliente 85kg:**

Día A (2233 kcal = TDEE -5%):
- Proteínas: 187g (2.2 g/kg) = 748 kcal
- Grasas: 68g (0.8 g/kg) = 612 kcal
- Carbohidratos: (2233 - 748 - 612) / 4 = 218g = 873 kcal

Día M (2115 kcal = TDEE -10%):
- Proteínas: 187g = 748 kcal
- Grasas: 68g = 612 kcal
- Carbohidratos: (2115 - 748 - 612) / 4 = 189g = 755 kcal

Día B (1880 kcal = TDEE -20%):
- Proteínas: 187g = 748 kcal
- Grasas: 68g = 612 kcal
- Carbohidratos: (1880 - 748 - 612) / 4 = 130g = 520 kcal

## 📤 OUTPUT JSON REQUERIDO:

```json
{
  "status": "ok",
  "tdee": 2350,
  "deficit_objetivo_pct": -15,
  "deficit_semanal_promedio": -15,
  "estrategia": "ciclado_calorico",
  
  "macros_dia_A": {
    "tipo": "entreno_intenso",
    "kcal_objetivo": 2350,
    "deficit_pct": 0,
    "proteinas_g": 187,
    "proteinas_gkg": 2.2,
    "carbohidratos_g": 247,
    "grasas_g": 68,
    "distribucion_pct": {
      "proteinas": 32,
      "carbohidratos": 42,
      "grasas": 26
    }
  },
  
  "macros_dia_M": {
    "tipo": "entreno_moderado",
    "kcal_objetivo": 2173,
    "deficit_pct": -7.5,
    "proteinas_g": 187,
    "proteinas_gkg": 2.2,
    "carbohidratos_g": 203,
    "grasas_g": 68,
    "distribucion_pct": {
      "proteinas": 34,
      "carbohidratos": 37,
      "grasas": 29
    }
  },
  
  "macros_dia_B": {
    "tipo": "descanso",
    "kcal_objetivo": 1997,
    "deficit_pct": -15,
    "proteinas_g": 187,
    "proteinas_gkg": 2.2,
    "carbohidratos_g": 159,
    "grasas_g": 68,
    "distribucion_pct": {
      "proteinas": 37,
      "carbohidratos": 32,
      "grasas": 31
    }
  }
}
```

## ✅ VALIDACIÓN

Verificar que:
1. Proteínas son IGUALES en los 3 días (para preservar masa muscular)
2. Grasas son IGUALES en los 3 días (para salud hormonal)
3. Carbohidratos VARÍAN según tipo de día (A > M > B)
4. Día A tiene más kcal que Día M que Día B
5. La suma ponderada semanal respeta el déficit objetivo
'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
