"""
Training Workflow Service - Integración con OpenAI Assistants API (E1-E7.5)

Este servicio implementa la llamada al workflow de entrenamiento EDN360
usando la API de Assistants de OpenAI.

Contrato:
- INPUT: EDN360Input (user_profile + questionnaires + context)
- OUTPUT: client_training_program_enriched

Referencia: POST /api/training-plan
Fecha: Noviembre 2025
"""

import os
import json
import logging
from typing import Dict, Any
from openai import OpenAI
from datetime import datetime

# Configuración
EDN360_OPENAI_API_KEY = os.getenv('EDN360_OPENAI_API_KEY')
EDN360_TRAINING_WORKFLOW_ID = os.getenv('EDN360_TRAINING_WORKFLOW_ID')

# Logger
logger = logging.getLogger(__name__)


async def call_training_workflow(edn360_input: Dict[str, Any]) -> Dict[str, Any]:
    """
    Llama al workflow de entrenamiento EDN360 (E1-E7.5) usando Assistants API.
    
    Este workflow:
    1. Recibe el EDN360Input completo (user_profile + questionnaires + context)
    2. Ejecuta los agentes E1-E7.5 con acceso a la BD de ejercicios
    3. Devuelve client_training_program_enriched
    
    Args:
        edn360_input: Objeto EDN360Input completo:
            {
                "user_profile": {...},
                "questionnaires": [...],
                "context": {...}
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
        Exception: Si hay error en la ejecución del workflow
    
    Configuración:
        - API Key: EDN360_OPENAI_API_KEY
        - Assistant ID: EDN360_TRAINING_WORKFLOW_ID
    """
    try:
        # ============================================
        # VALIDACIONES
        # ============================================
        if not EDN360_OPENAI_API_KEY or EDN360_OPENAI_API_KEY == "TU_API_KEY_AQUI":
            raise Exception(
                "EDN360_OPENAI_API_KEY no está configurada. "
                "Por favor, configura tu API Key de OpenAI en .env"
            )
        
        if not EDN360_TRAINING_WORKFLOW_ID or EDN360_TRAINING_WORKFLOW_ID == "TU_WORKFLOW_ID_AQUI":
            raise Exception(
                "EDN360_TRAINING_WORKFLOW_ID no está configurada. "
                "Por favor, pide el Workflow ID a Jorge y configúralo en .env"
            )
        
        logger.info(
            f"🚀 Iniciando Training Workflow EDN360 | "
            f"Assistant ID: {EDN360_TRAINING_WORKFLOW_ID}"
        )
        
        # ============================================
        # PREPARAR CLIENTE OPENAI
        # ============================================
        client = OpenAI(api_key=EDN360_OPENAI_API_KEY)
        
        # ============================================
        # SERIALIZAR EDN360INPUT
        # ============================================
        def datetime_handler(obj):
            """Handler para serializar datetime a ISO string"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        input_json = json.dumps(
            edn360_input, 
            indent=2, 
            ensure_ascii=False, 
            default=datetime_handler
        )
        
        logger.info(
            f"📋 EDN360Input preparado | "
            f"Size: {len(input_json)} chars | "
            f"Questionnaires: {len(edn360_input.get('questionnaires', []))}"
        )
        
        # ============================================
        # CREAR THREAD
        # ============================================
        thread = client.beta.threads.create()
        logger.info(f"🧵 Thread creado: {thread.id}")
        
        # ============================================
        # ENVIAR MENSAJE AL THREAD
        # ============================================
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=input_json
        )
        logger.info("📤 Mensaje enviado al thread")
        
        # ============================================
        # EJECUTAR ASSISTANT (create_and_poll)
        # ============================================
        logger.info("⏳ Ejecutando Assistant (esto puede tardar 1-2 minutos)...")
        
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=EDN360_TRAINING_WORKFLOW_ID
        )
        
        logger.info(
            f"🏁 Run completado | "
            f"Status: {run.status} | "
            f"Run ID: {run.id}"
        )
        
        # ============================================
        # VERIFICAR STATUS
        # ============================================
        if run.status != "completed":
            error_msg = f"Workflow no completado. Status: {run.status}"
            if hasattr(run, 'last_error') and run.last_error:
                error_msg += f" | Error: {run.last_error}"
            raise Exception(error_msg)
        
        # ============================================
        # OBTENER MENSAJES DEL THREAD
        # ============================================
        messages = client.beta.threads.messages.list(
            thread_id=thread.id,
            order="desc"
        )
        
        if not messages.data:
            raise Exception("No se recibieron mensajes del Assistant")
        
        # El último mensaje (primero en orden desc) es la respuesta
        final_message = messages.data[0]
        
        # Extraer contenido del mensaje
        if not final_message.content or len(final_message.content) == 0:
            raise Exception("El mensaje del Assistant está vacío")
        
        # El contenido es una lista de ContentBlock, tomamos el primero
        content_block = final_message.content[0]
        
        # Verificar que es texto
        if not hasattr(content_block, 'text'):
            raise Exception(f"Tipo de contenido inesperado: {type(content_block)}")
        
        response_text = content_block.text.value
        
        logger.info(
            f"📥 Respuesta recibida | "
            f"Size: {len(response_text)} chars"
        )
        
        # ============================================
        # PARSEAR JSON
        # ============================================
        try:
            workflow_response = json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error parseando JSON: {e}")
            logger.error(f"Respuesta recibida (primeros 500 chars): {response_text[:500]}")
            raise Exception(f"El Assistant no devolvió JSON válido: {str(e)}")
        
        # ============================================
        # VALIDAR ESTRUCTURA
        # ============================================
        if "client_training_program_enriched" not in workflow_response:
            raise Exception(
                f"La respuesta no contiene 'client_training_program_enriched'. "
                f"Claves recibidas: {list(workflow_response.keys())}"
            )
        
        logger.info(
            f"✅ Training Workflow ejecutado exitosamente | "
            f"Sessions: {len(workflow_response['client_training_program_enriched'].get('sessions', []))}"
        )
        
        return workflow_response
    
    except Exception as e:
        logger.error(f"❌ Error en call_training_workflow: {e}")
        raise


def get_training_workflow_config() -> Dict[str, Any]:
    """
    Devuelve la configuración actual del workflow de entrenamiento.
    
    Útil para debugging y verificación.
    
    Returns:
        Dict con configuración actual
    """
    return {
        "workflow_id": EDN360_TRAINING_WORKFLOW_ID,
        "has_api_key": bool(
            EDN360_OPENAI_API_KEY and 
            EDN360_OPENAI_API_KEY != "TU_API_KEY_AQUI"
        ),
        "api_key_preview": (
            f"{EDN360_OPENAI_API_KEY[:10]}..." 
            if EDN360_OPENAI_API_KEY and EDN360_OPENAI_API_KEY != "TU_API_KEY_AQUI" 
            else "NOT_CONFIGURED"
        ),
        "workflow_id_configured": bool(
            EDN360_TRAINING_WORKFLOW_ID and 
            EDN360_TRAINING_WORKFLOW_ID != "TU_WORKFLOW_ID_AQUI"
        )
    }
