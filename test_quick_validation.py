"""
Test rápido de validación antes de pruebas largas
"""
import asyncio
import sys
import time
from datetime import datetime, timezone
sys.path.insert(0, '/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = 'mongodb://localhost:27017'
client = AsyncIOMotorClient(MONGO_URL)
db = client.test_database

async def quick_test():
    print("\n🔬 TEST RÁPIDO DE VALIDACIÓN")
    print("=" * 60)
    
    # 1. Verificar worker está funcionando
    print("\n1️⃣ Verificando worker...")
    jobs_running = await db.generation_jobs.count_documents({"status": "running"})
    jobs_pending = await db.generation_jobs.count_documents({"status": "pending"})
    print(f"   Jobs running: {jobs_running}")
    print(f"   Jobs pending: {jobs_pending}")
    
    # 2. Crear un job de prueba pequeño
    print("\n2️⃣ Creando job de prueba (training only)...")
    user = await db.users.find_one({"role": "user"})
    submission = await db.nutrition_questionnaire_submissions.find_one({"user_id": user["_id"]})
    
    job_id = f"quick_test_{int(time.time() * 1000000)}"
    job_doc = {
        "_id": job_id,
        "user_id": user["_id"],
        "type": "training",
        "submission_id": submission["_id"],
        "status": "pending",
        "progress": {
            "phase": "pending",
            "completed_steps": 0,
            "total_steps": 9,
            "percentage": 0
        },
        "result": {},
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.generation_jobs.insert_one(job_doc)
    print(f"   ✅ Job creado: {job_id}")
    
    # 3. Esperar a que el worker lo tome (máx 30 segundos)
    print("\n3️⃣ Esperando que worker procese el job...")
    for i in range(30):
        await asyncio.sleep(1)
        job = await db.generation_jobs.find_one({"_id": job_id})
        status = job["status"]
        
        if status != "pending":
            print(f"   ✅ Worker tomó el job (status: {status})")
            
            # Monitorear por 2 minutos más para ver progreso inicial
            print("\n4️⃣ Monitoreando progreso inicial (2 min)...")
            for j in range(24):  # 2 minutos
                await asyncio.sleep(5)
                job = await db.generation_jobs.find_one({"_id": job_id})
                progress = job.get("progress", {})
                print(f"   [{j*5}s] {job['status']} | {progress.get('percentage', 0)}% | {progress.get('current_agent', 'N/A')}")
                
                if job["status"] in ["completed", "failed"]:
                    break
            
            # Resumen
            final_job = await db.generation_jobs.find_one({"_id": job_id})
            print("\n" + "=" * 60)
            print(f"📊 RESUMEN:")
            print(f"   Status final: {final_job['status']}")
            print(f"   Progreso: {final_job['progress'].get('percentage', 0)}%")
            if final_job["status"] == "failed":
                print(f"   Error: {final_job.get('error_message', 'N/A')[:200]}")
            
            return final_job
    
    print("   ⚠️ Worker no tomó el job en 30s (puede estar ocupado)")
    return None

if __name__ == "__main__":
    asyncio.run(quick_test())
