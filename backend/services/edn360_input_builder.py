"""
EDN360 Input Builder - Construcción del contrato de entrada

Este módulo construye el EDN360Input desde:
- BD Web (test_database.users)
- BD EDN360_APP (edn360_app.client_drawers)

El EDN360Input es el contrato estándar que usaremos para llamar
a los Workflows de OpenAI (E1-E9, N0-N8).

Referencia: FASE 2 - Definición EDN360_INPUT
Fecha: Enero 2025
"""

import os
import logging
from typing import Optional
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from edn360_models.edn360_input import (
    EDN360Input,
    EDN360UserProfile,
    EDN360Questionnaire,
    EDN360NoDrawerError,
    EDN360NoQuestionnaireError
)
from repositories.client_drawer_repository import get_drawer_by_user_id

# Configuración
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
MONGO_WEB_DB_NAME = os.getenv('MONGO_WEB_DB_NAME', 'test_database')

# Cliente MongoDB para BD Web
client_web = AsyncIOMotorClient(MONGO_URL)
db_web = client_web[MONGO_WEB_DB_NAME]

# Logger
logger = logging.getLogger(__name__)


# ============================================
# BUILDER PRINCIPAL
# ============================================

async def build_edn360_input_for_user(user_id: str) -> EDN360Input:
    """
    Construye el EDN360Input para un usuario específico.
    
    Este es el builder principal que:
    1. Lee el perfil del usuario desde BD Web (test_database.users)
    2. Lee el client_drawer desde BD EDN360_APP (edn360_app.client_drawers)
    3. Mapea los shared_questionnaires a EDN360Questionnaire
    4. Ordena los cuestionarios cronológicamente (ascendente)
    5. Retorna un EDN360Input completo
    
    Args:
        user_id: ID del usuario en BD Web
    
    Returns:
        EDN360Input completo con perfil + cuestionarios
    
    Raises:
        EDN360NoDrawerError: Si el usuario no tiene client_drawer
        EDN360NoQuestionnaireError: Si tiene drawer pero sin cuestionarios
        Exception: Cualquier otro error inesperado
    
    Example:
        edn360_input = await build_edn360_input_for_user("1762976907472415")
        print(f"Usuario: {edn360_input.user_profile.name}")
        print(f"Cuestionarios: {edn360_input.questionnaire_count()}")
    
    Orden de cuestionarios:
        Los cuestionarios se ordenan por submitted_at ASCENDENTE:
        - Primer elemento: Cuestionario más antiguo (inicial)
        - Siguientes: Followups en orden cronológico
        - Último elemento: Cuestionario más reciente
    
    Fuentes de datos:
        - user_profile: BD Web (test_database.users)
        - questionnaires: BD EDN360_APP (edn360_app.client_drawers.services.shared_questionnaires)
    """
    try:
        logger.info(f"🏗️  Construyendo EDN360Input para user_id: {user_id}")
        
        # ============================================
        # 1. LEER PERFIL DE USUARIO (BD WEB)
        # ============================================
        user_profile = await _build_user_profile(user_id)
        
        if not user_profile:
            raise Exception(f"Usuario {user_id} no encontrado en BD Web")
        
        logger.info(f"✅ Perfil de usuario cargado: {user_profile.name}")
        
        # ============================================
        # 2. LEER CLIENT_DRAWER (BD EDN360_APP)
        # ============================================
        drawer = await get_drawer_by_user_id(user_id)
        
        if not drawer:
            raise EDN360NoDrawerError(
                f"Usuario {user_id} no tiene client_drawer. "
                f"Esto puede ocurrir si el usuario nunca ha completado un cuestionario "
                f"o si el dual-write no estaba activado cuando lo hizo."
            )
        
        logger.info(f"✅ Client_drawer encontrado: {drawer.id}")
        
        # ============================================
        # 3. MAPEAR CUESTIONARIOS
        # ============================================
        questionnaires = _map_questionnaires(drawer.services.shared_questionnaires)
        
        if not questionnaires:
            logger.warning(f"⚠️  Client_drawer {drawer.id} no tiene cuestionarios")
            # De momento permitimos drawers sin cuestionarios
            # raise EDN360NoQuestionnaireError(
            #     f"Usuario {user_id} tiene client_drawer pero sin cuestionarios"
            # )
        
        logger.info(f"✅ {len(questionnaires)} cuestionario(s) mapeados")
        
        # ============================================
        # 4. CONSTRUIR EDN360INPUT
        # ============================================
        edn360_input = EDN360Input(
            user_profile=user_profile,
            questionnaires=questionnaires,
            generated_at=datetime.now(timezone.utc),
            version="1.0.0"
        )
        
        logger.info(
            f"✅ EDN360Input construido exitosamente: "
            f"{edn360_input.questionnaire_count()} cuestionario(s)"
        )
        
        return edn360_input
    
    except EDN360NoDrawerError:
        # Re-lanzar excepciones específicas
        raise
    except EDN360NoQuestionnaireError:
        raise
    except Exception as e:
        logger.error(f"❌ Error construyendo EDN360Input para user_id {user_id}: {e}")
        raise



async def build_edn360_input_for_user_with_specific_questionnaires(
    user_id: str,
    questionnaire_ids: list[str]
) -> EDN360Input:
    """
    Construye un EDN360Input para un usuario usando SOLO los cuestionarios específicos seleccionados.
    
    Args:
        user_id: ID del usuario
        questionnaire_ids: Lista de IDs de cuestionarios a incluir (en el orden deseado)
    
    Returns:
        EDN360Input completo con solo los cuestionarios seleccionados
    
    Example:
        # Incluir solo cuestionario inicial + seguimiento 1
        edn360_input = await build_edn360_input_for_user_with_specific_questionnaires(
            "1764016044644335",
            ["quest_initial_001", "quest_followup_001"]
        )
    """
    try:
        logger.info(
            f"🏗️  Construyendo EDN360Input para user_id: {user_id} | "
            f"Con {len(questionnaire_ids)} cuestionarios específicos"
        )
        
        # ============================================
        # 1. LEER PERFIL DE USUARIO (BD WEB)
        # ============================================
        user_profile = await _build_user_profile(user_id)
        
        if not user_profile:
            raise Exception(f"Usuario {user_id} no encontrado en BD Web")
        
        logger.info(f"✅ Perfil de usuario cargado: {user_profile.name}")
        
        # ============================================
        # 2. LEER CLIENT_DRAWER (BD EDN360_APP)
        # ============================================
        drawer = await get_drawer_by_user_id(user_id)
        
        if not drawer:
            raise EDN360NoDrawerError(
                f"Usuario {user_id} no tiene client_drawer"
            )
        
        logger.info(f"✅ Client_drawer encontrado: {drawer.id}")
        
        # ============================================
        # 3. FILTRAR CUESTIONARIOS POR IDS
        # ============================================
        all_questionnaires = drawer.services.shared_questionnaires
        
        # Crear mapa de cuestionarios por ID
        quest_map = {q.submission_id: q for q in all_questionnaires}
        
        # Obtener solo los cuestionarios seleccionados en el orden especificado
        selected_questionnaires_raw = []
        for q_id in questionnaire_ids:
            if q_id in quest_map:
                selected_questionnaires_raw.append(quest_map[q_id])
                logger.info(f"   ✓ Cuestionario incluido: {q_id}")
            else:
                logger.warning(f"   ⚠️  Cuestionario {q_id} no encontrado en drawer")
        
        if not selected_questionnaires_raw:
            raise Exception(
                f"Ninguno de los cuestionarios seleccionados fue encontrado en el drawer del usuario"
            )
        
        # Mapear a EDN360Questionnaire
        questionnaires = _map_questionnaires(selected_questionnaires_raw)
        
        logger.info(f"✅ {len(questionnaires)} cuestionario(s) seleccionados y mapeados")
        
        # ============================================
        # 4. CONSTRUIR EDN360INPUT
        # ============================================
        edn360_input = EDN360Input(
            user_profile=user_profile,
            questionnaires=questionnaires,
            generated_at=datetime.now(timezone.utc),
            version="1.0.0"
        )
        
        logger.info(
            f"✅ EDN360Input construido con cuestionarios específicos: "
            f"{edn360_input.questionnaire_count()} cuestionario(s)"
        )
        
        return edn360_input
    
    except EDN360NoDrawerError:
        raise
    except Exception as e:
        logger.error(
            f"❌ Error construyendo EDN360Input con cuestionarios específicos "
            f"para user_id {user_id}: {e}"
        )
        raise


# ============================================
# HELPERS INTERNOS
# ============================================

async def _build_user_profile(user_id: str) -> Optional[EDN360UserProfile]:
    """
    Construye el perfil de usuario desde BD Web.
    
    Args:
        user_id: ID del usuario en BD Web
    
    Returns:
        EDN360UserProfile o None si no existe
    """
    try:
        # Buscar usuario en BD Web
        user_doc = await db_web.users.find_one({"_id": user_id})
        
        if not user_doc:
            logger.warning(f"⚠️  Usuario {user_id} no encontrado en BD Web")
            return None
        
        # Handle both string and dict subscription formats (backward compatibility)
        subscription_data = user_doc.get("subscription", {})
        if isinstance(subscription_data, str):
            # Legacy format: subscription is a string (e.g., "premium")
            subscription_plan = subscription_data
            subscription_status = user_doc.get("subscription_status", "active")
        else:
            # Modern format: subscription is a dict
            subscription_plan = subscription_data.get("plan")
            subscription_status = subscription_data.get("payment_status")
        
        # Mapear a EDN360UserProfile
        user_profile = EDN360UserProfile(
            user_id=user_doc["_id"],
            name=user_doc.get("name"),
            email=user_doc.get("email"),
            phone=user_doc.get("phone"),
            created_at=user_doc.get("created_at"),
            subscription_plan=subscription_plan,
            subscription_status=subscription_status
        )
        
        return user_profile
    
    except Exception as e:
        logger.error(f"❌ Error construyendo user_profile para {user_id}: {e}")
        raise


def _map_questionnaires(shared_questionnaires: list) -> list[EDN360Questionnaire]:
    """
    Mapea SharedQuestionnaire de client_drawer a EDN360Questionnaire.
    
    Orden:
        Los cuestionarios se ordenan por submitted_at ASCENDENTE (más antiguo → más reciente)
    
    Args:
        shared_questionnaires: Lista de SharedQuestionnaire del drawer
    
    Returns:
        Lista de EDN360Questionnaire ordenada cronológicamente
    """
    try:
        # Mapear cada SharedQuestionnaire a EDN360Questionnaire
        questionnaires = []
        
        for sq in shared_questionnaires:
            questionnaire = EDN360Questionnaire(
                submission_id=sq.submission_id,
                submitted_at=sq.submitted_at,
                source=sq.source,
                payload=sq.raw_payload
            )
            questionnaires.append(questionnaire)
        
        # Ordenar por submitted_at ASCENDENTE (más antiguo primero)
        questionnaires.sort(key=lambda q: q.submitted_at)
        
        logger.info(
            f"📋 Cuestionarios ordenados cronológicamente: "
            f"{len(questionnaires)} total"
        )
        
        return questionnaires
    
    except Exception as e:
        logger.error(f"❌ Error mapeando cuestionarios: {e}")
        raise


# ============================================
# HELPERS ADICIONALES
# ============================================

async def validate_edn360_input_for_user(user_id: str) -> tuple[bool, list[str]]:
    """
    Valida que se puede construir un EDN360Input válido para un usuario.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        Tuple (es_valido, lista_de_errores)
    
    Example:
        is_valid, errors = await validate_edn360_input_for_user("1762...")
        if not is_valid:
            print(f"Errores: {errors}")
    """
    try:
        # Intentar construir el EDN360Input
        edn360_input = await build_edn360_input_for_user(user_id)
        
        # Validar la estructura
        from models.edn360_input import validate_edn360_input
        is_valid, errors = validate_edn360_input(edn360_input)
        
        return (is_valid, errors)
    
    except EDN360NoDrawerError as e:
        return (False, [str(e)])
    except EDN360NoQuestionnaireError as e:
        return (False, [str(e)])
    except Exception as e:
        return (False, [f"Error inesperado: {str(e)}"])


async def get_edn360_input_summary(user_id: str) -> dict:
    """
    Obtiene un resumen del EDN360Input sin construirlo completo.
    
    Útil para mostrar en UI sin cargar todo el payload.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        Dict con resumen:
        - user_id, name, email
        - questionnaires_count
        - has_initial, has_followups
        - latest_questionnaire_date
    """
    try:
        edn360_input = await build_edn360_input_for_user(user_id)
        
        latest_q = edn360_input.get_latest_questionnaire()
        
        return {
            "user_id": edn360_input.user_profile.user_id,
            "name": edn360_input.user_profile.name,
            "email": edn360_input.user_profile.email,
            "questionnaires_count": edn360_input.questionnaire_count(),
            "has_initial": edn360_input.get_initial_questionnaire() is not None,
            "has_followups": edn360_input.has_followups(),
            "latest_questionnaire_date": latest_q.submitted_at if latest_q else None,
            "generated_at": edn360_input.generated_at
        }
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen para user_id {user_id}: {e}")
        return {
            "error": str(e),
            "user_id": user_id
        }
