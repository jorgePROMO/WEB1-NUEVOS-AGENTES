"""
EDN360 Input Model - Contrato de entrada para Workflows

Este modelo define la estructura estándar que usaremos para llamar
a los Workflows de OpenAI (E1-E9, N0-N8).

Es el "contrato" entre:
- El sistema EDN360 (backend)
- Los Workflows de OpenAI

Referencia: FASE 2 - Definición EDN360_INPUT
Fecha: Enero 2025
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================
# USER PROFILE
# ============================================

class EDN360UserProfile(BaseModel):
    """
    Perfil básico del usuario.
    
    Fuente: BD Web (test_database.users)
    
    Contiene información esencial del usuario que puede ser útil
    como contexto para los Workflows de IA.
    """
    user_id: str = Field(
        ...,
        description="ID único del usuario en BD Web"
    )
    name: Optional[str] = Field(
        None,
        description="Nombre completo del usuario"
    )
    email: Optional[str] = Field(
        None,
        description="Email del usuario"
    )
    phone: Optional[str] = Field(
        None,
        description="Teléfono del usuario"
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Fecha de creación de la cuenta"
    )
    subscription_plan: Optional[str] = Field(
        None,
        description="Plan de suscripción actual (team, pro, etc.)"
    )
    subscription_status: Optional[str] = Field(
        None,
        description="Estado del pago (verified, pending, etc.)"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


# ============================================
# QUESTIONNAIRE
# ============================================

class EDN360Questionnaire(BaseModel):
    """
    Cuestionario individual (inicial o followup).
    
    Fuente: BD EDN360_APP (edn360_app.client_drawers.services.shared_questionnaires)
    
    Cada cuestionario contiene:
    - submission_id: ID del cuestionario en BD Web
    - submitted_at: Fecha de envío
    - source: Tipo de cuestionario ("nutrition_initial" | "followup")
    - payload: Contenido completo del cuestionario
    """
    submission_id: str = Field(
        ...,
        description="ID del cuestionario en BD Web"
    )
    submitted_at: datetime = Field(
        ...,
        description="Fecha y hora de envío del cuestionario"
    )
    source: str = Field(
        ...,
        description="Tipo de cuestionario: 'nutrition_initial' | 'followup'"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Contenido completo del cuestionario (raw_payload de BD Web)"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============================================
# EDN360 INPUT (Modelo Raíz)
# ============================================

class EDN360Input(BaseModel):
    """
    EDN360 Input - Contrato estándar para Workflows de OpenAI.
    
    Este es el modelo raíz que se usará como entrada para:
    - Workflows de entrenamiento (E1-E9)
    - Workflows de nutrición (N0-N8)
    
    Estructura:
    - user_profile: Perfil básico del usuario
    - questionnaires: Lista de cuestionarios ordenados cronológicamente
    
    Fuentes de datos:
    - user_profile: BD Web (test_database.users)
    - questionnaires: BD EDN360_APP (edn360_app.client_drawers)
    
    Orden de cuestionarios:
    - Ordenados por submitted_at ASCENDENTE (más antiguo → más reciente)
    - Primer elemento: Cuestionario inicial
    - Siguientes: Followups mensuales
    
    Uso futuro:
    - Input para OpenAI Workflows
    - Generación de ClientContext (E1-E9, N0-N8)
    - Creación de snapshots inmutables
    
    Referencia: DOCUMENTO_2_VFINAL_TO_BE_CLIENT_DRAWER.md
    """
    user_profile: EDN360UserProfile = Field(
        ...,
        description="Perfil básico del usuario"
    )
    questionnaires: List[EDN360Questionnaire] = Field(
        ...,
        description="Lista de cuestionarios ordenados cronológicamente (ascendente)"
    )
    
    # Metadatos opcionales
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Fecha y hora en que se generó este EDN360Input"
    )
    version: str = Field(
        default="1.0.0",
        description="Versión del modelo EDN360Input"
    )
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def get_initial_questionnaire(self) -> Optional[EDN360Questionnaire]:
        """
        Obtiene el cuestionario inicial (primer cuestionario).
        
        Returns:
            EDN360Questionnaire con source="nutrition_initial" o None
        """
        for q in self.questionnaires:
            if q.source == "nutrition_initial":
                return q
        return None
    
    def get_followup_questionnaires(self) -> List[EDN360Questionnaire]:
        """
        Obtiene todos los cuestionarios de seguimiento.
        
        Returns:
            Lista de EDN360Questionnaire con source="followup"
        """
        return [q for q in self.questionnaires if q.source == "followup"]
    
    def get_latest_questionnaire(self) -> Optional[EDN360Questionnaire]:
        """
        Obtiene el cuestionario más reciente.
        
        Returns:
            EDN360Questionnaire más reciente o None si no hay cuestionarios
        """
        if not self.questionnaires:
            return None
        return self.questionnaires[-1]  # Último elemento (más reciente)
    
    def questionnaire_count(self) -> int:
        """
        Cuenta el total de cuestionarios.
        
        Returns:
            Número total de cuestionarios
        """
        return len(self.questionnaires)
    
    def has_followups(self) -> bool:
        """
        Verifica si hay cuestionarios de seguimiento.
        
        Returns:
            True si hay al menos 1 followup
        """
        return any(q.source == "followup" for q in self.questionnaires)


# ============================================
# EXCEPTIONS
# ============================================

class EDN360NoDrawerError(Exception):
    """
    Error cuando un usuario no tiene client_drawer.
    
    Esto puede ocurrir si:
    - El usuario existe en BD Web pero nunca ha completado un cuestionario
    - El dual-write no se había activado cuando el usuario envió su cuestionario
    """
    pass


class EDN360NoQuestionnaireError(Exception):
    """
    Error cuando un usuario tiene drawer pero sin cuestionarios.
    
    Esto puede ocurrir si:
    - El drawer se creó pero no se añadió ningún cuestionario (bug)
    - Los cuestionarios se eliminaron manualmente
    """
    pass


# ============================================
# HELPERS Y UTILIDADES
# ============================================

def validate_edn360_input(edn360_input: EDN360Input) -> tuple[bool, list[str]]:
    """
    Valida un EDN360Input completo.
    
    Args:
        edn360_input: EDN360Input a validar
    
    Returns:
        Tuple (es_valido, lista_de_errores)
    """
    errors = []
    
    # Validar user_profile
    if not edn360_input.user_profile.user_id:
        errors.append("user_profile.user_id es obligatorio")
    
    # Validar questionnaires
    if not edn360_input.questionnaires:
        errors.append("questionnaires no puede estar vacío")
    
    # Validar que hay al menos 1 cuestionario inicial
    initial_count = sum(1 for q in edn360_input.questionnaires if q.source == "nutrition_initial")
    if initial_count == 0:
        errors.append("Debe haber al menos 1 cuestionario con source='nutrition_initial'")
    elif initial_count > 1:
        errors.append(f"Solo debe haber 1 cuestionario inicial, encontrados {initial_count}")
    
    # Validar orden cronológico
    dates = [q.submitted_at for q in edn360_input.questionnaires]
    if dates != sorted(dates):
        errors.append("Los cuestionarios deben estar ordenados cronológicamente (ascendente)")
    
    return (len(errors) == 0, errors)
