"""
Client Drawer Repository - Data Access Layer

Funciones de acceso a la colección client_drawers en BD EDN360_APP.

Responsabilidades:
- CRUD básico de ClientDrawer
- Búsqueda por user_id
- Creación de cajones vacíos
- Actualización de cuestionarios y planes

NO contiene lógica de negocio. Solo acceso a datos.

Referencia: DOCUMENTO_2_VFINAL_TO_BE_CLIENT_DRAWER.md
Fase: FASE 0 (Base mínima)
"""

import os
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

from models.client_drawer import (
    ClientDrawer,
    SharedQuestionnaire,
    Services,
    TrainingModule,
    NutritionModule,
    validate_drawer_structure
)

# Configuración
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
MONGO_EDN360_APP_DB_NAME = os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')

# Cliente MongoDB para EDN360_APP
client = AsyncIOMotorClient(MONGO_URL)
db_edn360 = client[MONGO_EDN360_APP_DB_NAME]
collection = db_edn360.client_drawers

# Logger
logger = logging.getLogger(__name__)


# ============================================
# FUNCIONES BÁSICAS DE LECTURA
# ============================================

async def get_drawer_by_user_id(user_id: str) -> Optional[ClientDrawer]:
    """
    Obtiene el cajón de un usuario por su user_id.
    
    Args:
        user_id: ID del usuario en BD Web
    
    Returns:
        ClientDrawer si existe, None si no existe
    
    Example:
        drawer = await get_drawer_by_user_id("1762094831193507")
        if drawer:
            print(f"Cajón encontrado: {drawer.id}")
    """
    try:
        # Buscar en BD EDN360_APP
        drawer_doc = await collection.find_one({"user_id": user_id})
        
        if not drawer_doc:
            logger.info(f"Cajón no encontrado para user_id: {user_id}")
            return None
        
        # Convertir a modelo Pydantic
        drawer = ClientDrawer(**drawer_doc)
        
        logger.info(f"✅ Cajón encontrado: {drawer.id} (user_id: {user_id})")
        return drawer
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo cajón para user_id {user_id}: {e}")
        return None


async def get_drawer_by_id(drawer_id: str) -> Optional[ClientDrawer]:
    """
    Obtiene el cajón por su ID (_id).
    
    Args:
        drawer_id: ID del cajón (ej: "client_1762094831193507")
    
    Returns:
        ClientDrawer si existe, None si no existe
    """
    try:
        drawer_doc = await collection.find_one({"_id": drawer_id})
        
        if not drawer_doc:
            return None
        
        return ClientDrawer(**drawer_doc)
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo cajón por ID {drawer_id}: {e}")
        return None


# ============================================
# FUNCIONES DE CREACIÓN
# ============================================

async def create_empty_drawer_for_user(user_id: str) -> ClientDrawer:
    """
    Crea un cajón vacío para un nuevo usuario.
    
    Args:
        user_id: ID del usuario en BD Web
    
    Returns:
        ClientDrawer creado y guardado en BD
    
    Raises:
        Exception: Si ya existe un cajón para este user_id
    
    Example:
        drawer = await create_empty_drawer_for_user("1762094831193507")
        print(f"Cajón creado: {drawer.id}")
    """
    try:
        # Verificar que no existe ya
        existing = await get_drawer_by_user_id(user_id)
        if existing:
            raise Exception(f"Ya existe un cajón para user_id: {user_id}")
        
        # Crear cajón vacío usando factory method
        drawer = ClientDrawer.create_empty_for_user(user_id)
        
        # Validar estructura
        is_valid, errors = validate_drawer_structure(drawer)
        if not is_valid:
            raise Exception(f"Cajón inválido: {errors}")
        
        # Convertir a dict y guardar en BD
        drawer_dict = drawer.dict(by_alias=True)
        
        await collection.insert_one(drawer_dict)
        
        logger.info(f"✅ Cajón vacío creado: {drawer.id} (user_id: {user_id})")
        
        return drawer
    
    except Exception as e:
        logger.error(f"❌ Error creando cajón para user_id {user_id}: {e}")
        raise


async def get_or_create_drawer(user_id: str) -> ClientDrawer:
    """
    Obtiene el cajón de un usuario, o lo crea si no existe.
    
    Args:
        user_id: ID del usuario en BD Web
    
    Returns:
        ClientDrawer (existente o nuevo)
    
    Example:
        drawer = await get_or_create_drawer("1762094831193507")
        # Siempre retorna un drawer válido
    """
    try:
        # Intentar obtener existente
        drawer = await get_drawer_by_user_id(user_id)
        
        if drawer:
            return drawer
        
        # Si no existe, crear
        logger.info(f"ℹ️  Cajón no existe para user_id {user_id}, creando...")
        return await create_empty_drawer_for_user(user_id)
    
    except Exception as e:
        logger.error(f"❌ Error en get_or_create_drawer para user_id {user_id}: {e}")
        raise


# ============================================
# FUNCIONES DE ACTUALIZACIÓN
# ============================================

async def upsert_drawer(drawer: ClientDrawer) -> ClientDrawer:
    """
    Guarda cambios en un cajón existente o crea uno nuevo.
    
    Actualiza automáticamente el campo updated_at.
    
    Args:
        drawer: ClientDrawer a guardar
    
    Returns:
        ClientDrawer actualizado
    
    Example:
        drawer = await get_drawer_by_user_id("1762...")
        drawer.services.training.active_plan_id = "plan_123"
        drawer = await upsert_drawer(drawer)
    """
    try:
        # Actualizar timestamp
        drawer.updated_at = datetime.now(timezone.utc)
        
        # Validar estructura
        is_valid, errors = validate_drawer_structure(drawer)
        if not is_valid:
            raise Exception(f"Cajón inválido: {errors}")
        
        # Convertir a dict
        drawer_dict = drawer.dict(by_alias=True)
        
        # Upsert en BD (actualizar o insertar)
        await collection.replace_one(
            {"user_id": drawer.user_id},
            drawer_dict,
            upsert=True
        )
        
        logger.info(f"✅ Cajón actualizado: {drawer.id} (user_id: {drawer.user_id})")
        
        return drawer
    
    except Exception as e:
        logger.error(f"❌ Error guardando cajón {drawer.id}: {e}")
        raise


async def update_drawer_field(
    user_id: str,
    field_path: str,
    value: Any
) -> bool:
    """
    Actualiza un campo específico del cajón sin reemplazar todo el documento.
    
    Args:
        user_id: ID del usuario
        field_path: Ruta del campo (ej: "services.training.active_plan_id")
        value: Nuevo valor
    
    Returns:
        True si se actualizó correctamente
    
    Example:
        success = await update_drawer_field(
            "1762...",
            "services.training.active_plan_id",
            "plan_123"
        )
    """
    try:
        result = await collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    field_path: value,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count > 0:
            logger.info(f"✅ Campo actualizado: {field_path} = {value} (user_id: {user_id})")
            return True
        else:
            logger.warning(f"⚠️  No se actualizó ningún campo (user_id: {user_id})")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error actualizando campo {field_path} para user_id {user_id}: {e}")
        return False


# ============================================
# FUNCIONES ESPECÍFICAS DE CUESTIONARIOS
# ============================================

async def add_questionnaire_to_drawer(
    user_id: str,
    submission_id: str,
    submitted_at: datetime,
    source: str,
    raw_payload: Optional[Dict[str, Any]] = None
) -> ClientDrawer:
    """
    Añade un cuestionario al cajón del usuario.
    
    ⚠️ IDEMPOTENTE: Si el cuestionario ya existe (mismo submission_id), NO se duplica.
    
    Si el cajón no existe, lo crea.
    
    Args:
        user_id: ID del usuario
        submission_id: ID del cuestionario en BD Web
        submitted_at: Fecha de envío
        source: "prospect_initial" / "nutrition_initial" / "followup"
        raw_payload: Payload completo del cuestionario (opcional)
    
    Returns:
        ClientDrawer actualizado
    
    Example:
        drawer = await add_questionnaire_to_drawer(
            user_id="1762...",
            submission_id="submission_123",
            submitted_at=datetime.now(timezone.utc),
            source="nutrition_initial"
        )
    """
    try:
        # Obtener o crear drawer
        drawer = await get_or_create_drawer(user_id)
        
        # ⚠️ IDEMPOTENCIA: Verificar si el cuestionario ya existe
        existing_ids = [q.submission_id for q in drawer.services.shared_questionnaires]
        
        if submission_id in existing_ids:
            logger.info(
                f"ℹ️  Cuestionario {submission_id} ya existe en drawer de user {user_id}. "
                f"No se duplica (idempotencia)."
            )
            return drawer
        
        # Crear SharedQuestionnaire
        questionnaire = SharedQuestionnaire(
            submission_id=submission_id,
            submitted_at=submitted_at,
            source=source,
            raw_payload=raw_payload or {}
        )
        
        # Añadir a la lista
        drawer.services.shared_questionnaires.append(questionnaire)
        
        # Guardar cambios
        drawer = await upsert_drawer(drawer)
        
        logger.info(
            f"✅ Cuestionario añadido a client_drawer: {submission_id} "
            f"(source: {source}, user_id: {user_id})"
        )
        
        return drawer
    
    except Exception as e:
        logger.error(
            f"❌ Error añadiendo cuestionario a client_drawer "
            f"(user_id: {user_id}, submission_id: {submission_id}): {e}"
        )
        raise


# ============================================
# FUNCIONES DE ESTADÍSTICAS
# ============================================

async def count_drawers() -> int:
    """
    Cuenta el total de cajones en la colección.
    
    Returns:
        Número total de cajones
    """
    try:
        count = await collection.count_documents({})
        return count
    except Exception as e:
        logger.error(f"❌ Error contando cajones: {e}")
        return 0


async def list_all_drawers(limit: int = 100) -> list[ClientDrawer]:
    """
    Lista todos los cajones (limitado).
    
    Args:
        limit: Número máximo de cajones a retornar
    
    Returns:
        Lista de ClientDrawer
    """
    try:
        cursor = collection.find().limit(limit)
        drawers_docs = await cursor.to_list(length=limit)
        
        drawers = [ClientDrawer(**doc) for doc in drawers_docs]
        
        return drawers
    
    except Exception as e:
        logger.error(f"❌ Error listando cajones: {e}")
        return []


# ============================================
# FUNCIONES DE ELIMINACIÓN (Uso con precaución)
# ============================================

async def delete_drawer_by_user_id(user_id: str) -> bool:
    """
    Elimina el cajón de un usuario.
    
    ⚠️ USAR CON PRECAUCIÓN: Esta acción es irreversible.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        True si se eliminó correctamente
    """
    try:
        result = await collection.delete_one({"user_id": user_id})
        
        if result.deleted_count > 0:
            logger.warning(f"⚠️  Cajón eliminado: user_id {user_id}")
            return True
        else:
            logger.info(f"ℹ️  No se encontró cajón para eliminar (user_id: {user_id})")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error eliminando cajón para user_id {user_id}: {e}")
        return False


# ============================================
# FUNCIONES DE UTILIDAD
# ============================================

async def get_drawer_stats(user_id: str) -> Optional[Dict[str, Any]]:
    """
    Obtiene estadísticas del cajón de un usuario.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        Dict con estadísticas o None si no existe
    
    Example:
        stats = await get_drawer_stats("1762...")
        print(f"Cuestionarios: {stats['questionnaires_count']}")
        print(f"Training plans: {stats['training_plans_count']}")
    """
    try:
        drawer = await get_drawer_by_user_id(user_id)
        
        if not drawer:
            return None
        
        return {
            "drawer_id": drawer.id,
            "user_id": drawer.user_id,
            "created_at": drawer.created_at,
            "updated_at": drawer.updated_at,
            "questionnaires_count": len(drawer.services.shared_questionnaires),
            "training_plans_count": len(drawer.services.training.plans),
            "training_snapshots_count": len(drawer.services.training.snapshots),
            "nutrition_plans_count": len(drawer.services.nutrition.plans),
            "nutrition_snapshots_count": len(drawer.services.nutrition.snapshots),
            "active_training_plan": drawer.services.training.active_plan_id,
            "active_nutrition_plan": drawer.services.nutrition.active_plan_id
        }
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo estadísticas para user_id {user_id}: {e}")
        return None
