"""
Script temporal para forzar el dual-write de un cuestionario existente.

Uso: python force_dual_write.py
"""
import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from repositories.client_drawer_repository import add_questionnaire_to_drawer

# Configuración
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
MONGO_WEB_DB_NAME = os.getenv('MONGO_WEB_DB_NAME', 'test_database')

# Cliente MongoDB
client = AsyncIOMotorClient(MONGO_URL)
db_web = client[MONGO_WEB_DB_NAME]

# Datos del cuestionario a forzar
USER_ID = "1764016044644335"
SUBMISSION_ID = "1764016775848319"


async def force_dual_write():
    """Fuerza el dual-write del cuestionario existente."""
    
    print(f"🔍 Buscando cuestionario {SUBMISSION_ID} para user_id {USER_ID}...")
    
    # Buscar el cuestionario en BD Web
    submission_doc = await db_web.nutrition_questionnaire_submissions.find_one(
        {"_id": SUBMISSION_ID}
    )
    
    if not submission_doc:
        print(f"❌ Cuestionario {SUBMISSION_ID} no encontrado en BD Web")
        return False
    
    print(f"✅ Cuestionario encontrado")
    print(f"   - Submitted at: {submission_doc['submitted_at']}")
    print(f"   - User ID: {submission_doc['user_id']}")
    
    # Extraer datos
    submitted_at = submission_doc['submitted_at']
    
    print(f"\n🔄 Forzando dual-write a client_drawers...")
    
    try:
        # Llamar a add_questionnaire_to_drawer
        await add_questionnaire_to_drawer(
            user_id=USER_ID,
            submission_id=SUBMISSION_ID,
            submitted_at=submitted_at,
            source="initial",  # Cuestionario inicial (ya corregido)
            raw_payload=submission_doc  # Documento completo
        )
        
        print(f"✅ Dual-write forzado exitosamente!")
        print(f"   - submission_id: {SUBMISSION_ID}")
        print(f"   - source: initial")
        print(f"   - submitted_at: {submitted_at}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error forzando dual-write: {e}")
        import traceback
        traceback.print_exc()
        return False


async def verify_dual_write():
    """Verifica que el cuestionario se guardó en client_drawers."""
    
    print(f"\n🔍 Verificando que el cuestionario se guardó en client_drawers...")
    
    from repositories.client_drawer_repository import get_drawer_by_user_id
    
    drawer = await get_drawer_by_user_id(USER_ID)
    
    if not drawer:
        print(f"❌ No se encontró client_drawer para user_id {USER_ID}")
        return False
    
    print(f"✅ Client_drawer encontrado: {drawer.id}")
    
    questionnaires = drawer.services.shared_questionnaires
    
    if not questionnaires:
        print(f"❌ El drawer no tiene cuestionarios")
        return False
    
    print(f"✅ Cuestionarios en drawer: {len(questionnaires)}")
    
    for i, q in enumerate(questionnaires):
        print(f"\n   Cuestionario {i+1}:")
        print(f"   - submission_id: {q.submission_id}")
        print(f"   - source: {q.source}")
        print(f"   - submitted_at: {q.submitted_at}")
        print(f"   - tiene payload: {bool(q.raw_payload)}")
    
    # Verificar que nuestro cuestionario está ahí
    found = any(q.submission_id == SUBMISSION_ID for q in questionnaires)
    
    if found:
        print(f"\n✅ El cuestionario {SUBMISSION_ID} está en client_drawers")
        return True
    else:
        print(f"\n❌ El cuestionario {SUBMISSION_ID} NO está en client_drawers")
        return False


async def main():
    """Función principal."""
    
    print("=" * 60)
    print("FORZAR DUAL-WRITE DE CUESTIONARIO EXISTENTE")
    print("=" * 60)
    print()
    
    # Paso 1: Forzar dual-write
    success = await force_dual_write()
    
    if not success:
        print("\n❌ No se pudo forzar el dual-write")
        return
    
    # Paso 2: Verificar
    verified = await verify_dual_write()
    
    if verified:
        print("\n" + "=" * 60)
        print("✅ DUAL-WRITE FORZADO Y VERIFICADO EXITOSAMENTE")
        print("=" * 60)
        print("\nAhora puedes lanzar el Workflow EDN360 y debería incluir el cuestionario.")
    else:
        print("\n" + "=" * 60)
        print("⚠️  DUAL-WRITE FORZADO PERO VERIFICACIÓN FALLÓ")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
