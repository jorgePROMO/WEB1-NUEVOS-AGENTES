"""
Test de jobs reales para validación operativa final
"""
import asyncio
import sys
import time
import json
from datetime import datetime, timezone
sys.path.insert(0, '/app/backend')

from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.test_database

async def create_test_job(user_id, submission_id, mode="full"):
    """Crea un job de prueba"""
    job_id = f"test_job_{mode}_{int(time.time() * 1000000)}"
    
    job_doc = {
        "_id": job_id,
        "user_id": user_id,
        "type": mode,
        "submission_id": submission_id,
        "training_plan_id": None,
        "previous_nutrition_plan_id": None,
        "previous_training_plan_id": None,
        "status": "pending",
        "progress": {
            "phase": "pending",
            "current_agent": None,
            "completed_steps": 0,
            "total_steps": 18 if mode == "full" else 9,
            "percentage": 0,
            "message": "Job de prueba creado"
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
    return job_id

async def monitor_job(job_id, timeout=1800):
    """Monitorea un job hasta que complete o falle"""
    start_time = time.time()
    last_progress = -1
    
    print(f"\n📊 Monitoreando job: {job_id}")
    print("=" * 60)
    
    while True:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print(f"⏱️ Timeout alcanzado ({timeout}s)")
            break
        
        job = await db.generation_jobs.find_one({"_id": job_id})
        if not job:
            print("❌ Job no encontrado")
            break
        
        status = job["status"]
        progress = job.get("progress", {})
        percentage = progress.get("percentage", 0)
        current_agent = progress.get("current_agent", "N/A")
        
        # Mostrar actualización si hay cambio
        if percentage != last_progress:
            print(f"[{elapsed:.1f}s] {status.upper()} | {percentage}% | Agente: {current_agent}")
            last_progress = percentage
        
        # Verificar si terminó
        if status in ["completed", "failed"]:
            total_time = time.time() - start_time
            
            print("\n" + "=" * 60)
            print(f"✅ Job finalizado: {status.upper()}")
            print(f"⏱️ Tiempo total: {total_time:.2f}s ({total_time/60:.2f} min)")
            
            if status == "completed":
                result = job.get("result", {})
                print(f"📦 Resultado:")
                print(f"   - Training Plan: {result.get('training_plan_id', 'N/A')}")
                print(f"   - Nutrition Plan: {result.get('nutrition_plan_id', 'N/A')}")
            else:
                error = job.get("error_message", "Unknown error")
                print(f"❌ Error: {error[:200]}")
            
            # Calcular tokens (estimación basada en agentes)
            if status == "completed":
                # Cada agente ~1000-2000 tokens promedio
                estimated_tokens = progress.get("completed_steps", 0) * 1500
                print(f"🎯 Tokens estimados: ~{estimated_tokens}")
            
            return {
                "job_id": job_id,
                "status": status,
                "total_time": total_time,
                "completed_steps": progress.get("completed_steps", 0),
                "error": job.get("error_message") if status == "failed" else None
            }
        
        await asyncio.sleep(5)  # Check cada 5 segundos

async def test_3_consecutive_jobs():
    """Test 1: 3 jobs FULL consecutivos"""
    print("\n" + "🧪 TEST 1: 3 JOBS FULL CONSECUTIVOS ".center(60, "="))
    
    # Buscar usuario y cuestionario de prueba
    user = await db.users.find_one({"role": "user"})
    if not user:
        print("❌ No hay usuarios disponibles")
        return
    
    submission = await db.nutrition_questionnaire_submissions.find_one({"user_id": user["_id"]})
    if not submission:
        print("❌ No hay cuestionarios disponibles")
        return
    
    user_id = user["_id"]
    submission_id = submission["_id"]
    
    results = []
    
    for i in range(1, 4):
        print(f"\n🚀 Iniciando Job {i}/3 (mode: full)")
        job_id = await create_test_job(user_id, submission_id, "full")
        result = await monitor_job(job_id, timeout=1800)  # 30 min max
        results.append(result)
        
        if result["status"] != "completed":
            print(f"\n⚠️ Job {i} falló, deteniendo prueba")
            break
        
        # Pequeña pausa entre jobs
        if i < 3:
            print("\n⏸️ Pausa de 10s antes del siguiente job...")
            await asyncio.sleep(10)
    
    # Resumen
    print("\n" + "📊 RESUMEN DE PRUEBA ".center(60, "="))
    for i, result in enumerate(results, 1):
        print(f"\nJob {i}:")
        print(f"  Status: {result['status']}")
        print(f"  Tiempo: {result['total_time']:.2f}s ({result['total_time']/60:.2f} min)")
        print(f"  Pasos completados: {result['completed_steps']}")
        if result.get('error'):
            print(f"  Error: {result['error'][:100]}")
    
    return results

async def test_2_concurrent_jobs():
    """Test 2: 2 jobs concurrentes"""
    print("\n" + "🧪 TEST 2: 2 JOBS CONCURRENTES ".center(60, "="))
    
    user = await db.users.find_one({"role": "user"})
    submission = await db.nutrition_questionnaire_submissions.find_one({"user_id": user["_id"]})
    
    user_id = user["_id"]
    submission_id = submission["_id"]
    
    # Crear 2 jobs simultáneamente
    job1_id = await create_test_job(user_id, submission_id, "training")
    job2_id = await create_test_job(user_id, submission_id, "training")
    
    print(f"🚀 Job 1: {job1_id}")
    print(f"🚀 Job 2: {job2_id}")
    
    # Monitorear ambos en paralelo
    result1, result2 = await asyncio.gather(
        monitor_job(job1_id, timeout=1800),
        monitor_job(job2_id, timeout=1800)
    )
    
    print("\n" + "📊 RESUMEN CONCURRENCIA ".center(60, "="))
    print(f"Job 1: {result1['status']} - {result1['total_time']:.2f}s")
    print(f"Job 2: {result2['status']} - {result2['total_time']:.2f}s")
    
    return [result1, result2]

async def main():
    print("\n" + "🔬 VALIDACIÓN OPERATIVA FINAL - E.D.N.360 ".center(60, "="))
    print(f"Fecha: {datetime.now()}")
    print("=" * 60)
    
    # TEST 1: 3 jobs consecutivos
    try:
        results_consecutive = await test_3_consecutive_jobs()
    except Exception as e:
        print(f"❌ Error en test consecutivo: {e}")
        results_consecutive = None
    
    # TEST 2: 2 jobs concurrentes
    try:
        results_concurrent = await test_2_concurrent_jobs()
    except Exception as e:
        print(f"❌ Error en test concurrente: {e}")
        results_concurrent = None
    
    print("\n" + "✅ VALIDACIÓN COMPLETA ".center(60, "="))

if __name__ == "__main__":
    asyncio.run(main())
