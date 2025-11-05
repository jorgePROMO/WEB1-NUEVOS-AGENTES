"""
Script para verificar manualmente el email de un usuario
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

async def check_and_fix_verification(email):
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    print(f"🔍 Buscando usuario: {email}")
    user = await db.users.find_one({"email": email})
    
    if not user:
        print(f"❌ Usuario no encontrado: {email}")
        client.close()
        return
    
    print(f"\n✅ Usuario encontrado:")
    print(f"  - ID: {user['_id']}")
    print(f"  - Username: {user.get('username')}")
    print(f"  - Email verificado: {user.get('email_verified', False)}")
    print(f"  - Token de verificación: {user.get('verification_token', 'No tiene')[:20]}...")
    print(f"  - Token expira: {user.get('verification_token_expires_at')}")
    
    if user.get('email_verified'):
        print(f"\n✅ El email ya está verificado!")
    else:
        print(f"\n⚠️ El email NO está verificado. ¿Verificar manualmente? (s/n)")
        # Auto-verificar para este script
        print("Verificando automáticamente...")
        
        result = await db.users.update_one(
            {"_id": user["_id"]},
            {
                "$set": {
                    "email_verified": True,
                    "verification_token": None,
                    "verification_token_expires_at": None,
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        if result.modified_count > 0:
            print("✅ Email verificado manualmente!")
        else:
            print("❌ Error al verificar")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_and_fix_verification("jorge31011987@gmail.com"))
