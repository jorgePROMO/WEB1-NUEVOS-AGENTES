"""
ClientDrawer Model - TO-BE Architecture (FASE 0)

Modelo central de la nueva arquitectura EDN360.
Un cajón único por cliente donde vive TODA su información.

Referencia: DOCUMENTO_2_VFINAL_TO_BE_CLIENT_DRAWER.md

Versión: 1.0.0 (FASE 0 - Base mínima)
Fecha: Enero 2025
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone


# ============================================
# SHARED QUESTIONNAIRES
# ============================================

class SharedQuestionnaire(BaseModel):
    """
    Cuestionario compartido (inicial o followup).
    
    En EDN360 hay UN SOLO cuestionario que cubre tanto training como nutrition.
    Este modelo almacena la referencia al cuestionario y metadatos.
    """
    submission_id: str = Field(
        ...,
        description="ID del cuestionario en la BD Web (nutrition_questionnaire_submissions o follow_up_submissions)"
    )
    submitted_at: datetime = Field(
        ...,
        description="Fecha de envío del cuestionario"
    )
    source: str = Field(
        ...,
        description="Tipo de cuestionario: 'initial' (primer cuestionario) o 'followup' (seguimiento mensual)"
    )
    raw_payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Payload completo del cuestionario (opcional, puede estar en BD Web)"
    )
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================
# TRAINING MODULE
# ============================================

class TrainingModule(BaseModel):
    """
    Módulo de entrenamiento del cliente.
    
    Contiene:
    - active_plan_id: Plan activo actual
    - plans: Lista de planes históricos (referencias)
    - snapshots: ClientContext históricos (outputs E1-E9)
    """
    active_plan_id: Optional[str] = Field(
        None,
        description="ID del plan de entrenamiento activo actual (referencia a training_plans)"
    )
    plans: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de planes de entrenamiento históricos. Estructura: {plan_id, version, snapshot_id, generated_at, status}"
    )
    snapshots: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Snapshots de ClientContext (outputs E1-E9). Cada snapshot es inmutable y versionado."
    )
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================
# NUTRITION MODULE
# ============================================

class NutritionModule(BaseModel):
    """
    Módulo de nutrición del cliente.
    
    Contiene:
    - active_plan_id: Plan activo actual
    - plans: Lista de planes históricos (referencias)
    - snapshots: ClientContext históricos (outputs N0-N8)
    """
    active_plan_id: Optional[str] = Field(
        None,
        description="ID del plan de nutrición activo actual (referencia a nutrition_plans)"
    )
    plans: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Lista de planes de nutrición históricos. Estructura: {plan_id, version, snapshot_id, generated_at, status}"
    )
    snapshots: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Snapshots de ClientContext (outputs N0-N8). Cada snapshot es inmutable y versionado."
    )
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================
# SERVICES (Contenedor de módulos)
# ============================================

class Services(BaseModel):
    """
    Servicios del cliente.
    
    Contiene:
    - shared_questionnaires: Cuestionarios únicos EDN360 (inicial + followups)
    - training: Módulo de entrenamiento
    - nutrition: Módulo de nutrición
    
    Nota: Futuro - psychology, rehabilitation, etc.
    """
    shared_questionnaires: List[SharedQuestionnaire] = Field(
        default_factory=list,
        description="Lista de cuestionarios del cliente (inicial + followups). Orden cronológico."
    )
    training: TrainingModule = Field(
        default_factory=TrainingModule,
        description="Módulo de entrenamiento (planes, snapshots)"
    )
    nutrition: NutritionModule = Field(
        default_factory=NutritionModule,
        description="Módulo de nutrición (planes, snapshots)"
    )
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


# ============================================
# CLIENT DRAWER (Modelo Principal)
# ============================================

class ClientDrawer(BaseModel):
    """
    Client Drawer - Cajón único del cliente (TO-BE Architecture).
    
    Principios fundamentales:
    1. Un cajón único por cliente (user_id)
    2. Fuente única de verdad para datos EDN360
    3. Versionado completo mediante snapshots
    4. Arquitectura modular (training, nutrition, future services)
    
    Estructura:
    - user_id: Referencia al usuario en BD Web
    - services: Módulos de servicios (training, nutrition)
    - created_at: Fecha de creación del cajón
    - updated_at: Última actualización
    
    Referencia: DOCUMENTO_2_VFINAL_TO_BE_CLIENT_DRAWER.md
    """
    
    # ID del documento (MongoDB _id)
    id: Optional[str] = Field(
        None,
        alias="_id",
        description="ID único del drawer en MongoDB (client_{user_id})"
    )
    
    # Referencia al usuario en BD Web
    user_id: str = Field(
        ...,
        description="ID del usuario en la BD Web (users collection)"
    )
    
    # Servicios del cliente
    services: Services = Field(
        default_factory=Services,
        description="Módulos de servicios del cliente (training, nutrition)"
    )
    
    # Metadatos temporales
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Fecha de creación del cajón"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Última actualización del cajón"
    )
    
    class Config:
        populate_by_name = True  # Permite usar tanto "id" como "_id"
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def dict(self, *args, **kwargs):
        """
        Serializa el modelo a diccionario.
        Convierte datetime a ISO string para MongoDB.
        """
        data = super().dict(*args, **kwargs)
        
        # Convertir fechas a ISO string
        if isinstance(data.get('created_at'), datetime):
            data['created_at'] = data['created_at'].isoformat()
        if isinstance(data.get('updated_at'), datetime):
            data['updated_at'] = data['updated_at'].isoformat()
        
        return data
    
    @classmethod
    def create_empty_for_user(cls, user_id: str) -> "ClientDrawer":
        """
        Crea un cajón vacío para un nuevo usuario.
        
        Args:
            user_id: ID del usuario en BD Web
        
        Returns:
            ClientDrawer vacío con estructura inicial
        """
        return cls(
            id=f"client_{user_id}",
            user_id=user_id,
            services=Services(
                shared_questionnaires=[],
                training=TrainingModule(),
                nutrition=NutritionModule()
            ),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )


# ============================================
# HELPERS Y UTILIDADES
# ============================================

def validate_drawer_structure(drawer: ClientDrawer) -> tuple[bool, list[str]]:
    """
    Valida la estructura de un ClientDrawer.
    
    Args:
        drawer: ClientDrawer a validar
    
    Returns:
        Tuple (es_valido, lista_de_errores)
    """
    errors = []
    
    # Validar user_id
    if not drawer.user_id:
        errors.append("user_id es obligatorio")
    
    # Validar ID del drawer
    if drawer.id and not drawer.id.startswith("client_"):
        errors.append("id debe comenzar con 'client_'")
    
    # Validar fechas
    if drawer.created_at > drawer.updated_at:
        errors.append("created_at no puede ser mayor que updated_at")
    
    # Validar cuestionarios
    for i, quest in enumerate(drawer.services.shared_questionnaires):
        if not quest.submission_id:
            errors.append(f"Cuestionario {i}: submission_id es obligatorio")
        if quest.source not in ["initial", "followup"]:
            errors.append(f"Cuestionario {i}: source debe ser 'initial' o 'followup'")
    
    return (len(errors) == 0, errors)


def get_latest_questionnaire(drawer: ClientDrawer) -> Optional[SharedQuestionnaire]:
    """
    Obtiene el cuestionario más reciente del cliente.
    
    Args:
        drawer: ClientDrawer
    
    Returns:
        SharedQuestionnaire más reciente o None si no hay cuestionarios
    """
    if not drawer.services.shared_questionnaires:
        return None
    
    return max(
        drawer.services.shared_questionnaires,
        key=lambda q: q.submitted_at
    )


def get_active_plans(drawer: ClientDrawer) -> Dict[str, Optional[str]]:
    """
    Obtiene los IDs de planes activos del cliente.
    
    Args:
        drawer: ClientDrawer
    
    Returns:
        Dict con training_plan_id y nutrition_plan_id
    """
    return {
        "training_plan_id": drawer.services.training.active_plan_id,
        "nutrition_plan_id": drawer.services.nutrition.active_plan_id
    }
