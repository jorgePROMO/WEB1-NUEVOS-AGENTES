"""
EJECUTAR JOB REAL - VALIDACIÓN BLOQUE 1
Crea un cuestionario realista y ejecuta un job completo de training
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys

sys.path.append('/app/backend')

from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client['edn360']

async def create_realistic_questionnaire():
    """Crea un cuestionario realista para el test"""
    print("📝 Creando cuestionario realista...")
    
    timestamp = int(time.time())
    quest_id = f"quest_bloque1_{timestamp}"
    
    questionnaire = {
        "_id": quest_id,
        "user_id": "user_test_bloque1",
        "created_at": datetime.now(timezone.utc),
        
        # Datos básicos
        "nombre_completo": "Carlos Martínez Ruiz",
        "email": "carlos.martinez@test.com",
        "fecha_nacimiento": "1988-03-20",
        "sexo": "hombre",
        "profesion": "Arquitecto - trabajo de oficina",
        "telefono": "+34 612 345 678",
        
        # Medidas
        "peso": "82",
        "altura_cm": "178",
        "grasa_porcentaje": "22",
        "cintura_cm": "88",
        
        # Salud
        "medicamentos": "Ninguno",
        "enfermedad_cronica": "No",
        "fuma_cantidad": "No fumo",
        "bebe_cantidad": "Ocasionalmente, fines de semana",
        "retencion_liquidos": "No",
        "problemas_corazon": "No",
        "hipertension": "No",
        "diabetes": "No",
        "colesterol": "Normal",
        "sobrepeso": "Ligero sobrepeso según IMC",
        
        # Experiencia
        "experiencia_entrenamiento": "He entrenado 2 años en gimnasio hace 5 años cuando estaba en la universidad. Era bastante constante, iba 4 veces por semana y seguía una rutina de hipertrofia. Después de graduarme dejé de entrenar por trabajo y mudanzas. Hace 6 meses volví al gym pero sin plan específico, solo hago lo que me apetece. Conozco los ejercicios básicos pero siento que he perdido mucha forma física.",
        
        "frecuencia_entrenamiento": "3-4 veces por semana",
        "tiempo_disponible": "60 minutos por sesión entre semana, 90 minutos sábados",
        "horario_preferido": "Tardes 19:00-20:00 entre semana, mañanas sábados",
        "equipo_disponible": "Gimnasio completo: barras, mancuernas, máquinas, rack, bancos",
        
        # Lesiones
        "lesiones_actuales": "Ninguna lesión activa actualmente",
        "lesiones_previas": "Hace 3 años tuve tendinitis en codo derecho por hacer demasiado curl de bíceps. Se recuperó con fisioterapia en 2 meses. No tengo molestias ahora.",
        
        # Objetivos
        "objetivo_principal": "Ganar masa muscular y perder algo de grasa abdominal",
        "objetivo_secundario": "Mejorar fuerza en los básicos (sentadilla, press banca, peso muerto) y recuperar la forma física que tenía hace 5 años",
        "peso_objetivo": "80kg con menos grasa corporal",
        
        # Estilo de vida
        "horas_sueno": "7-8 horas",
        "nivel_estres": "Medio - trabajo con deadlines pero manejable",
        "trabajo_sedentario": "Sí, 8 horas sentado",
        "adherencia_anterior": "Media - cuando entrenaba antes era constante, ahora me falta estructura",
        
        # Nutrición
        "alimentacion_actual": "Como 3 veces al día. Desayuno cereales, como menú del día en restaurante, ceno en casa (pollo, arroz, pasta). No cuento calorías.",
        "suplementos": "Whey protein ocasionalmente",
        "intolerancias": "Ninguna",
        "preferencias": "Como de todo, no tengo restricciones"
    }
    
    await db.nutrition_questionnaire_submissions.insert_one(questionnaire)
    print(f"✅ Cuestionario creado: {quest_id}")
    return quest_id

async def create_job(submission_id):
    """Crea el job de training"""
    print("\n🚀 Creando job de training...")
    
    timestamp_micro = int(time.time() * 1000000)
    job_id = f"job_bloque1_real_{timestamp_micro}"
    
    job_doc = {
        "_id": job_id,
        "user_id": "user_test_bloque1",
        "type": "training",
        "submission_id": submission_id,
        "training_plan_id": None,
        "previous_nutrition_plan_id": None,
        "previous_training_plan_id": None,
        "status": "pending",
        "progress": {
            "phase": "pending",
            "current_agent": None,
            "completed_steps": 0,
            "total_steps": 9,
            "percentage": 0,
            "message": "Job creado, esperando ejecución"
        },
        "result": {
            "training_plan_id": None,
            "nutrition_plan_id": None
        },
        "error_message": None,
        "token_usage": {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "by_agent": {}
        },
        "created_at": datetime.now(timezone.utc),
        "started_at": None,
        "completed_at": None
    }
    
    await db.generation_jobs.insert_one(job_doc)
    print(f"✅ Job creado: {job_id}")
    print(f"   El worker lo procesará automáticamente en ~5 segundos")
    return job_id

async def monitor_job(job_id, max_wait=900):
    """Monitorea el job hasta completar"""
    print(f"\n⏳ Monitoreando job (timeout: {max_wait}s = {max_wait//60} min)...")
    print("=" * 80)
    
    start_time = time.time()
    last_agent = None
    last_percentage = 0
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed > max_wait:
            print(f"\n⏱️ TIMEOUT: Job no completó en {max_wait}s")
            return None
        
        job = await db.generation_jobs.find_one({"_id": job_id})
        
        if not job:
            print("❌ Job no encontrado en DB")
            return None
        
        status = job.get("status")
        progress = job.get("progress", {})
        current_agent = progress.get("current_agent")
        percentage = progress.get("percentage", 0)
        message = progress.get("message", "")
        
        # Mostrar progreso
        if current_agent != last_agent or percentage != last_percentage:
            timestamp_str = time.strftime("%H:%M:%S")
            print(f"[{timestamp_str}] [{percentage:3d}%] {current_agent or 'PENDING'}: {message}")
            last_agent = current_agent
            last_percentage = percentage
        
        # Estados terminales
        if status == "completed":
            print(f"\n✅ JOB COMPLETADO en {elapsed:.1f}s ({elapsed/60:.1f} min)")
            print("=" * 80)
            return job
        
        elif status == "failed":
            error = job.get("error_message", "Error desconocido")
            print(f"\n❌ JOB FALLÓ: {error}")
            print("=" * 80)
            return job
        
        # Esperar antes de siguiente check
        await asyncio.sleep(3)

async def analyze_results(job_id):
    """Analiza resultados detallados del job"""
    print("\n" + "=" * 80)
    print("📊 ANÁLISIS COMPLETO DE RESULTADOS")
    print("=" * 80)
    
    job = await db.generation_jobs.find_one({"_id": job_id})
    
    if not job:
        print("❌ Job no encontrado")
        return
    
    # 1. Token Usage y Coste
    print("\n### 1️⃣ TOKEN USAGE Y COSTE")
    token_usage = job.get("token_usage", {})
    total_tokens = token_usage.get("total_tokens", 0)
    prompt_tokens = token_usage.get("total_prompt_tokens", 0)
    completion_tokens = token_usage.get("total_completion_tokens", 0)
    
    print(f"\n  Total Tokens: {total_tokens:,}")
    print(f"  └─ Input (Prompt): {prompt_tokens:,}")
    print(f"  └─ Output (Completion): {completion_tokens:,}")
    
    # Coste (GPT-4o mini: $0.150/1M input, $0.600/1M output)
    cost_input = (prompt_tokens / 1_000_000) * 0.150
    cost_output = (completion_tokens / 1_000_000) * 0.600
    total_cost = cost_input + cost_output
    
    print(f"\n  💰 Coste Estimado (GPT-4o mini):")
    print(f"     Input:  ${cost_input:.4f}")
    print(f"     Output: ${cost_output:.4f}")
    print(f"     ────────────────")
    print(f"     TOTAL:  ${total_cost:.4f} USD")
    
    # Por agente
    by_agent = token_usage.get("by_agent", {})
    if by_agent:
        print(f"\n  📊 Tokens por Agente:")
        for agent_id in ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9"]:
            if agent_id in by_agent:
                agent_data = by_agent[agent_id]
                agent_prompt = agent_data.get("prompt_tokens", 0)
                agent_completion = agent_data.get("completion_tokens", 0)
                agent_total = agent_prompt + agent_completion
                print(f"     {agent_id}: {agent_total:,} tokens (in: {agent_prompt:,}, out: {agent_completion:,})")
    
    # 2. Tiempo de Ejecución
    print("\n### 2️⃣ TIEMPO DE EJECUCIÓN")
    created_at = job.get("created_at")
    started_at = job.get("started_at")
    completed_at = job.get("completed_at")
    
    if created_at and completed_at:
        duration = (completed_at - created_at).total_seconds()
        print(f"  Duración Total: {duration:.1f}s ({duration/60:.1f} min)")
        
        if started_at:
            processing_time = (completed_at - started_at).total_seconds()
            queue_time = (started_at - created_at).total_seconds()
            print(f"  └─ En cola: {queue_time:.1f}s")
            print(f"  └─ Procesamiento: {processing_time:.1f}s")
    
    # 3. Client Summary Generado
    print("\n### 3️⃣ CLIENT_SUMMARY GENERADO POR E1")
    
    training_plan_id = job.get("result", {}).get("training_plan_id")
    
    if training_plan_id:
        training_plan = await db.training_plans.find_one({"_id": training_plan_id})
        
        if training_plan and "client_context" in training_plan:
            client_context = training_plan["client_context"]
            training = client_context.get("training", {})
            client_summary = training.get("client_summary")
            
            if client_summary:
                print("  ✅ client_summary EXISTE\n")
                print("  " + "─" * 76)
                print(json.dumps(client_summary, indent=2, ensure_ascii=False))
                print("  " + "─" * 76)
                
                # Validar campos obligatorios
                required = ["objetivo_principal", "nivel", "edad", "disponibilidad", "equipo", "modo"]
                missing = [f for f in required if f not in client_summary]
                
                if missing:
                    print(f"\n  ⚠️ Campos faltantes: {missing}")
                else:
                    print(f"\n  ✅ Todos los campos obligatorios presentes")
                
                # Tamaño
                summary_json = json.dumps(client_summary, ensure_ascii=False)
                tokens_estimate = len(summary_json) // 4
                print(f"  📏 Tamaño estimado: ~{tokens_estimate} tokens")
                
            else:
                print("  ❌ client_summary NO EXISTE")
        else:
            print("  ⚠️ No se encontró client_context en training_plan")
    else:
        print("  ⚠️ No se generó training_plan_id")
    
    # 4. Calidad del Plan (E4 - Mesocycle)
    print("\n### 4️⃣ CALIDAD DEL PLAN GENERADO (hasta E4)")
    
    if training_plan:
        mesocycle = training.get("mesocycle")
        
        if mesocycle:
            print("  ✅ Mesociclo generado\n")
            
            # Mostrar estructura
            if isinstance(mesocycle, dict):
                print(f"  Duración: {mesocycle.get('duracion_semanas', 'N/A')} semanas")
                print(f"  Objetivo: {mesocycle.get('objetivo', 'N/A')}")
                print(f"  Split: {mesocycle.get('split', 'N/A')}")
                
                semanas = mesocycle.get('semanas', [])
                if semanas:
                    print(f"\n  Estructura de {len(semanas)} semanas:")
                    for semana in semanas:
                        num = semana.get('numero', '?')
                        fase = semana.get('fase', '?')
                        vol = semana.get('volumen_pct', '?')
                        rir = semana.get('rir_objetivo', '?')
                        print(f"    S{num}: {fase:15} | Vol: {vol}% | RIR: {rir}")
                
                volumen = mesocycle.get('volumen_por_grupo', {})
                if volumen:
                    print(f"\n  Volumen por grupo muscular:")
                    for grupo, data in volumen.items():
                        if isinstance(data, dict):
                            series = data.get('series_semana', '?')
                            print(f"    {grupo:20}: {series} series/semana")
        else:
            print("  ⚠️ No se generó mesocycle")
    
    # 5. Estado Final
    print("\n### 5️⃣ ESTADO FINAL DEL JOB")
    print(f"  Status: {job.get('status')}")
    
    if job.get('status') == 'failed':
        print(f"  Error: {job.get('error_message')}")
    elif job.get('status') == 'completed':
        print(f"  ✅ Plan generado exitosamente")
        print(f"  Training Plan ID: {training_plan_id}")
    
    print("\n" + "=" * 80)

async def main():
    """Ejecuta el test completo"""
    print("\n" + "=" * 80)
    print("🧪 TEST REAL BLOQUE 1 - VALIDACIÓN COMPLETA")
    print("=" * 80)
    
    try:
        # 1. Crear cuestionario
        quest_id = await create_realistic_questionnaire()
        
        # 2. Crear job
        job_id = await create_job(quest_id)
        
        # 3. Esperar y monitorear (15 min timeout)
        job_result = await monitor_job(job_id, max_wait=900)
        
        if job_result:
            # 4. Analizar resultados detallados
            await analyze_results(job_id)
        else:
            print("\n⚠️ No se pudo completar el análisis")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()
    
    print("\n" + "=" * 80)
    print("✅ TEST FINALIZADO")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
