"""
Script para limpiar TODA la base de datos excepto el admin
USO: python cleanup_database.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

async def cleanup_database():
    """Borra TODOS los datos excepto el usuario admin"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print("🚨 INICIANDO LIMPIEZA TOTAL DE BASE DE DATOS...")
    print("=" * 60)
    
    # 1. Obtener admin antes de borrar
    admin = await db.users.find_one({"email": "ecjtrainer@gmail.com"})
    if not admin:
        print("❌ ERROR: No se encontró el usuario admin!")
        return
    
    admin_id = admin["_id"]
    print(f"✅ Admin encontrado: {admin['email']} (ID: {admin_id})")
    print()
    
    # 2. Borrar todos los usuarios EXCEPTO el admin
    result = await db.users.delete_many({"_id": {"$ne": admin_id}})
    print(f"✅ Usuarios eliminados: {result.deleted_count}")
    
    # 3. Borrar TODOS los datos de todas las colecciones
    collections = [
        ("nutrition_plans", "Planes de nutrición"),
        ("nutrition_questionnaire_submissions", "Respuestas de cuestionarios"),
        ("forms", "Formularios"),
        ("alerts", "Alertas"),
        ("messages", "Mensajes"),
        ("sessions", "Sesiones"),
        ("pdfs", "PDFs"),
        ("prospects", "Prospectos"),
        ("templates", "Templates"),
        ("deleted_users", "Usuarios eliminados (log)"),
        ("user_sessions", "Sesiones de usuario")
    ]
    
    for collection_name, description in collections:
        result = await db[collection_name].delete_many({})
        print(f"✅ {description}: {result.deleted_count} eliminados")
    
    print()
    print("=" * 60)
    print("✅ LIMPIEZA COMPLETA!")
    print(f"✅ Admin preservado: {admin['email']}")
    print("=" * 60)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(cleanup_database())
