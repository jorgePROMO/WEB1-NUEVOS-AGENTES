"""
Test script para el sistema de generación asíncrona de planes E.D.N.360
"""
import asyncio
import sys
import os
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, '/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment
load_dotenv('/app/backend/.env')
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')

# MongoDB setup
client = AsyncIOMotorClient(MONGO_URL)
db = client.test_database

async def test_async_generation():
    """Test completo del sistema de generación asíncrona"""
    
    print("\n" + "="*80)
    print("🧪 TEST: Sistema de Generación Asíncrona E.D.N.360")
    print("="*80 + "\n")
    
    # 1. Buscar un usuario con cuestionario
    print("📋 PASO 1: Buscando usuario con cuestionario...")
    
    user = await db.users.find_one({"role": "user"})
    if not user:
        print("❌ No se encontró ningún usuario")
        return
    
    user_id = user["_id"]
    print(f"✅ Usuario encontrado: {user.get('name', user.get('username'))} (ID: {user_id})")
    
    # 2. Buscar cuestionario de nutrición
    print("\n📋 PASO 2: Buscando cuestionario de nutrición...")
    
    submission = await db.nutrition_questionnaire_submissions.find_one(
        {"user_id": user_id},
        sort=[("submitted_at", 1)]
    )
    
    if not submission:
        print("❌ No se encontró cuestionario de nutrición para este usuario")
        return
    
    submission_id = submission["_id"]
    print(f"✅ Cuestionario encontrado (ID: {submission_id})")
    
    # 3. Crear job de generación
    print("\n🚀 PASO 3: Creando job de generación (mode: training)...")
    
    job_id = f"test_job_{int(datetime.now(timezone.utc).timestamp() * 1000000)}"
    
    job_doc = {
        "_id": job_id,
        "user_id": user_id,
        "type": "training",
        "submission_id": submission_id,
        "training_plan_id": None,
        "previous_nutrition_plan_id": None,
        "previous_training_plan_id": None,
        "status": "pending",
        "progress": {
            "phase": "pending",
            "current_agent": None,
            "completed_steps": 0,
            "total_steps": 9,
            "percentage": 0,
            "message": "Job creado, esperando ejecución"
        },
        "result": {
            "training_plan_id": None,
            "nutrition_plan_id": None
        },
        "error_message": None,
        "created_at": datetime.now(timezone.utc),
        "started_at": None,
        "completed_at": None
    }
    
    await db.generation_jobs.insert_one(job_doc)
    print(f"✅ Job creado: {job_id}")
    
    # 4. Verificar que el job fue creado
    print("\n🔍 PASO 4: Verificando job en la base de datos...")
    
    job = await db.generation_jobs.find_one({"_id": job_id})
    
    if not job:
        print("❌ Job no encontrado en la base de datos")
        return
    
    print(f"✅ Job verificado:")
    print(f"   - Estado: {job['status']}")
    print(f"   - Tipo: {job['type']}")
    print(f"   - Progreso: {job['progress']['percentage']}%")
    print(f"   - Mensaje: {job['progress']['message']}")
    
    # 5. Simular ejecución del background worker
    print("\n⚙️  PASO 5: El background worker procesaría este job automáticamente")
    print("   Para ejecutar manualmente, importa y llama a:")
    print(f"   >>> from server import process_generation_job")
    print(f"   >>> await process_generation_job('{job_id}')")
    
    print("\n" + "="*80)
    print("✅ TEST COMPLETADO")
    print("="*80 + "\n")
    
    print("📊 RESUMEN:")
    print(f"   - Job ID: {job_id}")
    print(f"   - Usuario: {user.get('name', user.get('username'))}")
    print(f"   - Cuestionario: {submission_id}")
    print(f"   - Estado: {job['status']}")
    print(f"\n💡 Consulta el estado en: GET /jobs/{job_id}")
    
    # Cleanup (opcional)
    print("\n🧹 Limpiando job de prueba...")
    await db.generation_jobs.delete_one({"_id": job_id})
    print("✅ Job eliminado")

if __name__ == "__main__":
    asyncio.run(test_async_generation())
