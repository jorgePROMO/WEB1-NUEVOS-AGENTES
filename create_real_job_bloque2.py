"""
Crear job REAL en MongoDB para que el worker lo procese
"""
import asyncio
import time
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'test_database')  # Usar la misma DB que el servidor
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
print(f"📁 Usando base de datos: {DB_NAME}")

async def create_job():
    print("=" * 80)
    print("🚀 CREANDO JOB REAL BLOQUE 2")
    print("=" * 80)
    
    # 1. Crear cuestionario
    timestamp = int(time.time())
    quest_id = f"quest_bloque2_real_{timestamp}"
    
    questionnaire = {
        "_id": quest_id,
        "user_id": "admin_jorge_001",  # Usuario real existente
        "created_at": datetime.now(timezone.utc),
        
        # Datos completos
        "nombre_completo": "María García López",
        "email": "maria.garcia@test.com",
        "fecha_nacimiento": "1990-06-15",
        "sexo": "mujer",
        "profesion": "Diseñadora gráfica",
        "peso": "65",
        "altura_cm": "168",
        "grasa_porcentaje": "26",
        "experiencia_entrenamiento": "2 años de gym, 3 veces por semana. Conozco ejercicios básicos.",
        "frecuencia_entrenamiento": "3 veces por semana",
        "tiempo_disponible": "60 minutos",
        "horario_preferido": "Mañanas 7:00",
        "equipo_disponible": "Gimnasio completo",
        "lesiones_actuales": "Ninguna",
        "lesiones_previas": "Tendinitis hombro derecho hace 1 año (recuperada)",
        "objetivo_principal": "Perder grasa y tonificar",
        "peso_objetivo": "60",
        "horas_sueno": "7",
        "nivel_estres": "Medio",
        "trabajo_sedentario": "Sí"
    }
    
    await db.nutrition_questionnaire_submissions.insert_one(questionnaire)
    print(f"✅ Cuestionario creado: {quest_id}")
    
    # 2. Crear job
    job_id = f"job_bloque2_validation_{timestamp}"
    
    job_doc = {
        "_id": job_id,
        "user_id": "user_bloque2_validation",
        "type": "training",
        "submission_id": quest_id,
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
            "message": "Job creado, esperando worker"
        },
        "result": {
            "training_plan_id": None,
            "nutrition_plan_id": None
        },
        "error_message": None,
        "token_usage": {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "by_agent": {}
        },
        "created_at": datetime.now(timezone.utc),
        "started_at": None,
        "completed_at": None
    }
    
    await db.generation_jobs.insert_one(job_doc)
    print(f"✅ Job creado: {job_id}")
    print(f"\n📋 El worker procesará este job automáticamente.")
    print(f"   Para consultar el estado: python check_job_status.py {job_id}")
    
    client.close()
    return job_id

if __name__ == "__main__":
    job_id = asyncio.run(create_job())
    print(f"\n🎯 Job ID: {job_id}")
    print("=" * 80)
