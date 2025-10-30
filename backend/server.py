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
    ReminderConfig, ClientRiskStatus
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

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== HELPER FUNCTIONS ====================

async def get_current_user(request: Request):
    user_id = await get_current_user_id_flexible(request)
    user = await db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )
    
    # Create user
    user_dict = {
        "_id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
        "username": user_data.username,
        "email": user_data.email,
        "password": get_password_hash(user_data.password),
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
        "updated_at": datetime.now(timezone.utc)
    }
    
    await db.users.insert_one(user_dict)
    
    # Create token
    access_token = create_access_token(data={"sub": user_dict["_id"]})
    
    # Return user without password
    user_response = {
        "id": user_dict["_id"],
        "username": user_dict["username"],
        "email": user_dict["email"],
        "name": user_dict["name"],
        "role": user_dict["role"],
        "subscription": user_dict["subscription"]
    }
    
    return {"user": user_response, "token": access_token}


@api_router.post("/auth/login", response_model=dict)
async def login(email: str, password: str):
    user = await db.users.find_one({"email": email})
    
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
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
            "role": updated_user["role"]
        }
    }


@api_router.post("/auth/google")
async def google_auth(session_id: str, response: Response):
    """
    Process Google OAuth session_id and create/login user
    """
    # Call Emergent Auth API to get session data
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id},
                timeout=10.0
            )
            auth_response.raise_for_status()
            session_data = auth_response.json()
        except Exception as e:
            logger.error(f"Failed to get session data: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session ID"
            )
    
    # Extract user data
    user_email = session_data.get("email")
    user_name = session_data.get("name")
    user_picture = session_data.get("picture")
    session_token = session_data.get("session_token")
    
    if not user_email or not session_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session data"
        )
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_email})
    
    if existing_user:
        user_id = existing_user["_id"]
        user_data = existing_user
    else:
        # Create new user
        user_id = str(datetime.now(timezone.utc).timestamp()).replace(".", "")
        user_data = {
            "_id": user_id,
            "username": user_name or user_email.split("@")[0],
            "email": user_email,
            "name": user_name or user_email.split("@")[0],
            "password": "",  # No password for OAuth users
            "role": "user",
            "picture": user_picture,
            "subscription": {
                "status": "pending",
                "plan": "team",
                "start_date": datetime.now(timezone.utc),
                "payment_status": "pending",
                "stripe_customer_id": None
            },
            "next_review": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(user_data)
    
    # Store session in database
    session_doc = {
        "_id": str(datetime.now(timezone.utc).timestamp()).replace(".", ""),
        "user_id": user_id,
        "session_token": session_token,
        "expires_at": datetime.now(timezone.utc) + timedelta(days=7),
        "created_at": datetime.now(timezone.utc)
    }
    await db.user_sessions.insert_one(session_doc)
    
    # Set httpOnly cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=7 * 24 * 60 * 60,  # 7 days
        path="/"
    )
    
    # Return user data
    user_response = {
        "id": user_id,
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "name": user_data.get("name"),
        "role": user_data.get("role"),
        "subscription": user_data.get("subscription"),
        "picture": user_data.get("picture")
    }
    
    return {"user": user_response, "session_token": session_token}


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
    
    # Get PDFs
    pdfs = await db.pdfs.find({"user_id": user_id}).to_list(100)
    for pdf in pdfs:
        pdf["id"] = str(pdf["_id"])
    
    # Get alerts
    alerts = await db.alerts.find({"user_id": user_id}).to_list(100)
    for alert in alerts:
        alert["id"] = str(alert["_id"])
    
    # Count unread alerts
    unread_count = len([a for a in alerts if not a.get("read", False)])
    
    return {
        "user": {
            "id": user["_id"],
            "username": user["username"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
            "subscription": user["subscription"],
            "next_review": user.get("next_review")
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
    users = await db.users.find({"role": "user"}).to_list(1000)
    
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
    pdfs = await db.pdfs.find({"user_id": user_id}).to_list(100)
    alerts = await db.alerts.find({"user_id": user_id}).to_list(100)
    
    for form in forms:
        form["id"] = str(form["_id"])
    for pdf in pdfs:
        pdf["id"] = str(pdf["_id"])
    for alert in alerts:
        alert["id"] = str(alert["_id"])
    
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
    # Delete all user data
    await db.forms.delete_many({"user_id": user_id})
    await db.alerts.delete_many({"user_id": user_id})
    await db.messages.delete_many({"user_id": user_id})
    await db.sessions.delete_many({"user_id": user_id})
    await db.user_sessions.delete_many({"user_id": user_id})
    
    # Delete PDFs from filesystem and database
    pdfs = await db.pdfs.find({"user_id": user_id}).to_list(100)
    for pdf in pdfs:
        file_path = Path(pdf["file_path"])
        if file_path.exists():
            file_path.unlink()
    
    await db.pdfs.delete_many({"user_id": user_id})
    
    # Delete user
    result = await db.users.delete_one({"_id": user_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"success": True, "message": "Client and all data deleted successfully"}


# ==================== FORM ENDPOINTS ====================



@api_router.patch("/admin/users/{user_id}")
async def admin_update_user(user_id: str, user_update: AdminUserUpdate, request: Request):
    """Admin updates a client's profile"""
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
        "message": "User updated successfully",
        "user": {
            "id": updated_user["_id"],
            "name": updated_user["name"],
            "email": updated_user["email"],
            "subscription": updated_user["subscription"]
        }
    }


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
    if user["role"] != "admin" and pdf["uploaded_by"] != "user":
        raise HTTPException(status_code=403, detail="You can only delete documents you uploaded")
    
    if user["role"] != "admin" and pdf["user_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete file from filesystem
    file_path = Path(pdf["file_path"])
    if file_path.exists():
        file_path.unlink()
    
    # Delete from database
    await db.pdfs.delete_one({"_id": pdf_id})
    
    return {"success": True, "message": "Document deleted successfully"}


@api_router.get("/pdfs/{pdf_id}/download")
async def download_pdf(pdf_id: str, request: Request):
    user = await get_current_user(request)
    pdf = await db.pdfs.find_one({"_id": pdf_id})
    
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")
    
    # Check if user owns this PDF or is admin
    if pdf["user_id"] != user["_id"] and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    file_path = Path(pdf["file_path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, media_type="application/pdf", filename=file_path.name)


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
    
    # Send email notification to user
    try:
        user = await db.users.find_one({"_id": session["user_id"]})
        if user and user.get("email"):
            # Email al cliente
            send_session_rescheduled_email(
                user_email=user["email"],
                user_name=user.get("name", user.get("username", "")),
                new_date=session_update.date,
                session_title=session.get("title", "Tu sesión")
            )
            # Email al admin
            send_admin_session_rescheduled_email(
                client_name=user.get("name", user.get("username", "")),
                client_email=user["email"],
                old_date=session["date"],
                new_date=session_update.date,
                session_title=session.get("title", "Sesión")
            )
    except Exception as e:
        logger.error(f"Failed to send session rescheduled email: {e}")
    
    return {"success": True, "message": "Session rescheduled successfully"}


@api_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, request: Request):
    admin = await require_admin(request)
    
    # Get session details before deleting (for email notification)
    session = await db.sessions.find_one({"_id": session_id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete the session
    result = await db.sessions.delete_one({"_id": session_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Send email notification to admin
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
    """Submit diagnostic questionnaire and send to admin email"""
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
            "converted_to_client": False
        }
        await db.questionnaire_responses.insert_one(prospect_doc)
        logger.info(f"Questionnaire saved to CRM with ID: {prospect_id}")
        
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
    """Get all team clients (users + converted prospects)"""
    await require_admin(request)
    
    try:
        # Get converted prospects marked as team clients (exclude moved ones)
        query = {"converted_to_client": True, "conversion_type": "team", "moved_to_external": {"$ne": True}}
        if status:
            # We'll need to add status tracking
            pass
        
        converted_prospects = await db.questionnaire_responses.find(query).to_list(length=None)
        
        # Get regular registered users (exclude moved ones)
        users = await db.users.find({"role": "user", "moved_to_external": {"$ne": True}}).to_list(length=None)
        
        # Combine and format
        clients_list = []
        
        # Add converted prospects
        for prospect in converted_prospects:
            clients_list.append({
                "id": prospect["_id"],
                "nombre": prospect.get("nombre"),
                "email": prospect.get("email"),
                "whatsapp": prospect.get("whatsapp"),
                "created_at": prospect.get("converted_at"),
                "status": "active",  # Default status
                "source": "prospect",
                "prospect_data": {
                    "objetivo": prospect.get("objetivo"),
                    "presupuesto": prospect.get("presupuesto"),
                    "intentos_previos": prospect.get("intentos_previos")
                }
            })
        
        # Add registered users
        for user in users:
            clients_list.append({
                "id": user["_id"],
                "nombre": user.get("name"),
                "username": user.get("username"),
                "email": user.get("email"),
                "whatsapp": user.get("whatsapp"),
                "created_at": user.get("created_at"),
                "status": "active",
                "source": "registration"
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
                "nombre": user.get("name"),
                "username": user.get("username"),
                "email": user.get("email"),
                "whatsapp": user.get("whatsapp"),
                "created_at": user.get("created_at"),
                "status": "active",
                "source": "registration",
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
            "amount": float(payment_data.get("amount")),
            "date": datetime.fromisoformat(payment_data.get("date")).replace(tzinfo=timezone.utc),
            "notes": payment_data.get("notes", "")
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
        
        logger.info(f"Payment added to external client {client_id}")
        return {"success": True, "message": "Pago registrado"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding payment: {e}")
        raise HTTPException(status_code=500, detail="Error al registrar pago")


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


# Include the router in the main app
app.include_router(api_router)

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


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()