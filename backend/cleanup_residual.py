"""
Script para limpiar registros residuales y permitir re-registro
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

async def cleanup_residual(email):
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"🧹 Limpiando registros residuales para: {email}")
    print("=" * 60)
    
    # Buscar en todas las colecciones posibles
    collections_to_check = [
        "users",
        "prospects", 
        "deleted_users",
        "nutrition_plans",
        "nutrition_questionnaire_submissions",
        "forms",
        "pdfs",
        "alerts",
        "messages"
    ]
    
    total_deleted = 0
    for coll_name in collections_to_check:
        # Buscar por email
        result = await db[coll_name].delete_many({"email": email})
        if result.deleted_count > 0:
            print(f"✅ {coll_name}: {result.deleted_count} eliminados")
            total_deleted += result.deleted_count
        
        # Buscar por email en mayúsculas (case insensitive)
        result2 = await db[coll_name].delete_many({"email": {"$regex": f"^{email}$", "$options": "i"}})
        if result2.deleted_count > 0:
            print(f"✅ {coll_name} (case insensitive): {result2.deleted_count} eliminados")
            total_deleted += result2.deleted_count
    
    print("=" * 60)
    if total_deleted > 0:
        print(f"✅ TOTAL: {total_deleted} registros eliminados")
        print(f"✅ El email {email} ahora puede registrarse de nuevo")
    else:
        print(f"✅ No se encontraron registros residuales")
        print(f"✅ El email {email} ya puede registrarse")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_residual("jorge31011987@gmail.com"))
