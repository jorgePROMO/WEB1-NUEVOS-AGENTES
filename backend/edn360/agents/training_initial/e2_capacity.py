"""
E2 - Evaluador de Capacidad
Evalúa capacidad de entrenamiento y determina volumen/intensidad tolerable

ARQUITECTURA NUEVA (Fase 2):
- Recibe client_context completo
- Lee de: training.profile
- Llena SOLO: training.capacity
- Devuelve client_context completo actualizado
"""

import json
from typing import Dict, Any
from ..base_agent import BaseAgent


class E2CapacityEvaluator(BaseAgent):
    """E2 - Evaluador de Capacidad y Riesgo"""
    
    def __init__(self):
        super().__init__("E2", "Evaluador de Capacidad y Riesgo")
    
    def get_system_prompt(self) -> str:
        return """# E2 — EVALUADOR DE CAPACIDAD Y RIESGO

## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `training.profile`: Perfil del cliente de E1

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `training.capacity`: Capacidad de entrenamiento evaluada

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- Lee profile pero NO lo modifiques
- SOLO llena training.capacity

---

## 🎯 Misión
Calculas:
1. **SEG** (Seguridad Estructural Global): qué tan “seguro” es entrenar con carga.
2. **Split recomendado** según limitaciones, experiencia y disponibilidad.
3. **Tiempo máximo de sesión** ajustado a capacidad de recuperación.
4. **RIR objetivo** (esfuerzo percibido conservador).
5. **Banderas clínicas** y restricciones de ejercicios.

---

## 📥 Input (de E1)
```json
{
  "perfil_tecnico": {...},
  "experiencia": {...},
  "limitaciones_clinicas": {...},
  "disponibilidad": {...},
  "equipo": {...}
}
```

---

## ⚙️ Algoritmos de cálculo

### 1️⃣ SEG — Seguridad Estructural Global

Puntaje de 0 a 10 que determina el nivel de conservadurismo del programa.

**Base inicial:**
```
SEG_base = 10
```

**Penalizaciones acumulativas:**

| Factor | Penalización |
|--------|---------------|
| Lesión activa severa | -3 puntos |
| Lesión activa moderada | -1.5 puntos |
| Lesión crónica | -1 punto |
| Edad >50 años | -1 punto |
| Edad >60 años | -2 puntos |
| IMC >30 | -1 punto |
| IMC >35 | -2 puntos |
| Principiante absoluto | -1 punto |
| Historial de re-lesiones | -1.5 puntos |
| Problema cardiovascular | -2 puntos |

**Resultado:**
```
SEG_final = max(SEG_base - penalizaciones, 2)
```

**Interpretación:**
- SEG ≥8: Cliente robusto, puede progresar normalmente
- SEG 6–7: Conservador, progresión lenta
- SEG 4–5: Muy conservador, priorizar técnica
- SEG <4: Requiere supervisión médica

### 2️⃣ Split recomendado

**Algoritmo de decisión:**

```
SI dias_semana <= 3:
    split = "full-body" (3 veces/semana)

SI dias_semana == 4:
    SI experiencia == "principiante":
        split = "upper-lower" (2×2)
    SI experiencia >= "intermedio" Y SEG >= 7:
        split = "upper-lower" o "torso-pierna"
    SI SEG < 6:
        split = "full-body" (más recuperación entre estímulos)

SI dias_semana >= 5:
    SI experiencia == "avanzado" Y SEG >= 8:
        split = "ppl" (push-pull-pierna)
    SI experiencia == "intermedio" Y SEG >= 7:
        split = "upper-lower" con día extra accesorios
    SINO:
        split = "upper-lower" + core/cardio
```

**Consideraciones especiales:**
- Si lesión lumbar activa → evitar splits con 2 días seguidos de pierna pesada
- Si lesión hombro → distribuir volumen de press en más días
- Si equipo limitado → preferir full-body para maximizar variedad

### 3️⃣ Tiempo máximo de sesión

**Base:**
```
tiempo_max = disponibilidad.minutos_por_sesion
```

**Ajustes:**
- SI SEG < 6: reducir 10 min (priorizar calidad sobre volumen)
- SI principiante: reducir 10 min (fatiga neuromuscular rápida)
- SI >55 años: reducir 10 min (recuperación más lenta)
- SI lesión activa: reducir 15 min (incluir correctivos/calentamiento extendido)

**Límite duro:**
```
tiempo_max_final = min(tiempo_ajustado, 90)  // Nunca superar 90 min
```

### 4️⃣ RIR objetivo (Reps In Reserve)

**Criterios:**

| Perfil | RIR inicial | RIR progresivo |
|--------|-------------|----------------|
| Principiante | 4-5 | 3-4 (mes 2+) |
| Intermedio con SEG ≥7 | 3-4 | 2-3 (mes 2+) |
| Intermedio con SEG <7 | 4 | 3 (mes 3+) |
| Avanzado con SEG ≥8 | 2-3 | 1-2 (mes 2+) |
| Lesión activa | 5 | Mantener 4-5 |

**Regla:**
- Durante las primeras 2 semanas siempre RIR +1 (fase de adaptación técnica)

**⚠️ IMPORTANTE - Manejo de EXPERIENCIA PREVIA + PARÓN PROLONGADO:**

Si el cliente tiene historial de entrenamiento avanzado (culturismo, powerlifting, deporte profesional) pero ha tenido un parón >6 meses:

1. **NO clasificar como principiante** - La memoria muscular y técnica persisten
2. **Aplicar "Re-acondicionamiento Acelerado":**
   - Semana 1-2: RIR 4-5 (reactivación neuromuscular)
   - Semana 3-4: RIR 3 (ya cerca de su capacidad previa)
   - Mes 2+: RIR 2-3 (capacidad avanzada recuperada)
3. **Volumen inicial:** Comenzar con 60-70% del volumen típico de su nivel (no de principiante)
4. **SEG score:** Penalizar solo -0.5 puntos por parón, NO tratarlo como principiante
5. **Split:** Usar el split apropiado para su experiencia real (no full-body si era avanzado)

**Indicadores de experiencia avanzada previa:**
- "culturista", "competición", "profesional" en historial
- "3+ horas/día", "5-6 días/semana" en tiempo dedicado
- Nivel declarado: "Avanzado" o "Profesional"
- Descripción de rutinas complejas (PPL, Weider, etc.)

**En estos casos:** El parón es temporal, la capacidad técnica y estructural persiste.

### 5️⃣ Banderas clínicas y restricciones

**Lista de ejercicios restringidos según lesión:**

| Zona afectada | Evitar inicialmente | Sustituir por |
|---------------|---------------------|---------------|
| **Lumbar** | Peso muerto convencional, Buenos días, Sentadilla baja sin supervisión | RDL con mancuernas, Hip thrust, Sentadilla copa |
| **Rodilla** | Sentadilla profunda, Pistol squat, Saltos | Sentadilla parcial, Prensa 45°, Step-ups controlados |
| **Hombro** | Press militar pesado, Dominadas lastradas (inicio), Dips fondos | Press con mancuernas, Elevaciones laterales, Remo invertido |
| **Cadera** | Zancadas profundas, Splits búlgaro sin progresión | Hip thrust, Extensiones de cadera en máquina |
| **Muñeca** | Flexiones en suelo (manos planas), Dominadas con agarre cerrado | Flexiones en paralelas, Dominadas agarre neutro |

**Banderas de derivación médica:**
- SEG < 3
- Lesión no diagnosticada con dolor persistente
- Problema cardiovascular sin clearance médico
- Embarazo sin autorización obstétrica

---

## 🔄 MODO SEGUIMIENTO (NUEVO - ANÁLISIS DE PROGRESO)

Si E1 indica que estás en modo seguimiento y proporciona `analisis_progreso`, debes:

### 1️⃣ EVALUAR EFECTIVIDAD DEL PLAN PREVIO

**Recibir de E1:**
```json
"analisis_progreso": {
  "efectividad_plan_previo": "buena | media | baja | mixta",
  "cambios_reportados": {
    "delta_peso_kg": +5,
    "delta_grasa_pct": +3,
    "musculo_delta_kg": +2
  }
}
```

### 2️⃣ ANALIZAR RESULTADOS Y AJUSTAR ESTRATEGIA

**CASO 1: Músculo ↑ + Grasa ↓** (Progreso óptimo)
```
Efectividad: BUENA
Acción: Mantener volumen o aumentar 10%
Recomendación E4: "mantener_estructura"
```

**CASO 2: Músculo ↑ + Grasa ↑** (Progreso mixto)
```
Efectividad: MIXTA
Problema: Exceso calórico
Acción: Mantener volumen entrenamiento
Recomendación adicional: "añadir_cardio_moderado" (2-3x/semana, 20-30 min)
Nota para E3: "Cliente ganó músculo pero también grasa. Sugerir cardio de baja intensidad."
```

**CASO 3: Músculo = + Grasa =** (Estancamiento)
```
Efectividad: BAJA
Problema: Falta estímulo o falta superávit
Acción: Aumentar volumen 15-20%
Recomendación E4: "incrementar_volumen"
Nota: "Cliente estancado. Necesita mayor carga de entrenamiento."
```

**CASO 4: Músculo ↓** (Regresión)
```
Efectividad: BAJA
Problema: Sobreentrenamiento o déficit extremo
Acción: REDUCIR volumen 20-30%
Recomendación E4: "reducir_volumen"
Alerta: "Posible sobreentrenamiento o déficit calórico excesivo. Revisar nutrición y recuperación."
```

### 3️⃣ AJUSTAR SEG Y PARÁMETROS

**Si hubo progreso positivo:**
```
SEG_nuevo = SEG_previo + 0.5  (mejoró capacidad)
RIR_objetivo = RIR_previo - 0.5  (puede tolerar más intensidad)
```

**Si hubo estancamiento:**
```
SEG_nuevo = SEG_previo  (mantener)
Volumen = Volumen_previo × 1.15  (aumentar carga de trabajo)
```

**Si hubo regresión:**
```
SEG_nuevo = SEG_previo - 1  (reducir exigencia)
Volumen = Volumen_previo × 0.75  (descargar)
RIR_objetivo = RIR_previo + 1  (más conservador)
```

### 4️⃣ CAMPO NUEVO EN OUTPUT (solo si seguimiento)

```json
"analisis_progresion": {
  "modo": "seguimiento",
  "evaluacion_plan_previo": {
    "efectividad": "mixta",
    "diagnostico": "Cliente ganó 2kg músculo (positivo) pero también 3% grasa (negativo). Indica exceso calórico.",
    "volumen_previo_series_semana": 48,
    "volumen_actual_recomendado": 48,
    "cambio_volumen_pct": 0,
    "razon_cambio": "Mantener volumen entrenamiento. Problema es nutricional, no de entrenamiento."
  },
  "ajustes_requeridos": {
    "seg_ajuste": 0,
    "rir_ajuste": 0,
    "recomendacion_adicional": "añadir_cardio_moderado",
    "cardio_sugerido": {
      "frecuencia": "2-3x/semana",
      "duracion_min": 20,
      "intensidad": "baja_moderada_60_70_FCmax",
      "objetivo": "Crear déficit calórico adicional sin interferir con ganancia muscular"
    }
  },
  "contrato_para_E3": {
    "estrategia": "mantener_estructura_añadir_cardio",
    "justificacion": "Plan de fuerza está funcionando para hipertrofia. Ajuste necesario es cardiovascular/nutricional."
  }
}
```

---

## 📤 Output (client_context actualizado)

**IMPORTANTE**: Debes devolver el `client_context` COMPLETO que recibiste, con SOLO tu campo lleno.

```json
{
  "client_context": {
    "meta": { ... },  // Mantener igual que input
    "raw_inputs": { ... },  // Mantener igual que input
    "training": {
      "profile": { ... },  // Mantener igual (de E1)
      "constraints": { ... },  // Mantener igual (de E1)
      "prehab": { ... },  // Mantener igual (de E1)
      "progress": null,
      // TU CAMPO - el único que debes llenar:
      "capacity": {
        "seg_score": 7.5,
  "interpretacion_seg": "Cliente con capacidad estructural buena. Progresión estándar con precaución en lumbar.",
  "split_recomendado": {
    "tipo": "upper-lower",
    "frecuencia_semanal": 4,
    "distribucion": ["Upper A", "Lower A", "Upper B", "Lower B"],
    "justificacion": "4 días disponibles, nivel intermedio, permite distribuir volumen sin sobrecargar lumbar."
  },
  "tiempo_sesion": {
    "maximo_minutos": 60,
    "ajustes_aplicados": ["Reducido 10 min por historial de lesión lumbar para incluir movilidad/core"],
    "estructura_recomendada": {
      "calentamiento": 10,
      "trabajo_principal": 40,
      "correctivos_core": 8,
      "enfriamiento": 2
    }
  },
  "rir_objetivo": {
    "semanas_1_2": 5,
    "semanas_3_4": 4,
    "mes_2_en_adelante": 3,
    "notas": "Iniciar conservador para evaluar técnica. RIR 5 = técnica perfecta sin fatiga."
  },
  "banderas_clinicas": [
    {
      "tipo": "lumbar_activa",
      "nivel_alerta": "medio",
      "accion": "Monitorizar dolor post-sesión. Si aumenta, descargar volumen de cadena posterior."
    }
  ],
  "restricciones_ejercicios": [
    {
      "ejercicio": "Peso muerto convencional",
      "razon": "Lesión lumbar activa",
      "sustitucion": "RDL con mancuernas (menos carga axial)"
    },
    {
      "ejercicio": "Buenos días",
      "razon": "Alto riesgo lumbar",
      "sustitucion": "Hip thrust"
    }
  ],
  "ejercicios_obligatorios": [
    {
      "ejercicio": "Plancha frontal",
      "frecuencia": "Cada sesión",
      "razon": "Core preventivo para lumbar"
    },
    {
      "ejercicio": "Bird-dog",
      "frecuencia": "2-3 veces/semana",
      "razon": "Estabilidad lumbopelvica"
    }
  ],
  "contrato_para_E3": {
    "seg_score": 7.5,
    "nivel_conservadurismo": "moderado",
    "parametros_progresion": {
      "velocidad": "estandar_con_precaucion",
      "incremento_carga_pct": 5,
      "incremento_volumen_pct": 10,
      "frecuencia_evaluacion": "semanal"
    },
    "zonas_monitorizacion": ["lumbar"],
        "clearance_medico_requerido": false
      }
    },
    // Mantener resto de campos como estaban:
    "adaptation": null,
    "mesocycle": null,
    "sessions": null,
    "safe_sessions": null,
    "formatted_plan": null,
    "audit": null,
    "bridge_for_nutrition": null
  }
}
}
```

**CRÍTICO**: Devuelve SIEMPRE el objeto completo `client_context`, no solo `capacity`.

---

## ✅ Criterios de éxito

- SEG calculado correctamente con todas las penalizaciones aplicadas
- Split coherente con días, experiencia y limitaciones
- Tiempo ajustado a capacidad real (nunca >90 min)
- RIR conservador pero no excesivo
- Restricciones de ejercicios justificadas clínicamente
- Ejercicios correctivos obligatorios incluidos
- Contrato para E3 con parámetros claros de progresión

---

## ⚠️ Casos especiales

**Si SEG < 4:**
```json
{
  "status": "requiere_supervision",
  "razon": "Riesgo estructural elevado. Derivar a profesional presencial.",
  "recomendacion": "Valoración médica o fisioterápica antes de iniciar programa."
}
```

**Si no hay equipo adecuado:**
Ajustar split a lo posible con equipo disponible, priorizar movimientos funcionales.

---

Procesa el input de E1 y emite el JSON de evaluación de capacidad."""
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Valida que el input contenga client_context con campos necesarios
        
        NUEVO (Fase 2): Validamos client_context
        """
        if "training" not in input_data:
            return False
        
        training = input_data["training"]
        
        # Debe tener campos requeridos
        return (training.get("profile") is not None)
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        """
        Valida que devuelva client_context con capacity lleno
        
        NUEVO (Fase 2): Validamos estructura de salida
        """
        try:
            output = self._extract_json_from_response(raw_output)
            
            if "client_context" not in output:
                raise ValueError("Output no contiene client_context")
            
            client_context = output["client_context"]
            training = client_context.get("training", {})
            
            # Validar que E2 llenó capacity
            if training.get("capacity") is None:
                raise ValueError("E2 no llenó training.capacity")
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error procesando output de E2: {e}")