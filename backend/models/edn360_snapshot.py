"""
EDN360 Snapshot Model - Log técnico inmutable de ejecuciones de Workflow

Este modelo almacena cada ejecución del Workflow EDN360 como un snapshot inmutable:
- El EDN360Input enviado (input completo)
- La respuesta cruda del Workflow de OpenAI (workflow_response)
- Estado (success/failed) y metadatos

Los snapshots son INMUTABLES: una vez creados, NO se modifican.

Propósito:
- Trazabilidad completa de todas las ejecuciones
- Debugging y auditoría
- Histórico de llamadas al Workflow

Colección: edn360_snapshots (BD: edn360_app)

Referencia: FASE 3 - Nuevo Orquestador EDN360 v1
Fecha: Enero 2025
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid


class EDN360Snapshot(BaseModel):
    """
    EDN360 Snapshot - Log técnico inmutable de una ejecución de Workflow.
    
    Estructura:
    - snapshot_id: ID único del snapshot (UUID)
    - user_id: ID del usuario para quien se ejecutó el workflow
    - created_at: Timestamp de creación del snapshot
    - version: Versión del sistema (semver)
    - input: EDN360Input completo enviado al workflow (dict)
    - workflow_name: Nombre lógico del workflow ejecutado
    - workflow_response: Respuesta cruda del workflow de OpenAI (dict)
    - status: Estado de la ejecución ("success" | "failed")
    - error_message: Mensaje de error si status="failed"
    
    Índices MongoDB:
    - user_id (para consultas por usuario)
    - created_at (para consultas cronológicas)
    - status (para filtrar success/failed)
    
    INMUTABILIDAD:
    Los snapshots NO se modifican después de su creación.
    Cada nueva ejecución crea un nuevo snapshot.
    """
    
    # ID del snapshot (usamos UUID para facilidad de serialización)
    snapshot_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="ID único del snapshot (UUID)",
        alias="_id"
    )
    
    # Usuario para quien se ejecutó el workflow
    user_id: str = Field(
        ...,
        description="ID del usuario en BD Web (users collection)"
    )
    
    # Timestamp de creación
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha y hora de creación del snapshot (UTC)"
    )
    
    # Versión del sistema
    version: str = Field(
        default="1.0.0",
        description="Versión del sistema EDN360 (semver)"
    )
    
    # Input enviado al workflow (EDN360Input serializado)
    input: Dict[str, Any] = Field(
        ...,
        description="EDN360Input completo enviado al workflow (dict/json)"
    )
    
    # Nombre del workflow ejecutado
    workflow_name: str = Field(
        ...,
        description="Nombre lógico del workflow ejecutado (ej: 'edn360_full_plan_v1')"
    )
    
    # Respuesta del workflow (cruda, tal cual la devuelve OpenAI)
    workflow_response: Dict[str, Any] = Field(
        ...,
        description="Respuesta cruda del workflow de OpenAI (dict/json)"
    )
    
    # Estado de la ejecución
    status: str = Field(
        ...,
        description="Estado de la ejecución: 'success' | 'failed'"
    )
    
    # Mensaje de error (solo si status="failed")
    error_message: Optional[str] = Field(
        None,
        description="Mensaje de error si la ejecución falló"
    )
    
    class Config:
        populate_by_name = True  # Permite usar tanto "snapshot_id" como "_id"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def dict(self, *args, **kwargs):
        """
        Serializa el modelo a diccionario.
        Convierte datetime a ISO string para MongoDB.
        """
        data = super().dict(*args, **kwargs)
        
        # Convertir created_at a ISO string
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        
        return data
    
    def is_success(self) -> bool:
        """Verifica si la ejecución fue exitosa."""
        return self.status == "success"
    
    def is_failed(self) -> bool:
        """Verifica si la ejecución falló."""
        return self.status == "failed"
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Devuelve un resumen ligero del snapshot (sin los payloads completos).
        
        Útil para mostrar en UI sin cargar JSONs gigantes.
        
        Returns:
            Dict con campos principales (snapshot_id, user_id, status, etc.)
        """
        return {
            "snapshot_id": self.snapshot_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "version": self.version,
            "workflow_name": self.workflow_name,
            "status": self.status,
            "error_message": self.error_message,
            "has_input": bool(self.input),
            "has_response": bool(self.workflow_response)
        }


# ============================================
# HELPERS Y UTILIDADES
# ============================================

def validate_snapshot_status(status: str) -> bool:
    """
    Valida que el status sea un valor permitido.
    
    Args:
        status: Estado a validar
    
    Returns:
        True si el status es válido
    """
    return status in ["success", "failed"]


def create_success_snapshot(
    user_id: str,
    edn360_input: Dict[str, Any],
    workflow_name: str,
    workflow_response: Dict[str, Any],
    version: str = "1.0.0"
) -> EDN360Snapshot:
    """
    Helper para crear un snapshot de ejecución exitosa.
    
    Args:
        user_id: ID del usuario
        edn360_input: EDN360Input completo (dict)
        workflow_name: Nombre del workflow ejecutado
        workflow_response: Respuesta del workflow
        version: Versión del sistema
    
    Returns:
        EDN360Snapshot con status="success"
    """
    return EDN360Snapshot(
        user_id=user_id,
        input=edn360_input,
        workflow_name=workflow_name,
        workflow_response=workflow_response,
        status="success",
        version=version
    )


def create_failed_snapshot(
    user_id: str,
    edn360_input: Dict[str, Any],
    workflow_name: str,
    error_message: str,
    version: str = "1.0.0"
) -> EDN360Snapshot:
    """
    Helper para crear un snapshot de ejecución fallida.
    
    Args:
        user_id: ID del usuario
        edn360_input: EDN360Input completo (dict)
        workflow_name: Nombre del workflow ejecutado
        error_message: Descripción del error
        version: Versión del sistema
    
    Returns:
        EDN360Snapshot con status="failed"
    """
    return EDN360Snapshot(
        user_id=user_id,
        input=edn360_input,
        workflow_name=workflow_name,
        workflow_response={},  # Respuesta vacía si falló
        status="failed",
        error_message=error_message,
        version=version
    )
