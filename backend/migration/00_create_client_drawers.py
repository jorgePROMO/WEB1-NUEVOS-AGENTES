"""
Script de inicialización - FASE 0

Crea la colección client_drawers en la BD EDN360_APP con índices necesarios.

NO migra datos históricos. Solo prepara la infraestructura.

Ejecución:
    python /app/backend/migration/00_create_client_drawers.py

Referencia: DOCUMENTO_3_V2_MANUAL_OPERATIVO_MIGRACION.md - Fase 0
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

# Configuración de BDs
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
MONGO_EDN360_APP_DB_NAME = os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')

print("="*80)
print(" FASE 0: Creación de Colección client_drawers")
print("="*80)
print()
print(f"📊 Configuración:")
print(f"   - MongoDB URL: {MONGO_URL}")
print(f"   - BD EDN360_APP: {MONGO_EDN360_APP_DB_NAME}")
print()


async def create_collection_and_indexes():
    """
    Crea la colección client_drawers y sus índices necesarios.
    """
    
    # Conectar a MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_EDN360_APP_DB_NAME]
    
    print("🔗 Conectado a MongoDB")
    print()
    
    # ============================================
    # 1. Crear colección client_drawers
    # ============================================
    
    collections = await db.list_collection_names()
    
    if "client_drawers" in collections:
        print("⚠️  La colección 'client_drawers' ya existe")
        print()
    else:
        # Crear colección explícitamente
        await db.create_collection("client_drawers")
        print("✅ Colección 'client_drawers' creada")
        print()
    
    # ============================================
    # 2. Crear índices
    # ============================================
    
    print("📋 Creando índices...")
    print()
    
    collection = db.client_drawers
    
    # Índice 1: user_id (ÚNICO)
    # Garantiza que cada usuario tiene un único cajón
    try:
        await collection.create_index(
            "user_id",
            unique=True,
            name="idx_user_id_unique"
        )
        print("✅ Índice creado: user_id (único)")
    except Exception as e:
        print(f"⚠️  Índice user_id ya existe o error: {e}")
    
    # Índice 2: created_at
    # Para ordenar cajones por fecha de creación
    try:
        await collection.create_index(
            "created_at",
            name="idx_created_at"
        )
        print("✅ Índice creado: created_at")
    except Exception as e:
        print(f"⚠️  Índice created_at ya existe o error: {e}")
    
    # Índice 3: updated_at
    # Para ordenar por última actualización
    try:
        await collection.create_index(
            "updated_at",
            name="idx_updated_at"
        )
        print("✅ Índice creado: updated_at")
    except Exception as e:
        print(f"⚠️  Índice updated_at ya existe o error: {e}")
    
    # Índice 4: services.shared_questionnaires.submission_id
    # Para búsquedas rápidas por cuestionario
    try:
        await collection.create_index(
            "services.shared_questionnaires.submission_id",
            name="idx_questionnaire_submission"
        )
        print("✅ Índice creado: services.shared_questionnaires.submission_id")
    except Exception as e:
        print(f"⚠️  Índice questionnaire_submission ya existe o error: {e}")
    
    print()
    
    # ============================================
    # 3. Listar índices existentes
    # ============================================
    
    print("📊 Índices existentes en client_drawers:")
    print()
    
    indexes = await collection.list_indexes().to_list(length=100)
    
    for idx in indexes:
        name = idx.get('name')
        keys = idx.get('key')
        unique = idx.get('unique', False)
        
        unique_str = " (ÚNICO)" if unique else ""
        print(f"   - {name}: {keys}{unique_str}")
    
    print()
    
    # ============================================
    # 4. Estadísticas de la colección
    # ============================================
    
    count = await collection.count_documents({})
    
    print("📊 Estadísticas de client_drawers:")
    print(f"   - Documentos: {count}")
    print()
    
    if count == 0:
        print("ℹ️  La colección está vacía (correcto en FASE 0)")
        print("   Los datos históricos se migrarán en fases posteriores.")
    
    print()
    
    # ============================================
    # 5. Crear documento de prueba (opcional)
    # ============================================
    
    # Preguntar si se desea crear documento de prueba
    print("❓ ¿Deseas crear 1 documento de prueba? (s/n): ", end="")
    # En script automático, por defecto NO
    create_test = False  # Cambiar a True si se desea crear automáticamente
    
    if create_test:
        test_drawer = {
            "_id": "client_TEST_USER_123",
            "user_id": "TEST_USER_123",
            "services": {
                "shared_questionnaires": [],
                "training": {
                    "active_plan_id": None,
                    "plans": [],
                    "snapshots": []
                },
                "nutrition": {
                    "active_plan_id": None,
                    "plans": [],
                    "snapshots": []
                }
            },
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        try:
            await collection.insert_one(test_drawer)
            print("✅ Documento de prueba creado: client_TEST_USER_123")
        except Exception as e:
            print(f"⚠️  Error creando documento de prueba: {e}")
    else:
        print("⏭️  Saltando creación de documento de prueba")
    
    print()
    
    # Cerrar conexión
    client.close()
    
    print("="*80)
    print(" ✅ FASE 0 COMPLETADA")
    print("="*80)
    print()
    print("Siguiente paso:")
    print("  - FASE 1: Implementar client_drawer_repository.py")
    print("  - FASE 2: Configurar dual-write en endpoints de cuestionarios")
    print()


if __name__ == "__main__":
    try:
        asyncio.run(create_collection_and_indexes())
    except KeyboardInterrupt:
        print("\n⛔ Script interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
