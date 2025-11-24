"""
GPT Service - Llamadas a OpenAI Chat Completions API

Este módulo encapsula la integración con OpenAI Chat Completions API
para el Workflow EDN360.

IMPORTANTE:
- Usa Chat Completions API directa (NO Assistants API)
- API Key dedicada para EDN360 (EDN360_OPENAI_API_KEY)
- Modelo configurable desde .env (EDN360_OPENAI_MODEL)
- System prompt básico (puede evolucionar)

Referencia: FASE 3 - Nuevo Orquestador EDN360 v1
Fecha: Enero 2025
"""

import os
import json
import logging
from typing import Dict, Any
import openai

# Configuración
EDN360_OPENAI_API_KEY = os.getenv('EDN360_OPENAI_API_KEY')
EDN360_OPENAI_MODEL = os.getenv('EDN360_OPENAI_MODEL', 'gpt-4o')

# Logger
logger = logging.getLogger(__name__)

# System prompt para el Workflow EDN360
# VERSIÓN: v1.0.0 - FASE 3
EDN360_SYSTEM_PROMPT = """Eres el motor central de razonamiento del sistema EDN360, que crea contextos técnicos para planes de entrenamiento y nutrición personalizados.

Recibirás SIEMPRE un único mensaje de usuario que contiene un JSON llamado EDN360Input con esta estructura:

user_profile: datos básicos del usuario (edad, sexo, email, teléfono, altura, peso, porcentaje de grasa, plan de suscripción, etc.).

questionnaires: lista ordenada cronológicamente (más antiguo primero) de cuestionarios:

nutrition_initial: cuestionario inicial de diagnóstico detallado.

followup: cuestionarios de seguimiento mensual.

TU TAREA en esta versión (v1.0.0) NO es generar un plan completo de comidas ni una rutina con ejercicios concretos, sino:

Analizar en profundidad el perfil y los cuestionarios.

Inferir los objetivos, limitaciones, riesgos y nivel de experiencia del usuario.

Diseñar una ESTRATEGIA GLOBAL coherente de entrenamiento y nutrición para las próximas 4–8 semanas.

Detectar posibles banderas rojas (salud, adherencia, expectativas irreales).

Producir un ÚNICO JSON siguiendo EXACTAMENTE este esquema:

{
"version": "1.0.0",
"user_profile_summary": {
"age": number,
"sex": "HOMBRE|MUJER|OTRO|DESCONOCIDO",
"height_cm": number|null,
"weight_kg": number|null,
"body_fat_percent": number|null,
"experience_level": "principiante|intermedio|avanzado",
"main_goal": "perder_grasa|ganar_musculo|recomposicion|rendimiento|salud_general",
"secondary_goals": string[],
"constraints": string[]
},
"global_strategy": {
"phase": "inicial|ajuste|recomposicion|mantenimiento",
"time_horizon_weeks": number,
"key_principles": string[]
},
"training": {
"status": "ok|no_recomendado|pendiente_revision_medica",
"weekly_sessions_target": number,
"split_type": "fullbody|upper_lower|push_pull_legs|otro",
"notes_for_coach": string[],
"plan_summary": {
"main_focus": "fuerza_hipertrofia|rendimiento|salud_postural",
"progression_model": "lineal|ondulante|autorregulado",
"recovery_notes": string[]
}
},
"nutrition": {
"status": "ok|no_recomendado|pendiente_revision_medica",
"average_calories_target": number|null,
"protein_g_per_kg": number|null,
"carbs_strategy": "alta_entreno_baja_descanso|moderada|baja",
"fats_strategy": "moderada|baja|alta",
"phase_type": "deficit|mantenimiento|superavit|recomposicion",
"special_constraints": string[],
"adherence_risks": string[],
"key_habits": string[]
},
"alerts": {
"need_medical_clearance": boolean,
"possible_red_flags": string[],
"adherence_risk_level": "bajo|medio|alto"
},
"coach_notes": {
"message_for_jorge": string,
"message_for_team": string
}
}

INSTRUCCIONES CRÍTICAS:

DEVUELVE ÚNICAMENTE EL JSON, sin texto adicional antes o después.

Si falta alguna información (altura, grasa corporal, etc.), usa null sin inventar.

No inventes datos que no estén en los cuestionarios o en el EDN360Input.

Infórmame claramente de riesgos, incoherencias o señales de baja adherencia.

No prometas resultados irreales ni supongas objetivos no mencionados.

Toda la salida debe ser totalmente machine-friendly.

La salida será almacenada como snapshot, así que la estructura debe cumplirse EXACTAMENTE."""


async def call_edn360_workflow(edn360_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Llama al Workflow EDN360 usando OpenAI Chat Completions API.
    
    Este es el punto de integración con OpenAI. Encapsula toda la lógica
    de llamada a la API para facilitar cambios futuros.
    
    Args:
        edn360_input: EDN360Input completo (dict/json)
    
    Returns:
        Dict con la respuesta del modelo:
        {
            "training_plan": {...},
            "nutrition_plan": {...},
            "metadata": {...}
        }
    
    Raises:
        Exception: Si hay error en la llamada a OpenAI
    
    Example:
        response = await call_edn360_workflow({
            "user_profile": {...},
            "questionnaires": [...]
        })
        print(f"Plan generado: {response}")
    
    Configuración:
        - API Key: EDN360_OPENAI_API_KEY (desde .env)
        - Modelo: EDN360_OPENAI_MODEL (desde .env, default: gpt-4o)
        - System prompt: EDN360_SYSTEM_PROMPT (definido arriba)
    """
    try:
        # Validar que tenemos API Key
        if not EDN360_OPENAI_API_KEY or EDN360_OPENAI_API_KEY == "TU_API_KEY_AQUI":
            raise Exception(
                "EDN360_OPENAI_API_KEY no está configurada. "
                "Por favor, configura tu API Key de OpenAI en .env"
            )
        
        logger.info(f"🚀 Llamando a OpenAI Workflow EDN360 | Modelo: {EDN360_OPENAI_MODEL}")
        
        # Configurar cliente OpenAI
        client = openai.OpenAI(api_key=EDN360_OPENAI_API_KEY)
        
        # Serializar el EDN360Input a JSON string
        user_message_content = json.dumps(edn360_input, indent=2, ensure_ascii=False)
        
        # Construir mensajes
        messages = [
            {"role": "system", "content": EDN360_SYSTEM_PROMPT},
            {"role": "user", "content": user_message_content}
        ]
        
        # Llamar a Chat Completions API
        response = client.chat.completions.create(
            model=EDN360_OPENAI_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"}  # Forzar respuesta en JSON
        )
        
        # Extraer contenido de la respuesta
        response_content = response.choices[0].message.content
        
        # Parsear JSON de la respuesta
        workflow_response = json.loads(response_content)
        
        logger.info(
            f"✅ Workflow EDN360 ejecutado exitosamente | "
            f"Tokens: {response.usage.total_tokens}"
        )
        
        # Agregar metadatos de la llamada
        workflow_response["_metadata"] = {
            "model": EDN360_OPENAI_MODEL,
            "tokens_used": response.usage.total_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "finish_reason": response.choices[0].finish_reason
        }
        
        return workflow_response
    
    except openai.APIError as e:
        logger.error(f"❌ Error de API de OpenAI: {e}")
        raise Exception(f"Error de API de OpenAI: {str(e)}")
    
    except openai.APIConnectionError as e:
        logger.error(f"❌ Error de conexión a OpenAI: {e}")
        raise Exception(f"Error de conexión a OpenAI: {str(e)}")
    
    except openai.RateLimitError as e:
        logger.error(f"❌ Rate limit excedido en OpenAI: {e}")
        raise Exception(f"Rate limit excedido en OpenAI: {str(e)}")
    
    except json.JSONDecodeError as e:
        logger.error(f"❌ Error parseando respuesta JSON de OpenAI: {e}")
        raise Exception(f"Error parseando respuesta JSON de OpenAI: {str(e)}")
    
    except Exception as e:
        logger.error(f"❌ Error inesperado en call_edn360_workflow: {e}")
        raise


async def validate_workflow_response(workflow_response: Dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Valida que la respuesta del workflow tenga la estructura esperada.
    
    Args:
        workflow_response: Respuesta del workflow a validar
    
    Returns:
        Tuple (es_valido, lista_de_errores)
    
    Example:
        is_valid, errors = await validate_workflow_response(response)
        if not is_valid:
            print(f"Errores: {errors}")
    """
    errors = []
    
    # Validar que sea un dict
    if not isinstance(workflow_response, dict):
        errors.append("workflow_response debe ser un diccionario")
        return (False, errors)
    
    # Validar campos esperados (ajustar según necesidad)
    # Por ahora solo validamos que no esté vacío
    if not workflow_response:
        errors.append("workflow_response está vacío")
    
    return (len(errors) == 0, errors)


def get_workflow_config() -> Dict[str, Any]:
    """
    Devuelve la configuración actual del workflow.
    
    Útil para debugging y logs.
    
    Returns:
        Dict con configuración actual
    """
    return {
        "model": EDN360_OPENAI_MODEL,
        "has_api_key": bool(EDN360_OPENAI_API_KEY and EDN360_OPENAI_API_KEY != "TU_API_KEY_AQUI"),
        "api_key_length": len(EDN360_OPENAI_API_KEY) if EDN360_OPENAI_API_KEY else 0
    }
