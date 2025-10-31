# 🚀 Jorge Calcerrada Trainer Platform - Guía Completa para Desarrollador

## 📋 Índice
1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Instalación y Configuración](#instalación-y-configuración)
5. [Variables de Entorno](#variables-de-entorno)
6. [Base de Datos](#base-de-datos)
7. [Endpoints API](#endpoints-api)
8. [Despliegue](#despliegue)
9. [Documentación Adicional](#documentación-adicional)

---

## 📖 Descripción del Proyecto

**Jorge Calcerrada Trainer Platform** es una aplicación web full-stack para gestión de clientes de entrenamiento personal. Incluye:

- 🏠 **Landing Page** corporativa con información de servicios
- 👤 **Dashboard de Usuario** con calendario, PDFs, alertas y chat
- 🛡️ **Dashboard de Administrador** con CRM completo, gestión de clientes, plantillas de comunicación y más
- 📧 **Sistema de notificaciones** por email
- 📱 **PWA** instalable en dispositivos móviles
- 🔐 **Autenticación JWT** con roles (admin/user)

**Idioma:** 100% en Español

---

## 🛠️ Stack Tecnológico

### Frontend
- **Framework:** React 18.x
- **Router:** React Router DOM v6
- **Estilos:** Tailwind CSS + Shadcn/UI
- **Iconos:** Lucide React
- **HTTP Client:** Axios
- **PWA:** Service Worker + Manifest

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Base de Datos:** MongoDB
- **Autenticación:** JWT (python-jose)
- **Passwords:** bcrypt
- **Email:** smtplib (Gmail SMTP)
- **CORS:** FastAPI middleware

### Infraestructura (Producción en Emergent)
- **Frontend:** Puerto 3000
- **Backend:** Puerto 8001 (con prefijo /api)
- **MongoDB:** Puerto 27017
- **Servidor:** Nginx + Supervisor

---

## 📁 Estructura del Proyecto

```
/app
├── backend/
│   ├── server.py           # API principal FastAPI
│   ├── auth.py             # Lógica de autenticación JWT
│   ├── email_utils.py      # Utilidades de email (SMTP)
│   ├── models.py           # Modelos Pydantic
│   ├── requirements.txt    # Dependencias Python
│   └── .env                # Variables de entorno backend
│
├── frontend/
│   ├── public/
│   │   ├── index.html
│   │   ├── manifest.json   # PWA manifest
│   │   ├── service-worker.js
│   │   └── ecj_icon.svg    # Logo
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   │   ├── ui/         # Shadcn UI components
│   │   │   ├── AdminComponents.jsx
│   │   │   ├── Calendar.jsx
│   │   │   ├── ChatBox.jsx
│   │   │   ├── ProspectsCRM.jsx
│   │   │   ├── TeamClientsCRM.jsx
│   │   │   ├── ExternalClientsCRM.jsx
│   │   │   ├── TemplatesManager.jsx
│   │   │   └── ...
│   │   ├── pages/
│   │   │   ├── LandingPage.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── UserDashboard.jsx
│   │   │   ├── AdminDashboard.jsx
│   │   │   └── ResetPassword.jsx
│   │   ├── App.js          # Componente principal
│   │   ├── App.css         # Estilos globales
│   │   ├── AuthContext.jsx # Context de autenticación
│   │   └── index.js        # Entry point
│   ├── package.json
│   └── .env                # Variables de entorno frontend
│
├── database_export/        # ✅ EXPORTACIÓN DE DATOS
│   ├── users.json
│   ├── prospects.json
│   ├── team_clients.json
│   ├── external_clients.json
│   ├── sessions.json
│   ├── pdfs.json
│   ├── alerts.json
│   ├── templates.json
│   └── tags.json
│
├── DOCUMENTACION_COMPLETA.md  # 📚 Documentación técnica detallada
├── GUIA_DISENO.md             # 🎨 Guía de diseño y colores
├── README_DEVELOPER.md        # 📖 Este archivo
└── database_init.sh           # 🔧 Script de inicialización DB
```

---

## ⚙️ Instalación y Configuración

### Requisitos Previos

```bash
# Versiones necesarias
Python 3.11+
Node.js 18+
MongoDB 6.0+
yarn o npm
```

### Paso 1: Clonar el Repositorio

```bash
git clone <tu-repositorio-github>
cd <nombre-proyecto>
```

### Paso 2: Configurar Backend

```bash
cd backend

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar y configurar .env
cp .env.example .env
# Editar .env con tus credenciales (ver sección Variables de Entorno)
```

### Paso 3: Configurar Frontend

```bash
cd frontend

# Instalar dependencias (usar yarn preferiblemente)
yarn install
# o
npm install

# Copiar y configurar .env
cp .env.example .env
# Editar REACT_APP_BACKEND_URL con tu URL de backend
```

### Paso 4: Inicializar Base de Datos

```bash
# Asegúrate de que MongoDB esté corriendo
sudo systemctl start mongodb
# o
mongod

# Importar datos iniciales
cd /app
bash database_init.sh
```

### Paso 5: Ejecutar la Aplicación

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
yarn start
# o
npm start
```

**Acceso:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8001
- API Docs: http://localhost:8001/docs

---

## 🔐 Variables de Entorno

### Backend (.env)

```bash
# MongoDB
MONGO_URL="mongodb://localhost:27017"
DB_NAME="ecj_trainer"

# JWT
JWT_SECRET_KEY="tu-super-secreto-jwt-key-cambiar-en-produccion"

# CORS
CORS_ORIGINS="http://localhost:3000,https://tu-dominio.com"

# Gmail SMTP para emails
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="ecjtrainer@gmail.com"
SMTP_PASSWORD="nxsv tzay tskg jikb"  # App password de Gmail
SMTP_FROM_NAME="Jorge Calcerrada"

# Frontend URL (para links en emails)
FRONTEND_URL="http://localhost:3000"
```

### Frontend (.env)

```bash
# Backend URL (¡IMPORTANTE! Incluir /api al final en producción)
REACT_APP_BACKEND_URL="http://localhost:8001"

# Otras configuraciones
WDS_SOCKET_PORT=443  # Solo para producción con SSL
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

### 🔑 Credenciales Actuales (Gmail SMTP)

**Email:** ecjtrainer@gmail.com  
**App Password:** nxsv tzay tskg jikb  
**Nombre:** Jorge Calcerrada

**⚠️ IMPORTANTE:** Esta es una App Password de Gmail, NO la contraseña de la cuenta. Para generar una nueva:
1. Ir a cuenta Google → Seguridad
2. Activar verificación en 2 pasos
3. Generar "Contraseña de aplicación"
4. Usar esa contraseña en SMTP_PASSWORD

---

## 💾 Base de Datos

### Colecciones de MongoDB

```javascript
// Base de datos: ecj_trainer

// 1. users - Usuarios del sistema (admins y clientes)
{
  id: String (UUID),
  email: String (único),
  username: String (único),
  password: String (hash bcrypt),
  full_name: String,
  role: String ("admin" | "user"),
  subscription: {
    plan: String,
    status: String,
    start_date: Date,
    renewal_date: Date
  },
  payment_status: String ("pending" | "verified"),
  created_at: Date,
  is_deleted: Boolean
}

// 2. prospects - Prospectos del CRM
{
  id: String (UUID),
  name: String,
  email: String,
  phone: String,
  status: String ("new" | "contacted" | "qualified" | "lost"),
  source: String,
  notes: String,
  created_at: Date
}

// 3. team_clients - Clientes registrados desde la web
{
  id: String (UUID),
  email: String,
  full_name: String,
  subscription: Object,
  payment_status: String,
  created_at: Date
}

// 4. external_clients - Clientes externos agregados manualmente
{
  id: String (UUID),
  name: String,
  email: String,
  phone: String,
  status: String ("active" | "inactive"),
  notes: String,
  created_at: Date
}

// 5. sessions - Sesiones/citas agendadas
{
  id: String (UUID),
  user_id: String,
  title: String,
  date: String (ISO date),
  time: String (HH:MM:SS),
  description: String,
  created_at: Date
}

// 6. pdfs - Documentos PDF
{
  id: String (UUID),
  user_id: String ("all" para todos los usuarios),
  title: String,
  type: String ("training" | "nutrition"),
  url: String,
  created_at: Date
}

// 7. alerts - Alertas/notificaciones
{
  id: String (UUID),
  user_id: String ("all" para broadcast),
  title: String,
  message: String,
  link: String (opcional),
  read: Boolean,
  created_at: Date
}

// 8. templates - Plantillas de comunicación
{
  id: String (UUID),
  client_id: String ("global" para plantillas globales),
  name: String,
  content: String,
  tags: Array<String>,
  created_at: Date
}

// 9. tags - Etiquetas globales para templates
{
  id: String (UUID),
  name: String,
  created_at: Date
}
```

### Importar Datos Exportados

```bash
# Importar todos los datos
cd /app/database_export

for collection in users prospects team_clients external_clients sessions pdfs alerts templates tags; do
  mongoimport --uri="mongodb://localhost:27017/ecj_trainer" \
    --collection=$collection \
    --file=$collection.json \
    --jsonArray
done
```

### Usuario Admin por Defecto

**Email:** admin@ecjtrainer.com  
**Password:** admin123  
**Role:** admin

---

## 🔌 Endpoints API

Ver documentación completa en:
- **Swagger UI:** http://localhost:8001/docs
- **Documentación detallada:** `/app/DOCUMENTACION_COMPLETA.md`

### Principales Endpoints

```
Autenticación:
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/reset-password-request
POST   /api/auth/reset-password

Usuarios (requiere autenticación):
GET    /api/users/me
PATCH  /api/users/me

Admin - Usuarios:
GET    /api/admin/users
GET    /api/admin/users/{user_id}
PATCH  /api/admin/users/{user_id}
DELETE /api/admin/users/{user_id}
POST   /api/admin/users/{user_id}/send-password-reset

Admin - CRM:
GET    /api/admin/prospects
POST   /api/admin/prospects
PATCH  /api/admin/prospects/{prospect_id}
DELETE /api/admin/prospects/{prospect_id}
POST   /api/admin/prospects/{prospect_id}/convert
POST   /api/admin/prospects/{prospect_id}/move-to-external

Admin - Sesiones:
GET    /api/admin/sessions
POST   /api/admin/sessions
GET    /api/admin/sessions/{session_id}
PATCH  /api/admin/sessions/{session_id}
DELETE /api/admin/sessions/{session_id}

PDFs:
GET    /api/pdfs/user
POST   /api/admin/pdfs
DELETE /api/admin/pdfs/{pdf_id}

Alertas:
GET    /api/alerts
POST   /api/admin/alerts
PATCH  /api/alerts/{alert_id}/read

Plantillas:
GET    /api/admin/templates
POST   /api/admin/templates
GET    /api/admin/templates/{template_id}
PATCH  /api/admin/templates/{template_id}
DELETE /api/admin/templates/{template_id}
GET    /api/admin/templates/tags/all
POST   /api/admin/templates/tags

Documentación:
GET    /api/admin/download-documentation
```

**⚠️ Importante:** Todos los endpoints protegidos requieren header:
```
Authorization: Bearer <jwt_token>
```

---

## 🚀 Despliegue

### Opción 1: Servidor Propio (VPS)

#### 1. Preparar Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
sudo apt install -y python3 python3-pip python3-venv nodejs npm mongodb nginx supervisor

# Instalar yarn
sudo npm install -g yarn
```

#### 2. Clonar y Configurar

```bash
# Clonar proyecto
cd /var/www
sudo git clone <tu-repo> ecj-trainer
cd ecj-trainer

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Configurar .env

# Frontend
cd ../frontend
yarn install
# Configurar .env
yarn build
```

#### 3. Configurar Supervisor

```bash
sudo nano /etc/supervisor/conf.d/ecj-backend.conf
```

```ini
[program:ecj-backend]
command=/var/www/ecj-trainer/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001
directory=/var/www/ecj-trainer/backend
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/ecj-backend.err.log
stdout_logfile=/var/log/supervisor/ecj-backend.out.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start ecj-backend
```

#### 4. Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/ecj-trainer
```

```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    # Frontend (React build)
    location / {
        root /var/www/ecj-trainer/frontend/build;
        try_files $uri /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ecj-trainer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 5. SSL con Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tu-dominio.com
```

### Opción 2: Docker (Recomendado)

```dockerfile
# Próximamente: Dockerfile y docker-compose.yml
```

### Opción 3: Vercel + MongoDB Atlas

**Frontend (Vercel):**
```bash
cd frontend
vercel deploy --prod
```

**Backend (Railway/Render/Fly.io):**
- Configurar variables de entorno
- Deploy desde GitHub

**Base de Datos (MongoDB Atlas):**
- Crear cluster gratuito
- Actualizar MONGO_URL en .env

---

## 📚 Documentación Adicional

### Archivos de Documentación

1. **DOCUMENTACION_COMPLETA.md** - Documentación técnica exhaustiva:
   - Arquitectura del sistema
   - Todos los endpoints con ejemplos
   - Flujos de autenticación
   - Modelos de datos
   - Casos de uso

2. **GUIA_DISENO.md** - Guía de diseño visual:
   - Paleta de colores corporativos
   - Tipografía
   - Componentes UI
   - Animaciones
   - Responsive design

3. **database_export/** - Datos exportados en JSON

### Testing

```bash
# Backend (pytest - próximamente)
cd backend
pytest

# Frontend (jest - próximamente)
cd frontend
yarn test
```

---

## 🐛 Solución de Problemas Comunes

### Backend no inicia

```bash
# Verificar logs
tail -f /var/log/supervisor/backend.err.log

# Verificar puerto
sudo lsof -i :8001

# Reiniciar
sudo supervisorctl restart backend
```

### Frontend no conecta al backend

```bash
# Verificar REACT_APP_BACKEND_URL en .env
cat frontend/.env

# Verificar CORS en backend
# Asegúrate de que CORS_ORIGINS incluya tu dominio frontend
```

### MongoDB connection failed

```bash
# Verificar que MongoDB esté corriendo
sudo systemctl status mongodb

# Iniciar MongoDB
sudo systemctl start mongodb

# Verificar MONGO_URL
echo $MONGO_URL
```

### Email no se envía

```bash
# Verificar credenciales SMTP en .env
# Verificar que SMTP_PASSWORD sea una "App Password" de Gmail
# Verificar logs del backend para errores SMTP
```

---

## 📞 Contacto

**Cliente:** Jorge Calcerrada  
**Email:** ecjtrainer@gmail.com

**Proyecto originalmente desarrollado en:** Emergent Agent Platform

---

## 📝 Notas Importantes

1. **Prefijo /api:** Todos los endpoints del backend DEBEN tener el prefijo `/api` en producción para que funcione con Nginx/ingress

2. **JWT Secret:** CAMBIAR `JWT_SECRET_KEY` en producción por algo seguro

3. **CORS:** Configurar `CORS_ORIGINS` correctamente para tu dominio en producción

4. **MongoDB:** Usar MongoDB Atlas o servidor dedicado en producción (no localhost)

5. **SMTP:** La App Password actual es válida pero considera crear una nueva para producción

6. **PWA:** Asegúrate de servir la app con HTTPS para que funcione la instalación PWA

7. **Service Worker:** Actualizar el cache version en `service-worker.js` cada deploy

---

## ✅ Checklist de Deployment

- [ ] Configurar variables de entorno de producción
- [ ] Cambiar JWT_SECRET_KEY
- [ ] Configurar CORS con dominios correctos
- [ ] Migrar a MongoDB Atlas o servidor dedicado
- [ ] Build del frontend (`yarn build`)
- [ ] Configurar Nginx/servidor web
- [ ] Configurar SSL (HTTPS)
- [ ] Importar datos iniciales
- [ ] Crear usuario admin
- [ ] Probar todos los flujos principales
- [ ] Configurar backups de base de datos
- [ ] Configurar monitoring/logs

---

**¡Listo para desarrollar! 🎉**

Si tienes dudas, consulta `DOCUMENTACION_COMPLETA.md` o revisa el código existente.