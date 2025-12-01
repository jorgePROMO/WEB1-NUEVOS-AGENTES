"""
Training Workflow Service - Integración con Microservicio Node.js (OpenAI Agents SDK)

Este servicio implementa la llamada al workflow de entrenamiento EDN360
usando un microservicio Node.js que ejecuta el SDK de Agentes de OpenAI.

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
from typing import Dict, Any
from datetime import datetime

# Configuración
EDN360_WORKFLOW_SERVICE_URL = os.getenv(
    'EDN360_WORKFLOW_SERVICE_URL',
    'http://localhost:4000/api/edn360/run-training-workflow'
)

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
        if not EDN360_WORKFLOW_SERVICE_URL:
            raise Exception(
                "EDN360_WORKFLOW_SERVICE_URL no está configurada. "
                "Por favor, configura la URL del microservicio en .env"
            )
        
        logger.info(
            f"🚀 Iniciando Training Workflow EDN360 | "
            f"Service URL: {EDN360_WORKFLOW_SERVICE_URL}"
        )
        
        # ============================================
        # PREPARAR EDN360INPUT
        # ============================================
        logger.info(
            f"📋 Preparando EDN360Input | "
            f"Questionnaires: {len(edn360_input.get('questionnaires', []))}"
        )
        
        # ============================================
        # LLAMAR AL MICROSERVICIO NODE.JS
        # ============================================
        logger.info("📤 Enviando EDN360Input al microservicio de workflow...")
        
        try:
            # Timeout de 120 segundos (2 minutos) para dar tiempo al workflow
            workflow_response_raw = requests.post(
                EDN360_WORKFLOW_SERVICE_URL,
                json=edn360_input,
                headers={"Content-Type": "application/json"},
                timeout=120
            )
            
            workflow_response_raw.raise_for_status()
            
            # Parsear respuesta
            workflow_response = workflow_response_raw.json()
            
            logger.info(
                f"📥 Respuesta recibida del microservicio | "
                f"Size: {len(json.dumps(workflow_response))} chars"
            )
            
        except requests.exceptions.Timeout:
            raise Exception(
                "Timeout: El microservicio no respondió en 2 minutos. "
                "Verifica que el servicio esté corriendo y que el workflow no tarde demasiado."
            )
        except requests.exceptions.ConnectionError:
            raise Exception(
                f"Error de conexión: No se puede conectar al microservicio en {EDN360_WORKFLOW_SERVICE_URL}. "
                "Verifica que el servicio esté corriendo."
            )
        except requests.exceptions.HTTPError as e:
            error_detail = workflow_response_raw.text if workflow_response_raw else str(e)
            raise Exception(
                f"Error HTTP {workflow_response_raw.status_code} del microservicio: {error_detail}"
            )
        except json.JSONDecodeError:
            raise Exception(
                "El microservicio no devolvió JSON válido. "
                f"Respuesta: {workflow_response_raw.text[:500]}"
            )
        
        
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
