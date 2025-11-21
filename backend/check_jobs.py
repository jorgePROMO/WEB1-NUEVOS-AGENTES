#!/usr/bin/env python3
"""Quick job status checker"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

JOB_IDS = [
    "job_1762976907472415_1763737932266551",
    "job_1762976907472415_1763737932367356",
    "job_1762976907472415_1763737932468476"
]

async def check():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.test_database
    
    jobs = await db.generation_jobs.find({"_id": {"$in": JOB_IDS}}).to_list(length=3)
    
    all_done = True
    statuses = []
    
    for i, job in enumerate(sorted(jobs, key=lambda x: JOB_IDS.index(x["_id"])), 1):
        status = job["status"]
        agent = job.get("progress", {}).get("current_agent") or "--"
        steps = job.get("progress", {}).get("completed_steps", 0)
        percentage = job.get("progress", {}).get("percentage", 0)
        
        emoji = "✅" if status == "completed" else "❌" if status == "failed" else "🔄"
        statuses.append(f"{emoji}J{i}:{status[:3]}({agent},{steps}/18,{percentage}%)")
        
        if status not in ["completed", "failed"]:
            all_done = False
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {' | '.join(statuses)}")
    print(f"DONE:{all_done}")

asyncio.run(check())
