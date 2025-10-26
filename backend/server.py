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

from models import (
    UserCreate, UserResponse, UserInDB, Subscription,
    FormCreate, FormInDB, PDFCreate, PDFInDB,
    AlertCreate, AlertInDB, MessageCreate, MessageInDB,
    SessionCreate, SessionInDB, SessionUpdate, UserSession,
    Token
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user_id, get_current_user_id_flexible
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
        "_id": str(datetime.utcnow().timestamp()).replace(".", ""),
        "username": user_data.username,
        "email": user_data.email,
        "password": get_password_hash(user_data.password),
        "name": user_data.username,
        "role": "user",
        "subscription": {
            "status": "pending",
            "plan": "team",
            "start_date": datetime.utcnow(),
            "payment_status": "pending",
            "stripe_customer_id": None
        },
        "next_review": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
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
            "updated_at": datetime.utcnow()
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
            "subscription.archived_date": datetime.utcnow(),
            "updated_at": datetime.utcnow()
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
            "updated_at": datetime.utcnow()
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

@api_router.post("/forms/send")
async def send_form(form_data: FormCreate, request: Request):
    admin = await require_admin(request)
    form_dict = {
        "_id": str(datetime.utcnow().timestamp()).replace(".", ""),
        "user_id": form_data.user_id,
        "title": form_data.title,
        "url": form_data.url,
        "completed": False,
        "sent_date": datetime.utcnow(),
        "completed_date": None,
        "created_at": datetime.utcnow()
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
            "completed_date": datetime.utcnow()
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
        "_id": str(datetime.utcnow().timestamp()).replace(".", ""),
        "user_id": user_id,
        "title": title,
        "type": type,
        "file_path": str(file_path),
        "upload_date": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    
    await db.pdfs.insert_one(pdf_dict)
    pdf_dict["id"] = pdf_dict["_id"]
    
    return pdf_dict


@api_router.get("/pdfs/{pdf_id}/download")
async def download_pdf(pdf_id: str, user: dict = Depends(get_current_user)):
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
async def send_alert(alert_data: AlertCreate, admin: dict = Depends(require_admin)):
    alert_dict = {
        "_id": str(datetime.utcnow().timestamp()).replace(".", ""),
        "user_id": alert_data.user_id,
        "title": alert_data.title,
        "message": alert_data.message,
        "type": alert_data.type,
        "link": alert_data.link,
        "read": False,
        "date": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    
    await db.alerts.insert_one(alert_dict)
    alert_dict["id"] = alert_dict["_id"]
    
    return alert_dict


@api_router.patch("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: str, user: dict = Depends(get_current_user)):
    result = await db.alerts.update_one(
        {"_id": alert_id, "user_id": user["_id"]},
        {"$set": {"read": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    return {"success": True}


@api_router.get("/alerts/unread")
async def get_unread_count(user: dict = Depends(get_current_user)):
    count = await db.alerts.count_documents({"user_id": user["_id"], "read": False})
    return {"count": count}


# ==================== MESSAGE/CHAT ENDPOINTS ====================

@api_router.get("/messages/{user_id}")
async def get_messages(user_id: str, current_user: dict = Depends(get_current_user)):
    # Admin can view any user's messages, users can only view their own
    if current_user["role"] != "admin" and current_user["_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    messages = await db.messages.find({"user_id": user_id}).sort("timestamp", 1).to_list(1000)
    
    for message in messages:
        message["id"] = str(message["_id"])
    
    return {"messages": messages}


@api_router.post("/messages/send")
async def send_message(message_data: MessageCreate, current_user: dict = Depends(get_current_user)):
    # Determine user_id based on role
    if current_user["role"] == "admin":
        user_id = message_data.user_id  # Admin specifies which client
    else:
        user_id = current_user["_id"]  # User sends to own conversation
    
    message_dict = {
        "_id": str(datetime.utcnow().timestamp()).replace(".", ""),
        "user_id": user_id,
        "sender_id": current_user["_id"],
        "sender_name": current_user["name"],
        "message": message_data.message,
        "is_admin": current_user["role"] == "admin",
        "timestamp": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    
    await db.messages.insert_one(message_dict)
    message_dict["id"] = message_dict["_id"]
    
    return message_dict


# ==================== SESSION/CALENDAR ENDPOINTS ====================

@api_router.post("/sessions/create")
async def create_session(session_data: SessionCreate, admin: dict = Depends(require_admin)):
    session_dict = {
        "_id": str(datetime.utcnow().timestamp()).replace(".", ""),
        "user_id": session_data.user_id,
        "title": session_data.title,
        "description": session_data.description,
        "date": session_data.date,
        "duration": session_data.duration,
        "type": session_data.type,
        "created_by": admin["_id"],
        "completed": False,
        "created_at": datetime.utcnow()
    }
    
    await db.sessions.insert_one(session_dict)
    session_dict["id"] = session_dict["_id"]
    
    return session_dict


@api_router.get("/sessions/user/{user_id}")
async def get_user_sessions(user_id: str, current_user: dict = Depends(get_current_user)):
    # Users can only see their own sessions, admins can see any
    if current_user["role"] != "admin" and current_user["_id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    sessions = await db.sessions.find({"user_id": user_id}).sort("date", 1).to_list(1000)
    
    for session in sessions:
        session["id"] = str(session["_id"])
    
    return {"sessions": sessions}


@api_router.get("/sessions/admin/all")
async def get_all_sessions(admin: dict = Depends(require_admin)):
    sessions = await db.sessions.find().sort("date", 1).to_list(1000)
    
    for session in sessions:
        session["id"] = str(session["_id"])
    
    return {"sessions": sessions}


@api_router.patch("/sessions/{session_id}/complete")
async def mark_session_complete(session_id: str, admin: dict = Depends(require_admin)):
    result = await db.sessions.update_one(
        {"_id": session_id},
        {"$set": {"completed": True}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True}


@api_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, admin: dict = Depends(require_admin)):
    result = await db.sessions.delete_one({"_id": session_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"success": True}


# ==================== ROOT ENDPOINT ====================

@api_router.get("/")
async def root():
    return {"message": "Jorge Calcerrada API - Working"}


# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()