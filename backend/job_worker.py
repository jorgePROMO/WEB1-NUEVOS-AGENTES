"""
Job Worker - Proceso separado para ejecutar jobs de generación E.D.N.360

Este worker:
1. Corre como proceso independiente de FastAPI
2. Lee jobs con status="pending" de MongoDB
3. Ejecuta process_generation_job() para cada job
4. Actualiza progreso en tiempo real
5. FastAPI NUNCA ejecuta el orquestador directamente

Ejecutar:
    python job_worker.py
    
O con supervisor:
    sudo supervisorctl start job_worker
"""

import asyncio
import sys
import os
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient

# Get MongoDB URL and DB name from environment (set by supervisor or default)
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'test_database')

# MongoDB setup
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('job_worker')

# Import the job processing function
from server import (
    process_generation_job,
    add_job_log,
    check_job_concurrency,
    update_job_progress
)

async def process_pending_jobs():
    """
    Busca y procesa jobs pendientes.
    Solo procesa si hay espacio (< 2 jobs en running).
    """
    try:
        # Contar jobs en running
        running_count = await db.generation_jobs.count_documents({"status": "running"})
        
        if running_count >= 2:
            logger.debug(f"⏳ Ya hay {running_count} jobs en ejecución. Esperando...")
            return
        
        # Buscar jobs pendientes (FIFO)
        available_slots = 2 - running_count
        pending_jobs = await db.generation_jobs.find(
            {"status": "pending"}
        ).sort("created_at", 1).limit(available_slots).to_list(length=10)
        
        for job in pending_jobs:
            job_id = job["_id"]
            logger.info(f"🚀 Worker procesando job: {job_id}")
            
            try:
                # Ejecutar job
                await process_generation_job(job_id)
                logger.info(f"✅ Job {job_id} completado por worker")
            except Exception as e:
                logger.error(f"❌ Error procesando job {job_id}: {e}")
                # El error ya se guarda en process_generation_job
    
    except Exception as e:
        logger.error(f"❌ Error en process_pending_jobs: {e}")

async def timeout_watchdog():
    """
    Watchdog que marca jobs stuck como failed después de 30 minutos.
    """
    timeout_minutes = 30
    
    while True:
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=timeout_minutes)
            
            # Buscar jobs stuck
            stuck_jobs = await db.generation_jobs.find({
                "status": "running",
                "started_at": {"$lt": cutoff_time}
            }).to_list(length=100)
            
            for job in stuck_jobs:
                job_id = job["_id"]
                logger.warning(f"⚠️ Timeout: Job {job_id} excedió {timeout_minutes} min")
                
                await db.generation_jobs.update_one(
                    {"_id": job_id},
                    {
                        "$set": {
                            "status": "failed",
                            "error_message": f"Job excedió timeout de {timeout_minutes} minutos",
                            "error_reason": "timeout",
                            "completed_at": datetime.now(timezone.utc)
                        }
                    }
                )
                
                try:
                    await add_job_log(job_id, "timeout", f"Marcado como failed por timeout ({timeout_minutes} min)")
                except:
                    pass
            
            if stuck_jobs:
                logger.info(f"✅ Timeout watchdog: {len(stuck_jobs)} job(s) marcados como failed")
        
        except Exception as e:
            logger.error(f"❌ Error en timeout_watchdog: {e}")
        
        # Check cada 5 minutos
        await asyncio.sleep(300)

async def worker_main():
    """
    Loop principal del worker.
    Procesa jobs cada 5 segundos.
    """
    logger.info("🚀 Job Worker iniciado")
    logger.info("📊 Configuración:")
    logger.info(f"   - MongoDB: {MONGO_URL}")
    logger.info(f"   - Intervalo de polling: 5 segundos")
    logger.info(f"   - Concurrencia máxima: 2 jobs simultáneos")
    logger.info(f"   - Timeout: 30 minutos")
    
    # Iniciar watchdog en background
    asyncio.create_task(timeout_watchdog())
    
    # Loop principal
    while True:
        try:
            await process_pending_jobs()
        except Exception as e:
            logger.error(f"❌ Error en worker_main: {e}")
        
        # Esperar 5 segundos antes del próximo ciclo
        await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(worker_main())
    except KeyboardInterrupt:
        logger.info("⛔ Worker detenido por usuario")
    except Exception as e:
        logger.error(f"❌ Error fatal en worker: {e}")
        sys.exit(1)
