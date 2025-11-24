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
# Este prompt puede evolucionar en fases futuras
EDN360_SYSTEM_PROMPT = """Eres un asistente experto en análisis de datos de salud, entrenamiento y nutrición.

Recibirás un JSON con información de un usuario y sus cuestionarios de salud.

Tu tarea es generar un plan completo y personalizado de entrenamiento y nutrición basado en:
- El perfil del usuario
- Sus cuestionarios iniciales y de seguimiento
- Sus objetivos y necesidades específicas

Devuelve un JSON estructurado con:
- training_plan: Plan de entrenamiento completo
- nutrition_plan: Plan de nutrición completo

Asegúrate de que los planes sean:
- Personalizados al usuario
- Basados en evidencia científica
- Prácticos y ejecutables
- Seguros y saludables"""


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
