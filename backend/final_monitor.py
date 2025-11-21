#!/usr/bin/env python3
"""
Monitor continuo hasta finalización de los 3 jobs
Genera reporte completo automáticamente
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import json

JOB_IDS = [
    "job_1762976907472415_1763737932266551",
    "job_1762976907472415_1763737932367356",
    "job_1762976907472415_1763737932468476"
]

async def monitor_until_complete():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_database
    
    print(f"🔍 MONITOREO CONTINUO INICIADO")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📋 Monitoreando 3 jobs hasta finalización completa")
    print("=" * 100)
    
    iteration = 0
    last_status = {}
    
    while True:
        iteration += 1
        jobs = await db.generation_jobs.find({"_id": {"$in": JOB_IDS}}).to_list(length=3)
        
        # Status line compacto
        status_parts = []
        all_done = True
        
        for i, job in enumerate(sorted(jobs, key=lambda x: JOB_IDS.index(x["_id"])), 1):
            status = job["status"]
            agent = job.get("progress", {}).get("current_agent") or "--"
            steps = job.get("progress", {}).get("completed_steps", 0)
            
            emoji = "✅" if status == "completed" else "❌" if status == "failed" else "🔄"
            status_parts.append(f"{emoji}J{i}:{agent}({steps}/18)")
            
            # Detectar cambios significativos
            job_key = f"J{i}"
            current = f"{status}:{agent}:{steps}"
            if last_status.get(job_key) != current:
                if steps > 0 or status in ["completed", "failed"]:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] {emoji} JOB {i}: {status.upper()} - {agent} - {steps}/18 steps")
                last_status[job_key] = current
            
            if status not in ["completed", "failed"]:
                all_done = False
        
        # Mostrar estado cada 10 iteraciones (1 min)
        if iteration % 10 == 0:
            print(f"\r[{datetime.now().strftime('%H:%M:%S')}] {' | '.join(status_parts)}", flush=True)
        
        if all_done:
            print("\n" + "=" * 100)
            print(f"✅ TODOS LOS JOBS FINALIZADOS - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 100)
            break
        
        await asyncio.sleep(6)  # Check cada 6 segundos
    
    # GENERAR REPORTE COMPLETO
    print("\n📊 Generando reporte completo...\n")
    
    report_data = {
        "generation_timestamp": datetime.now().isoformat(),
        "jobs": []
    }
    
    for i, job_id in enumerate(JOB_IDS, 1):
        job = await db.generation_jobs.find_one({"_id": job_id})
        
        job_report = {
            "job_number": i,
            "job_id": job_id,
            "status": job["status"],
            "type": job["type"],
            "created_at": job["created_at"].isoformat() if job.get("created_at") else None,
            "started_at": job["started_at"].isoformat() if job.get("started_at") else None,
            "completed_at": job["completed_at"].isoformat() if job.get("completed_at") else None,
            "duration_minutes": None,
            "progress": {
                "completed_steps": job.get("progress", {}).get("completed_steps", 0),
                "total_steps": job.get("progress", {}).get("total_steps", 18),
                "percentage": job.get("progress", {}).get("percentage", 0)
            },
            "token_usage": {
                "total_prompt_tokens": 0,
                "total_completion_tokens": 0,
                "total_tokens": 0,
                "by_agent": {}
            },
            "retry_count": job.get("retry_count", 0),
            "error_message": job.get("error_message"),
            "error_reason": job.get("error_reason"),
            "result": job.get("result", {})
        }
        
        # Calcular duración
        if job.get("started_at") and job.get("completed_at"):
            duration = (job["completed_at"] - job["started_at"]).total_seconds() / 60
            job_report["duration_minutes"] = round(duration, 2)
        
        # Token usage
        if "token_usage" in job:
            tu = job["token_usage"]
            job_report["token_usage"] = {
                "total_prompt_tokens": tu.get("total_prompt_tokens", 0),
                "total_completion_tokens": tu.get("total_completion_tokens", 0),
                "total_tokens": tu.get("total_tokens", 0),
                "by_agent": tu.get("by_agent", {})
            }
        
        report_data["jobs"].append(job_report)
    
    # Calcular métricas agregadas
    completed_jobs = [j for j in report_data["jobs"] if j["status"] == "completed"]
    failed_jobs = [j for j in report_data["jobs"] if j["status"] == "failed"]
    
    report_data["summary"] = {
        "total_jobs": len(report_data["jobs"]),
        "completed": len(completed_jobs),
        "failed": len(failed_jobs),
        "success_rate": round(len(completed_jobs) / len(report_data["jobs"]) * 100, 2) if report_data["jobs"] else 0
    }
    
    if completed_jobs:
        durations = [j["duration_minutes"] for j in completed_jobs if j["duration_minutes"]]
        tokens = [j["token_usage"]["total_tokens"] for j in completed_jobs]
        
        if durations:
            report_data["summary"]["duration"] = {
                "average_minutes": round(sum(durations) / len(durations), 2),
                "min_minutes": round(min(durations), 2),
                "max_minutes": round(max(durations), 2)
            }
        
        if tokens:
            report_data["summary"]["tokens"] = {
                "average_total": round(sum(tokens) / len(tokens), 0),
                "min_total": min(tokens),
                "max_total": max(tokens),
                "total_consumed": sum(tokens)
            }
            
            # Calcular coste estimado (GPT-4o pricing)
            total_prompt = sum(j["token_usage"]["total_prompt_tokens"] for j in completed_jobs)
            total_completion = sum(j["token_usage"]["total_completion_tokens"] for j in completed_jobs)
            
            cost_prompt = total_prompt * 2.50 / 1_000_000
            cost_completion = total_completion * 10.00 / 1_000_000
            cost_total = cost_prompt + cost_completion
            
            report_data["summary"]["cost_estimate_usd"] = {
                "prompt_cost": round(cost_prompt, 4),
                "completion_cost": round(cost_completion, 4),
                "total_cost": round(cost_total, 4),
                "average_per_job": round(cost_total / len(completed_jobs), 4) if completed_jobs else 0
            }
    
    # Guardar reporte
    report_path = "/app/backend/final_report.json"
    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Reporte guardado en: {report_path}")
    print(f"📊 Jobs completados: {report_data['summary']['completed']}/{report_data['summary']['total_jobs']}")
    
    if completed_jobs:
        print(f"⏱️  Duración promedio: {report_data['summary']['duration']['average_minutes']:.2f} min")
        print(f"💰 Tokens totales: {report_data['summary']['tokens']['total_consumed']:,}")
        print(f"💵 Coste total estimado: ${report_data['summary']['cost_estimate_usd']['total_cost']:.4f}")
    
    return report_path

if __name__ == "__main__":
    try:
        report_path = asyncio.run(monitor_until_complete())
        print(f"\n✅ MONITOREO COMPLETADO")
        print(f"📄 Reporte disponible en: {report_path}")
    except KeyboardInterrupt:
        print("\n⛔ Monitoreo interrumpido por usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
