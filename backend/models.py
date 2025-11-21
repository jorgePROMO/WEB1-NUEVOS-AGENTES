from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime, timezone
from bson import ObjectId


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Subscription(BaseModel):
    status: str = "pending"  # pending, active, cancelled, archived
    plan: str = "team"  # team, direct
    start_date: datetime = Field(default_factory=datetime.utcnow)
    payment_status: str = "pending"  # pending, verified
    stripe_customer_id: Optional[str] = None
    archived: bool = False
    archived_reason: Optional[str] = None
    archived_date: Optional[datetime] = None


class UserBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    phone: Optional[str] = None
    role: str = "user"  # user, admin


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    phone: str



class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None


class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    subscription_status: Optional[str] = None
    subscription_plan: Optional[str] = None
    payment_status: Optional[str] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str


class UserInDB(UserBase):
    id: str = Field(alias="_id")
    password: str
    subscription: Subscription
    next_review: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    email_verified: bool = False  # Nuevo campo
    verification_token: Optional[str] = None  # Nuevo campo
    verification_token_expires_at: Optional[datetime] = None  # Nuevo campo

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserResponse(UserBase):
    id: str
    subscription: Subscription
    next_review: Optional[datetime] = None


class FormBase(BaseModel):
    title: str
    url: str


class FormCreate(FormBase):
    user_id: str


class FormInDB(FormBase):
    id: str = Field(alias="_id")
    user_id: str
    completed: bool = False
    sent_date: datetime = Field(default_factory=datetime.utcnow)
    completed_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class PDFBase(BaseModel):
    title: str
    type: str  # training, nutrition


class PDFCreate(PDFBase):
    user_id: str
    file_path: str


class PDFInDB(PDFBase):
    id: str = Field(alias="_id")
    user_id: str
    file_path: str
    uploaded_by: str  # 'admin' or 'user'
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class AlertBase(BaseModel):
    title: str
    message: str
    type: str = "general"  # form, general, reminder
    link: Optional[str] = None


class AlertCreate(AlertBase):
    user_id: str


class AlertInDB(AlertBase):
    id: str = Field(alias="_id")
    user_id: str
    read: bool = False
    date: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class MessageBase(BaseModel):
    message: str


class MessageCreate(MessageBase):
    user_id: str  # Client user ID


class MessageInDB(MessageBase):
    id: str = Field(alias="_id")
    user_id: str  # Client user ID
    sender_id: str  # Who sent the message
    sender_name: str
    is_admin: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class SessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: datetime
    duration: int = 60  # minutes
    type: str = "review"  # review, training, consultation


class SessionCreate(SessionBase):
    user_id: str


class SessionInDB(SessionBase):
    id: str = Field(alias="_id")
    user_id: str
    created_by: str  # admin ID
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserSession(BaseModel):
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class SessionUpdate(BaseModel):
    date: datetime
    time: Optional[str] = None



class QuestionnaireSubmit(BaseModel):
    # Datos Personales
    nombre: str
    edad: str
    email: EmailStr
    whatsapp: str
    
    # Contexto Actual
    objetivo: str
    intentos_previos: str
    dificultades: List[str] = []
    dificultades_otro: Optional[str] = ''
    tiempo_semanal: str
    entrena: str
    
    # Nutrición
    alimentacion: str
    salud_info: str
    
    # Motivación
    por_que_ahora: str
    dispuesto_invertir: str
    tipo_acompanamiento: str
    presupuesto: str
    comentarios_adicionales: Optional[str] = ''


# ==================== CRM PROSPECTOS MODELS ====================

class ProspectStageCreate(BaseModel):
    name: str
    color: str = "#3B82F6"  # Default blue color
    order: int = 0

class ProspectStageInDB(ProspectStageCreate):
    id: str = Field(alias="_id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ProspectResponse(BaseModel):
    id: str = Field(alias="_id")
    # Datos Personales
    nombre: str
    edad: str
    email: EmailStr
    whatsapp: str
    
    # Contexto Actual
    objetivo: str
    intentos_previos: str
    dificultades: List[str] = []
    dificultades_otro: Optional[str] = None
    tiempo_semanal: str
    entrena: str
    
    # Nutrición
    alimentacion: str
    salud_info: str
    
    # Motivación
    por_que_ahora: str
    dispuesto_invertir: str
    tipo_acompanamiento: str
    presupuesto: str
    comentarios_adicionales: Optional[str] = None
    
    # CRM fields
    stage_id: Optional[str] = None
    stage_name: Optional[str] = "Nuevo"
    submitted_at: datetime
    converted_to_client: bool = False
    
    # GPT Report fields
    report_generated: bool = False
    report_sent_at: Optional[datetime] = None
    report_content: Optional[str] = None
    report_sent_via: Optional[str] = None  # 'email' or 'whatsapp'
    report_generated_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

class ProspectNoteCreate(BaseModel):
    prospect_id: str
    note: str

class ProspectNoteInDB(ProspectNoteCreate):
    id: str = Field(alias="_id")
    created_by: str  # admin user id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


# ==================== NUTRITION MODELS ====================

class NutritionQuestionnaireSubmit(BaseModel):
    # Datos básicos
    nombre_completo: str
    email: EmailStr
    fecha_nacimiento: str
    sexo: str
    profesion: str
    direccion: Optional[str] = None
    telefono: str
    
    # Medidas corporales
    peso: str
    altura_cm: str
    grasa_porcentaje: Optional[str] = None
    cintura_cm: Optional[str] = None
    cadera_cm: Optional[str] = None
    biceps_relajado_cm: Optional[str] = None
    biceps_flexionado_cm: Optional[str] = None
    muslo_cm: Optional[str] = None
    
    # Salud y medicación
    medicamentos: Optional[str] = None
    enfermedad_cronica: Optional[str] = None
    fuma_cantidad: Optional[str] = None
    bebe_cantidad: Optional[str] = None
    retencion_liquidos: Optional[str] = None
    problemas_corazon: Optional[str] = None
    hipertension: Optional[str] = None
    diabetes: Optional[str] = None
    colesterol: Optional[str] = None
    sobrepeso: Optional[str] = None
    epilepsia: Optional[str] = None
    alergias_intolerancias: Optional[str] = None
    problema_ejercicio: Optional[str] = None
    operaciones: Optional[str] = None
    embarazo: Optional[str] = None
    problemas_respiratorios: Optional[str] = None
    problemas_musculares: Optional[str] = None
    varo_valgo: Optional[str] = None
    hernias_protusiones: Optional[str] = None
    artrosis: Optional[str] = None
    menopausia: Optional[str] = None
    osteoporosis: Optional[str] = None
    
    # Trabajo y estrés
    estres_profesion: str
    movimiento_trabajo: str
    dia_trabajo: Optional[str] = None
    descansa_trabajo: str
    horas_trabajo: str
    actividad_fisica_diaria: str
    trabajo_fisicamente: str
    horas_ocio_semana: Optional[str] = None
    
    # Experiencia deportiva
    practicado_deporte: str
    experiencia_negativa: Optional[str] = None
    constante_deporte: str
    tiempo_dedicaba: Optional[str] = None
    nivel_deporte: Optional[str] = None
    entrenado_gimnasio: str
    entrenador_personal: str
    resistencia_cardiorespiratoria: str
    fuerza: str
    flexibilidad: str
    agilidad_coordinacion: str
    
    # Disponibilidad y preferencias
    dias_semana_entrenar: str
    tiempo_sesion: str
    entrena_manana_tarde: str
    gimnasio: str
    material_casa: Optional[str] = None
    actividades_realizar: Optional[str] = None
    tipo_persona: str
    cuesta_coger_peso: str
    motivos_entrenar: list
    
    # Horarios
    hora_levanta: str
    hora_desayuno: str
    hora_almuerzo: Optional[str] = None
    hora_comida: str
    hora_merienda: Optional[str] = None
    hora_cena: str
    hora_acuesta: str
    horas_duerme: str
    
    # Hábitos alimentarios
    comidas_dia: str
    comidas_fuertes_ligeras: Optional[str] = None
    alimento_no_soporta: Optional[str] = None
    comida_favorita: Optional[str] = None
    comida_basura_frecuencia: Optional[str] = None
    dietas_anteriores: Optional[str] = None
    sustancias_alteran: Optional[str] = None
    suplementacion: Optional[str] = None
    come_fuera_casa: str
    azucar_dulces_bolleria: str
    anade_sal: str
    bebidas_gas: str
    
    # Objetivos
    objetivo_fisico: str
    experiencia_ejercicio_constante: str
    impedido_constancia: Optional[str] = None
    motiva_ejercicio: Optional[str] = None
    nivel_energia_dia: str
    comentarios_adicionales: Optional[str] = None



# Modelo para almacenar SOLO las respuestas del cuestionario (sin plan generado)
class NutritionQuestionnaireSubmission(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    responses: dict  # Todas las respuestas del cuestionario
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    plan_generated: bool = False  # Si el admin ya generó el plan
    plan_id: Optional[str] = None  # ID del plan generado (si existe)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, datetime: str}


class NutritionPlanResponse(BaseModel):
    user_id: str
    questionnaire_data: dict
    plan_inicial: str
    plan_verificado: str
    generated_at: datetime
    edited: bool = False
    pdf_generated: bool = False
    pdf_url: Optional[str] = None


class NutritionPlanHistoryItem(BaseModel):
    id: str
    user_id: str
    month: int  # 1-12
    year: int
    questionnaire_data: dict
    plan_inicial: str
    plan_verificado: str
    generated_at: datetime
    edited: bool = False
    pdf_id: Optional[str] = None
    pdf_filename: Optional[str] = None
    sent_email: bool = False
    sent_whatsapp: bool = False


# ==================== TRAINING PLANS MODELS ====================

class TrainingPlanResponse(BaseModel):
    user_id: str
    questionnaire_data: dict
    agent_1_output: str  # Basic profile analysis
    agent_2_output: str  # Advanced contextualization
    agent_3_output: dict  # Weekly plan + table
    plan_final: str  # Final professional document
    generated_at: datetime
    edited: bool = False
    pdf_generated: bool = False
    pdf_url: Optional[str] = None


class TrainingPlanHistoryItem(BaseModel):
    id: str
    user_id: str
    month: int  # 1-12
    year: int
    questionnaire_data: dict
    agent_1_output: str
    agent_2_output: str
    agent_3_output: dict
    plan_final: str
    generated_at: datetime
    edited: bool = False
    pdf_id: Optional[str] = None
    pdf_filename: Optional[str] = None
    sent_email: bool = False
    sent_whatsapp: bool = False


class ProspectStageUpdate(BaseModel):
    stage_id: str


# ==================== EXTERNAL CLIENTS MODELS ====================

class ExternalClientCreate(BaseModel):
    nombre: str
    email: EmailStr
    whatsapp: str
    objetivo: Optional[str] = None
    plan_weeks: int = 12
    start_date: Optional[str] = None
    amount_paid: Optional[float] = 0
    notes: Optional[str] = None

class ExternalClientUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    whatsapp: Optional[str] = None
    objetivo: Optional[str] = None
    plan_weeks: Optional[int] = None
    start_date: Optional[str] = None
    weeks_completed: Optional[int] = None

class ExternalClientInDB(BaseModel):
    id: str = Field(alias="_id")
    nombre: str
    email: EmailStr
    whatsapp: str
    objetivo: Optional[str] = None
    plan_weeks: int
    start_date: Optional[datetime] = None
    next_payment_date: Optional[datetime] = None
    weeks_completed: int = 0
    status: str = "active"  # active, paused, completed
    payment_history: List[dict] = []
    notes: List[dict] = []
    source: str = "manual"  # manual or prospect
    prospect_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}



# Templates System
class MessageTemplate(BaseModel):
    id: Optional[str] = None
    type: str  # whatsapp, alert, email
    name: str
    subject: Optional[str] = None  # for emails/alerts
    content: str
    variables: List[str] = []  # [nombre, fecha, hora, etc]
    category: str  # welcome, reminder, followup, general
    tags: List[str] = []  # Etiquetas para búsqueda
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TemplateCreate(BaseModel):
    type: str = "whatsapp"  # Default type
    name: str
    subject: Optional[str] = None
    content: str
    variables: List[str] = []
    category: Optional[str] = "general"
    tags: List[str] = []

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class TemplateResponse(BaseModel):
    id: str
    type: str
    name: str
    subject: Optional[str] = None
    content: str
    variables: List[str]
    category: str
    tags: List[str] = []
    created_at: datetime

# Automated Reminders Configuration
class ReminderConfig(BaseModel):
    form_reminder_enabled: bool = True
    form_reminder_days: int = 3
    session_reminder_enabled: bool = True
    session_reminder_hours: int = 24
    inactive_alert_enabled: bool = True
    inactive_alert_days: int = 7

# Client Risk Indicators
class ClientRiskStatus(BaseModel):
    client_id: str
    client_name: str
    client_email: str
    risk_level: str  # red, yellow, green
    risk_reasons: List[str] = []
    days_inactive: Optional[int] = None
    pending_forms_days: Optional[int] = None
    last_session_date: Optional[datetime] = None
    last_activity_date: Optional[datetime] = None



# ==================== MONTHLY FOLLOW-UP MODELS ====================

class FollowUpMeasurements(BaseModel):
    """Mediciones del seguimiento - estructura condicional según tipo"""
    # Smart Scale measurements
    peso: Optional[str] = None
    grasa_corporal: Optional[str] = None
    masa_muscular: Optional[str] = None
    grasa_visceral: Optional[str] = None
    agua_corporal: Optional[str] = None
    
    # Tape measure circumferences
    circunferencia_pecho: Optional[str] = None
    circunferencia_cintura: Optional[str] = None
    circunferencia_gluteo: Optional[str] = None
    circunferencia_muslo: Optional[str] = None
    circunferencia_brazo_relajado: Optional[str] = None
    circunferencia_brazo_flexionado: Optional[str] = None
    circunferencia_gemelo: Optional[str] = None
    
    # Satisfacción con cambios
    satisfecho_cambios: Optional[str] = None  # "SI" o "NO"


class FollowUpAdherence(BaseModel):
    """Adherencia al plan"""
    constancia_entrenamiento: str
    seguimiento_alimentacion: str


class FollowUpWellbeing(BaseModel):
    """Bienestar general"""
    factores_externos: Optional[str] = None
    energia_animo_motivacion: str
    sueno_estres: str


class FollowUpChanges(BaseModel):
    """Cambios percibidos"""
    molestias_dolor_lesion: str
    cambios_corporales: str
    fuerza_rendimiento: str


class FollowUpFeedback(BaseModel):
    """Comentarios y ajustes"""
    objetivo_proximo_mes: str
    cambios_deseados: str
    comentarios_adicionales: Optional[str] = None


class FollowUpSubmit(BaseModel):
    """Modelo para recibir el cuestionario de seguimiento del cliente"""
    # Tipo de medición
    measurement_type: str  # "smart_scale", "tape_measure", "none"
    
    # Mediciones (condicionales)
    measurements: Optional[FollowUpMeasurements] = None
    
    # Secciones obligatorias
    adherence: FollowUpAdherence
    wellbeing: FollowUpWellbeing
    changes_perceived: FollowUpChanges
    feedback: FollowUpFeedback


class FollowUpSubmissionInDB(BaseModel):
    """Seguimiento mensual guardado en BD"""
    id: str = Field(alias="_id")
    user_id: str
    submission_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    days_since_last_plan: int  # Días desde el último plan
    previous_plan_id: Optional[str] = None  # Referencia al plan previo
    previous_questionnaire_id: Optional[str] = None  # Cuestionario inicial
    
    # Respuestas del cuestionario
    measurement_type: str
    measurements: Optional[dict] = None
    adherence: dict
    wellbeing: dict
    changes_perceived: dict
    feedback: dict
    
    # Estado del seguimiento
    status: str = "pending_analysis"  # pending_analysis, analyzed, plan_generated
    ai_analysis: Optional[str] = None  # Análisis generado por IA
    ai_analysis_edited: bool = False  # Si el admin editó el análisis
    new_plan_id: Optional[str] = None  # Plan generado después del análisis
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, datetime: str}


class FollowUpAlertCreate(BaseModel):
    """Alerta para el admin cuando un cliente cumple 30 días"""
    user_id: str
    user_name: str
    user_email: str
    days_since_plan: int
    last_plan_date: datetime


# ===================================
# STRIPE PAYMENT & SUBSCRIPTION MODELS
# ===================================

class StripeSubscriptionCreate(BaseModel):
    """Modelo para crear suscripción de Stripe"""
    plan_type: str = Field(..., description="Tipo de plan: monthly, annual")
    
class PaymentTransaction(BaseModel):
    """Modelo para transacciones de pago de Stripe"""
    transaction_id: str  # UUID único
    user_id: str
    user_email: str
    session_id: str  # Stripe session ID
    payment_status: str = "pending"  # pending, succeeded, failed, expired
    amount: float  # Monto en formato decimal (ej: 29.99)
    currency: str = "eur"
    subscription_id: Optional[str] = None  # ID de suscripción asociada
    metadata: Optional[dict] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: str}

class UserSubscription(BaseModel):
    """Modelo para suscripciones de usuarios"""
    subscription_id: str  # UUID único
    user_id: str
    user_email: str
    stripe_session_id: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    plan_type: str  # monthly, annual
    status: str = "active"  # active, cancelled, expired, pending
    amount: float
    currency: str = "eur"
    start_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    next_billing_date: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    class Config:
        populate_by_name = True
        json_encoders = {datetime: str}

class FinancialMetrics(BaseModel):
    """Modelo para métricas financieras del admin"""
    total_revenue: float
    monthly_revenue: float
    annual_revenue: float
    active_subscriptions: int
    cancelled_subscriptions: int
    total_transactions: int
    successful_payments: int
    failed_payments: int
    mrr: float  # Monthly Recurring Revenue
    
class PaymentHistoryItem(BaseModel):
    """Item del historial de pagos"""
    transaction_id: str
    date: datetime
    amount: float
    currency: str
    status: str
    user_name: Optional[str] = None
    user_email: str


class FinancialOverviewResponse(BaseModel):
    total_revenue: float
    monthly_revenue: float
    annual_revenue: float
    active_subscriptions: int
    cancelled_subscriptions: int
    pending_payments: int
    failed_payments: int


# ==================== EXERCISE DATABASE MODELS ====================

class Exercise(BaseModel):
    """Model for exercise from custom database"""
    id: Optional[str] = Field(alias="_id", default=None)
    nombre_ejercicio: str
    grupo_muscular_principal: str
    grupo_muscular_secundario: Optional[str] = None
    lugar_entrenamiento: str  # Casa / Gimnasio
    nivel_dificultad: str  # Principiante / Intermedio / Avanzado
    material_necesario: str
    equipamiento_opcional: Optional[str] = None
    tags_gpt: str  # Comma-separated tags
    url_video: str  # Google Drive URL
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class ExerciseResponse(BaseModel):
    """Response model for exercises"""
    id: str
    nombre_ejercicio: str
    grupo_muscular_principal: str
    grupo_muscular_secundario: Optional[str] = None
    lugar_entrenamiento: str
    nivel_dificultad: str
    material_necesario: str
    equipamiento_opcional: Optional[str] = None
    tags_gpt: str
    url_video: str


class ExerciseQuery(BaseModel):
    """Query parameters for filtering exercises"""
    grupo_muscular: Optional[str] = None
    nivel_dificultad: Optional[str] = None
    lugar_entrenamiento: Optional[str] = None
    material_disponible: Optional[List[str]] = None


# ==================== TRAINING PLAN CHAT MODELS ====================

class TrainingPlanChatMessage(BaseModel):
    """Message in training plan chat"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TrainingPlanChatRequest(BaseModel):
    """Request to chat about a training plan"""
    plan_id: str
    user_message: str


class TrainingPlanChatResponse(BaseModel):
    """Response from training plan chat"""
    assistant_message: str
    updated_plan: Optional[str] = None  # If the plan was modified


class NutritionPlanChatRequest(BaseModel):
    """Request to chat about a nutrition plan"""
    plan_id: str
    user_message: str


class NutritionPlanChatResponse(BaseModel):
    """Response from nutrition plan chat"""
    assistant_message: str
    updated_plan: Optional[str] = None  # If the plan was modified


# ==================== WAITLIST MODELS ====================

class WaitlistLeadSubmit(BaseModel):
    """Modelo para recibir el formulario de waitlist"""
    # 1. Datos básicos
    nombre_apellidos: str
    email: EmailStr
    telefono: str
    edad: str
    ciudad_pais: str
    como_conociste: str  # Nueva pregunta
    
    # 2. Capacidad económica y prioridades
    inversion_mensual: str  # "< 50€/mes", "100-200€/mes", "200-500€/mes", "500+€/mes"
    invierte_actualmente: str  # "No invierto", "Gimnasio o suplementos", etc.
    frase_representa: str  # "Busco algo económico", "Busco resultados reales", etc.
    
    # 3. Objetivos y motivación
    objetivo_principal: str  # "Perder grasa", "Ganar músculo", etc.
    por_que_ahora: str  # "Razón clara", "Cansado de posponer", etc.
    intentado_antes: str  # "No he hecho nada", "Dietas por mi cuenta", etc.
    como_verte_3_meses: str  # Respuesta abierta
    
    # 4. Experiencia y hábitos
    entrenas_actualmente: str  # "Sí con entrenador", "Sí por mi cuenta", etc.
    dias_semana_entrenar: str  # "1-2 días", "3-4 días", "5+ días"
    nivel_experiencia: str  # "Principiante", "Intermedio", "Avanzado"
    limitaciones_fisicas: Optional[str] = None
    
    # 5. Disponibilidad y compromiso
    tiempo_semanal: str  # "< 2h", "3-4h", "5-6h", "6+h"
    nivel_compromiso: str  # "1-4", "5-6", "7-8", "9-10"
    que_pasaria_sin_cambiar: str  # "No pasaría nada", "Me frustraría", etc.
    
    # 6. Personalidad y afinidad
    preferencia_comunicacion: str  # "Directa y exigente", "Intermedio", "Flexible"
    que_motiva_mas: str  # "Resultados visibles", "Sentirme mejor", etc.
    esperas_del_coach: str  # "Que me exijas", "Que me acompañes", etc.
    
    # 7. Disponibilidad para entrevista
    disponibilidad_llamada: str  # "Sí puedo adaptarme", "Prefiero WhatsApp", etc.


class WaitlistLeadInDB(BaseModel):
    """Lead de waitlist almacenado en BD con scoring y tags"""
    id: str = Field(alias="_id")
    
    # Datos básicos
    nombre_apellidos: str
    email: EmailStr
    telefono: str
    edad: str
    ciudad_pais: str
    como_conociste: str
    
    # Todas las respuestas (JSON completo)
    responses: dict
    
    # Scoring (calculado automáticamente)
    score_total: int  # 0-100
    score_capacidad_economica: int  # 0-25
    score_objetivos_motivacion: int  # 0-25
    score_experiencia_habitos: int  # 0-15
    score_disponibilidad_compromiso: int  # 0-20
    score_personalidad_afinidad: int  # 0-10
    score_disponibilidad_entrevista: int  # 0-5
    
    # Tags automáticos
    capacidad_economica: str  # "baja", "media", "alta"
    objetivo: str  # "definicion", "volumen", "recomposicion", "habitos"
    motivacion: str  # "baja", "media", "alta"
    nivel_experiencia: str  # "bajo", "medio", "alto"
    nivel_compromiso: str  # "bajo", "medio", "alto"
    urgencia: str  # "baja", "media", "alta"
    afinidad_estilo: str  # "alta", "media", "baja"
    
    # Prioridad (calculada según score)
    prioridad: str  # "alta" (66-100), "media" (41-65), "baja" (0-40)
    
    # Estado y gestión
    estado: str = "pendiente"  # "pendiente", "contactado", "aceptado", "rechazado"
    notas_admin: List[dict] = []  # [{texto, fecha, admin_id}]
    historial_contacto: List[dict] = []  # [{tipo, fecha, contenido}]
    
    # Fechas
    submitted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    contacted_at: Optional[datetime] = None
    converted_at: Optional[datetime] = None
    
    # Conversión
    converted_to_client: bool = False
    client_id: Optional[str] = None
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str, datetime: str}


class WaitlistLeadResponse(BaseModel):
    """Respuesta del lead para el frontend"""
    id: str
    nombre_apellidos: str
    email: str
    telefono: str
    edad: str
    ciudad_pais: str
    como_conociste: str
    score_total: int
    prioridad: str
    estado: str
    capacidad_economica: str
    objetivo: str
    motivacion: str
    nivel_compromiso: str
    submitted_at: datetime
    notas_admin: List[dict]


class WaitlistStatusUpdate(BaseModel):
    """Actualizar estado de un lead"""
    estado: str  # "pendiente", "contactado", "aceptado", "rechazado"


class WaitlistNoteAdd(BaseModel):
    """Añadir nota a un lead"""
    nota: str


class ManualPayment(BaseModel):
    """Pago manual para Caja A o B"""
    concepto: str
    amount: float
    fecha: str
    metodo_pago: str  # Stripe, Transferencia, Bizum, Efectivo
    notas: Optional[str] = ""

class ManualPaymentCreate(BaseModel):
    """Crear pago manual"""
    concepto: str
    amount: float
    fecha: str
    metodo_pago: str
    notas: Optional[str] = ""


# ============================================================================
# GENERATION JOBS - Sistema Asíncrono de Generación de Planes
# ============================================================================

class GenerationJobProgress(BaseModel):
    """Progreso del job de generación"""
    phase: str  # "training" | "nutrition" | "completed"
    current_agent: Optional[str] = None  # "E1" | "E2" | ... | "N0" | "N1" | ...
    completed_steps: int = 0
    total_steps: int = 18  # 9 agentes training + 9 agentes nutrition
    percentage: int = 0
    message: str = ""

class GenerationJobResult(BaseModel):
    """Resultado del job de generación"""
    training_plan_id: Optional[str] = None
    nutrition_plan_id: Optional[str] = None

class TokenUsage(BaseModel):
    """Uso de tokens por agente"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class JobTokenUsage(BaseModel):
    """Uso total de tokens del job"""
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    by_agent: dict = Field(default_factory=dict)  # {agent_id: {prompt, completion, total}}

class GenerationJob(BaseModel):
    """Job de generación de planes E.D.N.360 con estabilización"""
    job_id: str
    user_id: str
    type: str  # "training" | "nutrition" | "full"
    submission_id: str
    training_plan_id: Optional[str] = None  # Para sincronizar con plan de entrenamiento
    previous_nutrition_plan_id: Optional[str] = None  # Plan nutricional previo
    previous_training_plan_id: Optional[str] = None  # Plan de entrenamiento previo
    status: str = "pending"  # "pending" | "queued" | "running" | "completed" | "failed"
    progress: GenerationJobProgress = Field(default_factory=lambda: GenerationJobProgress(
        phase="pending",
        completed_steps=0,
        total_steps=18,
        percentage=0,
        message="Job creado, esperando ejecución"
    ))
    result: GenerationJobResult = Field(default_factory=GenerationJobResult)
    error_message: Optional[str] = None
    error_reason: Optional[str] = None  # "timeout" | "error"
    retry_count: int = 0  # Número de reintentos realizados
    execution_log: List[dict] = Field(default_factory=list)  # Log de eventos
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class GenerateAsyncRequest(BaseModel):
    """Request para generación asíncrona"""
    submission_id: str
    mode: str  # "training" | "nutrition" | "full"
    training_plan_id: Optional[str] = None
    previous_nutrition_plan_id: Optional[str] = None
    previous_training_plan_id: Optional[str] = None

