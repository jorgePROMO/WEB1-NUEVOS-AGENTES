"""
Forzar ejecución de job y guardar output
"""
import sys
sys.path.append('/app/backend')

import asyncio
from server import process_generation_job

async def main():
    job_id = "job_bloque2_validation_1763803330"
    
    print(f"🚀 Forzando ejecución de {job_id}...")
    print("   (Esto puede tardar 6-10 minutos)")
    print()
    
    try:
        await process_generation_job(job_id)
        print(f"\n✅ Job procesado exitosamente")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
