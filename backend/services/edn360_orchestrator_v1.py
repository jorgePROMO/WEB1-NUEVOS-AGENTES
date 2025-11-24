"""
EDN360 Orchestrator v1 - Orquestador principal de Workflow

Este módulo orquesta la ejecución completa del Workflow EDN360:
1. Construye el EDN360Input para un usuario (reutiliza FASE 2)
2. Llama al Workflow de OpenAI con ese input
3. Guarda un snapshot técnico inmutable en BD

El orquestador es el punto de entrada para ejecutar el Workflow EDN360
desde cualquier parte del sistema (endpoints admin, job workers, etc.)

IMPORTANTE:
- Esta FASE 3 NO modifica training_plans ni nutrition_plans
- Solo crea snapshots técnicos para testing interno
- NO reemplaza el sistema legacy de generación de planes todavía

Referencia: FASE 3 - Nuevo Orquestador EDN360 v1
Fecha: Enero 2025
"""

import os
import logging
from typing import Dict, Any
from datetime import datetime, timezone

from services.edn360_input_builder import build_edn360_input_for_user
from services.gpt_service import call_edn360_workflow
from repositories.edn360_snapshot_repository import create_snapshot
from models.edn360_input import EDN360NoDrawerError, EDN360NoQuestionnaireError

# Configuración
EDN360_WORKFLOW_NAME = os.getenv('EDN360_WORKFLOW_NAME', 'edn360_full_plan_v1')

# Logger
logger = logging.getLogger(__name__)


async def run_edn360_workflow_for_user(user_id: str) -> Dict[str, Any]:
    """
    Ejecuta el Workflow EDN360 completo para un usuario.
    
    Este es el orquestador principal que:
    1. Construye el EDN360Input usando build_edn360_input_for_user (FASE 2)
    2. Llama al Workflow de OpenAI con ese input
    3. Crea un EDN360Snapshot con input + response (inmutable)
    4. Devuelve un resumen ligero del resultado
    
    Args:
        user_id: ID del usuario en BD Web
    
    Returns:
        Dict con resumen del resultado:
        {
            "snapshot_id": "uuid-123-456",
            "user_id": "1762976907472415",
            "status": "success" | "failed",
            "created_at": "2025-01-20T10:30:00Z",
            "workflow_name": "edn360_full_plan_v1",
            "has_response": true
        }
    
    Raises:
        NO lanza excepciones. Siempre devuelve un resultado (success o failed).
        Los errores se capturan y se guardan en snapshots con status="failed".
    
    Example:
        # Desde un endpoint admin
        result = await run_edn360_workflow_for_user("1762976907472415")
        
        if result["status"] == "success":
            print(f"✅ Workflow ejecutado. Snapshot: {result['snapshot_id']}")
        else:
            print(f"❌ Error: {result.get('error_message')}")
    
    Flujo:
        1. Construir EDN360Input
           ↓
        2. Llamar a OpenAI Workflow
           ↓
        3. Crear snapshot (success o failed)
           ↓
        4. Devolver resumen
    
    Notas:
        - Esta función NO modifica training_plans ni nutrition_plans
        - Solo crea snapshots técnicos en edn360_snapshots
        - Los snapshots son inmutables (no se modifican después de crearlos)
        - Si hay error, se crea un snapshot con status="failed"
    """
    try:
        logger.info(f"🚀 INICIANDO Workflow EDN360 para user_id: {user_id}")
        
        # ============================================
        # PASO 1: CONSTRUIR EDN360INPUT
        # ============================================
        try:
            logger.info(f"📋 Paso 1: Construyendo EDN360Input para user_id: {user_id}")
            
            edn360_input = await build_edn360_input_for_user(user_id)
            
            # Serializar a dict para pasarlo a OpenAI y guardarlo en snapshot
            edn360_input_dict = edn360_input.dict()
            
            logger.info(
                f"✅ EDN360Input construido | "
                f"Cuestionarios: {edn360_input.questionnaire_count()}"
            )
        
        except EDN360NoDrawerError as e:
            # Usuario no tiene client_drawer
            logger.warning(f"⚠️  Usuario {user_id} no tiene client_drawer: {e}")
            
            # Crear snapshot de error
            error_snapshot = await create_snapshot(
                user_id=user_id,
                edn360_input={},
                workflow_name=EDN360_WORKFLOW_NAME,
                workflow_response={},
                status="failed",
                error_message=f"Usuario no tiene client_drawer: {str(e)}"
            )
            
            return {
                "snapshot_id": error_snapshot.snapshot_id,
                "user_id": user_id,
                "status": "failed",
                "created_at": error_snapshot.created_at.isoformat(),
                "workflow_name": EDN360_WORKFLOW_NAME,
                "has_response": False,
                "error_message": str(e)
            }
        
        except EDN360NoQuestionnaireError as e:
            # Usuario tiene drawer pero sin cuestionarios
            logger.warning(f"⚠️  Usuario {user_id} no tiene cuestionarios: {e}")
            
            error_snapshot = await create_snapshot(
                user_id=user_id,
                edn360_input={},
                workflow_name=EDN360_WORKFLOW_NAME,
                workflow_response={},
                status="failed",
                error_message=f"Usuario no tiene cuestionarios: {str(e)}"
            )
            
            return {
                "snapshot_id": error_snapshot.snapshot_id,
                "user_id": user_id,
                "status": "failed",
                "created_at": error_snapshot.created_at.isoformat(),
                "workflow_name": EDN360_WORKFLOW_NAME,
                "has_response": False,
                "error_message": str(e)
            }
        
        except Exception as e:
            # Error inesperado construyendo el input
            logger.error(f"❌ Error construyendo EDN360Input para user_id {user_id}: {e}")
            
            error_snapshot = await create_snapshot(
                user_id=user_id,
                edn360_input={},
                workflow_name=EDN360_WORKFLOW_NAME,
                workflow_response={},
                status="failed",
                error_message=f"Error construyendo EDN360Input: {str(e)}"
            )
            
            return {
                "snapshot_id": error_snapshot.snapshot_id,
                "user_id": user_id,
                "status": "failed",
                "created_at": error_snapshot.created_at.isoformat(),
                "workflow_name": EDN360_WORKFLOW_NAME,
                "has_response": False,
                "error_message": str(e)
            }
        
        # ============================================
        # PASO 2: LLAMAR A OPENAI WORKFLOW
        # ============================================
        try:
            logger.info(f"🤖 Paso 2: Llamando a OpenAI Workflow EDN360")
            
            workflow_response = await call_edn360_workflow(edn360_input_dict)
            
            logger.info(
                f"✅ Workflow ejecutado exitosamente | "
                f"Tokens: {workflow_response.get('_metadata', {}).get('tokens_used', 'N/A')}"
            )
        
        except Exception as e:
            # Error en la llamada a OpenAI
            logger.error(f"❌ Error llamando a OpenAI Workflow: {e}")
            
            # Crear snapshot de error (pero con el input que SÍ pudimos construir)
            error_snapshot = await create_snapshot(
                user_id=user_id,
                edn360_input=edn360_input_dict,
                workflow_name=EDN360_WORKFLOW_NAME,
                workflow_response={},
                status="failed",
                error_message=f"Error llamando a OpenAI Workflow: {str(e)}"
            )
            
            return {
                "snapshot_id": error_snapshot.snapshot_id,
                "user_id": user_id,
                "status": "failed",
                "created_at": error_snapshot.created_at.isoformat(),
                "workflow_name": EDN360_WORKFLOW_NAME,
                "has_response": False,
                "error_message": str(e)
            }
        
        # ============================================
        # PASO 3: CREAR SNAPSHOT (SUCCESS)
        # ============================================
        try:
            logger.info(f"💾 Paso 3: Guardando snapshot en BD")
            
            success_snapshot = await create_snapshot(
                user_id=user_id,
                edn360_input=edn360_input_dict,
                workflow_name=EDN360_WORKFLOW_NAME,
                workflow_response=workflow_response,
                status="success"
            )
            
            logger.info(
                f"✅ Snapshot creado exitosamente: {success_snapshot.snapshot_id}"
            )
        
        except Exception as e:
            # Error guardando el snapshot (muy raro)
            logger.error(f"❌ Error creando snapshot: {e}")
            
            # Intentar crear un snapshot de error básico
            try:
                error_snapshot = await create_snapshot(
                    user_id=user_id,
                    edn360_input=edn360_input_dict,
                    workflow_name=EDN360_WORKFLOW_NAME,
                    workflow_response={},
                    status="failed",
                    error_message=f"Error guardando snapshot: {str(e)}"
                )
                
                return {
                    "snapshot_id": error_snapshot.snapshot_id,
                    "user_id": user_id,
                    "status": "failed",
                    "created_at": error_snapshot.created_at.isoformat(),
                    "workflow_name": EDN360_WORKFLOW_NAME,
                    "has_response": False,
                    "error_message": str(e)
                }
            except:
                # Si ni siquiera podemos guardar el error, devolver respuesta manual
                return {
                    "snapshot_id": None,
                    "user_id": user_id,
                    "status": "failed",
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "workflow_name": EDN360_WORKFLOW_NAME,
                    "has_response": False,
                    "error_message": f"Error crítico: no se pudo guardar snapshot: {str(e)}"
                }
        
        # ============================================
        # PASO 4: DEVOLVER RESUMEN
        # ============================================
        logger.info(
            f"✅ WORKFLOW EDN360 COMPLETADO | "
            f"user_id: {user_id} | snapshot_id: {success_snapshot.snapshot_id}"
        )
        
        return {
            "snapshot_id": success_snapshot.snapshot_id,
            "user_id": user_id,
            "status": "success",
            "created_at": success_snapshot.created_at.isoformat(),
            "workflow_name": EDN360_WORKFLOW_NAME,
            "has_response": True
        }
    
    except Exception as e:
        # Catch-all para cualquier error no previsto
        logger.error(f"❌ Error inesperado en run_edn360_workflow_for_user: {e}")
        
        return {
            "snapshot_id": None,
            "user_id": user_id,
            "status": "failed",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "workflow_name": EDN360_WORKFLOW_NAME,
            "has_response": False,
            "error_message": f"Error inesperado: {str(e)}"
        }


# ============================================
# HELPERS ADICIONALES
# ============================================

async def get_workflow_status_for_user(user_id: str) -> Dict[str, Any]:
    """
    Obtiene el estado del workflow para un usuario (último snapshot).
    
    Args:
        user_id: ID del usuario
    
    Returns:
        Dict con estado del último workflow ejecutado
    """
    try:
        from repositories.edn360_snapshot_repository import get_latest_snapshot_for_user
        
        latest_snapshot = await get_latest_snapshot_for_user(user_id)
        
        if not latest_snapshot:
            return {
                "user_id": user_id,
                "has_workflow": False,
                "message": "No se ha ejecutado ningún workflow para este usuario"
            }
        
        return {
            "user_id": user_id,
            "has_workflow": True,
            "latest_snapshot": latest_snapshot.get_summary()
        }
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo estado de workflow para user_id {user_id}: {e}")
        return {
            "user_id": user_id,
            "error": str(e)
        }
