# API Contracts - Jorge Calcerrada Platform

## Overview
This document defines the API contracts, database models, and integration points between frontend and backend for the Jorge Calcerrada training platform.

## Database Models

### 1. User Model
```python
{
    "_id": ObjectId,
    "username": String (unique, required),
    "email": String (unique, required),
    "password": String (hashed, required),
    "name": String (required),
    "role": String (enum: ["user", "admin"], default: "user"),
    "subscription": {
        "status": String (enum: ["pending", "active", "cancelled"]),
        "plan": String (enum: ["team", "direct"]),
        "start_date": DateTime,
        "payment_status": String (enum: ["pending", "verified"]),
        "stripe_customer_id": String (optional)
    },
    "next_review": DateTime (optional),
    "created_at": DateTime,
    "updated_at": DateTime
}
```

### 2. Form Model
```python
{
    "_id": ObjectId,
    "user_id": ObjectId (ref: User),
    "title": String (required),
    "url": String (required),
    "completed": Boolean (default: False),
    "sent_date": DateTime (required),
    "completed_date": DateTime (optional),
    "created_at": DateTime
}
```

### 3. PDF Document Model
```python
{
    "_id": ObjectId,
    "user_id": ObjectId (ref: User),
    "title": String (required),
    "type": String (enum: ["training", "nutrition"], required),
    "file_path": String (required),  # Cloud storage URL or local path
    "upload_date": DateTime (required),
    "created_at": DateTime
}
```

### 4. Alert Model
```python
{
    "_id": ObjectId,
    "user_id": ObjectId (ref: User),
    "title": String (required),
    "message": String (required),
    "type": String (enum: ["form", "general", "reminder"]),
    "link": String (optional),
    "read": Boolean (default: False),
    "date": DateTime (required),
    "created_at": DateTime
}
```

### 5. Message Model
```python
{
    "_id": ObjectId,
    "user_id": ObjectId (ref: User),  # Client user
    "sender_id": ObjectId (ref: User),  # Who sent the message
    "sender_name": String (required),
    "message": String (required),
    "is_admin": Boolean (required),
    "timestamp": DateTime (required),
    "created_at": DateTime
}
```

## API Endpoints

### Authentication Endpoints

#### POST /api/auth/register
- **Description**: Register a new user
- **Request Body**:
```json
{
    "username": "string",
    "email": "string",
    "password": "string"
}
```
- **Response**: 
```json
{
    "user": { User object without password },
    "token": "JWT token"
}
```

#### POST /api/auth/login
- **Description**: Login user
- **Request Body**:
```json
{
    "email": "string",
    "password": "string"
}
```
- **Response**:
```json
{
    "user": { User object without password },
    "token": "JWT token"
}
```

#### GET /api/auth/me
- **Description**: Get current user info
- **Headers**: `Authorization: Bearer {token}`
- **Response**: User object without password

### User Endpoints

#### GET /api/users/dashboard
- **Description**: Get user dashboard data (forms, pdfs, alerts)
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
```json
{
    "user": { User object },
    "forms": [ Array of Form objects ],
    "pdfs": [ Array of PDF objects ],
    "alerts": [ Array of Alert objects ],
    "unread_alerts": number
}
```

#### GET /api/users/profile
- **Description**: Get user profile
- **Headers**: `Authorization: Bearer {token}`
- **Response**: User object

### Admin Endpoints

#### GET /api/admin/clients
- **Description**: Get all clients (admin only)
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
```json
{
    "clients": [ Array of User objects with subscription data ],
    "stats": {
        "total": number,
        "active": number,
        "pending": number
    }
}
```

#### GET /api/admin/clients/:userId
- **Description**: Get specific client details (admin only)
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
```json
{
    "user": { User object },
    "forms": [ Array of Form objects ],
    "pdfs": [ Array of PDF objects ],
    "alerts": [ Array of Alert objects ]
}
```

#### POST /api/admin/verify-payment/:userId
- **Description**: Mark client payment as verified (admin only)
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
```json
{
    "success": true,
    "message": "Payment verified"
}
```

### Form Endpoints

#### POST /api/forms/send
- **Description**: Admin sends form to client
- **Headers**: `Authorization: Bearer {token}`
- **Request Body**:
```json
{
    "user_id": "string",
    "title": "string",
    "url": "string"
}
```
- **Response**: Form object

#### PATCH /api/forms/:formId/complete
- **Description**: Mark form as completed
- **Headers**: `Authorization: Bearer {token}`
- **Response**: Updated Form object

### PDF Endpoints

#### POST /api/pdfs/upload
- **Description**: Admin uploads PDF for client
- **Headers**: `Authorization: Bearer {token}`, `Content-Type: multipart/form-data`
- **Request Body** (FormData):
```
user_id: string
title: string
type: "training" | "nutrition"
file: File (PDF)
```
- **Response**: PDF object

#### GET /api/pdfs/:pdfId/download
- **Description**: Download PDF file
- **Headers**: `Authorization: Bearer {token}`
- **Response**: PDF file stream

### Alert Endpoints

#### POST /api/alerts/send
- **Description**: Admin sends alert to client
- **Headers**: `Authorization: Bearer {token}`
- **Request Body**:
```json
{
    "user_id": "string",
    "title": "string",
    "message": "string",
    "type": "form" | "general" | "reminder",
    "link": "string (optional)"
}
```
- **Response**: Alert object

#### PATCH /api/alerts/:alertId/read
- **Description**: Mark alert as read
- **Headers**: `Authorization: Bearer {token}`
- **Response**: Updated Alert object

#### GET /api/alerts/unread
- **Description**: Get count of unread alerts
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
```json
{
    "count": number
}
```

### Message/Chat Endpoints

#### GET /api/messages/:userId
- **Description**: Get all messages for a user (admin gets client messages, user gets own messages)
- **Headers**: `Authorization: Bearer {token}`
- **Response**:
```json
{
    "messages": [ Array of Message objects ]
}
```

#### POST /api/messages/send
- **Description**: Send a message
- **Headers**: `Authorization: Bearer {token}`
- **Request Body**:
```json
{
    "user_id": "string",  # Client ID (required for admin, ignored for users)
    "message": "string"
}
```
- **Response**: Message object

## Mock Data Currently Used in Frontend

### Mock Users
- **User 1 (Active)**: maria@example.com / user123
  - Has forms, PDFs, alerts
  - Payment verified
  
- **User 2 (Pending)**: carlos@example.com 
  - No documents yet
  - Payment pending

### Admin User
- jorge@jorgecalcerrada.com / admin123

## Integration Points

### 1. Landing Page
- **Current**: Static with direct links
- **Backend Integration**: None required for landing page
- **"QUIERO ESTE PLAN" button**: Redirects to `/register`
- **"Trabaja conmigo" button**: Opens Google Calendar (no backend)
- **Forms de diagnóstico**: External Google Forms (no backend)

### 2. Registration Flow
- **Mock**: Creates user with pending payment status
- **Backend**: 
  - POST /api/auth/register
  - Store user in MongoDB
  - Return JWT token
  - Redirect to /dashboard

### 3. User Dashboard
- **Mock**: Uses mockUsers array
- **Backend**: 
  - GET /api/users/dashboard on component mount
  - Display real data from MongoDB
  - "Pagar ahora" button: Opens Stripe link (external, no backend)

### 4. Admin Dashboard
- **Mock**: Uses mockUsers array
- **Backend**:
  - GET /api/admin/clients on component mount
  - All form sends: POST /api/forms/send
  - PDF uploads: POST /api/pdfs/upload (with file handling)
  - Alert sends: POST /api/alerts/send
  - Payment verification: POST /api/admin/verify-payment/:userId

### 5. Chat System
- **Mock**: In-memory messages array
- **Backend**:
  - GET /api/messages/:userId on chat open
  - POST /api/messages/send when sending message
  - Consider WebSocket/Socket.io for real-time updates (optional for MVP)

## File Upload Strategy

### PDF Storage
- **Option 1 (Simple)**: Store in `/backend/uploads` directory
- **Option 2 (Recommended)**: Use cloud storage (AWS S3, Google Cloud Storage)
- **File naming**: `{user_id}_{timestamp}_{original_name}.pdf`

### Implementation
```python
from fastapi import UploadFile
import os
from datetime import datetime

async def save_pdf(file: UploadFile, user_id: str, pdf_type: str):
    # Create uploads directory if not exists
    upload_dir = "/app/backend/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{user_id}_{timestamp}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    return file_path
```

## Security Considerations

### 1. Authentication
- Use JWT tokens with expiration (7 days recommended)
- Hash passwords with bcrypt
- Implement password strength requirements

### 2. Authorization
- Middleware to check user role for admin endpoints
- Users can only access their own data
- Admins can access all client data

### 3. File Upload
- Validate file type (only PDF)
- Limit file size (max 10MB recommended)
- Scan for malware (optional but recommended)

### 4. Rate Limiting
- Implement rate limiting on auth endpoints
- Limit file uploads per user

## Testing Strategy

### Backend Testing
1. Test all authentication endpoints
2. Test user dashboard data retrieval
3. Test admin client management
4. Test file upload functionality
5. Test chat message send/receive
6. Test payment verification workflow

### Integration Testing
1. Register new user → Login → Dashboard
2. Admin login → Select client → Send form → Verify in user dashboard
3. Admin upload PDF → Verify in user documents
4. Send message in chat → Verify in recipient's chat

## Implementation Priority

### Phase 1 (Critical - MVP)
1. ✅ Authentication (register, login)
2. ✅ User dashboard data endpoints
3. ✅ Admin client list and selection
4. ✅ Form sending functionality
5. ✅ Payment verification

### Phase 2 (Important)
6. ✅ PDF upload and download
7. ✅ Alert system
8. ✅ Basic chat (without real-time)

### Phase 3 (Enhancement)
9. Real-time chat with WebSocket
10. Email notifications
11. Advanced analytics for admin
12. Calendar integration for reviews

## Notes
- All dates should be stored in UTC in MongoDB
- Frontend will handle timezone conversion
- Use proper error handling and return appropriate HTTP status codes
- Implement logging for all admin actions
- Consider implementing audit trail for sensitive operations
