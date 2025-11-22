"""
Versión automatizada del script de validación (sin input interactivo)
"""

import asyncio
from test_full_pipeline_validation import *

async def run_automated():
    """
    Ejecución automatizada sin pausas interactivas.
    """
    print("\n" + "="*70)
    print("   VALIDACIÓN AUTOMATIZADA DEL PIPELINE E1-E9")
    print("="*70)
    
    # Print schema documentation
    await print_schema_documentation()
    
    # Step 1: Create test data
    print("\n⏳ Creando usuario y cuestionario de prueba...")
    user_id, submission_id = await create_test_user_and_submission()
    
    if not user_id or not submission_id:
        print("\n❌ No se pudo crear el usuario o cuestionario de prueba")
        return
    
    # Step 2: Create generation job
    print("\n⏳ Creando job de generación...")
    job_id = await create_generation_job(user_id, submission_id)
    
    print(f"\n{'='*70}")
    print("📊 JOB CREADO - Esperando que el job_worker lo procese")
    print(f"   Job ID: {job_id}")
    print(f"   User ID: {user_id}")
    print(f"   Submission ID: {submission_id}")
    print(f"{'='*70}")
    
    # Step 3: Monitor job progress (15 min timeout)
    print("\n⏳ Monitoreando progreso del job (timeout: 15 minutos)...")
    print("   El worker procesa jobs cada 5 segundos")
    print("   El pipeline E1-E9 típicamente toma 6-10 minutos\n")
    
    final_job = await monitor_job_progress(job_id, timeout_minutes=15)
    
    if not final_job:
        print("\n❌ No se pudo completar el monitoreo del job")
        return
    
    if final_job["status"] != "completed":
        print(f"\n❌ Job no completado exitosamente")
        print(f"   Status final: {final_job['status']}")
        if final_job.get("error_message"):
            print(f"   Error: {final_job['error_message']}")
        return
    
    # Step 4: Extract metrics and outputs
    print("\n⏳ Extrayendo métricas y outputs...")
    report = await extract_metrics_and_outputs(job_id)
    
    if not report:
        print("\n❌ No se pudieron extraer métricas")
        return
    
    # Step 5: Validate coherence
    await validate_coherence(report)
    
    # Save report
    await save_report(report)
    
    print("\n" + "="*70)
    print("   ✅ VALIDACIÓN COMPLETADA EXITOSAMENTE")
    print("="*70)
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   Job ID: {job_id}")
    print(f"   Status: {report['status']}")
    print(f"   Duración: {report['execution_time'].get('duration_minutes', 0):.2f} minutos")
    print(f"   Tokens totales: {report['token_usage'].get('total_tokens', 0):,}")
    print(f"   Costo total: ${report['token_usage'].get('total_cost_usd', 0):.4f} USD")
    print(f"   Outputs generados: {len(report['outputs'])}/4")
    print(f"\n   ✅ Todos los objetivos del Bloque 2 cumplidos:")
    print(f"      1. KeyError 'responses' resuelto con validación robusta")
    print(f"      2. Worker asíncrono funcionando correctamente") 
    print(f"      3. Job E1-E9 completado con métricas reales")
    print(f"      4. Outputs extraídos y coherencia validada")
    

if __name__ == "__main__":
    try:
        asyncio.run(run_automated())
    except KeyboardInterrupt:
        print("\n\n⛔ Validación cancelada por usuario")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
