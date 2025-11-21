#!/usr/bin/env python3
"""
Monitor de jobs de validación
Rastrea el progreso de los 3 jobs FULL y genera reporte final
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import json

JOB_IDS = [
    "job_1762976907472415_1763736853661810",
    "job_1762976907472415_1763736853762441",
    "job_1762976907472415_1763736853863774"
]

async def monitor():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_database
    
    print("📊 MONITOREANDO 3 JOBS FULL CONSECUTIVOS")
    print("=" * 100)
    print(f"Inicio: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    iteration = 0
    while True:
        iteration += 1
        jobs = await db.generation_jobs.find({"_id": {"$in": JOB_IDS}}).to_list(length=3)
        
        # Status line
        status_parts = []
        for i, job in enumerate(sorted(jobs, key=lambda x: JOB_IDS.index(x["_id"])), 1):
            status = job["status"]
            agent = job.get("progress", {}).get("current_agent", "--")
            steps = job.get("progress", {}).get("completed_steps", 0)
            total = job.get("progress", {}).get("total_steps", 18)
            
            emoji = "✅" if status == "completed" else "❌" if status == "failed" else "🔄"
            status_parts.append(f"{emoji}J{i}:{agent}({steps}/{total})")
        
        print(f"\r[{datetime.now().strftime('%H:%M:%S')}] {' | '.join(status_parts)}", end="", flush=True)
        
        # Check if all done
        all_done = all(j["status"] in ["completed", "failed"] for j in jobs)
        if all_done:
            print("\n\n" + "=" * 100)
            print("✅ TODOS LOS JOBS FINALIZADOS")
            print("=" * 100)
            break
        
        await asyncio.sleep(10)  # Check cada 10 segundos
    
    # REPORTE FINAL
    print("\n📋 REPORTE FINAL DE VALIDACIÓN FASE A\n")
    
    for i, job_id in enumerate(JOB_IDS, 1):
        job = await db.generation_jobs.find_one({"_id": job_id})
        
        print(f"\n{'='*100}")
        print(f"JOB {i}: {job_id}")
        print(f"{'='*100}")
        
        print(f"\n📊 GENERAL:")
        print(f"   Status: {job['status']}")
        print(f"   Type: {job['type']}")
        print(f"   Steps: {job.get('progress', {}).get('completed_steps')}/{job.get('progress', {}).get('total_steps')}")
        
        print(f"\n⏱️  TIEMPOS:")
        if job.get('created_at'):
            print(f"   Created: {job['created_at']}")
        if job.get('started_at'):
            print(f"   Started: {job['started_at']}")
        if job.get('completed_at'):
            print(f"   Completed: {job['completed_at']}")
            if job.get('started_at'):
                duration = (job['completed_at'] - job['started_at']).total_seconds() / 60
                print(f"   ⏱️  Duration: {duration:.2f} minutes")
        
        print(f"\n💰 TOKEN USAGE:")
        if 'token_usage' in job:
            tu = job['token_usage']
            print(f"   Prompt tokens: {tu.get('total_prompt_tokens', 0):,}")
            print(f"   Completion tokens: {tu.get('total_completion_tokens', 0):,}")
            print(f"   Total tokens: {tu.get('total_tokens', 0):,}")
            
            # Top 3 agentes por tokens
            by_agent = tu.get('by_agent', {})
            if by_agent:
                sorted_agents = sorted(by_agent.items(), key=lambda x: x[1].get('total_tokens', 0), reverse=True)
                print(f"\n   Top 3 agentes por tokens:")
                for agent_id, tokens in sorted_agents[:3]:
                    print(f"      {agent_id}: {tokens.get('total_tokens', 0):,} tokens")
        
        print(f"\n🔄 REINTENTOS:")
        print(f"   Retry count: {job.get('retry_count', 0)}")
        
        if job.get('error_message'):
            print(f"\n❌ ERROR:")
            print(f"   {job['error_message']}")
            print(f"   Reason: {job.get('error_reason', 'N/A')}")
        
        if job['status'] == 'completed':
            print(f"\n✅ RESULTADO:")
            result = job.get('result', {})
            print(f"   Training plan ID: {result.get('training_plan_id', 'N/A')}")
            print(f"   Nutrition plan ID: {result.get('nutrition_plan_id', 'N/A')}")
    
    # RESUMEN COMPARATIVO
    print(f"\n\n{'='*100}")
    print("📊 RESUMEN COMPARATIVO")
    print(f"{'='*100}\n")
    
    jobs = await db.generation_jobs.find({"_id": {"$in": JOB_IDS}}).to_list(length=3)
    
    completed = [j for j in jobs if j['status'] == 'completed']
    failed = [j for j in jobs if j['status'] == 'failed']
    
    print(f"✅ Completados: {len(completed)}/3")
    print(f"❌ Fallados: {len(failed)}/3")
    
    if completed:
        durations = []
        total_tokens_list = []
        
        for job in completed:
            if job.get('started_at') and job.get('completed_at'):
                duration = (job['completed_at'] - job['started_at']).total_seconds() / 60
                durations.append(duration)
            
            if 'token_usage' in job:
                total_tokens_list.append(job['token_usage'].get('total_tokens', 0))
        
        if durations:
            print(f"\n⏱️  Tiempo promedio: {sum(durations)/len(durations):.2f} min")
            print(f"   Tiempo mínimo: {min(durations):.2f} min")
            print(f"   Tiempo máximo: {max(durations):.2f} min")
        
        if total_tokens_list:
            print(f"\n💰 Tokens promedio: {sum(total_tokens_list)/len(total_tokens_list):,.0f}")
            print(f"   Tokens mínimo: {min(total_tokens_list):,}")
            print(f"   Tokens máximo: {max(total_tokens_list):,}")
    
    print(f"\n{'='*100}\n")

if __name__ == "__main__":
    asyncio.run(monitor())
