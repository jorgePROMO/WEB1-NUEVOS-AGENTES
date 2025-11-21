# 🔐 Credenciales y Configuración del Sistema

## Base de Datos MongoDB

**URI de Conexión:**
```
mongodb://localhost:27017
```

**Base de Datos:**
```
ecj_trainer
```

**Colecciones:**
- users
- prospects
- team_clients
- external_clients
- sessions
- pdfs
- alerts
- templates
- tags

---

## Usuario Administrador

**Email:** `admin@ecjtrainer.com`  
**Password:** `admin123`  
**Rol:** `admin`

**Acceso:**
- Panel de administración completo
- Gestión de usuarios
- CRM completo
- Gestión de plantillas
- Subida de PDFs
- Envío de alertas
- Gestión de sesiones/citas

---

## Configuración SMTP (Email)

**Servicio:** Gmail SMTP  
**Host:** `smtp.gmail.com`  
**Puerto:** `587`  
**Seguridad:** STARTTLS

**Credenciales:**
- **Email:** `ecjtrainer@gmail.com`
- **App Password:** `nxsv tzay tskg jikb`
- **Nombre Remitente:** `Jorge Calcerrada`

### ⚠️ Importante sobre Gmail App Password

Esta NO es la contraseña de la cuenta de Gmail, es una **App Password** (Contraseña de Aplicación).

**Para generar una nueva App Password:**

1. Ir a: https://myaccount.google.com/security
2. Activar "Verificación en 2 pasos" si no está activada
3. Buscar "Contraseñas de aplicaciones" (App Passwords)
4. Seleccionar "Correo" y "Otro" (nombre personalizado)
5. Copiar la contraseña de 16 caracteres generada
6. Usar esa contraseña en `SMTP_PASSWORD`

**Funcionalidades de Email:**
- Notificaciones de sesiones agendadas
- Recuperación de contraseña
- Alertas a usuarios
- Comunicaciones desde plantillas

---

## JWT (JSON Web Token)

**Secret Key Actual:**
```
your-super-secret-jwt-key-change-in-production-12345
```

### ⚠️ CAMBIAR EN PRODUCCIÓN

**Generar una nueva clave segura:**

```bash
# Opción 1: Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Opción 2: OpenSSL
openssl rand -hex 32

# Opción 3: Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

Actualizar en: `/app/backend/.env` → `JWT_SECRET_KEY`

**Configuración JWT:**
- Algoritmo: HS256
- Expiración: 7 días (configurable en `auth.py`)
- Ubicación: Header `Authorization: Bearer <token>`

---

## Variables de Entorno

### Backend (.env)

```bash
# Base de Datos
MONGO_URL="mongodb://localhost:27017"
DB_NAME="ecj_trainer"

# Seguridad
JWT_SECRET_KEY="your-super-secret-jwt-key-change-in-production-12345"
CORS_ORIGINS="*"  # Cambiar en producción a dominios específicos

# Email SMTP
SMTP_HOST="smtp.gmail.com"
SMTP_PORT=587
SMTP_USER="ecjtrainer@gmail.com"
SMTP_PASSWORD="nxsv tzay tskg jikb"
SMTP_FROM_NAME="Jorge Calcerrada"

# Frontend URL (para links en emails)
FRONTEND_URL="https://edn-job-runner.preview.emergentagent.com"
```

### Frontend (.env)

```bash
# Backend API URL
REACT_APP_BACKEND_URL="https://edn-job-runner.preview.emergentagent.com"

# Configuración WebSocket (para desarrollo)
WDS_SOCKET_PORT=443

# Otras configuraciones
REACT_APP_ENABLE_VISUAL_EDITS=false
ENABLE_HEALTH_CHECK=false
```

---

## URLs y Puertos

### Desarrollo Local

**Frontend:**
- URL: http://localhost:3000
- Puerto: 3000

**Backend:**
- URL: http://localhost:8001
- API Docs: http://localhost:8001/docs
- Puerto: 8001

**MongoDB:**
- URL: mongodb://localhost:27017
- Puerto: 27017

### Producción (Emergent)

**Frontend + Backend:**
- URL: https://edn-job-runner.preview.emergentagent.com
- Backend API: https://edn-job-runner.preview.emergentagent.com/api

**Configuración Interna:**
- Frontend: Puerto 3000 (interno)
- Backend: Puerto 8001 (interno, mapeado a /api)
- MongoDB: Puerto 27017 (interno)

---

## CORS (Cross-Origin Resource Sharing)

### Configuración Actual

```python
# backend/server.py
CORS_ORIGINS = "*"  # Permite todos los orígenes
```

### ⚠️ Configuración Recomendada para Producción

```python
CORS_ORIGINS = "https://tu-dominio.com,https://www.tu-dominio.com"
```

O en `.env`:
```bash
CORS_ORIGINS="https://tu-dominio.com,https://www.tu-dominio.com"
```

---

## Archivos de Datos Exportados

**Ubicación:** `/app/database_export/`

**Archivos:**
- `users.json` - 1 usuario (admin)
- `prospects.json` - 0 registros
- `team_clients.json` - 0 registros
- `external_clients.json` - 0 registros
- `sessions.json` - 0 registros
- `pdfs.json` - 0 registros
- `alerts.json` - 0 registros
- `templates.json` - 0 registros
- `tags.json` - 0 registros

**Para importar:**
```bash
bash /app/database_init.sh
```

---

## Servicios de Terceros

### Actualmente NO se usan:
- ❌ AWS S3 / Storage
- ❌ Stripe / PayPal (pagos)
- ❌ Twilio (SMS)
- ❌ Socket.IO (chat en tiempo real - pendiente)
- ❌ Google OAuth (removido)

### Servicios utilizados:
- ✅ Gmail SMTP (emails)
- ✅ MongoDB (base de datos)

---

## Credenciales de Deploy

### GitHub
- Ya conectado por el usuario
- Push con: "Save to GitHub" en la interfaz

### Emergent Platform
- URL del preview: https://edn-job-runner.preview.emergentagent.com
- Control de servicios: `sudo supervisorctl restart all`

---

## Checklist de Seguridad para Producción

- [ ] Cambiar `JWT_SECRET_KEY` por uno aleatorio y seguro
- [ ] Configurar `CORS_ORIGINS` con dominios específicos
- [ ] Generar nueva App Password de Gmail para producción
- [ ] Usar MongoDB Atlas o servidor dedicado (no localhost)
- [ ] Habilitar HTTPS/SSL (requerido para PWA)
- [ ] Cambiar password del usuario admin
- [ ] Configurar rate limiting en API
- [ ] Habilitar logs de auditoría
- [ ] Configurar backups automáticos de MongoDB
- [ ] Revisar permisos de archivos en servidor
- [ ] Configurar firewall (UFW/iptables)
- [ ] Habilitar fail2ban para protección contra brute force

---

## Comandos Útiles

### Ver usuarios en MongoDB
```bash
mongosh mongodb://localhost:27017/ecj_trainer --eval "db.users.find().pretty()"
```

### Crear nuevo usuario admin
```bash
cd /app/backend
python3 -c "
from auth import get_password_hash
import uuid
user_id = str(uuid.uuid4())
print(f'ID: {user_id}')
print(f'Password Hash: {get_password_hash(\"tu-password\")}')
"
```

### Reiniciar servicios
```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
sudo supervisorctl restart all
```

### Ver logs
```bash
tail -f /var/log/supervisor/backend.err.log
tail -f /var/log/supervisor/frontend.err.log
```

---

## Contacto del Cliente

**Nombre:** Jorge Calcerrada  
**Email:** ecjtrainer@gmail.com  
**Aplicación:** Plataforma de entrenamiento personal

---

**NOTA IMPORTANTE:** Este archivo contiene información sensible. NO subir a repositorios públicos. Agregar `CREDENCIALES.md` al `.gitignore`.

```bash
# .gitignore
CREDENCIALES.md
.env
*.env
```