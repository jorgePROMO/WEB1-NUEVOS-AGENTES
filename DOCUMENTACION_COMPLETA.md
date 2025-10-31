# 📋 DOCUMENTACIÓN COMPLETA - ECJ TRAINER
## Sistema de Gestión de Entrenamiento Personal

**Versión:** 1.0  
**Fecha:** Octubre 2025  
**Stack:** React + FastAPI + MongoDB  

---

## 📑 ÍNDICE

1. [Arquitectura General](#1-arquitectura-general)
2. [Stack Tecnológico](#2-stack-tecnológico)
3. [Base de Datos](#3-base-de-datos)
4. [Autenticación y Seguridad](#4-autenticación-y-seguridad)
5. [Landing Page](#5-landing-page)
6. [Panel de Usuario](#6-panel-de-usuario)
7. [Panel de Administrador](#7-panel-de-administrador)
8. [Sistema de Templates](#8-sistema-de-templates)
9. [Sistema CRM](#9-sistema-crm)
10. [Sistema de Calendario](#10-sistema-de-calendario)
11. [Sistema de Alertas](#11-sistema-de-alertas)
12. [Sistema de Chat](#12-sistema-de-chat)
13. [Gestión de Documentos](#13-gestión-de-documentos)
14. [Sistema de Cuestionarios](#14-sistema-de-cuestionarios)
15. [PWA (Progressive Web App)](#15-pwa-progressive-web-app)
16. [Emails Automatizados](#16-emails-automatizados)
17. [APIs y Endpoints](#17-apis-y-endpoints)
18. [Variables de Entorno](#18-variables-de-entorno)
19. [Deployment](#19-deployment)
20. [Flujos Completos](#20-flujos-completos)

---

## 1. ARQUITECTURA GENERAL

### 1.1 Estructura de Carpetas

```
/app
├── backend/
│   ├── server.py          # API principal (FastAPI)
│   ├── auth.py            # Autenticación y seguridad
│   ├── email_utils.py     # Envío de emails
│   ├── models.py          # Modelos Pydantic
│   ├── requirements.txt   # Dependencias Python
│   └── .env              # Variables de entorno backend
│
├── frontend/
│   ├── public/
│   │   ├── manifest.json        # PWA manifest
│   │   ├── service-worker.js    # Service Worker PWA
│   │   └── icon.svg             # Icono de la app
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/              # Componentes Shadcn
│   │   │   ├── AdminComponents.jsx
│   │   │   ├── Calendar.jsx
│   │   │   ├── ChatBox.jsx
│   │   │   ├── ClientsAtRisk.jsx
│   │   │   ├── DiagnosisQuestionnaire.jsx
│   │   │   ├── ExternalClientsCRM.jsx
│   │   │   ├── Footer.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── ProspectsCRM.jsx
│   │   │   ├── ProfileComponents.jsx
│   │   │   ├── TeamClientsCRM.jsx
│   │   │   ├── TemplatesManager.jsx
│   │   │   └── [otros componentes de landing]
│   │   ├── context/
│   │   │   └── AuthContext.jsx  # Context de autenticación
│   │   ├── pages/
│   │   │   ├── AdminDashboard.jsx
│   │   │   ├── UserDashboard.jsx
│   │   │   ├── LandingPage.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── ResetPassword.jsx
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── .env              # Variables de entorno frontend
│
└── [archivos de documentación]
```

### 1.2 Flujo de Datos

```
Cliente (Navegador/PWA)
    ↓
Frontend React (puerto 3000)
    ↓
Backend FastAPI (puerto 8001) - /api/*
    ↓
MongoDB (puerto 27017)
```

### 1.3 Principios de Diseño

- **Single Page Application (SPA)** con React Router
- **RESTful API** con FastAPI
- **JWT Authentication** con cookies httpOnly
- **Responsive First** - Optimizado para móvil
- **PWA** - Instalable como app nativa
- **Soft Delete** - No se borran datos, se marcan como deleted

---

## 2. STACK TECNOLÓGICO

### 2.1 Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| React | 18.x | Framework principal |
| React Router | 6.x | Navegación SPA |
| Axios | 1.x | Cliente HTTP |
| Tailwind CSS | 3.x | Estilos utility-first |
| Shadcn UI | Latest | Componentes UI |
| Lucide React | Latest | Iconos |

### 2.2 Backend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| FastAPI | 0.104+ | Framework API |
| Python | 3.10+ | Lenguaje |
| Motor | Latest | Driver MongoDB async |
| PyJWT | 2.x | JSON Web Tokens |
| Bcrypt | 4.x | Hash de passwords |
| Python-Multipart | Latest | Upload de archivos |
| HTTPX | Latest | Cliente HTTP async |

### 2.3 Base de Datos

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| MongoDB | 5.0+ | Base de datos NoSQL |

### 2.4 PWA

| Tecnología | Propósito |
|------------|-----------|
| Service Worker | Caché offline |
| Web Manifest | Metadata de app |
| Web App Meta Tags | iOS/Android support |

---

## 3. BASE DE DATOS

### 3.1 Colecciones MongoDB

#### 3.1.1 `users` - Usuarios del Sistema

```javascript
{
  _id: "timestamp-based-id",           // String UUID
  email: "user@email.com",              // Único
  username: "username",                 
  name: "Nombre Completo",
  password: "bcrypt_hash",              // Hash bcrypt
  role: "user" | "admin",               // Rol del usuario
  status: "active" | "deleted",         // Soft delete
  picture: "url_to_picture",            // Opcional (OAuth)
  whatsapp: "+34600000000",             // Opcional
  subscription: {
    plan: "team" | "individual",
    status: "pending" | "active" | "paused" | "inactive",
    payment_status: "pending" | "verified",
    start_date: ISODate,
    stripe_customer_id: "cus_xxx"      // Opcional
  },
  next_review: ISODate,                 // Opcional
  created_at: ISODate,
  updated_at: ISODate,
  deleted_at: ISODate,                  // Si status = deleted
  deleted_by: "admin_id"                // Si fue borrado
}
```

**Índices:**
- `email` (unique)
- `role`
- `status`

#### 3.1.2 `deleted_users` - Log de Usuarios Borrados

```javascript
{
  email: "user@email.com",
  user_id: "original_user_id",
  deleted_at: ISODate,
  deleted_by: "admin_id",
  reason: "preventive_block" | "user_request" | "admin_action"
}
```

**Propósito:** Bloquear reautenticación de usuarios eliminados (especialmente OAuth)

#### 3.1.3 `sessions` - Sesiones de Entrenamiento

```javascript
{
  _id: "session-id",
  user_id: "user_id",
  title: "Título de la sesión",
  date: ISODate,
  time: "HH:MM:SS",
  duration: 60,                         // minutos
  location: "Online" | "Presencial",
  notes: "Notas de la sesión",
  created_at: ISODate,
  created_by: "admin_id"
}
```

**Índices:**
- `user_id`
- `date`

#### 3.1.4 `pdfs` - Documentos PDF

```javascript
{
  _id: "pdf-id",
  user_id: "user_id",
  title: "Título del documento",
  file_path: "/path/to/file.pdf",
  url: "/api/pdfs/download/pdf-id",
  uploaded_at: ISODate,
  uploaded_by: "admin_id",
  size: 123456                          // bytes
}
```

**Índices:**
- `user_id`

**Storage:** Archivos físicos en `/app/backend/uploads/`

#### 3.1.5 `alerts` - Alertas para Usuarios

```javascript
{
  _id: "alert-id",
  user_id: "user_id",
  title: "Título de la alerta",
  message: "Mensaje de la alerta",
  type: "info" | "warning" | "success" | "error",
  read: false,
  created_at: ISODate,
  created_by: "admin_id"
}
```

**Índices:**
- `user_id`
- `read`

#### 3.1.6 `messages` - Chat Bidireccional

```javascript
{
  _id: "message-id",
  user_id: "user_id",
  sender_id: "sender_id",
  sender_role: "user" | "admin",
  content: "Contenido del mensaje",
  timestamp: ISODate,
  read: false
}
```

**Índices:**
- `user_id`
- `timestamp`
- `read`

#### 3.1.7 `message_templates` - Templates de Mensajes

```javascript
{
  _id: "template-id",
  type: "whatsapp" | "alert" | "email",
  name: "Nombre del template",
  subject: "Asunto",                    // Solo para email
  content: "Hola {nombre}, tu sesión es el {fecha}",
  category: "general",                  // Deprecated
  tags: ["bienvenida", "recordatorio"], // Array de strings
  variables: ["nombre", "fecha", "hora"],
  created_at: ISODate,
  updated_at: ISODate
}
```

**Índices:**
- `type`
- `tags`

#### 3.1.8 `global_tags` - Etiquetas Globales

```javascript
{
  _id: "tag-name",                      // El nombre es el ID
  created_at: ISODate
}
```

**Propósito:** Gestión centralizada de etiquetas para templates

#### 3.1.9 `questionnaire_responses` - Cuestionario Diagnóstico

```javascript
{
  _id: "response-id",
  nombre: "Nombre",
  email: "email@example.com",
  telefono: "+34600000000",
  objetivo: "perder_peso" | "ganar_masa" | "mantenimiento",
  experiencia: "ninguna" | "basica" | "intermedia" | "avanzada",
  restricciones: "Texto libre",
  disponibilidad: "Texto libre",
  presupuesto: "Rango de presupuesto",
  converted_to_client: false,           // Si se convirtió en cliente
  status: "pending" | "contacted" | "converted" | "rejected",
  created_at: ISODate,
  contacted_at: ISODate,                // Opcional
  notes: "Notas del admin"              // Opcional
}
```

**Índices:**
- `email` (unique)
- `converted_to_client`
- `status`

#### 3.1.10 `external_clients` - Clientes Externos (no web)

```javascript
{
  _id: "client-id",
  nombre: "Nombre del cliente",
  email: "email@example.com",
  whatsapp: "+34600000000",
  objetivo: "Objetivo del cliente",
  plan_weeks: 12,                       // Duración del plan
  weeks_completed: 0,                   // Semanas completadas
  start_date: ISODate,
  next_payment_date: ISODate,
  status: "active" | "inactive",
  notes: "Notas del admin",
  created_at: ISODate,
  updated_at: ISODate
}
```

**Índices:**
- `email`
- `status`

#### 3.1.11 `team_client_notes` - Notas de Clientes

```javascript
{
  _id: "note-id",
  client_id: "user_id",
  content: "Contenido de la nota",
  created_at: ISODate,
  created_by: "admin_id"
}
```

**Índices:**
- `client_id`

#### 3.1.12 `automation_config` - Configuración de Automatizaciones

```javascript
{
  _id: "config-id",
  type: "reminder_session" | "renewal_reminder",
  enabled: true,
  schedule: "daily" | "weekly",
  template_id: "template-id",
  conditions: {},
  created_at: ISODate,
  updated_at: ISODate
}
```

---

## 4. AUTENTICACIÓN Y SEGURIDAD

### 4.1 Sistema de Autenticación

**Método:** JWT (JSON Web Tokens) + HTTP-Only Cookies

#### 4.1.1 Registro Manual

**Endpoint:** `POST /api/auth/register`

**Flujo:**
1. Usuario completa formulario (username, email, password)
2. Backend valida email único
3. Password se hashea con bcrypt (cost factor 12)
4. Usuario se crea en BD con role="user", status="active"
5. Subscription por defecto: plan="team", status="pending"
6. Se genera JWT token
7. Token se devuelve + datos de usuario

**Validaciones:**
- Email válido y único
- Password mínimo 6 caracteres
- Username no vacío

#### 4.1.2 Login Manual

**Endpoint:** `POST /api/auth/login`

**Flujo:**
1. Usuario ingresa email + password
2. Backend busca usuario por email
3. Verifica password con bcrypt
4. Verifica que status != "deleted"
5. Genera JWT token con user_id
6. Devuelve token + datos usuario

**Validaciones:**
- Usuario existe
- Password correcto
- Usuario no eliminado

#### 4.1.3 Soft Delete

Cuando se elimina un usuario:
1. NO se borra de `users`
2. Se marca `status: "deleted"`
3. Se guarda `deleted_at` y `deleted_by`
4. Se agrega registro a `deleted_users` con email
5. Login y OAuth bloquean usuarios con status="deleted"
6. OAuth bloquea emails en `deleted_users`

### 4.2 Autorización

#### 4.2.1 Roles

- **user**: Acceso a UserDashboard
- **admin**: Acceso a AdminDashboard + todas las funciones de gestión

#### 4.2.2 Protección de Rutas (Frontend)

```javascript
// AuthContext verifica token y role
const PrivateRoute = ({ children, adminOnly }) => {
  if (!user) return <Navigate to="/login" />;
  if (adminOnly && user.role !== 'admin') return <Navigate to="/dashboard" />;
  return children;
};
```

#### 4.2.3 Protección de Endpoints (Backend)

```python
# Decoradores de autenticación
async def get_current_user(request):
    # Valida JWT token
    # Retorna usuario o HTTPException 401

async def require_admin(request):
    # Valida JWT token
    # Verifica role == "admin"
    # Retorna admin o HTTPException 403
```

### 4.3 Seguridad

- **Passwords:** Bcrypt con cost factor 12
- **Tokens JWT:** Secret key en variable de entorno
- **CORS:** Configurado para frontend específico
- **HTTPOnly Cookies:** Tokens no accesibles desde JavaScript
- **HTTPS:** Requerido en producción
- **Validación de Inputs:** Pydantic models en todos los endpoints

---

## 5. LANDING PAGE

### 5.1 Secciones

#### 5.1.1 Header
- Logo + Navegación
- Botones: "Cliente" y "Administrador"
- Responsive: Hamburger menu en móvil

#### 5.1.2 Hero Section
- Título principal
- Subtítulo
- CTA: "Quiero este plan" → Redirige a /register

#### 5.1.3 Services Section
- Cards con servicios ofrecidos
- Iconos + descripciones

#### 5.1.4 Method Section
- Descripción de la metodología
- Pasos del proceso

#### 5.1.5 Transformations Section
- Casos de éxito (opcional con imágenes)

#### 5.1.6 Testimonials Section
- Testimonios de clientes
- Carrusel o grid

#### 5.1.7 Comparison Table
- Tabla comparativa de planes
- Plan destacado

#### 5.1.8 About Section
- Información sobre el entrenador
- Experiencia y certificaciones

#### 5.1.9 Diagnosis Questionnaire (On-page)
- Formulario en la misma landing
- Campos: nombre, email, teléfono, objetivo, experiencia, etc.
- Al enviar: guarda en `questionnaire_responses`
- Email automático al admin con los datos

#### 5.1.10 Final CTA Section
- Último llamado a la acción
- Botón a registro

#### 5.1.11 Footer
- Links legales
- Redes sociales
- Copyright

### 5.2 SEO

- Meta tags configurados
- Open Graph tags
- Título descriptivo
- Meta description

---

## 6. PANEL DE USUARIO

**Ruta:** `/dashboard`  
**Acceso:** Solo usuarios con role="user"

### 6.1 Layout

#### 6.1.1 Header
- Título: "Panel Usuario"
- Badge de "Pago pendiente" (si aplica)
- Nombre de usuario
- Botón "Salir"

#### 6.1.2 Tabs de Navegación
- **Responsive:**
  - Móvil: 3 columnas (Resumen, Cal, Docs / Alertas, Chat, Perfil)
  - Desktop: 6 columnas en una fila
- Pestañas:
  1. Resumen
  2. Calendario
  3. Documentos
  4. Alertas
  5. Chat
  6. Perfil

### 6.2 Tab: Resumen

#### 6.2.1 Alerta de Pago Pendiente
- Card destacada si `subscription.payment_status == "pending"`
- Botón "Pagar ahora - 49,90€/mes"
- Icono de alerta naranja

#### 6.2.2 Card: Mi Suscripción
**Datos mostrados:**
- Plan: `subscription.plan` → "Trabaja con mi equipo" o "Individual"
- Estado: `subscription.status` → "Activo" / "Pausado" / "Inactivo" (badge con colores)
- Pago: `subscription.payment_status` → "Verificado" / "Pendiente" (badge con colores)
- Inicio: `subscription.start_date` → Formato dd/mm/yyyy

**Colores:**
- Estado Activo: Verde
- Estado Pausado: Amarillo
- Estado Inactivo: Rojo
- Pago Verificado: Verde
- Pago Pendiente: Naranja

#### 6.2.3 Card: Próximas Sesiones
- Lista de próximas 3 sesiones desde `sessions`
- Formato: "DD MMM - HH:MM - Título"
- Si no hay: Mensaje "No tienes sesiones programadas"

#### 6.2.4 Card: Mis Documentos
- Lista de últimos 3 PDFs desde `pdfs`
- Botón "Descargar" por cada uno
- Link "Ver todos" → Tab Documentos

#### 6.2.5 Card: Alertas Recientes
- Últimas 3 alertas desde `alerts`
- Badge de tipo (info/warning/success)
- Link "Ver todas" → Tab Alertas

### 6.3 Tab: Calendario

**Componente:** `<UserCalendar />`

#### 6.3.1 Funcionalidades
- Vista de calendario mensual
- Muestra sesiones del usuario
- Click en sesión → Modal con detalles
- **Usuario puede:**
  - Ver detalles de sesión
  - **Cancelar sesión** (llama DELETE /sessions/{id})
  - **Reagendar sesión** (llama PATCH /sessions/{id}/reschedule)

#### 6.3.2 Notificaciones por Email
- **Cancelar sesión:** Email SOLO al admin
- **Reagendar sesión:** Email SOLO al admin

### 6.4 Tab: Documentos

#### 6.4.1 Lista de PDFs
- Tabla con todas las PDFs del usuario
- Columnas: Título, Fecha subida, Acciones
- Botón "Descargar" por cada PDF

#### 6.4.2 Descarga
**Endpoint:** `GET /api/pdfs/download/{pdf_id}`
- Verificación: Solo el dueño puede descargar
- Stream del archivo PDF

### 6.5 Tab: Alertas

#### 6.5.1 Lista de Alertas
- Todas las alertas del usuario (más recientes primero)
- Card por alerta con:
  - Título
  - Mensaje
  - Fecha/hora
  - Tipo (badge de color)
  - Estado: Leída / No leída

#### 6.5.2 Marcar como Leída
- Click en alerta → Se marca `read: true`
- Contador de no leídas en badge del tab

### 6.6 Tab: Chat

**Componente:** `<ChatBox />`

#### 6.6.1 Funcionalidades
- Chat bidireccional con admin
- **Usuario puede:**
  - Enviar mensajes al admin
  - Ver mensajes del admin
- Mensajes en tiempo real (polling cada X segundos)

#### 6.6.2 Envío de Mensaje
**Endpoint:** `POST /api/messages`
```javascript
{
  user_id: "user_id",
  content: "Mensaje del usuario"
}
```

#### 6.6.3 Visualización
- Mensajes propios: Alineados a la derecha, color azul
- Mensajes del admin: Alineados a la izquierda, color gris
- Scroll automático a último mensaje

### 6.7 Tab: Perfil

#### 6.7.1 Información del Usuario
**Datos mostrados:**
- Nombre
- Username
- Email
- WhatsApp (si existe)

#### 6.7.2 Editar Perfil
**Componente:** `<EditProfileForm />`
- Usuario puede cambiar:
  - Nombre
  - WhatsApp
  - Contraseña (con confirmación)

**Endpoint:** `PATCH /api/users/me`

#### 6.7.3 Subir Documentos
**Componente:** `<UploadDocumentForm />`
- Usuario puede subir archivos (opcional si está habilitado)
- Tipos permitidos: PDF, imágenes, etc.

---

## 7. PANEL DE ADMINISTRADOR

**Ruta:** `/admin`  
**Acceso:** Solo usuarios con role="admin"

### 7.1 Layout

#### 7.1.1 Header
- Logo
- Título: "Panel de Administración"
- Nombre del admin
- Botón "Salir"

#### 7.1.2 Vista Principal: Dashboard Overview

**Tarjetas de Resumen:**
1. **Total Clientes Activos**
   - Número de usuarios con status="active"
   
2. **Pagos Pendientes**
   - Número de usuarios con payment_status="pending"
   
3. **Sesiones Hoy**
   - Número de sesiones programadas para hoy
   
4. **Nuevos Prospectos**
   - Número de questionnaire_responses no contactados

**Sección: Clientes Activos**
- Lista de últimos 10 usuarios activos
- Por cada uno:
  - Nombre
  - Email
  - Plan
  - Estado de pago
  - Botones de acciones rápidas

**Tarjetas de Navegación CRM:**
1. CRM Clientes Equipo
2. CRM Clientes Externos
3. CRM Prospectos

### 7.2 Tabs de Navegación

Tabs principales:
1. **Vista General** (dashboard)
2. **Gestión de Clientes Activos**
3. **Templates**
4. **Clientes en Riesgo**

### 7.3 Tab: Gestión de Clientes Activos

**Propósito:** Gestionar usuarios registrados en la web (colección `users`)

#### 7.3.1 Lista de Clientes

**Tabla con columnas:**
- Nombre
- Email
- Fecha de registro
- Plan (team/individual)
- Estado de pago (badge con color)
- Estado de suscripción
- Acciones (botones)

**Búsqueda y Filtros:**
- Buscador por nombre o email
- Filtro por estado de pago
- Filtro por plan

#### 7.3.2 Seleccionar Cliente

Al hacer click en un cliente:
- Panel lateral o sección expandida
- Muestra información completa del cliente

**Información Mostrada:**
- Datos personales
- Suscripción completa
- Próximas sesiones
- Documentos
- Alertas
- Historial de chat

#### 7.3.3 Acciones sobre Cliente

**Botones disponibles:**

1. **Editar Info**
   - Modal con formulario
   - Campos editables:
     - Nombre
     - Email
     - Estado de suscripción (pending/active/paused/inactive)
     - Plan (team/individual)
     - Estado de pago (pending/verified)
   - **Endpoint:** `PATCH /admin/users/{user_id}`
   - **Sincronización:** Cambios se reflejan INMEDIATAMENTE en:
     - Panel del usuario
     - Todas las vistas de CRM

2. **Templates**
   - Abre selector de templates
   - Filtrado por etiquetas con dropdown
   - Al seleccionar template:
     - Vista previa con variables reemplazadas
     - Opciones de envío:
       - WhatsApp (abre link wa.me)
       - Email (envía desde servidor)
       - Alerta (crea en BD)
       - Chat (crea mensaje)

3. **Subir PDF**
   - Modal de upload de archivos
   - Usuario puede descargar desde su panel
   - **Endpoint:** `POST /admin/pdfs/upload`

4. **Nueva Sesión**
   - Modal con formulario de sesión
   - Campos: fecha, hora, título, notas
   - **Endpoint:** `POST /api/sessions/create`
   - **Notificación:** Email SOLO al cliente

5. **Ver Chat**
   - Abre chat bidireccional
   - Admin puede enviar mensajes
   - Ve historial completo

6. **Archivar**
   - Cambia status a "inactive" (soft delete disponible con mejora)
   - Cliente deja de aparecer en lista activa

7. **Eliminar**
   - **Soft delete:** Marca `status: "deleted"`
   - Agrega a `deleted_users`
   - Cliente NO puede volver a autenticarse
   - Datos se conservan para auditoría

### 7.4 Tab: Templates

**Componente:** `<TemplatesManager />`

#### 7.4.1 Funcionalidades Principales

**Gestión de Templates:**
1. **Ver Templates**
   - Lista de todos los templates
   - Cards con: Nombre, Tipo, Contenido, Etiquetas
   
2. **Filtrar por Etiquetas**
   - Dropdown con todas las etiquetas disponibles
   - Opción "Todas las etiquetas"
   - Muestra solo templates con etiqueta seleccionada

3. **Crear Template**
   - Modal con formulario
   - Campos:
     - Nombre *
     - Tipo: WhatsApp / Alerta / Email
     - Asunto (solo email)
     - Contenido * (con variables {nombre}, {fecha}, {hora})
     - Etiquetas (dropdown multi-select)
   - **Endpoint:** `POST /admin/templates`

4. **Editar Template**
   - Abre modal pre-rellenado
   - Todos los campos editables (excepto tipo)
   - Etiquetas editables (agregar/quitar)
   - **Endpoint:** `PATCH /admin/templates/{template_id}`

5. **Eliminar Template**
   - Confirmación
   - **Endpoint:** `DELETE /admin/templates/{template_id}`

#### 7.4.2 Gestión de Etiquetas Globales

**Botón:** "Gestionar Etiquetas" (icono de tag)

**Modal de Gestión:**

1. **Ver Todas las Etiquetas**
   - Lista de etiquetas en `global_tags`
   - Badge por etiqueta

2. **Crear Etiqueta**
   - Input + Botón "Crear"
   - **Endpoint:** `POST /admin/templates/tags`
   - Se agrega a `global_tags`
   - Disponible inmediatamente en dropdowns

3. **Eliminar Etiqueta**
   - Botón de basura por etiqueta
   - **Validación:** Verifica si está en uso
   - Si está en uso:
     - Muestra alerta: "Esta etiqueta está asignada a X templates"
     - NO permite eliminar
   - Si NO está en uso:
     - Elimina de `global_tags`
   - **Endpoint:** `DELETE /admin/templates/tags/{tag_name}`

#### 7.4.3 Sistema de Variables en Templates

**Variables Disponibles:**
- `{nombre}` → Nombre del usuario
- `{fecha}` → Fecha actual o de sesión
- `{hora}` → Hora de sesión
- `{plan}` → Plan de suscripción
- `{email}` → Email del usuario

**Reemplazo Automático:**
- Al usar template, variables se reemplazan con datos reales del cliente

### 7.5 Tab: Clientes en Riesgo

**Componente:** `<ClientsAtRisk />`

**Propósito:** Identificar clientes que necesitan atención

#### 7.5.1 Indicadores de Riesgo

**Criterios configurables:**
1. Pago pendiente > 7 días
2. Sin sesión programada próxima
3. Sin actividad en chat > 14 días
4. Suscripción en estado "paused"

#### 7.5.2 Vista de Clientes

**Lista con:**
- Nombre del cliente
- Indicador de riesgo (badge rojo/amarillo/naranja)
- Motivo del riesgo
- Última actividad
- Botones de acción:
  - Contactar (abre chat)
  - Ver perfil (va a gestión de clientes)

### 7.6 CRM: Clientes Equipo

**Componente:** `<TeamClientsCRM />`

**Datos:** Usuarios de colección `users` con role="user"

#### 7.6.1 Tabla de Clientes

**Columnas:**
- Nombre
- Email
- Fecha Registro
- Plan (badge)
- Estado Pago (badge con colores)
- Estado (dropdown editable)
- Acciones

**Estado Dropdown:**
- Pending
- Active
- Inactive
- **Cambio en tiempo real:** `PATCH /admin/team-clients/{client_id}/status`

#### 7.6.2 Acciones

**Botones:**
1. **WhatsApp Directo**
   - Link `wa.me/{numero}?text=...`
   
2. **Eliminar**
   - Soft delete
   - Mueve a `deleted_users`

### 7.7 CRM: Clientes Externos

**Componente:** `<ExternalClientsCRM />`

**Datos:** Clientes de colección `external_clients`

**Propósito:** Gestionar clientes que NO se registraron en la web (contacto directo, Instagram, etc.)

#### 7.7.1 Crear Cliente Externo

**Modal con campos:**
- Nombre *
- Email
- WhatsApp
- Objetivo
- Plan (semanas)
- Fecha inicio
- Semanas completadas

**Endpoint:** `POST /api/admin/external-clients`

#### 7.7.2 Tabla de Clientes Externos

**Columnas:**
- Nombre
- Email
- WhatsApp
- Objetivo
- Plan (X/Y semanas)
- Próximo pago
- Estado
- Acciones

#### 7.7.3 Acciones

**Botones:**
1. **Editar**
   - Modal pre-rellenado
   - **Endpoint:** `PATCH /api/admin/external-clients/{client_id}`

2. **WhatsApp**
   - Link directo

3. **Cambiar Estado**
   - Active / Inactive
   - **Endpoint:** `PATCH /api/admin/external-clients/{client_id}/status`

4. **Eliminar**
   - Borrado definitivo (no soft delete porque no tienen cuenta)
   - **Endpoint:** `DELETE /api/admin/external-clients/{client_id}`

### 7.8 CRM: Prospectos

**Componente:** `<ProspectsCRM />`

**Datos:** Registros de `questionnaire_responses`

**Propósito:** Gestionar personas que llenaron el cuestionario pero aún no son clientes

#### 7.8.1 Tabla de Prospectos

**Columnas:**
- Nombre
- Email
- Teléfono
- Objetivo
- Experiencia
- Presupuesto
- Fecha
- Estado
- Acciones

#### 7.8.2 Estados de Prospecto

- **Pending:** Recién llegado, no contactado
- **Contacted:** Ya se contactó
- **Converted:** Se convirtió en cliente
- **Rejected:** No interesado / no viable

#### 7.8.3 Acciones

**Botones:**
1. **Ver Detalles**
   - Modal con toda la información del cuestionario

2. **Contactar**
   - Marca como "contacted"
   - Abre WhatsApp o email

3. **Convertir a Cliente**
   - Opción 1: Crear en Clientes Externos
   - Opción 2: Enviar invitación a registrarse en web
   - Marca `converted_to_client: true`

4. **Rechazar**
   - Marca estado como "rejected"
   - Opcional: agregar nota del motivo

5. **Eliminar**
   - Borrado definitivo

---

## 8. SISTEMA DE TEMPLATES

### 8.1 Arquitectura

**Colecciones:**
- `message_templates`: Los templates
- `global_tags`: Etiquetas disponibles

### 8.2 Tipos de Templates

1. **WhatsApp**
   - Texto corto
   - Se envía vía link wa.me
   - Mensaje pre-rellenado

2. **Alerta**
   - Se crea en colección `alerts`
   - Usuario ve en su panel
   - Notificación visual

3. **Email**
   - Se envía vía SMTP
   - Asunto + contenido
   - Función `send_template_email()` en `email_utils.py`

### 8.3 Variables en Templates

**Formato:** `{variable_name}`

**Procesamiento:**
```python
def replace_variables(template_content, client_data):
    content = template_content
    content = content.replace("{nombre}", client_data["name"])
    content = content.replace("{email}", client_data["email"])
    content = content.replace("{fecha}", datetime.now().strftime("%d/%m/%Y"))
    # ... más variables
    return content
```

### 8.4 Sistema de Etiquetas

**Propósito:** Organizar templates por categoría/uso

**Flujo:**
1. Admin crea etiqueta global
2. Etiqueta se guarda en `global_tags` con `_id = nombre_etiqueta`
3. Al crear/editar template, admin selecciona etiquetas del dropdown
4. Template guarda array `tags: ["etiqueta1", "etiqueta2"]`
5. Filtrado: Busca templates donde `tags` contiene etiqueta seleccionada

**Validación al Eliminar:**
```python
# Cuenta cuántos templates usan la etiqueta
count = await db.message_templates.count_documents({"tags": tag_name})
if count > 0:
    raise HTTPException(400, f"La etiqueta está asignada a {count} templates")
```

### 8.5 Uso de Templates

**Desde Gestión de Clientes:**
1. Admin selecciona cliente
2. Click "Templates"
3. Modal con lista de templates
4. Filtro por etiqueta (dropdown)
5. Click en template → Modal de envío
6. Opciones:
   - **Enviar por WhatsApp:** Abre wa.me con mensaje
   - **Enviar por Email:** Ejecuta `send_template_email()`
   - **Crear Alerta:** INSERT en `alerts`
   - **Enviar Chat:** INSERT en `messages`

---

## 9. SISTEMA CRM

### 9.1 Tipos de Clientes

1. **Clientes del Equipo (Team Clients)**
   - Fuente: Colección `users` (role="user")
   - Registrados en la web
   - Tienen acceso al UserDashboard
   - Estado gestionado desde `TeamClientsCRM`

2. **Clientes Externos**
   - Fuente: Colección `external_clients`
   - No registrados en web (contacto directo, Instagram, etc.)
   - NO tienen acceso al sistema
   - Gestión manual completa

3. **Prospectos**
   - Fuente: Colección `questionnaire_responses`
   - Llenaron cuestionario diagnóstico
   - Aún no son clientes
   - Pueden convertirse en cualquiera de los 2 tipos anteriores

### 9.2 Flujo de Conversión

```
Prospecto (questionnaire_responses)
    ↓
  [Admin contacta]
    ↓
  [Admin decide]
    ↓
    ├─→ Cliente Externo (external_clients)
    │   - Crear manualmente
    │   - Gestión 100% manual
    │
    └─→ Cliente del Equipo (users)
        - Invitar a registrarse
        - Usuario crea cuenta
        - Acceso al panel
```

### 9.3 Sincronización de Datos

**Problema Original:** Cambios en admin no se reflejaban en panel usuario

**Solución Implementada:**

#### 9.3.1 Backend
**Endpoint:** `PATCH /admin/users/{user_id}`

**Flujo:**
1. Recibe datos a actualizar
2. Actualiza registro en colección `users`
3. Devuelve usuario actualizado

**Campos actualizables:**
- `name`
- `email`
- `subscription.status`
- `subscription.plan`
- `subscription.payment_status`

#### 9.3.2 Frontend
**UserDashboard:**
- Usa datos DINÁMICOS de `userData.subscription`
- NO hardcoded
- Al recargar dashboard, obtiene datos actuales de `/api/users/dashboard`

**AdminDashboard:**
- Al editar usuario, llama a `PATCH /admin/users/{user_id}`
- Recarga lista de clientes
- Cambios visibles inmediatamente en todas las vistas

### 9.4 Estados de Pago

**Valores posibles:**
- `pending`: No verificado
- `verified`: Verificado por admin

**Visualización:**
- UserDashboard: Badge con color (naranja/verde)
- AdminDashboard: Badge en todas las vistas de CRM
- Sincronizado en tiempo real

---

## 10. SISTEMA DE CALENDARIO

### 10.1 Arquitectura

**Colección:** `sessions`

**Componentes:**
- `<UserCalendar />` - Vista del usuario
- Admin usa componente integrado en gestión de clientes

### 10.2 Crear Sesión (Admin)

**Flujo:**
1. Admin selecciona cliente
2. Click "Nueva Sesión"
3. Modal con formulario:
   - Título
   - Fecha
   - Hora
   - Notas (opcional)
4. **Endpoint:** `POST /api/sessions/create`
5. **Notificación por Email:** SOLO al cliente

**Email al Cliente:**
- Asunto: "Nueva sesión programada"
- Contenido: Fecha, hora, título, notas
- Link al UserDashboard

### 10.3 Ver Calendario (Usuario)

**UserDashboard → Tab Calendario**

1. Usuario ve calendario mensual
2. Sesiones marcadas en fechas correspondientes
3. Click en sesión → Modal con detalles

### 10.4 Reagendar Sesión

**Quién puede:** Usuario o Admin

**Flujo Usuario:**
1. Click en sesión
2. Modal con detalles
3. Botón "Reagendar"
4. Selector de nueva fecha
5. **Endpoint:** `PATCH /api/sessions/{session_id}/reschedule`
6. **Notificación por Email:** SOLO al admin

**Flujo Admin:**
1. Busca sesión en gestión de clientes
2. Edita fecha
3. **Notificación por Email:** SOLO al cliente

### 10.5 Cancelar Sesión

**Quién puede:** Usuario o Admin

**Flujo Usuario:**
1. Click en sesión
2. Modal con detalles
3. Botón "Cancelar"
4. Confirmación
5. **Endpoint:** `DELETE /api/sessions/{session_id}`
6. **Notificación por Email:** SOLO al admin

**Flujo Admin:**
1. Elimina desde gestión de clientes
2. **NO se envía email** (asume que admin ya lo sabe)

### 10.6 Notificaciones por Email

**Lógica condicional en backend:**

```python
# Crear sesión
if created_by == "admin":
    send_email_to_user()  # Solo al cliente

# Reagendar sesión
if current_user.role == "user":
    send_email_to_admin()  # Cliente reagenda → Email a admin
else:
    send_email_to_user()   # Admin reagenda → Email a cliente

# Cancelar sesión
if current_user.role == "user":
    send_email_to_admin()  # Cliente cancela → Email a admin
else:
    pass  # Admin cancela → NO email
```

---

## 11. SISTEMA DE ALERTAS

### 11.1 Arquitectura

**Colección:** `alerts`

**Propósito:** Notificaciones internas del sistema

### 11.2 Crear Alerta (Admin)

**Métodos:**

1. **Desde Template**
   - Admin usa template de tipo "alerta"
   - Envía a cliente específico
   - Se crea registro en `alerts`

2. **Manual (futuro)**
   - Admin crea alerta directamente
   - Campos: título, mensaje, tipo, cliente

**Endpoint:** `POST /api/alerts` (usado internamente por templates)

### 11.3 Ver Alertas (Usuario)

**UserDashboard → Tab Alertas**

1. Lista de todas las alertas del usuario
2. Ordenadas por fecha (más recientes primero)
3. Badge de tipo:
   - Info: Azul
   - Warning: Amarillo
   - Success: Verde
   - Error: Rojo
4. Badge "Nueva" si no leída

### 11.4 Marcar como Leída

**Flujo:**
1. Usuario hace click en alerta
2. Se expande contenido completo
3. **Endpoint:** `PATCH /api/alerts/{alert_id}/read`
4. Actualiza `read: true`
5. Decrementa contador de no leídas en badge del tab

### 11.5 Contador de Alertas No Leídas

**Lógica:**
```python
unread_count = await db.alerts.count_documents({
    "user_id": user_id,
    "read": False
})
```

**Visualización:**
- Badge rojo en tab "Alertas"
- Número visible desde cualquier tab
- Se actualiza al marcar como leída

---

## 12. SISTEMA DE CHAT

### 12.1 Arquitectura

**Colección:** `messages`

**Tipo:** Chat bidireccional 1-a-1 (Usuario ↔ Admin)

### 12.2 Componente

**Frontend:** `<ChatBox />`

**Usado en:**
- UserDashboard → Tab Chat
- AdminDashboard → Modal "Ver Chat" al seleccionar cliente

### 12.3 Enviar Mensaje

**Usuario:**
```javascript
POST /api/messages
{
  user_id: "user_id",
  content: "Mensaje del usuario"
}
```

**Admin:**
```javascript
POST /api/messages
{
  user_id: "user_id_del_cliente",
  content: "Respuesta del admin"
}
```

**Backend registra automáticamente:**
- `sender_id`: ID de quien envía
- `sender_role`: "user" o "admin"
- `timestamp`: Fecha/hora actual
- `read: false`

### 12.4 Obtener Mensajes

**Endpoint:** `GET /api/messages?user_id={user_id}`

**Retorna:**
- Todos los mensajes de esa conversación
- Ordenados por timestamp (más antiguos primero)

### 12.5 Visualización

**Diseño:**
- Mensajes propios: Derecha, fondo azul
- Mensajes del otro: Izquierda, fondo gris
- Nombre del sender + timestamp
- Scroll automático al último mensaje

### 12.6 Actualización en Tiempo Real

**Método actual:** Polling

```javascript
useEffect(() => {
  const interval = setInterval(() => {
    loadMessages();
  }, 5000); // Cada 5 segundos
  
  return () => clearInterval(interval);
}, []);
```

**Mejora futura:** Socket.IO (ya importado en backend, no implementado)

---

## 13. GESTIÓN DE DOCUMENTOS

### 13.1 Arquitectura

**Colección:** `pdfs`

**Storage:** Sistema de archivos en `/app/backend/uploads/`

### 13.2 Subir PDF (Admin)

**Flujo:**
1. Admin selecciona cliente
2. Click "Subir PDF"
3. Modal con formulario:
   - Título del documento
   - Archivo (input file)
4. **Endpoint:** `POST /api/admin/pdfs/upload`
5. Archivo se guarda en `/app/backend/uploads/`
6. Registro en BD con:
   - `user_id`
   - `title`
   - `file_path`
   - `url: /api/pdfs/download/{pdf_id}`
   - `uploaded_by: admin_id`

**Validaciones:**
- Tipo de archivo: PDF, imagen, etc.
- Tamaño máximo: Configurable (default 10MB)

### 13.3 Ver PDFs (Usuario)

**UserDashboard → Tab Documentos**

1. Lista de todos los PDFs del usuario
2. Tabla con:
   - Título
   - Fecha de subida
   - Botón "Descargar"

### 13.4 Descargar PDF

**Endpoint:** `GET /api/pdfs/download/{pdf_id}`

**Seguridad:**
```python
# Verificar que el usuario es dueño del PDF
pdf = await db.pdfs.find_one({"_id": pdf_id})
if pdf["user_id"] != current_user["_id"]:
    raise HTTPException(403, "Access denied")
```

**Response:**
- Stream del archivo
- Headers correctos para descarga:
  - `Content-Type: application/pdf`
  - `Content-Disposition: attachment; filename="..."`

### 13.5 Eliminar PDF (Admin)

**Endpoint:** `DELETE /api/pdfs/{pdf_id}`

**Flujo:**
1. Elimina archivo físico del servidor
2. Elimina registro de BD

---

## 14. SISTEMA DE CUESTIONARIOS

### 14.1 Cuestionario Diagnóstico

**Ubicación:** Landing Page (on-page)

**Componente:** `<DiagnosisQuestionnaire />`

### 14.2 Campos del Formulario

1. **Nombre** (text, required)
2. **Email** (email, required)
3. **Teléfono** (tel, required)
4. **Objetivo** (select)
   - Perder peso
   - Ganar masa muscular
   - Mantenimiento
   - Mejorar rendimiento
5. **Experiencia** (select)
   - Ninguna
   - Básica
   - Intermedia
   - Avanzada
6. **Restricciones Alimentarias** (textarea, opcional)
7. **Disponibilidad Horaria** (textarea)
8. **Presupuesto** (text)

### 14.3 Envío del Formulario

**Endpoint:** `POST /api/questionnaire/submit`

**Flujo:**
1. Valida datos
2. Crea registro en `questionnaire_responses`
3. Envía email al admin con todos los datos
4. Muestra mensaje de confirmación al usuario

**Email al Admin:**
- Asunto: "Nuevo prospecto: [Nombre]"
- Contenido: Todas las respuestas del cuestionario
- Link directo al CRM de Prospectos

### 14.4 Gestión de Respuestas

**Ver:** AdminDashboard → CRM Prospectos

**Acciones:**
- Ver detalles completos
- Contactar (WhatsApp/Email)
- Agregar notas
- Convertir a cliente
- Rechazar
- Eliminar

---

## 15. PWA (PROGRESSIVE WEB APP)

### 15.1 Configuración

**Archivos clave:**
- `/app/frontend/public/manifest.json`
- `/app/frontend/public/service-worker.js`
- `/app/frontend/public/icon.svg`

### 15.2 Manifest.json

```json
{
  "short_name": "ECJ Trainer",
  "name": "ECJ Trainer - Entrenamiento Personal",
  "description": "Gestión de entrenamiento y nutrición personalizada",
  "icons": [
    {
      "src": "/icon-192.png",
      "type": "image/png",
      "sizes": "192x192",
      "purpose": "any maskable"
    },
    {
      "src": "/icon-512.png",
      "type": "image/png",
      "sizes": "512x512",
      "purpose": "any maskable"
    }
  ],
  "start_url": "/",
  "display": "standalone",
  "theme_color": "#f97316",
  "background_color": "#ffffff",
  "orientation": "portrait-primary"
}
```

### 15.3 Service Worker

**Funcionalidad:**
- Cache de archivos estáticos
- Funcionamiento offline
- Actualización automática de caché

**Versionado:**
```javascript
const CACHE_NAME = 'ecj-trainer-v2';
```

**Estrategia de caché:**
- Cache First: Archivos estáticos
- Network First: Datos dinámicos

### 15.4 Instalación

**iOS (Safari):**
1. Abrir en Safari
2. Compartir → "Agregar a pantalla de inicio"
3. Confirmar

**Android (Chrome):**
1. Abrir en Chrome
2. Banner automático: "Agregar a pantalla de inicio"
3. O menú (⋮) → "Instalar app"
4. Confirmar

### 15.5 Características PWA

✅ **Instalable** - Icono en pantalla de inicio  
✅ **Standalone** - Sin barra del navegador  
✅ **Offline** - Funciona sin conexión (limitado)  
✅ **Actualizaciones automáticas** - Sin ir a tienda  
✅ **Responsive** - Adaptado a móvil  
✅ **Fast** - Caché local  

### 15.6 Meta Tags

```html
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="ECJ Trainer" />
<meta name="mobile-web-app-capable" content="yes" />
<meta name="theme-color" content="#f97316" />
```

---

## 16. EMAILS AUTOMATIZADOS

### 16.1 Configuración SMTP

**Archivo:** `/app/backend/.env`

```bash
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="tu_email@gmail.com"
SMTP_PASSWORD="tu_app_password"
SMTP_FROM="ECJ Trainer <tu_email@gmail.com>"
```

### 16.2 Módulo de Emails

**Archivo:** `/app/backend/email_utils.py`

**Funciones disponibles:**

#### 16.2.1 Sesiones

```python
send_session_created_email(user_email, user_name, session_date, session_title)
send_admin_session_created_email(client_name, client_email, session_date, session_title)
send_session_rescheduled_email(user_email, user_name, new_date, session_title)
send_admin_session_rescheduled_email(client_name, client_email, old_date, new_date, session_title)
send_admin_session_cancelled_email(client_name, client_email, session_date, session_title)
```

#### 16.2.2 Cuestionario

```python
send_questionnaire_admin_email(questionnaire_data)
```

#### 16.2.3 Templates

```python
send_template_email(to_email, subject, content)
```

### 16.3 Triggers de Emails

**Sesiones:**
- Admin crea sesión → Email a cliente
- Cliente reagenda → Email a admin
- Admin reagenda → Email a cliente
- Cliente cancela → Email a admin

**Cuestionario:**
- Usuario envía → Email a admin

**Templates:**
- Admin usa template de email → Email a cliente

---

## 17. APIS Y ENDPOINTS

### 17.1 Autenticación

#### POST /api/auth/register
**Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
**Response:** Usuario + token

#### POST /api/auth/login
**Body:**
```json
{
  "email": "string",
  "password": "string"
}
```
**Response:** Usuario + token

#### POST /api/auth/logout
**Headers:** Authorization Bearer token  
**Response:** Success

---

### 17.2 Usuarios

#### GET /api/users/me
**Headers:** Authorization  
**Response:** Datos del usuario actual

#### PATCH /api/users/me
**Headers:** Authorization  
**Body:**
```json
{
  "name": "string",
  "whatsapp": "string",
  "password": "string"
}
```
**Response:** Usuario actualizado

#### GET /api/users/dashboard
**Headers:** Authorization  
**Response:**
```json
{
  "user": {...},
  "forms": [...],
  "pdfs": [...],
  "alerts": [...],
  "sessions": [...]
}
```

---

### 17.3 Administración de Usuarios

#### GET /api/admin/users
**Headers:** Authorization (Admin)  
**Query:** ?search=string&status=active  
**Response:** Lista de usuarios

#### PATCH /api/admin/users/{user_id}
**Headers:** Authorization (Admin)  
**Body:**
```json
{
  "name": "string",
  "email": "string",
  "subscription_status": "active",
  "subscription_plan": "team",
  "payment_status": "verified"
}
```
**Response:** Usuario actualizado

#### DELETE /api/admin/delete-client/{user_id}
**Headers:** Authorization (Admin)  
**Response:** Success (soft delete)

---

### 17.4 Sesiones

#### POST /api/sessions/create
**Headers:** Authorization (Admin)  
**Body:**
```json
{
  "user_id": "string",
  "title": "string",
  "date": "ISO8601",
  "time": "HH:MM:SS",
  "notes": "string"
}
```
**Response:** Sesión creada

#### GET /api/sessions
**Headers:** Authorization  
**Query:** ?user_id=string  
**Response:** Lista de sesiones

#### PATCH /api/sessions/{session_id}/reschedule
**Headers:** Authorization  
**Body:**
```json
{
  "date": "ISO8601",
  "time": "HH:MM:SS"
}
```
**Response:** Sesión actualizada

#### DELETE /api/sessions/{session_id}
**Headers:** Authorization  
**Response:** Success

---

### 17.5 PDFs

#### POST /api/admin/pdfs/upload
**Headers:** Authorization (Admin)  
**Body:** multipart/form-data
- user_id: string
- title: string
- file: file

**Response:** PDF creado

#### GET /api/pdfs
**Headers:** Authorization  
**Query:** ?user_id=string  
**Response:** Lista de PDFs

#### GET /api/pdfs/download/{pdf_id}
**Headers:** Authorization  
**Response:** Stream del archivo

#### DELETE /api/pdfs/{pdf_id}
**Headers:** Authorization (Admin)  
**Response:** Success

---

### 17.6 Alertas

#### POST /api/alerts
**Headers:** Authorization (Admin)  
**Body:**
```json
{
  "user_id": "string",
  "title": "string",
  "message": "string",
  "type": "info"
}
```
**Response:** Alerta creada

#### GET /api/alerts
**Headers:** Authorization  
**Query:** ?user_id=string  
**Response:** Lista de alertas

#### PATCH /api/alerts/{alert_id}/read
**Headers:** Authorization  
**Response:** Alerta marcada como leída

---

### 17.7 Chat

#### POST /api/messages
**Headers:** Authorization  
**Body:**
```json
{
  "user_id": "string",
  "content": "string"
}
```
**Response:** Mensaje creado

#### GET /api/messages
**Headers:** Authorization  
**Query:** ?user_id=string  
**Response:** Lista de mensajes

---

### 17.8 Templates

#### GET /api/admin/templates
**Headers:** Authorization (Admin)  
**Query:** ?type=whatsapp&tag=tag_name  
**Response:** Lista de templates

#### POST /api/admin/templates
**Headers:** Authorization (Admin)  
**Body:**
```json
{
  "type": "whatsapp",
  "name": "string",
  "subject": "string",
  "content": "string",
  "tags": ["tag1", "tag2"]
}
```
**Response:** Template creado

#### PATCH /api/admin/templates/{template_id}
**Headers:** Authorization (Admin)  
**Body:** Campos a actualizar  
**Response:** Template actualizado

#### DELETE /api/admin/templates/{template_id}
**Headers:** Authorization (Admin)  
**Response:** Success

#### GET /api/admin/templates/tags/all
**Headers:** Authorization (Admin)  
**Response:**
```json
{
  "tags": ["tag1", "tag2", "tag3"]
}
```

#### POST /api/admin/templates/tags
**Headers:** Authorization (Admin)  
**Body:**
```json
{
  "tag_name": "string"
}
```
**Response:** Tag creado

#### DELETE /api/admin/templates/tags/{tag_name}
**Headers:** Authorization (Admin)  
**Response:** Success (con validación de uso)

---

### 17.9 CRM

#### GET /api/admin/team-clients
**Headers:** Authorization (Admin)  
**Response:** Lista de clientes del equipo (users)

#### GET /api/admin/team-clients/{client_id}
**Headers:** Authorization (Admin)  
**Response:** Detalles completos del cliente

#### PATCH /api/admin/team-clients/{client_id}/status
**Headers:** Authorization (Admin)  
**Body:**
```json
{
  "status": "active"
}
```
**Response:** Success

---

#### GET /api/admin/external-clients
**Headers:** Authorization (Admin)  
**Response:** Lista de clientes externos

#### POST /api/admin/external-clients
**Headers:** Authorization (Admin)  
**Body:**
```json
{
  "nombre": "string",
  "email": "string",
  "whatsapp": "string",
  "objetivo": "string",
  "plan_weeks": 12,
  "start_date": "ISO8601"
}
```
**Response:** Cliente externo creado

#### PATCH /api/admin/external-clients/{client_id}
**Headers:** Authorization (Admin)  
**Body:** Campos a actualizar  
**Response:** Cliente actualizado

#### DELETE /api/admin/external-clients/{client_id}
**Headers:** Authorization (Admin)  
**Response:** Success

---

#### GET /api/questionnaire/responses
**Headers:** Authorization (Admin)  
**Response:** Lista de respuestas del cuestionario

#### POST /api/questionnaire/submit
**Body:**
```json
{
  "nombre": "string",
  "email": "string",
  "telefono": "string",
  "objetivo": "string",
  "experiencia": "string",
  "restricciones": "string",
  "disponibilidad": "string",
  "presupuesto": "string"
}
```
**Response:** Success + email al admin

---

## 18. VARIABLES DE ENTORNO

### 18.1 Backend (.env)

```bash
# Base de datos
DB_NAME="test_database"
MONGO_URL="mongodb://localhost:27017"

# JWT
SECRET_KEY="tu_secret_key_super_segura"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=10080

# SMTP
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="tu_email@gmail.com"
SMTP_PASSWORD="tu_app_password"
SMTP_FROM="ECJ Trainer <tu_email@gmail.com>"

# Admin por defecto
ADMIN_EMAIL="ecjtrainer@gmail.com"
ADMIN_PASSWORD="tu_password_hasheado"
```

### 18.2 Frontend (.env)

```bash
# Backend URL
REACT_APP_BACKEND_URL="https://tu-dominio.com"

# O en desarrollo
REACT_APP_BACKEND_URL="http://localhost:8001"
```

**IMPORTANTE:** NUNCA hardcodear URLs en el código

---

## 19. DEPLOYMENT

### 19.1 Requisitos

**Backend:**
- Python 3.10+
- MongoDB 5.0+
- Supervisor (gestor de procesos)

**Frontend:**
- Node.js 18+
- Yarn

### 19.2 Instalación Backend

```bash
cd /app/backend
pip install -r requirements.txt
```

### 19.3 Instalación Frontend

```bash
cd /app/frontend
yarn install
yarn build
```

### 19.4 Configuración Supervisor

**Backend:**
```ini
[program:backend]
command=uvicorn server:app --host 0.0.0.0 --port 8001
directory=/app/backend
autostart=true
autorestart=true
```

**Frontend:**
```ini
[program:frontend]
command=serve -s build -l 3000
directory=/app/frontend
autostart=true
autorestart=true
```

### 19.5 Nginx

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    location /api/ {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
    }
}
```

### 19.6 Comandos Útiles

```bash
# Reiniciar servicios
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart all

# Ver logs
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log

# Estado
sudo supervisorctl status
```

### 19.7 Build PWA

```bash
cd /app/frontend
rm -rf build/ node_modules/.cache/
yarn build
sudo supervisorctl restart frontend
```

---

## 20. FLUJOS COMPLETOS

### 20.1 Flujo: Nuevo Cliente (Registro Web)

1. Usuario ve landing page
2. Click "Quiero este plan"
3. Formulario de registro (email, username, password)
4. POST /api/auth/register
5. Usuario creado en BD:
   - role: "user"
   - status: "active"
   - subscription.status: "pending"
   - subscription.payment_status: "pending"
6. Login automático
7. Redirect a UserDashboard
8. Ve alerta de "Pago pendiente"
9. Admin ve nuevo cliente en CRM
10. Admin verifica pago → Cambia payment_status a "verified"
11. Usuario ve estado actualizado

---

### 20.2 Flujo: Prospecto → Cliente

1. Usuario llena cuestionario en landing
2. POST /api/questionnaire/submit
3. Registro en `questionnaire_responses`
4. Email automático al admin
5. Admin abre CRM Prospectos
6. Ve nuevo prospecto, status "pending"
7. Admin contacta por WhatsApp/Email
8. Admin marca "contacted"
9. Admin decide convertir:
   - **Opción A:** Cliente Externo
     - Crea en ExternalClientsCRM
     - Marca prospecto como "converted"
   - **Opción B:** Cliente del Equipo
     - Invita a registrarse en web
     - Usuario sigue flujo 20.1
     - Marca prospecto como "converted"

---

### 20.3 Flujo: Admin Crea Sesión para Cliente

1. Admin abre Gestión de Clientes Activos
2. Selecciona cliente
3. Click "Nueva Sesión"
4. Llena formulario (fecha, hora, título)
5. POST /api/sessions/create
6. Sesión guardada en BD
7. Email automático SOLO al cliente
8. Cliente ve sesión en su calendario
9. Cliente recibe notificación

---

### 20.4 Flujo: Cliente Reagenda Sesión

1. Cliente abre UserDashboard → Calendario
2. Click en sesión
3. Modal con detalles
4. Botón "Reagendar"
5. Selecciona nueva fecha
6. PATCH /api/sessions/{id}/reschedule
7. Sesión actualizada en BD
8. Email automático SOLO al admin
9. Admin ve cambio en calendario
10. Admin confirma o contacta al cliente

---

### 20.5 Flujo: Admin Usa Template

1. Admin abre Gestión de Clientes
2. Selecciona cliente
3. Click "Templates"
4. Modal con lista de templates
5. Filtro por etiqueta (opcional)
6. Selecciona template
7. Vista previa con variables reemplazadas
8. Admin elige método de envío:
   - **WhatsApp:** Abre wa.me con mensaje
   - **Email:** POST /api/emails/send-template
   - **Alerta:** POST /api/alerts
   - **Chat:** POST /api/messages
9. Cliente recibe comunicación
10. Historial registrado en BD

---

### 20.6 Flujo: Usuario Borra y Bloquea

1. Admin abre Gestión de Clientes
2. Selecciona usuario a eliminar
3. Click "Eliminar"
4. Confirmación
5. DELETE /api/admin/delete-client/{user_id}
6. Backend:
   - Marca `status: "deleted"` en `users`
   - Agrega email a `deleted_users`
   - Elimina datos relacionados (PDFs físicos, sesiones, alertas)
7. Usuario desaparece de todas las listas de CRM
8. Si usuario intenta login:
   - Backend verifica `status == "deleted"`
   - Retorna error 403: "Cuenta desactivada"
9. Usuario bloqueado permanentemente

---

## 21. NOTAS FINALES

### 21.1 Optimizaciones para Móvil

- Tabs: 3 columnas en móvil, 6 en desktop
- Padding reducido en móvil
- Texto más pequeño (text-xs vs text-sm)
- Botones adaptados al tamaño de pantalla
- Header responsive con información oculta en móvil

### 21.2 Buenas Prácticas

- **UUIDs:** No usar ObjectId de MongoDB, usar timestamps como IDs
- **Soft Delete:** Siempre marcar como deleted, nunca borrar
- **Validación:** Pydantic en backend, validación nativa en frontend
- **Seguridad:** JWT, bcrypt, validación de permisos
- **Notificaciones:** Email solo al destinatario necesario
- **Sincronización:** Datos dinámicos, no hardcoded

### 21.3 Limitaciones Conocidas

- Chat no es en tiempo real (usa polling)
- No hay notificaciones push
- Sistema de automatizaciones no está completamente implementado
- No hay sistema de pagos integrado (manual)

### 21.4 Mejoras Futuras

1. Socket.IO para chat en tiempo real
2. Notificaciones push (PWA)
3. Sistema de pagos con Stripe
4. Automatizaciones completas (recordatorios, renovaciones)
5. Dashboard analytics para admin
6. Exportación de datos
7. Multi-idioma

---

**FIN DE LA DOCUMENTACIÓN**

---

**Versión:** 1.0  
**Última actualización:** Octubre 2025  
**Autor:** Documentación generada para replicación del sistema

**Contacto para dudas:** [Incluir información de contacto]
