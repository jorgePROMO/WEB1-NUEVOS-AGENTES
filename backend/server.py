from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Form, Request, Response
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
    WaitlistLeadSubmit, WaitlistLeadInDB, WaitlistLeadResponse,
    WaitlistStatusUpdate, WaitlistNoteAdd,
    ManualPayment, ManualPaymentCreate
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
        frontend_url = os.environ.get('FRONTEND_URL', 'https://web-progress-1.preview.emergentagent.com')
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
    access_token = create_access_token(data={"sub": user["_id"]})
    
    # Return user without password
    user_response = {
        "id": user["_id"],
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
            frontend_url = os.environ.get('FRONTEND_URL', 'https://web-progress-1.preview.emergentagent.com')
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
            "id": user["_id"],
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
    """Submit diagnostic questionnaire and generate GPT report immediately"""
    try:
        # Convert to dict for email function
        questionnaire_data = questionnaire.dict()
        
        # Save to database for CRM
        prospect_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
        prospect_doc = {
            "_id": prospect_id,
            **questionnaire_data,
            "submitted_at": datetime.now(timezone.utc),
            "stage_name": "Nuevo",
            "stage_id": None,
            "converted_to_client": False,
            "report_generated": False,
            "report_sent_at": None,
            "report_content": None,
            "report_sent_via": None  # 'email' or 'whatsapp'
        }
        await db.questionnaire_responses.insert_one(prospect_doc)
        logger.info(f"Questionnaire saved to CRM with ID: {prospect_id}")
        
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
        prospects = await db.questionnaire_responses.find(query).sort("submitted_at", -1).to_list(length=None)
        
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
        notes = await db.prospect_notes.find({"prospect_id": prospect_id}).sort("created_at", -1).to_list(length=None)
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
        stages = await db.prospect_stages.find().sort("order", 1).to_list(length=None)
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
        }).to_list(length=None)
        
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
            notes = await db.team_client_notes.find({"client_id": client_id}).sort("created_at", -1).to_list(length=None)
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
            notes = await db.team_client_notes.find({"client_id": client_id}).sort("created_at", -1).to_list(length=None)
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
        
        clients = await db.external_clients.find(query).sort("created_at", -1).to_list(length=None)
        
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
        # Get tags from templates
        templates = await db.message_templates.find({}).to_list(length=None)
        template_tags = set()
        for template in templates:
            if template.get("tags"):
                template_tags.update(template["tags"])
        
        # Get tags from global_tags collection
        global_tags_docs = await db.global_tags.find({}).to_list(length=None)
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
        
        templates = await db.message_templates.find(query).to_list(length=None)
        
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
        }).to_list(length=None)
        
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
            }).to_list(length=None)
            
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
    """Usuario completa cuestionario de nutrición - SOLO GUARDA RESPUESTAS (no genera plan)"""
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
        
        # Guardar SOLO LAS RESPUESTAS en la colección nutrition_questionnaire_submissions
        submission_doc = {
            "_id": submission_id,
            "user_id": user_id,
            "responses": questionnaire_data,
            "submitted_at": datetime.now(timezone.utc),
            "plan_generated": False,  # El admin generará el plan después
            "plan_id": None
        }
        
        await db.nutrition_questionnaire_submissions.insert_one(submission_doc)
        
        logger.info(f"✅ Cuestionario guardado para usuario {user_id} - {submission_id}")
        
        # Responder INMEDIATAMENTE al frontend
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
async def admin_generate_nutrition_plan(user_id: str, submission_id: str, regenerate: bool = False, request: Request = None):
    """Admin genera el plan de nutrición desde las respuestas del cuestionario"""
    await require_admin(request)
    
    try:
        # Obtener la submission del cuestionario
        submission = await db.nutrition_questionnaire_submissions.find_one({"_id": submission_id})
        
        if not submission:
            raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
        
        if submission["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="El cuestionario no pertenece a este usuario")
        
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
        
        logger.info(f"🔄 Admin iniciando generación de plan para usuario {user_id} - submission {submission_id}")
        
        # Generar el plan con el LLM
        from nutrition_service import generate_nutrition_plan
        result = await generate_nutrition_plan(questionnaire_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error generando plan: {result.get('error', 'Error desconocido')}"
            )
        
        # Guardar el plan en nutrition_plans
        nutrition_plan_doc = {
            "_id": plan_id,
            "user_id": user_id,
            "month": current_month,
            "year": current_year,
            "questionnaire_data": questionnaire_data,
            "plan_inicial": result["plan_inicial"],
            "plan_verificado": result["plan_verificado"],
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
    ).sort("generated_at", -1).to_list(length=None)
    
    # Obtener submissions del cuestionario (respuestas sin plan generado)
    submissions = await db.nutrition_questionnaire_submissions.find(
        {"user_id": user_id}
    ).sort("submitted_at", -1).to_list(length=None)
    
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
        month = plan.get("month")
        year = plan.get("year")
        
        month_names = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
                       "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
        
        # Crear mensaje para WhatsApp (con límite de caracteres)
        message = f"""🥗 *Tu Plan de Nutrición Personalizado - {month_names[month]} {year}*

Hola {user.get('name', 'Cliente')}!

Te envío tu plan de nutrición personalizado:

{plan_content[:3000]}...

_Si necesitas el plan completo, revísalo en tu panel de usuario o te lo envío por email._

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

@api_router.post("/admin/users/{user_id}/training/generate")
async def admin_generate_training_plan(
    user_id: str,
    source_type: str = "initial",  # "initial" or "followup"
    source_id: str = None,  # questionnaire submission ID or followup ID
    regenerate: bool = False,
    request: Request = None
):
    """Admin genera el plan de entrenamiento desde cuestionario inicial o follow-up"""
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
            context_data = {
                "followup_responses": followup.get("responses", {}),
                "ai_analysis": followup.get("ai_analysis", "")
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
        
        logger.info(f"🏋️ Admin iniciando generación de plan de entrenamiento para usuario {user_id}")
        
        # Generar el plan con el servicio de entrenamiento
        from training_service import generate_training_plan, generate_training_plan_with_context
        
        if context_data:
            # Generar con contexto de follow-up
            result = await generate_training_plan_with_context(
                questionnaire_data,
                context_data["followup_responses"],
                context_data["ai_analysis"]
            )
        else:
            # Generar desde cuestionario inicial
            result = await generate_training_plan(questionnaire_data)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Error generando plan: {result.get('error', 'Error desconocido')}"
            )
        
        # Guardar el plan en training_plans
        training_plan_doc = {
            "_id": plan_id,
            "user_id": user_id,
            "month": current_month,
            "year": current_year,
            "source_type": source_type,
            "source_id": source_id,
            "questionnaire_data": questionnaire_data,
            "agent_1_output": result["agent_1_output"],
            "agent_2_output": result["agent_2_output"],
            "agent_3_output": result["agent_3_output"],
            "plan_final": result["plan_final"],
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
    ).sort("generated_at", -1).to_list(length=None)
    
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
    
    plan = await db.training_plans.find_one({"_id": plan_id, "user_id": user_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan de entrenamiento no encontrado")
    
    try:
        from weasyprint import HTML
        import io
        
        plan_content = plan.get("plan_final", "")
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
        
        plan_content = plan.get("plan_final", "")
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
        
        # Contenido del plan (limitado para WhatsApp)
        plan_content = plan.get("plan_final", "")
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
    """
    try:
        current_user = await get_current_user(request)
        user_id = current_user["id"]
        
        # Buscar el plan de nutrición más reciente del usuario
        latest_plan = await db.nutrition_plans.find_one(
            {"user_id": user_id},
            sort=[("generated_at", -1)]
        )
        
        if not latest_plan:
            raise HTTPException(status_code=404, detail="No se encontró un plan de nutrición previo")
        
        # Calcular días desde el último plan
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
        
        # Crear el documento de seguimiento
        follow_up_id = str(datetime.now(timezone.utc).timestamp()).replace('.', '')
        follow_up_doc = {
            "_id": follow_up_id,
            "user_id": user_id,
            "submission_date": datetime.now(timezone.utc),
            "days_since_last_plan": days_since_plan,
            "previous_plan_id": latest_plan["_id"],
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
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.follow_up_submissions.insert_one(follow_up_doc)
        
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
                "date": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc)
            }
            await db.alerts.insert_one(alert_doc)
        
        logger.info(f"Follow-up submission saved for user {user_id}")
        
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
            max_tokens=2000
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
        origin_url = str(request.headers.get("origin", "https://web-progress-1.preview.emergentagent.com"))
        
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
        webhook_url = "https://web-progress-1.preview.emergentagent.com/api/webhook/stripe"
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
        webhook_url = "https://web-progress-1.preview.emergentagent.com/api/webhook/stripe"
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
        
        # Total revenue (todos los pagos exitosos)
        successful_payments = await db.payment_transactions.find({"payment_status": "succeeded"}).to_list(length=None)
        total_revenue = sum(payment["amount"] for payment in successful_payments)
        
        # Revenue del mes actual
        now = datetime.now(timezone.utc)
        start_of_month = datetime(now.year, now.month, 1, tzinfo=timezone.utc).isoformat()
        monthly_payments = [p for p in successful_payments if p["created_at"] >= start_of_month]
        monthly_revenue = sum(payment["amount"] for payment in monthly_payments)
        
        # Revenue del año actual
        start_of_year = datetime(now.year, 1, 1, tzinfo=timezone.utc).isoformat()
        annual_payments = [p for p in successful_payments if p["created_at"] >= start_of_year]
        annual_revenue = sum(payment["amount"] for payment in annual_payments)
        
        # Suscripciones activas y canceladas
        active_subscriptions = await db.user_subscriptions.count_documents({"status": "active"})
        cancelled_subscriptions = await db.user_subscriptions.count_documents({"status": "cancelled"})
        
        # MRR (Monthly Recurring Revenue) - suma de todas las suscripciones activas
        active_subs = await db.user_subscriptions.find({"status": "active"}).to_list(length=None)
        mrr = sum(sub["amount"] for sub in active_subs)
        
        # Total transacciones
        total_transactions = await db.payment_transactions.count_documents({})
        successful_count = len(successful_payments)
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
            "mrr": round(mrr, 2)
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
        exercises = await db.exercises.find().to_list(length=None)
        
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
        
        exercises = await db.exercises.find(mongo_query).to_list(length=None)
        
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
        }).to_list(length=None)
        
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
        muscle_groups = await db.exercises.aggregate(muscle_groups_pipeline).to_list(length=None)
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
            max_tokens=4000
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
        leads = await db.waitlist_leads.find().sort("submitted_at", -1).to_list(length=None)
        
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
        payments = await db.manual_payments.find().sort("fecha", -1).to_list(length=None)
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


# Include the router in the main app (moved to end to include all endpoints)
app.include_router(api_router)

# Verify database connection at startup
@app.on_event("startup")
async def startup_db_verification():
    try:
        await db.command('ping')
        logger.info(f"✅ Successfully connected to database: {db_name}")
    except Exception as e:
        logger.error(f"❌ CRITICAL: Failed to connect to database {db_name}: {e}")
        raise RuntimeError(f"Database connection failed: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()