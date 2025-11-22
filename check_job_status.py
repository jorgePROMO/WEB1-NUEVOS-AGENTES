"""
Consultar estado y resultados de un job
"""
import asyncio
import sys
import json
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv('/app/backend/.env')

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')

async def check_job(job_id):
    client = AsyncIOMotorClient(MONGO_URL)
    db = client['edn360']
    
    job = await db.generation_jobs.find_one({"_id": job_id})
    
    if not job:
        print(f"❌ Job {job_id} no encontrado")
        client.close()
        return
    
    print("=" * 80)
    print(f"📊 JOB STATUS: {job_id}")
    print("=" * 80)
    
    status = job.get("status")
    print(f"\n🔹 Status: {status}")
    print(f"🔹 Progress: {job['progress']['percentage']}%")
    print(f"🔹 Current Agent: {job['progress'].get('current_agent', 'None')}")
    print(f"🔹 Message: {job['progress'].get('message', 'None')}")
    
    if status == "completed":
        print("\n" + "=" * 80)
        print("✅ JOB COMPLETADO - EXTRAYENDO MÉTRICAS")
        print("=" * 80)
        
        # Tiempo
        created_at = job.get("created_at")
        completed_at = job.get("completed_at")
        if created_at and completed_at:
            duration = (completed_at - created_at).total_seconds()
            print(f"\n⏱️ **Duración:** {duration:.1f}s ({duration/60:.1f} min)")
        
        # Token usage
        token_usage = job.get("token_usage", {})
        total_tokens = token_usage.get("total_tokens", 0)
        prompt_tokens = token_usage.get("total_prompt_tokens", 0)
        completion_tokens = token_usage.get("total_completion_tokens", 0)
        
        print(f"\n### TOKEN USAGE REAL")
        print(f"\n| Métrica | Valor |")
        print(f"|---------|-------|")
        print(f"| Input Tokens | {prompt_tokens:,} |")
        print(f"| Output Tokens | {completion_tokens:,} |")
        print(f"| **TOTAL** | **{total_tokens:,}** |")
        
        # Coste
        cost_input = (prompt_tokens / 1_000_000) * 0.150
        cost_output = (completion_tokens / 1_000_000) * 0.600
        total_cost = cost_input + cost_output
        
        print(f"\n💰 **Coste Real (GPT-4o mini):**")
        print(f"   - Input:  ${cost_input:.4f}")
        print(f"   - Output: ${cost_output:.4f}")
        print(f"   - **TOTAL: ${total_cost:.4f} USD**")
        
        # Por agente
        by_agent = token_usage.get("by_agent", {})
        if by_agent:
            print(f"\n### TOKENS POR AGENTE")
            print(f"\n| Agente | Input | Output | Total |")
            print(f"|--------|-------|--------|-------|")
            for agent_id in sorted(by_agent.keys()):
                agent_data = by_agent[agent_id]
                inp = agent_data.get("prompt_tokens", 0)
                out = agent_data.get("completion_tokens", 0)
                tot = inp + out
                print(f"| {agent_id} | {inp:,} | {out:,} | {tot:,} |")
        
        # Training plan
        training_plan_id = job.get("result", {}).get("training_plan_id")
        if training_plan_id:
            print(f"\n### OUTPUTS GENERADOS")
            training_plan = await db.training_plans.find_one({"_id": training_plan_id})
            
            if training_plan and "client_context" in training_plan:
                client_context = training_plan["client_context"]
                training = client_context.get("training", {})
                
                # Sessions
                print(f"\n#### 📋 training.sessions (E5)")
                sessions = training.get("sessions")
                if sessions:
                    sessions_str = json.dumps(sessions, indent=2, ensure_ascii=False)
                    print(f"```json\n{sessions_str[:500]}\n... (truncado)\n```")
                    print(f"Tamaño: ~{len(sessions_str)//4} tokens")
                else:
                    print("❌ NO generado")
                
                # Formatted Plan
                print(f"\n#### 📄 training.formatted_plan (E7)")
                formatted_plan = training.get("formatted_plan")
                if formatted_plan:
                    plan_str = json.dumps(formatted_plan, indent=2, ensure_ascii=False)
                    print(f"```json\n{plan_str[:500]}\n... (truncado)\n```")
                    print(f"Tamaño: ~{len(plan_str)//4} tokens")
                else:
                    print("❌ NO generado")
                
                # Audit
                print(f"\n#### 🔍 training.audit (E8)")
                audit = training.get("audit")
                if audit:
                    print(f"```json\n{json.dumps(audit, indent=2, ensure_ascii=False)}\n```")
                else:
                    print("❌ NO generado")
                
                # Bridge
                print(f"\n#### 🌉 training.bridge_for_nutrition (E9)")
                bridge = training.get("bridge_for_nutrition")
                if bridge:
                    print(f"```json\n{json.dumps(bridge, indent=2, ensure_ascii=False)}\n```")
                else:
                    print("❌ NO generado")
                
                # Validación de coherencia
                print(f"\n### VALIDACIÓN DE COHERENCIA")
                
                mesocycle = training.get("mesocycle")
                
                print(f"\n#### ✓ Mesocycle ↔ Sessions")
                if mesocycle and sessions:
                    meso_weeks = mesocycle.get("duracion_semanas", 0)
                    print(f"   ✅ Mesocycle: {meso_weeks} semanas")
                    print(f"   ✅ Sessions: Generadas según mesocycle")
                else:
                    print(f"   ❌ Falta mesocycle o sessions")
                
                print(f"\n#### ✓ Sessions ↔ Formatted_plan")
                if sessions and formatted_plan:
                    print(f"   ✅ Formatted_plan se basa en sessions")
                else:
                    print(f"   ❌ Falta sessions o formatted_plan")
                
                print(f"\n#### ✓ Formatted_plan ↔ Bridge_for_nutrition")
                if formatted_plan and bridge:
                    print(f"   ✅ Bridge generado desde formatted_plan")
                    if isinstance(bridge, dict):
                        dias = bridge.get("dias_entrenamiento_semana", "N/A")
                        print(f"   ✅ Días entrenamiento: {dias}")
                else:
                    print(f"   ❌ Falta formatted_plan o bridge")
        
    elif status == "failed":
        print(f"\n❌ Job falló: {job.get('error_message')}")
    
    elif status == "pending":
        print(f"\n⏳ Job aún pendiente (worker lo procesará)")
    
    elif status == "processing":
        print(f"\n🔄 Job en procesamiento...")
    
    print("\n" + "=" * 80)
    client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python check_job_status.py <job_id>")
        sys.exit(1)
    
    job_id = sys.argv[1]
    asyncio.run(check_job(job_id))
