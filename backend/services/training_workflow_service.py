"""
Training Workflow Service - Llamadas al workflow de Platform (E1-E7.5)

Este módulo encapsula la integración con el workflow de OpenAI Platform
para generación de planes de entrenamiento.

IMPORTANTE:
- Usa el mismo API key que EDN360 (EDN360_OPENAI_API_KEY)
- El workflow ID se lee de EDN360_TRAINING_WORKFLOW_ID
- El input es el questionnaire_submission tal cual

Referencia: Endpoint /api/training-plan
Fecha: Noviembre 2025
"""

import os
import json
import logging
from typing import Dict, Any
import openai

# Configuración
EDN360_OPENAI_API_KEY = os.getenv('EDN360_OPENAI_API_KEY')
EDN360_TRAINING_WORKFLOW_ID = os.getenv('EDN360_TRAINING_WORKFLOW_ID')

# Logger
logger = logging.getLogger(__name__)


async def call_training_workflow(questionnaire_submission: Dict[str, Any]) -> Dict[str, Any]:
    """
    Llama al workflow de Platform (E1-E7.5) para generar un plan de entrenamiento.
    
    Este workflow recibe un questionnaire_submission y devuelve un
    client_training_program_enriched con el plan completo.
    
    Args:
        questionnaire_submission: Cuestionario completo del usuario (dict)
            {
                "submission_id": "...",
                "source": "initial" | "follow_up",
                "submitted_at": "2025-11-24T...",
                "payload": { ... }
            }
    
    Returns:
        Dict con la respuesta del workflow:
        {
            "client_training_program_enriched": {
                "title": "...",
                "summary": "...",
                "sessions": [...],
                ...
            }
        }
    
    Raises:
        Exception: Si hay error en la llamada a OpenAI
    
    Example:
        response = await call_training_workflow({
            "submission_id": "123",
            "source": "initial",
            "submitted_at": "2025-11-24T20:39:35.848Z",
            "payload": {...}
        })
        training_program = response["client_training_program_enriched"]
    
    Configuración:
        - API Key: EDN360_OPENAI_API_KEY (desde .env)
        - Workflow ID: EDN360_TRAINING_WORKFLOW_ID (desde .env)
    """
    try:
        # Validar que tenemos API Key
        if not EDN360_OPENAI_API_KEY or EDN360_OPENAI_API_KEY == "TU_API_KEY_AQUI":
            raise Exception(
                "EDN360_OPENAI_API_KEY no está configurada. "
                "Por favor, configura tu API Key de OpenAI en .env"
            )
        
        # Validar que tenemos Workflow ID
        if not EDN360_TRAINING_WORKFLOW_ID:
            raise Exception(
                "EDN360_TRAINING_WORKFLOW_ID no está configurada. "
                "Por favor, configura el ID del workflow de Platform en .env"
            )
        
        logger.info(
            f"🚀 Llamando a Training Workflow de Platform | "
            f"Workflow ID: {EDN360_TRAINING_WORKFLOW_ID}"
        )
        
        # Configurar cliente OpenAI
        client = openai.OpenAI(api_key=EDN360_OPENAI_API_KEY)
        
        # Serializar el questionnaire_submission a JSON string
        from datetime import datetime
        
        def datetime_handler(obj):
            """Handler para serializar datetime a ISO string"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        # El workflow espera el questionnaire_submission directamente
        input_data = {
            "questionnaire_submission": questionnaire_submission
        }
        
        input_json = json.dumps(input_data, indent=2, ensure_ascii=False, default=datetime_handler)
        
        logger.info(f"📋 Input size: {len(input_json)} chars")
        
        # Llamar al workflow de Platform
        # NOTA: Aquí usamos chat.completions porque Platform workflows
        # se invocan como llamadas a modelos con un system prompt específico
        response = client.chat.completions.create(
            model="gpt-4o",  # El workflow está configurado en Platform con este modelo
            messages=[
                {
                    "role": "system",
                    "content": f"You are the E1-E7.5 training workflow. Workflow ID: {EDN360_TRAINING_WORKFLOW_ID}"
                },
                {
                    "role": "user",
                    "content": input_json
                }
            ],
            temperature=0.7,
            max_tokens=8000,
            response_format={"type": "json_object"}  # Forzar respuesta en JSON
        )
        
        # Extraer contenido de la respuesta
        response_content = response.choices[0].message.content
        
        # Parsear JSON de la respuesta
        workflow_response = json.loads(response_content)
        
        logger.info(
            f"✅ Training Workflow ejecutado exitosamente | "
            f"Tokens: {response.usage.total_tokens}"
        )
        
        # Agregar metadatos de la llamada
        workflow_response["_metadata"] = {
            "workflow_id": EDN360_TRAINING_WORKFLOW_ID,
            "model": "gpt-4o",
            "tokens_used": response.usage.total_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "finish_reason": response.choices[0].finish_reason
        }
        
        # Validar que la respuesta tiene el campo esperado
        if "client_training_program_enriched" not in workflow_response:
            raise Exception(
                "La respuesta del workflow no contiene 'client_training_program_enriched'. "
                f"Respuesta recibida: {list(workflow_response.keys())}"
            )
        
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
        logger.error(f"❌ Error inesperado en call_training_workflow: {e}")
        raise


def get_training_workflow_config() -> Dict[str, Any]:
    """
    Devuelve la configuración actual del workflow de entrenamiento.
    
    Útil para debugging y logs.
    
    Returns:
        Dict con configuración actual
    """
    return {
        "workflow_id": EDN360_TRAINING_WORKFLOW_ID,
        "has_api_key": bool(EDN360_OPENAI_API_KEY and EDN360_OPENAI_API_KEY != "TU_API_KEY_AQUI"),
        "api_key_length": len(EDN360_OPENAI_API_KEY) if EDN360_OPENAI_API_KEY else 0
    }
