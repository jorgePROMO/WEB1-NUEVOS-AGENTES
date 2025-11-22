"""
Validación rápida: Verifica que todo el flujo esté configurado correctamente
sin esperar los 6-10 minutos del pipeline completo.
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'test_database')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

from test_full_pipeline_validation import (
    EXAMPLE_QUESTIONNAIRE_RESPONSES,
    create_test_user_and_submission,
    create_generation_job,
    _validate_questionnaire_format
)

async def quick_check():
    """
    Verificación rápida de que todo está configurado correctamente.
    """
    print("\n" + "="*70)
    print("   VERIFICACIÓN RÁPIDA - CONFIGURACIÓN DEL SISTEMA")
    print("="*70)
    
    checks_passed = []
    checks_failed = []
    
    # Check 1: MongoDB connection
    print("\n1️⃣  Verificando conexión a MongoDB...")
    try:
        await db.command("ping")
        print(f"   ✅ MongoDB conectado: {MONGO_URL}")
        print(f"   ✅ Base de datos: {DB_NAME}")
        checks_passed.append("MongoDB connection")
    except Exception as e:
        print(f"   ❌ Error conectando a MongoDB: {e}")
        checks_failed.append("MongoDB connection")
        return
    
    # Check 2: Validate questionnaire format
    print("\n2️⃣  Validando formato del cuestionario de ejemplo...")
    test_submission = {
        "_id": "test_123",
        "user_id": "user_123",
        "responses": EXAMPLE_QUESTIONNAIRE_RESPONSES,
        "submitted_at": datetime.now(timezone.utc),
        "plan_generated": False
    }
    
    from server import _validate_questionnaire_format as validate_func
    is_valid, errors, data = validate_func(test_submission)
    
    if is_valid:
        print(f"   ✅ Cuestionario de ejemplo válido")
        print(f"   ✅ Validación robusta funcionando")
        checks_passed.append("Questionnaire validation")
    else:
        print(f"   ❌ Cuestionario inválido:")
        for error in errors:
            print(f"      - {error}")
        checks_failed.append("Questionnaire validation")
        return
    
    # Check 3: Create test user and submission
    print("\n3️⃣  Creando usuario y cuestionario de prueba...")
    try:
        user_id, submission_id = await create_test_user_and_submission()
        if user_id and submission_id:
            print(f"   ✅ Usuario creado: {user_id}")
            print(f"   ✅ Cuestionario guardado: {submission_id}")
            checks_passed.append("Test data creation")
        else:
            print(f"   ❌ No se pudo crear usuario/cuestionario")
            checks_failed.append("Test data creation")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        checks_failed.append("Test data creation")
        return
    
    # Check 4: Create generation job
    print("\n4️⃣  Creando job de generación...")
    try:
        job_id = await create_generation_job(user_id, submission_id)
        print(f"   ✅ Job creado: {job_id}")
        checks_passed.append("Job creation")
        
        # Verify job in database
        job = await db.generation_jobs.find_one({"_id": job_id})
        if job:
            print(f"   ✅ Job existe en MongoDB")
            print(f"      - Status: {job['status']}")
            print(f"      - Type: {job['type']}")
            print(f"      - User: {job['user_id']}")
            print(f"      - Submission: {job['submission_id']}")
        else:
            print(f"   ❌ Job no encontrado en MongoDB")
            checks_failed.append("Job in database")
            return
    except Exception as e:
        print(f"   ❌ Error: {e}")
        checks_failed.append("Job creation")
        return
    
    # Check 5: Worker status (check if it picks up the job)
    print("\n5️⃣  Verificando que el worker procese el job...")
    print("   ⏳ Esperando 10 segundos para que el worker lo detecte...")
    await asyncio.sleep(10)
    
    job_updated = await db.generation_jobs.find_one({"_id": job_id})
    if job_updated["status"] != "pending":
        print(f"   ✅ Worker está procesando el job")
        print(f"      - Status actualizado: {job_updated['status']}")
        if job_updated.get("started_at"):
            print(f"      - Iniciado: {job_updated['started_at']}")
        if job_updated.get("progress"):
            progress = job_updated["progress"]
            print(f"      - Progreso: {progress.get('percentage', 0):.1f}%")
            print(f"      - Agente actual: {progress.get('current_agent', 'N/A')}")
            print(f"      - Mensaje: {progress.get('message', 'N/A')}")
        checks_passed.append("Worker processing")
        
        print("\n   📊 JOB EN PROGRESO:")
        print(f"      El pipeline E1-E9 típicamente toma 6-10 minutos")
        print(f"      Para monitorear en tiempo real:")
        print(f"         python /app/backend/test_full_pipeline_validation.py")
        print(f"      O consultar directamente el job:")
        print(f"         Job ID: {job_id}")
    else:
        print(f"   ⚠️  Job aún en estado 'pending'")
        print(f"      Verificar logs del worker:")
        print(f"         tail -f /var/log/supervisor/job_worker.out.log")
        checks_failed.append("Worker processing")
    
    # Summary
    print("\n" + "="*70)
    print("   RESUMEN DE VERIFICACIÓN")
    print("="*70)
    print(f"\n✅ Checks exitosos ({len(checks_passed)}):")
    for check in checks_passed:
        print(f"   - {check}")
    
    if checks_failed:
        print(f"\n❌ Checks fallidos ({len(checks_failed)}):")
        for check in checks_failed:
            print(f"   - {check}")
    else:
        print(f"\n🎉 TODAS LAS VERIFICACIONES PASARON")
        print(f"\n📝 PRÓXIMOS PASOS:")
        print(f"   1. El job {job_id} está siendo procesado")
        print(f"   2. Para validación completa con métricas, ejecutar:")
        print(f"      cd /app/backend && python run_validation_auto.py")
        print(f"   3. O para monitoreo manual:")
        print(f"      cd /app/backend && python test_full_pipeline_validation.py")
    
    return len(checks_failed) == 0


if __name__ == "__main__":
    try:
        success = asyncio.run(quick_check())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⛔ Verificación cancelada")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
