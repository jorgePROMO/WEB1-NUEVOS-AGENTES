"""
Training Plan Models - Request/Response para endpoint /api/training-plan

Este módulo define los modelos Pydantic para el nuevo endpoint que llama
al workflow de Platform (E1-E7.5) y devuelve planes de entrenamiento.

Referencia: Endpoint /api/training-plan
Fecha: Noviembre 2025
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Union, Optional
from datetime import datetime


# ============================================
# REQUEST MODELS
# ============================================

class QuestionnaireSubmission(BaseModel):
    """
    Cuestionario de usuario que se envía al workflow de Platform.
    
    Este modelo representa un cuestionario completo con todas las respuestas
    del formulario de entrenamiento.
    """
    submission_id: str = Field(
        ...,
        description="ID único de esta submission"
    )
    source: str = Field(
        ...,
        description="Origen del cuestionario: 'initial' o 'follow_up'"
    )
    submitted_at: str = Field(
        ...,
        description="Fecha de envío en formato ISO8601"
    )
    payload: Dict[str, Any] = Field(
        ...,
        description="Respuestas completas del formulario (objeto plano con ~100 preguntas)"
    )


class TrainingPlanRequest(BaseModel):
    """
    Request para el endpoint POST /api/training-plan
    """
    questionnaire_submission: QuestionnaireSubmission = Field(
        ...,
        description="Cuestionario completo del usuario"
    )


# ============================================
# RESPONSE MODELS
# ============================================

class Exercise(BaseModel):
    """
    Ejercicio individual dentro de un bloque de entrenamiento.
    """
    order: int = Field(..., description="Orden del ejercicio en el bloque")
    db_id: str = Field(..., description="ID del ejercicio en la BD de ejercicios")
    name: str = Field(..., description="Nombre del ejercicio")
    primary_group: str = Field(..., description="Grupo muscular primario")
    secondary_group: str = Field(..., description="Grupo muscular secundario")
    series: Union[int, str] = Field(..., description="Número de series")
    reps: str = Field(..., description="Rango de repeticiones (ej: '10-12')")
    rpe: Union[int, str] = Field(..., description="RPE (Rate of Perceived Exertion)")
    video_url: str = Field(..., description="URL del video del ejercicio")


class Block(BaseModel):
    """
    Bloque de ejercicios dentro de una sesión.
    """
    id: str = Field(..., description="ID del bloque (ej: 'A', 'B', 'C')")
    primary_muscles: List[str] = Field(..., description="Músculos primarios del bloque")
    secondary_muscles: List[str] = Field(..., description="Músculos secundarios del bloque")
    exercises: List[Exercise] = Field(..., description="Lista de ejercicios del bloque")


class Session(BaseModel):
    """
    Sesión de entrenamiento completa.
    """
    id: str = Field(..., description="ID de la sesión (ej: 'D1', 'D2')")
    name: str = Field(..., description="Nombre de la sesión")
    focus: List[str] = Field(..., description="Enfoque de la sesión (ej: ['upper_body', 'push_focus'])")
    blocks: List[Block] = Field(..., description="Bloques de ejercicios de la sesión")
    session_notes: List[str] = Field(..., description="Notas específicas de la sesión")


class ClientTrainingProgramEnriched(BaseModel):
    """
    Programa de entrenamiento completo y enriquecido.
    
    Este es el modelo principal que devuelve el workflow de Platform (E1-E7.5).
    """
    title: str = Field(..., description="Título del programa")
    summary: str = Field(..., description="Resumen del programa")
    goal: str = Field(..., description="Objetivo principal del programa")
    training_type: str = Field(..., description="Tipo de entrenamiento (ej: 'upper_lower')")
    days_per_week: int = Field(..., description="Días de entrenamiento por semana")
    session_duration_min: int = Field(..., description="Duración de cada sesión en minutos")
    weeks: int = Field(..., description="Duración del programa en semanas")
    sessions: List[Session] = Field(..., description="Lista de sesiones del programa")
    general_notes: List[str] = Field(..., description="Notas generales del programa")


class TrainingPlanResponse(BaseModel):
    """
    Response del endpoint POST /api/training-plan
    """
    client_training_program_enriched: ClientTrainingProgramEnriched = Field(
        ...,
        description="Programa de entrenamiento completo"
    )


# ============================================
# VALIDATION HELPERS
# ============================================

def validate_questionnaire_submission(qs: QuestionnaireSubmission) -> tuple[bool, list[str]]:
    """
    Valida que un QuestionnaireSubmission tenga la estructura mínima necesaria.
    
    Args:
        qs: QuestionnaireSubmission a validar
    
    Returns:
        Tuple (es_valido, lista_de_errores)
    """
    errors = []
    
    # Validar source
    if qs.source not in ["initial", "follow_up"]:
        errors.append("source debe ser 'initial' o 'follow_up'")
    
    # Validar submission_id
    if not qs.submission_id or not qs.submission_id.strip():
        errors.append("submission_id no puede estar vacío")
    
    # Validar submitted_at (debe ser ISO8601)
    try:
        datetime.fromisoformat(qs.submitted_at.replace('Z', '+00:00'))
    except Exception:
        errors.append("submitted_at debe ser una fecha válida en formato ISO8601")
    
    # Validar que payload no esté vacío
    if not qs.payload or not isinstance(qs.payload, dict):
        errors.append("payload debe ser un objeto no vacío")
    
    return (len(errors) == 0, errors)
