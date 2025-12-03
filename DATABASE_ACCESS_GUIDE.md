# 🗄️ GUÍA DE ACCESO A BASES DE DATOS - EDN360

## 📊 BASES DE DATOS DISPONIBLES

### 1. **test_database** (Base de datos principal)
- **Variable de entorno:** `DB_NAME=test_database`
- **Conexión:** `MONGO_URL` en `/app/backend/.env`

**Colecciones principales:**
- `users` - Usuarios del sistema (5 usuarios)
- `payment_transactions` - Transacciones de pago (5)
- `user_subscriptions` - Suscripciones activas (5)
- `alerts` - Alertas del sistema (2)
- `messages` - Mensajes entre admin y clientes (3)
- `generation_jobs` - Jobs de generación de planes (36)
- `training_plans` - Planes de entrenamiento legacy (0)
- `nutrition_plans` - Planes de nutrición legacy (0)
- `follow_up_submissions` - Seguimientos mensuales (1)
- `nutrition_questionnaire_submissions` - Cuestionarios nutrición (1)

---

### 2. **edn360_app** (Base de datos EDN360)
- **Variable de entorno:** `MONGO_EDN360_APP_DB_NAME=edn360_app`
- **Conexión:** `MONGO_URL` en `/app/backend/.env`

**Colecciones principales:**
- `client_drawers` - Cajones de clientes con cuestionarios (2 cajones)
- `training_plans_v2` - Planes de entrenamiento EDN360 (0 actualmente)
- `edn360_snapshots` - Snapshots de ejecuciones de workflows (64)

**Estructura de client_drawers:**
```json
{
  "_id": "client_{user_id}",
  "user_id": "1764016044644335",
  "shared_questionnaires": [
    {
      "submission_id": "quest_001",
      "questionnaire_type": "initial",
      "submitted_at": "2025-12-02T...",
      "responses": {
        "nombre_completo": "...",
        "peso": 85,
        "altura_cm": 172,
        ... (83 campos)
      }
    }
  ],
  "created_at": "2025-11-26T...",
  "updated_at": "..."
}
```

---

### 3. **edn360** (Base de datos legacy)
- **Colecciones:**
  - `nutrition_questionnaire_submissions` (11)
  - `generation_jobs` (7)

---

### 4. **fitness_db** (Base de datos fitness)
- **Colecciones:**
  - `users` (2 usuarios)

---

## 🔧 CÓMO ACCEDER A LAS BASES DE DATOS

### Opción 1: Python Script

```python
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def main():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    
    # Acceder a base de datos principal
    db = client[os.getenv('DB_NAME')]
    
    # Acceder a base de datos EDN360
    edn360_db = client[os.getenv('MONGO_EDN360_APP_DB_NAME')]
    
    # Ejemplo: Buscar usuarios
    users = await db.users.find({}).to_list(100)
    print(f"Usuarios: {len(users)}")
    
    # Ejemplo: Buscar cuestionarios EDN360
    drawers = await edn360_db.client_drawers.find({}).to_list(100)
    for drawer in drawers:
        print(f"Usuario: {drawer['user_id']}")
        print(f"Cuestionarios: {len(drawer.get('shared_questionnaires', []))}")

asyncio.run(main())
```

### Opción 2: Bash + Python one-liner

```bash
cd /app/backend && python3 << 'EOF'
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('.env')

async def main():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    db = client['test_database']
    
    # TU CÓDIGO AQUÍ
    users = await db.users.find({}).to_list(100)
    for user in users:
        print(f"User: {user['email']}")

asyncio.run(main())
EOF
```

---

## 📝 OPERACIONES COMUNES

### 1. Ver todos los cuestionarios EDN360

```python
async def ver_cuestionarios():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    edn360_db = client['edn360_app']
    
    drawers = await edn360_db.client_drawers.find({}).to_list(100)
    
    for drawer in drawers:
        user_id = drawer['user_id']
        questionnaires = drawer.get('shared_questionnaires', [])
        
        print(f"\n📁 Usuario: {user_id}")
        for q in questionnaires:
            print(f"   - {q['submission_id']}")
            print(f"     Tipo: {q['questionnaire_type']}")
            print(f"     Fecha: {q['submitted_at']}")
```

### 2. Ver todos los planes de entrenamiento EDN360

```python
async def ver_planes():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    edn360_db = client['edn360_app']
    
    plans = await edn360_db.training_plans_v2.find({}).to_list(100)
    
    for plan in plans:
        print(f"\n📋 Plan:")
        print(f"   Usuario: {plan['user_id']}")
        print(f"   Creado: {plan['created_at']}")
        print(f"   Título: {plan['plan'].get('title')}")
```

### 3. Agregar un cuestionario manualmente

```python
async def agregar_cuestionario(user_id, questionnaire_data):
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    edn360_db = client['edn360_app']
    
    cuestionario = {
        "submission_id": "quest_manual_001",
        "questionnaire_type": "initial",
        "source": "manual",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "responses": questionnaire_data
    }
    
    await edn360_db.client_drawers.update_one(
        {'_id': f'client_{user_id}'},
        {
            '$push': {'shared_questionnaires': cuestionario},
            '$set': {'updated_at': datetime.now(timezone.utc).isoformat()}
        },
        upsert=True
    )
```

### 4. Eliminar un cuestionario específico

```python
async def eliminar_cuestionario(user_id, submission_id):
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    edn360_db = client['edn360_app']
    
    await edn360_db.client_drawers.update_one(
        {'_id': f'client_{user_id}'},
        {'$pull': {'shared_questionnaires': {'submission_id': submission_id}}}
    )
```

### 5. Eliminar un plan de entrenamiento

```python
async def eliminar_plan(user_id):
    client = AsyncIOMotorClient(os.getenv('MONGO_URL'))
    edn360_db = client['edn360_app']
    
    # Eliminar el último plan
    plan = await edn360_db.training_plans_v2.find_one(
        {'user_id': user_id},
        sort=[('created_at', -1)]
    )
    
    if plan:
        await edn360_db.training_plans_v2.delete_one({'_id': plan['_id']})
        print(f"✅ Plan eliminado")
```

---

## 🔍 CONSULTAS ÚTILES

### Contar documentos

```python
# Contar usuarios
count = await db.users.count_documents({})
print(f"Total usuarios: {count}")

# Contar planes EDN360
count = await edn360_db.training_plans_v2.count_documents({'user_id': user_id})
print(f"Planes del usuario: {count}")
```

### Buscar por fecha

```python
from datetime import datetime

# Planes generados hoy
today = datetime.now().strftime('%Y-%m-%d')
plans = await edn360_db.training_plans_v2.find({
    'created_at': {'$regex': f'^{today}'}
}).to_list(100)
```

### Actualizar un campo

```python
# Actualizar el título de un plan
await edn360_db.training_plans_v2.update_one(
    {'user_id': user_id},
    {'$set': {'plan.title': 'Nuevo Título'}}
)
```

---

## ⚠️ IMPORTANTE

**Variables de entorno en `/app/backend/.env`:**
```bash
MONGO_URL=mongodb://localhost:27017/
DB_NAME=test_database
MONGO_EDN360_APP_DB_NAME=edn360_app
```

**Siempre usar:**
- `{"_id": 0}` al hacer find() para excluir ObjectId
- `.to_list(limit)` con Motor (async driver)
- `await` en todas las operaciones de base de datos
- `timezone.utc` para fechas

---

## 📊 RESUMEN DE COLECCIONES CRÍTICAS

| Colección | Base de Datos | Propósito | Documentos Actuales |
|-----------|---------------|-----------|---------------------|
| `users` | test_database | Usuarios del sistema | 5 |
| `client_drawers` | edn360_app | Cuestionarios EDN360 | 2 |
| `training_plans_v2` | edn360_app | Planes EDN360 | 0 |
| `edn360_snapshots` | edn360_app | Logs de ejecuciones | 64 |
| `training_plans` | test_database | Planes legacy | 0 |
| `nutrition_plans` | test_database | Nutrición legacy | 0 |

---

**Última actualización:** 2 de Diciembre, 2025
