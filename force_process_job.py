"""Forzar procesamiento del job manualmente"""
import sys
sys.path.append('/app/backend')

import asyncio
from job_worker import process_job
from motor.motor_asyncio import AsyncIOMotorClient
import os

async def main():
    print("Procesando job manualmente...")
    
    client = AsyncIOMotorClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017'))
    db = client['edn360']
    
    job_id = "job_bloque1_real_1763749714769268"
    
    job = await db.generation_jobs.find_one({"_id": job_id})
    
    if not job:
        print(f"❌ Job {job_id} no encontrado")
        return
    
    print(f"✅ Job encontrado: {job_id}")
    print(f"   Status: {job['status']}")
    print(f"   Type: {job['type']}")
    
    # Procesar
    print("\n🚀 Iniciando procesamiento...")
    await process_job(db, job)
    
    print("\n✅ Procesamiento completado")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
