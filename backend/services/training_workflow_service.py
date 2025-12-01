"""
Training Workflow Service - Integración con OpenAI ChatKit (Agent Builder Workflows)

Este servicio implementa la llamada al workflow de entrenamiento EDN360
usando ChatKit SDK para workflows de Agent Builder.

Contrato:
- INPUT: EDN360Input (user_profile + questionnaires + context)
- OUTPUT: client_training_program_enriched

Referencia: POST /api/training-plan
Fecha: Diciembre 2025
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
                "Por favor, configura el Workflow ID en .env"
            )
        
        logger.info(
            f"🚀 Iniciando Training Workflow EDN360 | "
            f"Workflow ID: {EDN360_TRAINING_WORKFLOW_ID}"
        )
        
        # ============================================
        # PREPARAR CLIENTE OPENAI CON CHATKIT
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
        # CREAR SESIÓN CHATKIT CON EL WORKFLOW
        # ============================================
        logger.info("🔄 Creando sesión ChatKit con workflow EDN360...")
        
        # Crear sesión vinculada al workflow
        session = client.chatkit.sessions.create(
            workflow={"id": EDN360_TRAINING_WORKFLOW_ID},
            user=edn360_input.get('user_profile', {}).get('user_id', 'unknown')
        )
        
        logger.info(f"✅ Sesión ChatKit creada: {session.id}")
        
        # ============================================
        # ENVIAR EDN360INPUT COMO MENSAJE DE USUARIO
        # ============================================
        logger.info("📤 Enviando EDN360Input al workflow...")
        
        client.chatkit.messages.create(
            session_id=session.id,
            role="user",
            content=input_json
        )
        
        logger.info("✅ Mensaje enviado, esperando respuesta del workflow...")
        
        # ============================================
        # ESPERAR Y OBTENER RESPUESTA DEL WORKFLOW
        # ============================================
        logger.info("⏳ Ejecutando Workflow EDN360 (esto puede tardar 1-2 minutos)...")
        
        # Polling: esperar hasta que haya respuesta del assistant
        import time
        max_attempts = 60  # 2 minutos máximo
        attempt = 0
        
        while attempt < max_attempts:
            # Listar mensajes de la sesión
            messages_response = client.chatkit.messages.list(session_id=session.id)
            messages = messages_response.get('data', [])
            
            # Buscar último mensaje del assistant
            assistant_messages = [m for m in messages if m.get('role') == 'assistant']
            
            if assistant_messages:
                # Tomar el último mensaje del assistant
                final_message = assistant_messages[-1]
                response_text = final_message.get('content', '')
                
                if response_text:
                    logger.info(
                        f"📥 Respuesta recibida del workflow | "
                        f"Size: {len(response_text)} chars"
                    )
                    break
            
            # Esperar 2 segundos antes del siguiente intento
            time.sleep(2)
            attempt += 1
        
        if attempt >= max_attempts:
            raise Exception("Timeout: El workflow no respondió en 2 minutos")
        
        if not response_text:
            raise Exception("El workflow no devolvió contenido")
        
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
