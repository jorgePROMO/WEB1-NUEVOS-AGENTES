"""
Test del nuevo formato de E7 - Genera un job completo y muestra el formatted_plan
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env')

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'test_database')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

async def create_and_monitor_job():
    """
    Crea un nuevo job y monitorea hasta que complete
    """
    # Usar el mismo usuario y cuestionario de prueba anterior
    user_id = "test_user_1763806322"
    submission_id = "1763806322837723"
    
    # Crear nuevo job
    job_id = f"job_e7test_{int(datetime.now(timezone.utc).timestamp() * 1000000)}"
    
    job_doc = {
        "_id": job_id,
        "user_id": user_id,
        "submission_id": submission_id,
        "type": "training",
        "status": "pending",
        "progress": {
            "phase": "",
            "current_agent": "",
            "completed_steps": 0,
            "total_steps": 9,
            "percentage": 0,
            "message": "En cola..."
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
        "execution_log": [],
        "created_at": datetime.now(timezone.utc),
        "started_at": None,
        "completed_at": None
    }
    
    await db.generation_jobs.insert_one(job_doc)
    
    print(f"✅ Job creado: {job_id}")
    print(f"⏳ Esperando que el worker lo procese...")
    print(f"   (Duración esperada: ~6 minutos)\n")
    
    # Monitorear progreso
    last_status = None
    last_agent = None
    
    for i in range(120):  # 10 minutos máximo
        job = await db.generation_jobs.find_one({"_id": job_id})
        
        if not job:
            print("❌ Job no encontrado")
            return None
        
        status = job["status"]
        progress = job.get("progress", {})
        current_agent = progress.get("current_agent", "")
        
        if status != last_status or current_agent != last_agent:
            print(f"[{i*5:03d}s] Status: {status:10s} | Agent: {current_agent:5s} | {progress.get('percentage', 0):3.0f}%")
            last_status = status
            last_agent = current_agent
        
        if status in ["completed", "failed"]:
            print(f"\n{'✅' if status == 'completed' else '❌'} Job {status}")
            return job_id if status == "completed" else None
        
        await asyncio.sleep(5)
    
    print("\n⚠️  Timeout")
    return None


async def extract_and_display_formatted_plan(job_id):
    """
    Extrae y muestra el nuevo formatted_plan
    """
    print("\n" + "="*70)
    print("NUEVO FORMATTED_PLAN (E7 con prompt actualizado)")
    print("="*70)
    
    job = await db.generation_jobs.find_one({"_id": job_id})
    
    if not job:
        print("❌ Job no encontrado")
        return
    
    training_plan_id = job.get("result", {}).get("training_plan_id")
    
    if not training_plan_id:
        print("❌ No hay training_plan_id")
        return
    
    plan = await db.training_plans.find_one({"_id": training_plan_id})
    
    if not plan:
        print("❌ Training plan no encontrado")
        return
    
    edn360 = plan.get("edn360_data", {})
    formatted_plan = edn360.get("formatted_plan")
    
    if not formatted_plan:
        print("❌ formatted_plan no encontrado")
        return
    
    print(formatted_plan)
    
    # Guardar en archivo
    filename = f"/app/formatted_plan_nuevo_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(formatted_plan)
    
    print(f"\n💾 Guardado en: {filename}")
    
    # También mostrar longitud y estructura
    print(f"\n📊 Análisis:")
    print(f"   - Longitud: {len(formatted_plan)} caracteres")
    print(f"   - Líneas: {formatted_plan.count(chr(10))} líneas")
    print(f"   - Tablas: {formatted_plan.count('|')} pipes (indicador de tablas)")
    print(f"   - Secciones de semana: {formatted_plan.count('## 🗓️')}")


async def main():
    print("\n" + "="*70)
    print("TEST DEL NUEVO FORMATO E7 - PLAN PREMIUM EN MARKDOWN")
    print("="*70)
    
    # Crear y monitorear job
    job_id = await create_and_monitor_job()
    
    if not job_id:
        print("\n❌ No se pudo completar el job")
        return
    
    # Extraer y mostrar formatted_plan
    await extract_and_display_formatted_plan(job_id)
    
    print("\n" + "="*70)
    print("✅ TEST COMPLETADO")
    print("="*70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⛔ Test cancelado")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
