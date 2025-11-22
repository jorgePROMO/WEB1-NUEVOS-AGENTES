"""
Forzar procesamiento manual del job
"""
import sys
sys.path.append('/app/backend')

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Import process_generation_job
from server import process_generation_job

async def main():
    job_id = "job_bloque2_validation_1763801166"
    
    print(f"🚀 Forzando procesamiento de {job_id}...")
    
    try:
        await process_generation_job(job_id)
        print(f"✅ Job procesado")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
