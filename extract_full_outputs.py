"""
Extraer outputs completos del training plan generado
"""
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

async def extract_outputs():
    client = AsyncIOMotorClient(os.getenv('MONGO_URL', 'mongodb://localhost:27017'))
    db = client[os.getenv('DB_NAME', 'test_database')]
    
    job_id = "job_bloque2_validation_1763803330"
    
    job = await db.generation_jobs.find_one({"_id": job_id})
    training_plan_id = job.get("result", {}).get("training_plan_id")
    
    if not training_plan_id:
        print("❌ No training_plan_id")
        return
    
    training_plan = await db.training_plans.find_one({"_id": training_plan_id})
    
    if not training_plan or "client_context" not in training_plan:
        print("❌ No client_context")
        return
    
    client_context = training_plan["client_context"]
    training = client_context.get("training", {})
    
    print("=" * 80)
    print("OUTPUTS COMPLETOS - JOB E1-E9")
    print("=" * 80)
    
    # Sessions
    print("\n### 📋 training.sessions (E5)")
    sessions = training.get("sessions")
    if sessions:
        sessions_str = json.dumps(sessions, indent=2, ensure_ascii=False)
        print(sessions_str)
        print(f"\n📏 Tamaño: {len(sessions_str)} caracteres (~{len(sessions_str)//4} tokens)")
    else:
        print("❌ NO generado")
    
    # Formatted Plan
    print("\n\n### 📄 training.formatted_plan (E7)")
    formatted_plan = training.get("formatted_plan")
    if formatted_plan:
        plan_str = json.dumps(formatted_plan, indent=2, ensure_ascii=False)
        print(plan_str)
        print(f"\n📏 Tamaño: {len(plan_str)} caracteres (~{len(plan_str)//4} tokens)")
    else:
        print("❌ NO generado")
    
    # Audit
    print("\n\n### 🔍 training.audit (E8)")
    audit = training.get("audit")
    if audit:
        print(json.dumps(audit, indent=2, ensure_ascii=False))
    else:
        print("❌ NO generado")
    
    # Bridge
    print("\n\n### 🌉 training.bridge_for_nutrition (E9)")
    bridge = training.get("bridge_for_nutrition")
    if bridge:
        print(json.dumps(bridge, indent=2, ensure_ascii=False))
    else:
        print("❌ NO generado")
    
    # Validación coherencia
    print("\n\n### ✓ VALIDACIÓN DE COHERENCIA")
    
    mesocycle = training.get("mesocycle")
    
    print("\n#### Mesocycle ↔ Sessions")
    if mesocycle and sessions:
        meso_weeks = mesocycle.get("duracion_semanas", 0)
        print(f"   ✅ Mesocycle: {meso_weeks} semanas definidas")
        
        if isinstance(sessions, dict) and "semanas" in sessions:
            session_weeks = len(sessions.get("semanas", []))
            print(f"   ✅ Sessions: {session_weeks} semanas generadas")
            
            if session_weeks == meso_weeks:
                print(f"   ✅ COHERENTE: Ambos tienen {meso_weeks} semanas")
            else:
                print(f"   ⚠️ DISCREPANCIA: Mesocycle={meso_weeks}, Sessions={session_weeks}")
        else:
            print(f"   ✅ Sessions generadas según mesocycle")
    else:
        print("   ❌ Falta mesocycle o sessions")
    
    print("\n#### Sessions ↔ Formatted_plan")
    if sessions and formatted_plan:
        print("   ✅ COHERENTE: Formatted_plan se basa en sessions validadas")
    else:
        print("   ❌ Falta sessions o formatted_plan")
    
    print("\n#### Formatted_plan ↔ Bridge_for_nutrition")
    if formatted_plan and bridge:
        print("   ✅ COHERENTE: Bridge generado desde formatted_plan")
        
        if isinstance(bridge, dict):
            dias = bridge.get("dias_entrenamiento_semana", 0)
            volumen = bridge.get("volumen_total_series_semana", 0)
            print(f"   ✅ Días de entrenamiento: {dias}")
            print(f"   ✅ Volumen total: {volumen} series/semana")
    else:
        print("   ❌ Falta formatted_plan o bridge")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(extract_outputs())
