from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Request, Response, BackgroundTasks
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import List, Optional
import shutil
import httpx
import socketio
import uuid
import json
import asyncio

from models import (
    UserCreate, UserResponse, UserInDB, Subscription,
    UserUpdate, AdminUserUpdate, PasswordResetRequest, PasswordReset,
    FormCreate, FormInDB, PDFCreate, PDFInDB,
    AlertCreate, AlertInDB, MessageCreate, MessageInDB,
    SessionCreate, SessionInDB, SessionUpdate, UserSession,
    Token, QuestionnaireSubmit,
    ProspectStageCreate, ProspectStageInDB, ProspectResponse,
    ProspectNoteCreate, ProspectNoteInDB, ProspectStageUpdate,
    ExternalClientCreate, ExternalClientUpdate, ExternalClientInDB,
    MessageTemplate, TemplateCreate, TemplateResponse, TemplateUpdate,
    ReminderConfig, ClientRiskStatus,
    NutritionQuestionnaireSubmit, NutritionPlanResponse,
    FollowUpSubmit, FollowUpSubmissionInDB,
    StripeSubscriptionCreate, PaymentTransaction, UserSubscription,
    FinancialMetrics, PaymentHistoryItem,
    Exercise, ExerciseResponse, ExerciseQuery,
    TrainingPlanChatRequest, TrainingPlanChatResponse,
    NutritionPlanChatRequest, NutritionPlanChatResponse,
    WaitlistLeadSubmit, WaitlistLeadInDB, WaitlistLeadResponse,
    WaitlistStatusUpdate, WaitlistNoteAdd,
    ManualPayment, ManualPaymentCreate,
    GenerationJob, GenerateAsyncRequest, GenerationJobProgress, GenerationJobResult
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user_id, get_current_user_id_flexible
)
from email_utils import (
    send_session_created_email, 
    send_session_rescheduled_email,
    send_admin_session_created_email,
    send_admin_session_rescheduled_email,
    send_admin_session_cancelled_email,
    send_questionnaire_to_admin
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging FIRST (before any logging calls)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== HELPER FUNCTIONS ====================
def _serialize_datetime_fields(data):
    """
    Recursively convert datetime objects to ISO format strings for JSON serialization
    """
    if isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: _serialize_datetime_fields(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_serialize_datetime_fields(item) for item in data]
    else:
        return data


def _translate_training_plan_to_spanish(plan):
    """
    Traduce todos los términos de entrenamiento de inglés a español de España.
    Se aplica ANTES de guardar el plan en la base de datos.
    """
    # Diccionario de traducciones (inglés → español)
    translations = {
        # Tipos de entrenamiento
        'full_body': 'Cuerpo Completo',
        'upper_lower': 'Torso-Pierna',
        'push_pull_legs': 'Empuje-Tirón-Pierna',
        'bro_split': 'Rutina Weider',
        
        # Focos/énfasis de sesiones
        'upper_body': 'Tren Superior',
        'lower_body': 'Tren Inferior',
        'push': 'Empuje',
        'pull': 'Tirón',
        'push_focus': 'Énfasis Empuje',
        'pull_focus': 'Énfasis Tirón',
        'quad_focus': 'Énfasis Cuádriceps',
        'hamstring_focus': 'Énfasis Isquios',
        'push_emphasis': 'Énfasis Empuje',
        'pull_emphasis': 'Énfasis Tirón',
        'posterior_chain': 'Cadena Posterior',
        
        # Grupos musculares principales
        'Chest': 'Pecho',
        'chest': 'Pecho',
        'Back': 'Espalda',
        'back': 'Espalda',
        'Shoulders': 'Hombros',
        'shoulders': 'Hombros',
        'Triceps': 'Tríceps',
        'triceps': 'Tríceps',
        'Biceps': 'Bíceps',
        'biceps': 'Bíceps',
        'Quads': 'Cuádriceps',
        'quads': 'Cuádriceps',
        'Hamstrings': 'Isquiotibiales',
        'hamstrings': 'Isquiotibiales',
        'Glutes': 'Glúteos',
        'glutes': 'Glúteos',
        'Legs': 'Piernas',
        'legs': 'Piernas',
        'Arms': 'Brazos',
        'arms': 'Brazos',
        'core': 'Core',
        'Core': 'Core',
        'calves': 'Gemelos',
        
        # Grupos musculares específicos
        'front_delts': 'Deltoides Anterior',
        'side_delts': 'Deltoides Lateral',
        'rear_delts': 'Deltoides Posterior',
        'upper_chest': 'Pecho Superior',
        'lower_chest': 'Pecho Inferior',
        'lats': 'Dorsales',
        'upper_back': 'Espalda Superior',
        'traps': 'Trapecios',
        'lower_back': 'Lumbar',
        'abs': 'Abdominales',
        'obliques': 'Oblicuos',
        'forearms': 'Antebrazos',
        'abductors': 'Abductores',
        
        # Frases de nombres de sesiones completas (más específicas primero)
        'Chest & Triceps – Joint Friendly': 'Pecho y Tríceps - Amigable con Articulaciones',
        'Back & Biceps – Supported Pulls': 'Espalda y Bíceps - Jalones Asistidos',
        'Legs – Quads & Glutes Emphasis': 'Piernas - Énfasis Cuádriceps y Glúteos',
        'Shoulders & Arms – Machine/Isolation Safe': 'Hombros y Brazos - Máquinas Seguras',
        'Upper 1 – Push Emphasis': 'Tren Superior 1 - Énfasis Empuje',
        'Upper 2 – Pull Emphasis': 'Tren Superior 2 - Énfasis Tirón',
        'Lower 1 – Quad Emphasis': 'Tren Inferior 1 - Énfasis Cuádriceps',
        'Lower 2 – Posterior Chain': 'Tren Inferior 2 - Cadena Posterior',
        
        # Conectores y palabras comunes
        '&': 'y',
        'and': 'y',
        'Emphasis': 'Énfasis',
        'emphasis': 'Énfasis',
        'Joint Friendly': 'Amigable con Articulaciones',
        'Supported Pulls': 'Jalones Asistidos',
        'Machine/Isolation Safe': 'Máquinas Seguras',
        'Posterior Chain': 'Cadena Posterior',
        
        # Términos técnicos en inglés que necesitan traducción
        'ROM': 'Rango de Movimiento',
        'Rear Delts': 'Deltoides Posteriores',
        'rear delts': 'deltoides posteriores',
        'Support': 'Soporte',
        'support': 'soporte',
        'Safety': 'Seguridad',
        'safety': 'seguridad',
        'Support Only': 'Solo Soporte',
        'Support y Safety': 'Soporte y Seguridad',
        'lateral_delts': 'Deltoides Laterales',
        'upper_Espalda': 'Espalda Superior',
        'Machine Énfasis': 'Énfasis en Máquinas',
        'Cuff': 'Manguito Rotador',
        'Joint Care': 'Cuidado Articular'
    }
    
    def translate_text(text):
        """Traduce un string aplicando todas las traducciones del diccionario"""
        if not isinstance(text, str):
            return text
        
        translated = text
        for eng, esp in translations.items():
            # Case-insensitive replacement
            import re
            pattern = re.compile(re.escape(eng), re.IGNORECASE)
            translated = pattern.sub(esp, translated)
        
        return translated
    
    def translate_recursive(obj):
        """Aplica traducción recursivamente a todo el plan"""
        if isinstance(obj, dict):
            return {key: translate_recursive(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [translate_recursive(item) for item in obj]
        elif isinstance(obj, str):
            return translate_text(obj)
        else:
            return obj
    
    return translate_recursive(plan)


# ==================== ENVIRONMENT VALIDATION ====================
# Validate critical environment variables at startup
required_env_vars = ['MONGO_URL', 'DB_NAME']
missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    raise RuntimeError(f"❌ CRITICAL: Missing required environment variables: {missing_vars}. Check your .env file!")

# Log configuration at startup
db_name = os.environ['DB_NAME']
logger.info(f"🔧 Starting server with database: {db_name}")

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Create the main app without a prefix
app = FastAPI()


# ==================== PDF HELPER FUNCTIONS ====================

async def create_pdf_document(
    user_id: str, 
    title: str, 
    content: bytes, 
    pdf_type: str, 
    related_id: str = None, 
    filename: str = None
):
    """
    Standardized PDF document creation for all AI-generated documents
    
    Args:
        user_id: ID of the user
        title: Display title for the PDF
        content: PDF binary content
        pdf_type: Type of PDF ("nutrition", "training", "follow_up_analysis")
        related_id: ID of the source plan/analysis
        filename: Custom filename (auto-generated if None)
    
    Returns:
        pdf_id: UUID of created PDF document
    """
    import uuid
    
    pdf_id = str(uuid.uuid4())
    current_time = datetime.now(timezone.utc)
    
    if not filename:
        filename = f"{pdf_type}_{user_id}_{current_time.strftime('%Y%m%d_%H%M%S')}.pdf"
    
    pdf_doc = {
        "_id": pdf_id,
        "user_id": user_id,
        "title": title,
        "filename": filename,
        "file_data": content,  # Always store binary data
        "type": pdf_type,  # "nutrition", "training", "follow_up_analysis"
        "upload_date": current_time,  # Standardized date field
        "uploaded_by": "admin",
        "related_id": related_id  # Link to source plan/analysis
    }
    
    await db.pdfs.insert_one(pdf_doc)
    logger.info(f"✅ PDF created: {pdf_id} | Type: {pdf_type} | User: {user_id}")
    
    return pdf_id



# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Socket.IO setup for real-time chat
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=True
)
socket_app = socketio.ASGIApp(sio, app)

# Logging already configured at the top of the file


# ==================== HELPER FUNCTIONS ====================

async def get_current_user(request: Request):
    user_id = await get_current_user_id_flexible(request)
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is archived
    if user.get("status") == "archived":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta ha sido archivada. Contacta con el administrador para reactivarla."
        )
    
    user["id"] = str(user["_id"])
    return user


async def require_admin(request: Request):
    user = await get_current_user(request)
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


# ==================== AUTH ENDPOINTS ====================

@api_router.post("/auth/register", response_model=dict)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"$or": [
        {"email": user_data.email},
        {"username": user_data.username}
    ]})
    
    if existing_user:
        # Usuario ya existe - NO permitir registro
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Generar token de verificación único
    import secrets
    verification_token = secrets.token_urlsafe(32)
    verification_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    
    # Create user
    user_dict = {
        "_id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
        "username": user_data.username,
        "email": user_data.email,
        "password": get_password_hash(user_data.password),
        "phone": user_data.phone,
        "name": user_data.username,
        "role": "user",
        "subscription": {
            "status": "pending",
            "plan": "team",
            "start_date": datetime.now(timezone.utc),
            "payment_status": "pending",
            "stripe_customer_id": None
        },
        "next_review": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "email_verified": False,  # Nuevo
        "verification_token": verification_token,  # Nuevo
        "verification_token_expires_at": verification_expires_at  # Nuevo
    }
    
    await db.users.insert_one(user_dict)
    
    # Enviar email de verificación
    try:
        from email_utils import send_email
        frontend_url = os.environ.get('FRONTEND_URL')
        if not frontend_url:
            raise HTTPException(status_code=500, detail="FRONTEND_URL environment variable is required")
        verification_link = f"{frontend_url}/verify-email?token={verification_token}"
        
        email_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ background-color: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ padding: 30px; }}
                .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Verifica tu Email</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{user_data.username}</strong>,</p>
                    <p>¡Gracias por registrarte en CRM Fusion!</p>
                    <p>Para completar tu registro y activar tu cuenta, por favor verifica tu email haciendo click en el botón de abajo:</p>
                    <div style="text-align: center;">
                        <a href="{verification_link}" class="button">✅ Verificar mi Email</a>
                    </div>
                    <p style="color: #666; font-size: 14px;">Si no puedes hacer click en el botón, copia y pega este enlace en tu navegador:</p>
                    <p style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; word-break: break-all; font-size: 12px;">{verification_link}</p>
                    <p style="color: #999; font-size: 12px; margin-top: 30px;">Este enlace expirará en 24 horas.</p>
                </div>
                <div class="footer">
                    <p>Jorge Calcerrada - Entrenador Personal</p>
                    <p>Si no te has registrado, puedes ignorar este email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        send_email(
            to_email=user_data.email,
            subject="✅ Verifica tu email - CRM Fusion",
            html_body=email_html
        )
        
        logger.info(f"Email de verificación enviado a {user_data.email}")
    except Exception as e:
        logger.error(f"Error enviando email de verificación: {e}")
        # NO fallar el registro si el email falla
    
    # Create token (pero el usuario NO podrá usar la app hasta verificar)
    access_token = create_access_token(data={"sub": user_dict["_id"]})
    
    # Return user without password
    user_response = {
        "id": user_dict["_id"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "name": user_dict["name"],
        "role": user_dict["role"],
        "subscription": user_dict["subscription"],
        "email_verified": False  # Indicar que falta verificar
    }
    
    return {
        "user": user_response, 
        "token": access_token,
        "message": "Registro exitoso. Por favor verifica tu email para activar tu cuenta."
    }


@api_router.post("/auth/login", response_model=dict)
async def login(email: str, password: str):
    user = await db.users.find_one({"email": email})
    
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is archived
    if user.get("status") == "archived":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta ha sido archivada. Contacta con Jorge para reactivarla."
        )
    
    # Check if email is verified (skip for admin users)
    if user.get("role") != "admin" and not user.get("email_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Por favor verifica tu email antes de iniciar sesión. Revisa tu bandeja de entrada."
        )
    
    # NO bloqueamos por payment_status - el usuario debe poder acceder al dashboard para pagar
    # El dashboard mostrará el botón de pago si payment_status="pending"
    
    # Create token
    access_token = create_access_token(data={"sub": str(user["_id"])})
    
    # Return user without password
    user_response = {
        "id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "subscription": user["subscription"]
    }
    
    return {"user": user_response, "token": access_token}


@api_router.get("/auth/verify-email")
async def verify_email(token: str):
    """Verificar email del usuario mediante token"""
    try:
        # Buscar usuario por token
        user = await db.users.find_one({"verification_token": token})
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail="Token de verificación inválido o expirado"
            )
        
        # Verificar si ya está verificado
        if user.get("email_verified"):
            return {
                "success": True,
                "message": "Email ya verificado previamente",
                "already_verified": True
            }
        
        # Verificar expiración del token (24 horas)
        token_expires = user.get("verification_token_expires_at")
        if token_expires:
            # Asegurar que tiene timezone
            if token_expires.tzinfo is None:
                token_expires = token_expires.replace(tzinfo=timezone.utc)
            
            if token_expires < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=400,
                    detail="El token de verificación ha expirado. Por favor solicita un nuevo email de verificación."
                )
        
        # Actualizar usuario como verificado
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "email_verified": True,
                    "verification_token": None,  # Limpiar token
                    "verification_token_expires_at": None,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"Email verificado para usuario {user.get('email')}")
        
        return {
            "success": True,
            "message": "✅ Email verificado correctamente. Ya puedes iniciar sesión.",
            "email": user.get("email")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verificando email: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error verificando email"
        )


@api_router.post("/auth/resend-verification")
async def resend_verification_email(email: str):
    """Reenviar email de verificación"""
    try:
        # Buscar usuario por email
        user = await db.users.find_one({"email": email})
        
        if not user:
            # No revelar si el email existe o no por seguridad
            return {
                "success": True,
                "message": "Si el email existe en nuestro sistema, recibirás un nuevo email de verificación."
            }
        
        # Si ya está verificado, informar
        if user.get("email_verified"):
            raise HTTPException(
                status_code=400,
                detail="Este email ya ha sido verificado"
            )
        
        # Generar nuevo token
        import secrets
        verification_token = secrets.token_urlsafe(32)
        verification_expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        # Actualizar token en la base de datos
        await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "verification_token": verification_token,
                    "verification_token_expires_at": verification_expires_at,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Enviar nuevo email
        try:
            from email_utils import send_email
            frontend_url = os.environ.get('FRONTEND_URL')
            if not frontend_url:
                raise HTTPException(status_code=500, detail="FRONTEND_URL environment variable is required")
            verification_link = f"{frontend_url}/verify-email?token={verification_token}"
            
            email_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                    .container {{ background-color: white; padding: 30px; border-radius: 10px; max-width: 600px; margin: 0 auto; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                    .content {{ padding: 30px; }}
                    .button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Verifica tu Email</h1>
                    </div>
                    <div class="content">
                        <p>Hola <strong>{user.get('name', user.get('username'))}</strong>,</p>
                        <p>Has solicitado un nuevo email de verificación.</p>
                        <p>Para completar tu registro y activar tu cuenta, por favor verifica tu email haciendo click en el botón de abajo:</p>
                        <div style="text-align: center;">
                            <a href="{verification_link}" class="button">✅ Verificar mi Email</a>
                        </div>
                        <p style="color: #666; font-size: 14px;">Si no puedes hacer click en el botón, copia y pega este enlace en tu navegador:</p>
                        <p style="background-color: #f0f0f0; padding: 10px; border-radius: 5px; word-break: break-all; font-size: 12px;">{verification_link}</p>
                        <p style="color: #999; font-size: 12px; margin-top: 30px;">Este enlace expirará en 24 horas.</p>
                    </div>
                    <div class="footer">
                        <p>Jorge Calcerrada - Entrenador Personal</p>
                        <p>Si no solicitaste esto, puedes ignorar este email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            send_email(
                to_email=email,
                subject="✅ Verifica tu email - CRM Fusion",
                html_body=email_html
            )
            
            logger.info(f"Email de verificación reenviado a {email}")
        except Exception as e:
            logger.error(f"Error reenviando email de verificación: {e}")
            raise HTTPException(
                status_code=500,
                detail="Error al enviar email de verificación"
            )
        
        return {
            "success": True,
            "message": "Email de verificación enviado. Por favor revisa tu bandeja de entrada."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en resend verification: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error al reenviar email de verificación"
        )




@api_router.get("/auth/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    return {
        "id": user["_id"],
        "username": user["username"],
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "subscription": user["subscription"]
    }




@api_router.patch("/users/me")
async def update_my_profile(user_update: UserUpdate, request: Request):
    """Update current user's profile"""
    user = await get_current_user(request)
    user_id = user["_id"]
    
    update_data = {}
    
    if user_update.name:
        update_data["name"] = user_update.name
    
    if user_update.email:
        # Check if email is already taken by another user
        existing_user = await db.users.find_one({"email": user_update.email, "_id": {"$ne": user_id}})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        update_data["email"] = user_update.email
    
    if user_update.phone:
        update_data["phone"] = user_update.phone
    
    if user_update.password:
        update_data["password"] = get_password_hash(user_update.password)
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.users.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get updated user
    updated_user = await db.users.find_one({"_id": user_id})
    
    return {
        "success": True,
        "message": "Profile updated successfully",
        "user": {
            "id": updated_user["_id"],
            "name": updated_user["name"],
            "email": updated_user["email"],
            "phone": updated_user.get("phone"),
            "role": updated_user["role"]
        }
    }


@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """
    Logout user by removing session from database and clearing cookie
    """
    session_token = request.cookies.get("session_token")
    
    if session_token:
        # Delete session from database
        await db.user_sessions.delete_one({"session_token": session_token})
    
    # Clear cookie
    response.delete_cookie(key="session_token", path="/")
    
    return {"success": True, "message": "Logged out successfully"}



@api_router.post("/auth/reset-password")
async def reset_password(reset_data: PasswordReset):
    """Reset password using token"""
    # Find reset token
    reset_doc = await db.password_resets.find_one({"token": reset_data.token})
    
    if not reset_doc:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # Check if token is expired
    if reset_doc["expires_at"].replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        await db.password_resets.delete_one({"token": reset_data.token})
        raise HTTPException(status_code=400, detail="Token has expired")
    
    # Update user password
    hashed_password = get_password_hash(reset_data.new_password)
    result = await db.users.update_one(
        {"_id": reset_doc["user_id"]},
        {"$set": {
            "password": hashed_password,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Delete used token
    await db.password_resets.delete_one({"token": reset_data.token})
    
    return {"success": True, "message": "Password reset successfully"}



@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """
    Logout user by removing session from database and clearing cookie
    """
    session_token = request.cookies.get("session_token")
    
    if session_token:
        # Delete session from database
        await db.user_sessions.delete_one({"session_token": session_token})
    
    # Clear cookie
    response.delete_cookie(key="session_token", path="/")
    
    return {"success": True, "message": "Logged out successfully"}


# ==================== USER ENDPOINTS ====================

@api_router.get("/users/dashboard")
async def get_user_dashboard(request: Request):
    user = await get_current_user(request)
    user_id = user["_id"]
    
    # Get forms
    forms = await db.forms.find({"user_id": user_id}).to_list(100)
    for form in forms:
        form["id"] = str(form["_id"])
        # Convertir fechas a ISO string
        if "sent_date" in form and form["sent_date"]:
            form["sent_date"] = form["sent_date"].isoformat() if hasattr(form["sent_date"], 'isoformat') else form["sent_date"]
    
    # Get nutrition questionnaire submissions and add as 'nutrition' type form
    nutrition_submissions = await db.nutrition_questionnaire_submissions.find({"user_id": user_id}).to_list(100)
    for submission in nutrition_submissions:
        forms.append({
            "id": str(submission["_id"]),
            "type": "nutrition",
            "submitted_at": submission.get("submitted_at").isoformat() if submission.get("submitted_at") else None,
            "data": submission.get("responses", {}),
            "plan_generated": submission.get("plan_generated", False),
            "plan_id": submission.get("plan_id")
        })
    
    # Get PDFs
    # Exclude file_data from PDFs to avoid serialization issues
    pdfs = await db.pdfs.find(
        {"user_id": user_id},
        {"file_data": 0}
    ).to_list(100)
    for pdf in pdfs:
        pdf["id"] = str(pdf["_id"])
        # Convertir fechas a ISO string para que el frontend pueda parsearlas
        if "sent_date" in pdf and pdf["sent_date"]:
            pdf["upload_date"] = pdf["sent_date"].isoformat() if hasattr(pdf["sent_date"], 'isoformat') else pdf["sent_date"]
        elif "upload_date" in pdf and pdf["upload_date"]:
            pdf["upload_date"] = pdf["upload_date"].isoformat() if hasattr(pdf["upload_date"], 'isoformat') else pdf["upload_date"]
        elif "created_at" in pdf and pdf["created_at"]:
            pdf["upload_date"] = pdf["created_at"].isoformat() if hasattr(pdf["created_at"], 'isoformat') else pdf["created_at"]
    
    # Get alerts
    alerts = await db.alerts.find({"user_id": user_id}).to_list(100)
    for alert in alerts:
        alert["id"] = str(alert["_id"])
        # Convertir fechas a ISO string
        if "date" in alert and alert["date"]:
            alert["date"] = alert["date"].isoformat() if hasattr(alert["date"], 'isoformat') else alert["date"]
    
    # Count unread alerts
    unread_count = len([a for a in alerts if not a.get("read", False)])
    
    # Get nutrition plan (check if user has any nutrition plan)
    nutrition_plan = await db.nutrition_plans.find_one(
        {"user_id": user_id},
        sort=[("generated_at", -1)]  # Get most recent plan
    )
    
    if nutrition_plan:
        nutrition_plan["id"] = str(nutrition_plan["_id"])
    
    return {
        "user": {
            "id": str(user["_id"]),
            "username": user["username"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "subscription": user["subscription"],
            "next_review": user.get("next_review"),
            "nutrition_plan": nutrition_plan,  # Add nutrition plan info
            "followup_activated": user.get("followup_activated", False)  # Incluir estado de activación del cuestionario de seguimiento
        },
        "forms": forms,
        "pdfs": pdfs,
        "alerts": alerts,
        "unread_alerts": unread_count
    }


# ==================== ADMIN ENDPOINTS ====================

@api_router.get("/admin/clients")
async def get_all_clients(request: Request):
    admin = await require_admin(request)
    # Ya NO necesitamos filtrar "deleted" porque ahora es HARD DELETE
    users = await db.users.find({
        "role": "user"
    }).to_list(1000)
    
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]  # Eliminar _id de MongoDB
        if "password" in user:
            del user["password"]
    
    # Calculate stats
    total = len(users)
    active = len([u for u in users if u.get("subscription", {}).get("payment_status") == "verified"])
    pending = len([u for u in users if u.get("subscription", {}).get("payment_status") == "pending"])
    
    return {
        "clients": users,
        "stats": {
            "total": total,
            "active": active,
            "pending": pending
        }
    }


@api_router.get("/admin/clients/{user_id}")
async def get_client_details(user_id: str, request: Request):
    admin = await require_admin(request)
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get forms, pdfs, alerts for this user
    forms = await db.forms.find({"user_id": user_id}).to_list(100)
    # Exclude file_data from PDFs to avoid serialization issues
    pdfs = await db.pdfs.find(
        {"user_id": user_id},
        {"file_data": 0}  # Exclude binary data
    ).to_list(100)
    alerts = await db.alerts.find({"user_id": user_id}).to_list(100)
    
    # Get nutrition questionnaire submissions and add as 'nutrition' type form
    nutrition_submissions = await db.nutrition_questionnaire_submissions.find({"user_id": user_id}).to_list(100)
    
    for form in forms:
        form["id"] = str(form["_id"])
    for pdf in pdfs:
        pdf["id"] = str(pdf["_id"])
        # Convert upload_date to ISO string for JavaScript
        if pdf.get("upload_date"):
            if isinstance(pdf["upload_date"], datetime):
                pdf["upload_date"] = pdf["upload_date"].isoformat()
            # If already a string, leave it as is
    for alert in alerts:
        alert["id"] = str(alert["_id"])
    
    # Add nutrition submissions to forms list with type 'nutrition'
    for submission in nutrition_submissions:
        submitted_at = submission.get("submitted_at")
        if isinstance(submitted_at, datetime):
            submitted_at = submitted_at.isoformat()
        
        nutrition_form = {
            "id": str(submission["_id"]),
            "type": "nutrition",
            "submitted_at": submitted_at,
            "data": submission.get("responses", {}),
            "plan_generated": submission.get("plan_generated", False),
            "plan_id": submission.get("plan_id")
        }
        forms.append(nutrition_form)
    
    user["id"] = str(user["_id"])
    del user["password"]
    
    return {
        "user": user,
        "forms": forms,
        "pdfs": pdfs,
        "alerts": alerts
    }


@api_router.get("/admin/users/{user_id}/edn360-input-preview")
async def get_edn360_input_preview(user_id: str, request: Request):
    """
    Vista previa del EDN360Input para un usuario.
    
    FASE 2: Este endpoint construye y devuelve el JSON EDN360Input que
    usaremos como contrato de entrada para los Workflows de OpenAI.
    
    NO llama a ningún modelo de IA, solo construye y devuelve el input.
    
    Respuestas:
    - 200 OK: Devuelve el JSON EDN360Input completo
    - 404 Not Found: Usuario no existe o no tiene client_drawer
    - 500 Internal Server Error: Error inesperado
    
    Solo accesible para administradores.
    """
    # Verificar que es admin
    admin = await require_admin(request)
    
    try:
        # Importar el builder
        from services.edn360_input_builder import build_edn360_input_for_user
        from edn360_models.edn360_input import EDN360NoDrawerError, EDN360NoQuestionnaireError
        
        # Construir el EDN360Input
        edn360_input = await build_edn360_input_for_user(user_id)
        
        # Serializar a JSON
        edn360_input_json = edn360_input.dict()
        
        logger.info(
            f"✅ EDN360Input generado para user_id {user_id}: "
            f"{edn360_input.questionnaire_count()} cuestionario(s)"
        )
        
        return {
            "success": True,
            "user_id": user_id,
            "edn360_input": _serialize_datetime_fields(edn360_input_json),
            "metadata": {
                "questionnaires_count": edn360_input.questionnaire_count(),
                "has_initial": edn360_input.get_initial_questionnaire() is not None,
                "has_followups": edn360_input.has_followups(),
                "generated_at": edn360_input.generated_at.isoformat(),
                "version": edn360_input.version
            }
        }
    
    except EDN360NoDrawerError as e:
        logger.warning(f"⚠️  No drawer para user_id {user_id}: {e}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "no_drawer",
                "message": str(e),
                "user_id": user_id
            }
        )
    
    except EDN360NoQuestionnaireError as e:
        logger.warning(f"⚠️  Drawer sin cuestionarios para user_id {user_id}: {e}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "no_questionnaires",
                "message": str(e),
                "user_id": user_id
            }
        )
    
    except Exception as e:
        logger.error(f"❌ Error generando EDN360Input para user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error generando EDN360Input: {str(e)}",
                "user_id": user_id
            }
        )


@api_router.post("/admin/users/{user_id}/edn360-run-workflow")
async def admin_run_edn360_workflow(user_id: str, request: Request):
    """
    Lanza el Workflow EDN360 para un usuario (FASE 3 - Testing Interno).
    
    Este endpoint:
    1. Construye el EDN360Input para el usuario
    2. Llama al Workflow de OpenAI con ese input
    3. Crea un snapshot técnico inmutable en edn360_snapshots
    
    IMPORTANTE:
    - Este endpoint es solo para TESTING INTERNO desde panel admin
    - NO modifica training_plans ni nutrition_plans
    - NO envía planes a clientes finales
    - Solo crea snapshots técnicos en BD para validar el flujo
    
    Respuestas:
    - 200 OK: Workflow ejecutado, snapshot creado (success o failed)
    - 404 Not Found: Usuario no existe
    - 500 Internal Server Error: Error inesperado
    
    Solo accesible para administradores.
    """
    # Verificar que es admin
    admin = await require_admin(request)
    
    try:
        # Verificar que el usuario existe
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "user_not_found",
                    "message": f"Usuario {user_id} no encontrado",
                    "user_id": user_id
                }
            )
        
        logger.info(f"🚀 Admin {admin['_id']} lanzando Workflow EDN360 para user_id: {user_id}")
        
        # Importar el orquestador
        from services.edn360_orchestrator_v1 import run_edn360_workflow_for_user
        
        # Ejecutar el workflow
        result = await run_edn360_workflow_for_user(user_id)
        
        # Logear resultado
        if result["status"] == "success":
            logger.info(
                f"✅ Workflow EDN360 ejecutado exitosamente | "
                f"user_id: {user_id} | snapshot_id: {result['snapshot_id']}"
            )
        else:
            logger.warning(
                f"⚠️  Workflow EDN360 falló | "
                f"user_id: {user_id} | error: {result.get('error_message')}"
            )
        
        return {
            "success": True,
            "result": _serialize_datetime_fields(result),
            "message": "Workflow EDN360 ejecutado. Snapshot creado en BD."
        }
    
    except HTTPException:
        # Re-lanzar HTTPExceptions
        raise
    
    except Exception as e:
        logger.error(f"❌ Error ejecutando Workflow EDN360 para user_id {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error ejecutando Workflow EDN360: {str(e)}",
                "user_id": user_id
            }
        )


@api_router.post("/admin/verify-payment/{user_id}")
async def verify_payment(user_id: str, request: Request):
    admin = await require_admin(request)
    result = await db.users.update_one(
        {"_id": user_id},
        {"$set": {
            "subscription.payment_status": "verified",
            "subscription.status": "active",
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "message": "Payment verified successfully"}


from fastapi import BackgroundTasks

@api_router.post("/training-plan")
async def generate_training_plan(request: Request, background_tasks: BackgroundTasks):
    """
    Genera un plan de entrenamiento EVOLUTIVO usando el workflow EDN360 (E1-E7.5).
    
    GENERACION ASINCRONA - No bloquea el servidor.
    
    FLUJO EVOLUTIVO CON STATE:
    1. Recibe user_id y current_questionnaire_id
    2. Construye el objeto `state` con historial completo:
       - initial_questionnaire: Primer cuestionario del usuario
       - previous_followups: Todos los seguimientos anteriores (excepto el actual)
       - previous_plans: Todos los planes generados previamente
       - last_plan: El plan más reciente
    3. Construye el objeto `input` con el cuestionario actual
    4. Llama al workflow con input + state
    5. Guarda snapshot y plan en BD
    6. Devuelve client_training_program_enriched
    
    Request Body:
    {
        "user_id": "1764016044644335",
        "current_questionnaire_id": "quest_followup_002"
    }
    
    Response:
    {
        "client_training_program_enriched": {
            "title": "Hipertrofia...",
            "sessions": [...],
            ...
        }
    }
    
    Auth: Admin only
    """
    # Obtener admin autenticado
    admin = await require_admin(request)
    
    try:
        # Parsear body
        body = await request.json()
        
        user_id = body.get("user_id")
        questionnaire_ids = body.get("questionnaire_ids", [])
        previous_training_plan_id = body.get("previous_training_plan_id")
        
        # Validaciones
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "missing_fields",
                    "message": "Se requiere user_id"
                }
            )
        
        if not questionnaire_ids or len(questionnaire_ids) == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "missing_questionnaires",
                    "message": "Se requiere al menos un cuestionario en questionnaire_ids"
                }
            )
        
        # El current_questionnaire_id es el ÚLTIMO en el array
        # (el "Cuestionario Nuevo" de la UI)
        current_questionnaire_id = questionnaire_ids[-1]
        
        logger.info(
            f"🏋️ Generando plan de entrenamiento EVOLUTIVO | "
            f"admin: {admin['_id']} | user_id: {user_id} | "
            f"questionnaire_ids: {questionnaire_ids} | "
            f"current (último): {current_questionnaire_id} | "
            f"previous_plan_id: {previous_training_plan_id or 'none'}"
        )
        
        # ============================================
        # PASO 1: VALIDAR USUARIO
        # ============================================
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "user_not_found",
                    "message": f"Usuario {user_id} no encontrado"
                }
            )
        
        # ============================================
        # PASO 2: RECUPERAR TODOS LOS CUESTIONARIOS
        # ============================================
        try:
            from repositories.client_drawer_repository import get_drawer_by_user_id
            
            drawer = await get_drawer_by_user_id(user_id)
            if not drawer:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "no_drawer",
                        "message": f"Usuario {user_id} no tiene client_drawer"
                    }
                )
            
            all_questionnaires = drawer.services.shared_questionnaires
            if not all_questionnaires:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "no_questionnaires",
                        "message": f"Usuario {user_id} no tiene cuestionarios"
                    }
                )
            
            # Ordenar por fecha (más antiguo → más reciente)
            all_questionnaires.sort(key=lambda q: q.submitted_at)
            
            # CRÍTICO: initial_questionnaire SIEMPRE es el más antiguo de BD
            # independientemente de lo que se seleccione en la UI
            initial_questionnaire = all_questionnaires[0]
            
            # Encontrar el cuestionario actual (el último en questionnaire_ids de la UI)
            current_q = None
            current_q_index = -1
            for i, q in enumerate(all_questionnaires):
                if q.submission_id == current_questionnaire_id:
                    current_q = q
                    current_q_index = i
                    break
            
            if not current_q:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "questionnaire_not_found",
                        "message": f"Cuestionario {current_questionnaire_id} no encontrado"
                    }
                )
            
            # previous_followups: todos los cuestionarios entre el inicial y el actual
            # EXCLUYENDO el inicial y el actual
            previous_followups = all_questionnaires[1:current_q_index] if current_q_index > 1 else []
            
            logger.info(
                f"✅ Cuestionarios recuperados | "
                f"Total en BD: {len(all_questionnaires)} | "
                f"Initial (más antiguo): {initial_questionnaire.submission_id} | "
                f"Previous followups: {len(previous_followups)} | "
                f"Current: {current_q.submission_id}"
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error recuperando cuestionarios: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "questionnaire_fetch_error",
                    "message": f"Error recuperando cuestionarios: {str(e)}"
                }
            )
        
        # ============================================
        # PASO 3: RECUPERAR PLANES PREVIOS
        # ============================================
        try:
            edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
            
            # Recuperar todos los planes del usuario ordenados por fecha
            all_plans_cursor = edn360_db.training_plans_v2.find(
                {"user_id": user_id},
                {"_id": 1, "created_at": 1, "plan": 1}
            ).sort("created_at", 1)  # Ascendente (más antiguo → más reciente)
            
            all_plans = await all_plans_cursor.to_list(length=100)
            
            # Si se seleccionó un previous_training_plan_id en la UI,
            # usar solo los planes hasta ese ID (inclusive)
            if previous_training_plan_id:
                logger.info(f"📋 Filtrando planes hasta: {previous_training_plan_id}")
                
                # Buscar el plan seleccionado
                selected_plan_index = -1
                for i, plan in enumerate(all_plans):
                    plan_id = str(plan.get("_id", ""))
                    # También verificar formato "edn360_{i}_{created_at}"
                    if plan_id == previous_training_plan_id or plan.get("created_at") == previous_training_plan_id:
                        selected_plan_index = i
                        break
                
                if selected_plan_index >= 0:
                    # Incluir todos los planes hasta el seleccionado (inclusive)
                    previous_plans = all_plans[:selected_plan_index + 1]
                    last_plan = previous_plans[-1] if previous_plans else None
                    logger.info(f"✅ Planes filtrados hasta índice {selected_plan_index}: {len(previous_plans)} planes")
                else:
                    logger.warning(f"⚠️ Plan seleccionado {previous_training_plan_id} no encontrado, usando todos los planes")
                    previous_plans = all_plans
                    last_plan = previous_plans[-1] if previous_plans else None
            else:
                # No se seleccionó plan previo en UI
                # CASO A: Si no hay planes, esto es el primer plan
                previous_plans = all_plans
                last_plan = previous_plans[-1] if previous_plans else None
            
            logger.info(
                f"✅ Planes previos recuperados | "
                f"Total en BD: {len(all_plans)} | "
                f"Previous plans en STATE: {len(previous_plans)} | "
                f"Has last_plan: {bool(last_plan)}"
            )
        
        except Exception as e:
            logger.warning(f"⚠️ Error recuperando planes previos: {e}")
            previous_plans = []
            last_plan = None
        
        # ============================================
        # PASO 4: CONSTRUIR OBJETO STATE
        # ============================================
        try:
            # Construir el user_profile
            from services.edn360_input_builder import _build_user_profile
            user_profile = await _build_user_profile(user_id)
            
            if not user_profile:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "user_profile_error",
                        "message": f"No se pudo construir el perfil del usuario {user_id}"
                    }
                )
            
            # Función helper para serializar cuestionarios
            def serialize_questionnaire(q):
                return {
                    "submission_id": q.submission_id,
                    "submitted_at": q.submitted_at.isoformat() if hasattr(q.submitted_at, 'isoformat') else str(q.submitted_at),
                    "source": q.source,
                    "payload": _serialize_datetime_fields(q.raw_payload)
                }
            
            # Construir el objeto state
            state = {
                "initial_questionnaire": serialize_questionnaire(initial_questionnaire),
                "previous_followups": [serialize_questionnaire(q) for q in previous_followups],
                "previous_plans": previous_plans,
                "last_plan": last_plan
            }
            
            logger.info(
                f"✅ Objeto STATE construido | "
                f"Has initial: True | Previous followups: {len(previous_followups)} | "
                f"Previous plans: {len(previous_plans)} | Has last_plan: {bool(last_plan)}"
            )
        
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error construyendo STATE: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "state_build_error",
                    "message": f"Error construyendo STATE: {str(e)}"
                }
            )
        
        # ============================================
        # PASO 5: CONSTRUIR OBJETO INPUT
        # ============================================
        try:
            # El input contiene el cuestionario ACTUAL
            workflow_input = {
                "input": {
                    "input_as_text": json.dumps({
                        "user_profile": _serialize_datetime_fields(user_profile.dict()),
                        "current_questionnaire": serialize_questionnaire(current_q)
                    })
                },
                "state": state
            }
            
            logger.info(f"✅ Objeto INPUT construido con STATE")
        
        except Exception as e:
            logger.error(f"❌ Error construyendo INPUT: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "input_build_error",
                    "message": f"Error construyendo INPUT: {str(e)}"
                }
            )
        
        # ============================================
        # PASO 6: CREAR PLAN CON STATUS "generating" Y LANZAR BACKGROUND TASK
        # ============================================
        # Crear un plan_id único
        from uuid import uuid4
        plan_id = str(uuid4())
        
        # Guardar plan inicial con status="generating"
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        initial_plan_doc = {
            "id": plan_id,
            "user_id": user_id,
            "status": "generating",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "plan": None
        }
        await edn360_db.training_plans_v2.insert_one(initial_plan_doc)
        
        # Lanzar generación en background
        background_tasks.add_task(
            _generate_plan_background,
            plan_id,
            user_id,
            workflow_input,
            state,
            admin['_id']
        )
        
        logger.info(f"✅ Plan creado con status='generating' | plan_id: {plan_id} | Background task iniciado")
        
        # Devolver inmediatamente
        return {
            "plan_id": plan_id,
            "status": "generating",
            "message": "El plan se está generando. Consulta el status con GET /api/admin/users/{user_id}/training-plans/latest"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error inesperado en /training-plan: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error interno del servidor: {str(e)}"
            }
        )


async def _generate_plan_background(plan_id: str, user_id: str, workflow_input: dict, state: dict, admin_id: str):
    """
    Función background para generar el plan sin bloquear el servidor.
    """
    try:
        from services.training_workflow_service import call_training_workflow_with_state
        
        logger.info(f"🔄 [Background] Iniciando generación del plan | plan_id: {plan_id}")
        
        # ============================================
        # LLAMAR AL WORKFLOW EDN360
        # ============================================
        try:
            workflow_response = await call_training_workflow_with_state(workflow_input)
            
            logger.info(f"✅ [Background] Training workflow ejecutado | plan_id: {plan_id}")
        
        except Exception as e:
            logger.error(f"❌ [Background] Error ejecutando training workflow: {e}")
            
            # Actualizar status a "error"
            edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
            await edn360_db.training_plans_v2.update_one(
                {"id": plan_id},
                {"$set": {"status": "error", "error_message": str(e)}}
            )
            return
        
        # ============================================
        # PASO 7: TRADUCIR Y GUARDAR EN TRAINING_PLANS_V2
        # ============================================
        training_program = workflow_response.get("client_training_program_enriched")
        
        if not training_program:
            logger.error(f"❌ [Background] No se recibió training_program | plan_id: {plan_id}")
            edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
            await edn360_db.training_plans_v2.update_one(
                {"id": plan_id},
                {"$set": {"status": "error", "error_message": "Workflow no devolvió plan válido"}}
            )
            return
        
        # Traducir el plan a español
        training_program = _translate_training_plan_to_spanish(training_program)
        
        # ============================================
        # PASO 8: INTEGRAR PLANTILLAS DE 4 BLOQUES
        # ============================================
        try:
            logger.info("🔧 ========== INICIANDO INTEGRACIÓN DE PLANTILLAS 4-BLOQUES ==========")
            
            # Obtener datos del usuario para selección de plantillas
            # Try both databases - trainsmart and edn360_app
            db = client[os.getenv('MONGO_DB_NAME', 'trainsmart')]
            edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
            
            user = None
            # Try trainsmart database first
            user = await db.users.find_one({"_id": user_id})
            if not user:
                user = await db.users.find_one({"_id": str(user_id)})
            if not user:
                try:
                    user = await db.users.find_one({"_id": int(user_id)})
                except ValueError:
                    pass
            
            # If not found in trainsmart, try edn360_app database
            if not user:
                user = await edn360_db.users.find_one({"_id": user_id})
            if not user:
                user = await edn360_db.users.find_one({"_id": str(user_id)})
            if not user:
                try:
                    user = await edn360_db.users.find_one({"_id": int(user_id)})
                except ValueError:
                    pass
            
            logger.info(f"🔍 User lookup result: {'Found' if user else 'Not found'} | user_id: {user_id} | type: {type(user_id)}")
            
            # Obtener el cuestionario inicial para datos del usuario (desde state)
            initial_questionnaire = state.get("initial_questionnaire", {})
            questionnaire_payload = initial_questionnaire.get("payload", {})
            
            if questionnaire_payload:
                # Log questionnaire keys for debugging
                logger.info(f"🔍 Questionnaire payload keys: {list(questionnaire_payload.keys())[:20]}")
                logger.info(f"🔍 experience_level: {questionnaire_payload.get('experience_level')}")
                logger.info(f"🔍 goal_primary: {questionnaire_payload.get('goal_primary')}")
                
                # Extraer datos del usuario para selección de plantillas
                user_data_for_templates = {
                    'edad': questionnaire_payload.get('edad', questionnaire_payload.get('age', 0)),
                    'nivel': questionnaire_payload.get('experience_level', questionnaire_payload.get('nivel', 'principiante')).lower(),
                    'objetivo': questionnaire_payload.get('goal_primary', questionnaire_payload.get('objetivo', 'mantenimiento')).lower(),
                    'lesion_hombro': questionnaire_payload.get('injuries_or_limitations', '').lower().find('hombro') != -1,
                    'lesion_lumbar': questionnaire_payload.get('injuries_or_limitations', '').lower().find('lumbar') != -1 or 
                                   questionnaire_payload.get('injuries_or_limitations', '').lower().find('espalda baja') != -1,
                    'muy_sedentario': questionnaire_payload.get('lifestyle_activity', '').lower() == 'sedentary',
                    'primera_sesion': not bool(state.get("last_plan"))
                }
                
                logger.info(f"🔧 user_data_for_templates: {user_data_for_templates}")
                
                # Contar planes previos para determinar número de mes
                edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
                planes_previos_count = await edn360_db.training_plans_v2.count_documents({"user_id": user_id})
                numero_mes = planes_previos_count + 1
                
                # Integrar plantillas en el plan
                training_program = await _integrate_template_blocks(
                    training_program, 
                    user_data_for_templates,
                    week_number=numero_mes,
                    session_number_start=1
                )
                
                # Verificar que se agregaron los bloques estructurados
                if training_program.get('sessions') and len(training_program['sessions']) > 0:
                    first_session = training_program['sessions'][0]
                    if 'bloques_estructurados' in first_session:
                        logger.info("✅ Primera sesión TIENE bloques_estructurados")
                        logger.info(f"   Bloques: {list(first_session['bloques_estructurados'].keys())}")
                    else:
                        logger.error("❌ Primera sesión NO TIENE bloques_estructurados!")
                
                logger.info("✅ Plantillas 4-bloques integradas exitosamente")
            else:
                logger.warning("⚠️ Cuestionario no encontrado en state, saltando integración de plantillas")
                
        except Exception as e:
            logger.error(f"❌ Error integrando plantillas 4-bloques: {e}")
            # Continuar sin las plantillas si hay error
        
        # Actualizar el plan en BD con status="draft"
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        last_plan = state.get("last_plan")
        
        await edn360_db.training_plans_v2.update_one(
            {"id": plan_id},
            {"$set": {
                "status": "draft",
                "plan": _serialize_datetime_fields(training_program),
                "is_evolutionary": bool(last_plan),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }}
        )
        
        logger.info(f"✅ [Background] Plan generado y guardado | plan_id: {plan_id} | title: {training_program.get('title', 'N/A')}")
    
    except Exception as e:
        logger.error(f"❌ [Background] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        
        try:
            edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
            await edn360_db.training_plans_v2.update_one(
                {"id": plan_id},
                {"$set": {"status": "error", "error_message": str(e)}}
            )
        except:
            pass


@api_router.post("/training-plan/mock")
async def generate_training_plan_mock(request: Request):
    """
    Endpoint MOCK para testing - Genera un plan de entrenamiento de ejemplo.
    
    Este endpoint devuelve un plan hardcodeado con la estructura correcta:
    sessions[].blocks[].exercises[]
    
    Útil para:
    - Testing del flujo de persistencia
    - Desarrollo del Card Editable en frontend
    - Verificación de estructura de datos
    
    Request Body:
    {
        "user_id": "1764016044644335"
    }
    
    Response: client_training_program_enriched completo
    
    Auth: Admin only
    """
    admin = await require_admin(request)
    
    try:
        body = await request.json()
        user_id = body.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail={"error": "missing_user_id", "message": "Se requiere user_id"}
            )
        
        logger.info(f"🧪 Generando plan MOCK | admin: {admin['_id']} | user_id: {user_id}")
        
        # Plan de entrenamiento MOCK con estructura final
        mock_plan = {
            "client_training_program_enriched": {
                "title": "Plan de Hipertrofia Upper/Lower - 4 días/semana",
                "summary": "Programa de entrenamiento orientado a hipertrofia muscular, dividido en tren superior e inferior, 4 sesiones semanales de 60 minutos.",
                "goal": "Aumentar masa muscular con enfoque en técnica segura, considerando molestia en hombro izquierdo.",
                "training_type": "upper_lower",
                "days_per_week": 4,
                "session_duration_min": 60,
                "weeks": 8,
                "sessions": [
                    {
                        "id": "D1",
                        "name": "Upper 1 – Push Dominante",
                        "focus": ["upper_body", "push", "chest", "shoulders", "triceps"],
                        "blocks": [
                            {
                                "id": "A",
                                "primary_muscles": ["chest"],
                                "secondary_muscles": ["triceps", "shoulders"],
                                "exercises": [
                                    {
                                        "order": 1,
                                        "db_id": "E123",
                                        "name": "Press banca con barra",
                                        "primary_group": "Pecho",
                                        "secondary_group": "Tríceps",
                                        "series": 4,
                                        "reps": "8-10",
                                        "rpe": "8",
                                        "notes": "Control en descenso, evitar arqueo excesivo",
                                        "video_url": "https://drive.google.com/example1"
                                    },
                                    {
                                        "order": 2,
                                        "db_id": "E124",
                                        "name": "Press inclinado con mancuernas",
                                        "primary_group": "Pecho",
                                        "secondary_group": "Hombros",
                                        "series": 3,
                                        "reps": "10-12",
                                        "rpe": "7-8",
                                        "notes": "Inclinación 30-45°, cuidar hombros",
                                        "video_url": "https://drive.google.com/example2"
                                    }
                                ]
                            },
                            {
                                "id": "B",
                                "primary_muscles": ["shoulders"],
                                "secondary_muscles": ["triceps"],
                                "exercises": [
                                    {
                                        "order": 3,
                                        "db_id": "E201",
                                        "name": "Elevaciones laterales con mancuernas",
                                        "primary_group": "Hombros",
                                        "secondary_group": "Trapecio",
                                        "series": 3,
                                        "reps": "12-15",
                                        "rpe": "7",
                                        "notes": "Evitar overhead por molestia en hombro",
                                        "video_url": "https://drive.google.com/example3"
                                    },
                                    {
                                        "order": 4,
                                        "db_id": "E202",
                                        "name": "Press francés con barra Z",
                                        "primary_group": "Tríceps",
                                        "secondary_group": "",
                                        "series": 3,
                                        "reps": "10-12",
                                        "rpe": "7-8",
                                        "notes": "Control del movimiento, proteger codos",
                                        "video_url": "https://drive.google.com/example4"
                                    }
                                ]
                            }
                        ],
                        "session_notes": [
                            "Calentar hombros con rotaciones y banda elástica",
                            "Si hay dolor en hombro, reducir peso o saltar ejercicio",
                            "Finalizar con 5 min de estiramientos de pecho y hombros"
                        ]
                    },
                    {
                        "id": "D2",
                        "name": "Lower 1 – Cuádriceps Dominante",
                        "focus": ["lower_body", "quads", "glutes"],
                        "blocks": [
                            {
                                "id": "A",
                                "primary_muscles": ["quads"],
                                "secondary_muscles": ["glutes", "core"],
                                "exercises": [
                                    {
                                        "order": 1,
                                        "db_id": "E301",
                                        "name": "Sentadilla con barra",
                                        "primary_group": "Cuádriceps",
                                        "secondary_group": "Glúteos",
                                        "series": 4,
                                        "reps": "6-8",
                                        "rpe": "8",
                                        "notes": "Profundidad controlada, core activado",
                                        "video_url": "https://drive.google.com/example5"
                                    },
                                    {
                                        "order": 2,
                                        "db_id": "E302",
                                        "name": "Prensa de piernas",
                                        "primary_group": "Cuádriceps",
                                        "secondary_group": "Glúteos",
                                        "series": 3,
                                        "reps": "10-12",
                                        "rpe": "7-8",
                                        "notes": "Rango completo sin despegar zona lumbar",
                                        "video_url": "https://drive.google.com/example6"
                                    }
                                ]
                            },
                            {
                                "id": "B",
                                "primary_muscles": ["quads"],
                                "secondary_muscles": [],
                                "exercises": [
                                    {
                                        "order": 3,
                                        "db_id": "E303",
                                        "name": "Extensión de cuádriceps en máquina",
                                        "primary_group": "Cuádriceps",
                                        "secondary_group": "",
                                        "series": 3,
                                        "reps": "12-15",
                                        "rpe": "7",
                                        "notes": "Movimiento controlado, contracción en pico",
                                        "video_url": "https://drive.google.com/example7"
                                    }
                                ]
                            }
                        ],
                        "session_notes": [
                            "Calentar con movilidad de cadera y sentadillas sin peso",
                            "Mantener core activo en todos los ejercicios",
                            "Finalizar con estiramientos de cuádriceps e isquios"
                        ]
                    },
                    {
                        "id": "D3",
                        "name": "Upper 2 – Pull Dominante",
                        "focus": ["upper_body", "pull", "back", "biceps"],
                        "blocks": [
                            {
                                "id": "A",
                                "primary_muscles": ["back"],
                                "secondary_muscles": ["biceps"],
                                "exercises": [
                                    {
                                        "order": 1,
                                        "db_id": "E401",
                                        "name": "Dominadas con agarre prono",
                                        "primary_group": "Espalda",
                                        "secondary_group": "Bíceps",
                                        "series": 4,
                                        "reps": "6-8",
                                        "rpe": "8",
                                        "notes": "Usar lastre si es necesario, full ROM",
                                        "video_url": "https://drive.google.com/example8"
                                    },
                                    {
                                        "order": 2,
                                        "db_id": "E402",
                                        "name": "Remo con barra",
                                        "primary_group": "Espalda",
                                        "secondary_group": "Bíceps",
                                        "series": 4,
                                        "reps": "8-10",
                                        "rpe": "7-8",
                                        "notes": "Mantener espalda neutra, tirar hacia ombligo",
                                        "video_url": "https://drive.google.com/example9"
                                    }
                                ]
                            },
                            {
                                "id": "B",
                                "primary_muscles": ["biceps"],
                                "secondary_muscles": [],
                                "exercises": [
                                    {
                                        "order": 3,
                                        "db_id": "E403",
                                        "name": "Curl con barra Z",
                                        "primary_group": "Bíceps",
                                        "secondary_group": "",
                                        "series": 3,
                                        "reps": "10-12",
                                        "rpe": "7",
                                        "notes": "Sin balanceo, control en excéntrica",
                                        "video_url": "https://drive.google.com/example10"
                                    }
                                ]
                            }
                        ],
                        "session_notes": [
                            "Calentar con band pull-aparts y movimientos de escápulas",
                            "Enfoque en contracción de dorsales",
                            "Finalizar con estiramientos de espalda y bíceps"
                        ]
                    },
                    {
                        "id": "D4",
                        "name": "Lower 2 – Isquios y Glúteos Dominante",
                        "focus": ["lower_body", "hamstrings", "glutes"],
                        "blocks": [
                            {
                                "id": "A",
                                "primary_muscles": ["hamstrings", "glutes"],
                                "secondary_muscles": ["lower_back"],
                                "exercises": [
                                    {
                                        "order": 1,
                                        "db_id": "E501",
                                        "name": "Peso muerto rumano",
                                        "primary_group": "Isquiotibiales",
                                        "secondary_group": "Glúteos",
                                        "series": 4,
                                        "reps": "8-10",
                                        "rpe": "8",
                                        "notes": "Bisagra de cadera, espalda neutra",
                                        "video_url": "https://drive.google.com/example11"
                                    },
                                    {
                                        "order": 2,
                                        "db_id": "E502",
                                        "name": "Hip thrust con barra",
                                        "primary_group": "Glúteos",
                                        "secondary_group": "Isquiotibiales",
                                        "series": 3,
                                        "reps": "10-12",
                                        "rpe": "7-8",
                                        "notes": "Contracción máxima en la parte superior",
                                        "video_url": "https://drive.google.com/example12"
                                    }
                                ]
                            },
                            {
                                "id": "B",
                                "primary_muscles": ["hamstrings"],
                                "secondary_muscles": [],
                                "exercises": [
                                    {
                                        "order": 3,
                                        "db_id": "E503",
                                        "name": "Curl femoral en máquina",
                                        "primary_group": "Isquiotibiales",
                                        "secondary_group": "",
                                        "series": 3,
                                        "reps": "12-15",
                                        "rpe": "7",
                                        "notes": "Control en todo el rango",
                                        "video_url": "https://drive.google.com/example13"
                                    }
                                ]
                            }
                        ],
                        "session_notes": [
                            "Calentar con puente de glúteos y activación de isquios",
                            "Cuidar la zona lumbar en peso muerto",
                            "Finalizar con estiramientos de cadena posterior"
                        ]
                    }
                ],
                "general_notes": [
                    "Evitar ejercicios overhead por molestia en hombro izquierdo",
                    "Priorizar técnica sobre peso en todas las series",
                    "Progresar solo cuando la técnica sea correcta y sin dolor",
                    "Descanso entre series: 2-3 minutos para ejercicios principales, 1-2 min para accesorios"
                ]
            }
        }
        
        # Guardar en training_plans_v2
        try:
            edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
            
            training_plan_doc = {
                "user_id": user_id,
                "questionnaire_submission_id": "mock_submission_001",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "plan": mock_plan["client_training_program_enriched"],
                "status": "draft",
                "version": "1.0.0",
                "source": "mock_endpoint_v1"
            }
            
            result = await edn360_db.training_plans_v2.insert_one(training_plan_doc)
            
            logger.info(
                f"✅ Plan MOCK guardado | "
                f"plan_id: {str(result.inserted_id)} | user_id: {user_id}"
            )
        
        except Exception as e:
            logger.warning(f"⚠️ Error guardando plan MOCK: {e}")
        
        logger.info(f"✅ Plan MOCK generado | user_id: {user_id}")
        
        return mock_plan
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error en /training-plan/mock: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error generando plan mock: {str(e)}"
            }
        )


@api_router.get("/admin/users/{user_id}/training-plans/latest")
async def get_latest_training_plan(user_id: str, request: Request):
    """
    Obtiene el último plan de entrenamiento generado para un usuario.
    
    Este endpoint:
    - Busca el plan más reciente en training_plans_v2
    - Devuelve el plan completo con metadatos
    - Incluye información de cuándo fue creado y su estado
    
    Response:
    {
        "plan_id": "...",
        "user_id": "...",
        "created_at": "...",
        "status": "draft|sent",
        "plan": { client_training_program_enriched },
        "source": "..."
    }
    
    Auth: Admin only
    """
    admin = await require_admin(request)
    
    try:
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        
        # Buscar el plan más reciente
        plan_doc = await edn360_db.training_plans_v2.find_one(
            {"user_id": user_id},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
        
        if not plan_doc:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "no_plan_found",
                    "message": f"No se encontró ningún plan para el usuario {user_id}"
                }
            )
        
        logger.info(
            f"✅ Plan recuperado | user_id: {user_id} | "
            f"created_at: {plan_doc.get('created_at', 'N/A')}"
        )
        
        return {
            "user_id": plan_doc.get("user_id"),
            "questionnaire_submission_id": plan_doc.get("questionnaire_submission_id"),
            "created_at": plan_doc.get("created_at"),
            "status": plan_doc.get("status", "draft"),
            "plan": plan_doc.get("plan"),
            "plain_text_content": plan_doc.get("plain_text_content"),  # NEW: Return plain text
            "source": plan_doc.get("source"),
            "version": plan_doc.get("version")
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo plan: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error obteniendo plan: {str(e)}"
            }
        )



@api_router.put("/admin/users/{user_id}/training-plans/edit")
async def update_training_plan(user_id: str, request: Request):
    """
    Actualiza el plan de entrenamiento editado por el admin.
    
    Este endpoint:
    - Busca el plan más reciente del usuario
    - Actualiza el campo 'plan' con los cambios del admin
    - Guarda una marca de tiempo de la última edición
    - Mantiene la versión original en un campo separado
    
    Request Body:
    {
        "plan": { client_training_program_enriched con cambios }
    }
    
    Response:
    {
        "success": true,
        "message": "Plan actualizado correctamente"
    }
    
    Auth: Admin only
    """
    admin = await require_admin(request)
    
    try:
        body = await request.json()
        updated_plan = body.get("plan")
        plain_text_override = body.get("plain_text_override")  # NEW: Plain text content
        
        if not updated_plan:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "missing_plan",
                    "message": "Se requiere el campo 'plan' con el plan actualizado"
                }
            )
        
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        
        # Buscar el plan más reciente
        existing_plan = await edn360_db.training_plans_v2.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        if not existing_plan:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "no_plan_found",
                    "message": f"No se encontró ningún plan para el usuario {user_id}"
                }
            )
        
        # Guardar la versión original si no existe
        update_doc = {
            "plan": updated_plan,
            "last_edited_at": datetime.now(timezone.utc).isoformat(),
            "last_edited_by": admin["_id"]
        }
        
        # NEW: Save plain text override if provided
        if plain_text_override:
            update_doc["plain_text_content"] = plain_text_override
            logger.info(f"📝 Guardando plain_text_content ({len(plain_text_override)} caracteres)")
        
        # Si es la primera edición, guardar el plan original
        if "original_plan" not in existing_plan:
            update_doc["original_plan"] = existing_plan.get("plan")
        
        # Actualizar el documento
        result = await edn360_db.training_plans_v2.update_one(
            {"_id": existing_plan["_id"]},
            {"$set": update_doc}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "update_failed",
                    "message": "No se pudo actualizar el plan"
                }
            )
        
        logger.info(
            f"✅ Plan actualizado | user_id: {user_id} | "
            f"admin: {admin['_id']} | plan_id: {str(existing_plan['_id'])}"
        )
        
        return {
            "success": True,
            "message": "Plan actualizado correctamente",
            "plan_id": str(existing_plan["_id"])
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error actualizando plan: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error actualizando plan: {str(e)}"
            }
        )


@api_router.delete("/admin/users/{user_id}/training-plans/latest")
async def delete_latest_training_plan(user_id: str, request: Request):
    """
    Elimina el último plan de entrenamiento de un usuario.
    
    Este endpoint:
    - Busca el plan más reciente del usuario
    - Lo elimina de la base de datos
    - Devuelve confirmación
    
    Auth: Admin only
    """
    admin = await require_admin(request)
    
    try:
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        
        # Buscar el plan más reciente
        plan_doc = await edn360_db.training_plans_v2.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        if not plan_doc:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "no_plan_found",
                    "message": f"No se encontró ningún plan para el usuario {user_id}"
                }
            )
        
        # Eliminar el plan
        result = await edn360_db.training_plans_v2.delete_one(
            {"_id": plan_doc["_id"]}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "delete_failed",
                    "message": "No se pudo eliminar el plan"
                }
            )
        
        logger.info(
            f"✅ Plan eliminado | user_id: {user_id} | "
            f"admin: {admin['_id']} | plan_id: {str(plan_doc['_id'])}"
        )
        
        return {
            "success": True,
            "message": "Plan eliminado correctamente"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error eliminando plan: {e}")
        import traceback
        traceback.print_exc()


@api_router.patch("/admin/training-plans/{plan_id}/toggle-status")
async def toggle_training_plan_status(plan_id: str, request: Request):
    """
    Activa o desactiva un plan de entrenamiento (cambia status entre 'sent' y 'draft').
    
    Auth: Admin only
    """
    admin = await require_admin(request)
    
    try:
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        
        # Buscar el plan por questionnaire_submission_id o _id
        plan_doc = await edn360_db.training_plans_v2.find_one({"questionnaire_submission_id": plan_id})
        
        if not plan_doc:
            # Intentar buscar por _id si no se encuentra por questionnaire_submission_id
            from bson import ObjectId
            try:
                plan_doc = await edn360_db.training_plans_v2.find_one({"_id": ObjectId(plan_id)})
            except:
                pass
        
        if not plan_doc:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        # Alternar status
        current_status = plan_doc.get("status", "draft")
        new_status = "draft" if current_status == "sent" else "sent"
        
        # Actualizar usando el _id del documento encontrado
        result = await edn360_db.training_plans_v2.update_one(
            {"_id": plan_doc["_id"]},
            {"$set": {"status": new_status}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=500, detail="No se pudo actualizar el plan")
        
        logger.info(f"✅ Plan status cambiado | plan_id: {plan_id} | {current_status} → {new_status}")
        
        return {
            "success": True,
            "message": f"Plan {'activado' if new_status == 'sent' else 'desactivado'} correctamente",
            "new_status": new_status
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error cambiando status del plan: {e}")
        raise HTTPException(status_code=500, detail="Error interno del servidor")


@api_router.delete("/admin/training-plans/{plan_id}")
async def delete_training_plan_by_id(plan_id: str, request: Request):
    """
    Elimina un plan de entrenamiento específico por su ID.
    
    Auth: Admin only
    """
    admin = await require_admin(request)
    
    try:
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        
        # Buscar el plan por questionnaire_submission_id o _id
        plan_doc = await edn360_db.training_plans_v2.find_one({"questionnaire_submission_id": plan_id})
        
        if not plan_doc:
            # Intentar buscar por _id si no se encuentra por questionnaire_submission_id
            from bson import ObjectId
            try:
                plan_doc = await edn360_db.training_plans_v2.find_one({"_id": ObjectId(plan_id)})
            except:
                pass
        
        if not plan_doc:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "no_plan_found",
                    "message": f"No se encontró el plan con ID {plan_id}"
                }
            )
        
        # Eliminar el plan usando el _id del documento encontrado
        result = await edn360_db.training_plans_v2.delete_one({"_id": plan_doc["_id"]})
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=500,
                detail={
                    "error": "delete_failed",
                    "message": "No se pudo eliminar el plan"
                }
            )
        
        logger.info(
            f"✅ Plan eliminado | plan_id: {plan_id} | admin: {admin['_id']}"
        )
        
        return {
            "success": True,
            "message": "Plan eliminado exitosamente"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error eliminando plan: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error eliminando plan: {str(e)}"
            }
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error eliminando plan: {str(e)}"
            }
        )


@api_router.post("/admin/users/{user_id}/training-plans/send-to-user-panel")
async def send_training_plan_to_user_panel(user_id: str, request: Request):
    """
    Envía el plan de entrenamiento al panel del usuario y notifica por email.
    
    Este endpoint:
    - Actualiza el status del plan a 'sent'
    - Envía notificación por email al usuario con enlace a su panel
    - El plan aparecerá en el UserDashboard del cliente
    
    Auth: Admin only
    """
    admin = await require_admin(request)
    
    try:
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        
        # Buscar el plan más reciente
        plan_doc = await edn360_db.training_plans_v2.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        if not plan_doc:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "no_plan_found",
                    "message": f"No se encontró ningún plan para el usuario {user_id}"
                }
            )
        
        # Actualizar status a 'sent'
        await edn360_db.training_plans_v2.update_one(
            {"_id": plan_doc["_id"]},
            {"$set": {"status": "sent", "sent_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Obtener info del usuario para el email
        user = await db.users.find_one({"_id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Enviar email de notificación
        from email_utils import send_email
        
        frontend_url = os.environ.get('FRONTEND_URL', 'http://localhost:3000')
        dashboard_url = f"{frontend_url}/user-dashboard"
        
        notification_subject = "¡Tu Plan de Entrenamiento está Listo! 💪"
        notification_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="text-align: center; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 30px; border-radius: 10px; margin-bottom: 30px;">
                <h1 style="color: white; margin: 0; font-size: 28px;">EDN360</h1>
                <p style="color: #e0e7ff; margin: 10px 0 0 0; font-size: 16px;">¡Tu Plan de Entrenamiento está Listo!</p>
            </div>
            
            <h2 style="color: #1e40af;">¡Hola {user.get('name', 'Cliente')}!</h2>
            <p style="font-size: 16px;">Tu entrenador ha preparado un nuevo plan de entrenamiento personalizado para ti.</p>
            
            <div style="background-color: #eff6ff; padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6; margin: 30px 0;">
                <p style="margin: 0; font-size: 16px; font-weight: bold; color: #1e40af;">Tu plan ya está disponible en tu panel</p>
            </div>
            
            <div style="text-align: center; margin: 40px 0;">
                <a href="{dashboard_url}" 
                   style="display: inline-block; background-color: #3b82f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
                    Ver Mi Plan de Entrenamiento
                </a>
            </div>
            
            <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 14px;">
                <p>EDN360 - Entrenamiento Personalizado</p>
                <p>Jorge Calcerrada - Entrenador Personal</p>
            </div>
        </body>
        </html>
        """
        
        send_email(
            to_email=user.get('email'),
            subject=notification_subject,
            html_body=notification_html
        )
        
        logger.info(
            f"✅ Plan enviado al panel del usuario | user_id: {user_id} | "
            f"admin: {admin['_id']} | user_email: {user.get('email')}"
        )
        
        return {
            "success": True,
            "message": "Plan enviado al panel del usuario y notificación enviada por email"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error enviando plan al panel del usuario: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error enviando plan: {str(e)}"
            }
        )


@api_router.post("/admin/users/{user_id}/training-plans/send-email")
async def send_training_plan_email(user_id: str, request: Request):
    """
    Envía el plan de entrenamiento por email al usuario.
    
    Email incluye:
    - Toda la información del plan (objetivo, resumen, notas generales)
    - Sesiones completas con ejercicios
    - Enlaces a videos
    - Branding EDN360
    
    Auth: Admin only
    """
    admin = await require_admin(request)
    
    try:
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        
        # Buscar el plan más reciente
        plan_doc = await edn360_db.training_plans_v2.find_one(
            {"user_id": user_id},
            sort=[("created_at", -1)]
        )
        
        if not plan_doc:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "no_plan_found",
                    "message": f"No se encontró ningún plan para el usuario {user_id}"
                }
            )
        
        # Obtener info del usuario
        user = await db.users.find_one({"_id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Generar HTML del email
        email_html = _generate_training_plan_email_html(plan_doc, user)
        
        # Enviar email
        from email_utils import send_email
        
        email_subject = f"Tu Plan de Entrenamiento - {plan_doc['plan'].get('title', 'EDN360')}"
        
        send_email(
            to_email=user.get('email'),
            subject=email_subject,
            html_body=email_html
        )
        
        logger.info(
            f"✅ Plan enviado por email | user_id: {user_id} | "
            f"admin: {admin['_id']} | user_email: {user.get('email')}"
        )
        
        return {
            "success": True,
            "message": f"Plan enviado por email a {user.get('email')}"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error enviando email: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error enviando email: {str(e)}"
            }
        )


def _generate_training_plan_email_html(plan_doc: dict, user: dict) -> str:
    """
    Genera el HTML del email con el plan de entrenamiento.
    Incluye branding EDN360, toda la info del plan, y enlaces a videos.
    """
    plan = plan_doc.get("plan", {})
    
    # Construir HTML de sesiones
    sessions_html = ""
    for session in plan.get("sessions", []):
        sessions_html += f"""
        <div style="margin-bottom: 30px; background-color: #f8f9fa; padding: 20px; border-radius: 8px;">
            <h3 style="color: #1e40af; margin-bottom: 10px;">{session.get('name', 'Sesión')}</h3>
            <p style="color: #64748b; font-size: 14px; margin-bottom: 15px;">
                <strong>Foco:</strong> {', '.join(session.get('focus', []))}
            </p>
        """
        
        # Notas de la sesión
        if session.get('session_notes'):
            sessions_html += '<p style="color: #ef4444; font-size: 13px; margin-bottom: 10px;"><strong>⚠️ Notas:</strong></p><ul style="margin-left: 20px;">'
            for note in session['session_notes']:
                sessions_html += f'<li style="color: #ef4444; font-size: 13px;">{note}</li>'
            sessions_html += '</ul>'
        
        # Bloques y ejercicios - Support both new (bloques_estructurados) and old (blocks) structure
        if 'bloques_estructurados' in session:
            # New 4-block structure
            bloques_estructurados = session['bloques_estructurados']
            for block_key in ['A', 'B', 'C', 'D']:
                if block_key not in bloques_estructurados:
                    continue
                    
                block = bloques_estructurados[block_key]
                block_name = block.get('nombre', f'Bloque {block_key}')
                exercises = block.get('ejercicios', block.get('exercises', []))
                
                # Skip cardio block (D) - just show the options
                if block_key == 'D' and 'opciones' in block:
                    sessions_html += f"""
                    <div style="margin-bottom: 15px;">
                        <h4 style="color: #475569; font-size: 15px; margin-bottom: 10px;">
                            {block_name}
                        </h4>
                        <p style="color: #64748b; font-size: 14px; margin: 10px 0;">
                            <strong>Duración:</strong> {block.get('duracion_minutos', 10)} minutos
                        </p>
                        <p style="color: #64748b; font-size: 14px; margin: 10px 0;">
                            <strong>Opciones disponibles:</strong>
                        </p>
                        <ul style="margin-left: 20px; color: #64748b; font-size: 14px;">
                    """
                    for opcion in block.get('opciones', []):
                        # Handle both string and object formats
                        opcion_text = opcion if isinstance(opcion, str) else opcion.get('nombre', opcion.get('opcion', str(opcion)))
                        sessions_html += f'<li>{opcion_text}</li>'
                    sessions_html += """
                        </ul>
                    </div>
                    """
                    continue
                
                # For warmup and core blocks
                if len(exercises) > 0:
                    sessions_html += f"""
                    <div style="margin-bottom: 15px;">
                        <h4 style="color: #475569; font-size: 15px; margin-bottom: 10px;">
                            {block_name}
                        </h4>
                        <table style="width: 100%; border-collapse: collapse; background-color: white; border-radius: 4px; overflow: hidden;">
                            <thead style="background-color: #e2e8f0;">
                                <tr>
                                    <th style="padding: 8px; text-align: left; font-size: 13px; color: #475569;">#</th>
                                    <th style="padding: 8px; text-align: left; font-size: 13px; color: #475569;">Ejercicio</th>
                                    <th style="padding: 8px; text-align: center; font-size: 13px; color: #475569;">Series</th>
                                    <th style="padding: 8px; text-align: center; font-size: 13px; color: #475569;">Reps</th>
                                    <th style="padding: 8px; text-align: center; font-size: 13px; color: #475569;">RPE</th>
                                    <th style="padding: 8px; text-align: center; font-size: 13px; color: #475569;">Video</th>
                                </tr>
                            </thead>
                            <tbody>
                    """
                    
                    for exercise in exercises:
                        video_button = ''
                        if exercise.get('video_url'):
                            video_button = f'<a href="{exercise["video_url"]}" target="_blank" style="background-color: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 12px;">Ver</a>'
                        
                        sessions_html += f"""
                                <tr style="border-bottom: 1px solid #e2e8f0;">
                                    <td style="padding: 8px; font-size: 13px;">{exercise.get('order', '')}</td>
                                    <td style="padding: 8px; font-size: 13px;">
                                        <strong>{exercise.get('name', exercise.get('nombre', ''))}</strong><br>
                                        <span style="color: #64748b; font-size: 12px;">{exercise.get('notes', exercise.get('notas', ''))}</span>
                                    </td>
                                    <td style="padding: 8px; text-align: center; font-size: 13px;">{exercise.get('series', '')}</td>
                                    <td style="padding: 8px; text-align: center; font-size: 13px;">{exercise.get('reps', exercise.get('repeticiones', ''))}</td>
                                    <td style="padding: 8px; text-align: center; font-size: 13px;">{exercise.get('rpe', '')}</td>
                                    <td style="padding: 8px; text-align: center;">{video_button}</td>
                                </tr>
                        """
                    
                    sessions_html += """
                            </tbody>
                        </table>
                    </div>
                    """
        else:
            # Old structure for backward compatibility
            for block in session.get('blocks', []):
                sessions_html += f"""
                <div style="margin-bottom: 15px;">
                    <h4 style="color: #475569; font-size: 15px; margin-bottom: 10px;">
                        Bloque {block.get('id')} - {', '.join(block.get('primary_muscles', []))}
                    </h4>
                    <table style="width: 100%; border-collapse: collapse; background-color: white; border-radius: 4px; overflow: hidden;">
                        <thead style="background-color: #e2e8f0;">
                            <tr>
                                <th style="padding: 8px; text-align: left; font-size: 13px; color: #475569;">#</th>
                                <th style="padding: 8px; text-align: left; font-size: 13px; color: #475569;">Ejercicio</th>
                                <th style="padding: 8px; text-align: center; font-size: 13px; color: #475569;">Series</th>
                                <th style="padding: 8px; text-align: center; font-size: 13px; color: #475569;">Reps</th>
                                <th style="padding: 8px; text-align: center; font-size: 13px; color: #475569;">RPE</th>
                                <th style="padding: 8px; text-align: center; font-size: 13px; color: #475569;">Video</th>
                            </tr>
                        </thead>
                        <tbody>
                """
                
                for exercise in block.get('exercises', []):
                    video_button = ''
                    if exercise.get('video_url'):
                        video_button = f'<a href="{exercise["video_url"]}" target="_blank" style="background-color: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 12px;">Ver</a>'
                    
                    sessions_html += f"""
                            <tr style="border-bottom: 1px solid #e2e8f0;">
                                <td style="padding: 8px; font-size: 13px;">{exercise.get('order')}</td>
                                <td style="padding: 8px; font-size: 13px;">
                                    <strong>{exercise.get('name')}</strong><br>
                                    <span style="color: #64748b; font-size: 12px;">{exercise.get('notes', '')}</span>
                                </td>
                                <td style="padding: 8px; text-align: center; font-size: 13px;">{exercise.get('series')}</td>
                                <td style="padding: 8px; text-align: center; font-size: 13px;">{exercise.get('reps')}</td>
                                <td style="padding: 8px; text-align: center; font-size: 13px;">{exercise.get('rpe')}</td>
                                <td style="padding: 8px; text-align: center;">{video_button}</td>
                            </tr>
                    """
                
                sessions_html += """
                        </tbody>
                    </table>
                </div>
                """
        
        sessions_html += "</div>"
    
    # HTML completo del email
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
        <!-- Header con branding EDN360 -->
        <div style="text-align: center; background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%); padding: 30px; border-radius: 10px; margin-bottom: 30px;">
            <h1 style="color: white; margin: 0; font-size: 28px;">EDN360</h1>
            <p style="color: #e0e7ff; margin: 10px 0 0 0; font-size: 16px;">Tu Plan de Entrenamiento Personalizado</p>
        </div>
        
        <!-- Saludo -->
        <h2 style="color: #1e40af;">Hola {user.get('name', 'Cliente')}!</h2>
        <p style="font-size: 16px;">Tu entrenador ha preparado un nuevo plan de entrenamiento personalizado para ti.</p>
        
        <!-- Info del plan -->
        <div style="background-color: #eff6ff; padding: 20px; border-radius: 8px; border-left: 4px solid #3b82f6; margin-bottom: 30px;">
            <h3 style="color: #1e40af; margin-top: 0;">{plan.get('title', 'Plan de Entrenamiento')}</h3>
            <p style="margin: 10px 0;"><strong>Objetivo:</strong> {plan.get('goal', '')}</p>
            <p style="margin: 10px 0;"><strong>Resumen:</strong> {plan.get('summary', '')}</p>
            <p style="margin: 10px 0;"><strong>Duracion:</strong> {plan.get('weeks', 4)} semanas | {plan.get('days_per_week', 4)} dias/semana | {plan.get('session_duration_min', 45)} min/sesion</p>
        </div>
        
        <!-- Notas Generales -->
        {f'''
        <div style="background-color: #fef2f2; padding: 15px; border-radius: 8px; border-left: 4px solid #ef4444; margin-bottom: 30px;">
            <h3 style="color: #dc2626; margin-top: 0;">Notas Generales Importantes</h3>
            <ul style="margin: 10px 0; padding-left: 20px;">
                {''.join([f'<li style="color: #dc2626;">{note}</li>' for note in plan.get('general_notes', [])])}
            </ul>
        </div>
        ''' if plan.get('general_notes') else ''}
        
        <!-- Sesiones -->
        <h2 style="color: #1e40af; margin-top: 40px;">Tu Programa de Entrenamiento</h2>
        {sessions_html}
        
        <!-- Call to action -->
        <div style="text-align: center; margin-top: 40px; padding: 30px; background-color: #f8f9fa; border-radius: 10px;">
            <p style="font-size: 16px; margin-bottom: 20px;">Accede a tu panel para ver tu plan completo y descargar el PDF</p>
            <a href="{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/user-dashboard" 
               style="display: inline-block; background-color: #3b82f6; color: white; padding: 15px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
                Ir a Mi Panel
            </a>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; color: #64748b; font-size: 14px;">
            <p>EDN360 - Entrenamiento Personalizado</p>
            <p>Este email ha sido enviado por tu entrenador personal</p>
        </div>
    </body>
    </html>
    """
    
    return html


@api_router.post("/users/{user_id}/training-plans/send-to-me")
async def send_training_plan_to_myself(user_id: str, request: Request):
    """
    El usuario se envia su propio plan de entrenamiento por email.
    """
    # Verificar que el usuario solo pueda enviar su propio plan
    user_data = await get_current_user(request)
    if user_data['id'] != user_id:
        raise HTTPException(status_code=403, detail="No puedes acceder a planes de otros usuarios")
    
    try:
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        
        # Buscar el plan más reciente con status='sent'
        plan_doc = await edn360_db.training_plans_v2.find_one(
            {"user_id": user_id, "status": "sent"},
            sort=[("created_at", -1)]
        )
        
        if not plan_doc:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "no_plan_found",
                    "message": "No tienes ningún plan de entrenamiento disponible"
                }
            )
        
        # Obtener info del usuario
        user = await db.users.find_one({"_id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Generar HTML del email
        email_html = _generate_training_plan_email_html(plan_doc, user)
        
        # Enviar email
        from email_utils import send_email
        
        email_subject = f"Tu Plan de Entrenamiento - {plan_doc['plan'].get('title', 'EDN360')}"
        
        send_email(
            to_email=user.get('email'),
            subject=email_subject,
            html_body=email_html
        )
        
        logger.info(f"✅ Usuario se envió el plan por email | user_id: {user_id}")
        
        return {
            "success": True,
            "message": f"Plan enviado a tu email: {user.get('email')}"
        }
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error enviando email al usuario: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error enviando email: {str(e)}"
            }
        )


@api_router.get("/users/{user_id}/training-plans/download-pdf")
async def download_training_plan_pdf(user_id: str, request: Request):
    """
    Descarga el plan de entrenamiento como PDF con videos clicables.
    """
    # Verificar que el usuario solo pueda descargar su propio plan
    user_data = await get_current_user(request)
    if user_data['id'] != user_id:
        raise HTTPException(status_code=403, detail="No puedes acceder a planes de otros usuarios")
    
    try:
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        
        # Buscar el plan más reciente con status='sent'
        plan_doc = await edn360_db.training_plans_v2.find_one(
            {"user_id": user_id, "status": "sent"},
            sort=[("created_at", -1)]
        )
        
        if not plan_doc:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "no_plan_found",
                    "message": "No tienes ningún plan de entrenamiento disponible"
                }
            )
        
        # Obtener info del usuario
        user = await db.users.find_one({"_id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Generar HTML del plan (igual que el email)
        html_content = _generate_training_plan_email_html(plan_doc, user)
        
        # Convertir HTML a PDF usando pdfkit
        import pdfkit
        
        pdf = pdfkit.from_string(html_content, False)
        
        logger.info(f"✅ Usuario descargó PDF del plan | user_id: {user_id}")
        
        from fastapi.responses import Response
        return Response(
            content=pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=Plan_Entrenamiento_{user.get('name', 'Cliente')}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf"
            }
        )
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error generando PDF: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error generando PDF: {str(e)}"
            }
        )


@api_router.get("/users/{user_id}/training-plans/latest")
async def get_user_latest_training_plan(user_id: str, request: Request):
    """
    Obtiene el plan de entrenamiento más reciente del usuario (solo si status='sent').
    """
    # Verificar que el usuario solo pueda ver su propio plan
    user_data = await get_current_user(request)
    if user_data['id'] != user_id:
        raise HTTPException(status_code=403, detail="No puedes acceder a planes de otros usuarios")
    
    try:
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        
        # Buscar el plan más reciente con status='sent'
        plan_doc = await edn360_db.training_plans_v2.find_one(
            {"user_id": user_id, "status": "sent"},
            {"_id": 0},
            sort=[("created_at", -1)]
        )
        
        if not plan_doc:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "no_plan_found",
                    "message": "No tienes ningún plan de entrenamiento disponible"
                }
            )
        
        return plan_doc
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo plan del usuario: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "internal_error",
                "message": f"Error obteniendo plan: {str(e)}"
            }
        )


@api_router.post("/admin/archive-client/{user_id}")
async def archive_client(user_id: str, request: Request, reason: Optional[str] = None):
    admin = await require_admin(request)
    result = await db.users.update_one(
        {"_id": user_id},
        {"$set": {
            "subscription.archived": True,
            "subscription.archived_reason": reason,
            "subscription.archived_date": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "message": "Client archived successfully"}


@api_router.post("/admin/unarchive-client/{user_id}")
async def unarchive_client(user_id: str, request: Request):
    admin = await require_admin(request)
    result = await db.users.update_one(
        {"_id": user_id},
        {"$set": {
            "subscription.archived": False,
            "subscription.archived_reason": None,
            "subscription.archived_date": None,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "message": "Client unarchived successfully"}


@api_router.delete("/admin/delete-client/{user_id}")
async def delete_client(user_id: str, request: Request):
    admin = await require_admin(request)
    
    # Get user info before deleting
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"🗑️ HARD DELETE iniciado para usuario: {user.get('email')} por admin: {admin['email']}")
    
    # HARD DELETE COMPLETO - Borrar de TODAS las colecciones
    
    # 1. Borrar TODOS los planes de nutrición
    nutrition_plans_deleted = await db.nutrition_plans.delete_many({"user_id": user_id})
    logger.info(f"  ✅ {nutrition_plans_deleted.deleted_count} planes de nutrición eliminados")
    
    # 2. Borrar TODAS las respuestas del cuestionario
    questionnaire_submissions_deleted = await db.nutrition_questionnaire_submissions.delete_many({"user_id": user_id})
    logger.info(f"  ✅ {questionnaire_submissions_deleted.deleted_count} respuestas de cuestionario eliminadas")
    
    # 3. Borrar formularios
    forms_deleted = await db.forms.delete_many({"user_id": user_id})
    logger.info(f"  ✅ {forms_deleted.deleted_count} formularios eliminados")
    
    # 4. Borrar alertas
    alerts_deleted = await db.alerts.delete_many({"user_id": user_id})
    logger.info(f"  ✅ {alerts_deleted.deleted_count} alertas eliminadas")
    
    # 5. Borrar mensajes
    messages_deleted = await db.messages.delete_many({"user_id": user_id})
    logger.info(f"  ✅ {messages_deleted.deleted_count} mensajes eliminados")
    
    # 6. Borrar sesiones
    sessions_deleted = await db.sessions.delete_many({"user_id": user_id})
    logger.info(f"  ✅ {sessions_deleted.deleted_count} sesiones eliminadas")
    
    # 7. Borrar PDFs del filesystem y database
    # Exclude file_data from PDFs to avoid serialization issues
    pdfs = await db.pdfs.find(
        {"user_id": user_id},
        {"file_data": 0}
    ).to_list(100)
    for pdf in pdfs:
        file_path = Path(pdf["file_path"])
        if file_path.exists():
            file_path.unlink()
    pdfs_deleted = await db.pdfs.delete_many({"user_id": user_id})
    logger.info(f"  ✅ {pdfs_deleted.deleted_count} PDFs eliminados")
    
    # 8. Borrar prospectos si existen
    prospects_deleted = await db.prospects.delete_many({"user_id": user_id})
    logger.info(f"  ✅ {prospects_deleted.deleted_count} prospectos eliminados")
    
    # 9. FINALMENTE borrar el usuario
    user_deleted = await db.users.delete_one({"_id": user_id})
    logger.info(f"  ✅ Usuario eliminado de la base de datos")
    
    if user_deleted.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"✅ HARD DELETE COMPLETO para {user['email']} - TODOS los datos eliminados permanentemente")
    
    return {
        "success": True, 
        "message": "Cliente y TODOS sus datos eliminados permanentemente. Si se vuelve a registrar, comenzará desde cero.",
        "deleted_data": {
            "nutrition_plans": nutrition_plans_deleted.deleted_count,
            "questionnaire_submissions": questionnaire_submissions_deleted.deleted_count,
            "forms": forms_deleted.deleted_count,
            "alerts": alerts_deleted.deleted_count,
            "messages": messages_deleted.deleted_count,
            "sessions": sessions_deleted.deleted_count,
            "pdfs": pdfs_deleted.deleted_count,
            "prospects": prospects_deleted.deleted_count
        }
    }


# ==================== FORM ENDPOINTS ====================



@api_router.patch("/admin/users/{user_id}")
async def admin_update_user(user_id: str, user_update: AdminUserUpdate, request: Request):
    """Admin updates a client's profile - works for both users and converted prospects"""
    admin = await require_admin(request)
    
    update_data = {}
    
    if user_update.name:
        update_data["name"] = user_update.name
    
    if user_update.email:
        # Check if email is already taken by another user
        existing_user = await db.users.find_one({"email": user_update.email, "_id": {"$ne": user_id}})
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        update_data["email"] = user_update.email
    
    if user_update.subscription_status:
        update_data["subscription.status"] = user_update.subscription_status
    
    if user_update.subscription_plan:
        update_data["subscription.plan"] = user_update.subscription_plan
    
    if user_update.payment_status:
        update_data["subscription.payment_status"] = user_update.payment_status
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    # Try updating in users collection first
    result = await db.users.update_one(
        {"_id": user_id},
        {"$set": update_data}
    )
    
    if result.matched_count > 0:
        # Get updated user
        updated_user = await db.users.find_one({"_id": user_id})
        
        return {
            "success": True,
            "message": "User updated successfully",
            "user": {
                "id": updated_user["_id"],
                "name": updated_user["name"],
                "email": updated_user["email"],
                "subscription": updated_user.get("subscription", {})
            }
        }
    
    # If not found in users, try questionnaire_responses (converted prospects)
    prospect_update = {}
    if user_update.name:
        prospect_update["nombre"] = user_update.name
    if user_update.email:
        prospect_update["email"] = user_update.email
    prospect_update["updated_at"] = datetime.now(timezone.utc)
    
    result = await db.questionnaire_responses.update_one(
        {"_id": user_id},
        {"$set": prospect_update}
    )



@api_router.patch("/admin/archive-client/{user_id}")
async def archive_client(user_id: str, request: Request):
    """Archivar cliente - No puede acceder pero mantiene todos sus datos"""
    admin = await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Marcar como archivado
    result = await db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "status": "archived",
                "archived_at": datetime.now(timezone.utc),
                "archived_by": admin["_id"],
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"Cliente archivado: {user.get('email')} por admin: {admin['email']}")
    
    return {
        "success": True,
        "message": "Cliente archivado. No podrá acceder hasta que sea reactivado Y realice el pago."
    }


@api_router.patch("/admin/unarchive-client/{user_id}")
async def unarchive_client(user_id: str, request: Request):
    """Reactivar cliente archivado - Requiere verificación de pago"""
    admin = await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get("status") != "archived":
        raise HTTPException(status_code=400, detail="El usuario no está archivado")
    
    # Reactivar pero mantener pago pendiente
    result = await db.users.update_one(
        {"_id": user_id},
        {
            "$set": {
                "status": "active",
                "subscription.payment_status": "pending",  # Forzar que pague de nuevo
                "unarchived_at": datetime.now(timezone.utc),
                "unarchived_by": admin["_id"],
                "updated_at": datetime.now(timezone.utc)
            },
            "$unset": {
                "archived_at": "",
                "archived_by": ""
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    logger.info(f"Cliente reactivado: {user.get('email')} por admin: {admin['email']}")
    
    return {
        "success": True,
        "message": "Cliente reactivado. Podrá acceder cuando realice el pago."
    }


    
    if result.matched_count > 0:
        prospect = await db.questionnaire_responses.find_one({"_id": user_id})
        return {
            "success": True,
            "message": "Prospect updated successfully",
            "user": {
                "id": prospect["_id"],
                "name": prospect.get("nombre"),
                "email": prospect.get("email")
            }
        }
    
    raise HTTPException(status_code=404, detail="User not found")


@api_router.post("/admin/users/{user_id}/send-password-reset")
async def admin_send_password_reset(user_id: str, request: Request):
    """Admin sends password reset email to a client"""
    admin = await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate reset token (valid for 1 hour)
    reset_token = str(datetime.now(timezone.utc).timestamp()).replace(".", "") + user["_id"]
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    
    # Store reset token
    await db.password_resets.update_one(
        {"user_id": user_id},
        {"$set": {
            "token": reset_token,
            "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc)
        }},
        upsert=True
    )
    
    # Send email
    try:
        from email_utils import send_password_reset_email
        send_password_reset_email(
            user_email=user["email"],
            user_name=user.get("name", user.get("username", "")),
            reset_token=reset_token
        )
        return {"success": True, "message": "Password reset email sent"}
    except Exception as e:
        logger.error(f"Failed to send password reset email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send email")

@api_router.post("/forms/send")
async def send_form(form_data: FormCreate, request: Request):
    admin = await require_admin(request)
    form_dict = {
        "_id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
        "user_id": form_data.user_id,
        "title": form_data.title,
        "url": form_data.url,
        "completed": False,
        "sent_date": datetime.now(timezone.utc),
        "completed_date": None,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.forms.insert_one(form_dict)
    form_dict["id"] = form_dict["_id"]
    
    return form_dict


@api_router.patch("/forms/{form_id}/complete")
async def complete_form(form_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.forms.update_one(
        {"_id": form_id, "user_id": user["_id"]},
        {"$set": {
            "completed": True,
            "completed_date": datetime.now(timezone.utc)
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Form not found")
    
    return {"success": True}


# ==================== PDF ENDPOINTS ====================

@api_router.post("/pdfs/upload")
async def upload_pdf(
    request: Request,
    file: UploadFile = File(...),
    user_id: str = Form(...),
    title: str = Form(...),
    type: str = Form(...)
):
    admin = await require_admin(request)
    # Create uploads directory
    upload_dir = Path("/app/backend/uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}_{file.filename}"
    file_path = upload_dir / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save to database
    pdf_dict = {
        "_id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
        "user_id": user_id,
        "title": title,
        "type": type,
        "file_path": str(file_path),
        "uploaded_by": "admin",  # Mark as uploaded by admin
        "upload_date": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.pdfs.insert_one(pdf_dict)
    pdf_dict["id"] = pdf_dict["_id"]
    
    return pdf_dict




@api_router.post("/documents/upload")
async def user_upload_document(
    request: Request,
    file: UploadFile = File(...),
    title: str = Form(...),
    type: str = Form(...)
):
    """Users upload documents to admin"""
    user = await get_current_user(request)
    user_id = user["_id"]
    
    # Create uploads directory
    upload_dir = Path("/app/backend/uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}_{file.filename}"
    file_path = upload_dir / filename
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Save to database
    pdf_dict = {
        "_id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
        "user_id": user_id,
        "title": title,
        "type": type,
        "file_path": str(file_path),
        "uploaded_by": "user",  # Mark as uploaded by user
        "upload_date": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.pdfs.insert_one(pdf_dict)
    pdf_dict["id"] = pdf_dict["_id"]
    
    return {"success": True, "message": "Document uploaded successfully", "document": pdf_dict}




@api_router.delete("/pdfs/{pdf_id}")
async def delete_pdf(pdf_id: str, request: Request):
    """Delete a PDF - Users can delete their own uploads, Admin can delete any"""
    user = await get_current_user(request)
    
    # Get PDF details
    pdf = await db.pdfs.find_one({"_id": pdf_id})
    if not pdf:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions: users can delete their own uploaded docs, admin can delete any
    if user["role"] != "admin" and pdf.get("uploaded_by") != "user":
        raise HTTPException(status_code=403, detail="You can only delete documents you uploaded")
    
    if user["role"] != "admin" and pdf["user_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete file from filesystem if it exists (for backwards compatibility)
    if pdf.get("file_path"):
        file_path = Path(pdf["file_path"])
        if file_path.exists():
            file_path.unlink()
    
    # Delete from database (file_data is stored in MongoDB)
    await db.pdfs.delete_one({"_id": pdf_id})
    
    logger.info(f"✅ PDF deleted: {pdf_id} by {user['email']}")
    
    return {"success": True, "message": "Document deleted successfully"}


@api_router.get("/pdfs/{pdf_id}/download")
async def download_pdf(pdf_id: str, request: Request):
    from fastapi.responses import Response
    
    user = await get_current_user(request)
    pdf = await db.pdfs.find_one({"_id": pdf_id})
    
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Check if user owns this PDF or is admin
    if pdf["user_id"] != user["_id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # New structure: file_data stored in MongoDB
    if pdf.get("file_data"):
        filename = pdf.get("filename", f"{pdf.get('title', 'document')}.pdf")
        return Response(
            content=pdf["file_data"],
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'}
        )
    
    # Backwards compatibility: file_path in filesystem
    elif pdf.get("file_path"):
        file_path = Path(pdf["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(file_path, media_type="application/pdf", filename=file_path.name)
    
    else:
        raise HTTPException(status_code=404, detail="PDF content not found")


# ==================== ALERT ENDPOINTS ====================

@api_router.post("/alerts/send")
async def send_alert(alert_data: AlertCreate, request: Request):
    admin = await require_admin(request)
    alert_dict = {
        "_id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
        "user_id": alert_data.user_id,
        "title": alert_data.title,
        "message": alert_data.message,
        "type": alert_data.type,
        "link": alert_data.link,
        "read": False,
        "date": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.alerts.insert_one(alert_dict)
    alert_dict["id"] = alert_dict["_id"]
    
    return alert_dict


@api_router.patch("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str, request: Request):
    user = await get_current_user(request)
    result = await db.alerts.update_one(
        {"_id": alert_id, "user_id": user["_id"]},
        {"$set": {"read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"success": True}


@api_router.get("/alerts/unread")
async def get_unread_count(request: Request):
    user = await get_current_user(request)
    count = await db.alerts.count_documents({"user_id": user["_id"], "read": False})
    return {"count": count}


# ==================== MESSAGE/CHAT ENDPOINTS ====================

@api_router.get("/messages/{user_id}")
async def get_messages(user_id: str, request: Request):
    current_user = await get_current_user(request)
    # Admin can view any user's messages, users can only view their own
    if current_user["role"] != "admin" and current_user["_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    messages = await db.messages.find({"user_id": user_id}).sort("timestamp", 1).to_list(1000)
    
    for message in messages:
        message["id"] = str(message["_id"])
    
    return {"messages": messages}


@api_router.post("/messages/send")
async def send_message(message_data: MessageCreate, request: Request):
    current_user = await get_current_user(request)
    # Determine user_id based on role
    if current_user["role"] == "admin":
        user_id = message_data.user_id  # Admin specifies which client
    else:
        user_id = current_user["_id"]  # User sends to own conversation
    
    message_dict = {
        "_id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
        "user_id": user_id,
        "sender_id": current_user["_id"],
        "sender_name": current_user["name"],
        "message": message_data.message,
        "is_admin": current_user["role"] == "admin",
        "timestamp": datetime.now(timezone.utc),
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.messages.insert_one(message_dict)
    message_dict["id"] = message_dict["_id"]
    
    return message_dict


# ==================== SESSION/CALENDAR ENDPOINTS ====================

@api_router.post("/sessions/create")
async def create_session(session_data: SessionCreate, request: Request):
    admin = await require_admin(request)
    session_dict = {
        "_id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
        "user_id": session_data.user_id,
        "title": session_data.title,
        "description": session_data.description,
        "date": session_data.date,
        "duration": session_data.duration,
        "type": session_data.type,
        "created_by": admin["_id"],
        "completed": False,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.sessions.insert_one(session_dict)
    session_dict["id"] = session_dict["_id"]
    
    # Send email notification to user only (not admin)
    try:
        user = await db.users.find_one({"_id": session_data.user_id})
        if user and user.get("email"):
            # Email al cliente solamente
            send_session_created_email(
                user_email=user["email"],
                user_name=user.get("name", user.get("username", "")),
                session_date=session_data.date,
                session_title=session_data.title
            )
    except Exception as e:
        logger.error(f"Failed to send session created email: {e}")
    
    return session_dict


@api_router.get("/sessions/user/{user_id}")
async def get_user_sessions(user_id: str, request: Request):
    current_user = await get_current_user(request)
    # Users can only see their own sessions, admins can see any
    if current_user["role"] != "admin" and current_user["_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    sessions = await db.sessions.find({"user_id": user_id}).sort("date", 1).to_list(1000)
    
    for session in sessions:
        session["id"] = str(session["_id"])
    
    return {"sessions": sessions}


@api_router.get("/sessions/admin/all")
async def get_all_sessions(request: Request):
    admin = await require_admin(request)
    sessions = await db.sessions.find().sort("date", 1).to_list(1000)
    
    for session in sessions:
        session["id"] = str(session["_id"])
    
    return {"sessions": sessions}


@api_router.patch("/sessions/{session_id}/complete")
async def mark_session_complete(session_id: str, request: Request):
    admin = await require_admin(request)
    result = await db.sessions.update_one(
        {"_id": session_id},
        {"$set": {"completed": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True}



@api_router.patch("/sessions/{session_id}/reschedule")
async def reschedule_session(session_id: str, session_update: SessionUpdate, request: Request):
    """
    Allow users to reschedule their sessions or admins to reschedule any session
    """
    current_user = await get_current_user(request)
    
    # Get the session
    session = await db.sessions.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check permissions: users can only reschedule their own, admins can reschedule any
    if current_user["role"] != "admin" and session["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update the session date
    result = await db.sessions.update_one(
        {"_id": session_id},
        {"$set": {
            "date": session_update.date,
            "updated_at": datetime.now(timezone.utc)
        }}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Send email notification based on who is rescheduling
    try:
        user = await db.users.find_one({"_id": session["user_id"]})
        if user and user.get("email"):
            # If client is rescheduling, notify admin only
            if current_user["role"] != "admin":
                send_admin_session_rescheduled_email(
                    client_name=user.get("name", user.get("username", "")),
                    client_email=user["email"],
                    old_date=session["date"],
                    new_date=session_update.date,
                    session_title=session.get("title", "Sesión")
                )
            # If admin is rescheduling, notify client only
            else:
                send_session_rescheduled_email(
                    user_email=user["email"],
                    user_name=user.get("name", user.get("username", "")),
                    new_date=session_update.date,
                    session_title=session.get("title", "Tu sesión")
                )
    except Exception as e:
        logger.error(f"Failed to send session rescheduled email: {e}")
    
    return {"success": True, "message": "Session rescheduled successfully"}


@api_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, request: Request):
    """
    Delete a session. 
    - Admins can delete any session (no email sent)
    - Users can delete their own sessions (email sent to admin)
    """
    current_user = await get_current_user(request)
    
    # Get session details before deleting (for email notification)
    session = await db.sessions.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check permissions
    is_admin = current_user["role"] == "admin"
    is_owner = session["user_id"] == current_user["_id"]
    
    if not is_admin and not is_owner:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete the session
    result = await db.sessions.delete_one({"_id": session_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Send email notification only if CLIENT is deleting (not admin)
    if not is_admin:
        try:
            user = await db.users.find_one({"_id": session["user_id"]})
            if user and user.get("email"):
                send_admin_session_cancelled_email(
                    client_name=user.get("name", user.get("username", "")),
                    client_email=user["email"],
                    session_date=session["date"],
                    session_title=session.get("title", "Sesión")
                )
        except Exception as e:
            logger.error(f"Failed to send session cancelled email: {e}")
    
    return {"success": True}



# ==================== QUESTIONNAIRE ENDPOINT ====================

@api_router.post("/questionnaire/submit")
async def submit_questionnaire(questionnaire: QuestionnaireSubmit):
    """
    Submit diagnostic questionnaire and generate GPT report immediately.
    
    FASE 1 DUAL-WRITE: Este es el cuestionario de PROSPECCIÓN (antes de ser cliente).
    - Se guarda en BD Web (questionnaire_responses) como siempre
    - NO se escribe en client_drawers porque no hay user_id todavía
    - El cuestionario se añadirá a client_drawers cuando el prospecto se convierta en cliente
    """
    try:
        # Convert to dict for email function
        questionnaire_data = questionnaire.dict()
        
        # Save to database for CRM (BD WEB)
        prospect_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
        submitted_at = datetime.now(timezone.utc)
        
        prospect_doc = {
            "_id": prospect_id,
            **questionnaire_data,
            "submitted_at": submitted_at,
            "stage_name": "Nuevo",
            "stage_id": None,
            "converted_to_client": False,
            "report_generated": False,
            "report_sent_at": None,
            "report_content": None,
            "report_sent_via": None  # 'email' or 'whatsapp'
        }
        await db.questionnaire_responses.insert_one(prospect_doc)
        logger.info(f"✅ Questionnaire saved to CRM (BD Web) with ID: {prospect_id}")
        
        # ⚠️ NO DUAL-WRITE: Este cuestionario es de prospección, no tiene user_id
        # Se añadirá a client_drawers cuando se convierta en cliente
        
        # NOTE: Report generation is now manual from admin dashboard
        # Admin can generate/regenerate the report from ProspectsCRM
        
        # Send email to admin
        email_sent = send_questionnaire_to_admin(questionnaire_data)
        
        if email_sent:
            logger.info(f"Questionnaire submitted successfully from {questionnaire.email}")
            return {"success": True, "message": "Cuestionario enviado correctamente"}
        else:
            logger.warning(f"Questionnaire received but email not sent (SMTP not configured)")
            return {"success": True, "message": "Cuestionario recibido (email pendiente de configuración)"}
    
    except Exception as e:
        logger.error(f"Error submitting questionnaire: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al enviar el cuestionario"
        )



# ==================== CRM PROSPECTOS ENDPOINTS ====================

@api_router.get("/admin/prospects")
async def get_prospects(request: Request, stage: Optional[str] = None):
    """Get all prospects from questionnaire responses"""
    await require_admin(request)
    
    try:
        # Build query
        query = {"converted_to_client": False}
        if stage:
            query["stage_name"] = stage
        
        # Get all prospects
        prospects = await db.questionnaire_responses.find(query).sort("submitted_at", -1).to_list(length=1000)
        
        # Convert to response format
        prospects_list = []
        for p in prospects:
            p["id"] = p["_id"]
            prospects_list.append(p)
        
        return {"prospects": prospects_list, "total": len(prospects_list)}
    
    except Exception as e:
        logger.error(f"Error fetching prospects: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener prospectos")


@api_router.get("/admin/prospects/{prospect_id}")
async def get_prospect_detail(prospect_id: str, request: Request):
    """Get detailed information about a prospect"""
    await require_admin(request)
    
    try:
        prospect = await db.questionnaire_responses.find_one({"_id": prospect_id})
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospecto no encontrado")
        
        # Get notes for this prospect
        notes = await db.prospect_notes.find({"prospect_id": prospect_id}).sort("created_at", -1).to_list(length=100)
        for note in notes:
            note["id"] = note["_id"]
        
        prospect["id"] = prospect["_id"]
        prospect["notes"] = notes
        
        return prospect
    
    except Exception as e:
        logger.error(f"Error fetching prospect detail: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener detalle del prospecto")


@api_router.post("/admin/prospects/{prospect_id}/generate-report")
async def generate_prospect_report_manual(prospect_id: str, request: Request, regenerate: bool = False):
    """Generate or regenerate diagnostic report for a prospect"""
    await require_admin(request)
    
    try:
        # Get prospect
        prospect = await db.questionnaire_responses.find_one({"_id": prospect_id})
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospecto no encontrado")
        
        # Generate report
        from gpt_service import generate_prospect_report
        questionnaire_data = {k: v for k, v in prospect.items() if k not in ['_id', 'submitted_at', 'stage_name', 'stage_id', 'converted_to_client', 'report_generated', 'report_sent_at', 'report_content', 'report_sent_via', 'report_generated_at']}
        
        report = await generate_prospect_report(questionnaire_data)
        
        # Update prospect with generated report
        await db.questionnaire_responses.update_one(
            {"_id": prospect_id},
            {
                "$set": {
                    "report_generated": True,
                    "report_content": report,
                    "report_generated_at": datetime.now(timezone.utc),
                    "stage_id": "stage_001",
                    "stage_name": "INFORME GENERADO"
                }
            }
        )
        
        action = "regenerado" if regenerate else "generado"
        logger.info(f"Report {action} for prospect {prospect_id}")
        
        return {
            "success": True,
            "message": f"Informe {action} correctamente",
            "report": report
        }
    
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar informe: {str(e)}")


@api_router.patch("/admin/prospects/{prospect_id}/update-report")
async def update_prospect_report_manual(prospect_id: str, request: Request):
    """Update diagnostic report manually"""
    await require_admin(request)
    
    # Get request body
    body = await request.json()
    report_content = body.get("report_content")
    
    try:
        # Update report
        result = await db.questionnaire_responses.update_one(
            {"_id": prospect_id},
            {
                "$set": {
                    "report_content": report_content,
                    "report_edited": True,
                    "report_edited_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Prospecto no encontrado")
        
        logger.info(f"Report manually updated for prospect {prospect_id}")
        
        return {"success": True, "message": "Informe actualizado correctamente"}
    
    except Exception as e:
        logger.error(f"Error updating report: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar informe: {str(e)}")


        return prospect
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching prospect detail: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener detalle del prospecto")


@api_router.patch("/admin/prospects/{prospect_id}/stage")
async def update_prospect_stage(prospect_id: str, stage_update: ProspectStageUpdate, request: Request):
    """Update prospect stage"""
    await require_admin(request)
    
    try:
        # Get stage name
        stage = await db.prospect_stages.find_one({"_id": stage_update.stage_id})
        stage_name = stage["name"] if stage else "Sin etapa"
        
        # Update prospect
        result = await db.questionnaire_responses.update_one(
            {"_id": prospect_id},
            {"$set": {
                "stage_id": stage_update.stage_id,
                "stage_name": stage_name,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Prospecto no encontrado")
        
        return {"success": True, "message": "Etapa actualizada"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prospect stage: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar etapa")


@api_router.post("/admin/prospects/{prospect_id}/notes")
async def add_prospect_note(prospect_id: str, note_data: ProspectNoteCreate, request: Request):
    """Add a note to a prospect"""
    admin = await require_admin(request)
    
    try:
        note_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
        note_doc = {
            "_id": note_id,
            "prospect_id": prospect_id,
            "note": note_data.note,
            "created_by": admin["_id"],
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.prospect_notes.insert_one(note_doc)
        note_doc["id"] = note_doc["_id"]
        
        return note_doc
    
    except Exception as e:
        logger.error(f"Error adding prospect note: {e}")
        raise HTTPException(status_code=500, detail="Error al agregar nota")


@api_router.post("/admin/prospects/{prospect_id}/send-report-email")
async def send_prospect_report_email(prospect_id: str, request: Request):
    """Send GPT report to prospect via email (HTML formatted)"""
    await require_admin(request)
    
    try:
        # Get prospect
        prospect = await db.questionnaire_responses.find_one({"_id": prospect_id})
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospecto no encontrado")
        
        # Check if report exists
        if not prospect.get("report_content"):
            raise HTTPException(status_code=400, detail="No hay informe generado para este prospecto")
        
        # Convert markdown to HTML
        report_markdown = prospect["report_content"]
        report_html = markdown_to_html(report_markdown)
        
        # Send email
        from email_utils import send_email
        subject = f"Tu Análisis Personalizado - {prospect['nombre']}"
        
        email_sent = send_email(
            to_email=prospect["email"],
            subject=subject,
            html_body=report_html,
            text_body=report_markdown  # Fallback to markdown as plain text
        )
        
        if email_sent:
            # Update prospect with sent status AND change stage to "INFORME ENVIADO"
            await db.questionnaire_responses.update_one(
                {"_id": prospect_id},
                {
                    "$set": {
                        "report_sent_at": datetime.now(timezone.utc),
                        "report_sent_via": "email",
                        "stage_id": "stage_002",
                        "stage_name": "INFORME ENVIADO"
                    }
                }
            )
            logger.info(f"Report sent via email to {prospect['email']} - Stage changed to 'INFORME ENVIADO'")
            return {"success": True, "message": "Informe enviado por email correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al enviar el email")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending report email: {e}")
        raise HTTPException(status_code=500, detail=f"Error al enviar informe: {str(e)}")


@api_router.get("/admin/prospects/{prospect_id}/whatsapp-link")
async def get_whatsapp_link(prospect_id: str, request: Request):
    """Generate WhatsApp Web link with pre-filled report"""
    await require_admin(request)
    
    try:
        # Get prospect
        prospect = await db.questionnaire_responses.find_one({"_id": prospect_id})
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospecto no encontrado")
        
        # Check if report exists
        if not prospect.get("report_content"):
            raise HTTPException(status_code=400, detail="No hay informe generado para este prospecto")
        
        # Get WhatsApp number (remove + and spaces)
        whatsapp = prospect.get("whatsapp", "").replace("+", "").replace(" ", "").replace("-", "")
        if not whatsapp:
            raise HTTPException(status_code=400, detail="Este prospecto no tiene WhatsApp registrado")
        
        # Format report for WhatsApp (plain text, clean markdown)
        report_text = prospect["report_content"]
        # Remove markdown formatting for WhatsApp
        report_text = report_text.replace("**", "*")  # WhatsApp uses single asterisk for bold
        report_text = report_text.replace("# ", "")  # Remove markdown headers
        
        # URL encode the message
        from urllib.parse import quote
        encoded_message = quote(report_text)
        
        # Generate WhatsApp Web link
        whatsapp_link = f"https://wa.me/{whatsapp}?text={encoded_message}"
        
        # Update prospect (mark as sent via WhatsApp AND change stage to "INFORME ENVIADO")
        await db.questionnaire_responses.update_one(
            {"_id": prospect_id},
            {
                "$set": {
                    "report_sent_at": datetime.now(timezone.utc),
                    "report_sent_via": "whatsapp",
                    "stage_id": "stage_002",
                    "stage_name": "INFORME ENVIADO"
                }
            }
        )
        
        logger.info(f"WhatsApp link generated for prospect {prospect_id} - Stage changed to 'INFORME ENVIADO'")
        return {
            "success": True,
            "whatsapp_link": whatsapp_link,
            "phone": whatsapp
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating WhatsApp link: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar enlace de WhatsApp: {str(e)}")


@api_router.patch("/admin/prospects/{prospect_id}/update-report")
async def update_prospect_report(prospect_id: str, report_data: dict, request: Request):
    """Update the GPT report content for a prospect"""
    await require_admin(request)
    
    try:
        # Get prospect
        prospect = await db.questionnaire_responses.find_one({"_id": prospect_id})
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospecto no encontrado")
        
        # Get new report content
        new_report_content = report_data.get("report_content")
        if not new_report_content or not new_report_content.strip():
            raise HTTPException(status_code=400, detail="El contenido del informe no puede estar vacío")
        
        # Update report
        result = await db.questionnaire_responses.update_one(
            {"_id": prospect_id},
            {
                "$set": {
                    "report_content": new_report_content,
                    "report_updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Prospecto no encontrado")
        
        logger.info(f"Report updated for prospect {prospect_id}")
        return {"success": True, "message": "Informe actualizado correctamente"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating report: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar informe: {str(e)}")


def markdown_to_html(markdown_text: str) -> str:
    """Convert markdown to HTML with styling for email"""
    
    # Basic HTML template with styling
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 650px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .container {{
                background-color: white;
                padding: 40px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2563eb;
                font-size: 28px;
                margin-bottom: 20px;
                border-bottom: 3px solid #2563eb;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #1e40af;
                font-size: 22px;
                margin-top: 30px;
                margin-bottom: 15px;
            }}
            h3 {{
                color: #3b82f6;
                font-size: 18px;
                margin-top: 20px;
                margin-bottom: 10px;
            }}
            p {{
                margin-bottom: 15px;
                font-size: 16px;
            }}
            strong {{
                color: #1e40af;
            }}
            ul, ol {{
                margin: 15px 0;
                padding-left: 30px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            .highlight {{
                background-color: #eff6ff;
                padding: 15px;
                border-left: 4px solid #2563eb;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .footer {{
                margin-top: 40px;
                padding-top: 20px;
                border-top: 2px solid #e5e7eb;
                color: #6b7280;
                font-size: 14px;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            {content}
            <div class="footer">
                <p><strong>Jorge Calcerrada</strong><br>
                Entrenador Personal y Coach de Transformación<br>
                📧 ecjtrainer@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Convert markdown to HTML (basic conversion)
    html_content = markdown_text
    
    # Headers
    html_content = html_content.replace("# ", "<h1>").replace("\n\n", "</h1>\n\n")
    html_content = html_content.replace("## ", "<h2>").replace("\n\n", "</h2>\n\n")
    html_content = html_content.replace("### ", "<h3>").replace("\n\n", "</h3>\n\n")
    
    # Bold text
    import re
    html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
    
    # Lists (simple implementation)
    lines = html_content.split("\n")
    in_list = False
    processed_lines = []
    
    for line in lines:
        if line.strip().startswith("- "):
            if not in_list:
                processed_lines.append("<ul>")
                in_list = True
            processed_lines.append(f"<li>{line.strip()[2:]}</li>")
        else:
            if in_list:
                processed_lines.append("</ul>")
                in_list = False
            if line.strip():
                processed_lines.append(f"<p>{line}</p>")
            else:
                processed_lines.append("<br>")
    
    if in_list:
        processed_lines.append("</ul>")
    
    html_content = "\n".join(processed_lines)
    
    # Insert into template
    final_html = html_template.format(content=html_content)
    
    return final_html




@api_router.get("/admin/prospect-stages")
async def get_prospect_stages(request: Request):
    """Get all prospect stages"""
    await require_admin(request)
    
    try:
        stages = await db.prospect_stages.find().sort("order", 1).to_list(length=50)
        for stage in stages:
            stage["id"] = stage["_id"]
        
        return {"stages": stages}
    
    except Exception as e:
        logger.error(f"Error fetching stages: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener etapas")


@api_router.post("/admin/prospect-stages")
async def create_prospect_stage(stage_data: ProspectStageCreate, request: Request):
    """Create a new prospect stage"""
    await require_admin(request)
    
    try:
        stage_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
        stage_doc = {
            "_id": stage_id,
            "name": stage_data.name,
            "color": stage_data.color,
            "order": stage_data.order,
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.prospect_stages.insert_one(stage_doc)
        stage_doc["id"] = stage_doc["_id"]
        
        return stage_doc
    
    except Exception as e:
        logger.error(f"Error creating stage: {e}")
        raise HTTPException(status_code=500, detail="Error al crear etapa")


@api_router.patch("/admin/prospect-stages/{stage_id}")
async def update_prospect_stage_config(stage_id: str, stage_data: ProspectStageCreate, request: Request):
    """Update a prospect stage"""
    await require_admin(request)
    
    try:
        result = await db.prospect_stages.update_one(
            {"_id": stage_id},
            {"$set": {
                "name": stage_data.name,
                "color": stage_data.color,
                "order": stage_data.order
            }}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Etapa no encontrada")
        
        # Update all prospects with this stage
        await db.questionnaire_responses.update_many(
            {"stage_id": stage_id},
            {"$set": {"stage_name": stage_data.name}}
        )
        
        return {"success": True, "message": "Etapa actualizada"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating stage: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar etapa")


@api_router.delete("/admin/prospect-stages/{stage_id}")
async def delete_prospect_stage(stage_id: str, request: Request):
    """Delete a prospect stage"""
    await require_admin(request)
    
    try:
        # Check if any prospects are using this stage
        count = await db.questionnaire_responses.count_documents({"stage_id": stage_id})
        if count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede eliminar. {count} prospectos están usando esta etapa"
            )
        
        result = await db.prospect_stages.delete_one({"_id": stage_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Etapa no encontrada")
        
        return {"success": True, "message": "Etapa eliminada"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting stage: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar etapa")


@api_router.delete("/admin/prospects/{prospect_id}")
async def delete_prospect(prospect_id: str, request: Request):
    """Delete a prospect"""
    await require_admin(request)
    
    try:
        # Delete all notes associated with this prospect
        await db.prospect_notes.delete_many({"prospect_id": prospect_id})
        
        # Delete the prospect
        result = await db.questionnaire_responses.delete_one({"_id": prospect_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Prospecto no encontrado")
        
        logger.info(f"Prospect {prospect_id} deleted successfully")
        return {"success": True, "message": "Prospecto eliminado"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prospect: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar prospecto")


@api_router.post("/admin/prospects/{prospect_id}/convert")
async def convert_prospect(prospect_id: str, request: Request, target_crm: dict):
    """Convert a prospect to a client (team or external)"""
    await require_admin(request)
    
    try:
        # Get prospect data
        prospect = await db.questionnaire_responses.find_one({"_id": prospect_id})
        if not prospect:
            raise HTTPException(status_code=404, detail="Prospecto no encontrado")
        
        target = target_crm.get('target_crm')
        
        if target == 'team':
            # For team clients, we'll create a user account in the future
            # For now, just mark as converted to team
            await db.questionnaire_responses.update_one(
                {"_id": prospect_id},
                {"$set": {
                    "converted_to_client": True,
                    "conversion_type": "team",
                    "converted_at": datetime.now(timezone.utc)
                }}
            )
            logger.info(f"Prospect {prospect_id} converted to team client")
            return {"success": True, "message": "Prospecto convertido a Cliente Equipo"}
            
        elif target == 'external':
            # Create external client record
            client_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
            client_doc = {
                "_id": client_id,
                "nombre": prospect.get("nombre"),
                "email": prospect.get("email"),
                "whatsapp": prospect.get("whatsapp"),
                "edad": prospect.get("edad"),
                "objetivo": prospect.get("objetivo"),
                "source": "prospect",
                "prospect_id": prospect_id,
                "created_at": datetime.now(timezone.utc),
                "status": "active",
                # Default values
                "plan_weeks": 12,
                "start_date": None,
                "next_payment_date": None,
                "weeks_completed": 0,
                "payment_history": [],
                "notes": []
            }
            
            await db.external_clients.insert_one(client_doc)
            
            # Mark prospect as converted
            await db.questionnaire_responses.update_one(
                {"_id": prospect_id},
                {"$set": {
                    "converted_to_client": True,
                    "conversion_type": "external",
                    "converted_at": datetime.now(timezone.utc)
                }}
            )
            
            logger.info(f"Prospect {prospect_id} converted to external client {client_id}")
            return {"success": True, "message": "Prospecto convertido a Cliente Externo", "client_id": client_id}
        
        else:
            raise HTTPException(status_code=400, detail="Tipo de CRM inválido")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error converting prospect: {e}")
        raise HTTPException(status_code=500, detail="Error al convertir prospecto")


# ==================== TEAM CLIENTS CRM ENDPOINTS ====================

@api_router.get("/admin/team-clients")
async def get_team_clients(request: Request, status: Optional[str] = None):
    """Get all team clients (ONLY registered users, NO prospects)"""
    await require_admin(request)
    
    try:
        # Solo obtener usuarios registrados (role=user) que tengan plan team
        users = await db.users.find({
            "role": "user",
            "subscription.plan": "team"
        }).to_list(length=1000)
        
        # Formatear lista
        clients_list = []
        
        for user in users:
            # Determinar el status del cliente (puede venir de client_status o del payment_status)
            client_status = user.get("client_status")
            if not client_status:
                # Fallback a payment_status si no existe client_status
                payment_status = user.get("subscription", {}).get("payment_status", "pending")
                client_status = "active" if payment_status == "verified" else "pending"
            
            clients_list.append({
                "id": user["_id"],
                "nombre": user.get("name"),
                "username": user.get("username"),
                "email": user.get("email"),
                "phone": user.get("phone"),
                "created_at": user.get("created_at"),
                "status": client_status,
                "source": "registration",
                "subscription": user.get("subscription", {})
            })
        
        # Sort by created_at
        clients_list.sort(key=lambda x: x.get("created_at") or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        
        return {"clients": clients_list, "total": len(clients_list)}
    
    except Exception as e:
        logger.error(f"Error fetching team clients: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener clientes")


@api_router.get("/admin/team-clients/{client_id}")
async def get_team_client_detail(client_id: str, request: Request):
    """Get detailed information about a team client"""
    await require_admin(request)
    
    try:
        # Try to find in converted prospects first
        prospect = await db.questionnaire_responses.find_one({"_id": client_id, "converted_to_client": True})
        
        if prospect:
            # Get notes for this client
            notes = await db.team_client_notes.find({"client_id": client_id}).sort("created_at", -1).to_list(length=1000)
            for note in notes:
                note["id"] = note["_id"]
            
            return {
                "id": prospect["_id"],
                "nombre": prospect.get("nombre"),
                "email": prospect.get("email"),
                "whatsapp": prospect.get("whatsapp"),
                "created_at": prospect.get("converted_at"),
                "status": "active",
                "source": "prospect",
                "prospect_data": {
                    "objetivo": prospect.get("objetivo"),
                    "presupuesto": prospect.get("presupuesto"),
                    "intentos_previos": prospect.get("intentos_previos"),
                    "alimentacion": prospect.get("alimentacion"),
                    "por_que_ahora": prospect.get("por_que_ahora")
                },
                "notes": notes
            }
        
        # Try to find in regular users
        user = await db.users.find_one({"_id": client_id})
        if user:
            notes = await db.team_client_notes.find({"client_id": client_id}).sort("created_at", -1).to_list(length=1000)
            for note in notes:
                note["id"] = note["_id"]
            
            return {
                "id": user["_id"],
                "name": user.get("name"),
                "nombre": user.get("name"),
                "username": user.get("username"),
                "email": user.get("email"),
                "whatsapp": user.get("whatsapp"),
                "created_at": user.get("created_at"),
                "status": "active",
                "source": "registration",
                "subscription": user.get("subscription", {}),
                "notes": notes
            }
        
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching team client detail: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener detalle del cliente")


@api_router.post("/admin/team-clients/{client_id}/notes")
async def add_team_client_note(client_id: str, note_data: dict, request: Request):
    """Add a note to a team client"""
    admin = await require_admin(request)
    
    try:
        note_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
        note_doc = {
            "_id": note_id,
            "client_id": client_id,
            "note": note_data.get("note"),
            "created_by": admin["_id"],
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.team_client_notes.insert_one(note_doc)
        note_doc["id"] = note_doc["_id"]
        
        return note_doc
    
    except Exception as e:
        logger.error(f"Error adding team client note: {e}")
        raise HTTPException(status_code=500, detail="Error al agregar nota")


@api_router.patch("/admin/team-clients/{client_id}/status")
async def update_team_client_status(client_id: str, status_data: dict, request: Request):
    """Update team client status"""
    await require_admin(request)
    
    try:
        new_status = status_data.get("status")
        
        # Try to update in converted prospects
        result = await db.questionnaire_responses.update_one(
            {"_id": client_id, "converted_to_client": True},
            {"$set": {"client_status": new_status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        if result.matched_count == 0:
            # Try to update in users
            result = await db.users.update_one(
                {"_id": client_id},
                {"$set": {"client_status": new_status, "updated_at": datetime.now(timezone.utc)}}
            )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return {"success": True, "message": "Estado actualizado"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating team client status: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar estado")


@api_router.delete("/admin/team-clients/{client_id}")
async def delete_team_client(client_id: str, request: Request):
    """Delete a team client"""
    await require_admin(request)
    
    try:
        # Try to delete from converted prospects first
        result = await db.questionnaire_responses.delete_one({"_id": client_id, "converted_to_client": True})
        
        if result.deleted_count == 0:
            # Try to delete from users
            result = await db.users.delete_one({"_id": client_id})
        
        # Delete associated notes
        await db.team_client_notes.delete_many({"client_id": client_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        logger.info(f"Team client deleted: {client_id}")
        return {"success": True, "message": "Cliente eliminado"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting team client: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar cliente")


@api_router.post("/admin/team-clients/{client_id}/move")
async def move_team_client(client_id: str, request: Request, target_data: dict):
    """Move a team client to another CRM"""
    await require_admin(request)
    
    try:
        target_crm = target_data.get("target_crm")
        
        # Get client data
        client = None
        source_type = None
        
        # Try in converted prospects first
        client = await db.questionnaire_responses.find_one({"_id": client_id, "converted_to_client": True})
        if client:
            source_type = "prospect"
        else:
            # Try in users
            client = await db.users.find_one({"_id": client_id})
            if client:
                source_type = "user"
        
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        if target_crm == 'external':
            # Move to external clients
            external_client_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
            external_client_doc = {
                "_id": external_client_id,
                "nombre": client.get("nombre") or client.get("name"),
                "email": client.get("email"),
                "whatsapp": client.get("whatsapp", ""),
                "objetivo": client.get("objetivo", ""),
                "plan_weeks": 12,  # Default
                "start_date": datetime.now(timezone.utc),
                "next_payment_date": datetime.now(timezone.utc) + timedelta(weeks=12),
                "weeks_completed": 0,
                "status": "active",
                "payment_history": [],
                "notes": [],
                "source": "team_client",
                "original_team_client_id": client_id,
                "created_at": datetime.now(timezone.utc)
            }
            
            await db.external_clients.insert_one(external_client_doc)
            
            # Mark as moved in original location
            if source_type == "prospect":
                await db.questionnaire_responses.update_one(
                    {"_id": client_id},
                    {"$set": {"moved_to_external": True, "moved_at": datetime.now(timezone.utc)}}
                )
            else:
                await db.users.update_one(
                    {"_id": client_id},
                    {"$set": {"moved_to_external": True, "moved_at": datetime.now(timezone.utc)}}
                )
            
            logger.info(f"Team client {client_id} moved to external clients as {external_client_id}")
            return {"success": True, "message": "Cliente movido a Clientes Externos"}
        
        raise HTTPException(status_code=400, detail="Target CRM inválido")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moving team client: {e}")
        raise HTTPException(status_code=500, detail="Error al mover cliente")


# ==================== EXTERNAL CLIENTS CRM ENDPOINTS ====================

@api_router.get("/admin/external-clients")
async def get_external_clients(request: Request, status: Optional[str] = None):
    """Get all external clients"""
    await require_admin(request)
    
    try:
        query = {"moved_to_team": {"$ne": True}}
        if status:
            query["status"] = status
        
        clients = await db.external_clients.find(query).sort("created_at", -1).to_list(length=1000)
        
        clients_list = []
        for client in clients:
            client["id"] = client["_id"]
            clients_list.append(client)
        
        return {"clients": clients_list, "total": len(clients_list)}
    
    except Exception as e:
        logger.error(f"Error fetching external clients: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener clientes externos")


@api_router.get("/admin/external-clients/{client_id}")
async def get_external_client_detail(client_id: str, request: Request):
    """Get detailed information about an external client"""
    await require_admin(request)
    
    try:
        client = await db.external_clients.find_one({"_id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        client["id"] = client["_id"]
        return client
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching external client detail: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener detalle del cliente")


@api_router.post("/admin/external-clients")
async def create_external_client(client_data: ExternalClientCreate, request: Request):
    """Create a new external client"""
    await require_admin(request)
    
    try:
        client_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
        
        # Calculate next payment date based on start date and plan weeks
        start_date = None
        next_payment_date = None
        if client_data.start_date:
            start_date = datetime.fromisoformat(client_data.start_date).replace(tzinfo=timezone.utc)
            # Next payment is after the plan weeks
            next_payment_date = start_date + timedelta(weeks=client_data.plan_weeks)
        
        client_doc = {
            "_id": client_id,
            "nombre": client_data.nombre,
            "email": client_data.email,
            "whatsapp": client_data.whatsapp,
            "objetivo": client_data.objetivo,
            "plan_weeks": client_data.plan_weeks,
            "start_date": start_date,
            "next_payment_date": next_payment_date,
            "weeks_completed": 0,
            "status": "active",
            "payment_history": [],
            "notes": [],
            "source": "manual",
            "created_at": datetime.now(timezone.utc)
        }
        
        # Add initial payment if provided
        if client_data.amount_paid and float(client_data.amount_paid) > 0:
            client_doc["payment_history"] = [{
                "amount": float(client_data.amount_paid),
                "date": start_date or datetime.now(timezone.utc),
                "notes": "Pago inicial"
            }]
        
        # Add initial note if provided
        if client_data.notes:
            client_doc["notes"] = [{
                "id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
                "note": client_data.notes,
                "created_at": datetime.now(timezone.utc)
            }]
        
        await db.external_clients.insert_one(client_doc)
        
        logger.info(f"External client created: {client_id}")
        return {"success": True, "message": "Cliente creado", "client_id": client_id}
    
    except Exception as e:
        logger.error(f"Error creating external client: {e}")
        raise HTTPException(status_code=500, detail="Error al crear cliente")


@api_router.delete("/admin/external-clients/{client_id}")
async def delete_external_client(client_id: str, request: Request):
    """Delete an external client"""
    await require_admin(request)
    
    try:
        result = await db.external_clients.delete_one({"_id": client_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        logger.info(f"External client deleted: {client_id}")
        return {"success": True, "message": "Cliente eliminado"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting external client: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar cliente")


@api_router.post("/admin/external-clients/{client_id}/payments")
async def add_payment(client_id: str, payment_data: dict, request: Request):
    """Add a payment to external client"""
    await require_admin(request)
    
    try:
        payment = {
            "id": str(int(datetime.now(timezone.utc).timestamp() * 1000000)),
            "amount": float(payment_data.get("amount")),
            "date": datetime.fromisoformat(payment_data.get("date")).replace(tzinfo=timezone.utc),
            "notes": payment_data.get("notes", ""),
            "metodo_pago": payment_data.get("metodo_pago", "Transferencia")  # Bizum, Transferencia, Efectivo
        }
        
        # Get client to calculate new next_payment_date
        client = await db.external_clients.find_one({"_id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Update next payment date (add plan_weeks from payment date)
        new_next_payment = payment["date"] + timedelta(weeks=client.get("plan_weeks", 12))
        
        # Add payment and update next payment date
        result = await db.external_clients.update_one(
            {"_id": client_id},
            {
                "$push": {"payment_history": payment},
                "$set": {"next_payment_date": new_next_payment}
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        logger.info(f"Payment added to external client {client_id} - Método: {payment['metodo_pago']}")
        return {"success": True, "message": "Pago registrado", "payment": payment}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding payment: {e}")
        raise HTTPException(status_code=500, detail="Error al registrar pago")


@api_router.put("/admin/external-clients/{client_id}/payments/{payment_id}")
async def edit_payment(client_id: str, payment_id: str, payment_data: dict, request: Request):
    """Edit a payment from external client"""
    await require_admin(request)
    
    try:
        client = await db.external_clients.find_one({"_id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        payments = client.get("payment_history", [])
        payment_found = False
        
        for i, payment in enumerate(payments):
            if payment.get("id") == payment_id:
                payments[i] = {
                    "id": payment_id,
                    "amount": float(payment_data.get("amount")),
                    "date": datetime.fromisoformat(payment_data.get("date")).replace(tzinfo=timezone.utc),
                    "notes": payment_data.get("notes", ""),
                    "metodo_pago": payment_data.get("metodo_pago", "Transferencia")
                }
                payment_found = True
                break
        
        if not payment_found:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        result = await db.external_clients.update_one(
            {"_id": client_id},
            {"$set": {"payment_history": payments}}
        )
        
        logger.info(f"Payment {payment_id} edited for client {client_id}")
        return {"success": True, "message": "Pago actualizado"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error editing payment: {e}")
        raise HTTPException(status_code=500, detail="Error al editar pago")


@api_router.delete("/admin/external-clients/{client_id}/payments/{payment_id}")
async def delete_payment(client_id: str, payment_id: str, request: Request):
    """Delete a payment from external client"""
    await require_admin(request)
    
    try:
        client = await db.external_clients.find_one({"_id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        payments = client.get("payment_history", [])
        payments = [p for p in payments if p.get("id") != payment_id]
        
        result = await db.external_clients.update_one(
            {"_id": client_id},
            {"$set": {"payment_history": payments}}
        )
        
        logger.info(f"Payment {payment_id} deleted from client {client_id}")
        return {"success": True, "message": "Pago eliminado"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting payment: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar pago")


@api_router.post("/admin/external-clients/{client_id}/notes")
async def add_external_client_note(client_id: str, note_data: dict, request: Request):
    """Add a note to an external client"""
    await require_admin(request)
    
    try:
        note = {
            "id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
            "note": note_data.get("note"),
            "created_at": datetime.now(timezone.utc)
        }
        
        result = await db.external_clients.update_one(
            {"_id": client_id},
            {"$push": {"notes": note}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return note
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding note: {e}")
        raise HTTPException(status_code=500, detail="Error al agregar nota")


@api_router.patch("/admin/external-clients/{client_id}/status")
async def update_external_client_status(client_id: str, status_data: dict, request: Request):
    """Update external client status"""
    await require_admin(request)
    
    try:
        new_status = status_data.get("status")
        
        result = await db.external_clients.update_one(
            {"_id": client_id},
            {"$set": {"status": new_status, "updated_at": datetime.now(timezone.utc)}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        return {"success": True, "message": "Estado actualizado"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating external client status: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar estado")


@api_router.patch("/admin/external-clients/{client_id}")
async def update_external_client(client_id: str, update_data: ExternalClientUpdate, request: Request):
    """Update external client information"""
    await require_admin(request)
    
    try:
        # Build update document from provided fields only
        update_doc = {}
        
        if update_data.nombre is not None:
            update_doc["nombre"] = update_data.nombre
        if update_data.email is not None:
            update_doc["email"] = update_data.email
        if update_data.whatsapp is not None:
            update_doc["whatsapp"] = update_data.whatsapp
        if update_data.objetivo is not None:
            update_doc["objetivo"] = update_data.objetivo
        if update_data.plan_weeks is not None:
            update_doc["plan_weeks"] = update_data.plan_weeks
            # Recalculate next_payment_date if plan weeks changed
            client = await db.external_clients.find_one({"_id": client_id})
            if client and client.get("start_date"):
                start_date = client["start_date"]
                update_doc["next_payment_date"] = start_date + timedelta(weeks=update_data.plan_weeks)
        if update_data.start_date is not None:
            start_date = datetime.fromisoformat(update_data.start_date).replace(tzinfo=timezone.utc)
            update_doc["start_date"] = start_date
            # Also update next_payment_date
            client = await db.external_clients.find_one({"_id": client_id})
            if client:
                plan_weeks = update_data.plan_weeks if update_data.plan_weeks is not None else client.get("plan_weeks", 12)
                update_doc["next_payment_date"] = start_date + timedelta(weeks=plan_weeks)
        if update_data.weeks_completed is not None:
            update_doc["weeks_completed"] = update_data.weeks_completed
        
        update_doc["updated_at"] = datetime.now(timezone.utc)
        
        if not update_doc:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        result = await db.external_clients.update_one(
            {"_id": client_id},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        logger.info(f"External client updated: {client_id}")
        return {"success": True, "message": "Cliente actualizado"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating external client: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar cliente")


@api_router.post("/admin/external-clients/{client_id}/move")
async def move_external_client(client_id: str, request: Request, target_data: dict):
    """Move an external client to team clients CRM"""
    await require_admin(request)
    
    try:
        target_crm = target_data.get("target_crm")
        
        # Get external client data
        client = await db.external_clients.find_one({"_id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        if target_crm == 'team':
            # Convert external client to team client (as converted prospect)
            team_client_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
            team_client_doc = {
                "_id": team_client_id,
                "nombre": client.get("nombre"),
                "email": client.get("email"),
                "whatsapp": client.get("whatsapp"),
                "objetivo": client.get("objetivo", ""),
                "converted_to_client": True,
                "conversion_type": "team",
                "converted_at": datetime.now(timezone.utc),
                "source": "external_client",
                "original_external_client_id": client_id
            }
            
            await db.questionnaire_responses.insert_one(team_client_doc)
            
            # Mark as moved
            await db.external_clients.update_one(
                {"_id": client_id},
                {"$set": {"moved_to_team": True, "moved_at": datetime.now(timezone.utc)}}
            )
            
            # Optionally delete from external clients
            # await db.external_clients.delete_one({"_id": client_id})
            
            logger.info(f"External client {client_id} moved to team clients as {team_client_id}")
            return {"success": True, "message": "Cliente movido a Clientes Equipo"}
        
        raise HTTPException(status_code=400, detail="Target CRM inválido")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moving external client: {e}")
        raise HTTPException(status_code=500, detail="Error al mover cliente")


# ==================== SOCKET.IO EVENTS ====================

# Store connected users: {user_id: sid}
connected_users = {}

@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    logger.info(f"Client connected: {sid}")
    await sio.emit('connected', {'status': 'connected'}, room=sid)


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    # Remove user from connected users
    user_id_to_remove = None
    for user_id, socket_id in connected_users.items():
        if socket_id == sid:
            user_id_to_remove = user_id
            break
    
    if user_id_to_remove:
        del connected_users[user_id_to_remove]
    
    logger.info(f"Client disconnected: {sid}")


@sio.event
async def authenticate(sid, data):
    """Authenticate user via session_token or JWT"""
    try:
        token = data.get('token')
        if not token:
            await sio.emit('auth_error', {'message': 'No token provided'}, room=sid)
            return
        
        # Try to get user from session_token first
        session = await db.user_sessions.find_one({"session_token": token})
        if session and session["expires_at"] > datetime.now(timezone.utc):
            user_id = session["user_id"]
        else:
            # Fallback to JWT
            try:
                from auth import decode_token
                user_id = decode_token(token)
            except:
                await sio.emit('auth_error', {'message': 'Invalid token'}, room=sid)
                return
        
        # Store the connection
        connected_users[user_id] = sid
        
        # Get user data
        user = await db.users.find_one({"_id": user_id})
        if user:
            await sio.emit('authenticated', {
                'user_id': user_id,
                'name': user.get('name'),
                'role': user.get('role')
            }, room=sid)
            logger.info(f"User {user_id} authenticated on socket {sid}")
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        await sio.emit('auth_error', {'message': str(e)}, room=sid)


@sio.event
async def send_message(sid, data):
    """Handle incoming chat messages"""
    try:
        # Find which user this socket belongs to
        sender_id = None
        for user_id, socket_id in connected_users.items():
            if socket_id == sid:
                sender_id = user_id
                break
        
        if not sender_id:
            await sio.emit('error', {'message': 'Not authenticated'}, room=sid)
            return
        
        # Get sender info
        sender = await db.users.find_one({"_id": sender_id})
        if not sender:
            await sio.emit('error', {'message': 'User not found'}, room=sid)
            return
        
        # Determine recipient (for admin-client chat)
        recipient_id = data.get('user_id') if sender['role'] == 'admin' else sender_id
        message_text = data.get('message')
        
        if not message_text:
            await sio.emit('error', {'message': 'Message is required'}, room=sid)
            return
        
        # Save message to database
        message_dict = {
            "_id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
            "user_id": recipient_id,
            "sender_id": sender_id,
            "sender_name": sender.get('name'),
            "message": message_text,
            "is_admin": sender['role'] == 'admin',
            "timestamp": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.messages.insert_one(message_dict)
        message_dict["id"] = message_dict["_id"]
        
        # Send to sender
        await sio.emit('new_message', message_dict, room=sid)
        
        # Send to recipient if they're online
        if sender['role'] == 'admin':
            # Admin sending to user
            if recipient_id in connected_users:
                await sio.emit('new_message', message_dict, room=connected_users[recipient_id])
        else:
            # User sending to admin - find admin's socket
            admins = await db.users.find({"role": "admin"}).to_list(10)
            for admin in admins:
                if admin["_id"] in connected_users:
                    await sio.emit('new_message', message_dict, room=connected_users[admin["_id"]])
        
        logger.info(f"Message from {sender_id} to {recipient_id}: {message_text}")
    
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await sio.emit('error', {'message': str(e)}, room=sid)


@sio.event
async def join_chat(sid, data):
    """Join a specific chat room (for admin viewing client chats)"""
    try:
        user_id = data.get('user_id')
        if user_id:
            await sio.enter_room(sid, f"chat_{user_id}")
            logger.info(f"Socket {sid} joined chat_{user_id}")
    except Exception as e:
        logger.error(f"Error joining chat: {e}")

# ==================== ROOT ENDPOINT ====================

@api_router.get("/")
async def root():
    return {"message": "Jorge Calcerrada API - Working"}


# ============================================
# TEMPLATES & AUTOMATION ENDPOINTS
# ============================================

@api_router.get("/admin/templates/tags/all")
async def get_all_tags(request: Request):
    """Get all unique tags from templates AND global tags collection"""
    await require_admin(request)
    
    try:
        # Get tags from templates using aggregation (more efficient)
        template_tags_pipeline = [
            {"$match": {"tags": {"$exists": True, "$ne": []}}},
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags"}}
        ]
        template_tags_result = await db.message_templates.aggregate(template_tags_pipeline).to_list(length=1000)
        template_tags = set(doc["_id"] for doc in template_tags_result)
        
        # Get tags from global_tags collection (only _id field needed)
        global_tags_docs = await db.global_tags.find({}, {"_id": 1}).to_list(length=1000)
        global_tags = set(tag["_id"] for tag in global_tags_docs)
        
        # Combine both sets
        all_tags = template_tags.union(global_tags)
        
        return {"tags": sorted(list(all_tags))}
    except Exception as e:
        logger.error(f"Error getting all tags: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener tags")


@api_router.post("/admin/templates/tags")
async def create_global_tag(tag_data: dict, request: Request):
    """Create a new global tag"""
    await require_admin(request)
    
    try:
        new_tag = tag_data.get("tag", "").strip()
        if not new_tag:
            raise HTTPException(status_code=400, detail="Tag vacío")
        
        # Check if tag already exists
        existing = await db.global_tags.find_one({"_id": new_tag})
        if existing:
            raise HTTPException(status_code=400, detail="Tag ya existe")
        
        await db.global_tags.insert_one({
            "_id": new_tag,
            "created_at": datetime.now(timezone.utc)
        })
        
        return {"success": True, "message": "Tag creado", "tag": new_tag}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
        raise HTTPException(status_code=500, detail="Error al crear tag")


@api_router.delete("/admin/templates/tags/{tag_name}")
async def delete_global_tag(tag_name: str, request: Request):
    """Delete a global tag (warns if in use)"""
    await require_admin(request)
    
    try:
        # Check if tag is being used in any template
        templates_using_tag = await db.message_templates.count_documents({
            "tags": tag_name
        })
        
        if templates_using_tag > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Este tag está siendo usado en {templates_using_tag} template(s). No se puede eliminar."
            )
        
        # Delete the tag
        result = await db.global_tags.delete_one({"_id": tag_name})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Tag no encontrado")
        
        return {"success": True, "message": "Tag eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting tag: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar tag")


@api_router.get("/admin/templates")
async def get_templates(request: Request, type: Optional[str] = None, tags: Optional[str] = None):
    """Get all message templates with optional filtering by type and tags"""
    await require_admin(request)
    
    try:
        query = {}
        if type:
            query["type"] = type
        if tags:
            # Filter by tags (comma separated)
            tag_list = [t.strip() for t in tags.split(',')]
            query["tags"] = {"$in": tag_list}
        
        templates = await db.message_templates.find(query).to_list(length=1000)
        
        return {
            "templates": [
                {
                    "id": str(t["_id"]),
                    "type": t["type"],
                    "name": t["name"],
                    "subject": t.get("subject"),
                    "content": t["content"],
                    "variables": t.get("variables", []),
                    "category": t["category"],
                    "tags": t.get("tags", []),
                    "created_at": t["created_at"]
                }
                for t in templates
            ]
        }
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener templates")


@api_router.post("/admin/templates")
async def create_template(template_data: TemplateCreate, request: Request):
    """Create a new message template"""
    await require_admin(request)
    
    try:
        template_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
        
        template_doc = {
            "_id": template_id,
            "type": template_data.type,
            "name": template_data.name,
            "subject": template_data.subject,
            "content": template_data.content,
            "variables": template_data.variables,
            "category": template_data.category,
            "tags": template_data.tags,
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.message_templates.insert_one(template_doc)
        
        return {"success": True, "message": "Template creado", "template_id": template_id}
    except Exception as e:
        logger.error(f"Error creating template: {e}")
        raise HTTPException(status_code=500, detail="Error al crear template")


@api_router.delete("/admin/templates/{template_id}")
async def delete_template(template_id: str, request: Request):
    """Delete a message template"""
    await require_admin(request)
    
    try:
        result = await db.message_templates.delete_one({"_id": template_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Template no encontrado")
        
        return {"success": True, "message": "Template eliminado"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting template: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar template")


@api_router.patch("/admin/templates/{template_id}")
async def update_template(template_id: str, template_data: TemplateUpdate, request: Request):
    """Update a message template"""
    await require_admin(request)
    
    try:
        # Build update document from provided fields
        update_doc = {}
        
        if template_data.name is not None:
            update_doc["name"] = template_data.name
        if template_data.subject is not None:
            update_doc["subject"] = template_data.subject
        if template_data.content is not None:
            update_doc["content"] = template_data.content
        if template_data.category is not None:
            update_doc["category"] = template_data.category
        if template_data.tags is not None:
            update_doc["tags"] = template_data.tags
        
        if not update_doc:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        result = await db.message_templates.update_one(
            {"_id": template_id},
            {"$set": update_doc}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Template no encontrado")
        
        return {"success": True, "message": "Template actualizado"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating template: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar template")


@api_router.get("/admin/reminder-config")
async def get_reminder_config(request: Request):
    """Get reminder configuration"""
    await require_admin(request)
    
    try:
        config = await db.reminder_config.find_one({"_id": "default"})
        if not config:
            # Return default config
            return {
                "form_reminder_enabled": True,
                "form_reminder_days": 3,
                "session_reminder_enabled": True,
                "session_reminder_hours": 24,
                "inactive_alert_enabled": True,
                "inactive_alert_days": 7
            }
        return config
    except Exception as e:
        logger.error(f"Error getting reminder config: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener configuración")


@api_router.put("/admin/reminder-config")
async def update_reminder_config(config: ReminderConfig, request: Request):
    """Update reminder configuration"""
    await require_admin(request)
    
    try:
        await db.reminder_config.update_one(
            {"_id": "default"},
            {"$set": config.dict()},
            upsert=True
        )
        return {"success": True, "message": "Configuración actualizada"}
    except Exception as e:
        logger.error(f"Error updating reminder config: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar configuración")


@api_router.get("/admin/clients-at-risk")
async def get_clients_at_risk(request: Request):
    """Get list of clients that need attention based on risk indicators"""
    await require_admin(request)
    
    try:
        # Get reminder config
        config = await db.reminder_config.find_one({"_id": "default"})
        inactive_days_threshold = config.get("inactive_alert_days", 7) if config else 7
        form_days_threshold = config.get("form_reminder_days", 3) if config else 3
        
        # Get all active clients (not archived)
        clients = await db.users.find({
            "role": "user",
            "subscription.archived": {"$ne": True}
        }).to_list(length=1000)
        
        at_risk_clients = []
        now = datetime.now(timezone.utc)
        
        for client in clients:
            risk_reasons = []
            risk_level = "green"
            days_inactive = None
            pending_forms_days = None
            last_activity = None
            
            # Check last session
            last_session = await db.sessions.find_one(
                {"user_id": client["_id"]},
                sort=[("date", -1)]
            )
            
            if last_session and last_session.get("date"):
                days_since_session = (now - last_session["date"]).days
                if days_since_session >= 14:
                    risk_reasons.append(f"{days_since_session} días sin sesión")
                    risk_level = "red"
                    days_inactive = days_since_session
                    last_activity = last_session["date"]
                elif days_since_session >= inactive_days_threshold:
                    risk_reasons.append(f"{days_since_session} días sin sesión")
                    risk_level = "yellow" if risk_level == "green" else risk_level
                    days_inactive = days_since_session
                    last_activity = last_session["date"]
            elif not last_session:
                # New client with no sessions yet
                days_since_registration = (now - client["created_at"]).days
                if days_since_registration >= 7:
                    risk_reasons.append("Sin sesiones registradas")
                    risk_level = "yellow" if risk_level == "green" else risk_level
            
            # Check pending forms
            pending_forms = await db.forms.find({
                "user_id": client["_id"],
                "completed": False
            }).to_list(length=1000)
            
            for form in pending_forms:
                days_pending = (now - form["sent_date"]).days
                if days_pending >= 7:
                    risk_reasons.append(f"Formulario pendiente {days_pending} días")
                    risk_level = "red"
                    pending_forms_days = days_pending
                elif days_pending >= form_days_threshold:
                    risk_reasons.append(f"Formulario pendiente {days_pending} días")
                    risk_level = "yellow" if risk_level == "green" else risk_level
                    pending_forms_days = days_pending
            
            # Only include clients with yellow or red risk
            if risk_level in ["yellow", "red"]:
                at_risk_clients.append({
                    "client_id": client["_id"],
                    "client_name": client.get("name", client["username"]),
                    "client_email": client["email"],
                    "risk_level": risk_level,
                    "risk_reasons": risk_reasons,
                    "days_inactive": days_inactive,
                    "pending_forms_days": pending_forms_days,
                    "last_activity_date": last_activity
                })
        
        # Sort by risk level (red first, then yellow)
        at_risk_clients.sort(key=lambda x: (0 if x["risk_level"] == "red" else 1, x["client_name"]))
        
        return {
            "clients_at_risk": at_risk_clients,
            "total_red": len([c for c in at_risk_clients if c["risk_level"] == "red"]),
            "total_yellow": len([c for c in at_risk_clients if c["risk_level"] == "yellow"])
        }
    except Exception as e:
        logger.error(f"Error getting clients at risk: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener clientes en riesgo")


@api_router.post("/admin/send-email-template")
async def send_email_template(email_data: dict, request: Request):
    """Send email using template"""
    await require_admin(request)
    
    try:
        from email_utils import send_email
        
        to_email = email_data.get("to_email")
        subject = email_data.get("subject")
        message = email_data.get("message")
        
        if not to_email or not subject or not message:
            raise HTTPException(status_code=400, detail="Faltan datos requeridos")
        
        # Convert plain text to HTML
        html_body = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="white-space: pre-wrap;">{message}</div>
                    <br><br>
                    <div style="border-top: 1px solid #ddd; padding-top: 20px; margin-top: 20px; color: #666; font-size: 12px;">
                        <p>Jorge Calcerrada - Entrenador Personal</p>
                        <p>Email: ecjtrainer@gmail.com</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        # Send email
        success = send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=message
        )
        
        if success:
            return {"success": True, "message": "Email enviado correctamente"}
        else:
            raise HTTPException(status_code=500, detail="Error al enviar email")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email template: {e}")
        raise HTTPException(status_code=500, detail=f"Error al enviar email: {str(e)}")


# =====================================================
# GOOGLE CALENDAR INTEGRATION
# =====================================================



# ==================== NUTRITION ENDPOINTS ====================

@api_router.post("/nutrition/questionnaire/submit")
async def submit_nutrition_questionnaire(questionnaire: NutritionQuestionnaireSubmit, request: Request):
    """
    Usuario completa cuestionario de nutrición - SOLO GUARDA RESPUESTAS (no genera plan)
    
    FASE 1 DUAL-WRITE:
    - Guarda en BD Web (nutrition_questionnaire_submissions) como siempre
    - Si USE_CLIENT_DRAWER_WRITE=true, también guarda en client_drawers
    """
    user = await get_current_user(request)
    user_id = user["_id"]
    
    # Verificar que el usuario tiene plan team y pago verificado
    if user.get("subscription", {}).get("plan") != "team":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo usuarios con plan Team pueden acceder al cuestionario de nutrición"
        )
    
    if user.get("subscription", {}).get("payment_status") != "verified":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debes verificar el pago antes de acceder al cuestionario de nutrición"
        )
    
    try:
        # Convertir el cuestionario a dict
        questionnaire_data = questionnaire.dict()
        
        # Generar ID único para esta submission
        submission_id = str(int(datetime.now(timezone.utc).timestamp() * 1000000))
        submitted_at = datetime.now(timezone.utc)
        
        # ============================================
        # 1. GUARDAR EN BD WEB (fuente de verdad)
        # ============================================
        submission_doc = {
            "_id": submission_id,
            "user_id": user_id,
            "responses": questionnaire_data,
            "submitted_at": submitted_at,
            "plan_generated": False,  # El admin generará el plan después
            "plan_id": None
        }
        
        await db.nutrition_questionnaire_submissions.insert_one(submission_doc)
        logger.info(f"✅ Cuestionario guardado en BD Web: {submission_id} (user_id: {user_id})")
        
        # ============================================
        # 2. DUAL-WRITE A CLIENT_DRAWERS (best effort)
        # ============================================
        use_client_drawer_write = os.getenv('USE_CLIENT_DRAWER_WRITE', 'false').lower() == 'true'
        
        if use_client_drawer_write:
            try:
                from repositories.client_drawer_repository import add_questionnaire_to_drawer
                
                # Añadir cuestionario a client_drawer
                await add_questionnaire_to_drawer(
                    user_id=user_id,
                    submission_id=submission_id,
                    submitted_at=submitted_at,
                    source="initial",  # Cuestionario inicial
                    raw_payload=submission_doc  # Documento completo
                )
                
                logger.info(f"✅ Dual-write exitoso a client_drawers: {submission_id}")
                
            except Exception as drawer_error:
                # ⚠️ BEST EFFORT: Si falla client_drawers, NO falla el endpoint
                logger.error(
                    f"⚠️  Dual-write to client_drawers failed for user_id {user_id}, "
                    f"submission_id {submission_id}: {drawer_error}"
                )
                # Continuar normalmente, BD Web ya tiene el cuestionario
        else:
            logger.info(f"ℹ️  USE_CLIENT_DRAWER_WRITE=false, solo se guardó en BD Web")
        
        # ============================================
        # 3. RESPONDER AL FRONTEND
        # ============================================
        return {
            "success": True,
            "message": "¡Cuestionario enviado correctamente! Jorge revisará tus respuestas y generará tu plan personalizado.",
            "submission_id": submission_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error guardando cuestionario: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error guardando cuestionario: {str(e)}"
        )



@api_router.post("/admin/users/{user_id}/nutrition/generate")
async def admin_generate_nutrition_plan(
    user_id: str, 
    submission_id: str,  # Cuestionario a usar
    training_plan_id: str = None,  # Plan de entrenamiento de referencia
    previous_nutrition_plan_id: str = None,  # NUEVO: Plan nutricional previo para progresión
    regenerate: bool = False, 
    request: Request = None
):
    """
    Admin genera el plan de nutrición desde las respuestas del cuestionario
    
    Parámetros:
    - submission_id: ID del cuestionario (inicial o seguimiento) a usar
    - training_plan_id: (Opcional) ID del plan de entrenamiento para sincronizar. 
                        Si no se especifica, usa el último generado.
    - previous_nutrition_plan_id: (Opcional) ID del plan nutricional previo para progresión
    """
    await require_admin(request)
    
    try:
        # Intentar buscar en cuestionarios de nutrición primero
        submission = await db.nutrition_questionnaire_submissions.find_one({"_id": submission_id})
        is_followup = False
        context_data = None
        
        if not submission:
            # Si no está en cuestionarios de nutrición, buscar en follow-ups
            submission = await db.follow_up_submissions.find_one({"_id": submission_id})
            is_followup = True
            
            if not submission:
                raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
        
        if submission["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="El cuestionario no pertenece a este usuario")
        
        # Si es un followup, obtener el cuestionario inicial para contexto base
        if is_followup:
            logger.info(f"📋 Generando desde follow-up, obteniendo cuestionario inicial para contexto")
            initial_submission = await db.nutrition_questionnaire_submissions.find_one(
                {"user_id": user_id},
                sort=[("submitted_at", 1)]
            )
            
            if not initial_submission:
                raise HTTPException(
                    status_code=404,
                    detail="No se encontró cuestionario inicial para contexto"
                )
            
            questionnaire_data = initial_submission["responses"]
            # Serializar datetime fields del followup antes de usar
            submission_serialized = _serialize_datetime_fields(submission)
            context_data = {
                "followup_responses": submission_serialized.get("responses", {}),
                "ai_analysis": submission_serialized.get("ai_analysis", "")
            }
        else:
            # Si regenerate=True, eliminar planes existentes de este mes
            if regenerate and submission.get("plan_generated"):
                now = datetime.now(timezone.utc)
                current_month = now.month
                current_year = now.year
                
                logger.info(f"🔄 Regenerando plan - eliminando plan existente del mes {current_month}/{current_year}")
                
                # Eliminar el plan existente de este mes
                delete_result = await db.nutrition_plans.delete_many({
                    "user_id": user_id,
                    "month": current_month,
                    "year": current_year
                })
                
                logger.info(f"✅ Eliminados {delete_result.deleted_count} planes del mes actual")
                
                # Resetear flag en submission
                await db.nutrition_questionnaire_submissions.update_one(
                    {"_id": submission_id},
                    {"$set": {"plan_generated": False}}
                )
            
            if submission.get("plan_generated") and not regenerate:
                raise HTTPException(status_code=400, detail="Ya existe un plan generado para este cuestionario")
            
            # Obtener datos del cuestionario
            questionnaire_data = submission["responses"]
        
        # Obtener mes y año actual
        now = datetime.now(timezone.utc)
        current_month = now.month
        current_year = now.year
        
        # Generar ID único para este plan
        plan_id = str(int(datetime.now(timezone.utc).timestamp() * 1000000))
        
        logger.info(f"🍎 Admin iniciando generación de plan nutricional E.D.N.360 para usuario {user_id}")
        
        # Obtener plan de entrenamiento para sincronización
        training_plan = None
        if training_plan_id:
            # Usar el plan de entrenamiento especificado
            logger.info(f"📋 Usando plan de entrenamiento específico: {training_plan_id}")
            training_plan = await db.training_plans.find_one({"_id": training_plan_id})
            
            if not training_plan:
                raise HTTPException(status_code=404, detail=f"Plan de entrenamiento {training_plan_id} no encontrado")
            
            if training_plan.get("user_id") != user_id:
                raise HTTPException(status_code=403, detail="El plan de entrenamiento no pertenece a este usuario")
        else:
            # Si no se especificó, usar el último generado
            logger.info(f"📋 Buscando último plan de entrenamiento del usuario")
            training_plan = await db.training_plans.find_one(
                {"user_id": user_id},
                sort=[("generated_at", -1)]
            )
        
        if not training_plan:
            logger.warning(f"⚠️ No se encontró plan de entrenamiento para usuario {user_id}.")
            raise HTTPException(
                status_code=400, 
                detail="Debes generar primero un plan de ENTRENAMIENTO antes de generar el plan de nutrición. La nutrición necesita sincronizarse con el entrenamiento (días A/M/B, pre/post entreno, etc.)"
            )
        else:
            # Extraer datos del bridge (E9) si existen
            training_bridge_data = training_plan.get("edn360_data", {}).get("E9", {})
            if not training_bridge_data:
                # Si no hay E9, crear bridge básico
                training_bridge_data = {
                    "tdee_estimado": questionnaire_data.get("peso", 70) * 30,  # Estimación básica
                    "dias_amb": {},
                    "demanda_calorica_entrenamiento": {}
                }
            logger.info(f"✅ Plan de entrenamiento encontrado ({training_plan['_id']}). Sincronizando con nutrición.")
        
        # Adaptar cuestionario al formato E.D.N.360
        adapted_questionnaire = _adapt_questionnaire_for_edn360(questionnaire_data)
        
        # Obtener plan nutricional previo si se especificó (para progresión)
        previous_nutrition_plan = None
        if previous_nutrition_plan_id:
            logger.info(f"🔍 POST recibe previous_nutrition_plan_id: '{previous_nutrition_plan_id}' (tipo: {type(previous_nutrition_plan_id)})")
            logger.info(f"📋 Buscando plan nutricional previo con _id: '{previous_nutrition_plan_id}'")
            previous_nutrition_plan = await db.nutrition_plans.find_one({"_id": previous_nutrition_plan_id})
            
            if not previous_nutrition_plan:
                # Log extra para debugging
                logger.error(f"❌ Plan con _id '{previous_nutrition_plan_id}' NO encontrado en DB")
                # Intentar buscar todos los planes del usuario para ver qué IDs existen
                all_plans = await db.nutrition_plans.find({"user_id": user_id}).to_list(length=10)
                logger.error(f"📊 Planes existentes para user {user_id}: {[p['_id'] for p in all_plans]}")
                raise HTTPException(status_code=404, detail=f"Plan nutricional previo no encontrado")
            
            if previous_nutrition_plan.get("user_id") != user_id:
                raise HTTPException(status_code=403, detail="El plan nutricional previo no pertenece a este usuario")
        
        # Generar el plan con E.D.N.360 - SIEMPRE agentes N0-N8
        # ⚠️ DESACTIVADO: from edn360.orchestrator import EDN360Orchestrator
        # ⚠️ DESACTIVADO: orchestrator = EDN360Orchestrator()
        
        logger.info("🚀 Generando plan de NUTRICIÓN con agentes N0-N8")
        
        # Nota: El plan previo se pasa a los agentes para progresión
        if previous_nutrition_plan:
            logger.info(f"   📋 Plan previo encontrado: {previous_nutrition_plan['_id']} (usado para progresión)")
        
        result = await orchestrator._execute_nutrition_initial(
            questionnaire_data=adapted_questionnaire,
            training_bridge_data=training_bridge_data,
            previous_plan=previous_nutrition_plan
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error generando plan: {result.get('error', 'Error desconocido')}"
            )
        
        # Obtener datos del usuario para el plan
        user = await db.users.find_one({"_id": user_id})
        user_name = user.get("name", user.get("username", "Cliente")) if user else "Cliente"
        
        # Determinar número de mes (contar planes previos)
        planes_nutri_previos_count = await db.nutrition_plans.count_documents({"user_id": user_id})
        numero_mes_nutri = planes_nutri_previos_count + 1
        
        # Guardar el plan en nutrition_plans con formato E.D.N.360
        nutrition_plan_doc = {
            "_id": plan_id,
            "user_id": user_id,
            "month": current_month,
            "year": current_year,
            "submission_id": submission_id,  # NUEVO: Cuestionario usado
            "training_plan_id": training_plan["_id"] if training_plan else None,  # NUEVO: Plan de entrenamiento referenciado
            "questionnaire_data": questionnaire_data,
            
            # Datos de E.D.N.360
            "edn360_data": result["plan_data"],
            "agent_executions": result.get("executions", []),
            "system_version": "edn360_v1",
            "training_synchronized": training_plan is not None,
            
            # Compatibilidad con formato antiguo
            "plan_inicial": _format_edn360_nutrition_for_display(result["plan_data"]),
            "plan_verificado": _format_edn360_nutrition_as_text(result["plan_data"], user_name, numero_mes_nutri),  # TEXTO PROFESIONAL
            "plan_text": _format_edn360_nutrition_as_text(result["plan_data"], user_name, numero_mes_nutri),  # TEXTO PROFESIONAL para cliente
            
            "generated_at": now,
            "edited": False,
            "pdf_id": None,
            "pdf_filename": None,
            "sent_email": False,
            "sent_whatsapp": False
        }
        
        await db.nutrition_plans.insert_one(nutrition_plan_doc)
        
        # Actualizar la submission para marcarla como procesada
        await db.nutrition_questionnaire_submissions.update_one(
            {"_id": submission_id},
            {
                "$set": {
                    "plan_generated": True,
                    "plan_id": plan_id
                }
            }
        )
        
        logger.info(f"✅ Plan generado exitosamente para usuario {user_id} - {plan_id}")
        
        return {
            "success": True,
            "message": "Plan generado correctamente",
            "plan_id": plan_id,
            "plan": nutrition_plan_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando plan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando plan: {str(e)}"
        )




@api_router.get("/admin/users/{user_id}/nutrition")
async def get_user_nutrition_plans(user_id: str, request: Request):
    """Admin obtiene el historial de planes de nutrición Y respuestas del cuestionario de un usuario"""
    await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener todos los planes ordenados por fecha (más reciente primero)
    plans = await db.nutrition_plans.find(
        {"user_id": user_id}
    ).sort("generated_at", -1).to_list(length=1000)
    
    # Obtener submissions del cuestionario (respuestas sin plan generado)
    submissions = await db.nutrition_questionnaire_submissions.find(
        {"user_id": user_id}
    ).sort("submitted_at", -1).to_list(length=1000)
    
    # Formatear planes para respuesta
    formatted_plans = []
    for plan in plans:
        formatted_plans.append({
            "id": plan["_id"],
            "month": plan["month"],
            "year": plan["year"],
            "plan_verificado": plan["plan_verificado"],
            "plan_inicial": plan["plan_inicial"],
            "questionnaire_data": plan.get("questionnaire_data", {}),
            "generated_at": plan["generated_at"].isoformat() if plan.get("generated_at") else None,
            "edited": plan.get("edited", False),
            "pdf_id": plan.get("pdf_id"),
            "pdf_filename": plan.get("pdf_filename"),
            "sent_email": plan.get("sent_email", False),
            "sent_whatsapp": plan.get("sent_whatsapp", False)
        })
    
    # Formatear submissions
    formatted_submissions = []
    for sub in submissions:
        formatted_submissions.append({
            "id": sub["_id"],
            "submitted_at": sub["submitted_at"].isoformat() if sub.get("submitted_at") else None,
            "plan_generated": sub.get("plan_generated", False),
            "plan_id": sub.get("plan_id"),
            "responses": sub.get("responses", {})
        })
    
    return {
        "plans": formatted_plans,
        "questionnaire_submissions": formatted_submissions  # Nueva respuesta con submissions
    }


@api_router.patch("/admin/users/{user_id}/nutrition/{plan_id}")
async def update_user_nutrition_plan(user_id: str, plan_id: str, updated_plan: dict, request: Request):
    """Admin edita un plan de nutrición específico"""
    await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que el plan existe
    plan = await db.nutrition_plans.find_one({"_id": plan_id, "user_id": user_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan de nutrición no encontrado")
    
    try:
        # Actualizar el plan verificado con la versión editada
        await db.nutrition_plans.update_one(
            {"_id": plan_id},
            {
                "$set": {
                    "plan_verificado": updated_plan.get("plan_content"),
                    "edited": True,
                    "edited_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"Plan de nutrición {plan_id} editado para usuario {user_id}")
        
        return {
            "success": True,
            "message": "Plan de nutrición actualizado correctamente"
        }
        
    except Exception as e:
        logger.error(f"Error actualizando plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando plan: {str(e)}"
        )
        
    except Exception as e:
        logger.error(f"Error actualizando plan de nutrición: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error actualizando plan: {str(e)}"
        )


@api_router.delete("/admin/users/{user_id}/nutrition/{plan_id}")
async def delete_nutrition_plan(user_id: str, plan_id: str, request: Request):
    """Admin elimina completamente un plan de nutrición (hard delete)"""
    await require_admin(request)
    
    try:
        # Verificar que el usuario existe
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar que el plan existe
        plan = await db.nutrition_plans.find_one({"_id": plan_id, "user_id": user_id})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan de nutrición no encontrado")
        
        # Eliminar el PDF asociado si existe
        if plan.get("pdf_id"):
            await db.pdfs.delete_one({"_id": plan["pdf_id"]})
            logger.info(f"PDF eliminado: {plan['pdf_id']}")
        
        # Eliminar el plan de nutrición
        result = await db.nutrition_plans.delete_one({"_id": plan_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="No se pudo eliminar el plan")
        
        # Si este era el plan actual del usuario, limpiar la referencia
        if user.get("nutrition_plan") == plan_id:
            await db.users.update_one(
                {"_id": user_id},
                {"$unset": {"nutrition_plan": ""}}
            )
            logger.info(f"Referencia al plan eliminada del usuario {user_id}")
        
        logger.info(f"✅ Plan de nutrición {plan_id} eliminado completamente por admin")
        
        return {
            "success": True,
            "message": "Plan de nutrición eliminado completamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando plan de nutrición: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error eliminando plan: {str(e)}"
        )


@api_router.post("/admin/users/{user_id}/nutrition-pdf")
async def generate_nutrition_pdf(user_id: str, plan_id: str = None, request: Request = None):
    """Admin genera PDF del plan de nutrición más reciente y lo sube a documentos del usuario"""
    await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Si no se especifica plan_id, obtener el más reciente
    if not plan_id:
        plan = await db.nutrition_plans.find_one(
            {"user_id": user_id},
            sort=[("generated_at", -1)]
        )
    else:
        plan = await db.nutrition_plans.find_one({"_id": plan_id, "user_id": user_id})
    
    if not plan:
        raise HTTPException(status_code=404, detail="Usuario no tiene plan de nutrición")
    
    try:
        # Generar PDF usando markdown2pdf o similar
        import markdown
        from weasyprint import HTML
        import tempfile
        
        # Contenido del plan verificado
        plan_content = plan.get("plan_verificado", "")
        month = plan.get("month")
        year = plan.get("year")
        
        # Convertir markdown a HTML preservando saltos de línea
        html_content = markdown.markdown(plan_content, extensions=['nl2br'])
        
        # Template HTML con estilos
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.4;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 40px 20px;
                }}
                h1, h2, h3 {{
                    color: #2563eb;
                    margin-top: 15px;
                    margin-bottom: 8px;
                }}
                h1 {{
                    border-bottom: 3px solid #2563eb;
                    padding-bottom: 10px;
                }}
                p {{
                    margin: 5px 0;
                }}
                strong {{
                    font-weight: bold;
                    display: inline-block;
                    margin-top: 10px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 15px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: left;
                }}
                th {{
                    background-color: #2563eb;
                    color: white;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .footer {{
                    margin-top: 40px;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Plan de Nutrición Personalizado</h1>
                <p><strong>{user.get('name', user.get('username'))}</strong></p>
                <p>Generado: {datetime.now(timezone.utc).strftime('%d/%m/%Y')}</p>
            </div>
            {html_content}
            <div class="footer">
                <p><strong>Jorge Calcerrada</strong><br>
                Entrenador Personal y Coach de Transformación<br>
                📧 ecjtrainer@gmail.com</p>
            </div>
        </body>
        </html>
        """
        
        # Generate PDF content
        pdf_content = HTML(string=full_html).write_pdf()
        
        # Create standardized PDF document
        month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                       "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        pdf_title = f"Plan de Nutrición - {month_names[month]} {year}"
        pdf_filename = f"nutrition_plan_{user_id}_{month}_{year}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.pdf"
        
        pdf_id = await create_pdf_document(
            user_id=user_id,
            title=pdf_title,
            content=pdf_content,
            pdf_type="nutrition",
            related_id=plan["_id"],
            filename=pdf_filename
        )
        
        # Actualizar el plan en la colección marcando PDF generado
        await db.nutrition_plans.update_one(
            {"_id": plan["_id"]},
            {
                "$set": {
                    "pdf_id": pdf_id,
                    "pdf_filename": pdf_filename
                }
            }
        )
        
        logger.info(f"PDF de nutrición generado para usuario {user_id} - Plan {plan['_id']}")
        
        return {
            "success": True,
            "message": "PDF generado y subido a documentos del usuario",
            "pdf_id": pdf_id,
            "filename": pdf_filename
        }
        
    except Exception as e:
        logger.error(f"Error generando PDF de nutrición: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando PDF: {str(e)}"
        )


@api_router.post("/admin/users/{user_id}/nutrition/send-email")
async def send_nutrition_email(user_id: str, plan_id: str = None, request: Request = None):
    """Admin envía plan de nutrición por email al cliente"""
    await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Si no se especifica plan_id, obtener el más reciente
    if not plan_id:
        plan = await db.nutrition_plans.find_one(
            {"user_id": user_id},
            sort=[("generated_at", -1)]
        )
    else:
        plan = await db.nutrition_plans.find_one({"_id": plan_id, "user_id": user_id})
    
    if not plan:
        raise HTTPException(status_code=404, detail="Usuario no tiene plan de nutrición")
    
    try:
        from email_utils import send_email
        import markdown
        
        # Contenido del plan
        plan_content = plan.get("plan_verificado", "")
        
        # FIX: Verificar que no esté vacío
        if not plan_content or len(plan_content.strip()) < 100:
            # Intentar con plan_text
            plan_content = plan.get("plan_text", "")
            
        if not plan_content or len(plan_content.strip()) < 100:
            raise HTTPException(
                status_code=500, 
                detail="El plan no tiene contenido. Por favor, regenera el plan de nutrición."
            )
        
        month = plan.get("month")
        year = plan.get("year")
        
        # Convertir markdown a HTML
        html_content = markdown.markdown(plan_content, extensions=['nl2br', 'tables'])
        
        # Template HTML para email
        email_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f9f9f9;
                }}
                .container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #10b981;
                    border-bottom: 3px solid #10b981;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #059669;
                    margin-top: 25px;
                }}
                h3 {{
                    color: #047857;
                }}
                pre {{
                    background-color: #f3f4f6;
                    padding: 15px;
                    border-radius: 5px;
                    white-space: pre-wrap;
                    font-family: 'Arial', sans-serif;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #e5e7eb;
                    text-align: center;
                    color: #6b7280;
                    font-size: 14px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div style="text-align: center; margin-bottom: 30px;">
                    <img src="{request.base_url._url}logo-sin-fondo.png" alt="Jorge Calcerrada" style="height: 80px; width: auto;">
                </div>
                <h1>🥗 Tu Plan de Nutrición Personalizado</h1>
                <p>Hola {user.get('name', 'Cliente')},</p>
                <p>Te enviamos tu plan de nutrición personalizado elaborado especialmente para ti.</p>
                <hr>
                <div>{html_content}</div>
                <div class="footer">
                    <p><strong>Jorge Calcerrada - Entrenador Personal</strong></p>
                    <p>Si tienes alguna duda, no dudes en contactarme.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Enviar email
        send_email(
            to_email=user.get('email'),
            subject="🥗 Tu Plan de Nutrición Personalizado",
            html_body=email_html
        )
        
        # Marcar como enviado por email
        await db.nutrition_plans.update_one(
            {"_id": plan["_id"]},
            {"$set": {"sent_email": True}}
        )
        
        logger.info(f"Plan de nutrición enviado por email a {user.get('email')} - Plan {plan['_id']}")
        
        return {
            "success": True,
            "message": "Plan de nutrición enviado por email correctamente",
            "plan_id": plan["_id"]
        }
        
    except Exception as e:
        logger.error(f"Error enviando plan por email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando email: {str(e)}"
        )


@api_router.get("/admin/users/{user_id}/nutrition/whatsapp-link")
async def get_nutrition_whatsapp_link(user_id: str, plan_id: str = None, request: Request = None):
    """Admin obtiene link de WhatsApp con el plan de nutrición"""
    await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Si no se especifica plan_id, obtener el más reciente
    if not plan_id:
        plan = await db.nutrition_plans.find_one(
            {"user_id": user_id},
            sort=[("generated_at", -1)]
        )
    else:
        plan = await db.nutrition_plans.find_one({"_id": plan_id, "user_id": user_id})
    
    if not plan:
        raise HTTPException(status_code=404, detail="Usuario no tiene plan de nutrición")
    
    # Obtener teléfono del usuario
    phone = user.get('phone', '')
    if not phone:
        raise HTTPException(
            status_code=400,
            detail="El usuario no tiene número de teléfono registrado"
        )
    
    try:
        import urllib.parse
        
        # Contenido del plan (limitado para WhatsApp)
        plan_content = plan.get("plan_verificado", "")
        
        # FIX: Asegurar que plan_content es string
        if isinstance(plan_content, dict):
            plan_content = plan_content.get("text", str(plan_content))
        elif not isinstance(plan_content, str):
            plan_content = str(plan_content)
        
        month = plan.get("month")
        year = plan.get("year")
        
        month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                       "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Extraer secciones clave del plan para WhatsApp
        # Buscar sección de macros y menú (más importante)
        key_sections = []
        
        # Buscar sección de calorías y macros
        if "CALORÍAS Y MACRONUTRIENTES" in plan_content:
            start = plan_content.find("CALORÍAS Y MACRONUTRIENTES")
            end = plan_content.find("═══════", start + 100)
            if end > start:
                key_sections.append(plan_content[start:end])
        
        # Buscar tabla semanal
        if "MENÚ SEMANAL" in plan_content:
            start = plan_content.find("MENÚ SEMANAL")
            end = plan_content.find("═══════", start + 500)
            if end > start:
                key_sections.append(plan_content[start:end+500])
        
        # Si no encontramos secciones, usar el inicio del plan
        if not key_sections:
            preview_content = plan_content[:4500]
        else:
            preview_content = "\n\n".join(key_sections)[:4500]
        
        # Crear mensaje para WhatsApp
        message = f"""🥗 *Tu Plan de Nutrición Personalizado - {month_names[month]} {year}*

Hola {user.get('name', 'Cliente')}!

Te envío tu plan de nutrición personalizado:

{preview_content}...

_💡 Plan completo disponible en tu panel o por email._

*Jorge Calcerrada - Entrenador Personal*"""
        
        # Limpiar número de teléfono (solo dígitos)
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Generar link de WhatsApp
        encoded_message = urllib.parse.quote(message)
        whatsapp_link = f"https://wa.me/{clean_phone}?text={encoded_message}"
        
        # Marcar como enviado por WhatsApp
        await db.nutrition_plans.update_one(
            {"_id": plan["_id"]},
            {"$set": {"sent_whatsapp": True}}
        )
        
        logger.info(f"Link de WhatsApp generado para usuario {user_id} - Plan {plan['_id']}")
        
        return {
            "success": True,
            "whatsapp_link": whatsapp_link,
            "phone": phone,
            "plan_id": plan["_id"]
        }
        
    except Exception as e:
        logger.error(f"Error generando link de WhatsApp: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando link: {str(e)}"
        )



# ==================== TRAINING PLANS ENDPOINTS ====================

async def _adapt_followup_for_edn360(followup_data: dict, user_id: str) -> dict:
    """
    Adapta el cuestionario de seguimiento combinándolo con datos iniciales del cliente
    El followup solo tiene peso actualizado, necesitamos sexo y altura del cuestionario inicial
    """
    try:
        # Obtener el cuestionario inicial del usuario para datos base
        initial_questionnaire = await db.nutrition_questionnaire_submissions.find_one(
            {"user_id": user_id},
            sort=[("submitted_at", 1)]  # El más antiguo = inicial
        )
        
        if not initial_questionnaire:
            logger.warning(f"⚠️ No se encontró cuestionario inicial para usuario {user_id}")
            # Intentar obtener del usuario directamente
            user = await db.users.find_one({"_id": user_id})
            initial_data = user if user else {}
        else:
            initial_data = initial_questionnaire.get("responses", {})
        
        # Combinar datos: base del inicial + actualizaciones del followup
        combined_data = initial_data.copy()
        
        # Actualizar peso del seguimiento (el campo crítico que cambia)
        if "peso" in followup_data:
            combined_data["peso"] = followup_data["peso"]
        
        # Mantener otros datos del followup si existen
        for key in ["circunferencia_cintura", "circunferencia_pecho", "grasa_corporal", "masa_muscular"]:
            if key in followup_data:
                combined_data[key] = followup_data[key]
        
        logger.info(f"✅ Follow-up combinado con datos iniciales")
        logger.info(f"   - Peso actualizado: {combined_data.get('peso', 'N/A')} kg")
        logger.info(f"   - Sexo (del inicial): {combined_data.get('sexo', 'N/A')}")
        logger.info(f"   - Altura (del inicial): {combined_data.get('altura_cm', 'N/A')} cm")
        
        # Ahora adaptar con la función normal
        return _adapt_questionnaire_for_edn360(combined_data)
        
    except Exception as e:
        logger.error(f"❌ Error adaptando follow-up: {e}")
        # Fallback: usar solo datos del followup
        return _adapt_questionnaire_for_edn360(followup_data)


def _validate_questionnaire_format(submission: dict) -> tuple[bool, list[str], dict]:
    """
    Valida robustamente el formato del cuestionario antes de procesarlo.
    
    Args:
        submission: Documento de la BD (debe contener '_id', 'user_id', 'responses', etc.)
    
    Returns:
        (is_valid, errors, questionnaire_data)
        
    FORMATO ESPERADO EN MONGODB:
    {
        "_id": "string (timestamp único)",
        "user_id": "string",
        "responses": {
            "nombre_completo": "string",
            "email": "string",
            "fecha_nacimiento": "string (YYYY-MM-DD)",
            "sexo": "string (Hombre/Mujer)",
            "peso": "string (e.g., '75')",
            "altura_cm": "string (e.g., '175')",
            "objetivo_fisico": "string",
            ... (más campos)
        },
        "submitted_at": "datetime",
        "plan_generated": "boolean"
    }
    """
    errors = []
    
    # 1. Validar estructura del submission
    if not isinstance(submission, dict):
        errors.append(f"Submission debe ser un dict, recibido: {type(submission)}")
        return False, errors, {}
    
    if "_id" not in submission:
        errors.append("Campo '_id' ausente en submission")
    
    if "user_id" not in submission:
        errors.append("Campo 'user_id' ausente en submission")
    
    # 2. Validar campo 'responses' - CRÍTICO
    if "responses" not in submission:
        errors.append("❌ CRÍTICO: Campo 'responses' ausente en submission. El cuestionario debe guardarse con estructura: {_id, user_id, responses: {...}, submitted_at, plan_generated}")
        return False, errors, {}
    
    questionnaire_data = submission.get("responses", {})
    
    if not isinstance(questionnaire_data, dict):
        errors.append(f"Campo 'responses' debe ser un dict, recibido: {type(questionnaire_data)}")
        return False, errors, {}
    
    if len(questionnaire_data) == 0:
        errors.append("Campo 'responses' está vacío")
        return False, errors, {}
    
    # 3. Validar campos requeridos MÍNIMOS
    required_fields = {
        "nombre_completo": "Nombre completo del cliente",
        "email": "Email del cliente",
        "fecha_nacimiento": "Fecha de nacimiento (YYYY-MM-DD)",
        "sexo": "Sexo (Hombre/Mujer)",
        "peso": "Peso en kg",
        "altura_cm": "Altura en cm",
        "objetivo_fisico": "Objetivo principal del entrenamiento"
    }
    
    missing_required = []
    empty_required = []
    
    for field, description in required_fields.items():
        if field not in questionnaire_data:
            missing_required.append(f"{field} ({description})")
        elif not questionnaire_data[field]:
            empty_required.append(f"{field} ({description})")
    
    if missing_required:
        errors.append(f"Campos requeridos ausentes: {', '.join(missing_required)}")
    
    if empty_required:
        errors.append(f"Campos requeridos vacíos: {', '.join(empty_required)}")
    
    # 4. Validar formatos específicos
    if "fecha_nacimiento" in questionnaire_data and questionnaire_data["fecha_nacimiento"]:
        try:
            datetime.strptime(str(questionnaire_data["fecha_nacimiento"]), "%Y-%m-%d")
        except ValueError:
            errors.append(f"fecha_nacimiento debe estar en formato YYYY-MM-DD, recibido: {questionnaire_data['fecha_nacimiento']}")
    
    if "sexo" in questionnaire_data and questionnaire_data["sexo"]:
        sexo_normalized = str(questionnaire_data["sexo"]).lower().strip()
        valid_sexo = ["hombre", "mujer", "masculino", "femenino", "male", "female", "m", "f"]
        if sexo_normalized not in valid_sexo:
            errors.append(f"sexo debe ser 'Hombre' o 'Mujer', recibido: '{questionnaire_data['sexo']}'")
    
    # 5. Validar campos numéricos
    numeric_fields = {
        "peso": "Peso",
        "altura_cm": "Altura"
    }
    
    for field, name in numeric_fields.items():
        if field in questionnaire_data and questionnaire_data[field]:
            try:
                value = float(str(questionnaire_data[field]))
                if value <= 0:
                    errors.append(f"{name} debe ser un número positivo, recibido: {questionnaire_data[field]}")
            except (ValueError, TypeError):
                errors.append(f"{name} debe ser un número válido, recibido: '{questionnaire_data[field]}'")
    
    is_valid = len(errors) == 0
    
    if not is_valid:
        logger.error(f"❌ Validación de cuestionario falló:")
        for error in errors:
            logger.error(f"   - {error}")
    
    return is_valid, errors, questionnaire_data


def _adapt_questionnaire_for_edn360(questionnaire_data: dict) -> dict:
    """
    Adapta el formato del cuestionario actual al formato esperado por E.D.N.360
    Soporta tanto NutritionQuestionnaire como DiagnosisQuestionnaire
    """
    try:
        from datetime import datetime
        adapted = {}
        
        # === CAMPOS BÁSICOS - REQUERIDOS por E1 ===
        
        # NOMBRE: Buscar nombre_completo (NutritionQuestionnaire) o nombre (DiagnosisQuestionnaire)
        adapted["nombre"] = questionnaire_data.get("nombre_completo") or questionnaire_data.get("nombre", "Usuario")
        
        # EDAD: Calcular desde fecha_nacimiento o usar edad directa
        if "fecha_nacimiento" in questionnaire_data and questionnaire_data["fecha_nacimiento"]:
            try:
                # Calcular edad desde fecha de nacimiento
                fecha_nac = questionnaire_data["fecha_nacimiento"]
                if isinstance(fecha_nac, str):
                    # Formato esperado: YYYY-MM-DD
                    birth_date = datetime.strptime(fecha_nac, "%Y-%m-%d")
                    today = datetime.now()
                    edad = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                    adapted["edad"] = edad
                else:
                    adapted["edad"] = 30
            except Exception as e:
                logger.warning(f"⚠️ Error calculando edad desde fecha_nacimiento: {e}")
                adapted["edad"] = questionnaire_data.get("edad", 30)
        else:
            # Usar edad directa
            edad_str = questionnaire_data.get("edad", "30")
            try:
                adapted["edad"] = int(edad_str.split()[0]) if isinstance(edad_str, str) else int(edad_str)
            except:
                adapted["edad"] = 30
        
        # SEXO: Normalizar a minúsculas y mapear
        sexo_raw = questionnaire_data.get("sexo", "hombre")
        if isinstance(sexo_raw, str):
            sexo_normalized = sexo_raw.lower().strip()
            # Mapear HOMBRE/MUJER a hombre/mujer
            if sexo_normalized in ["hombre", "masculino", "male", "m"]:
                adapted["sexo"] = "hombre"
            elif sexo_normalized in ["mujer", "femenino", "female", "f"]:
                adapted["sexo"] = "mujer"
            else:
                adapted["sexo"] = sexo_normalized
        else:
            adapted["sexo"] = "hombre"
        
        # PESO: Buscar 'peso' (NutritionQuestionnaire) o 'peso_actual_kg' (otros)
        peso = questionnaire_data.get("peso") or questionnaire_data.get("peso_actual_kg")
        try:
            adapted["peso_actual_kg"] = float(peso) if peso else 70
        except (ValueError, TypeError):
            adapted["peso_actual_kg"] = 70
            logger.warning(f"⚠️ Peso inválido '{peso}', usando default 70kg")
        
        # ALTURA: Buscar 'altura_cm' (presente en ambos cuestionarios)
        altura = questionnaire_data.get("altura_cm")
        try:
            adapted["altura_cm"] = float(altura) if altura else 170
        except (ValueError, TypeError):
            adapted["altura_cm"] = 170
            logger.warning(f"⚠️ Altura inválida '{altura}', usando default 170cm")
        
        # === OBJETIVO ===
        # Buscar en varios campos posibles
        objetivo = (questionnaire_data.get("objetivo_principal") or 
                   questionnaire_data.get("objetivo") or 
                   questionnaire_data.get("objetivos_deseados") or "")
        
        if "adelgazar" in objetivo.lower() or "perder" in objetivo.lower() or "bajar" in objetivo.lower():
            adapted["objetivo_principal"] = "perdida_grasa"
        elif "ganar" in objetivo.lower() or "musculo" in objetivo.lower() or "volumen" in objetivo.lower():
            adapted["objetivo_principal"] = "ganancia_muscular"
        elif "definir" in objetivo.lower() or "recomposicion" in objetivo.lower():
            adapted["objetivo_principal"] = "recomposicion"
        else:
            adapted["objetivo_principal"] = objetivo or "mejora_general"
        
        # === EXPERIENCIA DE ENTRENAMIENTO ===
        # NutritionQuestionnaire tiene campos más detallados
        entrenado_gym = questionnaire_data.get("entrenado_gimnasio", "")
        nivel_deporte = questionnaire_data.get("nivel_deporte", "")
        constante_deporte = questionnaire_data.get("constante_deporte", "")
        tiempo_dedicaba = questionnaire_data.get("tiempo_dedicaba", "")
        entrena = questionnaire_data.get("entrena", "")
        
        # Construir experiencia desde múltiples campos
        experiencia_parts = []
        
        # Priorizar nivel declarado
        if nivel_deporte:
            experiencia_parts.append(f"Nivel: {nivel_deporte}")
        
        if entrenado_gym:
            experiencia_parts.append(f"Gimnasio: {entrenado_gym}")
        
        # CRÍTICO: Si tiene "tiempo_dedicaba" con volumen alto, es avanzado
        if tiempo_dedicaba:
            experiencia_parts.append(f"Dedicación previa: {tiempo_dedicaba}")
            # Detectar señales de nivel avanzado/profesional
            tiempo_lower = tiempo_dedicaba.lower()
            if any(indicator in tiempo_lower for indicator in ["3h", "3 h", "4h", "4 h", "5 días", "6 días", "profesional", "culturista", "competición"]):
                if not any("avanzado" in part.lower() or "profesional" in part.lower() for part in experiencia_parts):
                    experiencia_parts.insert(0, "⚠️ NIVEL REAL: AVANZADO/PROFESIONAL (según dedicación histórica)")
        
        if constante_deporte:
            experiencia_parts.append(f"Constancia: {constante_deporte}")
        
        if entrena:
            experiencia_parts.append(entrena)
        
        if experiencia_parts:
            adapted["experiencia_entrenamiento"] = ". ".join(experiencia_parts)
        else:
            if "no" in entrena.lower() or "nunca" in entrena.lower():
                adapted["experiencia_entrenamiento"] = "principiante absoluto, sin experiencia previa"
            elif "gym" in entrena.lower() or "gimnasio" in entrena.lower():
                adapted["experiencia_entrenamiento"] = "experiencia en gimnasio"
            else:
                adapted["experiencia_entrenamiento"] = "principiante"
        
        # === HISTORIAL DE ENTRENAMIENTO ===
        intentos = questionnaire_data.get("intentos_previos", "")
        constante_deporte = questionnaire_data.get("constante_deporte", "")
        tiempo_dedicaba = questionnaire_data.get("tiempo_dedicaba", "")
        
        historial_parts = []
        if intentos:
            historial_parts.append(f"Intentos previos: {intentos}")
        if constante_deporte:
            historial_parts.append(f"Constancia: {constante_deporte}")
        if tiempo_dedicaba:
            historial_parts.append(f"Tiempo dedicado: {tiempo_dedicaba}")
        
        adapted["historial_entrenamiento"] = ". ".join(historial_parts) if historial_parts else "sin historial previo"
        
        # === LESIONES Y LIMITACIONES ===
        # Recopilar de múltiples fuentes
        lesiones_parts = []
        
        # Dificultades (DiagnosisQuestionnaire)
        dificultades = questionnaire_data.get("dificultades", [])
        if isinstance(dificultades, list):
            lesiones_parts.extend(dificultades)
        elif dificultades:
            lesiones_parts.append(str(dificultades))
        
        dificultades_otro = questionnaire_data.get("dificultades_otro", "")
        if dificultades_otro:
            lesiones_parts.append(dificultades_otro)
        
        # Campos de salud del NutritionQuestionnaire
        problemas_musculares = questionnaire_data.get("problemas_musculares", "")
        hernias = questionnaire_data.get("hernias_protusiones", "")
        artrosis = questionnaire_data.get("artrosis", "")
        
        if problemas_musculares and problemas_musculares.lower() not in ["no", "ninguno"]:
            lesiones_parts.append(f"Problemas musculares: {problemas_musculares}")
        if hernias and hernias.lower() not in ["no", "ninguno"]:
            lesiones_parts.append(f"Hernias/protusiones: {hernias}")
        if artrosis and artrosis.lower() not in ["no", "ninguno"]:
            lesiones_parts.append(f"Artrosis: {artrosis}")
        
        lesiones_str = ", ".join(lesiones_parts) if lesiones_parts else "ninguna"
        adapted["lesiones_previas"] = lesiones_str
        adapted["limitaciones"] = lesiones_str
        
        # === DISPONIBILIDAD ===
        # NutritionQuestionnaire tiene campos específicos
        dias_semana_entrenar = questionnaire_data.get("dias_semana_entrenar", "")
        tiempo_sesion = questionnaire_data.get("tiempo_sesion", "")
        tiempo_semanal = questionnaire_data.get("tiempo_semanal", "")
        
        # Intentar extraer de los campos específicos primero
        import re
        if dias_semana_entrenar:
            try:
                adapted["dias_semana"] = int(dias_semana_entrenar)
            except (ValueError, TypeError):
                adapted["dias_semana"] = 3
        elif tiempo_semanal and ("días" in tiempo_semanal or "dias" in tiempo_semanal):
            dias_match = re.search(r'(\d+)\s*d[íi]as?', tiempo_semanal, re.IGNORECASE)
            adapted["dias_semana"] = int(dias_match.group(1)) if dias_match else 3
        else:
            adapted["dias_semana"] = 3
        
        if tiempo_sesion:
            try:
                # Puede venir como "60" o "60 min" o "60 minutos"
                min_match = re.search(r'(\d+)', str(tiempo_sesion))
                adapted["minutos_por_sesion"] = int(min_match.group(1)) if min_match else 60
            except (ValueError, TypeError):
                adapted["minutos_por_sesion"] = 60
        elif tiempo_semanal and "min" in tiempo_semanal:
            min_match = re.search(r'(\d+)\s*min', tiempo_semanal, re.IGNORECASE)
            adapted["minutos_por_sesion"] = int(min_match.group(1)) if min_match else 60
        else:
            adapted["minutos_por_sesion"] = 60
        
        adapted["tiempo_disponible_semanal"] = f"{adapted['dias_semana']} días/semana, {adapted['minutos_por_sesion']} min/sesión"
        
        # === HORARIO DE ENTRENAMIENTO ===
        horario_entrenar = questionnaire_data.get("entrena_manana_tarde", "")
        if horario_entrenar:
            if "mañana" in horario_entrenar.lower():
                adapted["horario_preferido"] = "mañana"
                adapted["horario_entrenamiento"] = "mañana"  # Para agentes de nutrición
                adapted["hora_entreno"] = "08:00"  # Horario típico mañana
            elif "tarde" in horario_entrenar.lower():
                adapted["horario_preferido"] = "tarde"
                adapted["horario_entrenamiento"] = "tarde"
                adapted["hora_entreno"] = "18:00"  # Horario típico tarde
            elif "noche" in horario_entrenar.lower():
                adapted["horario_preferido"] = "noche"
                adapted["horario_entrenamiento"] = "noche"
                adapted["hora_entreno"] = "20:00"  # Horario típico noche
            else:
                adapted["horario_preferido"] = horario_entrenar
                adapted["horario_entrenamiento"] = horario_entrenar
                adapted["hora_entreno"] = "18:00"  # Default
        else:
            adapted["horario_preferido"] = "tarde"
            adapted["horario_entrenamiento"] = "tarde"
            adapted["hora_entreno"] = "18:00"
        
        # === HORARIOS DE COMIDAS ===
        # Buscar horarios específicos en el cuestionario o usar defaults según horario de entreno
        adapted["horario_desayuno"] = questionnaire_data.get("horario_desayuno", "08:00")
        adapted["horario_comida"] = questionnaire_data.get("horario_comida", "14:00")
        adapted["horario_cena"] = questionnaire_data.get("horario_cena", "21:00")
        
        # Número de comidas al día
        num_comidas = questionnaire_data.get("comidas_dia", "") or questionnaire_data.get("numero_comidas", "")
        try:
            if isinstance(num_comidas, str):
                # Extraer número de texto como "4 comidas" o "4"
                import re
                match = re.search(r'(\d+)', num_comidas)
                adapted["numero_comidas"] = int(match.group(1)) if match else 4
            else:
                adapted["numero_comidas"] = int(num_comidas) if num_comidas else 4
        except (ValueError, TypeError):
            adapted["numero_comidas"] = 4
        
        # === EQUIPO DISPONIBLE ===
        gimnasio_campo = questionnaire_data.get("gimnasio", "")
        material_casa_campo = questionnaire_data.get("material_casa", "")
        
        if gimnasio_campo and gimnasio_campo.lower() not in ["no", "ninguno"]:
            adapted["equipo_disponible"] = f"Gym: {gimnasio_campo}"
        elif material_casa_campo and material_casa_campo.lower() not in ["no", "ninguno"]:
            adapted["equipo_disponible"] = f"Casa con equipo: {material_casa_campo}"
        elif "gym" in entrena.lower() or "gimnasio" in entrena.lower():
            adapted["equipo_disponible"] = "gym completo"
        elif "casa" in entrena.lower():
            adapted["equipo_disponible"] = "casa con equipo básico"
        else:
            adapted["equipo_disponible"] = "gym completo"
        
        # === NUTRICIÓN ACTUAL ===
        alimentacion = questionnaire_data.get("alimentacion", "")
        comidas_dia = questionnaire_data.get("comidas_dia", "")
        
        nutricion_parts = []
        if alimentacion:
            nutricion_parts.append(alimentacion)
        if comidas_dia:
            nutricion_parts.append(f"Comidas al día: {comidas_dia}")
        
        adapted["nutricion_actual"] = ". ".join(nutricion_parts) if nutricion_parts else "sin seguimiento específico"
        
        # === CONDICIONES DE SALUD ===
        # Recopilar condiciones del NutritionQuestionnaire
        condiciones = []
        
        salud_info = questionnaire_data.get("salud_info", "")
        if salud_info:
            condiciones.append(salud_info)
        
        # Campos específicos de salud
        medicamentos = questionnaire_data.get("medicamentos", "")
        enfermedad_cronica = questionnaire_data.get("enfermedad_cronica", "")
        hipertension = questionnaire_data.get("hipertension", "")
        diabetes = questionnaire_data.get("diabetes", "")
        
        if medicamentos and medicamentos.lower() not in ["no", "ninguno"]:
            condiciones.append(f"Medicamentos: {medicamentos}")
        if enfermedad_cronica and enfermedad_cronica.lower() not in ["no", "ninguno"]:
            condiciones.append(f"Enfermedad crónica: {enfermedad_cronica}")
        if hipertension and hipertension.lower() == "sí":
            condiciones.append("Hipertensión")
        if diabetes and diabetes.lower() == "sí":
            condiciones.append("Diabetes")
        
        adapted["condiciones_salud"] = ", ".join(condiciones) if condiciones else "sin condiciones especiales"
        
        # === MOTIVACIÓN ===
        por_que_ahora = questionnaire_data.get("por_que_ahora", "")
        objetivo_entrenamiento = questionnaire_data.get("objetivo_entrenamiento", "")
        
        motivacion_parts = []
        if por_que_ahora:
            motivacion_parts.append(por_que_ahora)
        if objetivo_entrenamiento:
            motivacion_parts.append(objetivo_entrenamiento)
        
        adapted["motivacion"] = ". ".join(motivacion_parts) if motivacion_parts else "mejorar salud y físico"
        adapted["nivel_compromiso"] = questionnaire_data.get("dispuesto_invertir", "") or questionnaire_data.get("nivel_compromiso", "medio")
        
        # === DATOS ADICIONALES ===
        # Intentar extraer de campos específicos
        horas_sueno = questionnaire_data.get("horas_sueno", "")
        estres = questionnaire_data.get("estres_profesion", "")
        
        try:
            adapted["sueno_promedio_h"] = int(horas_sueno) if horas_sueno else 7
        except (ValueError, TypeError):
            adapted["sueno_promedio_h"] = 7
        
        if estres:
            if "alto" in estres.lower() or "mucho" in estres.lower():
                adapted["estres_nivel"] = "alto"
            elif "bajo" in estres.lower() or "poco" in estres.lower():
                adapted["estres_nivel"] = "bajo"
            else:
                adapted["estres_nivel"] = "medio"
        else:
            adapted["estres_nivel"] = "medio"
        
        # Copiar todos los campos originales también
        adapted["_original_questionnaire"] = questionnaire_data
        
        # === LOGGING DETALLADO ===
        logger.info(f"✅ Cuestionario adaptado para E.D.N.360")
        logger.info(f"   📋 CAMPOS CRÍTICOS (requeridos por E1):")
        logger.info(f"      - nombre: {adapted['nombre']}")
        logger.info(f"      - edad: {adapted['edad']}")
        logger.info(f"      - sexo: {adapted['sexo']}")
        logger.info(f"      - peso_actual_kg: {adapted['peso_actual_kg']}")
        logger.info(f"      - altura_cm: {adapted['altura_cm']}")
        logger.info(f"   🎯 Objetivo: {adapted['objetivo_principal']}")
        logger.info(f"   📅 Disponibilidad: {adapted['dias_semana']} días x {adapted['minutos_por_sesion']} min")
        logger.info(f"   ⏰ Horario entreno: {adapted['horario_entrenamiento']} ({adapted['hora_entreno']})")
        logger.info(f"   🍽️ Comidas/día: {adapted['numero_comidas']}")
        logger.info(f"   🏋️ Experiencia: {adapted['experiencia_entrenamiento'][:50]}...")
        logger.info(f"   🏥 Lesiones: {adapted['lesiones_previas'][:50]}...")
        
        return adapted
        
    except Exception as e:
        logger.error(f"❌ Error adaptando cuestionario: {e}")
        logger.error(f"   Datos recibidos: {list(questionnaire_data.keys())}")
        # Devolver datos mínimos para que no falle
        return {
            "nombre": questionnaire_data.get("nombre", "Usuario"),
            "edad": 30,
            "sexo": "hombre",
            "peso_actual_kg": 70,
            "altura_cm": 170,
            "objetivo_principal": "mejora_general",
            "experiencia_entrenamiento": "principiante",
            "lesiones_previas": "ninguna",
            "tiempo_disponible_semanal": "3 días, 60 min",
            "dias_semana": 3,
            "minutos_por_sesion": 60,
            "equipo_disponible": "gym completo",
            "_original_questionnaire": questionnaire_data
        }

def _format_edn360_nutrition_as_text(edn360_data: dict, user_name: str = "Cliente", numero_mes: int = None) -> str:
    """
    Convierte el plan E.D.N.360 de nutrición en texto profesional para enviar al cliente
    """
    try:
        # Extraer datos de los agentes N0-N8
        n1_metabolic = edn360_data.get("N1", {})
        n2_energy = edn360_data.get("N2", {})
        n4_calendar = edn360_data.get("N4", {})
        n5_timing = edn360_data.get("N5", {})
        n6_menus = edn360_data.get("N6", {})
        n7_adherence = edn360_data.get("N7", {})
        
        # Generar el texto del plan
        mes_texto = f" - MES {numero_mes}" if numero_mes else ""
        
        plan_text = f"""
PLAN DE NUTRICIÓN PERSONALIZADO{mes_texto}
SISTEMA E.D.N.360

CLIENTE: {user_name}
DURACIÓN: 4 semanas (sincronizado con entrenamiento)
OBJETIVO: Plan nutricional adaptado a tu programa de entrenamiento


TU PERFIL METABÓLICO

• Metabolismo Basal (BMR): {n1_metabolic.get('bmr_estimado', 'N/A')} kcal
• Gasto Total Diario (TDEE): {n1_metabolic.get('tdee_estimado', 'N/A')} kcal
• Perfil Metabólico: {n1_metabolic.get('perfil_metabolico', 'N/A').replace('_', ' ').title()}
• Nivel de Actividad: {n1_metabolic.get('nivel_actividad', 'N/A').replace('_', ' ').title()}


CALORÍAS Y MACRONUTRIENTES (CICLADO CALÓRICO)

"""
        
        # Nuevo formato: mostrar macros por tipo de día
        tdee = n2_energy.get("tdee", "N/A")
        deficit_objetivo = n2_energy.get("deficit_objetivo_pct", 0)
        estrategia = n2_energy.get("estrategia", "")
        
        plan_text += f"""
TU GASTO ENERGÉTICO:
• TDEE (Gasto Total Diario): {tdee} kcal
• Déficit semanal promedio: {n2_energy.get('deficit_semanal_promedio', deficit_objetivo)}%
• Estrategia: {estrategia.replace('_', ' ').title()}

CONCEPTO DE CICLADO CALÓRICO:
Distribuimos las calorías según tu actividad diaria:
- Días de entreno: MÁS calorías y carbohidratos (mejor rendimiento)
- Días de descanso: MENOS calorías (donde aplicamos el déficit principal)

Resultado: Déficit semanal promedio alineado con tu objetivo

"""
        
        # Mostrar macros por tipo de día
        macros_a = n2_energy.get("macros_dia_A", {})
        macros_m = n2_energy.get("macros_dia_M", {})
        macros_b = n2_energy.get("macros_dia_B", {})
        
        if macros_a:
            plan_text += f"""
DÍA A (ENTRENO INTENSO) 🔥
• Calorías: {macros_a.get('kcal_objetivo', 'N/A')} kcal (déficit {macros_a.get('deficit_pct', 0)}%)
• Proteínas: {macros_a.get('proteinas_g', 'N/A')}g ({macros_a.get('proteinas_gkg', 'N/A')}g/kg)
• Carbohidratos: {macros_a.get('carbohidratos_g', 'N/A')}g (ALTO - para rendimiento)
• Grasas: {macros_a.get('grasas_g', 'N/A')}g
"""
        
        # Solo mostrar Día M si existe en el plan
        tipos_dia_generados = n2_energy.get("tipos_dia_generados", [])
        if macros_m and "M" in tipos_dia_generados:
            plan_text += f"""
DÍA M (ENTRENO MODERADO - Cardio/Movilidad) ⚖️
• Calorías: {macros_m.get('kcal_objetivo', 'N/A')} kcal (déficit {macros_m.get('deficit_pct', 0)}%)
• Proteínas: {macros_m.get('proteinas_g', 'N/A')}g ({macros_m.get('proteinas_gkg', 'N/A')}g/kg)
• Carbohidratos: {macros_m.get('carbohidratos_g', 'N/A')}g (MEDIO)
• Grasas: {macros_m.get('grasas_g', 'N/A')}g

Nota: Este plan incluye días de cardio/movilidad además del entrenamiento de fuerza.
"""
        
        if macros_b:
            plan_text += f"""
DÍA B (DESCANSO) 🌙
• Calorías: {macros_b.get('kcal_objetivo', 'N/A')} kcal (déficit {macros_b.get('deficit_pct', 0)}%)
• Proteínas: {macros_b.get('proteinas_g', 'N/A')}g ({macros_b.get('proteinas_gkg', 'N/A')}g/kg)
• Carbohidratos: {macros_b.get('carbohidratos_g', 'N/A')}g (BAJO - déficit principal)
• Grasas: {macros_b.get('grasas_g', 'N/A')}g
"""
        
        # Añadir calendario semanal si existe (formato nuevo)
        calendario_semanal = n4_calendar.get("calendario_semanal", {})
        descripcion_dias = n4_calendar.get("descripcion_dias", {})
        dias_entreno_semana = n4_calendar.get("dias_entrenamiento_semana", 0)
        
        if calendario_semanal:
            plan_text += """

─────────────────────────────────────────────────────────────────────────

CALENDARIO NUTRICIONAL SEMANAL (Sincronizado con tu entrenamiento)

Este plan se ajusta a tus días de entrenamiento:
• Día A (Alto): Días de entrenamiento INTENSO → Más calorías y carbohidratos
• Día M (Medio): Días de entrenamiento MODERADO → Calorías moderadas
• Día B (Bajo/Descanso): Días SIN entrenamiento → Menos calorías, sin pre/post entreno

"""
            plan_text += f"Frecuencia: Entrenas {dias_entreno_semana} días por semana\n\n"
            plan_text += "TU SEMANA:\n"
            
            dias_nombres = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            for i in range(1, 8):
                dia_key = f"dia_{i}"
                tipo = calendario_semanal.get(dia_key, "B")
                descripcion = descripcion_dias.get(dia_key, "")
                emoji = "🔥" if tipo == "A" else ("🌙" if tipo == "B" else "⚖️")
                dia_nombre = dias_nombres[i-1] if i <= 7 else f"Día {i}"
                
                plan_text += f"   {dia_nombre}: {emoji} Tipo {tipo}"
                if descripcion:
                    plan_text += f" - {descripcion}"
                plan_text += "\n"
        
        # Fallback para formato antiguo
        elif n4_calendar.get("calendario"):
            calendario = n4_calendar.get("calendario", [])
            plan_text += """

─────────────────────────────────────────────────────────────────────────

CALENDARIO NUTRICIONAL (Días Altos/Medios/Bajos)

PRIMERA SEMANA:
"""
            for i, dia in enumerate(calendario[:7], 1):
                tipo = dia.get('tipo', 'M')
                emoji = "🔥" if tipo == "A" else ("🌙" if tipo == "B" else "⚖️")
                plan_text += f"   Día {i}: {emoji} Tipo {tipo} - {dia.get('kcal', 'N/A')} kcal\n"
        
        # ELIMINADO: Sección "DISTRIBUCIÓN DE COMIDAS POR TIPO DE DÍA"
        # Usuario solicitó eliminar el detalle verbose de DÍAS A/M/B
        # Esta información ahora solo aparecerá en formato limpio en el menú semanal
        
        # Añadir menú semanal en formato limpio
        menu_semanal = n6_menus.get("menu_semanal", {})
        if menu_semanal:
            plan_text += """

─────────────────────────────────────────────────────────────────────────

DETALLE COMPLETO POR DÍA:

"""
            dias_nombres = ["LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO", "DOMINGO"]
            dias_keys = ["dia_1", "dia_2", "dia_3", "dia_4", "dia_5", "dia_6", "dia_7"]
            
            for dia_key, dia_nombre in zip(dias_keys, dias_nombres):
                dia_data = menu_semanal.get(dia_key, {})
                if dia_data:
                    tipo_dia = dia_data.get("tipo_dia", "M")
                    emoji = "🔥" if tipo_dia == "A" else ("🌙" if tipo_dia == "B" else "⚖️")
                    
                    plan_text += f"\n{emoji} {dia_nombre} - Día Tipo {tipo_dia}\n"
                    plan_text += "─" * 70 + "\n\n"
                    
                    comidas = dia_data.get("comidas", [])
                    for comida in comidas:
                        nombre_comida = comida.get("nombre", "Comida")
                        hora = comida.get("hora", "")
                        alimentos = comida.get("alimentos", [])
                        macros = comida.get("macros", {})
                        timing_nota = comida.get("timing_nota", "")
                        
                        plan_text += f"{nombre_comida.upper()} ({hora})\n"
                        
                        if timing_nota:
                            plan_text += f"Timing: {timing_nota}\n"
                        
                        if alimentos:
                            for alimento in alimentos:
                                if isinstance(alimento, dict):
                                    nombre_ali = alimento.get("nombre", "")
                                    cantidad = alimento.get("cantidad", "")
                                    plan_text += f"• {cantidad} {nombre_ali}\n"
                                elif isinstance(alimento, str):
                                    plan_text += f"• {alimento}\n"
                        
                        if macros:
                            p = macros.get("proteinas", 0)
                            c = macros.get("carbohidratos", 0)
                            g = macros.get("grasas", 0)
                            plan_text += f"Macros: {p}g proteína | {c}g carbos | {g}g grasas\n"
                        
                        plan_text += "\n"
        
        # Si no hay menú semanal, mostrar menús por tipo de día (formato antiguo)
        elif n6_menus.get("menus"):
            menus = n6_menus.get("menus", {})
            plan_text += """

─────────────────────────────────────────────────────────────────────────

EJEMPLOS DE MENÚS POR TIPO DE DÍA

"""
            for tipo, menu_list in menus.items():
                if menu_list and len(menu_list) > 0:
                    emoji = "🔥" if tipo == "A" else ("🌙" if tipo == "B" else "⚖️")
                    plan_text += f"\n{emoji} DÍAS TIPO {tipo}:\n\n"
                    for item in menu_list[:5]:  # Primeros 5 ejemplos
                        comida_nombre = item.get('comida', 'Comida')
                        alimentos = item.get('alimentos', [])
                        plan_text += f"{comida_nombre}:\n"
                        for alimento in alimentos:
                            if isinstance(alimento, dict):
                                nombre = alimento.get("nombre", "")
                                cantidad = alimento.get("cantidad", "")
                                plan_text += f"  • {cantidad} {nombre}\n"
                            else:
                                plan_text += f"  • {alimento}\n"
                        plan_text += "\n"
        
        # Añadir equivalencias/swaps si existen
        equivalencias = n6_menus.get("equivalencias", {})
        if equivalencias:
            plan_text += """

─────────────────────────────────────────────────────────────────────────

EQUIVALENCIAS DE ALIMENTOS (Opciones de reemplazo)

"""
            for categoria, swaps in equivalencias.items():
                cat_nombre = categoria.replace("_", " ").title()
                plan_text += f"\n{cat_nombre}:\n"
                if isinstance(swaps, dict):
                    for alimento_orig, alternativas in swaps.items():
                        alimento_nombre = alimento_orig.replace("_", " ").title()
                        if isinstance(alternativas, list):
                            alts_str = ", ".join(alternativas)
                            plan_text += f"• {alimento_nombre} → {alts_str}\n"
                        else:
                            plan_text += f"• {alimento_nombre} → {alternativas}\n"
        
        # Añadir protocolos de adherencia completos
        plan_text += """

─────────────────────────────────────────────────────────────────────────

PROTOCOLO DE ADHERENCIA Y SOSTENIBILIDAD

"""
        
        # Regla 80/20
        regla_80_20 = n7_adherence.get("regla_80_20", {})
        if regla_80_20:
            plan_text += "\nREGLA 80/20:\n"
            concepto = regla_80_20.get("concepto", "")
            if concepto:
                plan_text += f"{concepto}\n\n"
            
            aplicacion = regla_80_20.get("aplicacion_practica", [])
            if aplicacion:
                plan_text += "Aplicación Práctica:\n"
                for punto in aplicacion:
                    plan_text += f"• {punto}\n"
        
        # Comidas libres
        comidas_libres = n7_adherence.get("comidas_libres", {})
        if comidas_libres:
            plan_text += "\n\nCOMIDAS LIBRES:\n"
            freq = comidas_libres.get("frecuencia", "")
            cuando = comidas_libres.get("cuando", "")
            if freq:
                plan_text += f"Frecuencia: {freq}\n"
            if cuando:
                plan_text += f"Cuándo: {cuando}\n"
            
            reglas = comidas_libres.get("reglas", [])
            if reglas:
                plan_text += "\nReglas:\n"
                for regla in reglas:
                    plan_text += f"• {regla}\n"
        
        # Emergencias
        emergencias = n7_adherence.get("emergencias", {})
        if emergencias:
            plan_text += "\n\nPROTOCOLOS DE EMERGENCIA:\n"
            
            for situacion_key, situacion_data in emergencias.items():
                if isinstance(situacion_data, dict):
                    situacion_nombre = situacion_data.get("situacion", situacion_key.replace("_", " ").title())
                    plan_text += f"\n{situacion_nombre}:\n"
                    
                    accion = situacion_data.get("accion", situacion_data.get("estrategia", []))
                    if isinstance(accion, list):
                        for paso in accion:
                            plan_text += f"✓ {paso}\n"
                    elif isinstance(accion, str):
                        plan_text += f"✓ {accion}\n"
        
        # Meal prep
        meal_prep = n7_adherence.get("meal_prep_guia", {})
        if meal_prep:
            plan_text += "\n\nGUÍA DE MEAL PREP:\n"
            
            cuando = meal_prep.get("cuando", "")
            if cuando:
                plan_text += f"Cuándo: {cuando}\n\n"
            
            que_cocinar = meal_prep.get("que_cocinar", [])
            if que_cocinar:
                plan_text += "Qué cocinar:\n"
                for item in que_cocinar:
                    plan_text += f"• {item}\n"
            
            tips = meal_prep.get("tips", [])
            if tips:
                plan_text += "\nTips:\n"
                for tip in tips:
                    plan_text += f"• {tip}\n"
        
        # Recomendaciones finales
        recomendaciones_finales = n7_adherence.get("recomendaciones_finales", [])
        if recomendaciones_finales:
            plan_text += "\n\nRECOMENDACIONES FINALES:\n"
            for rec in recomendaciones_finales:
                plan_text += f"• {rec}\n"
        
        # Instrucciones finales
        # Generar lista de compra automática del menú semanal
        if menu_semanal:
            plan_text += """

─────────────────────────────────────────────────────────────────────────

LISTA DE LA COMPRA SEMANAL

"""
            # Recopilar todos los alimentos de la semana
            alimentos_totales = {}  # {nombre_alimento: cantidad_total}
            
            for dia_key in ["dia_1", "dia_2", "dia_3", "dia_4", "dia_5", "dia_6", "dia_7"]:
                dia_data = menu_semanal.get(dia_key, {})
                for comida in dia_data.get("comidas", []):
                    for alimento in comida.get("alimentos", []):
                        if isinstance(alimento, dict):
                            nombre = alimento.get("nombre", "").lower().strip()
                            cantidad_str = alimento.get("cantidad", "0")
                            
                            # Extraer número de la cantidad
                            import re
                            match = re.search(r'(\d+(?:\.\d+)?)', str(cantidad_str))
                            if match and nombre:
                                cantidad = float(match.group(1))
                                unidad = cantidad_str.replace(match.group(1), "").strip()
                                
                                # Agrupar por nombre de alimento
                                clave = nombre
                                if clave not in alimentos_totales:
                                    alimentos_totales[clave] = {"cantidad": 0, "unidad": unidad}
                                alimentos_totales[clave]["cantidad"] += cantidad
            
            # Categorizar alimentos
            categorias = {
                "Proteínas": ["pollo", "pavo", "ternera", "cerdo", "pescado", "atún", "salmón", "merluza", 
                             "lenguado", "bacalao", "tilapia", "huevo", "clara", "batido de proteínas", 
                             "proteína", "chuleta", "solomillo", "pechuga", "cordero", "gambas"],
                "Lácteos": ["yogur", "leche", "queso", "requesón", "skyr"],
                "Carbohidratos": ["arroz", "pasta", "quinoa", "avena", "pan", "tostada", "couscous", "cuscús", 
                                 "patata", "batata", "boniato"],
                "Frutas": ["plátano", "manzana", "fresas", "arándanos", "kiwi", "uvas", "melón", "naranja",
                          "fruta"],
                "Verduras": ["brócoli", "espinacas", "lechuga", "tomate", "ensalada", "verduras", "zanahoria",
                            "calabacín", "berenjena", "judías", "espárragos", "champiñones", "alcachofa", "guisantes"],
                "Grasas Saludables": ["aceite", "aguacate", "nueces", "almendras", "semillas"],
                "Otros": []
            }
            
            # Organizar alimentos por categoría
            alimentos_por_categoria = {cat: [] for cat in categorias.keys()}
            
            for nombre_alimento, datos in sorted(alimentos_totales.items()):
                categorizado = False
                for categoria, palabras_clave in categorias.items():
                    if any(palabra in nombre_alimento for palabra in palabras_clave):
                        cantidad = datos["cantidad"]
                        unidad = datos["unidad"]
                        alimentos_por_categoria[categoria].append({
                            "nombre": nombre_alimento.title(),
                            "cantidad": cantidad,
                            "unidad": unidad
                        })
                        categorizado = True
                        break
                
                if not categorizado:
                    cantidad = datos["cantidad"]
                    unidad = datos["unidad"]
                    alimentos_por_categoria["Otros"].append({
                        "nombre": nombre_alimento.title(),
                        "cantidad": cantidad,
                        "unidad": unidad
                    })
            
            # Imprimir lista organizada
            for categoria in ["Proteínas", "Lácteos", "Carbohidratos", "Frutas", "Verduras", "Grasas Saludables", "Otros"]:
                items = alimentos_por_categoria[categoria]
                if items:
                    plan_text += f"\n{categoria.upper()}:\n"
                    for item in items:
                        cantidad_fmt = f"{item['cantidad']:.0f}" if item['cantidad'] == int(item['cantidad']) else f"{item['cantidad']:.1f}"
                        plan_text += f"☑ {item['nombre']}: {cantidad_fmt}{item['unidad']}\n"
            
            plan_text += """

CONSEJOS PARA LA COMPRA:
• Compra proteínas en paquetes grandes para ahorrar
• Congela lo que no uses en 2-3 días
• Lava y corta verduras el día de compra (meal prep)
• Opta por congelados si es más económico (brócoli, fresas, etc.)
"""
        
        plan_text += """

─────────────────────────────────────────────────────────────────────────

INSTRUCCIONES IMPORTANTES

HIDRATACIÓN:
• Mínimo 2-3 litros de agua al día
• Aumentar en días de entrenamiento

TIMING:
• Pre-entreno: 1.5-2 horas antes
• Post-entreno: Dentro de 30-60 minutos

FLEXIBILIDAD:
• 80% del tiempo sigue el plan
• 20% permite flexibilidad (1-2 comidas libres/semana)

AJUSTES:
• Si tienes hambre excesiva → Añade +100-200 kcal
• Si no pierdes peso en 2 semanas → Reduce -100-200 kcal
• Consulta siempre con tu nutricionista antes de cambios mayores

SEÑALES DE ALERTA:
• Fatiga extrema → Puede necesitar más carbohidratos
• Pérdida de fuerza → Revisa proteína y calorías totales
• Hambre constante → Plan demasiado restrictivo

─────────────────────────────────────────────────────────────────────────

Dudas o consultas: Contacta a tu nutricionista

¡Éxito en tu plan nutricional!
"""
        
        return plan_text
        
    except Exception as e:
        logger.error(f"Error formateando plan E.D.N.360 nutrición como texto: {e}")
        return "Error generando el plan. Contacta a tu nutricionista."


def _format_edn360_nutrition_for_display(edn360_data: dict) -> dict:
    """
    Convierte el output de nutrición E.D.N.360 al formato que espera el frontend actual
    """
    try:
        # Extraer información clave de los agentes de nutrición
        n1_metabolic = edn360_data.get("N1", {})
        n2_energy = edn360_data.get("N2", {})
        n3_template = edn360_data.get("N3", {})
        n4_amb = edn360_data.get("N4", {})
        n5_timing = edn360_data.get("N5", {})
        n6_menus = edn360_data.get("N6", {})
        
        # Formatear para el frontend
        formatted_plan = {
            "objetivo_calorico": n2_energy.get("kcal_objetivo", 0),
            "tdee": n1_metabolic.get("tdee", 0),
            "macros": n2_energy.get("macros_gkg", {}),
            "plantilla": n3_template.get("plantilla_asignada", ""),
            "calendario_amb": n4_amb.get("calendario_mensual", []),
            "comidas": n5_timing.get("horarios_comidas", []),
            "menus_semanales": n6_menus.get("menus_semanales", {}),
            "system": "edn360",
            "agents_executed": list(edn360_data.keys())
        }
        
        return formatted_plan
    except Exception as e:
        logger.error(f"Error formateando plan nutricional E.D.N.360: {e}")
        return edn360_data

def _format_edn360_plan_as_text(edn360_data: dict, user_name: str = "Cliente", numero_mes: int = None) -> str:
    """
    Convierte el plan E.D.N.360 en texto profesional y legible para enviar al cliente
    """
    try:
        # Extraer datos del plan
        e4_program = edn360_data.get("E4", {})
        e5_sessions = edn360_data.get("E5", {})
        
        mesociclo = e4_program.get("mesociclo", {})
        semanas = e4_program.get("semanas", [])
        sesiones = e5_sessions.get("sesiones_detalladas", [])
        volumen = e4_program.get("volumen_por_grupo", {})
        
        # Generar el texto del plan
        mes_texto = f" - MES {numero_mes}" if numero_mes else ""
        plan_text = f"""
PLAN DE ENTRENAMIENTO PERSONALIZADO{mes_texto}
SISTEMA E.D.N.360

CLIENTE: {user_name}
DURACIÓN: {mesociclo.get('duracion_semanas', 4)} semanas
OBJETIVO: {mesociclo.get('objetivo', 'Mejora general').replace('_', ' ').title()}
ESTRATEGIA: {mesociclo.get('estrategia', 'Progresiva').title()}
SPLIT: {mesociclo.get('split', 'Full-Body').upper()}
FRECUENCIA: {mesociclo.get('frecuencia_semanal', 3)} días por semana


ESTRUCTURA DEL MESOCICLO

"""
        
        # Añadir información de cada semana
        for semana in semanas:
            plan_text += f"""
SEMANA {semana.get('numero', 1)} - {semana.get('fase', 'Entrenamiento').upper()}

Objetivo: {semana.get('notas', 'Progresión gradual')}
Volumen: {semana.get('volumen_pct', 100)}% del volumen base
Intensidad: {semana.get('intensidad', 'media').replace('_', ' ').title()}
RIR objetivo: {semana.get('rir_objetivo', 3)} repeticiones en reserva
Tiempo estimado por sesión: ~{semana.get('kpis', {}).get('tiempo_total_min', 60) // mesociclo.get('frecuencia_semanal', 3)} minutos

"""
        
        # Añadir sesiones detalladas
        plan_text += """
─────────────────────────────────────────────────────────────────────────

SESIONES DE ENTRENAMIENTO DETALLADAS

"""
        
        if sesiones:
            for sesion in sesiones:
                plan_text += f"""
DÍA {sesion.get('dia', 1)} - {sesion.get('nombre', 'Sesión').upper()}
─────────────────────────────────────────────────────────────────────────

Duración estimada: {sesion.get('duracion_min', 50)} minutos

EJERCICIOS:
"""
                
                for idx, ejercicio in enumerate(sesion.get('ejercicios', []), 1):
                    plan_text += f"""
{idx}. {ejercicio.get('nombre', 'Ejercicio').upper()}
• Series: {ejercicio.get('series', 3)}
• Repeticiones: {ejercicio.get('reps', '10-12')}
• RIR (reserva): {ejercicio.get('rir', '3')} reps antes del fallo
• Descanso: {ejercicio.get('descanso', 90)} segundos
"""
        else:
            plan_text += "\nNo se generaron sesiones detalladas. Contacta a tu entrenador.\n"
        
        # Añadir volumen por grupo muscular
        plan_text += """

─────────────────────────────────────────────────────────────────────────

VOLUMEN DE ENTRENAMIENTO POR GRUPO MUSCULAR (Series/Semana)

"""
        
        for grupo, info in volumen.items():
            plan_text += f"• {grupo.replace('_', ' ').title()}: {info.get('series_semana', 0)} series/semana\n"
        
        # Añadir instrucciones finales
        plan_text += """

─────────────────────────────────────────────────────────────────────────

INSTRUCCIONES IMPORTANTES

PROGRESIÓN:
- Aumenta el peso cuando puedas completar todas las series en el rango 
  alto de repeticiones con el RIR objetivo
- Prioriza SIEMPRE la técnica correcta sobre el peso

RIR (Reps In Reserve):
- RIR 5 = Podrías hacer 5 repeticiones más
- RIR 3 = Podrías hacer 3 repeticiones más
- RIR 1 = Podrías hacer solo 1 repetición más

DESCANSOS:
- Respeta los tiempos de descanso indicados
- En ejercicios pesados (multiarticulares) puede necesitar hasta 3 min

RECUPERACIÓN:
- Duerme al menos 7-8 horas diarias
- Hidrátate adecuadamente (2-3 litros/día)
- Alimentación alineada con tu plan nutricional

SEÑALES DE ALERTA:
- Dolor articular persistente → PARA y consulta
- Fatiga excesiva → Reduce volumen/intensidad
- Falta de progreso 2+ semanas → Evaluar con entrenador

─────────────────────────────────────────────────────────────────────────

Dudas o consultas: Contacta a tu entrenador

¡Éxito en tu entrenamiento!
"""
        
        return plan_text
        
    except Exception as e:
        logger.error(f"Error formateando plan E.D.N.360 como texto: {e}")
        return "Error generando el plan. Contacta a tu entrenador."


async def _integrate_template_blocks(
    plan_data: dict,
    user_data: dict,
    week_number: int = 1,
    session_number_start: int = 1
) -> dict:
    """
    Integra los bloques de plantillas (A, C, D) con el Bloque B generado por IA.
    Usa los nuevos templates paramétricos de Fase 6.
    
    Args:
        plan_data: Plan generado por IA (puede ser el plan directamente o estructura con E4)
        user_data: Datos del usuario para selección de plantillas
        week_number: Número de semana para rotación de ABS
        session_number_start: Número inicial de sesión para rotación de cardio
        
    Returns:
        Plan con estructura de 4 bloques (A, B, C, D) en cada sesión
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Import new templates (Fase 6)
    try:
        from templates.block_a_warmup import generate_warmup_block
        from templates.block_c_core import generate_core_block
        from templates.block_d_cardio import generate_cardio_block
        logger.info("✅ Nuevos templates A, C, D importados correctamente")
    except ImportError as e:
        logger.error(f"❌ Error importando templates: {e}")
        return plan_data
    
    # Obtener el training_plan desde E4 (estructura vieja) o directamente (estructura nueva)
    if 'E4' in plan_data:
        training_plan = plan_data.get('E4', {}).get('training_plan', {})
    elif 'sessions' in plan_data:
        # plan_data ya es el training_plan directamente
        training_plan = plan_data
    else:
        logger.warning("⚠️ No se encontró training_plan en plan_data, devolviendo sin modificar")
        return plan_data
    
    if not training_plan or 'sessions' not in training_plan:
        logger.warning("⚠️ No se encontraron sessions en training_plan, devolviendo sin modificar")
        return plan_data
    
    # Extraer parámetros del usuario
    nivel = user_data.get('nivel', 'intermedio')
    objetivo = user_data.get('objetivo', 'hipertrofia')
    injuries = []
    if user_data.get('lesion_hombro'): injuries.append('shoulder')
    if user_data.get('lesion_lumbar'): injuries.append('low_back')
    
    training_type = training_plan.get('training_type', 'upper_lower')
    session_duration = training_plan.get('session_duration_min', 60)
    days_per_week = training_plan.get('days_per_week', 4)
    
    logger.info(f"🔧 Parámetros para templates: nivel={nivel}, objetivo={objetivo}, injuries={injuries}, tipo={training_type}")
    
    sessions = training_plan['sessions']
    session_number = session_number_start
    
    for session in sessions:
        # Determinar focus del entrenamiento (upper, lower, full_body)
        focus_list = session.get('focus', [])
        training_focus = 'full_body'  # default
        
        if any(f in ['upper_body', 'push', 'pull', 'push_focus', 'pull_focus'] for f in focus_list):
            training_focus = 'upper'
        elif any(f in ['lower_body', 'legs', 'quads', 'hamstrings'] for f in focus_list):
            training_focus = 'lower'
        
        logger.info(f"📍 Sesión {session.get('id')}: focus={training_focus}, focus_list={focus_list}")
        
        # ============================================
        # GENERAR BLOQUES A, C, D USANDO TEMPLATES PARAMETRICOS
        # ============================================
        
        # BLOCK A - Warmup
        try:
            block_a_data = generate_warmup_block(
                training_focus=training_focus,
                nivel=nivel,
                injuries=injuries,
                environment='gym',  # Default, could be from user_data
                session_duration_min=session_duration
            )
            logger.info(f"  ✅ Block A generado: {block_a_data['duration_min']} min")
        except Exception as e:
            logger.error(f"  ❌ Error generando Block A: {e}")
            block_a_data = {'id': 'A', 'block_name': 'Calentamiento', 'duration_min': 10, 'components': []}
        
        # Determine volumen del Bloque B para ajustar C
        # Aproximación: contar ejercicios en blocks
        total_exercises_b = sum(len(block.get('exercises', [])) for block in session.get('blocks', []))
        if total_exercises_b >= 6:
            volumen_b = 'alto'
        elif total_exercises_b >= 4:
            volumen_b = 'medio'
        else:
            volumen_b = 'bajo'
        
        # BLOCK C - Core
        try:
            block_c_data = generate_core_block(
                nivel=nivel,
                objetivo=objetivo,
                volumen_bloque_b=volumen_b,
                injuries=injuries,
                environment='gym'
            )
            logger.info(f"  ✅ Block C generado: {len(block_c_data['exercises'])} ejercicios")
        except Exception as e:
            logger.error(f"  ❌ Error generando Block C: {e}")
            block_c_data = {'id': 'C', 'block_name': 'Core', 'exercises': []}
        
        # BLOCK D - Cardio
        try:
            block_d_data = generate_cardio_block(
                objetivo=objetivo,
                nivel=nivel,
                volumen_bloque_b=volumen_b,
                injuries=injuries,
                session_duration_min=session_duration,
                dias_por_semana=days_per_week
            )
            logger.info(f"  ✅ Block D generado: {len(block_d_data['recommendations'])} recomendaciones")
        except Exception as e:
            logger.error(f"  ❌ Error generando Block D: {e}")
            block_d_data = {'id': 'D', 'block_name': 'Cardio', 'recommendations': []}
        
        # ============================================
        # BLOQUE B: FUERZA (DEL E4) - ENRIQUECIDO
        # ============================================
        from exercise_catalog_loader import get_exercise_by_code, get_variants_by_code, load_exercise_catalog
        
        # Cargar todos los códigos del catálogo para fuzzy matching
        full_catalog = load_exercise_catalog()
        all_catalog_codes = [ex['exercise_code'] for ex in full_catalog]
        
        def format_exercise_name(exercise_code: str) -> str:
            """Formatea exercise_code a nombre legible en español"""
            # Mapeo manual de códigos comunes
            name_mapping = {
                'press_mancuernas': 'Press con mancuernas',
                'press_banca_barra': 'Press banca con barra',
                'press_inclinado_mancuernas': 'Press inclinado con mancuernas',
                'aperturas_polea': 'Aperturas con polea',
                'press_polea': 'Press con polea',
                'fonds_triceps_suelo': 'Fondos de tríceps en suelo',
                'jalon_supino_maquina': 'Jalón supino en máquina',
                'remo_bajo_maquina': 'Remo bajo en máquina',
                'dominadas': 'Dominadas',
                'jalon_banda': 'Jalón con banda',
                'curl_biceps': 'Curl de bíceps',
                'sentadilla_barra': 'Sentadilla con barra',
                'hip_thrust_smith': 'Hip thrust en Smith',
                'sentadilla_bulgara': 'Sentadilla búlgara',
                'peso_muerto_smith': 'Peso muerto en Smith',
                'gemelos': 'Gemelos',
                'elevaciones_laterales_maquina': 'Elevaciones laterales en máquina',
                'core_antiextension': 'Core antiextensión',
                'core_antirotacion': 'Core antirrotación',
            }
            
            # Si está en el mapeo, usarlo
            if exercise_code in name_mapping:
                return name_mapping[exercise_code]
            
            # Si no, formatear automáticamente
            formatted = exercise_code.replace('_', ' ')
            # Capitalizar cada palabra
            formatted = ' '.join(word.capitalize() for word in formatted.split())
            return formatted
        
        def map_generic_to_catalog_code(generic_code: str, catalog_all_codes: list) -> str:
            """
            Mapea códigos genéricos de E4 a códigos específicos del catálogo.
            
            Estrategia:
            1. Normalizar código (lowercase, sin tildes)
            2. Mapeo manual explícito para códigos legacy (prioridad alta)
            3. Fuzzy matching como fallback para planes antiguos
            
            NOTA: E4 v2 CANÓNICO ya está 100% alineado con el catálogo backend.
            Este mapeo se mantiene solo para retrocompatibilidad con planes antiguos.
            """
            # Normalizar código de entrada
            normalized_code = generic_code.lower().strip()
            
            # MAPEO MANUAL EXPLÍCITO (prioridad)
            manual_mapping = {
                # Press variants
                'press_mancuernas': 'press_suelo_mancuernas',
                'press_polea': 'press_pecho_cable',
                'fonds_triceps_suelo': 'fondos_triceps_suelo_pies_elevados',
                
                # Aperturas
                'aperturas_polea': 'aperturas_medias_poleas',
                
                # Jalones y remos
                'jalon_supino_maquina': 'jalon_agarre_supino',
                'remo_bajo_maquina': 'remo_bajo_agarre_neutro',
                'jalon_banda': 'jalon_banda_elastica',
                
                # Dominadas
                'dominadas': 'dominadas_barra_fija',
                
                # Curl
                'curl_biceps': 'curl_biceps_barra',
                
                # Piernas
                'sentadilla_barra': 'sentadilla_barra_high_bar',
                'hip_thrust_smith': 'hip_thrust_maquina_smith',
                'sentadilla_bulgara': 'sentadilla_bulgara_peso_corporal',
                'peso_muerto_smith': 'peso_muerto_rumano_smith',
                'gemelos': 'gemelos_de_pie_unipodal',
                
                # Elevaciones
                'elevaciones_laterales_maquina': 'elevaciones_laterales_maquina_convergente',
                
                # Core
                'core_antiextension': 'plancha_frontal',
                'core_antirotacion': 'plancha_lateral',
            }
            
            # 1. Intento con mapeo manual (solo para códigos legacy)
            if normalized_code in manual_mapping:
                return manual_mapping[normalized_code]
            
            # 2. Fuzzy matching (fallback para planes antiguos)
            # E4 v2 CANÓNICO ya genera códigos perfectos, esto solo aplica a planes legacy
            from difflib import get_close_matches
            
            # Buscar match cercano en catálogo (threshold 0.6 = 60% similitud)
            close_matches = get_close_matches(normalized_code, catalog_all_codes, n=1, cutoff=0.6)
            
            if close_matches:
                matched_code = close_matches[0]
                logger.info(f"  🔍 Fuzzy match (legacy): {generic_code} → {matched_code}")
                return matched_code
            
            # 3. Si no hay match, devolver el código normalizado (será enriquecido con fallback)
            logger.warning(f"  ⚠️ Sin match para: {generic_code} (normalizado: {normalized_code})")
            return normalized_code
        
        all_exercises = []
        exercise_counter = 1
        
        for block in session.get('blocks', []):
            for exercise in block.get('exercises', []):
                exercise_copy = exercise.copy()
                exercise_copy['order'] = exercise_counter
                
                # ENRIQUECER con catálogo EDN360
                exercise_types = exercise_copy.get('exercise_types', [])
                if exercise_types and len(exercise_types) > 0:
                    exercise_code = exercise_types[0]
                    
                    # Mapear código genérico a código del catálogo (con fuzzy matching)
                    catalog_code = map_generic_to_catalog_code(exercise_code, all_catalog_codes)
                    exercise_copy['exercise_code'] = catalog_code
                    
                    # Buscar en catálogo enriquecido
                    catalog_exercise = get_exercise_by_code(catalog_code)
                    if catalog_exercise:
                        # Usar name_es del catálogo (ahora disponible)
                        exercise_copy['name'] = catalog_exercise.get('name_es', format_exercise_name(exercise_code))
                        
                        # Video canónico del catálogo
                        exercise_copy['video_url'] = catalog_exercise.get('video_url', '')
                        
                        # Extraer músculos del catálogo
                        primary_muscles = catalog_exercise.get('primary_muscles_clean', [])
                        if primary_muscles:
                            exercise_copy['primary_group'] = ', '.join(primary_muscles)
                        else:
                            exercise_copy['primary_group'] = ''
                        
                        secondary_muscles = catalog_exercise.get('secondary_muscles_clean', [])
                        if secondary_muscles:
                            exercise_copy['secondary_group'] = ', '.join(secondary_muscles)
                        else:
                            exercise_copy['secondary_group'] = ''
                        
                        logger.info(f"  ✅ Enriquecido: {exercise_code} → {exercise_copy['name']} (video: {'✓' if exercise_copy['video_url'] else '✗'})")
                    else:
                        # Fallback si no está en catálogo
                        exercise_copy['name'] = format_exercise_name(exercise_code)
                        exercise_copy['video_url'] = ''
                        exercise_copy['primary_group'] = ''
                        exercise_copy['secondary_group'] = ''
                        logger.warning(f"  ⚠️ Ejercicio no encontrado en catálogo: {exercise_code}")
                
                all_exercises.append(exercise_copy)
                exercise_counter += 1
        
        all_muscles = []
        for block in session.get('blocks', []):
            muscles = block.get('primary_muscles', [])
            all_muscles.extend(muscles)
        
        bloque_b = {
            'id': 'B',
            'nombre': 'Entrenamiento Principal (Fuerza)',
            'tipo': 'strength_training',
            'primary_muscles': list(set(all_muscles)),
            'exercises': all_exercises
        }
        
        # ============================================
        # INTEGRAR ESTRUCTURA COMPLETA A+B+C+D
        # ============================================
        session['bloques_estructurados'] = {
            'A': {
                'id': 'A',
                'nombre': block_a_data.get('block_name', 'Calentamiento'),
                'tipo': 'calentamiento',
                'duracion_minutos': block_a_data.get('duration_min', 10),
                'ejercicios': _convert_warmup_to_ejercicios(block_a_data)
            },
            'B': bloque_b,
            'C': {
                'id': 'C',
                'nombre': block_c_data.get('block_name', 'Core'),
                'tipo': 'core',
                'duracion_minutos': block_c_data.get('duration_estimate_min', 10),
                'ejercicios': _convert_core_to_ejercicios(block_c_data)
            },
            'D': {
                'id': 'D',
                'nombre': block_d_data.get('block_name', 'Cardio'),
                'tipo': 'cardio',
                'recomendaciones': block_d_data.get('recommendations', []),
                'general_notes': block_d_data.get('general_notes', [])
            }
        }
        
        session_number += 1
        logger.info(f"✅ Sesión '{session.get('name')}': Bloques A, B, C, D integrados con nuevos templates")
    
    return plan_data


def _convert_warmup_to_ejercicios(block_a_data):
    """Convierte la estructura del Block A a formato de ejercicios para BD"""
    ejercicios = []
    orden = 1
    
    for component in block_a_data.get('components', []):
        for exercise in component.get('exercises', []):
            ejercicio = {
                'orden': orden,
                'nombre': exercise.get('name', exercise.get('exercise_code', 'Ejercicio')),
                'series': exercise.get('sets', '1-2'),
                'reps': exercise.get('reps', exercise.get('duration', '30 seg')),
                'instrucciones': exercise.get('notes', exercise.get('description', ''))
            }
            ejercicios.append(ejercicio)
            orden += 1
    
    return ejercicios


def _convert_core_to_ejercicios(block_c_data):
    """Convierte la estructura del Block C a formato de ejercicios para BD"""
    ejercicios = []
    
    for exercise in block_c_data.get('exercises', []):
        ejercicio = {
            'orden': exercise.get('order', 1),
            'nombre': exercise.get('name', exercise.get('exercise_code', 'Ejercicio Core')),
            'series': exercise.get('series', 3),
            'reps': exercise.get('reps', '10-12'),
            'instrucciones': exercise.get('notes', ''),
            'video_url': exercise.get('video_url', ''),
            'exercise_code': exercise.get('exercise_code', '')
        }
        ejercicios.append(ejercicio)
    
    return ejercicios


def _format_edn360_plan_for_display(edn360_data: dict) -> dict:
    """
    Convierte el output de E.D.N.360 al formato que espera el frontend actual
    """
    try:
        # Extraer información clave de los agentes
        e4_program = edn360_data.get("E4", {})
        e5_sessions = edn360_data.get("E5", {})
        e7_load = edn360_data.get("E7", {})
        
        # Formatear para el frontend
        formatted_plan = {
            "mesociclo": e4_program.get("mesociclo", {}),
            "semanas": e4_program.get("semanas", []),
            "sesiones_detalladas": e5_sessions.get("sesiones_detalladas", []),
            "volumen_por_grupo": e4_program.get("volumen_por_grupo", {}),
            "metricas": {
                "cit_semanal": e7_load.get("cit_semanal", 0),
                "irg_score": e7_load.get("irg_score", 0)
            },
            "system": "edn360",
            "agents_executed": list(edn360_data.keys())
        }
        
        return formatted_plan
    except Exception as e:
        logger.error(f"Error formateando plan E.D.N.360: {e}")
        return edn360_data

@api_router.post("/admin/users/{user_id}/training/generate")
async def admin_generate_training_plan(
    user_id: str,
    source_type: str = "initial",  # "initial" or "followup"
    source_id: str = None,  # questionnaire submission ID or followup ID
    previous_plan_id: str = None,  # NUEVO: Plan previo de referencia para progresión
    regenerate: bool = False,
    request: Request = None
):
    """
    Admin genera el plan de entrenamiento desde cuestionario inicial o follow-up con E.D.N.360
    
    Parámetros:
    - source_id: ID del cuestionario (inicial o seguimiento) a usar
    - previous_plan_id: (Opcional) ID del plan previo para progresión
    """
    await require_admin(request)
    
    try:
        # Obtener datos del cuestionario según el tipo de fuente
        if source_type == "initial":
            # Generar desde cuestionario inicial de nutrición
            submission = await db.nutrition_questionnaire_submissions.find_one({"_id": source_id})
            
            if not submission:
                raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
            
            if submission["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="El cuestionario no pertenece a este usuario")
            
            questionnaire_data = submission["responses"]
            context_data = None
            
        elif source_type == "followup":
            # Generar desde follow-up
            followup = await db.follow_up_submissions.find_one({"_id": source_id})
            
            if not followup:
                raise HTTPException(status_code=404, detail="Follow-up no encontrado")
            
            if followup["user_id"] != user_id:
                raise HTTPException(status_code=403, detail="El follow-up no pertenece a este usuario")
            
            # Obtener cuestionario inicial
            initial_submission = await db.nutrition_questionnaire_submissions.find_one(
                {"user_id": user_id},
                sort=[("submitted_at", 1)]
            )
            
            if not initial_submission:
                raise HTTPException(
                    status_code=404,
                    detail="No se encontró cuestionario inicial para contexto"
                )
            
            questionnaire_data = initial_submission["responses"]
            # Serializar datetime fields del followup antes de usar
            followup_serialized = _serialize_datetime_fields(followup)
            context_data = {
                "followup_responses": followup_serialized.get("responses", {}),
                "ai_analysis": followup_serialized.get("ai_analysis", "")
            }
        else:
            raise HTTPException(status_code=400, detail="source_type debe ser 'initial' o 'followup'")
        
        # Obtener mes y año actual
        now = datetime.now(timezone.utc)
        current_month = now.month
        current_year = now.year
        
        # Si regenerate=True, eliminar planes existentes de este mes
        if regenerate:
            logger.info(f"🔄 Regenerando plan - eliminando plan existente del mes {current_month}/{current_year}")
            
            delete_result = await db.training_plans.delete_many({
                "user_id": user_id,
                "month": current_month,
                "year": current_year
            })
            
            logger.info(f"✅ Eliminados {delete_result.deleted_count} planes del mes actual")
        
        # Generar ID único para este plan
        plan_id = str(int(datetime.now(timezone.utc).timestamp() * 1000000))
        
        logger.info(f"🏋️ Admin iniciando generación de plan de entrenamiento E.D.N.360 para usuario {user_id}")
        
        # Obtener datos del cliente
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Adaptar cuestionario al formato E.D.N.360
        # Si es followup, mezclar datos del inicial con actualizaciones del followup
        if source_type == "followup" and context_data:
            # Combinar datos base del inicial con actualizaciones del followup
            merged_data = questionnaire_data.copy()
            merged_data.update(context_data.get("followup_responses", {}))
            adapted_questionnaire = _adapt_questionnaire_for_edn360(merged_data)
            logger.info(f"📋 Usando datos combinados: cuestionario inicial + actualizaciones de follow-up")
        else:
            adapted_questionnaire = _adapt_questionnaire_for_edn360(questionnaire_data)
        
        # Obtener plan previo si se especificó (para progresión)
        previous_plan_data = None
        if previous_plan_id:
            logger.info(f"📋 Usando plan previo {previous_plan_id} como referencia")
            previous_plan = await db.training_plans.find_one({"_id": previous_plan_id})
            
            if not previous_plan:
                raise HTTPException(status_code=404, detail=f"Plan previo no encontrado")
            
            if previous_plan.get("user_id") != user_id:
                raise HTTPException(status_code=403, detail="El plan previo no pertenece a este usuario")
            
            previous_plan_data = previous_plan
        
        # Usar el orquestador E.D.N.360 - SIEMPRE agentes E1-E9
        logger.info("🚀 Generando plan con agentes E1-E9")
        
        # Nota: El plan previo se pasa a los agentes para progresión
        if previous_plan_data:
            logger.info(f"   📋 Plan previo encontrado: {previous_plan_data['_id']} (usado para progresión)")
        
        # ⚠️ DESACTIVADO: from edn360.orchestrator import EDN360Orchestrator
        # ⚠️ DESACTIVADO: orchestrator = EDN360Orchestrator()
        
        # Pasar plan previo a los agentes si existe
        result = await orchestrator._execute_training_initial(
            adapted_questionnaire,
            previous_plan=previous_plan_data
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error generando plan: {result.get('error', 'Error desconocido')}"
            )
        
        # Determinar número de mes (contar planes previos del usuario)
        planes_previos_count = await db.training_plans.count_documents({"user_id": user_id})
        numero_mes = planes_previos_count + 1
        
        # ========== INTEGRACIÓN DE PLANTILLAS (BLOQUES A, C, D) ==========
        logger.info("🔧 ========== INICIANDO INTEGRACIÓN DE PLANTILLAS ==========")
        logger.info(f"🔧 Plan original tiene {len(result['plan_data'].get('sessions', []))} sesiones")
        
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from training_templates import seleccionar_plantillas
        
        # Extraer datos del usuario para selección de plantillas
        user_data_for_templates = {
            'edad': adapted_questionnaire.get('edad', 0),
            'nivel': adapted_questionnaire.get('experience_level', 'principiante').lower(),
            'objetivo': adapted_questionnaire.get('goal_primary', 'mantenimiento').lower(),
            'lesion_hombro': adapted_questionnaire.get('injuries_or_limitations', '').lower().find('hombro') != -1,
            'lesion_lumbar': adapted_questionnaire.get('injuries_or_limitations', '').lower().find('lumbar') != -1 or 
                           adapted_questionnaire.get('injuries_or_limitations', '').lower().find('espalda baja') != -1,
            'muy_sedentario': adapted_questionnaire.get('lifestyle_activity', '').lower() == 'sedentary',
            'primera_sesion': planes_previos_count == 0
        }
        
        # Procesar el plan de la IA y agregar plantillas a cada sesión
        plan_data_original = result["plan_data"]
        logger.info(f"🔧 Llamando a _integrate_template_blocks con {len(plan_data_original.get('sessions', []))} sesiones")
        logger.info(f"🔧 user_data_for_templates: {user_data_for_templates}")
        
        plan_with_blocks = await _integrate_template_blocks(
            plan_data_original, 
            user_data_for_templates,
            week_number=numero_mes,  # Usar número de mes como número de semana
            session_number_start=1
        )
        
        logger.info(f"🔧 Después de _integrate_template_blocks: {len(plan_with_blocks.get('sessions', []))} sesiones")
        if plan_with_blocks.get('sessions'):
            first_session = plan_with_blocks['sessions'][0]
            if 'bloques_estructurados' in first_session:
                logger.info("✅ Primera sesión TIENE bloques_estructurados")
                logger.info(f"   Bloques: {list(first_session['bloques_estructurados'].keys())}")
            else:
                logger.error("❌ Primera sesión NO TIENE bloques_estructurados!")
        
        # Usar el plan con bloques integrados
        result["plan_data"] = plan_with_blocks
        logger.info("✅ Plantillas integradas exitosamente en todas las sesiones")
        
        # Generar versiones del plan
        plan_data_json = _format_edn360_plan_for_display(result["plan_data"])
        
        # FUENTE DE VERDAD: edn360_data.formatted_plan (generado por post-procesador)
        formatted_plan = result["plan_data"].get("formatted_plan")
        
        if isinstance(formatted_plan, str) and formatted_plan.strip():
            plan_text_professional = formatted_plan
            logger.info("✅ plan_text tomado directamente de edn360_data.formatted_plan (post-procesador)")
        else:
            logger.error("⚠️ formatted_plan ausente o vacío, usando _format_edn360_plan_as_text como fallback")
            plan_text_professional = _format_edn360_plan_as_text(result["plan_data"], user.get("name", user.get("username", "Cliente")), numero_mes)
        
        # Guardar el plan en training_plans con formato E.D.N.360
        training_plan_doc = {
            "_id": plan_id,
            "user_id": user_id,
            "month": current_month,
            "year": current_year,
            "source_type": source_type,
            "source_id": source_id,
            "previous_plan_id": previous_plan_id,  # NUEVO: Referencia al plan previo
            "questionnaire_data": questionnaire_data,
            
            # Datos de E.D.N.360
            "edn360_data": result["plan_data"],
            "agent_executions": result.get("executions", []),
            "system_version": "edn360_v1",
            
            # Compatibilidad con formato antiguo (para renderizado)
            "agent_1_output": result["plan_data"].get("E1", {}),
            "agent_2_output": result["plan_data"].get("E2", {}),
            "agent_3_output": result["plan_data"].get("E4", {}),  # Arquitecto del programa
            "plan_final": plan_data_json,  # JSON estructurado para el frontend
            "plan_text": plan_text_professional,  # TEXTO PROFESIONAL para enviar al cliente
            
            "generated_at": now,
            "edited": False,
            "pdf_id": None,
            "pdf_filename": None,
            "sent_email": False,
            "sent_whatsapp": False
        }
        
        await db.training_plans.insert_one(training_plan_doc)
        
        logger.info(f"✅ Plan de entrenamiento generado exitosamente para usuario {user_id} - {plan_id}")
        
        return {
            "success": True,
            "message": "Plan de entrenamiento generado correctamente",
            "plan_id": plan_id,
            "plan": training_plan_doc
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generando plan de entrenamiento: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando plan: {str(e)}"
        )


@api_router.get("/admin/users/{user_id}/training")
async def get_user_training_plans(user_id: str, request: Request):
    """Admin obtiene el historial de planes de entrenamiento de un usuario"""
    await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Obtener planes de entrenamiento ordenados por fecha
    plans = await db.training_plans.find(
        {"user_id": user_id}
    ).sort("generated_at", -1).to_list(length=1000)
    
    # Obtener información de PDFs asociados y convertir _id a id
    for plan in plans:
        plan["id"] = str(plan["_id"])  # Convert _id to id for frontend
        if plan.get("pdf_id"):
            pdf = await db.pdfs.find_one({"_id": plan["pdf_id"]})
            if pdf:
                plan["pdf_filename"] = pdf.get("filename")
                plan["pdf_url"] = pdf.get("file_path")
    
    return {
        "success": True,
        "plans": plans,
        "total": len(plans)
    }


@api_router.patch("/admin/users/{user_id}/training/{plan_id}")
async def update_training_plan(
    user_id: str,
    plan_id: str,
    request: Request
):
    """Admin edita manualmente el plan de entrenamiento final"""
    await require_admin(request)
    
    # Get body
    body = await request.json()
    plan_final = body.get("plan_final")
    
    plan = await db.training_plans.find_one({"_id": plan_id, "user_id": user_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan no encontrado")
    
    # Actualizar plan
    await db.training_plans.update_one(
        {"_id": plan_id},
        {
            "$set": {
                "plan_final": plan_final,
                "edited": True
            }
        }
    )
    
    logger.info(f"✅ Plan de entrenamiento {plan_id} editado por admin")
    
    return {
        "success": True,
        "message": "Plan actualizado correctamente"
    }


@api_router.delete("/admin/users/{user_id}/training/{plan_id}")
async def delete_training_plan(user_id: str, plan_id: str, request: Request = None):
    """Admin elimina completamente un plan de entrenamiento"""
    await require_admin(request)
    
    try:
        # Buscar el plan
        plan = await db.training_plans.find_one({"_id": plan_id, "user_id": user_id})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan de entrenamiento no encontrado")
        
        # Eliminar PDF asociado si existe
        if plan.get("pdf_id"):
            pdf_result = await db.pdfs.delete_one({"_id": plan["pdf_id"]})
            logger.info(f"🗑️ PDF asociado eliminado: {pdf_result.deleted_count} documento(s)")
        
        # Eliminar el plan de entrenamiento
        result = await db.training_plans.delete_one({"_id": plan_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        logger.info(f"✅ Plan de entrenamiento {plan_id} eliminado completamente")
        
        return {
            "success": True,
            "message": "Plan de entrenamiento eliminado correctamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando plan de entrenamiento: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando plan: {str(e)}"
        )


@api_router.post("/admin/users/{user_id}/training-pdf")
async def generate_training_pdf(user_id: str, plan_id: str, request: Request = None):
    """Admin genera PDF del plan de entrenamiento"""
    await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Try EDN360 v2 first (training_plans_v2), then fallback to legacy (training_plans)
    edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
    plan = await edn360_db.training_plans_v2.find_one({"_id": plan_id, "user_id": user_id}, {"_id": 0})
    if not plan:
        plan = await db.training_plans.find_one({"_id": plan_id, "user_id": user_id})
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan de entrenamiento no encontrado")
    
    try:
        from weasyprint import HTML
        import io
        
        # Get plan content with proper fallback chain
        plan_content = plan.get("plain_text_content", "") or plan.get("plan_text", "")
        
        # If no plain text, generate from structured data (EDN360 v2)
        if not plan_content and plan.get("plan"):
            plan_content = _generate_plain_text_from_structured_plan(plan.get("plan"))
        
        # Fallback to plan_final for legacy plans
        if not plan_content:
            plan_content = plan.get("plan_final", "")
            if isinstance(plan_content, dict):
                plan_content = str(plan_content)
        
        if not isinstance(plan_content, str):
            plan_content = str(plan_content)
        
        month = plan.get("month")
        year = plan.get("year")
        
        month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                       "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Helper function to convert video URLs to clickable links
        import re
        def convert_video_urls_to_links(text):
            """Convert (Video: URL) format to clickable HTML links"""
            # Pattern: (Video: URL)
            pattern = r'\(Video:\s*(https?://[^\)]+)\)'
            
            def replace_video(match):
                url = match.group(1).strip()
                return f' (<a href="{url}" style="color: #2563eb; text-decoration: none; font-weight: bold;" target="_blank">📹 Ver Video</a>)'
            
            return re.sub(pattern, replace_video, text)
        
        # Mejorar conversión de texto a HTML con soporte para video links
        lines = plan_content.split('\n')
        html_lines = []
        in_list = False
        
        for line in lines:
            line = line.strip()
            if not line:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append('<br>')
                continue
            
            # Convert video URLs to clickable links
            line = convert_video_urls_to_links(line)
            
            # Títulos principales (emojis + texto en mayúsculas)
            if line.startswith('🏋') or line.startswith('📅') or line.startswith('⚠️') or line.startswith('📈') or line.startswith('📞'):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<h2 style="color: #2563eb; margin-top: 20px; margin-bottom: 10px;">{line}</h2>')
            # Subtítulos (** text **)
            elif line.startswith('**') and line.endswith('**'):
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                clean_line = line.replace('**', '')
                html_lines.append(f'<h3 style="color: #1e40af; margin-top: 15px; margin-bottom: 8px;">{clean_line}</h3>')
            # Items de lista (- texto)
            elif line.startswith('-'):
                if not in_list:
                    html_lines.append('<ul style="margin-left: 20px; line-height: 1.8;">')
                    in_list = True
                clean_line = line[1:].strip()
                html_lines.append(f'<li>{clean_line}</li>')
            # Texto normal
            else:
                if in_list:
                    html_lines.append('</ul>')
                    in_list = False
                html_lines.append(f'<p style="margin: 8px 0;">{line}</p>')
        
        if in_list:
            html_lines.append('</ul>')
        
        html_content = '\n'.join(html_lines)
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: 'Arial', sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                h1 {{
                    color: #2563eb;
                    border-bottom: 3px solid #2563eb;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #1e40af;
                    margin-top: 20px;
                }}
                h3 {{
                    color: #1e40af;
                    margin-top: 15px;
                    margin-bottom: 8px;
                }}
                a {{
                    color: #2563eb;
                    text-decoration: none;
                    font-weight: bold;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .footer {{
                    margin-top: 50px;
                    text-align: center;
                    color: #666;
                    font-size: 0.9em;
                }}
                ul {{
                    margin-left: 20px;
                    line-height: 1.8;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                p {{
                    margin: 8px 0;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏋️ Plan de Entrenamiento Personalizado</h1>
                <p><strong>{user.get('name', 'Cliente')}</strong></p>
                <p>{month_names[month]} {year}</p>
            </div>
            <div class="content">
                {html_content}
            </div>
            <div class="footer">
                <p>Jorge Calcerrada - Entrenador Personal</p>
                <p>Plan generado el {datetime.now(timezone.utc).strftime('%d/%m/%Y')}</p>
            </div>
        </body>
        </html>
        """
        
        # Generate PDF content
        pdf_content = HTML(string=html_template).write_pdf()
        
        # Create standardized PDF document
        pdf_title = f"Plan de Entrenamiento - {month_names[month]} {year}"
        pdf_filename = f"plan_entrenamiento_{user.get('name', user_id)}_{month}_{year}.pdf"
        
        pdf_id = await create_pdf_document(
            user_id=user_id,
            title=pdf_title,
            content=pdf_content,
            pdf_type="training",
            related_id=plan_id,
            filename=pdf_filename
        )
        
        # Actualizar plan con referencia al PDF
        await db.training_plans.update_one(
            {"_id": plan_id},
            {
                "$set": {
                    "pdf_id": pdf_id,
                    "pdf_filename": pdf_filename,
                    "pdf_generated": True
                }
            }
        )
        
        logger.info(f"✅ PDF de entrenamiento generado para usuario {user_id} - {pdf_id}")
        
        return {
            "success": True,
            "message": "PDF generado correctamente",
            "pdf_id": pdf_id,
            "filename": pdf_filename
        }
        
    except Exception as e:
        logger.error(f"Error generando PDF de entrenamiento: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generando PDF: {str(e)}"
        )


@api_router.post("/admin/users/{user_id}/training/send-email")
async def send_training_email(user_id: str, plan_id: str = None, request: Request = None):
    """Admin envía el plan de entrenamiento por email"""
    await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Si no se especifica plan_id, obtener el más reciente
    if not plan_id:
        plan = await db.training_plans.find_one(
            {"user_id": user_id},
            sort=[("generated_at", -1)]
        )
    else:
        plan = await db.training_plans.find_one({"_id": plan_id, "user_id": user_id})
    
    if not plan:
        raise HTTPException(status_code=404, detail="Usuario no tiene plan de entrenamiento")
    
    try:
        from email_utils import send_email
        import markdown
        
        # FIX: Usar plan_text (texto profesional) en lugar de plan_final (JSON)
        plan_content = plan.get("plan_text", "")
        
        # Fallback a plan_final si no existe plan_text (planes antiguos)
        if not plan_content:
            plan_content = plan.get("plan_final", "")
            if isinstance(plan_content, dict):
                plan_content = str(plan_content)
        
        if not isinstance(plan_content, str):
            plan_content = str(plan_content)
        
        month = plan.get("month")
        year = plan.get("year")
        
        month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                       "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Convertir markdown a HTML
        html_content = markdown.markdown(plan_content)
        
        email_html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    padding: 30px;
                    background: #f9fafb;
                }}
                .footer {{
                    background: #1f2937;
                    color: white;
                    padding: 20px;
                    text-align: center;
                    border-radius: 0 0 10px 10px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <img src="{request.base_url._url}logo-sin-fondo.png" alt="Jorge Calcerrada" style="height: 80px; width: auto; margin: 0 auto 20px;">
                <h1>🏋️ Tu Plan de Entrenamiento Personalizado</h1>
                <p><strong>{month_names[month]} {year}</strong></p>
            </div>
            <div class="content">
                <p>Hola <strong>{user.get('name', 'Cliente')}</strong>,</p>
                <p>Te envío tu plan de entrenamiento personalizado para este mes:</p>
                <hr>
                {html_content}
            </div>
            <div class="footer">
                <p><strong>Jorge Calcerrada</strong></p>
                <p>Entrenador Personal</p>
            </div>
        </body>
        </html>
        """
        
        subject = f"🏋️ Tu Plan de Entrenamiento - {month_names[month]} {year}"
        
        send_email(
            to_email=user.get('email'),
            subject=subject,
            html_body=email_html
        )
        
        # Marcar como enviado
        await db.training_plans.update_one(
            {"_id": plan["_id"]},
            {"$set": {"sent_email": True}}
        )
        
        logger.info(f"✅ Plan de entrenamiento enviado por email a {user.get('email')}")
        
        return {
            "success": True,
            "message": "Plan enviado por email correctamente"
        }
        
    except Exception as e:
        logger.error(f"Error enviando email de entrenamiento: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error enviando email: {str(e)}"
        )


@api_router.get("/admin/users/{user_id}/training/whatsapp-link")
async def get_training_whatsapp_link(user_id: str, plan_id: str = None, request: Request = None):
    """Admin obtiene link de WhatsApp con el plan de entrenamiento"""
    await require_admin(request)
    
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Si no se especifica plan_id, obtener el más reciente
    if not plan_id:
        plan = await db.training_plans.find_one(
            {"user_id": user_id},
            sort=[("generated_at", -1)]
        )
    else:
        plan = await db.training_plans.find_one({"_id": plan_id, "user_id": user_id})
    
    if not plan:
        raise HTTPException(status_code=404, detail="Usuario no tiene plan de entrenamiento")
    
    # Obtener teléfono del usuario
    phone = user.get('phone', '')
    if not phone:
        raise HTTPException(
            status_code=400,
            detail="El usuario no tiene número de teléfono registrado"
        )
    
    try:
        import urllib.parse
        
        # FIX: Usar plan_text (texto profesional) en lugar de plan_final (JSON)
        plan_content = plan.get("plan_text", "")
        
        # Fallback a plan_final si no existe plan_text (planes antiguos)
        if not plan_content:
            plan_content = plan.get("plan_final", "")
            if isinstance(plan_content, dict):
                plan_content = str(plan_content)
        
        if not isinstance(plan_content, str):
            plan_content = str(plan_content)
        
        month = plan.get("month")
        year = plan.get("year")
        
        month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                       "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Crear mensaje para WhatsApp (con límite de caracteres)
        message = f"""🏋️ *Tu Plan de Entrenamiento Personalizado - {month_names[month]} {year}*

Hola {user.get('name', 'Cliente')}!

Te envío tu plan de entrenamiento personalizado:

{plan_content[:3000]}...

_Si necesitas el plan completo, revísalo en tu panel de usuario o te lo envío por email._

*Jorge Calcerrada - Entrenador Personal*"""
        
        # Limpiar número de teléfono (solo dígitos)
        clean_phone = ''.join(filter(str.isdigit, phone))
        
        # Generar link de WhatsApp
        encoded_message = urllib.parse.quote(message)
        whatsapp_link = f"https://wa.me/{clean_phone}?text={encoded_message}"
        
        # Marcar como enviado por WhatsApp
        await db.training_plans.update_one(
            {"_id": plan["_id"]},
            {"$set": {"sent_whatsapp": True}}
        )
        
        logger.info(f"Link de WhatsApp generado para plan de entrenamiento {user_id} - Plan {plan['_id']}")
        
        return {
            "success": True,
            "whatsapp_link": whatsapp_link,
            "phone": phone,
            "plan_id": plan["_id"]
        }
        
    except Exception as e:
        logger.error(f"Error generando link de WhatsApp de entrenamiento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando link: {str(e)}"
        )




from google_calendar_service import (
    get_authorization_url,
    exchange_code_for_tokens,
    create_calendar_event,
    list_upcoming_events,
    delete_calendar_event,
    update_calendar_event
)
from fastapi.responses import RedirectResponse

@api_router.get("/auth/google/calendar/login")
async def google_calendar_login(request: Request):
    """Inicia proceso de autorización de Google Calendar"""
    admin = await require_admin(request)
    
    auth_url = get_authorization_url()
    return {"authorization_url": auth_url}


@api_router.get("/auth/google/calendar/callback")
async def google_calendar_callback(code: str):
    """Callback de OAuth - intercambia código por tokens"""
    try:
        tokens = await exchange_code_for_tokens(code)
        admin_email = "ecjtrainer@gmail.com"
        
        await db.calendar_config.update_one(
            {"admin_email": admin_email},
            {
                "$set": {
                    "google_tokens": tokens,
                    "connected_at": datetime.now(timezone.utc)
                }
            },
            upsert=True
        )
        
        return RedirectResponse(
            url=f"{os.getenv('FRONTEND_URL')}/admin?calendar_connected=true"
        )
        
    except Exception as e:
        logger.error(f"Error in calendar callback: {e}")
        return RedirectResponse(
            url=f"{os.getenv('FRONTEND_URL')}/admin?calendar_error=true"
        )


@api_router.get("/calendar/status")
async def check_calendar_status(request: Request):
    """Verifica si Google Calendar está conectado"""
    admin = await require_admin(request)
    
    admin_email = "ecjtrainer@gmail.com"
    config = await db.calendar_config.find_one({"admin_email": admin_email})
    
    if config and config.get("google_tokens"):
        return {
            "connected": True,
            "connected_at": config.get("connected_at")
        }
    
    return {"connected": False}


@api_router.post("/calendar/events")
async def create_event(request: Request, event_data: dict):
    """Crea un evento en Google Calendar"""
    admin = await require_admin(request)
    
    try:
        admin_email = "ecjtrainer@gmail.com"
        config = await db.calendar_config.find_one({"admin_email": admin_email})
        
        if not config or not config.get("google_tokens"):
            raise HTTPException(
                status_code=400,
                detail="Google Calendar no está conectado"
            )
        
        tokens = config["google_tokens"]
        
        # Obtener email del cliente
        client_email = None
        if event_data.get("client_id"):
            client = await db.users.find_one({"id": event_data["client_id"]})
            if client:
                client_email = client.get("email")
        
        # Parsear fechas
        start_dt = datetime.fromisoformat(event_data["start"].replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(event_data["end"].replace('Z', '+00:00'))
        
        # Crear evento
        result = await create_calendar_event(
            tokens=tokens,
            summary=event_data["title"],
            start_datetime=start_dt,
            end_datetime=end_dt,
            attendee_email=client_email,
            description=event_data.get("description")
        )
        
        # Actualizar tokens si se refrescaron
        if result.get("updated_tokens"):
            await db.calendar_config.update_one(
                {"admin_email": admin_email},
                {"$set": {"google_tokens": result["updated_tokens"]}}
            )
        
        return {
            "success": True,
            "event": result["event"],
            "html_link": result["event"].get("htmlLink")
        }
        
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/calendar/events")
async def get_upcoming_events(request: Request):
    """Lista próximos eventos del calendario"""
    admin = await require_admin(request)
    
    try:
        admin_email = "ecjtrainer@gmail.com"
        config = await db.calendar_config.find_one({"admin_email": admin_email})
        
        if not config or not config.get("google_tokens"):
            return {"connected": False, "events": []}
        
        tokens = config["google_tokens"]
        events = await list_upcoming_events(tokens, max_results=30)
        
        return {
            "connected": True,
            "events": events
        }
        
    except Exception as e:
        logger.error(f"Error fetching events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/calendar/events/{event_id}")
async def delete_event(request: Request, event_id: str):
    """Elimina un evento del calendario"""
    admin = await require_admin(request)
    
    try:
        admin_email = "ecjtrainer@gmail.com"
        config = await db.calendar_config.find_one({"admin_email": admin_email})
        
        if not config or not config.get("google_tokens"):
            raise HTTPException(status_code=400, detail="Calendar not connected")
        
        tokens = config["google_tokens"]
        success = await delete_calendar_event(tokens, event_id)
        
        if success:
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete event")
            
    except Exception as e:
        logger.error(f"Error deleting event: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Add Cache Control Middleware to prevent browser caching of API responses
@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    # Only add no-cache headers to API responses
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db():
    """Initialize default prospect stages and templates if they don't exist"""
    try:
        # Check if stages exist
        count = await db.prospect_stages.count_documents({})
        if count == 0:
            # Create default stages
            default_stages = [
                {"_id": "stage_nuevo", "name": "Nuevo", "color": "#3B82F6", "order": 1, "created_at": datetime.now(timezone.utc)},
                {"_id": "stage_contactado", "name": "Contactado", "color": "#8B5CF6", "order": 2, "created_at": datetime.now(timezone.utc)},
                {"_id": "stage_interesado", "name": "Interesado", "color": "#10B981", "order": 3, "created_at": datetime.now(timezone.utc)},
                {"_id": "stage_no_interesado", "name": "No Interesado", "color": "#EF4444", "order": 4, "created_at": datetime.now(timezone.utc)},
                {"_id": "stage_convertido", "name": "Convertido", "color": "#F59E0B", "order": 5, "created_at": datetime.now(timezone.utc)}
            ]
            await db.prospect_stages.insert_many(default_stages)
            logger.info("Default prospect stages created")
        
        # Check if templates exist
        template_count = await db.message_templates.count_documents({})
        if template_count == 0:
            # Create default templates
            default_templates = [
                # WhatsApp Templates
                {
                    "_id": "template_wa_welcome",
                    "type": "whatsapp",
                    "name": "Bienvenida Nuevo Cliente",
                    "content": "¡Hola {nombre}! 🎉 Bienvenido al equipo 💪\n\nYa tienes acceso a tu panel personal. ¿Cuándo te viene bien tu primera sesión?\n\n¡Vamos a conseguir tus objetivos juntos!",
                    "variables": ["nombre"],
                    "category": "welcome",
                    "tags": ["bienvenida", "nuevo", "onboarding"],
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "_id": "template_wa_session_reminder",
                    "type": "whatsapp",
                    "name": "Recordatorio de Sesión",
                    "content": "Hola {nombre} 👋\n\nTe recuerdo nuestra sesión mañana a las {hora}. ¿Confirmas que nos vemos? 💪",
                    "variables": ["nombre", "hora"],
                    "category": "reminder",
                    "tags": ["recordatorio", "sesión", "cita"],
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "_id": "template_wa_progress_photos",
                    "type": "whatsapp",
                    "name": "Solicitud Fotos de Progreso",
                    "content": "¡Hey {nombre}! 📸\n\nEs hora de ver tu progreso. ¿Me puedes enviar fotos actualizadas? (Frente, espalda, lateral)\n\n¡Seguro que hay grandes cambios!",
                    "variables": ["nombre"],
                    "category": "followup",
                    "tags": ["progreso", "fotos", "seguimiento"],
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "_id": "template_wa_checkin",
                    "type": "whatsapp",
                    "name": "Check-in Semanal",
                    "content": "Hola {nombre} 💪\n\n¿Cómo ha ido la semana? ¿Alguna dificultad con la rutina o la nutrición?\n\nRecuerda que estoy aquí para ayudarte.",
                    "variables": ["nombre"],
                    "category": "followup",
                    "tags": ["seguimiento", "semanal", "check-in"],
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "_id": "template_wa_motivation",
                    "type": "whatsapp",
                    "name": "Mensaje Motivacional",
                    "content": "¡{nombre}! 🔥\n\nRecuerda por qué empezaste. Cada día de entrenamiento es un paso más cerca de tu objetivo.\n\n¡Tú puedes! 💪",
                    "variables": ["nombre"],
                    "category": "general",
                    "tags": ["motivación", "ánimo", "inspiración"],
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "_id": "template_wa_form_reminder",
                    "type": "whatsapp",
                    "name": "Recordatorio Formulario",
                    "content": "Hola {nombre} 👋\n\nTe recuerdo que tienes pendiente el formulario de seguimiento. Es importante para ajustar tu plan.\n\n¿Algún problema para completarlo?",
                    "variables": ["nombre"],
                    "category": "reminder",
                    "tags": ["recordatorio", "formulario", "pendiente"],
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "_id": "template_wa_congratulations",
                    "type": "whatsapp",
                    "name": "Felicitaciones por Logro",
                    "content": "¡FELICIDADES {nombre}! 🎉🎊\n\n¡Has alcanzado tu objetivo! Esto es el resultado de tu esfuerzo y dedicación.\n\n¡Estoy muy orgulloso de ti! 💪✨",
                    "variables": ["nombre"],
                    "category": "general",
                    "tags": ["felicitación", "logro", "éxito"],
                    "created_at": datetime.now(timezone.utc)
                },
                # Alert Templates
                {
                    "_id": "template_alert_new_routine",
                    "type": "alert",
                    "name": "Nueva Rutina Disponible",
                    "subject": "Nueva rutina de entrenamiento 💪",
                    "content": "Tu nueva rutina de entrenamiento ya está disponible. Revísala en la sección de Documentos.",
                    "variables": [],
                    "category": "general",
                    "tags": ["rutina", "entrenamiento", "nuevo"],
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "_id": "template_alert_nutrition_plan",
                    "type": "alert",
                    "name": "Plan Nutricional Actualizado",
                    "subject": "Actualización de tu plan nutricional 🥗",
                    "content": "He actualizado tu plan nutricional basándome en tu progreso. Revísalo en Documentos.",
                    "variables": [],
                    "category": "general",
                    "tags": ["nutrición", "plan", "actualización"],
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "_id": "template_alert_form_pending",
                    "type": "alert",
                    "name": "Formulario Pendiente",
                    "subject": "Formulario de seguimiento pendiente 📋",
                    "content": "Tienes un formulario de seguimiento pendiente. Por favor, complétalo para que pueda ajustar tu plan.",
                    "variables": [],
                    "category": "reminder",
                    "tags": ["formulario", "recordatorio", "pendiente"],
                    "created_at": datetime.now(timezone.utc)
                },
                {
                    "_id": "template_alert_session_scheduled",
                    "type": "alert",
                    "name": "Sesión Programada",
                    "subject": "Sesión programada para {fecha} 📅",
                    "content": "Tu próxima sesión está programada para el {fecha} a las {hora}. ¡Nos vemos!",
                    "variables": ["fecha", "hora"],
                    "category": "reminder",
                    "tags": ["sesión", "cita", "programada"],
                    "created_at": datetime.now(timezone.utc)
                }
            ]
            await db.message_templates.insert_many(default_templates)
            logger.info("Default message templates created")
            
    except Exception as e:
        logger.error(f"Error initializing defaults: {e}")




# ==================== MONTHLY FOLLOW-UP ENDPOINTS ====================

@api_router.post("/follow-up/submit")
async def submit_follow_up(follow_up: FollowUpSubmit, request: Request):
    """
    Cliente envía cuestionario de seguimiento mensual
    
    FASE 1 DUAL-WRITE:
    - Guarda en BD Web (follow_up_submissions) como siempre
    - Si USE_CLIENT_DRAWER_WRITE=true, también guarda en client_drawers
    """
    try:
        current_user = await get_current_user(request)
        user_id = current_user["id"]
        
        # Buscar el plan de nutrición más reciente del usuario (opcional)
        latest_plan = await db.nutrition_plans.find_one(
            {"user_id": user_id},
            sort=[("generated_at", -1)]
        )
        
        # Calcular días desde el último plan (si existe)
        days_since_plan = None
        if latest_plan:
            plan_generated_at = latest_plan["generated_at"]
            # Asegurar que la fecha tenga timezone
            if plan_generated_at.tzinfo is None:
                plan_generated_at = plan_generated_at.replace(tzinfo=timezone.utc)
            days_since_plan = (datetime.now(timezone.utc) - plan_generated_at).days
        
        # Buscar el cuestionario inicial
        initial_questionnaire = await db.nutrition_questionnaire_submissions.find_one(
            {"user_id": user_id},
            sort=[("submitted_at", -1)]
        )
        
        # Generar ID y timestamp
        follow_up_id = str(datetime.now(timezone.utc).timestamp()).replace('.', '')
        submission_date = datetime.now(timezone.utc)
        
        # ============================================
        # 1. GUARDAR EN BD WEB (fuente de verdad)
        # ============================================
        follow_up_doc = {
            "_id": follow_up_id,
            "user_id": user_id,
            "submission_date": submission_date,
            "days_since_last_plan": days_since_plan,
            "previous_plan_id": latest_plan["_id"] if latest_plan else None,
            "previous_questionnaire_id": initial_questionnaire["_id"] if initial_questionnaire else None,
            "measurement_type": follow_up.measurement_type,
            "measurements": follow_up.measurements.dict() if follow_up.measurements else None,
            "adherence": follow_up.adherence.dict(),
            "wellbeing": follow_up.wellbeing.dict(),
            "changes_perceived": follow_up.changes_perceived.dict(),
            "feedback": follow_up.feedback.dict(),
            "status": "pending_analysis",
            "ai_analysis": None,
            "ai_analysis_edited": False,
            "new_plan_id": None,
            "created_at": submission_date,
            "updated_at": submission_date
        }
        
        await db.follow_up_submissions.insert_one(follow_up_doc)
        logger.info(f"✅ Follow-up guardado en BD Web: {follow_up_id} (user_id: {user_id})")
        
        # Desactivar el botón de seguimiento después de completar
        await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "followup_activated": False,
                    "followup_activated_at": None,
                    "followup_activated_by": None
                }
            }
        )
        
        # Crear alerta para el admin
        admin_user = await db.users.find_one({"role": "admin"})
        if admin_user:
            alert_id = str(datetime.now(timezone.utc).timestamp()).replace('.', '') + "_alert"
            alert_doc = {
                "_id": alert_id,
                "user_id": admin_user["_id"],
                "title": f"📊 Seguimiento mensual recibido - {current_user['name']}",
                "message": f"{current_user['name']} ha completado su cuestionario de seguimiento mensual ({days_since_plan} días desde su último plan). Revisa sus respuestas y genera su análisis.",
                "type": "follow_up",
                "link": f"/admin?client={user_id}&tab=seguimiento",
                "read": False,
                "date": submission_date,
                "created_at": submission_date
            }
            await db.alerts.insert_one(alert_doc)
        
        # ============================================
        # 2. DUAL-WRITE A CLIENT_DRAWERS (best effort)
        # ============================================
        use_client_drawer_write = os.getenv('USE_CLIENT_DRAWER_WRITE', 'false').lower() == 'true'
        
        if use_client_drawer_write:
            try:
                from repositories.client_drawer_repository import add_questionnaire_to_drawer
                
                # Añadir cuestionario a client_drawer
                await add_questionnaire_to_drawer(
                    user_id=user_id,
                    submission_id=follow_up_id,
                    submitted_at=submission_date,
                    source="followup",  # Cuestionario de seguimiento mensual
                    raw_payload=follow_up_doc  # Documento completo
                )
                
                logger.info(f"✅ Dual-write exitoso a client_drawers: {follow_up_id}")
                
            except Exception as drawer_error:
                # ⚠️ BEST EFFORT: Si falla client_drawers, NO falla el endpoint
                logger.error(
                    f"⚠️  Dual-write to client_drawers failed for user_id {user_id}, "
                    f"submission_id {follow_up_id}: {drawer_error}"
                )
                # Continuar normalmente, BD Web ya tiene el cuestionario
        else:
            logger.info(f"ℹ️  USE_CLIENT_DRAWER_WRITE=false, solo se guardó en BD Web")
        
        # ============================================
        # 3. RESPONDER AL FRONTEND
        # ============================================
        return {
            "success": True,
            "message": "Cuestionario de seguimiento enviado correctamente",
            "follow_up_id": follow_up_id,
            "days_since_plan": days_since_plan
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting follow-up: {e}")
        raise HTTPException(status_code=500, detail=f"Error al enviar el cuestionario: {str(e)}")


@api_router.get("/admin/users/{user_id}/follow-ups")
async def get_user_follow_ups(user_id: str, request: Request):
    """
    Admin obtiene todos los seguimientos de un usuario
    """
    await require_admin(request)
    
    try:
        follow_ups = await db.follow_up_submissions.find(
            {"user_id": user_id}
        ).sort("submission_date", -1).to_list(100)
        
        # Convertir fechas a ISO string
        for follow_up in follow_ups:
            follow_up["id"] = str(follow_up["_id"])
            if "submission_date" in follow_up:
                follow_up["submission_date"] = follow_up["submission_date"].isoformat()
            if "created_at" in follow_up:
                follow_up["created_at"] = follow_up["created_at"].isoformat()
            if "updated_at" in follow_up:
                follow_up["updated_at"] = follow_up["updated_at"].isoformat()
        
        return {"follow_ups": follow_ups}
        
    except Exception as e:
        logger.error(f"Error getting follow-ups: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener seguimientos: {str(e)}")


@api_router.post("/admin/users/{user_id}/followups/{followup_id}/analyze-with-ia")
async def analyze_follow_up_with_ai(user_id: str, followup_id: str, request: Request):
    """
    Admin solicita análisis con IA de un seguimiento mensual
    Compara datos iniciales vs actuales y genera recomendaciones
    """
    await require_admin(request)
    
    try:
        # Obtener el seguimiento
        follow_up = await db.follow_up_submissions.find_one({"_id": followup_id, "user_id": user_id})
        if not follow_up:
            raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
        
        # Obtener usuario
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Obtener el seguimiento ANTERIOR (el más reciente antes de este)
        previous_follow_up = await db.follow_up_submissions.find_one(
            {
                "user_id": user_id,
                "_id": {"$ne": followup_id},  # Excluir el actual
                "submission_date": {"$lt": follow_up.get("submission_date")}
            },
            sort=[("submission_date", -1)]  # El más reciente anterior
        )
        
        # Si no hay seguimiento anterior, es el PRIMER seguimiento
        # En ese caso, obtener el cuestionario INICIAL de nutrición para comparar
        initial_nutrition_questionnaire = None
        if not previous_follow_up:
            initial_nutrition_questionnaire = await db.nutrition_questionnaire_submissions.find_one(
                {"user_id": user_id},
                sort=[("submitted_at", 1)]  # El más antiguo (primer cuestionario)
            )
        
        # Obtener plan de nutrición previo
        previous_plan = await db.nutrition_plans.find_one(
            {"_id": follow_up.get("previous_plan_id")}
        )
        
        # Construir el prompt para el análisis
        prompt = f"""Eres un entrenador personal experto analizando el progreso de un cliente después de seguir un plan de nutrición.

**DATOS DEL CLIENTE:**
Nombre: {user.get('name', 'Cliente')}
Días desde el último plan: {follow_up.get('days_since_last_plan', 0)} días

**MEDICIONES ANTERIORES PARA COMPARACIÓN:**
"""
        
        if previous_follow_up and previous_follow_up.get('measurements'):
            # Hay seguimiento anterior - usar esos datos
            prev_measurements = previous_follow_up['measurements']
            prompt += f"""
(Del seguimiento anterior)
- Peso anterior: {prev_measurements.get('peso', 'N/A')} kg
- Tipo de medición: {previous_follow_up.get('measurement_type', 'N/A')}

**Medidas corporales anteriores:**
"""
            if prev_measurements.get('grasa_corporal'):
                prompt += f"- Grasa corporal: {prev_measurements.get('grasa_corporal')}%\n"
            if prev_measurements.get('masa_muscular'):
                prompt += f"- Masa muscular: {prev_measurements.get('masa_muscular')} kg\n"
            if prev_measurements.get('circunferencia_cintura'):
                prompt += f"- Cintura: {prev_measurements.get('circunferencia_cintura')} cm\n"
            if prev_measurements.get('circunferencia_pecho'):
                prompt += f"- Pecho: {prev_measurements.get('circunferencia_pecho')} cm\n"
            if prev_measurements.get('circunferencia_cadera'):
                prompt += f"- Cadera: {prev_measurements.get('circunferencia_cadera')} cm\n"
        elif initial_nutrition_questionnaire:
            # Es el PRIMER seguimiento - usar datos del cuestionario inicial
            responses = initial_nutrition_questionnaire.get('responses', {})
            prompt += f"""
(Del cuestionario inicial de nutrición - PRIMER SEGUIMIENTO)
- Peso inicial: {responses.get('peso', 'N/A')} kg
- Altura: {responses.get('altura_cm', 'N/A')} cm
- Tipo de medición: {responses.get('measurement_type', 'N/A')}

**Medidas corporales iniciales:**
"""
            if responses.get('grasa_porcentaje'):
                prompt += f"- Grasa corporal: {responses.get('grasa_porcentaje')}%\n"
            if responses.get('masa_muscular_porcentaje'):
                prompt += f"- Masa muscular: {responses.get('masa_muscular_porcentaje')}%\n"
            if responses.get('masa_osea_kg'):
                prompt += f"- Masa ósea: {responses.get('masa_osea_kg')} kg\n"
            if responses.get('agua_porcentaje'):
                prompt += f"- Agua corporal: {responses.get('agua_porcentaje')}%\n"
            if responses.get('cintura_cm'):
                prompt += f"- Cintura: {responses.get('cintura_cm')} cm\n"
            if responses.get('cadera_cm'):
                prompt += f"- Cadera: {responses.get('cadera_cm')} cm\n"
            if responses.get('pecho_cm'):
                prompt += f"- Pecho: {responses.get('pecho_cm')} cm\n"
            if responses.get('biceps_relajado_cm'):
                prompt += f"- Bíceps relajado: {responses.get('biceps_relajado_cm')} cm\n"
            if responses.get('muslo_cm'):
                prompt += f"- Muslo: {responses.get('muslo_cm')} cm\n"
        else:
            prompt += "\n(No se encontraron datos de referencia)\n"
        
        prompt += f"""

**SEGUIMIENTO ACTUAL (después de {follow_up.get('days_since_last_plan', 0)} días):**

**Tipo de medición:** {follow_up.get('measurement_type', 'N/A')}
"""
        
        # Agregar mediciones actuales si existen
        if follow_up.get('measurements'):
            measurements = follow_up['measurements']
            prompt += "\n**Mediciones actuales:**\n"
            if measurements.get('peso'): prompt += f"- Peso: {measurements['peso']} kg\n"
            if measurements.get('grasa_corporal'): prompt += f"- Grasa corporal: {measurements['grasa_corporal']}%\n"
            if measurements.get('masa_muscular'): prompt += f"- Masa muscular: {measurements['masa_muscular']} kg\n"
            if measurements.get('circunferencia_cintura'): prompt += f"- Cintura: {measurements['circunferencia_cintura']} cm\n"
            if measurements.get('circunferencia_pecho'): prompt += f"- Pecho: {measurements['circunferencia_pecho']} cm\n"
            if measurements.get('satisfecho_cambios'): prompt += f"- ¿Satisfecho con cambios?: {measurements['satisfecho_cambios']}\n"
        
        # Adherencia
        adherence = follow_up.get('adherence', {})
        prompt += f"""
**Adherencia al plan:**
- Constancia entrenamiento: {adherence.get('constancia_entrenamiento', 'N/A')}
- Seguimiento alimentación: {adherence.get('seguimiento_alimentacion', 'N/A')}
"""
        
        # Bienestar
        wellbeing = follow_up.get('wellbeing', {})
        prompt += f"""
**Bienestar general:**
- Energía, ánimo y motivación: {wellbeing.get('energia_animo_motivacion', 'N/A')}
- Sueño y estrés: {wellbeing.get('sueno_estres', 'N/A')}
"""
        if wellbeing.get('factores_externos'):
            prompt += f"- Factores externos: {wellbeing['factores_externos']}\n"
        
        # Cambios percibidos
        changes = follow_up.get('changes_perceived', {})
        prompt += f"""
**Cambios percibidos:**
- Molestias/dolor/lesión: {changes.get('molestias_dolor_lesion', 'N/A')}
- Cambios corporales: {changes.get('cambios_corporales', 'N/A')}
- Fuerza y rendimiento: {changes.get('fuerza_rendimiento', 'N/A')}
"""
        
        # Feedback
        feedback = follow_up.get('feedback', {})
        prompt += f"""
**Feedback del cliente:**
- Objetivo próximo mes: {feedback.get('objetivo_proximo_mes', 'N/A')}
- Cambios deseados: {feedback.get('cambios_deseados', 'N/A')}
"""
        if feedback.get('comentarios_adicionales'):
            prompt += f"- Comentarios adicionales: {feedback['comentarios_adicionales']}\n"
        
        prompt += """

**TU TAREA:**
Genera un análisis completo y motivador del progreso del cliente. Debe incluir:

1. **Felicitación y reconocimiento**: Empieza reconociendo el esfuerzo y destacando los logros positivos.

2. **Análisis de cambios físicos**: Compara las mediciones ANTERIORES vs ACTUALES. Si hay seguimiento previo, compara con ese. Si es el PRIMER seguimiento, compara con el cuestionario INICIAL de nutrición. SIEMPRE hay datos de referencia para comparar. Celebra mejoras o explica razones de forma constructiva si no hay cambios.

3. **Evaluación de adherencia**: Analiza cómo ha sido su constancia con el entrenamiento y alimentación. Da feedback positivo y constructivo.

4. **Bienestar y factores externos**: Considera cómo el sueño, estrés y otros factores pueden estar afectando sus resultados.

5. **Recomendaciones específicas**: Basándote en TODO lo anterior, recomienda ajustes concretos para el próximo mes:
   - ¿Debe cambiar calorías? (aumentar/mantener/reducir)
   - ¿Ajustar macronutrientes?
   - ¿Cambiar frecuencia de comidas?
   - ¿Incluir alimentos específicos?
   - ¿Modificar intensidad/volumen de entrenamiento?

6. **Motivación final**: Termina con un mensaje motivador y realista sobre qué esperar en el próximo mes.

**IMPORTANTE:**
- Sé empático y motivador, nunca crítico o desalentador
- Usa un tono cercano y profesional
- Sé específico en las recomendaciones
- SIEMPRE compara las mediciones anteriores (ya sea del seguimiento previo o del cuestionario inicial) con las actuales
- Muestra las diferencias explícitamente (ej: "Tu peso ha bajado de 85kg a 82kg, una pérdida de 3kg")
- Si es el primer seguimiento, menciona que estás comparando con las mediciones iniciales del cuestionario
- Adapta el análisis según la adherencia del cliente

Genera el análisis en español, con formato markdown para facilitar la lectura."""
        
        logger.info(f"Generating AI analysis for follow-up {followup_id} of user {user_id}")
        
        # Llamar a la IA usando OpenAI directamente
        from openai import AsyncOpenAI
        import os
        
        # Obtener la clave de OpenAI
        openai_key = os.environ.get('OPENAI_API_KEY')
        
        # Crear el cliente de OpenAI
        client = AsyncOpenAI(api_key=openai_key)
        
        # Llamar a la API de OpenAI GPT-4o
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un entrenador personal experto analizando el progreso de un cliente después de seguir un plan de nutrición."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000,
            timeout=120
        )
        
        ai_analysis = response.choices[0].message.content
        
        # Guardar el análisis en el seguimiento
        await db.follow_up_submissions.update_one(
            {"_id": followup_id},
            {
                "$set": {
                    "ai_analysis": ai_analysis,
                    "status": "analyzed",
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"AI analysis generated successfully for follow-up {followup_id}")
        
        return {
            "success": True,
            "analysis": ai_analysis,
            "message": "Análisis generado correctamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing follow-up with AI: {e}")
        raise HTTPException(status_code=500, detail=f"Error al analizar seguimiento: {str(e)}")


@api_router.get("/admin/follow-ups/pending")
async def get_pending_follow_ups(request: Request):
    """
    Admin obtiene todos los seguimientos pendientes de análisis
    """
    await require_admin(request)
    
    try:
        follow_ups = await db.follow_up_submissions.find(
            {"status": "pending_analysis"}
        ).sort("submission_date", -1).to_list(100)
        
        # Enriquecer con datos del usuario
        for follow_up in follow_ups:
            follow_up["id"] = str(follow_up["_id"])
            user = await db.users.find_one({"_id": follow_up["user_id"]})
            if user:
                follow_up["user_name"] = user.get("name", "Usuario")
                follow_up["user_email"] = user.get("email", "")
            
            # Convertir fechas
            if "submission_date" in follow_up:
                follow_up["submission_date"] = follow_up["submission_date"].isoformat()
        
        return {"pending_follow_ups": follow_ups, "count": len(follow_ups)}
        
    except Exception as e:
        logger.error(f"Error getting pending follow-ups: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener seguimientos pendientes: {str(e)}")


@api_router.patch("/admin/users/{user_id}/followups/{followup_id}/analysis")
async def update_follow_up_analysis(user_id: str, followup_id: str, analysis_data: dict, request: Request):
    """
    Admin actualiza/edita el análisis de un seguimiento
    """
    await require_admin(request)
    
    try:
        result = await db.follow_up_submissions.update_one(
            {"_id": followup_id, "user_id": user_id},
            {
                "$set": {
                    "ai_analysis": analysis_data.get("analysis"),
                    "ai_analysis_edited": True,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
        
        return {"success": True, "message": "Análisis actualizado correctamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Error al actualizar análisis: {str(e)}")


@api_router.post("/admin/users/{user_id}/followups/{followup_id}/generate-plan")
async def generate_plan_from_follow_up(user_id: str, followup_id: str, request: Request):
    """
    Genera un nuevo plan de nutrición basado en el análisis del seguimiento
    """
    await require_admin(request)
    
    try:
        # Obtener el seguimiento
        follow_up = await db.follow_up_submissions.find_one({"_id": followup_id, "user_id": user_id})
        if not follow_up:
            raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
        
        if not follow_up.get("ai_analysis"):
            raise HTTPException(status_code=400, detail="Debe analizar el seguimiento antes de generar un nuevo plan")
        
        # Obtener usuario y cuestionario inicial
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Obtener el cuestionario inicial (el primero del usuario)
        initial_questionnaire = await db.nutrition_questionnaire_submissions.find_one(
            {"user_id": user_id},
            sort=[("submitted_at", 1)]  # El más antiguo
        )
        
        if not initial_questionnaire:
            raise HTTPException(status_code=404, detail="Cuestionario inicial no encontrado")
        
        # Obtener el plan anterior para referencia
        previous_plan = await db.nutrition_plans.find_one(
            {"_id": follow_up.get("previous_plan_id")}
        )
        
        # Generar el nuevo plan usando el servicio de nutrición
        # Pasamos TODA la información necesaria
        from nutrition_service import generate_nutrition_plan_with_context
        
        result = await generate_nutrition_plan_with_context(
            questionnaire=initial_questionnaire,
            follow_up_analysis=follow_up.get("ai_analysis"),
            follow_up_data=follow_up,
            previous_plan=previous_plan
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Error generando plan"))
        
        # Guardar el nuevo plan con TODOS los campos necesarios
        plan_id = str(datetime.now(timezone.utc).timestamp()).replace('.', '')
        now = datetime.now(timezone.utc)
        
        nutrition_plan = {
            "_id": plan_id,
            "user_id": user_id,
            "month": now.month,
            "year": now.year,
            "plan_verificado": result["plan_verificado"],
            "plan_inicial": result.get("plan_inicial", ""),
            "questionnaire_data": initial_questionnaire,
            "generated_at": now,
            "uploaded_by": "admin",
            "generated_from_followup": followup_id,
            "previous_plan_id": follow_up.get("previous_plan_id"),
            "status": "active",
            "edited": False
        }
        
        await db.nutrition_plans.insert_one(nutrition_plan)
        
        # Actualizar el usuario con el nuevo plan
        await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "nutrition_plan": {
                        "id": plan_id,
                        "generated_at": datetime.now(timezone.utc),
                        "uploaded_by": "admin"
                    }
                }
            }
        )
        
        # Actualizar el seguimiento con el ID del nuevo plan
        await db.follow_up_submissions.update_one(
            {"_id": followup_id},
            {
                "$set": {
                    "new_plan_id": plan_id,
                    "status": "plan_generated",
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"New nutrition plan generated from follow-up {followup_id} for user {user_id}")
        
        return {
            "success": True,
            "plan_id": plan_id,
            "plan_content": result["plan_verificado"],
            "message": "Nuevo plan de nutrición generado correctamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating plan from follow-up: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar nuevo plan: {str(e)}")


@api_router.post("/admin/users/{user_id}/followups/{followup_id}/send-email")
async def send_followup_analysis_email(user_id: str, followup_id: str, request: Request):
    """Admin envía el análisis de seguimiento por email al cliente"""
    await require_admin(request)
    
    try:
        from email_utils import send_email
        import markdown
        
        # Obtener el seguimiento
        follow_up = await db.follow_up_submissions.find_one({"_id": followup_id, "user_id": user_id})
        if not follow_up:
            raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
        
        # Obtener usuario
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar que hay análisis
        analysis_content = follow_up.get("ai_analysis", "")
        if not analysis_content:
            raise HTTPException(
                status_code=400,
                detail="El seguimiento no tiene análisis. Por favor, genera el análisis primero."
            )
        
        submission_date = follow_up.get("submission_date")
        if isinstance(submission_date, str):
            submission_date = datetime.fromisoformat(submission_date.replace('Z', '+00:00'))
        
        month_name = submission_date.strftime("%B") if submission_date else "este mes"
        
        # Convertir markdown a HTML
        html_content = markdown.markdown(analysis_content, extensions=['nl2br', 'tables'])
        
        # Construir el email
        subject = f"Tu Análisis de Seguimiento - {month_name.capitalize()}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .analysis-box {{ background-color: white; padding: 25px; border-left: 4px solid #667eea; margin: 20px 0; border-radius: 5px; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #eee; color: #666; }}
                h1 {{ margin: 0; font-size: 28px; }}
                h2 {{ color: #667eea; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Tu Análisis de Progreso</h1>
                    <p style="margin: 10px 0 0 0; font-size: 18px;">Seguimiento de {month_name.capitalize()}</p>
                </div>
                <div class="content">
                    <p style="font-size: 16px;">Hola <strong>{user.get('name', 'Cliente')}</strong>,</p>
                    <p>He revisado tu cuestionario de seguimiento y aquí está mi análisis detallado de tu progreso:</p>
                    
                    <div class="analysis-box">
                        {html_content}
                    </div>
                    
                    <p style="margin-top: 25px;">Si tienes alguna duda sobre este análisis o quieres comentar algo, no dudes en contactarme.</p>
                    <p>¡Sigamos trabajando juntos para alcanzar tus objetivos!</p>
                    
                    <div class="footer">
                        <p><strong>Jorge Calcerrada</strong><br>
                        Entrenador Personal</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Enviar el email
        success = send_email(
            to_email=user.get('email'),
            subject=subject,
            html_body=html_body
        )
        
        if success:
            logger.info(f"Follow-up analysis email sent to {user.get('email')} for followup {followup_id}")
            return {
                "success": True,
                "message": f"Análisis enviado correctamente a {user.get('email')}"
            }
        else:
            raise HTTPException(
                status_code=500,
                detail="Error al enviar el email. Verifica la configuración SMTP."
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending follow-up analysis email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error enviando email: {str(e)}"
        )


@api_router.post("/admin/users/{user_id}/followups/{followup_id}/send-whatsapp")
async def send_followup_analysis_whatsapp(user_id: str, followup_id: str, request: Request):
    """Admin envía el análisis de seguimiento por WhatsApp al cliente"""
    await require_admin(request)
    
    try:
        # Obtener el seguimiento
        follow_up = await db.follow_up_submissions.find_one({"_id": followup_id, "user_id": user_id})
        if not follow_up:
            raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
        
        # Obtener usuario
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar que hay análisis
        analysis_content = follow_up.get("ai_analysis", "")
        if not analysis_content:
            raise HTTPException(
                status_code=400,
                detail="El seguimiento no tiene análisis. Por favor, genera el análisis primero."
            )
        
        # Obtener teléfono del usuario
        phone = user.get('telefono') or user.get('phone')
        if not phone:
            raise HTTPException(
                status_code=400,
                detail="El usuario no tiene teléfono registrado"
            )
        
        submission_date = follow_up.get("submission_date")
        if isinstance(submission_date, str):
            submission_date = datetime.fromisoformat(submission_date.replace('Z', '+00:00'))
        
        month_name = submission_date.strftime("%B") if submission_date else "este mes"
        
        # Construir el mensaje para WhatsApp (texto plano, sin HTML)
        message = f"""Hola {user.get('name', 'Cliente')} 👋

📊 *Tu Análisis de Progreso - {month_name.capitalize()}*

He revisado tu cuestionario de seguimiento y aquí está mi análisis:

{analysis_content}

Si tienes alguna duda, no dudes en escribirme.

¡Sigamos trabajando juntos! 💪

Jorge Calcerrada
Entrenador Personal"""
        
        # Crear URL de WhatsApp
        import urllib.parse
        whatsapp_url = f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"
        
        logger.info(f"WhatsApp URL generated for follow-up {followup_id} to user {user_id}")
        
        return {
            "success": True,
            "whatsapp_url": whatsapp_url,
            "message": "URL de WhatsApp generada correctamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating WhatsApp URL for follow-up: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando WhatsApp: {str(e)}"
        )


@api_router.post("/admin/users/{user_id}/followups/{followup_id}/generate-pdf")
async def generate_followup_analysis_pdf(user_id: str, followup_id: str, request: Request):
    """Admin genera PDF del análisis de seguimiento"""
    await require_admin(request)
    
    try:
        # Obtener el seguimiento
        follow_up = await db.follow_up_submissions.find_one({"_id": followup_id, "user_id": user_id})
        if not follow_up:
            raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
        
        # Obtener usuario
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Verificar que hay análisis
        analysis_content = follow_up.get("ai_analysis", "")
        if not analysis_content:
            raise HTTPException(
                status_code=400,
                detail="El seguimiento no tiene análisis. Por favor, genera el análisis primero."
            )
        
        submission_date = follow_up.get("submission_date")
        if isinstance(submission_date, str):
            submission_date = datetime.fromisoformat(submission_date.replace('Z', '+00:00'))
        
        month_name = submission_date.strftime("%B") if submission_date else "Seguimiento"
        year = submission_date.strftime("%Y") if submission_date else ""
        
        # Convertir markdown a HTML
        import markdown
        html_content = markdown.markdown(analysis_content, extensions=['nl2br', 'tables'])
        
        # Crear HTML completo para el PDF
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    padding-bottom: 20px;
                    border-bottom: 3px solid #667eea;
                }}
                .header h1 {{
                    color: #667eea;
                    font-size: 28px;
                    margin-bottom: 10px;
                }}
                .header .subtitle {{
                    font-size: 18px;
                    color: #666;
                }}
                .client-info {{
                    background-color: #f5f5f5;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 25px;
                }}
                .content {{
                    margin-top: 20px;
                }}
                h2 {{
                    color: #667eea;
                    margin-top: 25px;
                    border-bottom: 2px solid #eee;
                    padding-bottom: 10px;
                }}
                h3 {{
                    color: #555;
                    margin-top: 20px;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 2px solid #eee;
                    text-align: center;
                    color: #666;
                    font-size: 14px;
                }}
                strong {{
                    color: #667eea;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Análisis de Progreso</h1>
                <div class="subtitle">Seguimiento de {month_name.capitalize()} {year}</div>
            </div>
            
            <div class="client-info">
                <strong>Cliente:</strong> {user.get('name', 'Cliente')}<br>
                <strong>Fecha de análisis:</strong> {datetime.now(timezone.utc).strftime("%d de %B de %Y")}
            </div>
            
            <div class="content">
                {html_content}
            </div>
            
            <div class="footer">
                <strong>Jorge Calcerrada</strong><br>
                Entrenador Personal
            </div>
        </body>
        </html>
        """
        
        # Generar PDF usando WeasyPrint
        from weasyprint import HTML
        import io
        
        pdf_buffer = io.BytesIO()
        HTML(string=html_template).write_pdf(pdf_buffer)
        pdf_buffer.seek(0)
        pdf_content = pdf_buffer.read()
        
        # Guardar el PDF en la base de datos
        pdf_id = str(datetime.now(timezone.utc).timestamp()).replace('.', '')
        pdf_title = f"Análisis de Seguimiento - {month_name.capitalize()} {year}"
        
        # Create standardized PDF document
        pdf_id = await create_pdf_document(
            user_id=user_id,
            title=pdf_title,
            content=pdf_content,
            pdf_type="follow_up_analysis",
            related_id=followup_id,
            filename=f"{pdf_title}.pdf"
        )
        
        logger.info(f"Follow-up analysis PDF generated: {pdf_id} for user {user_id}")
        
        return {
            "success": True,
            "pdf_id": pdf_id,
            "message": "PDF del análisis generado correctamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating follow-up analysis PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generando PDF: {str(e)}"
        )


@api_router.get("/admin/pending-reviews")
async def get_pending_reviews(request: Request):
    """
    Admin obtiene lista de clientes que necesitan revisión de seguimiento
    (>= 30 días desde último plan y no han completado seguimiento)
    """
    await require_admin(request)
    
    try:
        pending_reviews = []
        
        # Obtener todos los clientes team con plan de nutrición
        team_clients = await db.users.find({
            "subscription.plan": "team",
            "nutrition_plan": {"$exists": True}
        }).to_list(1000)
        
        for client in team_clients:
            # Calcular días desde el último plan
            if client.get("nutrition_plan") and client["nutrition_plan"].get("generated_at"):
                plan_date = client["nutrition_plan"]["generated_at"]
                days_since_plan = (datetime.now(timezone.utc) - plan_date).days
                
                if days_since_plan >= 30:
                    # Verificar si tiene seguimiento completado reciente
                    recent_followup = await db.follow_up_submissions.find_one({
                        "user_id": client["_id"],
                        "submission_date": {"$gte": plan_date}
                    })
                    
                    # Determinar estado
                    if recent_followup:
                        status = "completed"
                        status_date = recent_followup["submission_date"]
                    elif client.get("followup_activated"):
                        status = "activated"
                        status_date = client.get("followup_activated_at")
                    else:
                        status = "pending"
                        status_date = None
                    
                    pending_reviews.append({
                        "user_id": client["_id"],
                        "name": client.get("name", "Usuario"),
                        "email": client.get("email"),
                        "phone": client.get("phone"),
                        "days_since_plan": days_since_plan,
                        "last_plan_date": plan_date.isoformat(),
                        "status": status,
                        "status_date": status_date.isoformat() if status_date else None,
                        "followup_activated": client.get("followup_activated", False),
                        "last_followup_id": recent_followup["_id"] if recent_followup else None
                    })
        
        # Ordenar por días transcurridos (más urgentes primero)
        pending_reviews.sort(key=lambda x: x["days_since_plan"], reverse=True)
        
        return {
            "pending_reviews": pending_reviews,
            "count": len(pending_reviews)
        }
        
    except Exception as e:
        logger.error(f"Error getting pending reviews: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener revisiones pendientes: {str(e)}")


@api_router.post("/admin/users/{user_id}/activate-followup")
async def activate_followup(user_id: str, request: Request):
    """
    Admin activa el cuestionario de seguimiento para un cliente específico
    """
    await require_admin(request)
    
    try:
        # Actualizar usuario para activar el cuestionario
        result = await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "followup_activated": True,
                    "followup_activated_at": datetime.now(timezone.utc),
                    "followup_activated_by": "admin"
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        logger.info(f"Follow-up activated for user {user_id} by admin")
        
        return {
            "success": True,
            "message": "Cuestionario de seguimiento activado correctamente"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error activating follow-up: {e}")
        raise HTTPException(status_code=500, detail=f"Error al activar cuestionario: {str(e)}")


@api_router.post("/admin/users/{user_id}/deactivate-followup")
async def deactivate_followup(user_id: str, request: Request):
    """
    Admin desactiva el cuestionario de seguimiento (por si se activó por error)
    """
    await require_admin(request)
    
    try:
        result = await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "followup_activated": False,
                    "followup_activated_at": None,
                    "followup_activated_by": None
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        logger.info(f"Follow-up deactivated for user {user_id} by admin")
        
        return {
            "success": True,
            "message": "Cuestionario de seguimiento desactivado"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deactivating follow-up: {e}")
        raise HTTPException(status_code=500, detail=f"Error al desactivar cuestionario: {str(e)}")

# ============================================
# STRIPE PAYMENT & SUBSCRIPTION ENDPOINTS
# ============================================

# Planes de suscripción (FIJO EN BACKEND - NO MODIFICABLE DESDE FRONTEND)
SUBSCRIPTION_PLANS = {
    "monthly": {
        "amount": 49.9,
        "currency": "eur",
        "name": "Plan Mensual",
        "billing_period": "monthly"
    }
}

@api_router.post("/stripe/create-subscription-session")
async def create_subscription_session(
    request: Request,
    subscription_data: StripeSubscriptionCreate,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Crea una sesión de pago de Stripe para suscripción
    SEGURIDAD: Monto definido en backend, no aceptado desde frontend
    """
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest
        import uuid
        
        # Obtener usuario (el _id es un string, no un ObjectId)
        user = await db.users.find_one({"_id": current_user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Validar plan seleccionado
        if subscription_data.plan_type not in SUBSCRIPTION_PLANS:
            raise HTTPException(status_code=400, detail="Plan de suscripción inválido")
        
        plan = SUBSCRIPTION_PLANS[subscription_data.plan_type]
        
        # Obtener host URL desde el frontend
        origin_url = str(request.headers.get("origin", os.environ.get("FRONTEND_URL", "")))
        
        # Construir URLs de éxito y cancelación
        # Usar {CHECKOUT_SESSION_ID} sin las dobles llaves para que Stripe lo reemplace correctamente
        success_url = f"{origin_url}/subscription-success?session_id=" + "{CHECKOUT_SESSION_ID}"
        cancel_url = f"{origin_url}/dashboard"
        
        # Inicializar Stripe Checkout
        api_key = os.environ.get("STRIPE_API_KEY")
        webhook_url = f"{origin_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        # Metadata para identificar el pago
        metadata = {
            "user_id": current_user_id,
            "user_email": user.get("email"),
            "plan_type": subscription_data.plan_type,
            "payment_type": "subscription"
        }
        
        # Crear checkout session
        checkout_request = CheckoutSessionRequest(
            amount=plan["amount"],
            currency=plan["currency"],
            success_url=success_url,
            cancel_url=cancel_url,
            metadata=metadata
        )
        
        session_response = await stripe_checkout.create_checkout_session(checkout_request)
        
        # Generar transaction_id único
        transaction_id = str(uuid.uuid4())
        
        # Crear registro de transacción PENDIENTE
        payment_transaction = {
            "transaction_id": transaction_id,
            "user_id": current_user_id,
            "user_email": user.get("email"),
            "session_id": session_response.session_id,
            "payment_status": "pending",
            "amount": plan["amount"],
            "currency": plan["currency"],
            "subscription_id": None,  # Se asignará después del pago exitoso
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.payment_transactions.insert_one(payment_transaction)
        
        logger.info(f"Stripe checkout session created: {session_response.session_id} for user {current_user_id}")
        
        return {
            "checkout_url": session_response.url,
            "session_id": session_response.session_id,
            "transaction_id": transaction_id
        }
        
    except Exception as e:
        logger.error(f"Error creating Stripe checkout session: {e}")
        raise HTTPException(status_code=500, detail=f"Error al crear sesión de pago: {str(e)}")


@api_router.get("/stripe/checkout-status/{session_id}")
async def get_checkout_status(
    session_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Verifica el estado de una sesión de checkout de Stripe
    Se usa para polling desde el frontend después del pago
    """
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        logger.info(f"Checking checkout status for session: {session_id}")
        
        # Inicializar Stripe Checkout
        api_key = os.environ.get("STRIPE_API_KEY")
        frontend_url = os.environ.get("FRONTEND_URL", "https://exerule-system.preview.emergentagent.com")
        webhook_url = f"{frontend_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        # Obtener estado del checkout
        logger.info(f"Calling Stripe API to get checkout status...")
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        logger.info(f"Stripe API returned: payment_status={checkout_status.payment_status}, status={checkout_status.status}")
        
        # Buscar transacción en DB
        transaction = await db.payment_transactions.find_one({"session_id": session_id})
        
        if not transaction:
            logger.error(f"Transaction not found for session_id: {session_id}")
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        
        logger.info(f"Transaction found: payment_status={transaction.get('payment_status')}, user_id={transaction.get('user_id')}")
        
        # Solo procesar si el pago fue exitoso y aún no se ha procesado
        logger.info(f"Checking conditions: checkout_status.payment_status={checkout_status.payment_status}, transaction payment_status={transaction['payment_status']}")
        
        if checkout_status.payment_status == "paid" and transaction["payment_status"] != "succeeded":
            
            # Actualizar transacción
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {
                    "$set": {
                        "payment_status": "succeeded",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            # Crear/Actualizar suscripción del usuario
            subscription_id = str(uuid.uuid4())
            plan_type = transaction["metadata"].get("plan_type", "monthly")
            
            user_subscription = {
                "subscription_id": subscription_id,
                "user_id": transaction["user_id"],
                "user_email": transaction["user_email"],
                "stripe_session_id": session_id,
                "plan_type": plan_type,
                "status": "active",
                "amount": transaction["amount"],
                "currency": transaction["currency"],
                "start_date": datetime.now(timezone.utc).isoformat(),
                "next_billing_date": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Insertar o actualizar suscripción
            existing_subscription = await db.user_subscriptions.find_one({"user_id": transaction["user_id"], "status": "active"})
            
            if existing_subscription:
                # Actualizar suscripción existente
                await db.user_subscriptions.update_one(
                    {"user_id": transaction["user_id"], "status": "active"},
                    {"$set": user_subscription}
                )
            else:
                # Crear nueva suscripción
                await db.user_subscriptions.insert_one(user_subscription)
            
            # Actualizar transaction con subscription_id
            await db.payment_transactions.update_one(
                {"session_id": session_id},
                {"$set": {"subscription_id": subscription_id}}
            )
            
            # Actualizar usuario - marcar como ACTIVO con suscripción activa (_id es string)
            await db.users.update_one(
                {"_id": transaction["user_id"]},
                {
                    "$set": {
                        "status": "active",  # Cambiar de inactive a active
                        "subscription.status": "active",
                        "subscription.plan": "team",  # El plan mensual incluye acceso completo al equipo
                        "subscription.payment_status": "verified",
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            logger.info(f"Payment succeeded and subscription activated for user {transaction['user_id']}")
        
        return {
            "session_id": session_id,
            "payment_status": checkout_status.payment_status,
            "status": checkout_status.status,
            "amount_total": checkout_status.amount_total,
            "currency": checkout_status.currency,
            "transaction_status": transaction.get("payment_status", "pending")
        }
        
    except Exception as e:
        logger.error(f"Error checking checkout status: {e}")
        raise HTTPException(status_code=500, detail=f"Error al verificar estado del pago: {str(e)}")


@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    """
    Webhook de Stripe para recibir eventos de pago
    """
    try:
        from emergentintegrations.payments.stripe.checkout import StripeCheckout
        
        # Leer el body del webhook
        body = await request.body()
        signature = request.headers.get("Stripe-Signature")
        
        # Inicializar Stripe Checkout
        api_key = os.environ.get("STRIPE_API_KEY")
        frontend_url = os.environ.get("FRONTEND_URL", "https://exerule-system.preview.emergentagent.com")
        webhook_url = f"{frontend_url}/api/webhook/stripe"
        stripe_checkout = StripeCheckout(api_key=api_key, webhook_url=webhook_url)
        
        # Procesar webhook
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        logger.info(f"Stripe webhook received: {webhook_response.event_type} - Session: {webhook_response.session_id}")
        
        # Actualizar transacción según el evento
        if webhook_response.event_type == "checkout.session.completed":
            if webhook_response.payment_status == "paid":
                await db.payment_transactions.update_one(
                    {"session_id": webhook_response.session_id},
                    {
                        "$set": {
                            "payment_status": "succeeded",
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    }
                )
        
        return {"status": "success", "event": webhook_response.event_type}
        
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {e}")
        return {"status": "error", "message": str(e)}


@api_router.get("/stripe/my-subscription")
async def get_user_subscription(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Obtiene la suscripción activa del usuario actual
    """
    try:
        subscription = await db.user_subscriptions.find_one({
            "user_id": current_user_id,
            "status": "active"
        })
        
        if not subscription:
            return {"has_subscription": False, "subscription": None}
        
        # Limpiar ObjectId si existe
        if "_id" in subscription:
            del subscription["_id"]
        
        return {
            "has_subscription": True,
            "subscription": subscription
        }
        
    except Exception as e:
        logger.error(f"Error getting user subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener suscripción: {str(e)}")


@api_router.get("/stripe/my-payments")
async def get_user_payments(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Obtiene el historial de pagos del usuario actual
    """
    try:
        payments_cursor = db.payment_transactions.find({
            "user_id": current_user_id,
            "payment_status": "succeeded"
        }).sort("created_at", -1)
        
        payments = await payments_cursor.to_list(length=100)
        
        # Limpiar ObjectId
        for payment in payments:
            if "_id" in payment:
                del payment["_id"]
        
        return {"payments": payments, "count": len(payments)}
        
    except Exception as e:
        logger.error(f"Error getting user payments: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener historial de pagos: {str(e)}")


@api_router.post("/stripe/cancel-subscription")
async def cancel_user_subscription(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Cancela la suscripción activa del usuario
    """
    try:
        # Buscar suscripción activa
        subscription = await db.user_subscriptions.find_one({
            "user_id": current_user_id,
            "status": "active"
        })
        
        if not subscription:
            raise HTTPException(status_code=404, detail="No tienes una suscripción activa")
        
        # Actualizar suscripción a cancelada
        await db.user_subscriptions.update_one(
            {"subscription_id": subscription["subscription_id"]},
            {
                "$set": {
                    "status": "cancelled",
                    "cancelled_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Actualizar usuario (_id es un string)
        await db.users.update_one(
            {"_id": current_user_id},
            {
                "$set": {
                    "subscription.status": "cancelled",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        logger.info(f"Subscription cancelled for user {current_user_id}")
        
        return {
            "success": True,
            "message": "Suscripción cancelada exitosamente",
            "cancelled_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cancelling subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Error al cancelar suscripción: {str(e)}")


@api_router.post("/admin/cancel-subscription/{user_id}")
async def admin_cancel_user_subscription(
    user_id: str,
    request: Request = None
):
    """
    Admin cancela la suscripción de un cliente específico
    """
    await require_admin(request)
    
    try:
        # Buscar suscripción activa del cliente
        subscription = await db.user_subscriptions.find_one({
            "user_id": user_id,
            "status": "active"
        })
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Este cliente no tiene una suscripción activa")
        
        # Actualizar suscripción a cancelada
        await db.user_subscriptions.update_one(
            {"subscription_id": subscription["subscription_id"]},
            {
                "$set": {
                    "status": "cancelled",
                    "cancelled_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Actualizar usuario
        await db.users.update_one(
            {"_id": user_id},
            {
                "$set": {
                    "subscription.status": "cancelled",
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        logger.info(f"Admin cancelled subscription for user {user_id}")
        
        return {
            "success": True,
            "message": "Suscripción del cliente cancelada exitosamente",
            "user_id": user_id,
            "cancelled_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error cancelling subscription for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al cancelar suscripción: {str(e)}")


@api_router.post("/admin/refund-payment/{payment_id}")
async def admin_refund_payment(
    payment_id: str,
    request: Request = None
):
    """
    Admin marca un pago como devuelto (refund)
    """
    await require_admin(request)
    
    try:
        # Buscar el pago
        payment = await db.payment_transactions.find_one({"_id": payment_id})
        
        if not payment:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        # Marcar como devuelto
        await db.payment_transactions.update_one(
            {"_id": payment_id},
            {
                "$set": {
                    "payment_status": "refunded",
                    "refunded_at": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        logger.info(f"Admin refunded payment {payment_id}")
        
        return {
            "success": True,
            "message": "Pago marcado como devuelto",
            "payment_id": payment_id,
            "refunded_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error refunding payment {payment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al devolver pago: {str(e)}")


@api_router.get("/admin/generate-invoice/{payment_id}")
async def admin_generate_invoice(
    payment_id: str,
    request: Request = None
):
    """
    Admin genera una factura para un pago específico
    """
    await require_admin(request)
    
    try:
        # Buscar el pago
        payment = await db.payment_transactions.find_one({"_id": payment_id})
        
        if not payment:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        # Buscar información del usuario
        user = await db.users.find_one({"_id": payment.get("user_id")})
        
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Generar número de factura único
        invoice_number = f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{payment_id[:8].upper()}"
        
        # Crear documento de factura
        invoice_data = {
            "invoice_number": invoice_number,
            "payment_id": payment_id,
            "user_id": payment.get("user_id"),
            "user_name": user.get("name", user.get("username", "Cliente")),
            "user_email": user.get("email"),
            "amount": payment.get("amount", 0),
            "payment_date": payment.get("created_at"),
            "payment_method": payment.get("payment_method", "Stripe"),
            "concept": payment.get("concept", "Suscripción E.D.N.360"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "status": "paid"
        }
        
        logger.info(f"Invoice generated for payment {payment_id}: {invoice_number}")
        
        return {
            "success": True,
            "invoice": invoice_data
        }
        
    except Exception as e:
        logger.error(f"Error generating invoice for payment {payment_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al generar factura: {str(e)}")


# ============================================
# ADMIN - FINANCIAL OVERVIEW ENDPOINTS
# ============================================

@api_router.get("/admin/financial-overview")
async def get_financial_overview(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Obtiene métricas financieras completas para el admin
    """
    try:
        # Verificar que es admin (_id es un string)
        user = await db.users.find_one({"_id": current_user_id})
        if not user or user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        # Calcular fechas de referencia
        now = datetime.now(timezone.utc)
        start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc)
        start_of_year = datetime(now.year, 1, 1, tzinfo=timezone.utc)
        
        # OPTIMIZED: Use aggregation pipelines to calculate server-side (no loading all data into memory)
        
        # Total revenue from payment_transactions (succeeded only)
        total_revenue_pipeline = [
            {"$match": {"payment_status": "succeeded"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        total_revenue_result = await db.payment_transactions.aggregate(total_revenue_pipeline).to_list(length=1)
        total_revenue = total_revenue_result[0]["total"] if total_revenue_result else 0
        
        # Count successful payments
        successful_count = await db.payment_transactions.count_documents({"payment_status": "succeeded"})
        
        # Monthly revenue from payment_transactions
        monthly_revenue_pipeline = [
            {"$match": {"payment_status": "succeeded", "created_at": {"$gte": start_of_month.isoformat()}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        monthly_revenue_result = await db.payment_transactions.aggregate(monthly_revenue_pipeline).to_list(length=1)
        monthly_revenue = monthly_revenue_result[0]["total"] if monthly_revenue_result else 0
        
        # Annual revenue from payment_transactions
        annual_revenue_pipeline = [
            {"$match": {"payment_status": "succeeded", "created_at": {"$gte": start_of_year.isoformat()}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        annual_revenue_result = await db.payment_transactions.aggregate(annual_revenue_pipeline).to_list(length=1)
        annual_revenue = annual_revenue_result[0]["total"] if annual_revenue_result else 0
        
        # MANUAL PAYMENTS - Total revenue
        manual_total_pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        manual_total_result = await db.manual_payments.aggregate(manual_total_pipeline).to_list(length=1)
        total_manual_revenue = manual_total_result[0]["total"] if manual_total_result else 0
        total_revenue += total_manual_revenue
        
        # MANUAL PAYMENTS - Monthly revenue
        manual_monthly_pipeline = [
            {"$match": {"fecha": {"$gte": start_of_month}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        manual_monthly_result = await db.manual_payments.aggregate(manual_monthly_pipeline).to_list(length=1)
        monthly_manual_revenue = manual_monthly_result[0]["total"] if manual_monthly_result else 0
        monthly_revenue += monthly_manual_revenue
        
        # MANUAL PAYMENTS - Annual revenue
        manual_annual_pipeline = [
            {"$match": {"fecha": {"$gte": start_of_year}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        manual_annual_result = await db.manual_payments.aggregate(manual_annual_pipeline).to_list(length=1)
        annual_manual_revenue = manual_annual_result[0]["total"] if manual_annual_result else 0
        annual_revenue += annual_manual_revenue
        
        # Count manual payments
        manual_payments_count = await db.manual_payments.count_documents({})
        
        # Suscripciones activas y canceladas
        active_subscriptions = await db.user_subscriptions.count_documents({"status": "active"})
        cancelled_subscriptions = await db.user_subscriptions.count_documents({"status": "cancelled"})
        
        # MRR (Monthly Recurring Revenue) - suma de todas las suscripciones activas usando aggregation
        mrr_pipeline = [
            {"$match": {"status": "active"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        mrr_result = await db.user_subscriptions.aggregate(mrr_pipeline).to_list(length=1)
        mrr = mrr_result[0]["total"] if mrr_result else 0
        
        # Total transacciones
        total_transactions = await db.payment_transactions.count_documents({})
        failed_payments = await db.payment_transactions.count_documents({"payment_status": "failed"})
        
        metrics = {
            "total_revenue": round(total_revenue, 2),
            "monthly_revenue": round(monthly_revenue, 2),
            "annual_revenue": round(annual_revenue, 2),
            "active_subscriptions": active_subscriptions,
            "cancelled_subscriptions": cancelled_subscriptions,
            "total_transactions": total_transactions,
            "successful_payments": successful_count,
            "failed_payments": failed_payments,
            "mrr": round(mrr, 2),
            # Nuevas métricas para pagos manuales
            "manual_payments_count": manual_payments_count,
            "manual_payments_total": round(total_manual_revenue, 2),
            "manual_payments_monthly": round(monthly_manual_revenue, 2),
            "manual_payments_annual": round(annual_manual_revenue, 2)
        }
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting financial overview: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas financieras: {str(e)}")


@api_router.get("/admin/all-payments")
async def get_all_payments(
    current_user_id: str = Depends(get_current_user_id),
    status: Optional[str] = None,
    limit: int = 100
):
    """
    Obtiene todos los pagos del sistema para el admin con filtros opcionales
    """
    try:
        # Verificar que es admin (_id es un string)
        user = await db.users.find_one({"_id": current_user_id})
        if not user or user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        # Construir query con filtros
        query = {}
        if status:
            query["payment_status"] = status
        
        # Obtener pagos
        payments_cursor = db.payment_transactions.find(query).sort("created_at", -1).limit(limit)
        payments = await payments_cursor.to_list(length=limit)
        
        # Enriquecer con datos de usuario
        enriched_payments = []
        for payment in payments:
            # Buscar usuario
            user_data = await db.users.find_one({"_id": payment["user_id"]})
            
            payment_item = {
                "transaction_id": payment["transaction_id"],
                "date": payment["created_at"],
                "amount": payment["amount"],
                "currency": payment["currency"],
                "status": payment["payment_status"],
                "user_name": user_data.get("name", "Usuario Desconocido") if user_data else "Usuario Desconocido",
                "user_email": payment["user_email"],
                "session_id": payment.get("session_id"),
                "subscription_id": payment.get("subscription_id")
            }
            enriched_payments.append(payment_item)
        
        return {
            "payments": enriched_payments,
            "count": len(enriched_payments),
            "filter_applied": status if status else "none"
        }
        
    except Exception as e:
        logger.error(f"Error getting all payments: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener pagos: {str(e)}")


@api_router.get("/admin/client-subscription/{user_id}")
async def get_client_subscription(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Obtiene la suscripción de un cliente específico (admin only)
    """
    try:
        # Verificar que es admin (_id es un string)
        user = await db.users.find_one({"_id": current_user_id})
        if not user or user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        # Buscar suscripción del cliente
        subscription = await db.user_subscriptions.find_one({"user_id": user_id})
        
        if not subscription:
            return {"has_subscription": False, "subscription": None}
        
        # Limpiar ObjectId
        if "_id" in subscription:
            del subscription["_id"]
        
        # Obtener historial de pagos del cliente
        payments = await db.payment_transactions.find({
            "user_id": user_id,
            "payment_status": "succeeded"
        }).sort("created_at", -1).to_list(length=50)
        
        for payment in payments:
            if "_id" in payment:
                del payment["_id"]
        
        return {
            "has_subscription": True,
            "subscription": subscription,
            "payments": payments,
            "payments_count": len(payments)
        }
        
    except Exception as e:
        logger.error(f"Error getting client subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener suscripción del cliente: {str(e)}")


@api_router.delete("/admin/payment/{transaction_id}")
async def delete_payment_transaction(
    transaction_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Borra una transacción de pago específica (admin only)
    """
    try:
        # Verificar que es admin
        user = await db.users.find_one({"_id": current_user_id})
        if not user or user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        # Borrar la transacción
        result = await db.payment_transactions.delete_one({"transaction_id": transaction_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        
        logger.info(f"Payment transaction deleted: {transaction_id} by admin {current_user_id}")
        
        return {
            "success": True,
            "message": "Transacción eliminada exitosamente",
            "transaction_id": transaction_id
        }
        
    except Exception as e:
        logger.error(f"Error deleting payment transaction: {e}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar transacción: {str(e)}")


@api_router.delete("/admin/payments/cleanup")
async def cleanup_pending_payments(
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Limpia todas las transacciones con estado 'pending' (admin only)
    Útil para limpiar transacciones de prueba fallidas
    """
    try:
        # Verificar que es admin
        user = await db.users.find_one({"_id": current_user_id})
        if not user or user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Acceso denegado")
        
        # Borrar todas las transacciones pending
        result = await db.payment_transactions.delete_many({"payment_status": "pending"})
        
        logger.info(f"Cleaned up {result.deleted_count} pending payment transactions by admin {current_user_id}")
        
        return {
            "success": True,
            "message": f"Se eliminaron {result.deleted_count} transacciones pendientes",
            "deleted_count": result.deleted_count
        }
        
    except Exception as e:
        logger.error(f"Error cleaning up pending payments: {e}")
        raise HTTPException(status_code=500, detail=f"Error al limpiar transacciones: {str(e)}")

        
        return {
            "has_subscription": True,
            "subscription": subscription,
            "payments": payments,
            "payments_count": len(payments)
        }
        
    except Exception as e:
        logger.error(f"Error getting client subscription: {e}")
        raise HTTPException(status_code=500, detail=f"Error al obtener suscripción del cliente: {str(e)}")


# ==================== EXERCISE DATABASE ENDPOINTS ====================

@api_router.get("/exercises/all", response_model=List[ExerciseResponse])
async def get_all_exercises(request: Request):
    """Get all exercises from the database (requires authentication)"""
    await get_current_user(request)
    
    try:
        exercises = await db.exercises.find().to_list(length=1000)
        
        for exercise in exercises:
            exercise["id"] = exercise["_id"]
        
        return exercises
    
    except Exception as e:
        logger.error(f"Error fetching exercises: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener ejercicios")


@api_router.post("/exercises/query", response_model=List[ExerciseResponse])
async def query_exercises(query: ExerciseQuery, request: Request):
    """Query exercises by muscle group, difficulty, location, or equipment"""
    await get_current_user(request)
    
    try:
        # Build MongoDB query
        mongo_query = {}
        
        if query.grupo_muscular:
            # Search in both primary and secondary muscle groups
            mongo_query["$or"] = [
                {"grupo_muscular_principal": {"$regex": query.grupo_muscular, "$options": "i"}},
                {"grupo_muscular_secundario": {"$regex": query.grupo_muscular, "$options": "i"}}
            ]
        
        if query.nivel_dificultad:
            mongo_query["nivel_dificultad"] = {"$regex": query.nivel_dificultad, "$options": "i"}
        
        if query.lugar_entrenamiento:
            mongo_query["lugar_entrenamiento"] = {"$regex": query.lugar_entrenamiento, "$options": "i"}
        
        if query.material_disponible:
            # Match exercises that can be done with available equipment
            material_conditions = []
            for material in query.material_disponible:
                material_conditions.append({"material_necesario": {"$regex": material, "$options": "i"}})
            if material_conditions:
                mongo_query["$or"] = material_conditions
        
        exercises = await db.exercises.find(mongo_query).to_list(length=1000)
        
        for exercise in exercises:
            exercise["id"] = exercise["_id"]
        
        logger.info(f"Found {len(exercises)} exercises matching query")
        
        return exercises
    
    except Exception as e:
        logger.error(f"Error querying exercises: {e}")
        raise HTTPException(status_code=500, detail="Error al buscar ejercicios")


@api_router.get("/exercises/by-muscle-group/{muscle_group}", response_model=List[ExerciseResponse])
async def get_exercises_by_muscle_group(muscle_group: str, request: Request):
    """Get exercises by muscle group (e.g., 'Pectoral', 'Biceps', 'Espalda')"""
    await get_current_user(request)
    
    try:
        exercises = await db.exercises.find({
            "$or": [
                {"grupo_muscular_principal": {"$regex": muscle_group, "$options": "i"}},
                {"grupo_muscular_secundario": {"$regex": muscle_group, "$options": "i"}}
            ]
        }).to_list(length=1000)
        
        for exercise in exercises:
            exercise["id"] = exercise["_id"]
        
        return exercises
    
    except Exception as e:
        logger.error(f"Error fetching exercises by muscle group: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener ejercicios por grupo muscular")


@api_router.get("/exercises/stats")
async def get_exercise_stats(request: Request):
    """Get statistics about the exercise database"""
    await get_current_user(request)
    
    try:
        total = await db.exercises.count_documents({})
        
        # Count by difficulty
        principiante = await db.exercises.count_documents({"nivel_dificultad": {"$regex": "Principiante", "$options": "i"}})
        intermedio = await db.exercises.count_documents({"nivel_dificultad": {"$regex": "Intermedio", "$options": "i"}})
        avanzado = await db.exercises.count_documents({"nivel_dificultad": {"$regex": "Avanzado", "$options": "i"}})
        
        # Get unique muscle groups
        muscle_groups_pipeline = [
            {"$group": {"_id": "$grupo_muscular_principal"}},
            {"$sort": {"_id": 1}}
        ]
        muscle_groups = await db.exercises.aggregate(muscle_groups_pipeline).to_list(length=1000)
        unique_muscle_groups = [mg["_id"] for mg in muscle_groups if mg["_id"]]
        
        return {
            "total_exercises": total,
            "by_difficulty": {
                "principiante": principiante,
                "intermedio": intermedio,
                "avanzado": avanzado
            },
            "muscle_groups": unique_muscle_groups,
            "muscle_groups_count": len(unique_muscle_groups)
        }
    
    except Exception as e:
        logger.error(f"Error fetching exercise stats: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener estadísticas de ejercicios")


# ==================== TRAINING PLAN CHAT ENDPOINT ====================

@api_router.post("/training-plan/chat", response_model=TrainingPlanChatResponse)
async def chat_about_training_plan(chat_request: TrainingPlanChatRequest, request: Request):
    """
    Chat with AI to modify an existing training plan
    """
    current_user = await get_current_user(request)
    
    try:
        # Get the training plan
        plan = await db.training_plans.find_one({"_id": chat_request.plan_id})
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan de entrenamiento no encontrado")
        
        # Verify user has access (admin or owner)
        if current_user.get("role") != "admin" and plan.get("user_id") != current_user.get("_id"):
            raise HTTPException(status_code=403, detail="No tienes permiso para modificar este plan")
        
        # Get chat history if exists
        chat_history = plan.get("chat_history", [])
        
        # Prepare context for AI
        current_plan_content = plan.get("plan_final", "")
        
        # Call OpenAI to process the modification request
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        messages = [
            {
                "role": "system",
                "content": """Eres un entrenador personal experto que ayuda a ajustar planes de entrenamiento.

Tu misión es:
1. Entender la petición del entrenador
2. Modificar el plan según sus indicaciones
3. Mantener la estructura profesional del documento
4. Explicar brevemente los cambios realizados

REGLAS:
- Ser conciso en las explicaciones
- Mantener el formato del plan original
- Solo modificar lo que se solicita
- Asegurar que los cambios tengan sentido técnicamente"""
            },
            {
                "role": "user",
                "content": f"""PLAN ACTUAL:
{current_plan_content}

PETICIÓN DEL ENTRENADOR:
{chat_request.user_message}

Por favor:
1. Modifica el plan según la petición
2. Devuelve el plan COMPLETO modificado
3. Explica brevemente qué cambiaste"""
            }
        ]
        
        # Add chat history
        for msg in chat_history[-5:]:  # Last 5 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=4000,
            timeout=120
        )
        
        ai_response = response.choices[0].message.content
        
        # Check if AI modified the plan (look for plan structure in response)
        updated_plan = None
        if "🏋️" in ai_response or "PROGRAMA" in ai_response or "PLAN DE ENTRENAMIENTO" in ai_response:
            # AI returned a modified plan
            updated_plan = ai_response
            
            # Update the plan in database
            await db.training_plans.update_one(
                {"_id": chat_request.plan_id},
                {
                    "$set": {
                        "plan_final": updated_plan,
                        "last_modified": datetime.now(timezone.utc).isoformat()
                    },
                    "$push": {
                        "chat_history": {
                            "$each": [
                                {
                                    "role": "user",
                                    "content": chat_request.user_message,
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                },
                                {
                                    "role": "assistant",
                                    "content": ai_response,
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                }
                            ]
                        }
                    }
                }
            )
            
            logger.info(f"✅ Training plan {chat_request.plan_id} modified via chat")
        else:
            # AI just answered without modifying plan
            await db.training_plans.update_one(
                {"_id": chat_request.plan_id},
                {
                    "$push": {
                        "chat_history": {
                            "$each": [
                                {
                                    "role": "user",
                                    "content": chat_request.user_message,
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                },
                                {
                                    "role": "assistant",
                                    "content": ai_response,
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                }
                            ]
                        }
                    }
                }
            )
        
        return TrainingPlanChatResponse(
            assistant_message=ai_response,
            updated_plan=updated_plan
        )
        
    except Exception as e:
        logger.error(f"Error in training plan chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando chat: {str(e)}")


# ==================== NUTRITION PLAN CHAT ENDPOINT ====================

@api_router.post("/nutrition-plan/chat", response_model=NutritionPlanChatResponse)
async def chat_about_nutrition_plan(chat_request: NutritionPlanChatRequest, request: Request):
    """
    Chat with AI to modify an existing nutrition plan
    """
    current_user = await get_current_user(request)
    
    try:
        # Get the nutrition plan
        plan = await db.nutrition_plans.find_one({"_id": chat_request.plan_id})
        
        if not plan:
            raise HTTPException(status_code=404, detail="Plan de nutrición no encontrado")
        
        # Verify user has access (admin or owner)
        if current_user.get("role") != "admin" and plan.get("user_id") != current_user.get("_id"):
            raise HTTPException(status_code=403, detail="No tienes permiso para modificar este plan")
        
        # Get chat history if exists
        chat_history = plan.get("chat_history", [])
        
        # Prepare context for AI - try plan_text first, fallback to plan_verificado
        current_plan_content = plan.get("plan_text") or plan.get("plan_verificado", "")
        
        # Call OpenAI to process the modification request
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        messages = [
            {
                "role": "system",
                "content": """Eres un nutricionista profesional experto que ayuda a ajustar planes de nutrición.

Tu misión es:
1. Entender la petición del nutricionista
2. Modificar el plan según sus indicaciones
3. Mantener la estructura profesional del documento
4. Explicar brevemente los cambios realizados

REGLAS:
- Ser conciso en las explicaciones
- Mantener el formato del plan original
- Solo modificar lo que se solicita
- Asegurar que los cambios tengan sentido nutricional
- Mantener equilibrio de macronutrientes cuando sea posible
- Considerar alergias y preferencias del cliente"""
            },
            {
                "role": "user",
                "content": f"""PLAN ACTUAL:
{current_plan_content}

PETICIÓN DEL NUTRICIONISTA:
{chat_request.user_message}

Por favor:
1. Modifica el plan según la petición
2. Devuelve el plan COMPLETO modificado
3. Explica brevemente qué cambiaste"""
            }
        ]
        
        # Add chat history
        for msg in chat_history[-5:]:  # Last 5 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=4000,
            timeout=120
        )
        
        ai_response = response.choices[0].message.content
        
        # Check if AI modified the plan (look for plan structure in response)
        updated_plan = None
        if "🥗" in ai_response or "PLAN DE NUTRICIÓN" in ai_response or "PROGRAMA NUTRICIONAL" in ai_response or "DESAYUNO" in ai_response:
            # AI returned a modified plan
            updated_plan = ai_response
            
            # Update the plan in database - update both plan_verificado and plan_text
            await db.nutrition_plans.update_one(
                {"_id": chat_request.plan_id},
                {
                    "$set": {
                        "plan_verificado": updated_plan,
                        "plan_text": updated_plan,
                        "last_modified": datetime.now(timezone.utc).isoformat(),
                        "edited": True
                    },
                    "$push": {
                        "chat_history": {
                            "$each": [
                                {
                                    "role": "user",
                                    "content": chat_request.user_message,
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                },
                                {
                                    "role": "assistant",
                                    "content": ai_response,
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                }
                            ]
                        }
                    }
                }
            )
            
            logger.info(f"✅ Nutrition plan {chat_request.plan_id} modified via chat")
        else:
            # AI just answered without modifying plan
            await db.nutrition_plans.update_one(
                {"_id": chat_request.plan_id},
                {
                    "$push": {
                        "chat_history": {
                            "$each": [
                                {
                                    "role": "user",
                                    "content": chat_request.user_message,
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                },
                                {
                                    "role": "assistant",
                                    "content": ai_response,
                                    "timestamp": datetime.now(timezone.utc).isoformat()
                                }
                            ]
                        }
                    }
                }
            )
        
        return NutritionPlanChatResponse(
            assistant_message=ai_response,
            updated_plan=updated_plan
        )
        
    except Exception as e:
        logger.error(f"Error in nutrition plan chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error procesando chat: {str(e)}")


# ==================== ENDPOINTS PARA SELECTORES ====================

@api_router.get("/admin/users/{user_id}/questionnaires")
async def get_user_questionnaires(user_id: str, request: Request):
    """Obtiene todos los cuestionarios de un usuario (inicial + seguimientos)"""
    await require_admin(request)
    
    questionnaires = []
    
    # Cuestionario inicial
    initial = await db.nutrition_questionnaire_submissions.find_one(
        {"user_id": user_id},
        sort=[("submitted_at", 1)]
    )
    
    if initial:
        # Manejar casos donde submitted_at podría no existir
        submitted_at = initial.get("submitted_at")
        if submitted_at:
            date_str = submitted_at.strftime('%d/%m/%Y')
            iso_str = submitted_at.isoformat()
        else:
            date_str = "Fecha desconocida"
            iso_str = datetime.now(timezone.utc).isoformat()
        
        questionnaires.append({
            "id": initial["_id"],
            "type": "initial",
            "label": f"Cuestionario Inicial ({date_str})",
            "submitted_at": iso_str,
            "is_initial": True
        })
    
    # Seguimientos
    followups = await db.follow_up_submissions.find(
        {"user_id": user_id}
    ).sort("created_at", 1).to_list(length=1000)
    
    for i, followup in enumerate(followups, 1):
        # Intentar varios campos posibles de fecha
        submitted_at = followup.get("submitted_at") or followup.get("created_at") or followup.get("updated_at")
        if submitted_at:
            date_str = submitted_at.strftime('%d/%m/%Y')
            iso_str = submitted_at.isoformat()
        else:
            date_str = "Fecha desconocida"
            iso_str = datetime.now(timezone.utc).isoformat()
        
        questionnaires.append({
            "id": followup["_id"],
            "type": "followup",
            "label": f"Seguimiento {i} ({date_str})",
            "submitted_at": iso_str,
            "is_initial": False
        })
    
    return {"questionnaires": questionnaires}



@api_router.get("/admin/users/{user_id}/edn360-questionnaires")
async def get_user_edn360_questionnaires(user_id: str, request: Request):
    """
    Obtiene cuestionarios desde client_drawers (arquitectura EDN360).
    
    Este endpoint lee los cuestionarios guardados en la nueva arquitectura
    EDN360 (client_drawers.services.shared_questionnaires).
    
    Returns:
        {
            "questionnaires": [
                {
                    "submission_id": "...",
                    "source": "initial" | "follow_up",
                    "submitted_at": "2025-11-26T15:03:52Z",
                    "label": "Cuestionario Inicial (26/11/2025)"
                }
            ]
        }
    """
    await require_admin(request)
    
    try:
        # Obtener BD de EDN360 App
        edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
        
        logger.info(f"🔍 [EDN360] Buscando cuestionarios para user_id: {user_id}")
        
        # Buscar client_drawer del usuario
        client_drawer = await edn360_db.client_drawers.find_one(
            {"user_id": user_id},
            {"services.shared_questionnaires": 1}
        )
        
        logger.info(f"📦 [EDN360] Client drawer encontrado: {client_drawer is not None}")
        
        if not client_drawer:
            logger.warning(f"⚠️ [EDN360] No se encontró client_drawer para user_id: {user_id}")
            return {"questionnaires": []}
        
        # Extraer cuestionarios
        shared_questionnaires = (
            client_drawer.get("services", {}).get("shared_questionnaires", [])
        )
        
        logger.info(f"📋 [EDN360] Cuestionarios en shared_questionnaires: {len(shared_questionnaires)}")
        
        if not shared_questionnaires:
            logger.warning(f"⚠️ [EDN360] No hay cuestionarios en shared_questionnaires para user_id: {user_id}")
            return {"questionnaires": []}
        
        # Formatear cuestionarios para el frontend
        questionnaires = []
        for q in shared_questionnaires:
            # Parsear fecha
            submitted_at = q.get("submitted_at")
            if isinstance(submitted_at, str):
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                    date_str = dt.strftime('%d/%m/%Y')
                    iso_str = submitted_at
                except:
                    date_str = "Fecha desconocida"
                    iso_str = submitted_at
            elif hasattr(submitted_at, 'strftime'):
                date_str = submitted_at.strftime('%d/%m/%Y')
                iso_str = submitted_at.isoformat()
            else:
                date_str = "Fecha desconocida"
                iso_str = str(submitted_at) if submitted_at else ""
            
            # Determinar label
            source = q.get("source", "")
            if source == "initial" or source == "nutrition_initial":
                label = f"Cuestionario Inicial ({date_str})"
            elif source == "follow_up":
                label = f"Seguimiento ({date_str})"
            else:
                label = f"Cuestionario ({date_str})"
            
            questionnaires.append({
                "id": q.get("submission_id"),
                "submission_id": q.get("submission_id"),
                "source": source,
                "submitted_at": iso_str,
                "label": label
            })
        
        logger.info(
            f"✅ Cuestionarios EDN360 obtenidos | "
            f"user_id: {user_id} | count: {len(questionnaires)}"
        )
        
        return {"questionnaires": questionnaires}
    
    except Exception as e:
        logger.error(f"❌ Error obteniendo cuestionarios EDN360: {e}")
        return {"questionnaires": []}


@api_router.get("/admin/users/{user_id}/training-plans")
async def get_user_training_plans(user_id: str, request: Request):
    """Obtiene todos los planes de entrenamiento de un usuario con toda la información"""
    await require_admin(request)
    
    all_plans = []
    
    # 1. Obtener planes EDN360 de training_plans_v2 con TODA la información
    edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
    edn360_plans = await edn360_db.training_plans_v2.find(
        {"user_id": user_id}
    ).sort("created_at", -1).to_list(length=1000)
    
    for plan_doc in edn360_plans:
        # Usar questionnaire_submission_id si existe, o convertir _id a string
        plan_id = plan_doc.get("questionnaire_submission_id")
        if not plan_id:
            plan_id = str(plan_doc.get("_id"))
        
        # Devolver el plan completo con toda la información
        all_plans.append({
            "id": plan_id,
            "plan": plan_doc.get("plan", {}),
            "plain_text_content": plan_doc.get("plain_text_content"),  # NEW: Include plain text
            "created_at": plan_doc.get("created_at"),
            "status": plan_doc.get("status", "draft"),
            "source_type": "edn360",
            "user_id": plan_doc.get("user_id")
        })
    
    return all_plans


# ==================== QUESTIONNAIRE MANAGEMENT ENDPOINTS ====================

@api_router.delete("/admin/questionnaires/{submission_id}")
async def delete_questionnaire_submission(submission_id: str, request: Request):
    """
    Elimina un cuestionario de diagnóstico o nutrición
    Solo admin puede eliminar
    """
    await require_admin(request)
    
    try:
        user_id = None
        questionnaire_type = None
        
        # Buscar primero en nutrition_questionnaire_submissions
        nutrition_doc = await db.nutrition_questionnaire_submissions.find_one({"_id": submission_id})
        if nutrition_doc:
            user_id = nutrition_doc.get("user_id")
            questionnaire_type = "nutrition"
            result = await db.nutrition_questionnaire_submissions.delete_one({"_id": submission_id})
            if result.deleted_count > 0:
                logger.info(f"✅ Cuestionario de nutrición eliminado: {submission_id}")
        
        # Si no estaba en nutrition, buscar en diagnosis
        if not nutrition_doc:
            diagnosis_doc = await db.diagnosis_questionnaire_submissions.find_one({"_id": submission_id})
            if diagnosis_doc:
                user_id = diagnosis_doc.get("user_id")
                questionnaire_type = "diagnosis"
                result = await db.diagnosis_questionnaire_submissions.delete_one({"_id": submission_id})
                if result.deleted_count > 0:
                    logger.info(f"✅ Cuestionario de diagnóstico eliminado: {submission_id}")
        
        if not nutrition_doc and not diagnosis_doc:
            raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
        
        # Eliminar también del client_drawer si existe
        if user_id:
            edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
            update_result = await edn360_db.client_drawers.update_one(
                {"user_id": user_id},
                {"$pull": {"services.shared_questionnaires": {"submission_id": submission_id}}}
            )
            if update_result.modified_count > 0:
                logger.info(f"✅ Cuestionario eliminado del client_drawer: {submission_id}")
            else:
                logger.warning(f"⚠️ No se encontró el cuestionario en client_drawer o ya no existía")
        
        return {"message": "Cuestionario eliminado exitosamente", "type": questionnaire_type}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando cuestionario: {e}")
        raise HTTPException(status_code=500, detail=f"Error eliminando cuestionario: {str(e)}")


@api_router.delete("/admin/follow-ups/{followup_id}")
async def delete_follow_up_submission(followup_id: str, request: Request):
    """
    Elimina un cuestionario de seguimiento
    Solo admin puede eliminar
    """
    await require_admin(request)
    
    try:
        # Obtener el cuestionario antes de eliminarlo para saber el user_id
        followup_doc = await db.follow_up_submissions.find_one({"_id": followup_id})
        
        if not followup_doc:
            raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
        
        user_id = followup_doc.get("user_id")
        
        # Eliminar de follow_up_submissions
        result = await db.follow_up_submissions.delete_one({"_id": followup_id})
        
        if result.deleted_count > 0:
            logger.info(f"✅ Seguimiento eliminado de follow_up_submissions: {followup_id}")
            
            # También eliminar del client_drawer si existe
            if user_id:
                edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')]
                update_result = await edn360_db.client_drawers.update_one(
                    {"user_id": user_id},
                    {"$pull": {"services.shared_questionnaires": {"submission_id": followup_id}}}
                )
                if update_result.modified_count > 0:
                    logger.info(f"✅ Seguimiento eliminado del client_drawer: {followup_id}")
                else:
                    logger.warning(f"⚠️ No se encontró el seguimiento en client_drawer o ya no existía")
            
            return {"message": "Seguimiento eliminado exitosamente"}
        
        raise HTTPException(status_code=404, detail="Seguimiento no encontrado")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando seguimiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error eliminando seguimiento: {str(e)}")


# ==================== FOLLOW-UP REPORT ENDPOINTS ====================

@api_router.get("/admin/users/{user_id}/nutrition-plans")
async def get_user_nutrition_plans(user_id: str, request: Request):
    """Obtiene todos los planes de nutrición de un usuario (solo planes, sin cuestionarios)"""
    await require_admin(request)
    
    # Obtener planes de nutrición
    plans = await db.nutrition_plans.find(
        {"user_id": user_id}
    ).sort("generated_at", -1).to_list(length=1000)
    
    formatted_plans = []
    
    # Agregar planes de nutrición
    for i, plan in enumerate(plans):
        # Manejar casos donde generated_at podría no existir
        generated_at = plan.get("generated_at")
        if generated_at:
            date_str = generated_at.strftime('%d/%m/%Y')
            iso_str = generated_at.isoformat()
        else:
            date_str = "Fecha desconocida"
            iso_str = datetime.now(timezone.utc).isoformat()
        
        # Determinar label con convención de nombres mejorada
        plan_number = len(plans) - i
        label = f"PLAN NUTRICION {plan_number} - {date_str}"
        
        plan_id_str = str(plan["_id"])
        logger.info(f"🔍 GET nutrition-plans devuelve ID: '{plan_id_str}' (tipo: {type(plan['_id'])})")
        formatted_plans.append({
            "id": plan_id_str,
            "label": label,
            "generated_at": iso_str,
            "month": plan.get("month"),
            "year": plan.get("year"),
            "type": "nutrition_plan"
        })
    
    # Ordenar por fecha (más reciente primero)
    formatted_plans.sort(key=lambda x: x["generated_at"], reverse=True)
    
    return {"plans": formatted_plans}


@api_router.delete("/admin/users/{user_id}/follow-up-reports/{report_id}")
async def delete_follow_up_report(
    user_id: str,
    report_id: str,
    request: Request = None
):
    """
    Admin elimina un informe de seguimiento
    """
    await require_admin(request)
    
    try:
        result = await db.follow_up_reports.delete_one({"_id": report_id, "user_id": user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Informe no encontrado")
        
        logger.info(f"✅ Informe de seguimiento eliminado: {report_id}")
        
        return {"success": True, "message": "Informe eliminado exitosamente"}
        
    except Exception as e:
        logger.error(f"Error eliminando informe: {e}")
        raise HTTPException(status_code=500, detail=f"Error eliminando informe: {str(e)}")


@api_router.patch("/admin/users/{user_id}/follow-up-reports/{report_id}")
async def update_follow_up_report(
    user_id: str,
    report_id: str,
    request: Request
):
    """
    Admin edita el contenido de un informe de seguimiento
    """
    await require_admin(request)
    
    try:
        body = await request.json()
        report_text = body.get("report_text")
        
        if not report_text:
            raise HTTPException(status_code=400, detail="report_text es requerido")
        
        result = await db.follow_up_reports.update_one(
            {"_id": report_id, "user_id": user_id},
            {
                "$set": {
                    "report_text": report_text,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Informe no encontrado")
        
        logger.info(f"✅ Informe de seguimiento actualizado: {report_id}")
        
        return {"success": True, "message": "Informe actualizado exitosamente"}
        
    except Exception as e:
        logger.error(f"Error actualizando informe: {e}")
        raise HTTPException(status_code=500, detail=f"Error actualizando informe: {str(e)}")


@api_router.get("/admin/users/{user_id}/follow-up-questionnaires")
async def get_follow_up_questionnaires(user_id: str, request: Request):
    """Obtiene todos los cuestionarios de seguimiento de un usuario"""
    await require_admin(request)
    
    # Obtener cuestionarios de seguimiento de la colección correcta
    questionnaires = await db.follow_up_submissions.find({
        "user_id": user_id
    }).sort("submission_date", -1).to_list(length=100)
    
    # Formatear respuesta
    formatted = []
    for q in questionnaires:
        # Usar submission_date en lugar de submitted_at
        submission_date = q.get("submission_date")
        if submission_date:
            date_str = submission_date.strftime('%d/%m/%Y')
            iso_str = submission_date.isoformat()
        else:
            date_str = "Fecha desconocida"
            iso_str = datetime.now(timezone.utc).isoformat()
        
        formatted.append({
            "id": str(q["_id"]),
            "label": f"📋 Seguimiento ({date_str})",
            "submitted_at": iso_str,
            "submission_date": iso_str,
            "days_since_last_plan": q.get("days_since_last_plan"),
            "status": q.get("status", "pending_analysis"),
            "type": "followup"
        })
    
    return {"questionnaires": formatted}


@api_router.get("/admin/users/{user_id}/follow-up-reports")
async def get_follow_up_reports(user_id: str, request: Request):
    """Obtiene todos los informes de seguimiento de un usuario"""
    await require_admin(request)
    
    reports = await db.follow_up_reports.find(
        {"user_id": user_id}
    ).sort("generated_at", -1).to_list(length=100)  # Limit to last 100 reports
    
    # Convert _id to string for JSON serialization
    for report in reports:
        report["_id"] = str(report["_id"])
        # Also convert generated_at datetime to ISO string if it's a datetime object
        if isinstance(report.get("generated_at"), datetime):
            report["generated_at"] = report["generated_at"].isoformat()
    
    return {"reports": reports}


def _format_date_safe(date_value):
    """Helper function to safely format dates that could be string or datetime objects"""
    if not date_value:
        return 'N/A'
    try:
        if isinstance(date_value, datetime):
            return date_value.strftime('%d/%m/%Y')
        elif isinstance(date_value, str):
            return datetime.fromisoformat(date_value).strftime('%d/%m/%Y')
        else:
            return 'N/A'
    except:
        return 'N/A'


@api_router.post("/admin/users/{user_id}/follow-up-report/generate")
async def generate_follow_up_report(
    user_id: str,
    request: Request
):
    """
    Genera un informe de seguimiento inteligente analizando cuestionario y planes
    """
    await require_admin(request)
    
    # Obtener datos del body
    body = await request.json()
    previous_training_id = body.get("previous_training_id")
    new_training_id = body.get("new_training_id")
    previous_nutrition_id = body.get("previous_nutrition_id")
    new_nutrition_id = body.get("new_nutrition_id")
    followup_questionnaire_id = body.get("followup_questionnaire_id")
    
    # Validar parámetros requeridos
    if not previous_training_id or not new_training_id:
        raise HTTPException(status_code=400, detail="previous_training_id y new_training_id son requeridos")
    
    if not followup_questionnaire_id:
        raise HTTPException(status_code=400, detail="followup_questionnaire_id es requerido para análisis inteligente")
    
    try:
        logger.info(f"📊 Generando informe de seguimiento INTELIGENTE para usuario {user_id}")
        
        # FASE 1: Obtener TODOS los datos necesarios
        
        # 1.1 Cuestionario de seguimiento (CRÍTICO) - Buscar en la colección correcta
        logger.info(f"🔍 Buscando cuestionario de seguimiento con _id: '{followup_questionnaire_id}' (tipo: {type(followup_questionnaire_id)})")
        followup_questionnaire = await db.follow_up_submissions.find_one({
            "_id": followup_questionnaire_id,
            "user_id": user_id
        })
        
        if not followup_questionnaire:
            # Intentar buscar sin user_id para debug
            any_with_id = await db.follow_up_submissions.find_one({"_id": followup_questionnaire_id})
            if any_with_id:
                logger.error(f"❌ Cuestionario existe pero user_id no coincide. Esperado: {user_id}, Encontrado: {any_with_id.get('user_id')}")
            else:
                logger.error(f"❌ No existe ningún cuestionario con _id: '{followup_questionnaire_id}'")
            raise HTTPException(status_code=404, detail="Cuestionario de seguimiento no encontrado")
        
        # 1.2 Planes de entrenamiento
        prev_training = await db.training_plans.find_one({"_id": previous_training_id})
        new_training = await db.training_plans.find_one({"_id": new_training_id})
        
        if not prev_training or not new_training:
            raise HTTPException(status_code=404, detail="Planes de entrenamiento no encontrados")
        
        # 1.3 Planes de nutrición
        prev_nutrition = None
        new_nutrition = None
        if previous_nutrition_id and new_nutrition_id:
            prev_nutrition = await db.nutrition_plans.find_one({"_id": previous_nutrition_id})
            new_nutrition = await db.nutrition_plans.find_one({"_id": new_nutrition_id})
        
        # 1.4 Información del usuario
        user = await db.users.find_one({"_id": user_id})
        user_name = user.get("name", user.get("username", "Cliente")) if user else "Cliente"
        
        # FASE 2: Extraer y estructurar datos para el LLM
        
        # 2.1 Datos del cuestionario de seguimiento
        # En follow_up_submissions los datos están en campos estructurados
        adherence = followup_questionnaire.get("adherence", {})
        wellbeing = followup_questionnaire.get("wellbeing", {})
        changes_perceived = followup_questionnaire.get("changes_perceived", {})
        feedback = followup_questionnaire.get("feedback", {})
        measurements = followup_questionnaire.get("measurements", {})
        
        questionnaire_text = f"""
CUESTIONARIO DE SEGUIMIENTO DEL CLIENTE:

Fecha: {_format_date_safe(followup_questionnaire.get('submission_date'))}
Días desde último plan: {followup_questionnaire.get('days_since_last_plan', 'N/A')}

ADHERENCIA:
{json.dumps(adherence, indent=2, ensure_ascii=False)}

BIENESTAR:
{json.dumps(wellbeing, indent=2, ensure_ascii=False)}

CAMBIOS PERCIBIDOS:
{json.dumps(changes_perceived, indent=2, ensure_ascii=False)}

FEEDBACK:
{json.dumps(feedback, indent=2, ensure_ascii=False)}

MEDICIONES:
{json.dumps(measurements, indent=2, ensure_ascii=False)}
"""
        
        # 2.2 Extraer datos estructurados de entrenamiento
        prev_training_data = prev_training.get("edn360_data", {})
        new_training_data = new_training.get("edn360_data", {})
        prev_e4 = prev_training_data.get("E4", {})
        new_e4 = new_training_data.get("E4", {})
        prev_mesociclo = prev_e4.get("mesociclo", {})
        new_mesociclo = new_e4.get("mesociclo", {})
        
        # 2.3 Datos estructurados de nutrición
        nutrition_data_text = ""
        if prev_nutrition and new_nutrition:
            prev_nutrition_data = prev_nutrition.get("edn360_data", {})
            new_nutrition_data = new_nutrition.get("edn360_data", {})
            
            # Estructura correcta: N1 para metabólico, N2 para energy/macros
            prev_n1 = prev_nutrition_data.get("N1", {})
            new_n1 = new_nutrition_data.get("N1", {})
            prev_n2 = prev_nutrition_data.get("N2", {})
            new_n2 = new_nutrition_data.get("N2", {})
            
            # Obtener macros del día A (días de entrenamiento)
            prev_macros_a = prev_n2.get("macros_dia_A", {})
            new_macros_a = new_n2.get("macros_dia_A", {})
            
            nutrition_data_text = f"""
PLAN DE NUTRICIÓN ANTERIOR (Mes {prev_nutrition.get('month')}/{prev_nutrition.get('year')}):
- TDEE: {prev_n1.get('tdee_estimado', prev_n2.get('tdee', 'N/A'))} kcal/día
- Calorías (Día Entreno): {prev_macros_a.get('kcal_objetivo', 'N/A')} kcal
- Proteínas: {prev_macros_a.get('proteinas_g', 'N/A')}g ({prev_macros_a.get('proteinas_gkg', 'N/A')}g/kg)
- Carbohidratos: {prev_macros_a.get('carbohidratos_g', 'N/A')}g
- Grasas: {prev_macros_a.get('grasas_g', 'N/A')}g

PLAN DE NUTRICIÓN NUEVO (Mes {new_nutrition.get('month')}/{new_nutrition.get('year')}):
- TDEE: {new_n1.get('tdee_estimado', new_n2.get('tdee', 'N/A'))} kcal/día
- Calorías (Día Entreno): {new_macros_a.get('kcal_objetivo', 'N/A')} kcal
- Proteínas: {new_macros_a.get('proteinas_g', 'N/A')}g ({new_macros_a.get('proteinas_gkg', 'N/A')}g/kg)
- Carbohidratos: {new_macros_a.get('carbohidratos_g', 'N/A')}g
- Grasas: {new_macros_a.get('grasas_g', 'N/A')}g
"""
            
        
        # 2.4 Datos estructurados de entrenamiento para LLM
        training_data_text = f"""
PLAN DE ENTRENAMIENTO ANTERIOR (Mes {prev_training.get('month')}/{prev_training.get('year')}):
- Frecuencia semanal: {prev_mesociclo.get('frecuencia_semanal', 'N/A')} días
- Duración: {prev_mesociclo.get('duracion_semanas', 'N/A')} semanas  
- Objetivo: {prev_mesociclo.get('objetivo', 'N/A').replace('_', ' ').title()}
- Split: {prev_mesociclo.get('split', 'N/A').upper()}
- Estrategia: {prev_mesociclo.get('estrategia', 'N/A').title()}

PLAN DE ENTRENAMIENTO NUEVO (Mes {new_training.get('month')}/{new_training.get('year')}):
- Frecuencia semanal: {new_mesociclo.get('frecuencia_semanal', 'N/A')} días
- Duración: {new_mesociclo.get('duracion_semanas', 'N/A')} semanas
- Objetivo: {new_mesociclo.get('objetivo', 'N/A').replace('_', ' ').title()}
- Split: {new_mesociclo.get('split', 'N/A').upper()}
- Estrategia: {new_mesociclo.get('estrategia', 'N/A').title()}
"""
        
        # FASE 3: Generar informe inteligente con LLM
        
        from openai import AsyncOpenAI
        
        # Usar OpenAI API key
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY no configurada en el entorno")
        
        # Prompt del sistema basado en tu documento
        system_message = f"""Eres un entrenador profesional y nutricionista experto generando un informe de seguimiento personalizado.

Tu tarea: Analizar el cuestionario de seguimiento del cliente, comparar planes anteriores con nuevos, y generar un informe estructurado.

ESTRUCTURA DEL INFORME (OBLIGATORIA):

1️⃣ Lo que hemos visto en tu seguimiento
- Objetivo actual del cliente
- Puntos clave del cuestionario (adherencia, cambios físicos, molestias, disponibilidad, estrés, feedback)
- Resumen diagnóstico breve

2️⃣ Cambios en tu entrenamiento
- ANTES (frecuencia, estructura, volumen, enfoque)
- AHORA (frecuencia, estructura, volumen, enfoque)
- Cambios clave: Explica QUÉ cambió y POR QUÉ basándote en el cuestionario
- Qué necesito de ti: Instrucciones específicas para el cliente

3️⃣ Cambios en tu nutrición (si aplica)
- ANTES (calorías, macros, comidas/día, estrategia)
- AHORA (calorías, macros, comidas/día, estrategia)
- Cambios clave: Explica QUÉ cambió y POR QUÉ basándote en el cuestionario
- Qué necesito de ti: Instrucciones específicas

4️⃣ Dónde tienes tus nuevos programas
- Indica que están disponibles en su panel
- Link: {os.environ.get("FRONTEND_URL", "https://tu-dominio.emergent.host")}

5️⃣ Mensaje final
- En qué debe enfocarse este mes
- Mensaje motivacional personalizado

REGLAS IMPORTANTES:
- Conecta TODOS los cambios con lo que el cliente escribió en el cuestionario
- Sé específico: "aumentamos 100 kcal" NO "ajustamos calorías"
- Usa lenguaje cercano (tú/tu) pero profesional
- Si algo NO cambió, explica por qué (ej: "parámetros funcionando bien")
- Analiza como un entrenador real: interpretar feedback, proponer soluciones
- El informe se envía por email junto con los nuevos planes

Cliente: {user_name}
Fecha: {datetime.now(timezone.utc).strftime('%d/%m/%Y')}
"""
        
        user_prompt_text = f"""
{questionnaire_text}

{training_data_text}

{nutrition_data_text if nutrition_data_text else "NO HAY PLAN DE NUTRICIÓN"}

Genera el informe de seguimiento completo siguiendo la estructura obligatoria.
"""
        
        try:
            logger.info("🤖 Generando informe con LLM...")
            
            # Inicializar cliente de OpenAI
            client = AsyncOpenAI(api_key=openai_key)
            
            # Crear solicitud a GPT-4o
            completion = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_prompt_text}
                ],
                temperature=0.7,
                max_tokens=3000,
                timeout=120
            )
            
            # Obtener respuesta
            report_text = completion.choices[0].message.content
            logger.info("✅ Informe inteligente generado exitosamente")
            
        except Exception as e:
            logger.error(f"Error generando informe con LLM: {e}")
            report_text = f"# INFORME DE SEGUIMIENTO\n\nError generando informe: {str(e)}"
        
        # Guardar informe
        report_id = str(uuid.uuid4())
        report_doc = {
            "_id": report_id,
            "user_id": user_id,
            "generated_at": datetime.now(timezone.utc),
            "previous_training_id": previous_training_id,
            "new_training_id": new_training_id,
            "previous_nutrition_id": previous_nutrition_id,
            "new_nutrition_id": new_nutrition_id,
            "report_text": report_text,
            "training_comparison_label": f"Plan Anterior vs Plan Nuevo",
            "nutrition_comparison_label": f"Plan Anterior vs Plan Nuevo" if prev_nutrition else None
        }
        
        await db.follow_up_reports.insert_one(report_doc)
        
        logger.info(f"✅ Informe de seguimiento generado: {report_id}")
        
        return {"report_id": report_id, "message": "Informe generado exitosamente"}
        
    except Exception as e:
        logger.error(f"Error generando informe de seguimiento: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando informe: {str(e)}")


# ==================== WAITLIST ENDPOINTS ====================

from waitlist_scoring import calculate_waitlist_score

@api_router.post("/waitlist/submit")
async def submit_waitlist(lead_data: WaitlistLeadSubmit):
    """
    Endpoint público para enviar el formulario de waitlist
    No requiere autenticación
    """
    try:
        # Convertir datos a dict
        responses = lead_data.dict()
        
        # Calcular scoring y tags automáticos
        scoring_result = calculate_waitlist_score(responses)
        
        # Crear ID único
        lead_id = str(int(datetime.now(timezone.utc).timestamp() * 1000000))
        
        # Preparar documento para MongoDB
        lead_document = {
            "_id": lead_id,
            "nombre_apellidos": lead_data.nombre_apellidos,
            "email": lead_data.email,
            "telefono": lead_data.telefono,
            "edad": lead_data.edad,
            "ciudad_pais": lead_data.ciudad_pais,
            "como_conociste": lead_data.como_conociste,
            "responses": responses,
            "score_total": scoring_result["score_total"],
            "score_capacidad_economica": scoring_result["score_capacidad_economica"],
            "score_objetivos_motivacion": scoring_result["score_objetivos_motivacion"],
            "score_experiencia_habitos": scoring_result["score_experiencia_habitos"],
            "score_disponibilidad_compromiso": scoring_result["score_disponibilidad_compromiso"],
            "score_personalidad_afinidad": scoring_result["score_personalidad_afinidad"],
            "score_disponibilidad_entrevista": scoring_result["score_disponibilidad_entrevista"],
            "capacidad_economica": scoring_result["capacidad_economica"],
            "objetivo": scoring_result["objetivo"],
            "motivacion": scoring_result["motivacion"],
            "nivel_experiencia": scoring_result["nivel_experiencia"],
            "nivel_compromiso": scoring_result["nivel_compromiso"],
            "urgencia": scoring_result["urgencia"],
            "afinidad_estilo": scoring_result["afinidad_estilo"],
            "prioridad": scoring_result["prioridad"],
            "estado": "pendiente",
            "notas_admin": [],
            "historial_contacto": [],
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "contacted_at": None,
            "converted_at": None,
            "converted_to_client": False,
            "client_id": None
        }
        
        # Guardar en MongoDB
        await db.waitlist_leads.insert_one(lead_document)
        
        logger.info(f"✅ Waitlist lead submitted: {lead_data.email} - Score: {scoring_result['score_total']} - Prioridad: {scoring_result['prioridad']}")
        
        # TODO: Enviar email de confirmación según prioridad
        
        return {
            "success": True,
            "message": "Formulario enviado correctamente",
            "score": scoring_result["score_total"],
            "prioridad": scoring_result["prioridad"]
        }
        
    except Exception as e:
        logger.error(f"Error submitting waitlist lead: {e}")
        raise HTTPException(status_code=500, detail=f"Error al enviar formulario: {str(e)}")


@api_router.get("/admin/waitlist/all", response_model=List[WaitlistLeadResponse])
async def get_all_waitlist_leads(request: Request):
    """
    Obtener todos los leads de waitlist (solo admin)
    """
    current_user = await get_current_user(request)
    
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    try:
        leads = await db.waitlist_leads.find().sort("submitted_at", -1).to_list(length=1000)
        
        # Formatear para respuesta
        leads_response = []
        for lead in leads:
            leads_response.append({
                "id": lead["_id"],
                "nombre_apellidos": lead.get("nombre_apellidos"),
                "email": lead.get("email"),
                "telefono": lead.get("telefono"),
                "edad": lead.get("edad"),
                "ciudad_pais": lead.get("ciudad_pais"),
                "como_conociste": lead.get("como_conociste"),
                "score_total": lead.get("score_total", 0),
                "prioridad": lead.get("prioridad", "media"),
                "estado": lead.get("estado", "pendiente"),
                "capacidad_economica": lead.get("capacidad_economica", "media"),
                "objetivo": lead.get("objetivo", "indefinido"),
                "motivacion": lead.get("motivacion", "media"),
                "nivel_compromiso": lead.get("nivel_compromiso", "medio"),
                "submitted_at": lead.get("submitted_at"),
                "notas_admin": lead.get("notas_admin", [])
            })
        
        return leads_response
        
    except Exception as e:
        logger.error(f"Error fetching waitlist leads: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener leads")


@api_router.get("/admin/waitlist/{lead_id}")
async def get_waitlist_lead_detail(lead_id: str, request: Request):
    """
    Obtener detalle completo de un lead
    """
    current_user = await get_current_user(request)
    
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    try:
        lead = await db.waitlist_leads.find_one({"_id": lead_id})
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        return lead
        
    except Exception as e:
        logger.error(f"Error fetching lead detail: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener detalle del lead")


@api_router.put("/admin/waitlist/{lead_id}/status")
async def update_waitlist_lead_status(lead_id: str, status_update: WaitlistStatusUpdate, request: Request):
    """
    Actualizar estado de un lead
    """
    current_user = await get_current_user(request)
    
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    try:
        update_data = {
            "estado": status_update.estado
        }
        
        # Si se marca como contactado, guardar timestamp
        if status_update.estado == "contactado":
            update_data["contacted_at"] = datetime.now(timezone.utc).isoformat()
        
        result = await db.waitlist_leads.update_one(
            {"_id": lead_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        logger.info(f"✅ Lead {lead_id} status updated to {status_update.estado}")
        
        return {"success": True, "message": "Estado actualizado"}
        
    except Exception as e:
        logger.error(f"Error updating lead status: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar estado")


@api_router.post("/admin/waitlist/{lead_id}/note")
async def add_waitlist_lead_note(lead_id: str, note_data: WaitlistNoteAdd, request: Request):
    """
    Añadir nota a un lead
    """
    current_user = await get_current_user(request)
    
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    try:
        nota = {
            "texto": note_data.nota,
            "fecha": datetime.now(timezone.utc).isoformat(),
            "admin_id": current_user.get("_id"),
            "admin_name": current_user.get("name", "Admin")
        }
        
        result = await db.waitlist_leads.update_one(
            {"_id": lead_id},
            {"$push": {"notas_admin": nota}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        logger.info(f"✅ Note added to lead {lead_id}")
        
        return {"success": True, "message": "Nota añadida", "nota": nota}
        
    except Exception as e:
        logger.error(f"Error adding note: {e}")
        raise HTTPException(status_code=500, detail="Error al añadir nota")


# ============================================
# MANUAL PAYMENTS (CAJA A / CAJA B)
# ============================================

@api_router.get("/admin/manual-payments")
async def get_manual_payments(request: Request):
    """Obtener todos los pagos manuales (Caja A y B)"""
    current_user = await get_current_user(request)
    
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    try:
        payments = await db.manual_payments.find().sort("fecha", -1).to_list(length=1000)
        return {"success": True, "payments": payments}
    except Exception as e:
        logger.error(f"Error fetching manual payments: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener pagos")


@api_router.post("/admin/manual-payments")
async def create_manual_payment(payment_data: ManualPaymentCreate, request: Request):
    """Crear pago manual"""
    current_user = await get_current_user(request)
    
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    try:
        payment_id = str(int(datetime.now(timezone.utc).timestamp() * 1000000))
        
        payment = {
            "_id": payment_id,
            "concepto": payment_data.concepto,
            "amount": payment_data.amount,
            "fecha": payment_data.fecha,
            "metodo_pago": payment_data.metodo_pago,
            "notas": payment_data.notas or "",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "created_by": current_user.get("name", "Admin")
        }
        
        await db.manual_payments.insert_one(payment)
        
        logger.info(f"✅ Manual payment created: {payment_data.concepto} - {payment_data.amount}€ - {payment_data.metodo_pago}")
        
        return {"success": True, "message": "Pago registrado", "payment": payment}
        
    except Exception as e:
        logger.error(f"Error creating manual payment: {e}")
        raise HTTPException(status_code=500, detail="Error al crear pago")


@api_router.put("/admin/manual-payments/{payment_id}")
async def update_manual_payment(payment_id: str, payment_data: ManualPaymentCreate, request: Request):
    """Actualizar pago manual"""
    current_user = await get_current_user(request)
    
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    try:
        update_data = {
            "concepto": payment_data.concepto,
            "amount": payment_data.amount,
            "fecha": payment_data.fecha,
            "metodo_pago": payment_data.metodo_pago,
            "notas": payment_data.notas or ""
        }
        
        result = await db.manual_payments.update_one(
            {"_id": payment_id},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        logger.info(f"✅ Manual payment updated: {payment_id}")
        
        return {"success": True, "message": "Pago actualizado"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating manual payment: {e}")
        raise HTTPException(status_code=500, detail="Error al actualizar pago")


@api_router.delete("/admin/manual-payments/{payment_id}")
async def delete_manual_payment(payment_id: str, request: Request):
    """Eliminar pago manual"""
    current_user = await get_current_user(request)
    
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    try:
        result = await db.manual_payments.delete_one({"_id": payment_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Pago no encontrado")
        
        logger.info(f"✅ Manual payment deleted: {payment_id}")
        
        return {"success": True, "message": "Pago eliminado"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting manual payment: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar pago")

        logger.error(f"Error adding note: {e}")
        raise HTTPException(status_code=500, detail="Error al añadir nota")


@api_router.delete("/admin/waitlist/{lead_id}/note/{note_index}")
async def delete_waitlist_lead_note(lead_id: str, note_index: int, request: Request):
    """
    Eliminar una nota específica de un lead
    """
    current_user = await get_current_user(request)
    
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    try:
        # Obtener el lead
        lead = await db.waitlist_leads.find_one({"_id": lead_id})
        
        if not lead:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        notas = lead.get("notas_admin", [])
        
        if note_index < 0 or note_index >= len(notas):
            raise HTTPException(status_code=404, detail="Nota no encontrada")
        
        # Eliminar la nota por índice
        notas.pop(note_index)
        
        # Actualizar el documento
        result = await db.waitlist_leads.update_one(
            {"_id": lead_id},
            {"$set": {"notas_admin": notas}}
        )
        
        logger.info(f"✅ Note {note_index} deleted from lead {lead_id}")
        
        return {"success": True, "message": "Nota eliminada"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting note: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar nota")


@api_router.delete("/admin/waitlist/{lead_id}")
async def delete_waitlist_lead(lead_id: str, request: Request):
    """
    Eliminar un lead de waitlist
    """
    current_user = await get_current_user(request)
    
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="No autorizado")
    
    try:
        result = await db.waitlist_leads.delete_one({"_id": lead_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Lead no encontrado")
        
        logger.info(f"✅ Lead {lead_id} deleted")
        
        return {"success": True, "message": "Lead eliminado"}
        
    except Exception as e:
        logger.error(f"Error deleting lead: {e}")
        raise HTTPException(status_code=500, detail="Error al eliminar lead")


# ============================================
# E.D.N.360 SYSTEM ENDPOINTS
# ⚠️ DESACTIVADOS TEMPORALMENTE - Migración a client_drawer
# ============================================

# ⚠️ COMENTADO: Orquestador eliminado durante migración
# from edn360.orchestrator import EDN360Orchestrator
# from edn360.models import PlanType, PlanStatus

# ⚠️ COMENTADO: Orquestador no disponible
# edn360_orchestrator = EDN360Orchestrator()

@api_router.post("/admin/edn360/generate-initial-plan")
async def generate_edn360_initial_plan(
    request: Request,
    questionnaire_id: str = Form(...),
    client_id: str = Form(...),
    admin_notes: Optional[str] = Form(None)
):
    """
    Genera un plan inicial E.D.N.360 completo (Entrenamiento + Nutrición)
    usando los 18 agentes especializados (E1-E9 + N0-N8)
    """
    await require_admin(request)
    
    try:
        logger.info(f"🚀 Generando plan E.D.N.360 para cliente {client_id}")
        
        # Obtener cuestionario
        questionnaire = await db.questionnaires.find_one({"_id": questionnaire_id})
        if not questionnaire:
            raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
        
        # Obtener datos del cliente
        client = await db.users.find_one({"_id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Generar ID único para el plan
        plan_id = f"edn360_{client_id}_{int(datetime.now(timezone.utc).timestamp())}"
        
        # Ejecutar orquestador
        result = await edn360_orchestrator.generate_initial_plan(
            questionnaire_data=questionnaire,
            client_data=client,
            plan_id=plan_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Error generando plan"))
        
        # Guardar plan en MongoDB
        now = datetime.now(timezone.utc)
        edn360_plan = {
            "_id": plan_id,
            "client_id": client_id,
            "client_name": client.get("name", ""),
            "plan_type": "initial_complete",
            "status": "draft",
            "created_at": now,
            "updated_at": now,
            "generated_at": now,
            "questionnaire_id": questionnaire_id,
            "training_plan": result["training_plan"],
            "nutrition_plan": result["nutrition_plan"],
            "agent_executions": result["agent_executions"],
            "validation": result["validation"],
            "total_duration_seconds": result["total_duration_seconds"],
            "admin_notes": admin_notes,
            "current_version": 1,
            "modifications": []
        }
        
        await db.edn360_plans.insert_one(edn360_plan)
        
        logger.info(f"✅ Plan E.D.N.360 generado exitosamente: {plan_id}")
        
        return {
            "success": True,
            "plan_id": plan_id,
            "status": "draft",
            "message": "Plan generado exitosamente",
            "duration_seconds": result["total_duration_seconds"],
            "validation": result["validation"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generando plan E.D.N.360: {e}")
        raise HTTPException(status_code=500, detail=f"Error generando plan: {str(e)}")


@api_router.post("/admin/edn360/generate-followup-plan")
async def generate_edn360_followup_plan(
    request: Request,
    client_id: str = Form(...),
    followup_questionnaire_id: str = Form(...),
    admin_notes: Optional[str] = Form(None)
):
    """
    Genera un plan de seguimiento mensual E.D.N.360
    usando los 8 agentes de seguimiento (ES1-ES4 + NS1-NS4)
    """
    await require_admin(request)
    
    try:
        logger.info(f"🔄 Generando seguimiento E.D.N.360 para cliente {client_id}")
        
        # Obtener cuestionario de seguimiento
        followup = await db.followup_questionnaires.find_one({"_id": followup_questionnaire_id})
        if not followup:
            raise HTTPException(status_code=404, detail="Cuestionario de seguimiento no encontrado")
        
        # Obtener plan anterior
        previous_plan = await db.edn360_plans.find_one(
            {"client_id": client_id},
            sort=[("created_at", -1)]
        )
        if not previous_plan:
            raise HTTPException(status_code=404, detail="No hay plan anterior para este cliente")
        
        # Obtener datos del cliente
        client = await db.users.find_one({"_id": client_id})
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # Generar ID único
        plan_id = f"edn360_followup_{client_id}_{int(datetime.now(timezone.utc).timestamp())}"
        
        # Ejecutar orquestador de seguimiento
        result = await edn360_orchestrator.generate_followup_plan(
            followup_questionnaire=followup,
            previous_plan=previous_plan,
            client_data=client,
            plan_id=plan_id
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("error", "Error generando seguimiento"))
        
        # Guardar plan de seguimiento
        now = datetime.now(timezone.utc)
        followup_plan = {
            "_id": plan_id,
            "client_id": client_id,
            "client_name": client.get("name", ""),
            "plan_type": "followup_complete",
            "status": "draft",
            "created_at": now,
            "updated_at": now,
            "generated_at": now,
            "followup_questionnaire_id": followup_questionnaire_id,
            "previous_plan_id": previous_plan["_id"],
            "training_adjustments": result["training_adjustments"],
            "nutrition_adjustments": result["nutrition_adjustments"],
            "agent_executions": result["agent_executions"],
            "validation": result["validation"],
            "total_duration_seconds": result["total_duration_seconds"],
            "admin_notes": admin_notes,
            "current_version": 1,
            "modifications": []
        }
        
        await db.edn360_plans.insert_one(followup_plan)
        
        logger.info(f"✅ Seguimiento E.D.N.360 generado: {plan_id}")
        
        return {
            "success": True,
            "plan_id": plan_id,
            "status": "draft",
            "message": "Plan de seguimiento generado exitosamente",
            "duration_seconds": result["total_duration_seconds"],
            "validation": result["validation"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generando seguimiento E.D.N.360: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@api_router.get("/admin/edn360/plans/{plan_id}")
async def get_edn360_plan(plan_id: str, request: Request):
    """
    Obtiene un plan E.D.N.360 específico
    """
    await require_admin(request)
    
    try:
        plan = await db.edn360_plans.find_one({"_id": plan_id})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo plan: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener plan")


@api_router.get("/admin/edn360/client/{client_id}/plans")
async def get_client_edn360_plans(client_id: str, request: Request):
    """
    Obtiene todos los planes E.D.N.360 de un cliente
    """
    await require_admin(request)
    
    try:
        plans = await db.edn360_plans.find(
            {"client_id": client_id}
        ).sort("created_at", -1).to_list(length=100)
        
        return {
            "success": True,
            "plans": plans,
            "count": len(plans)
        }
        
    except Exception as e:
        logger.error(f"Error obteniendo planes del cliente: {e}")
        raise HTTPException(status_code=500, detail="Error al obtener planes")


@api_router.put("/admin/edn360/plans/{plan_id}/approve")
async def approve_edn360_plan(plan_id: str, request: Request):
    """
    Aprueba un plan E.D.N.360 (cambia status de draft a approved)
    """
    await require_admin(request)
    
    try:
        result = await db.edn360_plans.update_one(
            {"_id": plan_id},
            {
                "$set": {
                    "status": "approved",
                    "approved_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        logger.info(f"✅ Plan aprobado: {plan_id}")
        
        return {"success": True, "message": "Plan aprobado"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error aprobando plan: {e}")
        raise HTTPException(status_code=500, detail="Error al aprobar plan")


@api_router.post("/admin/edn360/plans/{plan_id}/send")
async def send_edn360_plan(
    plan_id: str,
    request: Request,
    delivery_method: str = Form(...),  # "email", "whatsapp", "attach_to_docs"
    custom_message: Optional[str] = Form(None)
):
    """
    Envía un plan E.D.N.360 al cliente
    """
    await require_admin(request)
    
    try:
        plan = await db.edn360_plans.find_one({"_id": plan_id})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        client = await db.users.find_one({"_id": plan["client_id"]})
        if not client:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        
        # TODO: Implementar envío según método
        if delivery_method == "email":
            # Enviar por email
            pass
        elif delivery_method == "whatsapp":
            # Enviar por WhatsApp
            pass
        elif delivery_method == "attach_to_docs":
            # Adjuntar a documentos del cliente
            pass
        
        # Actualizar estado del plan
        await db.edn360_plans.update_one(
            {"_id": plan_id},
            {
                "$set": {
                    "status": "sent",
                    "sent_at": datetime.now(timezone.utc),
                    "delivery_method": delivery_method,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        logger.info(f"✅ Plan enviado vía {delivery_method}: {plan_id}")
        
        return {
            "success": True,
            "message": f"Plan enviado vía {delivery_method}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enviando plan: {e}")
        raise HTTPException(status_code=500, detail="Error al enviar plan")


@api_router.post("/admin/edn360/plans/{plan_id}/chat")
async def chat_modify_edn360_plan(
    plan_id: str,
    request: Request,
    message: str = Form(...),
    context: Optional[str] = Form(None)
):
    """
    Chat con IA para modificar un plan E.D.N.360 existente
    Usa GPT-4o para entender la solicitud y aplicar cambios
    """
    await require_admin(request)
    
    try:
        # Obtener plan
        plan = await db.edn360_plans.find_one({"_id": plan_id})
        if not plan:
            raise HTTPException(status_code=404, detail="Plan no encontrado")
        
        # Obtener historial de chat
        chat_history = plan.get("chat_history", [])
        
        # Preparar contexto del plan para la IA
        plan_context = f"""
# Plan E.D.N.360 Actual

**Cliente:** {plan.get('client_name')}
**Tipo de Plan:** {plan.get('plan_type')}
**Estado:** {plan.get('status')}

## Plan de Entrenamiento:
{json.dumps(plan.get('training_plan', {}), indent=2, ensure_ascii=False)}

## Plan de Nutrición:
{json.dumps(plan.get('nutrition_plan', {}), indent=2, ensure_ascii=False)}

## Historial de Modificaciones:
{json.dumps(plan.get('modifications', []), indent=2, ensure_ascii=False)}
"""
        
        # Prompt del sistema para modificaciones
        system_prompt = """Eres un experto entrenador y nutricionista que ayuda a modificar planes E.D.N.360.

Tu trabajo es:
1. Entender la solicitud de modificación del administrador
2. Identificar qué partes del plan deben cambiar
3. Aplicar los cambios de forma precisa y profesional
4. Mantener la coherencia del plan (reglas E.D.N.360)
5. Explicar los cambios realizados

REGLAS IMPORTANTES:
- Sesiones ≤90 minutos
- Proteína ≥1.8 g/kg
- Grasas ≥0.6 g/kg
- Equilibrios Push/Pull (0.9-1.1)
- CIT óptimo: 35-55

Si la solicitud es solo una pregunta sin cambios, responde sin modificar el plan.
Si requiere cambios, genera el plan modificado en formato JSON."""
        
        # Preparar mensaje para la IA
        full_message = f"""{plan_context}

---

**Solicitud del Administrador:**
{message}

{f"**Contexto adicional:** {context}" if context else ""}

---

Analiza la solicitud y genera el plan modificado o responde la pregunta."""
        
        # Ejecutar LLM
        from openai import AsyncOpenAI
        
        openai_key = os.environ.get("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY no configurada en el entorno")
        
        client = AsyncOpenAI(api_key=openai_key)
        
        completion = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_message}
            ],
            temperature=0.7,
            max_tokens=4000,
            timeout=120
        )
        
        ai_response = completion.choices[0].message.content
        
        # Intentar detectar si hay modificaciones en la respuesta
        modifications_made = False
        modified_plan = None
        
        try:
            # Buscar JSON en la respuesta
            import re
            json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
            matches = re.findall(json_pattern, ai_response, re.DOTALL)
            
            if matches:
                modified_plan = json.loads(matches[0])
                modifications_made = True
        except:
            pass
        
        # Actualizar historial de chat
        chat_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_message": message,
            "ai_response": ai_response,
            "modifications_made": modifications_made
        }
        chat_history.append(chat_entry)
        
        # Actualizar plan en DB
        update_data = {
            "chat_history": chat_history,
            "updated_at": datetime.now(timezone.utc)
        }
        
        if modifications_made and modified_plan:
            # Incrementar versión
            new_version = plan.get("current_version", 1) + 1
            
            # Registrar modificación
            modification = {
                "version": new_version,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "modification_type": "chat_ai",
                "message": message,
                "changes_applied": ai_response[:500]  # Resumen
            }
            
            modifications = plan.get("modifications", [])
            modifications.append(modification)
            
            update_data.update({
                "training_plan": modified_plan.get("training_plan", plan.get("training_plan")),
                "nutrition_plan": modified_plan.get("nutrition_plan", plan.get("nutrition_plan")),
                "current_version": new_version,
                "modifications": modifications
            })
            
            logger.info(f"✅ Plan {plan_id} modificado vía chat (v{new_version})")
        
        await db.edn360_plans.update_one(
            {"_id": plan_id},
            {"$set": update_data}
        )
        
        return {
            "success": True,
            "ai_response": ai_response,
            "modifications_made": modifications_made,
            "new_version": plan.get("current_version", 1) + 1 if modifications_made else plan.get("current_version", 1)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en chat modificación: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============================================================================
# GENERATION JOBS - Sistema Asíncrono de Generación de Planes con Estabilización
# ============================================================================

# ========== HELPER FUNCTIONS ==========

async def add_job_log(job_id: str, event: str, details: str = ""):
    """Añade un evento al log del job"""
    log_entry = {
        "timestamp": datetime.now(timezone.utc),
        "event": event,
        "details": details
    }
    await db.generation_jobs.update_one(
        {"_id": job_id},
        {"$push": {"execution_log": log_entry}}
    )

async def update_job_progress(job_id: str, phase: str, current_agent: str, completed: int, total: int, message: str):
    """Actualiza el progreso del job después de cada agente REAL"""
    percentage = int((completed / total) * 100)
    
    await db.generation_jobs.update_one(
        {"_id": job_id},
        {
            "$set": {
                "progress.phase": phase,
                "progress.current_agent": current_agent,
                "progress.completed_steps": completed,
                "progress.total_steps": total,
                "progress.percentage": percentage,
                "progress.message": message
            }
        }
    )
    
    logger.info(f"  📊 Progreso actualizado: {current_agent} completado ({percentage}%)")

async def check_job_concurrency(job_id: str) -> bool:
    """
    Verifica si hay espacio para ejecutar el job.
    Límite: 2 jobs simultáneos en "running"
    Si no hay espacio, marca el job como "queued"
    """
    running_jobs = await db.generation_jobs.count_documents({"status": "running"})
    
    if running_jobs >= 2:
        logger.info(f"⏳ Job {job_id} en cola (2 jobs ya en ejecución)")
        await db.generation_jobs.update_one(
            {"_id": job_id},
            {"$set": {"status": "queued"}}
        )
        await add_job_log(job_id, "queued", f"{running_jobs} jobs en ejecución")
        return False
    
    return True

async def execute_with_retry(func, max_retries=2, *args, **kwargs):
    """
    Ejecuta una función con retry automático para errores de OpenAI
    Reintentos: 2 con delays de 10s y 30s
    """
    delays = [10, 30]
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            result = await func(*args, **kwargs)
            if attempt > 0:
                logger.info(f"  ✅ Reintento exitoso (intento {attempt + 1})")
            return result, attempt
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            
            # Solo reintentar en errores recuperables (rate limit, timeout)
            is_retryable = any(keyword in error_str for keyword in [
                "rate limit", "timeout", "429", "503", "connection"
            ])
            
            if attempt < max_retries and is_retryable:
                delay = delays[attempt]
                logger.warning(f"  ⚠️ Error recuperable, reintentando en {delay}s (intento {attempt + 1}/{max_retries + 1})")
                await asyncio.sleep(delay)
            else:
                logger.error(f"  ❌ Error no recuperable o límite de reintentos alcanzado")
                raise last_error
    
    raise last_error

async def process_generation_job(job_id: str):
    """
    Procesa un job de generación en background con estabilización.
    
    MEJORAS IMPLEMENTADAS:
    - ✅ Control de concurrencia (máx 2 jobs simultáneos)
    - ✅ Progreso REAL después de cada agente
    - ✅ Retry automático (2 reintentos con delays 10s, 30s)
    - ✅ Logging de eventos
    - ✅ Timeout será manejado por watchdog externo
    """
    retry_count = 0
    
    try:
        # Cargar el job
        job = await db.generation_jobs.find_one({"_id": job_id})
        if not job:
            logger.error(f"❌ Job {job_id} no encontrado")
            return
        
        logger.info(f"🚀 Iniciando procesamiento de job {job_id} (type: {job['type']})")
        
        # 1️⃣ CONTROL DE CONCURRENCIA
        can_run = await check_job_concurrency(job_id)
        if not can_run:
            # Job marcado como "queued", salir
            return
        
        # 2️⃣ CAMBIAR STATUS A RUNNING + LOG
        await db.generation_jobs.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "running",
                    "started_at": datetime.now(timezone.utc),
                    "execution_log": []  # Inicializar log
                }
            }
        )
        await add_job_log(job_id, "started", f"Iniciando generación (mode: {job['type']})")
        
        # Obtener datos necesarios
        user_id = job["user_id"]
        submission_id = job["submission_id"]
        job_type = job["type"]
        
        # Obtener usuario
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise Exception(f"Usuario {user_id} no encontrado")
        
        # Obtener cuestionario
        submission = await db.nutrition_questionnaire_submissions.find_one({"_id": submission_id})
        is_followup = False
        context_data = None
        
        if not submission:
            # Buscar en follow-ups
            submission = await db.follow_up_submissions.find_one({"_id": submission_id})
            is_followup = True
            
            if not submission:
                raise Exception(f"Cuestionario {submission_id} no encontrado en nutrition_questionnaire_submissions ni follow_up_submissions")
        
        # VALIDACIÓN ROBUSTA DEL CUESTIONARIO
        logger.info(f"🔍 Validando formato del cuestionario {submission_id}")
        
        submission_to_validate = submission
        
        # Si es followup, obtener cuestionario inicial para validar
        if is_followup:
            logger.info(f"📋 Detectado follow-up, obteniendo cuestionario inicial para validación")
            initial_submission = await db.nutrition_questionnaire_submissions.find_one(
                {"user_id": user_id},
                sort=[("submitted_at", 1)]
            )
            
            if not initial_submission:
                raise Exception("No se encontró cuestionario inicial para contexto del follow-up")
            
            submission_to_validate = initial_submission
        
        # Validar el formato del cuestionario
        is_valid, validation_errors, questionnaire_data = _validate_questionnaire_format(submission_to_validate)
        
        if not is_valid:
            error_msg = "❌ FORMATO DE CUESTIONARIO INVÁLIDO:\n" + "\n".join(f"  • {e}" for e in validation_errors)
            error_msg += "\n\n📋 FORMATO ESPERADO: El cuestionario debe guardarse en MongoDB con estructura:\n"
            error_msg += "{\n"
            error_msg += "  '_id': 'timestamp_unico',\n"
            error_msg += "  'user_id': 'id_usuario',\n"
            error_msg += "  'responses': {\n"
            error_msg += "    'nombre_completo': 'string',\n"
            error_msg += "    'email': 'string',\n"
            error_msg += "    'fecha_nacimiento': 'YYYY-MM-DD',\n"
            error_msg += "    'sexo': 'Hombre/Mujer',\n"
            error_msg += "    'peso': 'string',\n"
            error_msg += "    'altura_cm': 'string',\n"
            error_msg += "    'objetivo_fisico': 'string',\n"
            error_msg += "    ... (otros campos del cuestionario)\n"
            error_msg += "  },\n"
            error_msg += "  'submitted_at': datetime,\n"
            error_msg += "  'plan_generated': boolean\n"
            error_msg += "}"
            
            logger.error(error_msg)
            raise Exception(error_msg)
        
        logger.info(f"✅ Cuestionario validado correctamente")
        
        # Si es followup, combinar con datos del follow-up
        if is_followup:
            submission_serialized = _serialize_datetime_fields(submission)
            context_data = {
                "followup_responses": submission_serialized.get("responses", {}),
                "ai_analysis": submission_serialized.get("ai_analysis", "")
            }
            
            # Combinar datos
            merged_data = questionnaire_data.copy()
            merged_data.update(context_data.get("followup_responses", {}))
            adapted_questionnaire = _adapt_questionnaire_for_edn360(merged_data)
        else:
            # Usar datos validados directamente
            adapted_questionnaire = _adapt_questionnaire_for_edn360(questionnaire_data)
        
        # Obtener fecha actual
        now = datetime.now(timezone.utc)
        current_month = now.month
        current_year = now.year
        
        # Importar orquestador
        # ⚠️ DESACTIVADO: from edn360.orchestrator import EDN360Orchestrator
        # ⚠️ DESACTIVADO: orchestrator = EDN360Orchestrator()
        
        result_data = {
            "training_plan_id": None,
            "nutrition_plan_id": None
        }
        
        # EJECUTAR SEGÚN EL TIPO
        if job_type == "training" or job_type == "full":
            # ===== FASE TRAINING (E1-E9) =====
            logger.info("🏋️ Fase TRAINING: Ejecutando agentes E1-E9")
            
            # Actualizar progreso
            await db.generation_jobs.update_one(
                {"_id": job_id},
                {
                    "$set": {
                        "progress.phase": "training",
                        "progress.current_agent": "E1",
                        "progress.message": "Iniciando análisis del perfil del cliente (E1)"
                    }
                }
            )
            
            # Obtener plan de entrenamiento previo si existe
            previous_training_plan = None
            if job.get("previous_training_plan_id"):
                previous_training_plan = await db.training_plans.find_one({"_id": job["previous_training_plan_id"]})
            
            await add_job_log(job_id, "training_started", "Iniciando pipeline E1-E9")
            
            # 3️⃣ EJECUTAR PIPELINE CON RETRY
            async def run_training_pipeline():
                return await orchestrator._execute_training_initial(
                    adapted_questionnaire,
                    previous_plan=previous_training_plan
                )
            
            training_result, retry_count = await execute_with_retry(run_training_pipeline)
            
            if not training_result["success"]:
                raise Exception(f"Error en pipeline de training: {training_result.get('error', 'Error desconocido')}")
            
            # 4️⃣ ACTUALIZAR PROGRESO REAL BASADO EN EXECUTIONS
            # El orquestador devuelve executions con info de cada agente ejecutado
            executions = training_result.get("executions", [])
            total_steps = 9 if job_type == "training" else 18
            
            if executions:
                for idx, execution in enumerate(executions):
                    agent_id = execution.get("agent_id", f"E{idx+1}")
                    completed = idx + 1
                    
                    # Capturar tokens del agente
                    token_usage = execution.get("token_usage")
                    if token_usage:
                        await db.generation_jobs.update_one(
                            {"_id": job_id},
                            {
                                "$inc": {
                                    "token_usage.total_prompt_tokens": token_usage.get("prompt_tokens", 0),
                                    "token_usage.total_completion_tokens": token_usage.get("completion_tokens", 0),
                                    "token_usage.total_tokens": token_usage.get("total_tokens", 0)
                                },
                                "$set": {
                                    f"token_usage.by_agent.{agent_id}": token_usage
                                }
                            }
                        )
                    
                    await update_job_progress(
                        job_id,
                        "training",
                        agent_id,
                        completed,
                        total_steps,
                        f"Agente {agent_id} completado"
                    )
                    await add_job_log(job_id, "agent_completed", f"{agent_id} ejecutado exitosamente")
            else:
                # Fallback si no hay executions
                for i in range(1, 10):
                    agent_name = f"E{i}"
                    await update_job_progress(
                        job_id,
                        "training",
                        agent_name,
                        i,
                        total_steps,
                        f"Agente {agent_name} completado"
                    )
            
            if retry_count > 0:
                await add_job_log(job_id, "retry_success", f"Pipeline completado después de {retry_count} reintento(s)")
            
            # Guardar plan de entrenamiento
            planes_previos_count = await db.training_plans.count_documents({"user_id": user_id})
            numero_mes = planes_previos_count + 1
            
            plan_id = str(int(datetime.now(timezone.utc).timestamp() * 1000000))
            plan_data_json = _format_edn360_plan_for_display(training_result["plan_data"])
            
            # FUENTE DE VERDAD: edn360_data.formatted_plan (generado por post-procesador)
            formatted_plan = training_result["plan_data"].get("formatted_plan")
            
            if isinstance(formatted_plan, str) and formatted_plan.strip():
                plan_text_professional = formatted_plan
                logger.info("✅ plan_text tomado directamente de edn360_data.formatted_plan (post-procesador)")
            else:
                logger.error("⚠️ formatted_plan ausente o vacío, usando _format_edn360_plan_as_text como fallback")
                plan_text_professional = _format_edn360_plan_as_text(
                    training_result["plan_data"], 
                    user.get("name", user.get("username", "Cliente")), 
                    numero_mes
                )
            
            training_plan_doc = {
                "_id": plan_id,
                "user_id": user_id,
                "month": current_month,
                "year": current_year,
                "source_type": "followup" if is_followup else "initial",
                "source_id": submission_id,
                "previous_plan_id": job.get("previous_training_plan_id"),
                "questionnaire_data": questionnaire_data,
                "edn360_data": training_result["plan_data"],
                "agent_executions": training_result.get("executions", []),
                "system_version": "edn360_v1",
                "agent_1_output": training_result["plan_data"].get("E1", {}),
                "agent_2_output": training_result["plan_data"].get("E2", {}),
                "agent_3_output": training_result["plan_data"].get("E4", {}),
                "plan_final": plan_data_json,
                "plan_text": plan_text_professional,
                "generated_at": now,
                "edited": False,
                "pdf_id": None,
                "pdf_filename": None,
                "sent_email": False,
                "sent_whatsapp": False
            }
            
            await db.training_plans.insert_one(training_plan_doc)
            result_data["training_plan_id"] = plan_id
            
            await add_job_log(job_id, "training_completed", f"Plan de entrenamiento generado: {plan_id}")
            logger.info(f"✅ Plan de entrenamiento generado: {plan_id}")
        
        if job_type == "nutrition" or job_type == "full":
            # ===== FASE NUTRITION (N0-N8) =====
            logger.info("🥗 Fase NUTRITION: Ejecutando agentes N0-N8")
            
            # Actualizar progreso
            await db.generation_jobs.update_one(
                {"_id": job_id},
                {
                    "$set": {
                        "progress.phase": "nutrition",
                        "progress.current_agent": "N0",
                        "progress.message": "Iniciando análisis nutricional (N0)"
                    }
                }
            )
            
            # Obtener plan de entrenamiento para sincronizar
            training_plan_for_sync = None
            if job_type == "full" and result_data["training_plan_id"]:
                # Usar el plan de entrenamiento recién generado
                training_plan_for_sync = await db.training_plans.find_one({"_id": result_data["training_plan_id"]})
            elif job.get("training_plan_id"):
                # Usar plan de entrenamiento especificado
                training_plan_for_sync = await db.training_plans.find_one({"_id": job["training_plan_id"]})
            else:
                # Usar último plan de entrenamiento del usuario
                training_plan_for_sync = await db.training_plans.find_one(
                    {"user_id": user_id},
                    sort=[("generated_at", -1)]
                )
            
            if not training_plan_for_sync:
                raise Exception("No se encontró plan de entrenamiento para sincronizar")
            
            # Obtener plan nutricional previo si existe
            previous_nutrition_plan = None
            if job.get("previous_nutrition_plan_id"):
                previous_nutrition_plan = await db.nutrition_plans.find_one({"_id": job["previous_nutrition_plan_id"]})
            
            await add_job_log(job_id, "nutrition_started", "Iniciando pipeline N0-N8")
            
            # EJECUTAR PIPELINE CON RETRY
            async def run_nutrition_pipeline():
                return await orchestrator._execute_nutrition_initial(
                    adapted_questionnaire,
                    training_plan=training_plan_for_sync,
                    previous_plan=previous_nutrition_plan
                )
            
            nutrition_result, nutrition_retry_count = await execute_with_retry(run_nutrition_pipeline)
            
            if not nutrition_result["success"]:
                raise Exception(f"Error en pipeline de nutrition: {nutrition_result.get('error', 'Error desconocido')}")
            
            # ACTUALIZAR PROGRESO REAL BASADO EN EXECUTIONS
            executions_nutrition = nutrition_result.get("executions", [])
            base_steps = 9 if job_type == "full" else 0
            total_steps = 18 if job_type == "full" else 9
            
            if executions_nutrition:
                for idx, execution in enumerate(executions_nutrition):
                    agent_id = execution.get("agent_id", f"N{idx}")
                    completed = base_steps + idx + 1
                    
                    # Capturar tokens del agente
                    token_usage = execution.get("token_usage")
                    if token_usage:
                        await db.generation_jobs.update_one(
                            {"_id": job_id},
                            {
                                "$inc": {
                                    "token_usage.total_prompt_tokens": token_usage.get("prompt_tokens", 0),
                                    "token_usage.total_completion_tokens": token_usage.get("completion_tokens", 0),
                                    "token_usage.total_tokens": token_usage.get("total_tokens", 0)
                                },
                                "$set": {
                                    f"token_usage.by_agent.{agent_id}": token_usage
                                }
                            }
                        )
                    
                    await update_job_progress(
                        job_id,
                        "nutrition",
                        agent_id,
                        completed,
                        total_steps,
                        f"Agente {agent_id} completado"
                    )
                    await add_job_log(job_id, "agent_completed", f"{agent_id} ejecutado exitosamente")
            else:
                # Fallback
                for i in range(9):
                    agent_name = f"N{i}"
                    completed = base_steps + i + 1
                    
                    await update_job_progress(
                        job_id,
                        "nutrition",
                        agent_name,
                        completed,
                        total_steps,
                        f"Agente {agent_name} completado"
                    )
            
            if nutrition_retry_count > 0:
                await add_job_log(job_id, "retry_success", f"Pipeline nutrition completado después de {nutrition_retry_count} reintento(s)")
            
            # Guardar plan de nutrición
            nutrition_planes_count = await db.nutrition_plans.count_documents({"user_id": user_id})
            numero_plan = nutrition_planes_count + 1
            
            nutrition_plan_id = str(int(datetime.now(timezone.utc).timestamp() * 1000000))
            plan_verificado_json = _format_edn360_nutrition_for_display(nutrition_result["plan_data"])
            plan_text_nutrition = _format_edn360_nutrition_as_text(
                nutrition_result["plan_data"],
                user.get("name", user.get("username", "Cliente")),
                numero_plan
            )
            
            nutrition_plan_doc = {
                "_id": nutrition_plan_id,
                "user_id": user_id,
                "month": current_month,
                "year": current_year,
                "questionnaire_id": submission_id,
                "training_plan_id": training_plan_for_sync["_id"],
                "previous_nutrition_plan_id": job.get("previous_nutrition_plan_id"),
                "questionnaire_data": questionnaire_data,
                "edn360_data": nutrition_result["plan_data"],
                "agent_executions": nutrition_result.get("executions", []),
                "system_version": "edn360_v1",
                "plan_verificado": plan_verificado_json,
                "plan_text": plan_text_nutrition,
                "generated_at": now,
                "edited": False,
                "pdf_id": None,
                "pdf_filename": None,
                "sent_email": False,
                "sent_whatsapp": False
            }
            
            await db.nutrition_plans.insert_one(nutrition_plan_doc)
            result_data["nutrition_plan_id"] = nutrition_plan_id
            
            # Marcar cuestionario como usado
            if not is_followup:
                await db.nutrition_questionnaire_submissions.update_one(
                    {"_id": submission_id},
                    {"$set": {"plan_generated": True}}
                )
            
            logger.info(f"✅ Plan de nutrición generado: {nutrition_plan_id}")
        
        # ===== 5️⃣ JOB COMPLETADO =====
        await db.generation_jobs.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "completed",
                    "progress.phase": "completed",
                    "progress.percentage": 100,
                    "progress.message": "Generación completada exitosamente",
                    "result": result_data,
                    "completed_at": datetime.now(timezone.utc),
                    "retry_count": retry_count
                }
            }
        )
        
        await add_job_log(job_id, "completed", f"Job finalizado exitosamente. Planes generados: {result_data}")
        
        # Obtener token usage final para log
        final_job = await db.generation_jobs.find_one({"_id": job_id})
        if final_job and "token_usage" in final_job:
            usage = final_job["token_usage"]
            logger.info(
                f"💰 JOB {job_id} – tokens: "
                f"prompt={usage.get('total_prompt_tokens', 0)}, "
                f"completion={usage.get('total_completion_tokens', 0)}, "
                f"total={usage.get('total_tokens', 0)}"
            )
        
        logger.info(f"✅ Job {job_id} completado exitosamente")
        
    except Exception as e:
        logger.error(f"❌ Error procesando job {job_id}: {str(e)}")
        
        # Determinar si es timeout o error general
        error_type = "error"
        error_str = str(e).lower()
        if "timeout" in error_str or "time" in error_str:
            error_type = "timeout"
        
        # Actualizar job con error
        await db.generation_jobs.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": "failed",
                    "error_message": str(e),
                    "error_reason": error_type,
                    "completed_at": datetime.now(timezone.utc),
                    "retry_count": retry_count
                }
            }
        )
        
        await add_job_log(job_id, "failed", f"Error: {str(e)}")


# ========== WATCHDOG DE TIMEOUT ==========

async def job_timeout_watchdog():
    """
    1️⃣ TIMEOUT WATCHDOG
    Revisa jobs en "running" por más de 30 minutos y los marca como failed.
    Se ejecuta cada 5 minutos.
    """
    # Delay inicial para permitir que el servidor arranque completamente
    await asyncio.sleep(10)
    
    timeout_minutes = 30
    
    while True:
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
            
            # Buscar jobs en running que empezaron hace más de 30 minutos
            stuck_jobs = await db.generation_jobs.find({
                "status": "running",
                "started_at": {"$lt": cutoff_time}
            }).to_list(length=100)
            
            for job in stuck_jobs:
                job_id = job["_id"]
                logger.warning(f"⚠️ Watchdog: Job {job_id} excedió timeout de {timeout_minutes} min")
                
                # Marcar como failed con timeout
                await db.generation_jobs.update_one(
                    {"_id": job_id},
                    {
                        "$set": {
                            "status": "failed",
                            "error_message": f"Job excedió timeout de {timeout_minutes} minutos",
                            "error_reason": "timeout",
                            "completed_at": datetime.now(timezone.utc)
                        }
                    }
                )
                
                try:
                    await add_job_log(job_id, "timeout", f"Job marcado como failed por timeout ({timeout_minutes} min)")
                except:
                    pass  # Si falla el log, no bloquear
            
            if stuck_jobs:
                logger.info(f"✅ Watchdog: {len(stuck_jobs)} job(s) marcado(s) como failed por timeout")
            
        except Exception as e:
            logger.error(f"❌ Error en watchdog de timeout: {e}")
        
        # Esperar 5 minutos antes de la próxima revisión
        await asyncio.sleep(300)

async def process_queued_jobs():
    """
    4️⃣ PROCESADOR DE COLA
    Revisa jobs en "queued" y los procesa si hay espacio.
    Se ejecuta cada 30 segundos.
    """
    # Delay inicial para permitir que el servidor arranque completamente
    await asyncio.sleep(15)
    
    while True:
        try:
            # Contar jobs en running
            running_count = await db.generation_jobs.count_documents({"status": "running"})
            
            if running_count < 2:
                # Hay espacio, buscar jobs en cola
                queued_jobs = await db.generation_jobs.find(
                    {"status": "queued"}
                ).sort("created_at", 1).limit(2 - running_count).to_list(length=10)
                
                for job in queued_jobs:
                    job_id = job["_id"]
                    logger.info(f"🚀 Procesando job de cola: {job_id}")
                    
                    # Lanzar procesamiento
                    asyncio.create_task(process_generation_job(job_id))
                    await asyncio.sleep(1)  # Pequeño delay entre jobs
        
        except Exception as e:
            logger.error(f"❌ Error en procesador de cola: {e}")
        
        # Esperar 30 segundos antes de la próxima revisión
        await asyncio.sleep(30)


@api_router.post("/admin/users/{user_id}/plans/generate_async")
async def generate_plans_async(
    user_id: str,
    request_data: GenerateAsyncRequest,
    request: Request = None
):
    """
    Genera planes de entrenamiento/nutrición de forma asíncrona usando background jobs.
    """
    await require_admin(request)
    
    try:
        # Validar usuario
        user = await db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # ===== RATE LIMIT: Verificar límite diario por usuario =====
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Contar jobs creados hoy
        jobs_today = await db.generation_jobs.count_documents({
            "user_id": user_id,
            "created_at": {"$gte": today_start}
        })
        
        # Contar jobs FULL creados hoy
        full_jobs_today = await db.generation_jobs.count_documents({
            "user_id": user_id,
            "type": "full",
            "created_at": {"$gte": today_start}
        })
        
        # Aplicar límites
        if request_data.mode == "full" and full_jobs_today >= 5:
            raise HTTPException(
                status_code=429,
                detail="Has alcanzado el límite diario de generación de planes completos (5/día). Vuelve a intentarlo mañana o contacta con soporte si crees que es un error."
            )
        
        if jobs_today >= 10:
            raise HTTPException(
                status_code=429,
                detail="Has alcanzado el límite diario de generación de planes (10/día). Vuelve a intentarlo mañana o contacta con soporte si crees que es un error."
            )
        
        # Validar cuestionario
        submission = await db.nutrition_questionnaire_submissions.find_one({"_id": request_data.submission_id})
        is_followup = False
        
        if not submission:
            submission = await db.follow_up_submissions.find_one({"_id": request_data.submission_id})
            is_followup = True
            
            if not submission:
                raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
        
        if submission["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="El cuestionario no pertenece a este usuario")
        
        # Validar mode
        if request_data.mode not in ["training", "nutrition", "full"]:
            raise HTTPException(status_code=400, detail="mode debe ser 'training', 'nutrition' o 'full'")
        
        # Crear job_id único
        job_id = f"job_{user_id}_{int(datetime.now(timezone.utc).timestamp() * 1000000)}"
        
        # Determinar total_steps según mode
        total_steps = 9 if request_data.mode in ["training", "nutrition"] else 18
        
        # Crear documento de job
        job_doc = {
            "_id": job_id,
            "user_id": user_id,
            "type": request_data.mode,
            "submission_id": request_data.submission_id,
            "training_plan_id": request_data.training_plan_id,
            "previous_nutrition_plan_id": request_data.previous_nutrition_plan_id,
            "previous_training_plan_id": request_data.previous_training_plan_id,
            "status": "pending",
            "progress": {
                "phase": "pending",
                "current_agent": None,
                "completed_steps": 0,
                "total_steps": total_steps,
                "percentage": 0,
                "message": "Job creado, esperando ejecución"
            },
            "result": {
                "training_plan_id": None,
                "nutrition_plan_id": None
            },
            "error_message": None,
            "token_usage": {
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_tokens": 0,
                "by_agent": {}
            },
            "created_at": datetime.now(timezone.utc),
            "started_at": None,
            "completed_at": None
        }
        
        # Guardar job en BD con status="pending"
        await db.generation_jobs.insert_one(job_doc)
        
        logger.info(f"✅ Job {job_id} creado para usuario {user_id} (mode: {request_data.mode}) - Worker externo lo procesará")
        
        # NO ejecutar aquí - el worker externo lo procesará
        # FastAPI solo crea el job y responde
        
        # Responder inmediatamente
        return {
            "success": True,
            "job_id": job_id,
            "status": "pending",
            "message": "Job creado. El worker lo procesará. Use GET /jobs/{job_id} para consultar el estado."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando job de generación: {e}")
        raise HTTPException(status_code=500, detail=f"Error creando job: {str(e)}")


@api_router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """
    Consulta el estado de un job de generación.
    Endpoint público (no requiere autenticación) para simplificar polling.
    """
    try:
        job = await db.generation_jobs.find_one({"_id": job_id})
        
        if not job:
            raise HTTPException(status_code=404, detail="Job no encontrado")
        
        # Serializar datetime fields
        job_serialized = _serialize_datetime_fields(job)
        
        return {
            "job_id": job_serialized["_id"],
            "user_id": job_serialized["user_id"],
            "type": job_serialized["type"],
            "status": job_serialized["status"],
            "progress": job_serialized["progress"],
            "result": job_serialized["result"],
            "error_message": job_serialized.get("error_message"),
            "created_at": job_serialized["created_at"],
            "started_at": job_serialized.get("started_at"),
            "completed_at": job_serialized.get("completed_at")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error consultando job {job_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error consultando job: {str(e)}")




# Include the router in the main app (moved to end to include all endpoints)
app.include_router(api_router)

# Include E4 Debug Router (K1 System)
from e4_debug_endpoint import debug_router
app.include_router(debug_router, prefix="/api")

# Verify database connection at startup
@app.on_event("startup")
async def startup_db_verification():
    try:
        await db.command('ping')
        logger.info(f"✅ Successfully connected to database: {db_name}")
        
        # WATCHDOGS DESHABILITADOS - Causan bloqueo del event loop durante generación
        # TODO: Migrar a worker separado (Celery/RQ) para jobs en background
        # asyncio.create_task(job_timeout_watchdog())
        # asyncio.create_task(process_queued_jobs())
        logger.info("⚠️ Job watchdogs deshabilitados (causan bloqueo del event loop)")
        
    except Exception as e:
        logger.error(f"❌ CRITICAL: Failed to connect to database {db_name}: {e}")
        raise RuntimeError(f"Database connection failed: {e}")


@app.on_event("startup")
async def startup_fase3_indexes():
    """
    Inicializar índices de FASE 3 (edn360_snapshots).
    
    Este startup event crea los índices necesarios en la colección
    edn360_snapshots de la BD edn360_app.
    """
    try:
        logger.info("🔧 Inicializando índices de FASE 3 (edn360_snapshots)...")
        
        from repositories.edn360_snapshot_repository import ensure_snapshot_indexes
        await ensure_snapshot_indexes()
        
        logger.info("✅ Índices de FASE 3 inicializados correctamente")
    
    except Exception as e:
        logger.warning(f"⚠️ Error inicializando índices de FASE 3: {e}")
        # No lanzar error para no bloquear el startup del servidor

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()