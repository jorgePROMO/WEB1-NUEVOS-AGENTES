from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
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
    role: str = "user"  # user, admin


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str



class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
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

class ProspectStageUpdate(BaseModel):
    stage_id: str

    comentarios_adicionales: Optional[str] = None
