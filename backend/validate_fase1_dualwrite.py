"""
Script de Validación - FASE 1 Dual Write

Valida que la implementación de dual-write está funcionando correctamente.

Ejecución:
    python /app/backend/validate_fase1_dualwrite.py

Verifica:
- Feature flag USE_CLIENT_DRAWER_WRITE
- Telemetría global de client_drawers
- Comparación BD Web vs client_drawers
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from repositories.client_drawer_repository import get_global_telemetry, count_drawers

# Configuración
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
MONGO_WEB_DB_NAME = os.getenv('MONGO_WEB_DB_NAME', 'test_database')
MONGO_EDN360_APP_DB_NAME = os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')
USE_CLIENT_DRAWER_WRITE = os.getenv('USE_CLIENT_DRAWER_WRITE', 'false').lower() == 'true'

print("="*80)
print(" VALIDACIÓN FASE 1 - DUAL WRITE")
print("="*80)
print()


async def validate_dual_write():
    """
    Valida la implementación de dual-write.
    """
    
    # Conectar a MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db_web = client[MONGO_WEB_DB_NAME]
    db_edn360 = client[MONGO_EDN360_APP_DB_NAME]
    
    print("📊 CONFIGURACIÓN")
    print("-" * 80)
    print(f"MongoDB URL: {MONGO_URL}")
    print(f"BD Web: {MONGO_WEB_DB_NAME}")
    print(f"BD EDN360 APP: {MONGO_EDN360_APP_DB_NAME}")
    print(f"USE_CLIENT_DRAWER_WRITE: {USE_CLIENT_DRAWER_WRITE}")
    print()
    
    # ============================================
    # 1. Verificar Feature Flag
    # ============================================
    print("🚩 FEATURE FLAG")
    print("-" * 80)
    if USE_CLIENT_DRAWER_WRITE:
        print("✅ USE_CLIENT_DRAWER_WRITE=true → Dual-write ACTIVO")
    else:
        print("⚠️  USE_CLIENT_DRAWER_WRITE=false → Solo BD Web (legacy)")
    print()
    
    # ============================================
    # 2. Telemetría Global de client_drawers
    # ============================================
    print("📊 TELEMETRÍA CLIENT_DRAWERS")
    print("-" * 80)
    
    telemetry = await get_global_telemetry()
    
    print(f"Total de cajones (client_drawers): {telemetry['total_drawers']}")
    print(f"Total de cuestionarios compartidos: {telemetry['total_shared_questionnaires']}")
    print(f"Promedio de cuestionarios por cajón: {telemetry['avg_questionnaires_per_drawer']}")
    print()
    
    if telemetry['total_drawers'] == 0:
        print("ℹ️  No hay cajones todavía (normal si acabas de activar dual-write)")
        print("   Los cajones se crearán cuando llegue el primer cuestionario nuevo.")
    elif telemetry['total_shared_questionnaires'] == 0:
        print("⚠️  Hay cajones pero sin cuestionarios")
        print("   Esto puede indicar que los cajones se crearon pero no se añadieron cuestionarios.")
    else:
        print(f"✅ Sistema operativo con {telemetry['total_drawers']} cajón(es) "
              f"y {telemetry['total_shared_questionnaires']} cuestionario(s)")
    
    print()
    
    # ============================================
    # 3. Estadísticas BD Web
    # ============================================
    print("📊 ESTADÍSTICAS BD WEB")
    print("-" * 80)
    
    # Cuestionarios de prospección
    prospect_count = await db_web.questionnaire_responses.count_documents({})
    print(f"Cuestionarios de prospección (questionnaire_responses): {prospect_count}")
    
    # Cuestionarios nutricionales detallados
    nutrition_count = await db_web.nutrition_questionnaire_submissions.count_documents({})
    print(f"Cuestionarios nutricionales (nutrition_questionnaire_submissions): {nutrition_count}")
    
    # Cuestionarios de seguimiento
    followup_count = await db_web.follow_up_submissions.count_documents({})
    print(f"Cuestionarios de seguimiento (follow_up_submissions): {followup_count}")
    
    total_web = nutrition_count + followup_count
    print()
    print(f"📈 Total de cuestionarios en BD Web (nutrition + followup): {total_web}")
    print(f"📈 Total en client_drawers: {telemetry['total_shared_questionnaires']}")
    print()
    
    # ============================================
    # 4. Comparación y Match Rate
    # ============================================
    print("🔍 ANÁLISIS DE MATCH RATE")
    print("-" * 80)
    
    if not USE_CLIENT_DRAWER_WRITE:
        print("⚠️  Dual-write desactivado, no se espera match")
    elif total_web == 0:
        print("ℹ️  No hay cuestionarios en BD Web todavía")
    elif telemetry['total_shared_questionnaires'] == 0:
        print("⚠️  Hay cuestionarios en BD Web pero ninguno en client_drawers")
        print("   Posibles causas:")
        print("   - Dual-write se activó recientemente y aún no hay cuestionarios nuevos")
        print("   - Hay un error en la implementación de dual-write")
    else:
        # Calcular match rate (aproximado)
        # Nota: Esta es una estimación simple, no cuenta duplicados
        if total_web > 0:
            match_rate = (telemetry['total_shared_questionnaires'] / total_web) * 100
            print(f"📊 Match Rate estimado: {match_rate:.2f}%")
            
            if match_rate >= 90:
                print("✅ Match rate excelente (≥90%)")
            elif match_rate >= 75:
                print("⚠️  Match rate aceptable (75-90%), revisar logs")
            else:
                print("❌ Match rate bajo (<75%), revisar implementación")
    
    print()
    
    # ============================================
    # 5. Verificar últimos cuestionarios
    # ============================================
    print("🔍 ÚLTIMOS CUESTIONARIOS (BD WEB)")
    print("-" * 80)
    
    # Último nutrition questionnaire
    last_nutrition = await db_web.nutrition_questionnaire_submissions.find_one(
        {},
        sort=[("submitted_at", -1)]
    )
    
    if last_nutrition:
        print(f"Último cuestionario nutricional:")
        print(f"  - ID: {last_nutrition['_id']}")
        print(f"  - User ID: {last_nutrition.get('user_id')}")
        print(f"  - Fecha: {last_nutrition.get('submitted_at')}")
        
        # Verificar si está en client_drawers
        user_id = last_nutrition.get('user_id')
        if user_id:
            drawer = await db_edn360.client_drawers.find_one({"user_id": user_id})
            if drawer:
                submission_ids = [q['submission_id'] for q in drawer.get('services', {}).get('shared_questionnaires', [])]
                if last_nutrition['_id'] in submission_ids:
                    print(f"  ✅ Encontrado en client_drawers")
                else:
                    print(f"  ⚠️  NO encontrado en client_drawers")
            else:
                print(f"  ⚠️  No existe drawer para user_id {user_id}")
    else:
        print("No hay cuestionarios nutricionales")
    
    print()
    
    # Último followup
    last_followup = await db_web.follow_up_submissions.find_one(
        {},
        sort=[("submission_date", -1)]
    )
    
    if last_followup:
        print(f"Último cuestionario de seguimiento:")
        print(f"  - ID: {last_followup['_id']}")
        print(f"  - User ID: {last_followup.get('user_id')}")
        print(f"  - Fecha: {last_followup.get('submission_date')}")
        
        # Verificar si está en client_drawers
        user_id = last_followup.get('user_id')
        if user_id:
            drawer = await db_edn360.client_drawers.find_one({"user_id": user_id})
            if drawer:
                submission_ids = [q['submission_id'] for q in drawer.get('services', {}).get('shared_questionnaires', [])]
                if last_followup['_id'] in submission_ids:
                    print(f"  ✅ Encontrado en client_drawers")
                else:
                    print(f"  ⚠️  NO encontrado en client_drawers")
            else:
                print(f"  ⚠️  No existe drawer para user_id {user_id}")
    else:
        print("No hay cuestionarios de seguimiento")
    
    print()
    
    # ============================================
    # 6. Resumen Final
    # ============================================
    print("="*80)
    print(" RESUMEN VALIDACIÓN")
    print("="*80)
    print()
    
    issues = []
    
    if not USE_CLIENT_DRAWER_WRITE:
        issues.append("⚠️  Dual-write desactivado (USE_CLIENT_DRAWER_WRITE=false)")
    
    if USE_CLIENT_DRAWER_WRITE and total_web > 0 and telemetry['total_shared_questionnaires'] == 0:
        issues.append("❌ Hay cuestionarios en BD Web pero ninguno en client_drawers")
    
    if telemetry['total_drawers'] > 0 and telemetry['total_shared_questionnaires'] == 0:
        issues.append("⚠️  Hay cajones pero sin cuestionarios")
    
    if issues:
        print("⚠️  PROBLEMAS DETECTADOS:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ VALIDACIÓN EXITOSA")
        print(f"   - Dual-write activo: {USE_CLIENT_DRAWER_WRITE}")
        print(f"   - Cajones: {telemetry['total_drawers']}")
        print(f"   - Cuestionarios en client_drawers: {telemetry['total_shared_questionnaires']}")
    
    print()
    
    client.close()


if __name__ == "__main__":
    try:
        asyncio.run(validate_dual_write())
    except KeyboardInterrupt:
        print("\n⛔ Validación interrumpida por usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
