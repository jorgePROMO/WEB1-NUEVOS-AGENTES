"""
Training Workflow Service - Integración con OpenAI ChatKit (Agent Builder Workflows)

Este servicio implementa la llamada al workflow de entrenamiento EDN360
usando ChatKit REST API para workflows de Agent Builder.

Contrato:
- INPUT: EDN360Input (user_profile + questionnaires + context)
- OUTPUT: client_training_program_enriched

Referencia: POST /api/training-plan
Fecha: Diciembre 2025
"""

import os
import json
import logging
import requests
import time
from typing import Dict, Any
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
                "Por favor, configura el Workflow ID en .env"
            )
        
        logger.info(
            f"🚀 Iniciando Training Workflow EDN360 | "
            f"Workflow ID: {EDN360_TRAINING_WORKFLOW_ID}"
        )
        
        # ============================================
        # PREPARAR HEADERS PARA CHATKIT REST API
        # ============================================
        chatkit_base_url = "https://api.openai.com/v1/chatkit"
        headers = {
            "Authorization": f"Bearer {EDN360_OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "OpenAI-Beta": "chatkit_beta=v1"
        }
        
        # ============================================
        # SERIALIZAR EDN360INPUT
        # ============================================
        def datetime_handler(obj):
            """Handler para serializar datetime a ISO string"""
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        input_json_str = json.dumps(
            edn360_input, 
            indent=2, 
            ensure_ascii=False, 
            default=datetime_handler
        )
        
        logger.info(
            f"📋 EDN360Input preparado | "
            f"Size: {len(input_json_str)} chars | "
            f"Questionnaires: {len(edn360_input.get('questionnaires', []))}"
        )
        
        # ============================================
        # PASO 1: CREAR SESIÓN CHATKIT (SIN INPUT)
        # ============================================
        logger.info("🔄 Creando sesión ChatKit con workflow EDN360...")
        
        user_id = edn360_input.get('user_profile', {}).get('user_id', 'edn360_backend')
        
        # Crear sesión SIN el campo 'input' (ChatKit no lo soporta)
        session_payload = {
            "workflow": {"id": EDN360_TRAINING_WORKFLOW_ID},
            "user": user_id
        }
        
        sessions_url = f"{chatkit_base_url}/sessions"
        logger.info(f"📤 POST {sessions_url}")
        logger.info(f"   Workflow ID: {EDN360_TRAINING_WORKFLOW_ID}")
        
        session_response = requests.post(
            sessions_url,
            headers=headers,
            json=session_payload,
            timeout=30
        )
        
        session_response.raise_for_status()
        
        session_data = session_response.json()
        session_id = session_data.get('id')
        
        logger.info(f"✅ Sesión ChatKit creada: {session_id}")
        
        # ============================================
        # PASO 2: ENVIAR EDN360INPUT COMO MENSAJE
        # ============================================
        logger.info("📤 Enviando EDN360Input como mensaje de usuario...")
        
        message_payload = {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": input_json_str
                }
            ]
        }
        
        messages_url = f"{chatkit_base_url}/sessions/{session_id}/messages"
        logger.info(f"📤 POST {messages_url}")
        
        message_response = requests.post(
            messages_url,
            headers=headers,
            json=message_payload,
            timeout=30
        )
        
        message_response.raise_for_status()
        
        logger.info("✅ Mensaje enviado correctamente")
        
        # ============================================
        # PASO 3: POLLING - ESPERAR RESPUESTA DEL WORKFLOW
        # ============================================
        logger.info("⏳ Ejecutando Workflow EDN360 (esto puede tardar 1-2 minutos)...")
        
        # Polling: esperar hasta que haya respuesta del assistant
        max_attempts = 60  # 2 minutos máximo (60 intentos x 2 segundos)
        sleep_seconds = 2
        response_text = None
        
        for attempt in range(max_attempts):
            # Esperar antes de cada intento (excepto el primero)
            if attempt > 0:
                time.sleep(sleep_seconds)
            
            # Obtener mensajes de la sesión (ordenados desc para obtener los más recientes)
            messages_response = requests.get(
                f"{chatkit_base_url}/sessions/{session_id}/messages",
                headers=headers,
                params={"limit": 50, "order": "desc"},
                timeout=10
            )
            
            if messages_response.status_code != 200:
                logger.warning(f"⚠️ Error obteniendo mensajes: {messages_response.status_code}")
                continue
            
            messages_data = messages_response.json()
            messages = messages_data.get('data', [])
            
            # Buscar el primer mensaje del assistant con contenido type = "output_text"
            for message in messages:
                if message.get('role') == 'assistant':
                    content_blocks = message.get('content', [])
                    for block in content_blocks:
                        # ChatKit puede usar "output_text" o "text" como tipo
                        if block.get('type') in ['output_text', 'text']:
                            response_text = block.get('text', '')
                            if response_text:
                                logger.info(
                                    f"📥 Respuesta recibida del workflow | "
                                    f"Size: {len(response_text)} chars | "
                                    f"Attempt: {attempt + 1}/{max_attempts}"
                                )
                                break
                    if response_text:
                        break
            
            if response_text:
                break
            
            # Log cada 10 intentos para dar feedback
            if (attempt + 1) % 10 == 0:
                logger.info(f"⏳ Esperando respuesta... ({attempt + 1}/{max_attempts} intentos)")
        
        if not response_text:
            raise Exception(f"Timeout o sin respuesta: El workflow no respondió después de {max_attempts * sleep_seconds} segundos")
        
        
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
            # Loggear el contenido completo si hay un error
            logger.error(f"❌ Respuesta NO contiene 'client_training_program_enriched'")
            logger.error(f"📦 Claves recibidas: {list(workflow_response.keys())}")
            logger.error(f"📄 Contenido completo: {json.dumps(workflow_response, indent=2)[:1000]}")
            
            raise Exception(
                f"La respuesta no contiene 'client_training_program_enriched'. "
                f"Claves recibidas: {list(workflow_response.keys())}. "
                f"Respuesta: {json.dumps(workflow_response, indent=2)[:500]}"
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
        "workflow_type": "openai_agent_builder",
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
