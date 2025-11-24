"""
EDN360 Snapshot Repository - Acceso a datos de snapshots

Este módulo maneja todas las operaciones de base de datos para edn360_snapshots:
- Crear snapshots (INMUTABLES - solo INSERT, no UPDATE)
- Consultar snapshots por usuario, ID, etc.
- Obtener último snapshot de un usuario

Colección: edn360_snapshots (BD: edn360_app)

IMPORTANTE:
Los snapshots son INMUTABLES. Este repository NO tiene funciones de UPDATE.

Referencia: FASE 3 - Nuevo Orquestador EDN360 v1
Fecha: Enero 2025
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient

from edn360_models.edn360_snapshot import EDN360Snapshot

# Configuración
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
MONGO_EDN360_APP_DB_NAME = os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')

# Cliente MongoDB para BD EDN360_APP
client_edn360 = AsyncIOMotorClient(MONGO_URL)
db_edn360 = client_edn360[MONGO_EDN360_APP_DB_NAME]

# Colección de snapshots
snapshots_collection = db_edn360.edn360_snapshots

# Logger
logger = logging.getLogger(__name__)


# ============================================
# INICIALIZACIÓN DE ÍNDICES
# ============================================

async def ensure_snapshot_indexes():
    """
    Crea los índices necesarios en la colección edn360_snapshots.
    
    Índices:
    - user_id: Para consultas por usuario
    - created_at: Para consultas cronológicas (descendente)
    - status: Para filtrar success/failed
    
    Se ejecuta automáticamente al arrancar el servidor.
    """
    try:
        # Índice por user_id
        await snapshots_collection.create_index("user_id")
        logger.info("✅ Índice creado: edn360_snapshots.user_id")
        
        # Índice por created_at (descendente para obtener más recientes primero)
        await snapshots_collection.create_index([("created_at", -1)])
        logger.info("✅ Índice creado: edn360_snapshots.created_at")
        
        # Índice por status
        await snapshots_collection.create_index("status")
        logger.info("✅ Índice creado: edn360_snapshots.status")
        
        logger.info("✅ Índices de edn360_snapshots verificados")
    
    except Exception as e:
        logger.error(f"❌ Error creando índices de edn360_snapshots: {e}")
        raise


# ============================================
# CREATE OPERATIONS
# ============================================

async def create_snapshot(
    user_id: str,
    edn360_input: Dict[str, Any],
    workflow_name: str,
    workflow_response: Dict[str, Any],
    status: str,
    error_message: Optional[str] = None,
    version: str = "1.0.0"
) -> EDN360Snapshot:
    """
    Crea un nuevo snapshot en la BD.
    
    Este es el método principal para guardar ejecuciones del workflow.
    Los snapshots son INMUTABLES: una vez creados, NO se modifican.
    
    Args:
        user_id: ID del usuario
        edn360_input: EDN360Input completo (dict)
        workflow_name: Nombre del workflow ejecutado
        workflow_response: Respuesta del workflow (dict)
        status: Estado ("success" | "failed")
        error_message: Mensaje de error (solo si status="failed")
        version: Versión del sistema (default: "1.0.0")
    
    Returns:
        EDN360Snapshot creado
    
    Raises:
        Exception: Si hay error al insertar en BD
    
    Example:
        snapshot = await create_snapshot(
            user_id="1762976907472415",
            edn360_input={"user_profile": {...}, "questionnaires": [...]},
            workflow_name="edn360_full_plan_v1",
            workflow_response={"training_plan": {...}, "nutrition_plan": {...}},
            status="success"
        )
        print(f"Snapshot creado: {snapshot.snapshot_id}")
    """
    try:
        # Crear el modelo EDN360Snapshot
        snapshot = EDN360Snapshot(
            user_id=user_id,
            input=edn360_input,
            workflow_name=workflow_name,
            workflow_response=workflow_response,
            status=status,
            error_message=error_message,
            version=version
        )
        
        # Serializar a dict para MongoDB
        snapshot_dict = snapshot.dict(by_alias=True)
        
        # Insertar en la BD
        await snapshots_collection.insert_one(snapshot_dict)
        
        logger.info(
            f"✅ Snapshot creado: {snapshot.snapshot_id} | "
            f"user_id: {user_id} | status: {status} | workflow: {workflow_name}"
        )
        
        return snapshot
    
    except Exception as e:
        logger.error(f"❌ Error creando snapshot para user_id {user_id}: {e}")
        raise


# ============================================
# READ OPERATIONS
# ============================================

async def get_snapshot_by_id(snapshot_id: str) -> Optional[EDN360Snapshot]:
    """
    Obtiene un snapshot por su ID.
    
    Args:
        snapshot_id: ID del snapshot
    
    Returns:
        EDN360Snapshot o None si no existe
    
    Example:
        snapshot = await get_snapshot_by_id("uuid-123-456")
        if snapshot:
            print(f"Status: {snapshot.status}")
    """
    try:
        snapshot_doc = await snapshots_collection.find_one({"_id": snapshot_id})
        
        if not snapshot_doc:
            logger.warning(f"⚠️  Snapshot {snapshot_id} no encontrado")
            return None
        
        # Convertir a modelo Pydantic
        snapshot = EDN360Snapshot(**snapshot_doc)
        
        return snapshot
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo snapshot {snapshot_id}: {e}")
        return None


async def get_snapshots_by_user(
    user_id: str,
    limit: Optional[int] = None,
    status_filter: Optional[str] = None
) -> List[EDN360Snapshot]:
    """
    Obtiene todos los snapshots de un usuario.
    
    Args:
        user_id: ID del usuario
        limit: Límite de resultados (opcional)
        status_filter: Filtrar por status ("success" | "failed") (opcional)
    
    Returns:
        Lista de EDN360Snapshot ordenados por created_at (descendente)
    
    Example:
        # Todos los snapshots del usuario
        snapshots = await get_snapshots_by_user("1762976907472415")
        
        # Solo los últimos 5 exitosos
        snapshots = await get_snapshots_by_user(
            "1762976907472415",
            limit=5,
            status_filter="success"
        )
    """
    try:
        # Construir query
        query = {"user_id": user_id}
        
        if status_filter:
            query["status"] = status_filter
        
        # Ejecutar query (ordenar por created_at descendente)
        cursor = snapshots_collection.find(query).sort("created_at", -1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        # Convertir a lista de modelos Pydantic
        snapshots = []
        async for doc in cursor:
            snapshot = EDN360Snapshot(**doc)
            snapshots.append(snapshot)
        
        logger.info(
            f"📋 Obtenidos {len(snapshots)} snapshot(s) para user_id: {user_id}"
        )
        
        return snapshots
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo snapshots para user_id {user_id}: {e}")
        return []


async def get_latest_snapshot_for_user(user_id: str) -> Optional[EDN360Snapshot]:
    """
    Obtiene el snapshot más reciente de un usuario.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        EDN360Snapshot más reciente o None si no hay snapshots
    
    Example:
        latest = await get_latest_snapshot_for_user("1762976907472415")
        if latest:
            print(f"Último snapshot: {latest.created_at}")
    """
    try:
        snapshot_doc = await snapshots_collection.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        if not snapshot_doc:
            logger.info(f"ℹ️  No hay snapshots para user_id: {user_id}")
            return None
        
        snapshot = EDN360Snapshot(**snapshot_doc)
        
        return snapshot
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo último snapshot para user_id {user_id}: {e}")
        return None


async def count_snapshots_by_user(user_id: str, status_filter: Optional[str] = None) -> int:
    """
    Cuenta el número total de snapshots de un usuario.
    
    Args:
        user_id: ID del usuario
        status_filter: Filtrar por status ("success" | "failed") (opcional)
    
    Returns:
        Número de snapshots
    
    Example:
        total = await count_snapshots_by_user("1762976907472415")
        success_count = await count_snapshots_by_user("1762976907472415", "success")
        failed_count = await count_snapshots_by_user("1762976907472415", "failed")
    """
    try:
        query = {"user_id": user_id}
        
        if status_filter:
            query["status"] = status_filter
        
        count = await snapshots_collection.count_documents(query)
        
        return count
    
    except Exception as e:
        logger.error(f"❌ Error contando snapshots para user_id {user_id}: {e}")
        return 0


# ============================================
# HELPERS ADICIONALES
# ============================================

async def get_snapshot_summary_for_user(user_id: str) -> Dict[str, Any]:
    """
    Obtiene un resumen de los snapshots de un usuario sin cargar payloads completos.
    
    Args:
        user_id: ID del usuario
    
    Returns:
        Dict con estadísticas y último snapshot
    
    Example:
        summary = await get_snapshot_summary_for_user("1762976907472415")
        print(f"Total: {summary['total_count']}")
        print(f"Éxitos: {summary['success_count']}")
        print(f"Fallos: {summary['failed_count']}")
    """
    try:
        total_count = await count_snapshots_by_user(user_id)
        success_count = await count_snapshots_by_user(user_id, status_filter="success")
        failed_count = await count_snapshots_by_user(user_id, status_filter="failed")
        
        latest_snapshot = await get_latest_snapshot_for_user(user_id)
        
        return {
            "user_id": user_id,
            "total_count": total_count,
            "success_count": success_count,
            "failed_count": failed_count,
            "latest_snapshot": latest_snapshot.get_summary() if latest_snapshot else None
        }
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo resumen para user_id {user_id}: {e}")
        return {
            "user_id": user_id,
            "error": str(e)
        }
