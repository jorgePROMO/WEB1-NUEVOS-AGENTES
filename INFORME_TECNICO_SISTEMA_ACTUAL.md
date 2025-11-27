# 📊 INFORME TÉCNICO EXHAUSTIVO - SISTEMA ACTUAL EDN360

**Fecha**: Noviembre 2025  
**Propósito**: Documentar el sistema actual completo antes de migrar al nuevo sistema EDN360 (E1-E7.5)  
**Autor**: Análisis del sistema existente

---

## 📑 ÍNDICE

1. [Flujo Completo de Usuario](#1-flujo-completo-de-usuario)
2. [Flujo Completo del Panel Admin](#2-flujo-completo-del-panel-admin)
3. [Relación Frontend ↔ Backend](#3-relación-frontend--backend)
4. [Flujo Actual de Generación de Planes (LEGACY)](#4-flujo-actual-de-generación-de-planes-legacy)
5. [Limitaciones, Dependencias y Wiring](#5-limitaciones-dependencias-y-wiring)
6. [Diagrama Completo del Sistema Actual](#6-diagrama-completo-del-sistema-actual)
7. [Colecciones MongoDB Utilizadas](#7-colecciones-mongodb-utilizadas)
8. [Endpoints Completos del Backend](#8-endpoints-completos-del-backend)

---

## 1️⃣ FLUJO COMPLETO DE USUARIO

### 1.1 Entrada en la Web

**URL**: `/` (LandingPage.jsx)

**Componentes renderizados**:
- `HeroSection`: Presentación principal
- `ServicesSection`: Servicios ofrecidos
- `AboutSection`: Información sobre el servicio
- `DualCTA`: Llamadas a la acción (registrarse/iniciar sesión)
- `Footer`: Footer de la página

**Acciones disponibles**:
- Click en "Registrarse" → Navega a `/register`
- Click en "Iniciar sesión" → Navega a `/login`
- Click en "Trabaja conmigo" → Navega a `/trabaja-conmigo`

---

### 1.2 Registro de Usuario

**URL**: `/register`  
**Componente**: `Register.jsx`

**Flujo**:

1. **Usuario rellena formulario**:
   - Nombre completo
   - Email
   - Contraseña
   - Confirmación de contraseña

2. **Frontend valida**:
   - Contraseñas coinciden
   - Email válido
   - Campos no vacíos

3. **Request al backend**:
   ```
   POST /api/auth/register
   Body: {
     full_name: string,
     email: string,
     password: string
   }
   ```

4. **Backend crea usuario**:
   - Hashea la contraseña (bcrypt)
   - Crea documento en `users` collection
   - Genera token de verificación
   - Envía email de verificación
   - Devuelve:
   ```json
   {
     "message": "Usuario registrado exitosamente",
     "user_id": "...",
     "email_sent": true
   }
   ```

5. **Frontend muestra**:
   - Mensaje de éxito
   - Instrucciones para verificar email
   - Redirige a `/verify-email`

**Colección MongoDB**:
```javascript
db.users.insertOne({
  _id: "<generated_id>",
  full_name: "...",
  email: "...",
  password: "<hashed>",
  role: "user",
  email_verified: false,
  verification_token: "...",
  created_at: ISODate("..."),
  subscription: {
    plan: null,
    status: "inactive",
    payment_status: "pending"
  }
})
```

---

### 1.3 Verificación de Email

**URL**: `/verify-email?token=...`  
**Componente**: `VerifyEmail.jsx`

**Flujo**:

1. **Frontend extrae token de URL**
2. **Request al backend**:
   ```
   GET /api/auth/verify-email?token=<token>
   ```

3. **Backend verifica token**:
   - Busca usuario con ese token
   - Marca `email_verified: true`
   - Elimina el token

4. **Frontend muestra**:
   - Mensaje de éxito
   - Botón "Ir a iniciar sesión" → `/login`

---

### 1.4 Inicio de Sesión

**URL**: `/login`  
**Componente**: `Login.jsx`

**Flujo**:

1. **Usuario rellena**:
   - Email
   - Contraseña

2. **Request al backend**:
   ```
   POST /api/auth/login
   Body: {
     email: string,
     password: string
   }
   ```

3. **Backend valida**:
   - Busca usuario por email
   - Verifica contraseña (bcrypt)
   - Verifica email_verified
   - Genera JWT token

4. **Respuesta**:
   ```json
   {
     "token": "eyJ...",
     "user": {
       "id": "...",
       "full_name": "...",
       "email": "...",
       "role": "user",
       "subscription": {...}
     }
   }
   ```

5. **Frontend**:
   - Guarda token en localStorage
   - Guarda user en AuthContext
   - Redirige según rol:
     - Admin → `/admin`
     - User → `/dashboard`

---

### 1.5 Pago (Subscription)

**URL**: `/dashboard` (UserDashboard.jsx)  
**Estado**: Usuario sin suscripción activa

**Flujo de Pago**:

1. **Frontend detecta**: `subscription.status !== 'active'`

2. **Muestra sección de pago** con planes:
   - Individual (€200/mes)
   - Team (€400/mes)

3. **Usuario selecciona plan** → Click en "Suscribirse"

4. **Request al backend**:
   ```
   POST /api/stripe/create-subscription-session
   Body: {
     plan: "individual" | "team"
   }
   Headers: {
     Authorization: "Bearer <token>"
   }
   ```

5. **Backend crea sesión Stripe**:
   - Crea Stripe Checkout Session
   - Devuelve:
   ```json
   {
     "sessionId": "cs_...",
     "url": "https://checkout.stripe.com/..."
   }
   ```

6. **Frontend redirige a Stripe Checkout**:
   ```javascript
   window.location.href = url
   ```

7. **Usuario completa pago en Stripe**

8. **Stripe redirige a**:
   ```
   /subscription-success?session_id=...
   ```

9. **Frontend (SubscriptionSuccess.jsx)**:
   - Muestra mensaje de éxito
   - Instrucciones de espera
   - "El admin verificará tu pago y activará tu cuenta"

10. **Admin verifica pago** (ver sección admin):
    - Va a `/admin` → Lista de clientes
    - Ve cliente con `payment_status: "pending"`
    - Click en "Verificar pago"
    - Endpoint: `POST /api/admin/verify-payment/{user_id}`

11. **Backend actualiza**:
    ```javascript
    db.users.updateOne(
      { _id: user_id },
      { $set: {
        "subscription.payment_status": "verified",
        "subscription.status": "active"
      }}
    )
    ```

12. **Usuario vuelve a `/dashboard`** → Ya puede acceder

---

### 1.6 Acceso al Panel de Usuario

**URL**: `/dashboard`  
**Componente**: `UserDashboard.jsx`  
**Auth**: Protected (requiere token válido)

**Request inicial**:
```
GET /api/users/dashboard
Headers: {
  Authorization: "Bearer <token>"
}
```

**Backend devuelve**:
```json
{
  "user": {
    "id": "...",
    "full_name": "...",
    "email": "...",
    "subscription": {
      "plan": "individual",
      "status": "active",
      "payment_status": "verified"
    }
  },
  "training_plans": [...],
  "nutrition_plans": [...],
  "pending_followups": [...]
}
```

**Secciones del Dashboard**:

1. **Header**: Nombre, email, botón logout
2. **Cuestionario Nutricional**: Si no ha rellenado → Botón "Rellenar cuestionario"
3. **Planes de Entrenamiento**: Lista de planes generados
4. **Planes de Nutrición**: Lista de planes generados
5. **Follow-ups Pendientes**: Cuestionarios de seguimiento

---

### 1.7 Rellenar Cuestionario Nutricional

**Componente**: `NutritionQuestionnaire.jsx` (modal)

**Trigger**: Click en "Rellenar cuestionario nutricional"

**Flujo**:

1. **Modal se abre** con formulario de ~100 preguntas

2. **Secciones del cuestionario**:
   - Datos personales (nombre, email, fecha nacimiento, sexo, profesión)
   - Medidas (peso, altura, % grasa, cintura, cadera, bíceps, muslo)
   - Salud (medicamentos, enfermedades crónicas, alergias, operaciones)
   - Actividad física (experiencia, nivel, días/semana, tiempo/sesión)
   - Hábitos alimenticios (horarios, comidas, preferencias, intolerancias)
   - Objetivos (físicos, motivación, impedimentos)

3. **Usuario rellena todo** → Click en "Enviar"

4. **Frontend valida**:
   - Campos obligatorios completos
   - Formatos correctos (fechas, números)

5. **Request al backend**:
   ```
   POST /api/nutrition/questionnaire/submit
   Body: {
     responses: {
       nombre_completo: "...",
       email: "...",
       // ... ~100 campos más
     }
   }
   Headers: {
     Authorization: "Bearer <token>"
   }
   ```

6. **Backend procesa**:
   
   a) **Guarda en BD Web** (`test_database`):
   ```javascript
   db.nutrition_questionnaire_submissions.insertOne({
     _id: "<generated_id>",
     user_id: "<user_id>",
     responses: { ... },
     submitted_at: ISODate("..."),
     plan_generated: false,
     plan_id: null
   })
   ```

   b) **Dual-write a BD Técnica** (`edn360_app`) - SI `USE_CLIENT_DRAWER_WRITE=true`:
   ```javascript
   // Llama a add_questionnaire_to_drawer()
   db.client_drawers.updateOne(
     { user_id: "<user_id>" },
     {
       $push: {
         "services.shared_questionnaires": {
           submission_id: "<submission_id>",
           submitted_at: ISODate("..."),
           source: "initial",
           raw_payload: { ... }
         }
       }
     },
     { upsert: true }
   )
   ```

7. **Respuesta al frontend**:
   ```json
   {
     "message": "Cuestionario guardado exitosamente",
     "submission_id": "..."
   }
   ```

8. **Frontend**:
   - Cierra modal
   - Muestra mensaje de éxito
   - Muestra: "Cuestionario enviado. Espera a que el coach genere tu plan."
   - **NO genera plan automáticamente** (lo hace el admin)

---

### 1.8 ¿Qué hace la web después de enviar el cuestionario?

**IMPORTANTE**: La web **NO** genera planes automáticamente.

**Flujo actual**:

1. Usuario envía cuestionario → Guardado en BD
2. Usuario ve en dashboard: "Cuestionario enviado ✅"
3. Usuario espera
4. Admin ve en panel: Usuario con cuestionario pendiente
5. Admin genera plan manualmente (ver sección admin)
6. Usuario recibe plan por email
7. Usuario ve plan en su dashboard

**Pantallas que ve el usuario después**:

- **Dashboard**: Sección de "Cuestionarios" muestra:
  - "✅ Cuestionario inicial enviado el [fecha]"
  - "⏳ Esperando generación del plan"

- **No hay generación automática** en frontend
- **No hay botón "Generar plan"** para el usuario
- **Todo lo hace el admin desde `/admin`**

---

### 1.9 Ver Planes Generados

**Ubicación**: `/dashboard` → Secciones "Planes de Entrenamiento" / "Planes de Nutrición"

**Request**:
```
GET /api/users/dashboard
```

**Response incluye**:
```json
{
  "training_plans": [
    {
      "_id": "...",
      "title": "Plan de Hipertrofia 4 días",
      "created_at": "...",
      "weeks": 4,
      "days_per_week": 4
    }
  ],
  "nutrition_plans": [
    {
      "_id": "...",
      "title": "Plan Nutricional Personalizado",
      "created_at": "...",
      "calories": 2500
    }
  ]
}
```

**Renderizado**:
- Lista de cards con título, fecha, resumen
- Click en card → Muestra detalles del plan
- Botón "Descargar PDF" (si disponible)

---

## 2️⃣ FLUJO COMPLETO DEL PANEL ADMIN

**URL**: `/admin`  
**Componente**: `AdminDashboard.jsx`  
**Auth**: Protected + Admin only

---

### 2.1 Vista Principal Admin

**Request inicial**:
```
GET /api/admin/clients
```

**Response**:
```json
{
  "clients": [
    {
      "_id": "...",
      "full_name": "...",
      "email": "...",
      "subscription": {
        "plan": "individual",
        "status": "active",
        "payment_status": "verified" | "pending"
      },
      "questionnaires_count": 1,
      "training_plans_count": 2,
      "nutrition_plans_count": 1,
      "pending_followups_count": 0,
      "created_at": "..."
    }
  ]
}
```

**Filtros disponibles**:
- Por plan (individual, team)
- Por estado de pago (pending, verified)
- Por estado de suscripción (active, inactive)
- Búsqueda por nombre/email

---

### 2.2 Botones y Acciones del Panel Admin

#### **SECCIÓN: LISTA DE CLIENTES**

**Tabla con columnas**:
- Nombre
- Email
- Plan
- Estado Pago
- Cuestionarios
- Planes Training
- Planes Nutrición
- Follow-ups Pendientes
- Acciones

**Botones por cliente**:

1. **"Ver Detalles"**
   - **Endpoint**: `GET /api/admin/clients/{user_id}`
   - **Payload**: None
   - **Response**: Objeto completo del usuario
   - **Renderizado**: Modal con toda la info del cliente

2. **"Verificar Pago"** (si `payment_status: "pending"`)
   - **Endpoint**: `POST /api/admin/verify-payment/{user_id}`
   - **Payload**: None
   - **Response**: `{ success: true, message: "..." }`
   - **Efecto**: Actualiza `payment_status: "verified"` y `status: "active"`
   - **Renderizado**: Desaparece el botón, aparece badge "✅ Verificado"

3. **"Archivar Cliente"**
   - **Endpoint**: `POST /api/admin/archive-client/{user_id}`
   - **Payload**: `{ reason: string (optional) }`
   - **Response**: `{ success: true }`
   - **Efecto**: Marca `subscription.archived: true`
   - **Renderizado**: Cliente pasa a lista de "Archivados"

4. **"Desarchivar Cliente"**
   - **Endpoint**: `POST /api/admin/unarchive-client/{user_id}`
   - **Payload**: None
   - **Response**: `{ success: true }`
   - **Efecto**: Marca `subscription.archived: false`

5. **"Eliminar Cliente"**
   - **Endpoint**: `DELETE /api/admin/delete-client/{user_id}`
   - **Payload**: None
   - **Response**: `{ success: true }`
   - **Efecto**: Elimina usuario de BD (⚠️ irreversible)
   - **Confirmación**: Requiere confirmar con nombre del cliente

6. **"Enviar Reset Password"**
   - **Endpoint**: `POST /api/admin/users/{user_id}/send-password-reset`
   - **Payload**: None
   - **Response**: `{ success: true, email_sent: true }`
   - **Efecto**: Envía email con link de reset

---

#### **SECCIÓN: DETALLE DE CLIENTE**

**Click en "Ver Detalles"** → Modal con:

**Tabs**:
1. Información General
2. Cuestionarios
3. Planes de Entrenamiento
4. Planes de Nutrición
5. Follow-ups
6. Historial

---

##### **TAB 1: INFORMACIÓN GENERAL**

**Botones**:

1. **"Ver EDN360 Input"** (FASE 2)
   - **Endpoint**: `GET /api/admin/users/{user_id}/edn360-input-preview`
   - **Payload**: None
   - **Response**:
   ```json
   {
     "user_profile": {...},
     "questionnaires": [...],
     "generated_at": "...",
     "version": "1.0.0"
   }
   ```
   - **Renderizado**: Modal con JSON formateado

2. **"Lanzar EDN360 Workflow (TEST)"** (FASE 3)
   - **Endpoint**: `POST /api/admin/users/{user_id}/edn360-run-workflow`
   - **Payload**: None
   - **Response**:
   ```json
   {
     "success": true,
     "result": {
       "snapshot_id": "...",
       "user_id": "...",
       "status": "success" | "failed",
       "workflow_name": "...",
       "has_response": true
     }
   }
   ```
   - **Renderizado**: Alert con snapshot_id y status

---

##### **TAB 2: CUESTIONARIOS**

**Muestra lista de cuestionarios** del usuario:

**Request**:
```
GET /api/admin/clients/{user_id}
```

**Parte de la response**:
```json
{
  "questionnaires": [
    {
      "_id": "...",
      "type": "nutrition_initial",
      "submitted_at": "...",
      "plan_generated": false
    }
  ]
}
```

**Botones por cuestionario**:

1. **"Ver Respuestas"**
   - **Acción**: Expande accordion con todas las respuestas
   - **No endpoint**: Ya está en el response inicial

2. **"Generar Plan de Nutrición"** (LEGACY - ver sección 4)
   - **Endpoint**: `POST /api/admin/users/{user_id}/nutrition/generate`
   - **Payload**:
   ```json
   {
     "submission_id": "...",
     "nutrition_plan_id": null
   }
   ```
   - **Response**: `{ job_id: "..." }` (sistema async legacy)
   - **Renderizado**: Modal de progreso con polling

---

##### **TAB 3: PLANES DE ENTRENAMIENTO**

**Request**:
```
GET /api/admin/users/{user_id}/training
```

**Response**:
```json
{
  "training_plans": [
    {
      "_id": "...",
      "title": "...",
      "created_at": "...",
      "weeks": 4,
      "sessions": [...]
    }
  ]
}
```

**Botones por plan**:

1. **"Ver Plan"**
   - **Acción**: Expande accordion con todo el plan
   - **No endpoint**: Ya está en el response

2. **"Generar PDF"**
   - **Endpoint**: `POST /api/admin/users/{user_id}/training-pdf`
   - **Payload**: `{ plan_id: "..." }`
   - **Response**: Blob (archivo PDF)
   - **Renderizado**: Descarga automática

3. **"Enviar por Email"**
   - **Endpoint**: `POST /api/admin/users/{user_id}/training/send-email`
   - **Payload**: `{ plan_id: "..." }`
   - **Response**: `{ success: true, email_sent: true }`
   - **Renderizado**: Toast de éxito

4. **"Compartir por WhatsApp"**
   - **Endpoint**: `GET /api/admin/users/{user_id}/training/whatsapp-link`
   - **Query**: `?plan_id=...`
   - **Response**: `{ whatsapp_link: "https://wa.me/..." }`
   - **Renderizado**: Abre link en nueva pestaña

5. **"Eliminar Plan"**
   - **Endpoint**: `DELETE /api/admin/users/{user_id}/training/{plan_id}`
   - **Payload**: None
   - **Response**: `{ success: true }`
   - **Confirmación**: Requiere confirmar
   - **Renderizado**: Elimina de la lista

6. **"Regenerar Plan"** (LEGACY - ver sección 4)
   - **Endpoint**: `POST /api/admin/users/{user_id}/training/generate`
   - **Payload**:
   ```json
   {
     "submission_id": "...",
     "training_plan_id": "<id_del_plan_anterior>"
   }
   ```
   - **Response**: `{ job_id: "..." }`
   - **Renderizado**: Modal de progreso

---

##### **TAB 4: PLANES DE NUTRICIÓN**

**Request**:
```
GET /api/admin/users/{user_id}/nutrition
```

**Response**:
```json
{
  "nutrition_plans": [
    {
      "_id": "...",
      "title": "...",
      "created_at": "...",
      "calories": 2500,
      "meals": [...]
    }
  ]
}
```

**Botones por plan**: (idénticos a training)

1. **"Ver Plan"**
2. **"Generar PDF"**
   - Endpoint: `POST /api/admin/users/{user_id}/nutrition-pdf`
3. **"Enviar por Email"**
   - Endpoint: `POST /api/admin/users/{user_id}/nutrition/send-email`
4. **"Compartir por WhatsApp"**
   - Endpoint: `GET /api/admin/users/{user_id}/nutrition/whatsapp-link`
5. **"Eliminar Plan"**
   - Endpoint: `DELETE /api/admin/users/{user_id}/nutrition/{plan_id}`
6. **"Regenerar Plan"**
   - Endpoint: `POST /api/admin/users/{user_id}/nutrition/generate`

---

##### **TAB 5: FOLLOW-UPS**

**Request**:
```
GET /api/admin/users/{user_id}/follow-ups
```

**Response**:
```json
{
  "follow_ups": [
    {
      "_id": "...",
      "submitted_at": "...",
      "responses": {...},
      "plan_generated": false,
      "analysis": null
    }
  ]
}
```

**Botones por follow-up**:

1. **"Analizar con IA"** (LEGACY)
   - **Endpoint**: `POST /api/admin/users/{user_id}/followups/{followup_id}/analyze-with-ia`
   - **Payload**: None
   - **Response**:
   ```json
   {
     "analysis": {
       "progress": "...",
       "recommendations": "..."
     }
   }
   ```
   - **Renderizado**: Modal con análisis

2. **"Generar Plan Ajustado"** (LEGACY)
   - **Endpoint**: `POST /api/admin/users/{user_id}/followups/{followup_id}/generate-plan`
   - **Payload**: None
   - **Response**: `{ job_id: "..." }`
   - **Renderizado**: Modal de progreso

3. **"Enviar por Email"**
   - **Endpoint**: `POST /api/admin/users/{user_id}/followups/{followup_id}/send-email`

4. **"Enviar por WhatsApp"**
   - **Endpoint**: `POST /api/admin/users/{user_id}/followups/{followup_id}/send-whatsapp`

5. **"Generar PDF"**
   - **Endpoint**: `POST /api/admin/users/{user_id}/followups/{followup_id}/generate-pdf`

---

##### **TAB 6: HISTORIAL**

**Muestra timeline de acciones**:
- Cuestionarios enviados
- Planes generados
- Follow-ups completados
- Pagos verificados
- Emails enviados

**No hay botones específicos**, solo visualización.

---

#### **OTRAS SECCIONES DEL PANEL ADMIN**

##### **PROSPECTS CRM**

**URL**: `/admin` → Tab "Prospects"

**Request**:
```
GET /api/admin/prospects
```

**Botones**:
- "Generar Reporte" → `POST /api/admin/prospects/{id}/generate-report`
- "Enviar Reporte Email" → `POST /api/admin/prospects/{id}/send-report-email`
- "Convertir a Cliente" → `POST /api/admin/prospects/{id}/convert`
- "Eliminar" → `DELETE /api/admin/prospects/{id}`

##### **CLIENTES EXTERNOS**

**URL**: `/admin` → Tab "Externos"

**Request**:
```
GET /api/admin/external-clients
```

**Botones**:
- "Registrar Pago" → `POST /api/admin/external-clients/{id}/payments`
- "Agregar Nota" → `POST /api/admin/external-clients/{id}/notes`
- "Mover a Team" → `POST /api/admin/external-clients/{id}/move`

##### **PLANTILLAS EMAIL**

**URL**: `/admin` → Tab "Plantillas"

**Request**:
```
GET /api/admin/templates
```

**Botones**:
- "Crear Plantilla" → `POST /api/admin/templates`
- "Eliminar" → `DELETE /api/admin/templates/{id}`
- "Enviar Email" → `POST /api/admin/send-email-template`

##### **CLIENTES EN RIESGO**

**URL**: `/admin` → Tab "En Riesgo"

**Request**:
```
GET /api/admin/clients-at-risk
```

**Muestra clientes** con:
- Sin follow-ups en >30 días
- Sin planes generados
- Pagos pendientes

---

## 3️⃣ RELACIÓN FRONTEND ↔ BACKEND

### 3.1 Endpoints Completos por Módulo

#### **AUTENTICACIÓN**

| Endpoint | Método | Descripción | Colecciones |
|----------|--------|-------------|-------------|
| `/api/auth/register` | POST | Registrar usuario | `users` |
| `/api/auth/login` | POST | Iniciar sesión | `users` |
| `/api/auth/verify-email` | GET | Verificar email | `users` |
| `/api/auth/resend-verification` | POST | Reenviar verificación | `users` |
| `/api/auth/me` | GET | Obtener usuario actual | `users` |
| `/api/auth/logout` | POST | Cerrar sesión | - |
| `/api/auth/reset-password` | POST | Reset password | `users` |

#### **DASHBOARD USUARIO**

| Endpoint | Método | Descripción | Colecciones |
|----------|--------|-------------|-------------|
| `/api/users/dashboard` | GET | Dashboard completo | `users`, `training_plans`, `nutrition_plans`, `followup_submissions` |

#### **CUESTIONARIOS**

| Endpoint | Método | Descripción | Colecciones |
|----------|--------|-------------|-------------|
| `/api/nutrition/questionnaire/submit` | POST | Enviar cuestionario nutrición | `nutrition_questionnaire_submissions`, `client_drawers` |
| `/api/questionnaire/submit` | POST | Enviar cuestionario genérico | `questionnaire_submissions` |
| `/api/follow-up/submit` | POST | Enviar follow-up | `followup_submissions`, `client_drawers` |

#### **ADMIN - CLIENTES**

| Endpoint | Método | Descripción | Colecciones |
|----------|--------|-------------|-------------|
| `/api/admin/clients` | GET | Listar clientes | `users` |
| `/api/admin/clients/{user_id}` | GET | Detalle cliente | `users`, `nutrition_questionnaire_submissions`, `training_plans`, `nutrition_plans` |
| `/api/admin/verify-payment/{user_id}` | POST | Verificar pago | `users` |
| `/api/admin/archive-client/{user_id}` | POST | Archivar cliente | `users` |
| `/api/admin/unarchive-client/{user_id}` | POST | Desarchivar cliente | `users` |
| `/api/admin/delete-client/{user_id}` | DELETE | Eliminar cliente | `users`, todas las relacionadas |

#### **ADMIN - PLANES TRAINING (LEGACY)**

| Endpoint | Método | Descripción | Colecciones |
|----------|--------|-------------|-------------|
| `/api/admin/users/{user_id}/training/generate` | POST | Generar plan training | `training_plans`, `generation_jobs` |
| `/api/admin/users/{user_id}/training` | GET | Listar planes training | `training_plans` |
| `/api/admin/users/{user_id}/training/{plan_id}` | DELETE | Eliminar plan | `training_plans` |
| `/api/admin/users/{user_id}/training-pdf` | POST | Generar PDF | `training_plans` |
| `/api/admin/users/{user_id}/training/send-email` | POST | Enviar email | `training_plans` |
| `/api/admin/users/{user_id}/training/whatsapp-link` | GET | Link WhatsApp | `training_plans` |

#### **ADMIN - PLANES NUTRICIÓN (LEGACY)**

| Endpoint | Método | Descripción | Colecciones |
|----------|--------|-------------|-------------|
| `/api/admin/users/{user_id}/nutrition/generate` | POST | Generar plan nutrición | `nutrition_plans`, `generation_jobs` |
| `/api/admin/users/{user_id}/nutrition` | GET | Listar planes nutrición | `nutrition_plans` |
| `/api/admin/users/{user_id}/nutrition/{plan_id}` | DELETE | Eliminar plan | `nutrition_plans` |
| `/api/admin/users/{user_id}/nutrition-pdf` | POST | Generar PDF | `nutrition_plans` |
| `/api/admin/users/{user_id}/nutrition/send-email` | POST | Enviar email | `nutrition_plans` |
| `/api/admin/users/{user_id}/nutrition/whatsapp-link` | GET | Link WhatsApp | `nutrition_plans` |

#### **ADMIN - FOLLOW-UPS (LEGACY)**

| Endpoint | Método | Descripción | Colecciones |
|----------|--------|-------------|-------------|
| `/api/admin/users/{user_id}/follow-ups` | GET | Listar follow-ups | `followup_submissions` |
| `/api/admin/users/{user_id}/followups/{id}/analyze-with-ia` | POST | Analizar con IA | `followup_submissions` |
| `/api/admin/users/{user_id}/followups/{id}/generate-plan` | POST | Generar plan ajustado | `followup_submissions`, `generation_jobs` |
| `/api/admin/users/{user_id}/followups/{id}/send-email` | POST | Enviar email | `followup_submissions` |
| `/api/admin/users/{user_id}/followups/{id}/send-whatsapp` | POST | Enviar WhatsApp | `followup_submissions` |
| `/api/admin/users/{user_id}/followups/{id}/generate-pdf` | POST | Generar PDF | `followup_submissions` |

#### **ADMIN - EDN360 (NUEVO)**

| Endpoint | Método | Descripción | Colecciones |
|----------|--------|-------------|-------------|
| `/api/admin/users/{user_id}/edn360-input-preview` | GET | Ver EDN360Input | `users`, `client_drawers` |
| `/api/admin/users/{user_id}/edn360-run-workflow` | POST | Lanzar workflow EDN360 | `client_drawers`, `edn360_snapshots` |
| `/api/training-plan` | POST | Generar plan training (E1-E7.5) | `client_drawers`, `edn360_snapshots` |

#### **PAGO**

| Endpoint | Método | Descripción | Colecciones |
|----------|--------|-------------|-------------|
| `/api/stripe/create-subscription-session` | POST | Crear sesión Stripe | `users` |

---

### 3.2 Colecciones MongoDB por Pantalla

#### **FRONTEND: Landing Page**
- **Colecciones**: Ninguna (estática)

#### **FRONTEND: Register**
- **Colecciones**: `users` (write)

#### **FRONTEND: Login**
- **Colecciones**: `users` (read)

#### **FRONTEND: UserDashboard**
- **Colecciones**:
  - `users` (read)
  - `training_plans` (read)
  - `nutrition_plans` (read)
  - `followup_submissions` (read)

#### **FRONTEND: NutritionQuestionnaire (modal)**
- **Colecciones**:
  - `nutrition_questionnaire_submissions` (write)
  - `client_drawers` (write - dual-write)

#### **FRONTEND: AdminDashboard**
- **Colecciones**:
  - `users` (read/write)
  - `training_plans` (read/write)
  - `nutrition_plans` (read/write)
  - `nutrition_questionnaire_submissions` (read)
  - `followup_submissions` (read/write)
  - `generation_jobs` (read - para polling)
  - `client_drawers` (read - FASE 2)
  - `edn360_snapshots` (write - FASE 3)

---

### 3.3 Módulos Legacy Integrados

**Módulos que están activos hoy**:

1. **Orquestador E1-E9 (Training)** - EN server.py
   - Usado por: `POST /api/admin/users/{user_id}/training/generate`
   - Agentes: E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8 → E9
   - Output: JSON con plan de entrenamiento estructurado

2. **Orquestador N0-N8 (Nutrition)** - EN server.py
   - Usado por: `POST /api/admin/users/{user_id}/nutrition/generate`
   - Agentes: N0 → N1 → N2 → N3 → N4 → N5 → N6 → N7 → N8
   - Output: JSON con plan nutricional estructurado

3. **Sistema de Jobs Asíncronos** - EN server.py
   - Colección: `generation_jobs`
   - Polling: Frontend hace GET `/api/jobs/{job_id}` cada 3 segundos
   - Estados: pending → running → completed / failed

4. **Generación de PDFs** - EN server.py
   - Usando librerías: reportlab, jinja2
   - Genera PDFs de planes para descargar/enviar

5. **Envío de Emails** - EN server.py
   - Usando: SMTP o SendGrid
   - Templates: HTML con planes embebidos

---

## 4️⃣ FLUJO ACTUAL DE GENERACIÓN DE PLANES (LEGACY)

### 4.1 Endpoint de Generación Training (LEGACY)

**URL**: `POST /api/admin/users/{user_id}/training/generate`

**Trigger**: Admin hace click en "Generar Plan de Entrenamiento"

**Payload enviado**:
```json
{
  "submission_id": "1764016775848319",
  "training_plan_id": null
}
```

**Flujo Backend**:

1. **Valida usuario y cuestionario**:
   ```python
   user = await db.users.find_one({"_id": user_id})
   submission = await db.nutrition_questionnaire_submissions.find_one({
       "_id": submission_id
   })
   ```

2. **Crea job asíncrono**:
   ```python
   job_id = str(uuid.uuid4())
   await db.generation_jobs.insert_one({
       "_id": job_id,
       "user_id": user_id,
       "type": "training",
       "submission_id": submission_id,
       "status": "pending",
       "progress": {
           "phase": "E1",
           "current_agent": "E1",
           "completed_steps": [],
           "percentage": 0
       },
       "result": None,
       "error_message": None,
       "created_at": datetime.now(timezone.utc)
   })
   ```

3. **Lanza background task**:
   ```python
   asyncio.create_task(process_generation_job(job_id))
   ```

4. **Responde inmediatamente**:
   ```json
   {
     "job_id": "uuid-123-456",
     "status": "pending",
     "message": "Generación iniciada"
   }
   ```

---

### 4.2 Proceso Background (process_generation_job)

**Flujo interno**:

1. **Actualiza status a "running"**:
   ```python
   await db.generation_jobs.update_one(
       {"_id": job_id},
       {"$set": {"status": "running"}}
   )
   ```

2. **Obtiene datos del usuario y cuestionario**

3. **Ejecuta Orquestador E1-E9** (código hardcoded en server.py):

   ```python
   # E1: Análisis inicial
   e1_result = await agent_e1(submission_data)
   await update_progress(job_id, "E1", 11)
   
   # E2: Definición de objetivos
   e2_result = await agent_e2(e1_result)
   await update_progress(job_id, "E2", 22)
   
   # E3: Diseño de estructura
   e3_result = await agent_e3(e2_result)
   await update_progress(job_id, "E3", 33)
   
   # ... E4, E5, E6, E7, E8
   
   # E9: Formateo final
   final_plan = await agent_e9(e8_result)
   await update_progress(job_id, "E9", 100)
   ```

4. **Guarda plan en BD**:
   ```python
   plan_id = str(uuid.uuid4())
   await db.training_plans.insert_one({
       "_id": plan_id,
       "user_id": user_id,
       "submission_id": submission_id,
       "title": final_plan["title"],
       "summary": final_plan["summary"],
       "weeks": final_plan["weeks"],
       "days_per_week": final_plan["days_per_week"],
       "sessions": final_plan["sessions"],
       "created_at": datetime.now(timezone.utc)
   })
   ```

5. **Actualiza job como completado**:
   ```python
   await db.generation_jobs.update_one(
       {"_id": job_id},
       {"$set": {
           "status": "completed",
           "result": {
               "training_plan_id": plan_id
           }
       }}
   )
   ```

---

### 4.3 Polling desde Frontend

**Frontend hace polling cada 3 segundos**:

```javascript
const pollJobStatus = async (jobId) => {
  const interval = setInterval(async () => {
    const response = await axios.get(`${API}/jobs/${jobId}`);
    
    if (response.data.status === 'completed') {
      clearInterval(interval);
      // Muestra plan generado
      showSuccessMessage();
      reloadPlans();
    } else if (response.data.status === 'failed') {
      clearInterval(interval);
      showErrorMessage(response.data.error_message);
    } else {
      // Actualiza barra de progreso
      updateProgressBar(response.data.progress.percentage);
      updateCurrentAgent(response.data.progress.current_agent);
    }
  }, 3000);
};
```

---

### 4.4 Estructura del Plan Generado (LEGACY)

**En `training_plans` collection**:

```javascript
{
  _id: "plan-uuid-123",
  user_id: "1764016044644335",
  submission_id: "1764016775848319",
  title: "Plan de Hipertrofia 4 días - Nivel Avanzado",
  summary: "Plan centrado en ganancia muscular con enfoque en hombros y zona lumbar",
  goal: "Ganar músculo sin agravar lesiones",
  training_type: "upper_lower",
  days_per_week: 4,
  session_duration_min: 45,
  weeks: 4,
  sessions: [
    {
      id: "D1",
      name: "Upper 1 – Empuje dominante",
      focus: ["upper_body", "push_focus"],
      blocks: [
        {
          id: "A",
          primary_muscles: ["chest", "front_delts", "triceps"],
          exercises: [
            {
              order: 1,
              db_id: "E049",
              name: "press banca smith agarre cerrado",
              series: 3,
              reps: "10-12",
              rpe: "7",
              video_url: "https://..."
            }
          ]
        }
      ],
      session_notes: ["No press por encima cabeza"]
    }
  ],
  general_notes: ["Calentar hombros y zona lumbar"],
  created_at: ISODate("2025-11-26T...")
}
```

---

### 4.5 Renderizado en Frontend

**AdminDashboard**:

1. **Lista de planes**:
   - Card por cada plan
   - Muestra: título, fecha, semanas, días/semana

2. **Click en "Ver Plan"**:
   - Expande accordion
   - Muestra todas las sesiones
   - Por cada sesión:
     - Nombre
     - Bloques de ejercicios
     - Por cada ejercicio:
       - Nombre
       - Series x Reps
       - RPE
       - Video (iframe o link)

3. **Botones**:
   - "Descargar PDF" → Llama a `/training-pdf`
   - "Enviar Email" → Llama a `/training/send-email`
   - "WhatsApp" → Abre link generado

---

## 5️⃣ LIMITACIONES, DEPENDENCIAS Y WIRING

### 5.1 Partes del Frontend Acopladas a Endpoints Viejos

**AdminDashboard.jsx**:

1. **Función `generateTrainingPlan()`**:
   - **Línea ~5000-5100**
   - **Endpoint**: `POST /api/admin/users/{user_id}/training/generate`
   - **Acoplamiento**: Espera `{ job_id }` y hace polling a `/jobs/{job_id}`
   - **Impacto**: Si cambiamos a nuevo sistema, esta función debe reescribirse

2. **Función `generateNutritionPlan()`**:
   - **Línea ~5100-5200**
   - **Endpoint**: `POST /api/admin/users/{user_id}/nutrition/generate`
   - **Acoplamiento**: Igual que training
   - **Impacto**: Reescritura completa

3. **Componente `GenerationProgressModal`**:
   - **Archivo**: `/app/frontend/src/components/GenerationProgressModal.jsx`
   - **Acoplamiento**: Polling cada 3 segundos, espera estructura específica de progress
   - **Impacto**: Si cambiamos a sistema síncrono o con otra estructura, este componente es inútil

4. **Renderizado de planes**:
   - **Estructura hardcoded**: Espera `sessions[].blocks[].exercises[]`
   - **Impacto**: Si el nuevo sistema devuelve otra estructura, hay que actualizar renderizado

---

### 5.2 Partes que Dependen de Colecciones Legacy

**Backend endpoints que leen/escriben en colecciones legacy**:

1. **`training_plans` collection**:
   - Usada por: 9 endpoints
   - Endpoints:
     - `GET /admin/users/{user_id}/training`
     - `DELETE /admin/users/{user_id}/training/{plan_id}`
     - `POST /admin/users/{user_id}/training-pdf`
     - `POST /admin/users/{user_id}/training/send-email`
     - `GET /admin/users/{user_id}/training/whatsapp-link`
     - `POST /admin/users/{user_id}/training/generate`
   - **Impacto**: Si eliminamos esta colección, hay que migrar/reescribir todos estos endpoints

2. **`nutrition_plans` collection**:
   - Usada por: 9 endpoints
   - Mismo patrón que training
   - **Impacto**: Igual que training

3. **`generation_jobs` collection**:
   - Usada por: 3 endpoints
   - Endpoints:
     - `POST /admin/users/{user_id}/training/generate`
     - `POST /admin/users/{user_id}/nutrition/generate`
     - `GET /jobs/{job_id}`
   - **Impacto**: Si eliminamos sistema async, esta colección desaparece

4. **`nutrition_questionnaire_submissions` collection**:
   - Usada por: 4 endpoints
   - Endpoints:
     - `POST /nutrition/questionnaire/submit`
     - `GET /admin/clients/{user_id}` (para mostrar cuestionarios)
     - `POST /admin/users/{user_id}/training/generate` (lee cuestionario)
     - `POST /admin/users/{user_id}/nutrition/generate` (lee cuestionario)
   - **Impacto**: Esta colección se mantiene (BD Web), pero el dual-write a `client_drawers` debe seguir funcionando

---

### 5.3 Lógica de UI que Habría que Revisar

**Al cambiar al nuevo sistema EDN360**:

1. **Eliminar `GenerationProgressModal.jsx`**:
   - Ya no habrá polling
   - Nueva lógica: Llamada directa síncrona o con streaming

2. **Actualizar `generateTrainingPlan()` en AdminDashboard**:
   - Cambiar endpoint de `POST /training/generate` (legacy async)
   - A `POST /training-plan` (nuevo síncrono)
   - Eliminar polling, mostrar resultado directo

3. **Actualizar renderizado de planes**:
   - Si estructura cambia, actualizar:
     - Accordion de sesiones
     - Lista de ejercicios
     - Formato de series/reps/RPE

4. **Botones de "Regenerar"**:
   - Actualmente: Llaman a endpoint con `training_plan_id` (para usar plan anterior como contexto)
   - Nuevo sistema: ¿Cómo manejamos la regeneración? ¿Snapshot anterior?

5. **Botones "Descargar PDF", "Enviar Email", "WhatsApp"**:
   - Actualmente: Esperan `plan_id` de `training_plans` collection
   - Nuevo sistema: ¿Usamos `snapshot_id`? ¿O creamos nueva tabla de "planes presentables"?

---

### 5.4 Módulos Hardcoded para Training/Nutrition

**En server.py**:

1. **Orquestador E1-E9** (Training):
   - **Líneas**: ~6000-6300
   - **Hardcoded**: Toda la lógica de los agentes está en el mismo archivo
   - **Acoplamiento**: Muy fuerte con `generation_jobs` y `training_plans`
   - **Impacto**: Hay que eliminar/comentar todo este código

2. **Orquestador N0-N8** (Nutrition):
   - **Líneas**: ~4000-4300
   - **Hardcoded**: Igual que training
   - **Acoplamiento**: Con `generation_jobs` y `nutrition_plans`
   - **Impacto**: Eliminar/comentar

3. **Función `process_generation_job(job_id)`**:
   - **Líneas**: ~11000-11500
   - **Hardcoded**: Background task que ejecuta los orquestadores
   - **Acoplamiento**: Con `generation_jobs`
   - **Impacto**: Eliminar completamente

4. **Endpoint `GET /jobs/{job_id}`**:
   - **Líneas**: ~11600-11650
   - **Público**: No requiere auth (para simplificar polling)
   - **Acoplamiento**: Con `generation_jobs`
   - **Impacto**: Ya no necesario en nuevo sistema

---

### 5.5 Dependencias Críticas

**Librerías Python (backend)**:
- `openai`: Para llamadas a GPT (se mantiene)
- `motor`: MongoDB async (se mantiene)
- `bcrypt`: Hashing passwords (se mantiene)
- `PyJWT`: Tokens JWT (se mantiene)
- `stripe`: Pagos (se mantiene)
- `reportlab`: PDFs (se mantiene o reemplaza)
- `jinja2`: Templates (se mantiene)

**Librerías JavaScript (frontend)**:
- `react-router-dom`: Rutas (se mantiene)
- `axios`: HTTP requests (se mantiene)
- `shadcn/ui`: Componentes UI (se mantiene)
- `lucide-react`: Iconos (se mantiene)

---

## 6️⃣ DIAGRAMA COMPLETO DEL SISTEMA ACTUAL

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Landing  │  │ Register │  │  Login   │  │  Verify  │      │
│  │  Page    │  │          │  │          │  │  Email   │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │              │             │             │
│       └─────────────┴──────────────┴─────────────┘             │
│                         │                                       │
│                         ▼                                       │
│              ┌──────────────────┐                              │
│              │  AuthContext     │                              │
│              │  (JWT Token)     │                              │
│              └────────┬─────────┘                              │
│                       │                                         │
│         ┌─────────────┴─────────────┐                          │
│         ▼                           ▼                          │
│  ┌─────────────┐            ┌─────────────┐                   │
│  │    User     │            │    Admin    │                   │
│  │  Dashboard  │            │  Dashboard  │                   │
│  └──────┬──────┘            └──────┬──────┘                   │
│         │                          │                           │
│         │ GET /users/dashboard     │ GET /admin/clients       │
│         │                          │ GET /admin/clients/{id}  │
│         │                          │ POST /training/generate  │
│         │                          │ POST /nutrition/generate │
│         │                          │ GET /jobs/{job_id}       │
│         │                          │                          │
└─────────┼──────────────────────────┼──────────────────────────┘
          │                          │
          │                          │
          ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐    │
│  │              API ROUTER (server.py)                   │    │
│  ├───────────────────────────────────────────────────────┤    │
│  │                                                       │    │
│  │  AUTH ENDPOINTS                                       │    │
│  │  ├─ POST /auth/register                              │    │
│  │  ├─ POST /auth/login                                 │    │
│  │  ├─ GET  /auth/verify-email                          │    │
│  │  └─ GET  /auth/me                                    │    │
│  │                                                       │    │
│  │  USER ENDPOINTS                                       │    │
│  │  └─ GET  /users/dashboard                            │    │
│  │                                                       │    │
│  │  QUESTIONNAIRE ENDPOINTS                              │    │
│  │  ├─ POST /nutrition/questionnaire/submit             │    │
│  │  ├─ POST /questionnaire/submit                       │    │
│  │  └─ POST /follow-up/submit                           │    │
│  │                                                       │    │
│  │  ADMIN ENDPOINTS                                      │    │
│  │  ├─ GET  /admin/clients                              │    │
│  │  ├─ GET  /admin/clients/{user_id}                    │    │
│  │  ├─ POST /admin/verify-payment/{user_id}             │    │
│  │  │                                                    │    │
│  │  ADMIN - TRAINING (LEGACY)                           │    │
│  │  ├─ POST /admin/users/{id}/training/generate   ◄─┐  │    │
│  │  ├─ GET  /admin/users/{id}/training            │  │  │    │
│  │  ├─ DELETE /admin/users/{id}/training/{plan_id}│  │  │    │
│  │  ├─ POST /admin/users/{id}/training-pdf        │  │  │    │
│  │  └─ POST /admin/users/{id}/training/send-email │  │  │    │
│  │                                                 │  │  │    │
│  │  ADMIN - NUTRITION (LEGACY)                    │  │  │    │
│  │  ├─ POST /admin/users/{id}/nutrition/generate ◄┘  │  │    │
│  │  ├─ GET  /admin/users/{id}/nutrition             │  │    │
│  │  └─ ... (similar a training)                     │  │    │
│  │                                                   │  │    │
│  │  JOBS (LEGACY)                                    │  │    │
│  │  └─ GET  /jobs/{job_id}  ◄───────────────────────┘  │    │
│  │                                                      │    │
│  │  EDN360 (NUEVO)                                      │    │
│  │  ├─ GET  /admin/users/{id}/edn360-input-preview     │    │
│  │  ├─ POST /admin/users/{id}/edn360-run-workflow      │    │
│  │  └─ POST /training-plan                              │    │
│  │                                                      │    │
│  │  STRIPE                                              │    │
│  │  └─ POST /stripe/create-subscription-session        │    │
│  │                                                      │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                                │
│  ┌───────────────────────────────────────────────────────┐   │
│  │           ORQUESTADORES LEGACY (hardcoded)            │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │                                                       │   │
│  │  TRAINING: E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8 → E9│   │
│  │  NUTRITION: N0 → N1 → N2 → N3 → N4 → N5 → N6 → N7 → N8   │
│  │                                                       │   │
│  │  - Llamadas a OpenAI GPT                             │   │
│  │  - Progreso actualizado en generation_jobs           │   │
│  │  - Output guardado en training_plans/nutrition_plans │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                                │
│  ┌───────────────────────────────────────────────────────┐   │
│  │         BACKGROUND WORKER (asyncio tasks)             │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │                                                       │   │
│  │  process_generation_job(job_id)                      │   │
│  │  └─ Ejecuta orquestador E1-E9 o N0-N8                │   │
│  │  └─ Actualiza progress en generation_jobs             │   │
│  │  └─ Guarda resultado en training_plans/nutrition_plans│   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                                │
│  ┌───────────────────────────────────────────────────────┐   │
│  │            SERVICIOS EDN360 (nuevos)                  │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │                                                       │   │
│  │  edn360_input_builder.py                             │   │
│  │  └─ build_edn360_input_for_user()                    │   │
│  │                                                       │   │
│  │  gpt_service.py                                      │   │
│  │  └─ call_edn360_workflow()                           │   │
│  │                                                       │   │
│  │  edn360_orchestrator_v1.py                           │   │
│  │  └─ run_edn360_workflow_for_user()                   │   │
│  │                                                       │   │
│  │  training_workflow_service.py                        │   │
│  │  └─ call_training_workflow()                         │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                                │
│  ┌───────────────────────────────────────────────────────┐   │
│  │              REPOSITORIES                             │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │                                                       │   │
│  │  client_drawer_repository.py                         │   │
│  │  └─ add_questionnaire_to_drawer()                    │   │
│  │  └─ get_drawer_by_user_id()                          │   │
│  │                                                       │   │
│  │  edn360_snapshot_repository.py                       │   │
│  │  └─ create_snapshot()                                │   │
│  │  └─ get_snapshots_by_user()                          │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                                │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MONGODB                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │          BD WEB (test_database)                      │     │
│  ├──────────────────────────────────────────────────────┤     │
│  │                                                      │     │
│  │  ├─ users                                            │     │
│  │  │  └─ Usuarios, auth, suscripciones                │     │
│  │  │                                                   │     │
│  │  ├─ nutrition_questionnaire_submissions              │     │
│  │  │  └─ Cuestionarios nutricionales                  │     │
│  │  │                                                   │     │
│  │  ├─ questionnaire_submissions                        │     │
│  │  │  └─ Cuestionarios genéricos                      │     │
│  │  │                                                   │     │
│  │  ├─ followup_submissions                             │     │
│  │  │  └─ Cuestionarios de seguimiento                 │     │
│  │  │                                                   │     │
│  │  ├─ training_plans  (LEGACY)                         │     │
│  │  │  └─ Planes de entrenamiento generados            │     │
│  │  │                                                   │     │
│  │  ├─ nutrition_plans (LEGACY)                         │     │
│  │  │  └─ Planes de nutrición generados                │     │
│  │  │                                                   │     │
│  │  └─ generation_jobs (LEGACY)                         │     │
│  │     └─ Jobs asíncronos de generación                │     │
│  │                                                      │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                 │
│  ┌──────────────────────────────────────────────────────┐     │
│  │      BD TÉCNICA EDN360 (edn360_app)                 │     │
│  ├──────────────────────────────────────────────────────┤     │
│  │                                                      │     │
│  │  ├─ client_drawers                                   │     │
│  │  │  └─ Cajón único por usuario (FASE 1)             │     │
│  │  │  └─ services.shared_questionnaires[]             │     │
│  │  │                                                   │     │
│  │  └─ edn360_snapshots                                 │     │
│  │     └─ Snapshots inmutables (FASE 3)                │     │
│  │     └─ input + workflow_response + status           │     │
│  │                                                      │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7️⃣ COLECCIONES MONGODB UTILIZADAS

### BD: `test_database` (BD Web)

#### **users**
```javascript
{
  _id: "<user_id>",
  full_name: "Jorge",
  email: "jorge@example.com",
  password: "<hashed>",
  role: "user" | "admin",
  email_verified: true,
  verification_token: null,
  created_at: ISODate("..."),
  subscription: {
    plan: "individual" | "team" | null,
    status: "active" | "inactive",
    payment_status: "pending" | "verified",
    archived: false,
    archived_reason: null,
    archived_date: null
  }
}
```

#### **nutrition_questionnaire_submissions**
```javascript
{
  _id: "<submission_id>",
  user_id: "<user_id>",
  responses: {
    nombre_completo: "...",
    email: "...",
    // ~100 campos más
  },
  submitted_at: ISODate("..."),
  plan_generated: false,
  plan_id: null
}
```

#### **training_plans** (LEGACY)
```javascript
{
  _id: "<plan_id>",
  user_id: "<user_id>",
  submission_id: "<submission_id>",
  title: "Plan de Hipertrofia...",
  summary: "...",
  goal: "...",
  training_type: "upper_lower",
  days_per_week: 4,
  session_duration_min: 45,
  weeks: 4,
  sessions: [...],
  general_notes: [...],
  created_at: ISODate("...")
}
```

#### **nutrition_plans** (LEGACY)
```javascript
{
  _id: "<plan_id>",
  user_id: "<user_id>",
  submission_id: "<submission_id>",
  title: "Plan Nutricional...",
  summary: "...",
  calories: 2500,
  protein_g: 180,
  carbs_g: 250,
  fats_g: 70,
  meals: [...],
  created_at: ISODate("...")
}
```

#### **generation_jobs** (LEGACY)
```javascript
{
  _id: "<job_id>",
  user_id: "<user_id>",
  type: "training" | "nutrition" | "full",
  submission_id: "<submission_id>",
  status: "pending" | "running" | "completed" | "failed",
  progress: {
    phase: "E1" | "E2" | ...,
    current_agent: "E1",
    completed_steps: ["E1", "E2"],
    percentage: 55
  },
  result: {
    training_plan_id: "<plan_id>",
    nutrition_plan_id: "<plan_id>"
  },
  error_message: null,
  created_at: ISODate("..."),
  updated_at: ISODate("...")
}
```

---

### BD: `edn360_app` (BD Técnica EDN360)

#### **client_drawers**
```javascript
{
  _id: "client_<user_id>",
  user_id: "<user_id>",
  services: {
    shared_questionnaires: [
      {
        submission_id: "<submission_id>",
        submitted_at: ISODate("..."),
        source: "initial" | "followup",
        raw_payload: { ... }
      }
    ],
    training: {
      active_sessions: [],
      historical_sessions: []
    },
    nutrition: {
      active_plans: [],
      historical_plans: []
    }
  },
  created_at: ISODate("..."),
  updated_at: ISODate("...")
}
```

#### **edn360_snapshots**
```javascript
{
  _id: "<snapshot_id>",
  user_id: "<user_id>",
  created_at: ISODate("..."),
  version: "1.0.0",
  input: { 
    user_profile: {...},
    questionnaires: [...]
  },
  workflow_name: "edn360_full_plan_v1" | "training_plan_v1",
  workflow_response: { ... },
  status: "success" | "failed",
  error_message: null
}
```

---

## 8️⃣ ENDPOINTS COMPLETOS DEL BACKEND

### Tabla Completa de Endpoints

| Endpoint | Método | Auth | Descripción | Colecciones | Status |
|----------|--------|------|-------------|-------------|--------|
| `/api/auth/register` | POST | No | Registrar usuario | `users` | ✅ Activo |
| `/api/auth/login` | POST | No | Login | `users` | ✅ Activo |
| `/api/auth/verify-email` | GET | No | Verificar email | `users` | ✅ Activo |
| `/api/auth/me` | GET | User | Usuario actual | `users` | ✅ Activo |
| `/api/users/dashboard` | GET | User | Dashboard usuario | `users`, `training_plans`, `nutrition_plans` | ✅ Activo |
| `/api/nutrition/questionnaire/submit` | POST | User | Enviar cuestionario | `nutrition_questionnaire_submissions`, `client_drawers` | ✅ Activo (Dual-write) |
| `/api/follow-up/submit` | POST | User | Enviar follow-up | `followup_submissions`, `client_drawers` | ✅ Activo (Dual-write) |
| `/api/admin/clients` | GET | Admin | Listar clientes | `users` | ✅ Activo |
| `/api/admin/clients/{user_id}` | GET | Admin | Detalle cliente | `users`, `nutrition_questionnaire_submissions`, `training_plans`, `nutrition_plans` | ✅ Activo |
| `/api/admin/verify-payment/{user_id}` | POST | Admin | Verificar pago | `users` | ✅ Activo |
| `/api/admin/users/{id}/training/generate` | POST | Admin | Generar plan training | `training_plans`, `generation_jobs` | ⚠️ LEGACY - Reemplazar |
| `/api/admin/users/{id}/nutrition/generate` | POST | Admin | Generar plan nutrición | `nutrition_plans`, `generation_jobs` | ⚠️ LEGACY - Reemplazar |
| `/api/jobs/{job_id}` | GET | Public | Estado de job | `generation_jobs` | ⚠️ LEGACY - Eliminar |
| `/api/admin/users/{id}/edn360-input-preview` | GET | Admin | Ver EDN360Input | `users`, `client_drawers` | ✅ NUEVO (FASE 2) |
| `/api/admin/users/{id}/edn360-run-workflow` | POST | Admin | Lanzar workflow EDN360 | `client_drawers`, `edn360_snapshots` | ✅ NUEVO (FASE 3) |
| `/api/training-plan` | POST | User | Generar plan training | `client_drawers`, `edn360_snapshots` | ✅ NUEVO (E1-E7.5) |
| `/api/stripe/create-subscription-session` | POST | User | Pago Stripe | `users` | ✅ Activo |

---

## 🎯 CONCLUSIONES Y RECOMENDACIONES

### Endpoints a Reemplazar/Eliminar

**ELIMINAR**:
1. `POST /api/admin/users/{id}/training/generate` (LEGACY)
2. `POST /api/admin/users/{id}/nutrition/generate` (LEGACY)
3. `GET /api/jobs/{job_id}` (LEGACY - polling)
4. Toda la lógica de `generation_jobs` collection
5. Orquestadores E1-E9 y N0-N8 hardcoded en server.py
6. Función `process_generation_job()` (background worker)

**REEMPLAZAR CON**:
- `POST /api/training-plan` (ya implementado, usa E1-E7.5)
- Futuro: `POST /api/nutrition-plan` (equivalente para nutrición)

---

### Frontend: Cambios Necesarios

**AdminDashboard.jsx**:

1. **Función `generateTrainingPlan()`**:
   - Cambiar de:
     ```javascript
     POST /admin/users/{id}/training/generate
     → polling a GET /jobs/{job_id}
     ```
   - A:
     ```javascript
     POST /training-plan
     → respuesta directa con plan
     ```

2. **Eliminar**:
   - `GenerationProgressModal.jsx` (ya no necesario)
   - Lógica de polling
   - Estado `jobId` y `pollingInterval`

3. **Actualizar renderizado**:
   - Si estructura de `client_training_program_enriched` difiere
   - Adaptar accordion y cards

---

### Backend: Migraciones Pendientes

**Colecciones a mantener**:
- `users` ✅
- `nutrition_questionnaire_submissions` ✅ (BD Web)
- `client_drawers` ✅ (BD Técnica)
- `edn360_snapshots` ✅ (BD Técnica)

**Colecciones a deprecar** (mantener histórico, no escribir nuevos):
- `training_plans` ⚠️ (histórico legacy)
- `nutrition_plans` ⚠️ (histórico legacy)
- `generation_jobs` ⚠️ (eliminar completamente)

**Nueva estructura TO-BE**:
- Los planes se generan con `POST /training-plan`
- El snapshot se guarda en `edn360_snapshots`
- Los planes presentables se extraen de `workflow_response.client_training_program_enriched`
- ¿Crear nueva collection `client_training_programs_final`? (a decidir)

---

### Próximos Pasos Sugeridos

1. **Confirmar arquitectura TO-BE**:
   - ¿Los planes se guardan en nueva collection o solo en snapshots?
   - ¿Cómo manejamos histórico de planes legacy?

2. **Implementar `/api/nutrition-plan`** (equivalente a training)

3. **Migrar frontend**:
   - Actualizar `generateTrainingPlan()` y `generateNutritionPlan()`
   - Eliminar polling y modales legacy
   - Actualizar renderizado de planes

4. **Deprecar endpoints legacy**:
   - Comentar/eliminar código de orquestadores viejos
   - Eliminar `generation_jobs` logic
   - Mantener endpoints de lectura (GET planes) para histórico

5. **Testing completo**:
   - Flujo completo: registro → cuestionario → generación → visualización
   - Verificar dual-write funciona
   - Verificar snapshots se crean correctamente

---

**FIN DEL INFORME TÉCNICO**

---

Este informe documenta el sistema actual completo. Ahora puedes diseñar el TO-BE y dar instrucciones precisas para la migración. 🚀
