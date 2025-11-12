"""
Modelos de datos para E.D.N.360
Define las estructuras de datos utilizadas por el sistema
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class PlanStatus(str, Enum):
    """Estados posibles de un plan"""
    PENDING = "pending"  # Cuestionario recibido, esperando generación
    GENERATING = "generating"  # Agentes trabajando
    DRAFT = "draft"  # Plan generado, pendiente de revisión admin
    APPROVED = "approved"  # Plan aprobado por admin
    SENT = "sent"  # Plan enviado al cliente
    ARCHIVED = "archived"  # Plan archivado


class PlanType(str, Enum):
    """Tipos de plan"""
    INITIAL_TRAINING = "initial_training"
    INITIAL_NUTRITION = "initial_nutrition"
    INITIAL_COMPLETE = "initial_complete"  # Training + Nutrition
    FOLLOWUP_TRAINING = "followup_training"
    FOLLOWUP_NUTRITION = "followup_nutrition"
    FOLLOWUP_COMPLETE = "followup_complete"


class AgentStatus(str, Enum):
    """Estados de ejecución de un agente"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"


# ==================== AGENT EXECUTION TRACKING ====================

class AgentExecution(BaseModel):
    """Registro de ejecución de un agente"""
    agent_id: str  # E1, E2, N0, etc.
    agent_name: str
    status: AgentStatus = AgentStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    tokens_used: Optional[int] = None


# ==================== QUESTIONNAIRE DATA ====================

class QuestionnaireData(BaseModel):
    """Datos del cuestionario inicial o de seguimiento"""
    questionnaire_id: str
    user_id: str
    questionnaire_type: str  # "initial" o "followup"
    submitted_at: datetime
    data: Dict[str, Any]  # Todas las respuestas del formulario


# ==================== PLAN COMPONENTS ====================

class TrainingPlan(BaseModel):
    """Plan de entrenamiento generado"""
    plan_id: str
    version: int = 1
    created_at: datetime
    
    # Outputs de los agentes de entrenamiento
    e1_perfil_tecnico: Optional[Dict[str, Any]] = None
    e2_capacidad_riesgo: Optional[Dict[str, Any]] = None
    e3_historial_adaptacion: Optional[Dict[str, Any]] = None
    e4_programa_mesociclo: Optional[Dict[str, Any]] = None
    e5_microciclos_sesiones: Optional[Dict[str, Any]] = None
    e6_clinico_preventivo: Optional[Dict[str, Any]] = None
    e7_carga_recuperacion: Optional[Dict[str, Any]] = None
    e8_auditoria_tecnica: Optional[Dict[str, Any]] = None
    e9_bridge_nutricion: Optional[Dict[str, Any]] = None
    
    # Plan final consolidado
    plan_mensual: Optional[Dict[str, Any]] = None
    metricas: Optional[Dict[str, Any]] = None


class NutritionPlan(BaseModel):
    """Plan de nutrición generado"""
    plan_id: str
    version: int = 1
    created_at: datetime
    
    # Outputs de los agentes de nutrición
    n0_triage: Optional[Dict[str, Any]] = None
    n1_analista_metabolico: Optional[Dict[str, Any]] = None
    n2_selector_energetico: Optional[Dict[str, Any]] = None
    n3_plantilla_comercial: Optional[Dict[str, Any]] = None
    n4_sincronizador_amb: Optional[Dict[str, Any]] = None
    n5_reparto_timing: Optional[Dict[str, Any]] = None
    n6_menus_equivalencias: Optional[Dict[str, Any]] = None
    n7_coach_adherencia: Optional[Dict[str, Any]] = None
    n8_watchdog: Optional[Dict[str, Any]] = None
    
    # Plan final consolidado
    plan_nutricional: Optional[Dict[str, Any]] = None
    calendario_amb: Optional[Dict[str, Any]] = None
    menus: Optional[Dict[str, Any]] = None


class FollowUpPlan(BaseModel):
    """Plan de seguimiento mensual"""
    plan_id: str
    version: int = 1
    created_at: datetime
    month_number: int  # Mes de seguimiento (1, 2, 3...)
    
    # Outputs agentes seguimiento entrenamiento
    es1_interprete: Optional[Dict[str, Any]] = None
    es2_evaluador: Optional[Dict[str, Any]] = None
    es3_arquitecto_ajustes: Optional[Dict[str, Any]] = None
    es4_auditor: Optional[Dict[str, Any]] = None
    
    # Outputs agentes seguimiento nutrición
    ns1_interprete_metabolico: Optional[Dict[str, Any]] = None
    ns2_evaluador_energia: Optional[Dict[str, Any]] = None
    ns3_ajustador_macros: Optional[Dict[str, Any]] = None
    ns4_auditor_nutricional: Optional[Dict[str, Any]] = None
    
    # Planes ajustados
    training_ajustes: Optional[Dict[str, Any]] = None
    nutrition_ajustes: Optional[Dict[str, Any]] = None


# ==================== MAIN PLAN DOCUMENT ====================

class EDN360Plan(BaseModel):
    """Documento principal que representa un plan E.D.N.360 completo"""
    
    # Identificación
    plan_id: str
    client_id: str
    client_name: str
    plan_type: PlanType
    status: PlanStatus = PlanStatus.PENDING
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    generated_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    
    # Cuestionario origen
    questionnaire_data: QuestionnaireData
    
    # Planes generados
    training_plan: Optional[TrainingPlan] = None
    nutrition_plan: Optional[NutritionPlan] = None
    followup_plan: Optional[FollowUpPlan] = None
    
    # Ejecución de agentes
    agent_executions: List[AgentExecution] = []
    total_duration_seconds: Optional[float] = None
    
    # Modificaciones
    modifications: List[Dict[str, Any]] = []  # Historial de cambios manuales o por IA
    current_version: int = 1
    
    # PDF generado
    pdf_url: Optional[str] = None
    pdf_generated_at: Optional[datetime] = None
    
    # Metadatos admin
    generated_by_admin_id: Optional[str] = None
    notes: Optional[str] = None  # Notas del admin
    tags: List[str] = []


# ==================== REQUEST/RESPONSE MODELS ====================

class GeneratePlanRequest(BaseModel):
    """Request para generar un plan"""
    questionnaire_id: str
    plan_type: PlanType
    admin_notes: Optional[str] = None


class GeneratePlanResponse(BaseModel):
    """Response de generación de plan"""
    plan_id: str
    status: PlanStatus
    message: str
    estimated_time_seconds: Optional[int] = None


class ModifyPlanRequest(BaseModel):
    """Request para modificar un plan con IA"""
    plan_id: str
    modification_request: str  # Lo que el admin quiere cambiar
    context: Optional[Dict[str, Any]] = None


class ModifyPlanResponse(BaseModel):
    """Response de modificación de plan"""
    plan_id: str
    new_version: int
    modifications_applied: List[str]
    updated_at: datetime


class SendPlanRequest(BaseModel):
    """Request para enviar plan al cliente"""
    plan_id: str
    delivery_method: str  # "email", "whatsapp", "attach_to_docs"
    custom_message: Optional[str] = None


class SendPlanResponse(BaseModel):
    """Response de envío de plan"""
    plan_id: str
    delivery_method: str
    sent_at: datetime
    success: bool
    message: str
