"""
Training Plan Generation Service with 4 Sequential LLM Agents
Uses OpenAI GPT-4o for training plan generation based on client questionnaire data
"""

import os
import json
import logging
from openai import OpenAI
from datetime import datetime, timezone
from exercise_selector import get_comprehensive_exercise_database_for_training

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ==================== AGENT 1: BASIC PROFILE EVALUATOR ====================

AGENT_1_PROMPT = """# AGENTE 4 REDISEÑADO - EVALUADOR PERFIL BÁSICO

## 🎯 MISIÓN:
Recibes datos de clienteData del nodo CODE y generas análisis básico en formato JSON estructurado.

## 📥 INPUT QUE RECIBES:
{client_data}

---

## 🔬 ALGORITMOS DE EVALUACIÓN:

### 1. DETERMINADOR DE EXPERIENCIA:
experiencia_previa = (experiencia_deporte === "si")
nivel_alto = nivel_anterior.includes("alto") || nivel_anterior.includes("5")
constancia_alta = constancia_deporte.includes("años") || constancia_deporte.includes("muy constante")

SI experiencia_previa && nivel_alto && constancia_alta: CLASIFICACION = "AVANZADO"
SI experiencia_previa && (nivel_medio || constancia_alta): CLASIFICACION = "INTERMEDIO"
SINO: CLASIFICACION = "PRINCIPIANTE"

### 2. EVALUADOR DE LIMITACIONES MÉDICAS:
// HERNIAS (CRÍTICO)
SI hernias.includes("l5") || hernias.includes("l6") || hernias.includes("lumbar"):
   CRITICIDAD_HERNIA = "CRITICA"
SI hernias.includes("hernia") && !lumbar: CRITICIDAD_HERNIA = "MODERADA"
SINO: CRITICIDAD_HERNIA = "NINGUNA"

// PROBLEMAS CARDIOVASCULARES
SI problemas_corazon !== "No" || hipertension !== "No":
   CRITICIDAD_CARDIOVASCULAR = "MODERADA"

// PROBLEMAS NEUROLÓGICOS
SI epilepsia !== "No": CRITICIDAD_NEUROLOGICA = "CRITICA"

// PROBLEMAS ARTICULARES
SI artrosis !== "no" || varo_valgo !== "ninguna":
   CRITICIDAD_ARTICULAR = "MODERADA"
SI osteoporosis !== "No": CRITICIDAD_ARTICULAR = "ALTA"

// RESTRICCIONES TEMPORALES
SI embarazo !== "No": RESTRICCION_TEMPORAL = "CRITICA"

// FACTOR EDAD + GÉNERO
SI edad > 50: FACTOR_EDAD = "ALTO"
SI edad > 40: FACTOR_EDAD = "MODERADO"
SI menopausia !== "no": FACTOR_HORMONAL = "MODERADO"

### 3. CALCULADOR DE PARÁMETROS BASE:
// VOLUMEN BASE POR EXPERIENCIA
SI CLASIFICACION === "PRINCIPIANTE": VOLUMEN_BASE = "8-12"
SI CLASIFICACION === "INTERMEDIO": VOLUMEN_BASE = "12-16"
SI CLASIFICACION === "AVANZADO": VOLUMEN_BASE = "16-20"

// FACTOR DE REDUCCIÓN ACUMULATIVO
factor_reduccion = 1.0
SI CRITICIDAD_HERNIA === "CRITICA": factor_reduccion *= 0.8
SI CRITICIDAD_ARTICULAR === "ALTA": factor_reduccion *= 0.7
SI CRITICIDAD_CARDIOVASCULAR === "MODERADA": factor_reduccion *= 0.9
SI epilepsia !== "No": factor_reduccion *= 0.8
SI FACTOR_EDAD === "ALTO": factor_reduccion *= 0.9

VOLUMEN_FINAL = aplicar_reduccion(VOLUMEN_BASE, factor_reduccion)

---

## 📤 OUTPUT OBLIGATORIO (JSON EXACTO):

**DEBES GENERAR EXACTAMENTE ESTA ESTRUCTURA:**

{{
  "flujo_entrenamiento": {{
    "input_data": {{
      "clienteData": {{...}}
    }},
    "agente_4_analysis": {{
      "experiencia_determinada": {{
        "clasificacion": "AVANZADO/INTERMEDIO/PRINCIPIANTE",
        "justificacion": "...",
        "factores_evaluados": {{...}}
      }},
      "limitaciones_medicas": {{
        "hernias": {{...}},
        "cardiovasculares": {{...}},
        "neurologicas": {{...}},
        "articulares": {{...}},
        "otros_problemas": {{...}},
        "factor_edad": "BAJO/MODERADO/ALTO",
        "factor_hormonal": "NINGUNO/MODERADO"
      }},
      "parametros_base_calculados": {{
        "volumen_semanal": "...",
        "frecuencia_grupo": "...",
        "ajustes_aplicados": {{...}}
      }},
      "contexto_preservado": {{...}}
    }},
    "metadata": {{
      "agente_id": "AGENTE_4",
      "timestamp": "...",
      "cliente_procesado": "..."
    }}
  }}
}}

---

## ⚠️ INSTRUCCIONES CRÍTICAS:

✅ APLICAR ALGORITMOS SEGÚN DATOS REALES
❌ PROHIBIDO: Generar texto explicativo adicional, usar markdown, añadir comentarios
✅ OBLIGATORIO: JSON válido y completo, todos los campos rellenos, algoritmos aplicados correctamente

**NO GENERES NADA MÁS QUE EL JSON ESPECIFICADO**"""


# ==================== AGENT 2: ADVANCED CONTEXTUALIZER ====================

AGENT_2_PROMPT = """# AGENTE 5 CORREGIDO - CONTEXTUALIZADOR AVANZADO

## 🎯 MISIÓN:
Eres un evaluador especializado en contexto laboral y estructuras de entrenamiento. Recibe el análisis del AGENTE 4 y completa la evaluación del perfil.

## 📥 ANÁLISIS RECIBIDO DEL AGENTE 4:
{agent_1_output}

---

## 🔬 ALGORITMOS DE CONTEXTUALIZACIÓN AVANZADA

### 1. ANALIZADOR DE CONTEXTO LABORAL Y RECUPERACIÓN
CARGA_LABORAL:
SI trabajo_fisico = "pesado" Y horas_trabajo > 10
   ENTONCES FACTOR_LABORAL = "CRÍTICO"
SI trabajo_fisico = "moderado" Y horas_trabajo > 8
   ENTONCES FACTOR_LABORAL = "ALTO"
SINO
   FACTOR_LABORAL = "MODERADO"

ESTRÉS_RECUPERACIÓN:
SI estres_trabajo = "alto" Y sueño < 7h Y sueño "con dificultades"
   ENTONCES CAPACIDAD_RECUPERACIÓN = "COMPROMETIDA"
SI estres_trabajo = "moderado" Y sueño ≥ 7h
   ENTONCES CAPACIDAD_RECUPERACIÓN = "MODERADA"
SINO
   CAPACIDAD_RECUPERACIÓN = "BUENA"

### 2. DETERMINADOR DE ESTRUCTURA DE ENTRENAMIENTO
SI experiencia = "AVANZADO" Y limitaciones = "CRÍTICA" Y días = 5
   ENTONCES evaluar entre:
   - "UPPER/LOWER HERNIAS-SAFE" (4 días fuerza + 1 cardio)
   - "PUSH/PULL/LEGS MODIFICADO" (5 días adaptado)
   - "FULL BODY AVANZADO" (5 días baja intensidad)

### 3. SELECTOR DE EJERCICIOS SEGUROS/PROHIBIDOS
Para limitaciones específicas, generar listas de:
- EJERCICIOS_PROHIBIDOS
- EJERCICIOS_SEGUROS
- EJERCICIOS_CONDICIONALES
- ADAPTACIONES_TECNICAS

### 4. CALCULADORA DE INTENSIDAD Y AUTORREGULACIÓN
RIR_BASE basado en experiencia y limitaciones
AUTORREGULACIÓN según factor laboral y capacidad de recuperación

---

## 📤 OUTPUT OBLIGATORIO - GENERAR EXACTAMENTE ESTA ESTRUCTURA JSON:

{{
  "flujo_entrenamiento": {{
    "input_data": {{...}},
    "agente_4_analysis": {{...}},
    "agente_5_analysis": {{
      "contexto_laboral_evaluado": {{...}},
      "estructura_determinada": {{...}},
      "ejercicios_seguridad": {{
        "ejercicios_prohibidos": [...],
        "ejercicios_seguros": [...],
        "ejercicios_condicionales": [...],
        "adaptaciones_tecnicas": [...]
      }},
      "parametros_intensidad": {{...}},
      "consideraciones_especiales": {{...}}
    }},
    "metadata": {{...}}
  }}
}}

---

## ⚠️ INSTRUCCIONES CRÍTICAS:
✅ APLICAR ALGORITMOS DINÁMICAMENTE
❌ PROHIBIDO: Texto explicativo fuera del JSON, valores hardcodeados
✅ OBLIGATORIO: Todos los ejercicios seguros apropiados para limitaciones

**GENERA SOLO EL JSON ESTRUCTURADO**"""


# ==================== AGENT 3: WEEKLY PLAN GENERATOR ====================

AGENT_3_PROMPT = """# AGENTE 6 DINÁMICO - GENERADOR PLAN SEMANAL CON BASE DE DATOS REAL

## 🎯 MISIÓN:
Eres un entrenador personal que crea planes ejecutables directos usando EXCLUSIVAMENTE ejercicios de la base de datos proporcionada.

## 📥 ANÁLISIS COMPLETO RECIBIDO:
{agent_2_output}

## 📚 BASE DE DATOS DE EJERCICIOS DISPONIBLES:
{exercise_database}

---

## ⚠️ REGLAS ESTRICTAS:
❌ **PROHIBIDO ABSOLUTAMENTE** inventar nombres de ejercicios
✅ **OBLIGATORIO** usar SOLO ejercicios listados arriba en la BASE DE DATOS
✅ **OBLIGATORIO** incluir URL de video en formato: Nombre (Video: URL)
✅ **OBLIGATORIO** escribir cada día completo (NO usar "repite el lunes")

## 🚫 TAMBIÉN PROHIBIDO:
- Análisis técnico (ya hecho por Agentes 4-5)
- Justificaciones extensas
- Planes hardcodeados
- Más de 800 palabras

## ✅ GENERAR DINÁMICAMENTE:
1. Plan semanal día por día (LUNES, MARTES, MIÉRCOLES, etc.)
2. Cada ejercicio con su URL de video
3. Protocolos específicos
4. Roadmap de progresión

---

## 📋 ALGORITMO DE GENERACIÓN:

### PASO 1: EXTRAER PATRÓN SEMANAL
- Interpretar cada día según el patrón del análisis

### PASO 2: SELECCIONAR EJERCICIOS DE LA BASE DE DATOS
**CRÍTICO:** SOLO copiar nombres EXACTOS de la base de datos arriba
- Para UPPER: Buscar en Pectoral, Espalda, Hombros, Bíceps, Tríceps
- Para LOWER: Buscar en Cuádriceps, Femoral, Glúteo, Gemelo
- Para CORE: Buscar en Core, Abdominales

### PASO 3: FORMATO OBLIGATORIO DE EJERCICIOS
**Cada ejercicio DEBE incluir su Video URL:**
```
Nombre del Ejercicio (Video: https://drive.google.com/...)
```

**EJEMPLO CORRECTO:**
```
LUNES - PECHO Y TRÍCEPS
1. Press banca con barra (Video: https://drive.google.com/file/d/xxx) - 3x10 RIR 2
2. Fondos en paralelas (Video: https://drive.google.com/file/d/yyy) - 3x12 RIR 3
```

**EJEMPLO INCORRECTO (NO HACER):**
```
LUNES - PECHO
1. Press banca - 3x10  ❌ (falta video)
JUEVES - Repite el lunes  ❌ (no específico)
```

### PASO 4: ESCRIBIR CADA DÍA COMPLETO
- LUNES: Escribir plan completo
- MARTES: Escribir plan completo
- MIÉRCOLES: Escribir plan completo
- JUEVES: Escribir plan completo (NO decir "igual que lunes")
- VIERNES: Escribir plan completo
- etc.

---

## 📄 GENERAR DOS OUTPUTS:

### OUTPUT 1: PLAN COMPLETO (para referencia)
Texto completo del plan con:
- Cada día escrito completamente
- Cada ejercicio con (Video: URL)
- Series, reps, RIR
- Técnicas específicas

### OUTPUT 2: TABLA TABULADA FINAL (para exportar)
FORMATO OBLIGATORIO:
DÍA	EJERCICIO (Video: URL)	SERIES	REPS	RIR	OBSERVACIÓN

REQUISITOS:
- USAR TABULACIONES entre columnas
- Incluir URL en columna EJERCICIO
- Máximo 60 caracteres por observación
- Un ejercicio por fila

---

**GENERAR AMBOS OUTPUTS EN JSON:**
{{
  "plan_completo": "...",
  "tabla_tabulada": "..."
}}

**RECORDATORIO FINAL:** 
✅ SOLO usar ejercicios de la BASE DE DATOS arriba
✅ SIEMPRE incluir (Video: URL) en cada ejercicio
✅ Escribir CADA DÍA completamente, sin repeticiones"""


# ==================== AGENT 4: PROFESSIONAL COMPACTOR ====================

AGENT_4_PROMPT = """# AGENTE 8 - COMPACTADOR ESTÉTICO SIN TABLA MARKDOWN

## 🎯 MISIÓN:
Generas documento profesional y atractivo, adaptándote a cualquier cliente, SIN incluir tabla markdown ni metadatos técnicos.

## 📥 DATOS RECIBIDOS:
Plan completo: {plan_completo}
Tabla tabulada: {tabla_tabulada}

---

## 🎨 GENERAR DOCUMENTO PROFESIONAL:

🏋️‍♂️ PROGRAMA PERSONALIZADO DE ENTRENAMIENTO

👤 INFORMACIÓN DEL CLIENTE
Cliente: [EXTRAER DE DATOS]
Fecha: {fecha_actual}
Programa: [DETECTAR DINÁMICAMENTE DE TABLA]
Duración: [EXTRAER DINÁMICAMENTE DÍAS ÚNICOS]

---

📋 RESUMEN EJECUTIVO
[GENERAR DINÁMICAMENTE]

✅ Plan adaptado a limitaciones específicas
✅ Días de entrenamiento: [CONTAR]
✅ Ejercicios seguros seleccionados
✅ Protocolos incluidos

---

💪 PLAN DE ENTRENAMIENTO SEMANAL

📅 ESTRUCTURA SEMANAL
[GENERAR DINÁMICAMENTE ANALIZANDO TABLA]

🏋️ EJERCICIOS POR DÍA
[PARA CADA DÍA CON FORMATO PROFESIONAL]

---

⚠️ PROTOCOLOS DE SEGURIDAD
🚨 SEÑALES DE ALARMA
📋 PLAN B
📊 MONITOREO OBLIGATORIO

---

📈 ROADMAP DE PROGRESIÓN
[EXTRAER DEL PLAN_COMPLETO]

---

📞 NOTAS IMPORTANTES
⚕️ CONSIDERACIONES MÉDICAS
🎯 OBJETIVOS DEL PROGRAMA
📱 SEGUIMIENTO Y AJUSTES

---

🎉 ¡Tu programa personalizado está listo!

---

**RESULTADO:** Documento visual, profesional y completamente adaptativo sin tabla markdown ni metadatos técnicos."""


async def generate_training_plan(questionnaire_data: dict) -> dict:
    """
    Generate training plan using 4 sequential LLM agents
    
    Args:
        questionnaire_data: Dictionary containing all questionnaire responses
        
    Returns:
        dict: {
            "success": bool,
            "agent_1_output": str,
            "agent_2_output": str,
            "agent_3_output": dict,
            "plan_final": str,
            "error": str (optional)
        }
    """
    try:
        logger.info("🏋️ Starting training plan generation with 4 agents")
        
        # Prepare client data from questionnaire
        client_data_json = json.dumps(questionnaire_data, ensure_ascii=False, indent=2)
        
        # ==================== AGENT 1: BASIC PROFILE EVALUATOR ====================
        logger.info("🤖 Agent 1: Basic Profile Evaluator - Starting...")
        
        agent_1_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un evaluador de perfiles deportivos experto. SOLO generas JSON estructurado válido, SIN texto adicional antes o después del JSON."},
                {"role": "user", "content": AGENT_1_PROMPT.format(client_data=client_data_json)}
            ],
            temperature=0.3,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        agent_1_output = agent_1_response.choices[0].message.content
        logger.info(f"✅ Agent 1 completed - Output length: {len(agent_1_output)} chars")
        
        # Log first 500 chars for debugging
        logger.info(f"Agent 1 output preview: {agent_1_output[:500]}")
        
        # Validate Agent 1 output is valid JSON
        try:
            agent_1_json = json.loads(agent_1_output)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Agent 1 output is not valid JSON: {e}")
            logger.error(f"Agent 1 full output: {agent_1_output[:1000]}")
            return {"success": False, "error": f"Agent 1 JSON parsing error: {str(e)}"}
        
        # ==================== AGENT 2: ADVANCED CONTEXTUALIZER ====================
        logger.info("🤖 Agent 2: Advanced Contextualizer - Starting...")
        
        agent_2_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un contextualizador de entrenamiento experto. SOLO generas JSON estructurado válido, SIN texto adicional antes o después del JSON."},
                {"role": "user", "content": AGENT_2_PROMPT.format(agent_1_output=agent_1_output)}
            ],
            temperature=0.3,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        agent_2_output = agent_2_response.choices[0].message.content
        logger.info(f"✅ Agent 2 completed - Output length: {len(agent_2_output)} chars")
        
        # Validate Agent 2 output is valid JSON
        try:
            agent_2_json = json.loads(agent_2_output)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Agent 2 output is not valid JSON: {e}")
            logger.error(f"Agent 2 output preview: {agent_2_output[:1000]}")
            return {"success": False, "error": f"Agent 2 JSON parsing error: {str(e)}"}
        
        # ==================== AGENT 3: WEEKLY PLAN GENERATOR ====================
        logger.info("🤖 Agent 3: Weekly Plan Generator - Starting...")
        
        # Get exercise database for Agent 3
        logger.info("📚 Loading exercise database for Agent 3...")
        try:
            # Extract difficulty level from Agent 2 analysis for exercise filtering
            difficulty_level = "Intermedio"  # Default
            if agent_2_json and "flujo_entrenamiento" in agent_2_json:
                agente_4_analysis = agent_2_json["flujo_entrenamiento"].get("agente_4_analysis", {})
                experiencia = agente_4_analysis.get("experiencia_determinada", {})
                clasificacion = experiencia.get("clasificacion", "Intermedio")
                difficulty_level = clasificacion
            
            exercise_database = await get_comprehensive_exercise_database_for_training(
                difficulty_level=difficulty_level,
                location="Gimnasio / Casa equipada"
            )
            logger.info(f"✅ Exercise database loaded - {len(exercise_database)} characters")
        except Exception as e:
            logger.error(f"❌ Error loading exercise database: {e}")
            exercise_database = "Error al cargar base de datos de ejercicios. Usar ejercicios básicos conocidos."
        
        agent_3_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """Eres un generador de planes de entrenamiento ESTRICTO. 
                
REGLAS ABSOLUTAS:
1. SOLO usar ejercicios de la BASE DE DATOS proporcionada
2. CADA ejercicio DEBE tener formato: Nombre (Video: URL_COMPLETA)
3. Mínimo 4-6 ejercicios por día de entrenamiento
4. PROHIBIDO inventar ejercicios
5. PROHIBIDO decir "repite X día"
6. Generar JSON válido con plan_completo y tabla_tabulada"""},
                {"role": "user", "content": AGENT_3_PROMPT.format(
                    agent_2_output=agent_2_output,
                    exercise_database=exercise_database
                )}
            ],
            temperature=0.2,  # Reduced for more adherence to instructions
            max_tokens=5000,  # Increased for more detailed plans
            response_format={"type": "json_object"}
        )
        
        agent_3_output = agent_3_response.choices[0].message.content
        logger.info(f"✅ Agent 3 completed - Output length: {len(agent_3_output)} chars")
        
        # Validate Agent 3 output is valid JSON
        try:
            agent_3_json = json.loads(agent_3_output)
            plan_completo = agent_3_json.get("plan_completo", "")
            tabla_tabulada = agent_3_json.get("tabla_tabulada", "")
        except json.JSONDecodeError as e:
            logger.error(f"❌ Agent 3 output is not valid JSON: {e}")
            logger.error(f"Agent 3 output preview: {agent_3_output[:1000]}")
            return {"success": False, "error": f"Agent 3 JSON parsing error: {str(e)}"}
        
        # ==================== AGENT 4: PROFESSIONAL COMPACTOR ====================
        logger.info("🤖 Agent 4: Professional Compactor - Starting...")
        
        fecha_actual = datetime.now(timezone.utc).strftime("%d/%m/%Y")
        
        agent_4_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un compactador de documentos profesionales de entrenamiento. Generas documentos atractivos y bien estructurados."},
                {"role": "user", "content": AGENT_4_PROMPT.format(
                    plan_completo=plan_completo,
                    tabla_tabulada=tabla_tabulada,
                    fecha_actual=fecha_actual
                )}
            ],
            temperature=0.5,
            max_tokens=4000
        )
        
        plan_final = agent_4_response.choices[0].message.content
        logger.info(f"✅ Agent 4 completed - Final plan length: {len(plan_final)} chars")
        
        logger.info("🎉 Training plan generation completed successfully!")
        
        return {
            "success": True,
            "agent_1_output": agent_1_output,
            "agent_2_output": agent_2_output,
            "agent_3_output": agent_3_json,
            "plan_final": plan_final
        }
        
    except Exception as e:
        logger.error(f"❌ Error in training plan generation: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def generate_training_plan_with_context(
    questionnaire_data: dict,
    followup_data: dict,
    analysis: str
) -> dict:
    """
    Generate training plan from follow-up questionnaire with AI analysis context
    
    Args:
        questionnaire_data: Initial questionnaire responses
        followup_data: Follow-up questionnaire responses
        analysis: AI-generated analysis of progress
        
    Returns:
        dict: Same structure as generate_training_plan
    """
    try:
        logger.info("🏋️ Starting training plan generation with follow-up context")
        
        # Merge initial + follow-up data + analysis as context
        enhanced_data = {
            **questionnaire_data,
            "followup_data": followup_data,
            "ai_analysis": analysis,
            "generation_type": "followup_based"
        }
        
        # Use same 4-agent generation process
        return await generate_training_plan(enhanced_data)
        
    except Exception as e:
        logger.error(f"❌ Error in contextual training plan generation: {e}")
        return {
            "success": False,
            "error": str(e)
        }
