"""
TEST BLOQUE 1 - Validación de Arquitectura de Cajones
Ejecuta 1 job de prueba y captura métricas detalladas
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import sys

# Agregar backend al path
sys.path.append('/app/backend')
sys.path.append('/app/backend/edn360')

load_dotenv('/app/backend/.env')

# Conectar a MongoDB
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client['edn360']

def estimate_tokens(text):
    """Estimación aproximada de tokens (1 token ≈ 4 caracteres)"""
    if isinstance(text, dict):
        text = json.dumps(text, ensure_ascii=False)
    elif not isinstance(text, str):
        text = str(text)
    return len(text) // 4

async def create_test_questionnaire():
    """Crea un cuestionario de prueba estándar"""
    print("📝 Creando cuestionario de prueba...")
    
    questionnaire = {
        "_id": f"test_quest_{int(time.time())}",
        "user_id": "test_user_bloque1",
        "created_at": datetime.now(timezone.utc),
        
        # Datos básicos
        "nombre_completo": "Ana López García",
        "email": "ana.lopez@test.com",
        "fecha_nacimiento": "1992-05-15",
        "sexo": "mujer",
        "profesion": "Ingeniera de software",
        "telefono": "+34 600 123 456",
        
        # Medidas corporales
        "peso": "68",
        "altura_cm": "165",
        "grasa_porcentaje": "28",
        "cintura_cm": "78",
        
        # Salud
        "medicamentos": "Ninguno",
        "enfermedad_cronica": "No",
        "fuma_cantidad": "No fumo",
        "bebe_cantidad": "Social (1-2 veces/semana)",
        
        # Experiencia entrenamiento
        "experiencia_entrenamiento": "3 años de gimnasio intermitente",
        "frecuencia_entrenamiento": "3-4 veces por semana",
        "tiempo_disponible": "60 minutos por sesión",
        "horario_preferido": "Tarde (18:00)",
        "equipo_disponible": "Gimnasio completo con máquinas, barras, mancuernas",
        
        # Lesiones
        "lesiones_actuales": "Dolor lumbar ocasional cuando hago peso muerto",
        "lesiones_previas": "Esguince de tobillo hace 1 año (recuperado)",
        
        # Objetivos
        "objetivo_principal": "Perder grasa y definir músculo",
        "objetivo_secundario": "Mejorar fuerza y composición corporal",
        "peso_objetivo": "62",
        
        # Estilo de vida
        "horas_sueno": "7",
        "nivel_estres": "Medio",
        "trabajo_sedentario": "Sí",
        "adherencia_anterior": "Baja - he dejado el gym varias veces"
    }
    
    # Insertar en MongoDB
    await db.nutrition_questionnaire_submissions.insert_one(questionnaire)
    print(f"✅ Cuestionario creado: {questionnaire['_id']}")
    return questionnaire

async def create_test_job(submission_id):
    """Crea un job de prueba para training"""
    print("\n🚀 Creando job de prueba (solo training)...")
    
    job_id = f"test_job_bloque1_{int(time.time() * 1000000)}"
    
    job_doc = {
        "_id": job_id,
        "user_id": "test_user_bloque1",
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
    return job_id

async def monitor_job(job_id, max_wait=600):
    """Monitorea el job hasta que termine o falle"""
    print(f"\n⏳ Monitoreando job: {job_id}")
    print("=" * 80)
    
    start_time = time.time()
    last_agent = None
    
    while True:
        elapsed = time.time() - start_time
        
        if elapsed > max_wait:
            print(f"\n⏱️ Timeout: El job superó {max_wait}s")
            return None
        
        job = await db.generation_jobs.find_one({"_id": job_id})
        
        if not job:
            print("❌ Job no encontrado")
            return None
        
        status = job.get("status")
        progress = job.get("progress", {})
        current_agent = progress.get("current_agent")
        
        # Mostrar progreso si cambió de agente
        if current_agent != last_agent and current_agent:
            percentage = progress.get("percentage", 0)
            message = progress.get("message", "")
            print(f"  [{percentage:3d}%] {current_agent}: {message}")
            last_agent = current_agent
        
        # Estados terminales
        if status == "completed":
            print(f"\n✅ Job completado en {elapsed:.1f}s")
            return job
        
        elif status == "failed":
            error = job.get("error_message", "Error desconocido")
            print(f"\n❌ Job falló: {error}")
            return job
        
        # Esperar antes de volver a chequear
        await asyncio.sleep(2)

async def analyze_job_results(job_id):
    """Analiza los resultados del job y extrae métricas"""
    print("\n" + "=" * 80)
    print("📊 ANÁLISIS DE RESULTADOS - BLOQUE 1")
    print("=" * 80)
    
    job = await db.generation_jobs.find_one({"_id": job_id})
    
    if not job:
        print("❌ Job no encontrado")
        return
    
    # 1. Token Usage
    print("\n### 1️⃣ TOKEN USAGE")
    token_usage = job.get("token_usage", {})
    total_tokens = token_usage.get("total_tokens", 0)
    prompt_tokens = token_usage.get("total_prompt_tokens", 0)
    completion_tokens = token_usage.get("total_completion_tokens", 0)
    
    print(f"  Total Tokens: {total_tokens:,}")
    print(f"  Prompt Tokens: {prompt_tokens:,}")
    print(f"  Completion Tokens: {completion_tokens:,}")
    
    # Coste estimado (GPT-4o pricing aprox)
    # Input: $2.50 per 1M tokens, Output: $10 per 1M tokens
    cost_input = (prompt_tokens / 1_000_000) * 2.5
    cost_output = (completion_tokens / 1_000_000) * 10.0
    total_cost = cost_input + cost_output
    
    print(f"\n  💰 Coste Estimado:")
    print(f"     Input: ${cost_input:.4f}")
    print(f"     Output: ${cost_output:.4f}")
    print(f"     TOTAL: ${total_cost:.4f}")
    
    # Por agente
    by_agent = token_usage.get("by_agent", {})
    if by_agent:
        print(f"\n  📊 Por Agente:")
        for agent_id in ["E1", "E2", "E3", "E4"]:
            if agent_id in by_agent:
                agent_data = by_agent[agent_id]
                agent_total = agent_data.get("prompt_tokens", 0) + agent_data.get("completion_tokens", 0)
                print(f"     {agent_id}: {agent_total:,} tokens (input: {agent_data.get('prompt_tokens', 0):,})")
    
    # 2. Tiempo de ejecución
    print("\n### 2️⃣ TIEMPO DE EJECUCIÓN")
    created_at = job.get("created_at")
    completed_at = job.get("completed_at")
    
    if created_at and completed_at:
        duration = (completed_at - created_at).total_seconds()
        print(f"  Duración Total: {duration:.1f}s ({duration/60:.1f} min)")
    
    # 3. Client Summary generado
    print("\n### 3️⃣ CLIENT_SUMMARY GENERADO")
    
    # Buscar el training plan asociado
    training_plan_id = job.get("result", {}).get("training_plan_id")
    if training_plan_id:
        training_plan = await db.training_plans.find_one({"_id": training_plan_id})
        
        if training_plan and "client_context" in training_plan:
            client_context = training_plan["client_context"]
            training = client_context.get("training", {})
            client_summary = training.get("client_summary")
            
            if client_summary:
                print("  ✅ client_summary existe")
                
                # Mostrar contenido
                print(f"\n  Contenido:")
                for key, value in client_summary.items():
                    if isinstance(value, dict):
                        print(f"    {key}: {{...}}")
                    elif isinstance(value, list):
                        print(f"    {key}: [{len(value)} items]")
                    else:
                        print(f"    {key}: {value}")
                
                # Tamaño
                summary_size = estimate_tokens(client_summary)
                print(f"\n  📏 Tamaño: ~{summary_size} tokens")
                
                # Validar campos obligatorios
                required_fields = ["objetivo_principal", "nivel", "edad", "disponibilidad", "equipo", "modo"]
                missing = [f for f in required_fields if f not in client_summary]
                
                if missing:
                    print(f"  ⚠️ Campos faltantes: {missing}")
                else:
                    print(f"  ✅ Todos los campos obligatorios presentes")
                
            else:
                print("  ❌ client_summary NO existe")
        else:
            print("  ⚠️ No se encontró training_plan o client_context")
    else:
        print("  ⚠️ No se generó training_plan_id")
    
    # 4. Comparativa de inputs (estimado desde logs si disponible)
    print("\n### 4️⃣ COMPARATIVA DE INPUTS (ESTIMADO)")
    print("  Basado en token_usage por agente:")
    
    if by_agent:
        for agent_id in ["E1", "E2", "E3", "E4"]:
            if agent_id in by_agent:
                input_tokens = by_agent[agent_id].get("prompt_tokens", 0)
                print(f"    {agent_id}: ~{input_tokens:,} tokens de input")
        
        # Calcular reducción
        if "E1" in by_agent and "E2" in by_agent:
            e1_input = by_agent["E1"].get("prompt_tokens", 0)
            e2_input = by_agent["E2"].get("prompt_tokens", 0)
            
            if e1_input > 0:
                reduction = ((e1_input - e2_input) / e1_input) * 100
                print(f"\n  📉 Reducción E1→E2: {reduction:.1f}%")
    
    print("\n" + "=" * 80)

async def main():
    """Función principal del test"""
    print("\n" + "=" * 80)
    print("🧪 TEST BLOQUE 1 - VALIDACIÓN DE ARQUITECTURA DE CAJONES")
    print("=" * 80)
    
    try:
        # 1. Crear cuestionario de prueba
        questionnaire = await create_test_questionnaire()
        
        # 2. Crear job
        job_id = await create_test_job(questionnaire["_id"])
        
        # 3. Esperar a que el worker lo procese
        print("\n⏳ Esperando a que el worker procese el job...")
        print("   (El worker revisa cada 5 segundos)")
        
        job_result = await monitor_job(job_id, max_wait=600)
        
        if job_result:
            # 4. Analizar resultados
            await analyze_job_results(job_id)
            
            # 5. Mostrar estado final
            print(f"\n### 5️⃣ ESTADO FINAL")
            print(f"  Status: {job_result.get('status')}")
            
            if job_result.get('status') == 'failed':
                print(f"  Error: {job_result.get('error_message')}")
        else:
            print("\n❌ No se pudo completar el test")
        
    except Exception as e:
        print(f"\n❌ Error en test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cerrar conexión
        client.close()
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
