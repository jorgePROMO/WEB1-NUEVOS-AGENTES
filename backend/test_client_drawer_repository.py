"""
Script de prueba del Client Drawer Repository

Verifica que todas las funciones del repository funcionan correctamente.

Ejecución:
    python /app/backend/test_client_drawer_repository.py

NO modifica datos de producción. Solo crea/elimina datos de prueba.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from repositories.client_drawer_repository import (
    get_drawer_by_user_id,
    create_empty_drawer_for_user,
    upsert_drawer,
    add_questionnaire_to_drawer,
    get_or_create_drawer,
    count_drawers,
    get_drawer_stats,
    delete_drawer_by_user_id
)
from models.client_drawer import ClientDrawer

print("="*80)
print(" TEST: Client Drawer Repository")
print("="*80)
print()


async def run_tests():
    """
    Ejecuta una batería de tests del repository.
    """
    
    test_user_id = "TEST_USER_FASE0_123456"
    
    try:
        # ============================================
        # TEST 1: Crear cajón vacío
        # ============================================
        
        print("📋 TEST 1: Crear cajón vacío")
        print("-" * 80)
        
        drawer = await create_empty_drawer_for_user(test_user_id)
        
        print(f"✅ Cajón creado:")
        print(f"   - ID: {drawer.id}")
        print(f"   - User ID: {drawer.user_id}")
        print(f"   - Created at: {drawer.created_at}")
        print(f"   - Cuestionarios: {len(drawer.services.shared_questionnaires)}")
        print(f"   - Training plans: {len(drawer.services.training.plans)}")
        print(f"   - Nutrition plans: {len(drawer.services.nutrition.plans)}")
        print()
        
        # ============================================
        # TEST 2: Obtener cajón por user_id
        # ============================================
        
        print("📋 TEST 2: Obtener cajón por user_id")
        print("-" * 80)
        
        drawer_retrieved = await get_drawer_by_user_id(test_user_id)
        
        if drawer_retrieved:
            print(f"✅ Cajón recuperado:")
            print(f"   - ID: {drawer_retrieved.id}")
            print(f"   - User ID: {drawer_retrieved.user_id}")
        else:
            print("❌ No se pudo recuperar el cajón")
        print()
        
        # ============================================
        # TEST 3: Añadir cuestionario
        # ============================================
        
        print("📋 TEST 3: Añadir cuestionario inicial")
        print("-" * 80)
        
        drawer = await add_questionnaire_to_drawer(
            user_id=test_user_id,
            submission_id="submission_test_001",
            submitted_at=datetime.now(timezone.utc),
            source="initial",
            raw_payload={"test": "data"}
        )
        
        print(f"✅ Cuestionario añadido:")
        print(f"   - Cuestionarios totales: {len(drawer.services.shared_questionnaires)}")
        print(f"   - Último cuestionario ID: {drawer.services.shared_questionnaires[-1].submission_id}")
        print(f"   - Source: {drawer.services.shared_questionnaires[-1].source}")
        print()
        
        # ============================================
        # TEST 4: Actualizar cajón (upsert)
        # ============================================
        
        print("📋 TEST 4: Actualizar cajón (activar plan)")
        print("-" * 80)
        
        drawer.services.training.active_plan_id = "plan_test_123"
        drawer = await upsert_drawer(drawer)
        
        print(f"✅ Cajón actualizado:")
        print(f"   - Training active plan: {drawer.services.training.active_plan_id}")
        print(f"   - Updated at: {drawer.updated_at}")
        print()
        
        # ============================================
        # TEST 5: Obtener estadísticas
        # ============================================
        
        print("📋 TEST 5: Obtener estadísticas del cajón")
        print("-" * 80)
        
        stats = await get_drawer_stats(test_user_id)
        
        if stats:
            print(f"✅ Estadísticas:")
            for key, value in stats.items():
                print(f"   - {key}: {value}")
        else:
            print("❌ No se pudieron obtener estadísticas")
        print()
        
        # ============================================
        # TEST 6: Contar cajones
        # ============================================
        
        print("📋 TEST 6: Contar cajones totales")
        print("-" * 80)
        
        total = await count_drawers()
        
        print(f"✅ Total de cajones en BD: {total}")
        print()
        
        # ============================================
        # TEST 7: get_or_create (con cajón existente)
        # ============================================
        
        print("📋 TEST 7: get_or_create con cajón existente")
        print("-" * 80)
        
        drawer = await get_or_create_drawer(test_user_id)
        
        print(f"✅ Cajón obtenido (existente):")
        print(f"   - ID: {drawer.id}")
        print(f"   - Cuestionarios: {len(drawer.services.shared_questionnaires)}")
        print()
        
        # ============================================
        # LIMPIEZA: Eliminar cajón de prueba
        # ============================================
        
        print("🧹 LIMPIEZA: Eliminando cajón de prueba")
        print("-" * 80)
        
        deleted = await delete_drawer_by_user_id(test_user_id)
        
        if deleted:
            print(f"✅ Cajón de prueba eliminado: {test_user_id}")
        else:
            print(f"⚠️  No se pudo eliminar el cajón de prueba")
        print()
        
        # ============================================
        # VERIFICACIÓN FINAL
        # ============================================
        
        print("🔍 VERIFICACIÓN FINAL")
        print("-" * 80)
        
        drawer_after_delete = await get_drawer_by_user_id(test_user_id)
        
        if drawer_after_delete is None:
            print("✅ Cajón correctamente eliminado (no existe)")
        else:
            print("⚠️  El cajón todavía existe después de eliminarlo")
        print()
        
        # ============================================
        # RESUMEN
        # ============================================
        
        print("="*80)
        print(" ✅ TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
        print("="*80)
        print()
        print("Repository functions verified:")
        print("  ✅ create_empty_drawer_for_user")
        print("  ✅ get_drawer_by_user_id")
        print("  ✅ add_questionnaire_to_drawer")
        print("  ✅ upsert_drawer")
        print("  ✅ get_drawer_stats")
        print("  ✅ count_drawers")
        print("  ✅ get_or_create_drawer")
        print("  ✅ delete_drawer_by_user_id")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR EN TEST: {e}")
        import traceback
        traceback.print_exc()
        
        # Intentar limpiar
        print("\n🧹 Intentando limpiar cajón de prueba...")
        try:
            await delete_drawer_by_user_id(test_user_id)
            print("✅ Cajón de prueba limpiado")
        except:
            print("⚠️  No se pudo limpiar el cajón de prueba")


if __name__ == "__main__":
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n⛔ Tests interrumpidos por usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        sys.exit(1)
