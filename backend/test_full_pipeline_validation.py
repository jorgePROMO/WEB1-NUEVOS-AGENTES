"""
Script de validación completa del pipeline E1-E9.

Este script:
1. Define el schema EXACTO del cuestionario esperado
2. Crea un cuestionario de ejemplo válido
3. Crea un job de generación
4. Monitorea su progreso
5. Extrae métricas reales (tokens, costos, tiempos)
6. Extrae outputs concretos (sessions, formatted_plan, audit, bridge_for_nutrition)
7. Valida coherencia entre outputs

Uso:
    python test_full_pipeline_validation.py
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timezone
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

# MongoDB setup
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
DB_NAME = os.getenv('DB_NAME', 'test_database')

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# ============================================================
# SCHEMA DEL CUESTIONARIO - FORMATO EXACTO ESPERADO
# ============================================================

QUESTIONNAIRE_SCHEMA = {
    "description": "Cuestionario de Nutrición E.D.N.360",
    "storage_format": {
        "_id": "string (timestamp único)",
        "user_id": "string",
        "responses": {
            "nombre_completo": "string",
            "email": "string",
            "fecha_nacimiento": "string (YYYY-MM-DD)",
            "sexo": "string (Hombre/Mujer)",
            "profesion": "string",
            "telefono": "string",
            "peso": "string (e.g., '75')",
            "altura_cm": "string (e.g., '175')",
            "estres_profesion": "string",
            "movimiento_trabajo": "string",
            "descansa_trabajo": "string",
            "horas_trabajo": "string",
            "actividad_fisica_diaria": "string",
            "trabajo_fisicamente": "string",
            "practicado_deporte": "string",
            "constante_deporte": "string",
            "nivel_deporte": "string",
            "entrenado_gimnasio": "string",
            "entrenador_personal": "string",
            "resistencia_cardiorespiratoria": "string",
            "fuerza": "string",
            "flexibilidad": "string",
            "agilidad_coordinacion": "string",
            "dias_semana_entrenar": "string",
            "tiempo_sesion": "string",
            "entrena_manana_tarde": "string",
            "gimnasio": "string",
            "tipo_persona": "string",
            "cuesta_coger_peso": "string",
            "motivos_entrenar": ["list", "of", "strings"],
            "hora_levanta": "string",
            "hora_desayuno": "string",
            "hora_comida": "string",
            "hora_cena": "string",
            "hora_acuesta": "string",
            "horas_duerme": "string",
            "comidas_dia": "string",
            "come_fuera_casa": "string",
            "azucar_dulces_bolleria": "string",
            "anade_sal": "string",
            "bebidas_gas": "string",
            "objetivo_fisico": "string",
            "experiencia_ejercicio_constante": "string",
            "nivel_energia_dia": "string"
        },
        "submitted_at": "datetime",
        "plan_generated": "boolean",
        "plan_id": "string or null"
    },
    "required_fields": [
        "nombre_completo", "email", "fecha_nacimiento", "sexo", 
        "peso", "altura_cm", "objetivo_fisico"
    ],
    "notes": [
        "El campo 'responses' contiene TODOS los datos del cuestionario como dict plano",
        "Los campos numéricos (peso, altura_cm) se guardan como strings",
        "La fecha_nacimiento debe estar en formato YYYY-MM-DD",
        "Los campos Optional pueden ser None o strings vacías"
    ]
}

# ============================================================
# CUESTIONARIO DE EJEMPLO VÁLIDO
# ============================================================

EXAMPLE_QUESTIONNAIRE_RESPONSES = {
    # Datos básicos
    "nombre_completo": "Carlos Fernández López",
    "email": "carlos.fernandez@example.com",
    "fecha_nacimiento": "1990-05-15",  # 34 años
    "sexo": "Hombre",
    "profesion": "Ingeniero de Software",
    "direccion": "Calle Mayor 123, Madrid",
    "telefono": "+34 612 345 678",
    
    # Medidas corporales
    "peso": "78",
    "altura_cm": "178",
    "grasa_porcentaje": "18",
    "cintura_cm": "85",
    "cadera_cm": "95",
    "biceps_relajado_cm": "32",
    "biceps_flexionado_cm": "35",
    "muslo_cm": "55",
    
    # Salud y medicación
    "medicamentos": "Ninguno",
    "enfermedad_cronica": "No",
    "fuma_cantidad": "No fumo",
    "bebe_cantidad": "Ocasionalmente (1-2 veces por semana)",
    "retencion_liquidos": "No",
    "problemas_corazon": "No",
    "hipertension": "No",
    "diabetes": "No",
    "colesterol": "Niveles normales",
    "sobrepeso": "No",
    "epilepsia": "No",
    "alergias_intolerancias": "Intolerancia leve a la lactosa",
    "problema_ejercicio": "Ninguno",
    "operaciones": "Ninguna",
    "embarazo": "No aplica",
    "problemas_respiratorios": "No",
    "problemas_musculares": "Dolor lumbar ocasional",
    "varo_valgo": "No",
    "hernias_protusiones": "No",
    "artrosis": "No",
    "menopausia": "No aplica",
    "osteoporosis": "No",
    
    # Trabajo y estrés
    "estres_profesion": "Moderado (6/10)",
    "movimiento_trabajo": "Principalmente sentado, con descansos activos",
    "dia_trabajo": "Trabajo de oficina con ordenador",
    "descansa_trabajo": "Sí, tomo descansos cada 90 minutos",
    "horas_trabajo": "8 horas diarias",
    "actividad_fisica_diaria": "Camino 30 minutos al día",
    "trabajo_fisicamente": "No, trabajo sentado",
    "horas_ocio_semana": "10-15 horas",
    
    # Experiencia deportiva
    "practicado_deporte": "Sí, fútbol en la adolescencia y gimnasio en los últimos 3 años",
    "experiencia_negativa": "Lesión de rodilla hace 2 años jugando fútbol",
    "constante_deporte": "Los últimos 3 años he sido bastante constante",
    "tiempo_dedicaba": "5 días a la semana, 1 hora por sesión",
    "nivel_deporte": "Intermedio",
    "entrenado_gimnasio": "Sí, 3 años de experiencia",
    "entrenador_personal": "No, siempre he entrenado por mi cuenta",
    "resistencia_cardiorespiratoria": "7/10",
    "fuerza": "6/10",
    "flexibilidad": "5/10",
    "agilidad_coordinacion": "7/10",
    
    # Disponibilidad y preferencias
    "dias_semana_entrenar": "4-5 días",
    "tiempo_sesion": "60-75 minutos",
    "entrena_manana_tarde": "Tarde (18:00-20:00)",
    "gimnasio": "Sí, tengo acceso a gimnasio completo",
    "material_casa": "Mancuernas de 5-20kg, bandas elásticas",
    "actividades_realizar": "Peso libre, máquinas, algo de cardio",
    "tipo_persona": "Disciplinado pero necesito variedad para no aburrirme",
    "cuesta_coger_peso": "Me cuesta algo pero he mejorado",
    "motivos_entrenar": [
        "Mejorar mi composición corporal",
        "Ganar fuerza y músculo",
        "Sentirme mejor físicamente",
        "Reducir estrés del trabajo"
    ],
    
    # Horarios
    "hora_levanta": "07:00",
    "hora_desayuno": "07:30",
    "hora_almuerzo": "11:00",
    "hora_comida": "14:00",
    "hora_merienda": "17:00",
    "hora_cena": "21:00",
    "hora_acuesta": "23:30",
    "horas_duerme": "7-8 horas",
    
    # Hábitos alimentarios
    "comidas_dia": "5 comidas (desayuno, almuerzo, comida, merienda, cena)",
    "comidas_fuertes_ligeras": "Comida fuerte y cena ligera",
    "alimento_no_soporta": "Pescado azul (me cuesta)",
    "comida_favorita": "Pasta, arroz con pollo",
    "comida_basura_frecuencia": "1 vez a la semana (fines de semana)",
    "dietas_anteriores": "Probé dieta keto hace 2 años pero no la mantuve",
    "sustancias_alteran": "Café (2-3 tazas al día)",
    "suplementacion": "Proteína whey ocasionalmente",
    "come_fuera_casa": "2-3 veces por semana",
    "azucar_dulces_bolleria": "Ocasionalmente (1-2 veces/semana)",
    "anade_sal": "Sí, pero moderadamente",
    "bebidas_gas": "Raramente",
    
    # Objetivos
    "objetivo_fisico": "Ganar músculo y definir (recomposición corporal)",
    "experiencia_ejercicio_constante": "He sido constante los últimos 3 años pero sin plan estructurado",
    "impedido_constancia": "A veces el estrés laboral y viajes de trabajo",
    "motiva_ejercicio": "Ver progreso visual y mejorar mis marcas",
    "nivel_energia_dia": "7/10 - Buena energía en general",
    "comentarios_adicionales": "Busco un plan estructurado y progresivo que me ayude a optimizar mi tiempo en el gimnasio. He estado entrenando pero siento que podría mejorar mucho con mejor programación."
}

# ============================================================
# FUNCIÓN PRINCIPAL DE VALIDACIÓN
# ============================================================

async def validate_questionnaire_format(responses: dict) -> tuple[bool, list[str]]:
    """
    Valida que un cuestionario tenga el formato correcto.
    
    Returns:
        (is_valid, errors)
    """
    errors = []
    
    # Check required fields
    required = [
        "nombre_completo", "email", "fecha_nacimiento", "sexo",
        "peso", "altura_cm", "objetivo_fisico"
    ]
    
    for field in required:
        if field not in responses:
            errors.append(f"Campo requerido ausente: {field}")
        elif not responses[field]:
            errors.append(f"Campo requerido vacío: {field}")
    
    # Validate specific formats
    if "fecha_nacimiento" in responses:
        try:
            datetime.strptime(responses["fecha_nacimiento"], "%Y-%m-%d")
        except ValueError:
            errors.append("fecha_nacimiento debe estar en formato YYYY-MM-DD")
    
    if "sexo" in responses:
        if responses["sexo"].lower() not in ["hombre", "mujer", "masculino", "femenino"]:
            errors.append(f"sexo debe ser 'Hombre' o 'Mujer', recibido: {responses['sexo']}")
    
    # Validate numeric fields
    for field in ["peso", "altura_cm"]:
        if field in responses:
            try:
                float(responses[field])
            except (ValueError, TypeError):
                errors.append(f"{field} debe ser un número válido, recibido: {responses[field]}")
    
    return len(errors) == 0, errors


async def create_test_user_and_submission():
    """
    Crea un usuario de prueba y una submission válida.
    
    Returns:
        (user_id, submission_id)
    """
    print("\n" + "="*60)
    print("PASO 1: Crear usuario y cuestionario de prueba")
    print("="*60)
    
    # Create test user
    user_id = f"test_user_{int(datetime.now(timezone.utc).timestamp())}"
    user_doc = {
        "_id": user_id,
        "username": f"testuser_{user_id}",
        "email": "test@edn360.com",
        "name": "Test User",
        "password": "hashed_password",
        "role": "user",
        "subscription": {
            "status": "active",
            "plan": "team",
            "payment_status": "verified"
        },
        "created_at": datetime.now(timezone.utc)
    }
    
    # Check if user exists
    existing_user = await db.users.find_one({"_id": user_id})
    if existing_user:
        print(f"✓ Usuario ya existe: {user_id}")
    else:
        await db.users.insert_one(user_doc)
        print(f"✓ Usuario creado: {user_id}")
    
    # Validate questionnaire format
    print("\n📋 Validando formato del cuestionario...")
    is_valid, errors = await validate_questionnaire_format(EXAMPLE_QUESTIONNAIRE_RESPONSES)
    
    if not is_valid:
        print("❌ Cuestionario inválido:")
        for error in errors:
            print(f"   - {error}")
        return None, None
    
    print("✅ Cuestionario válido")
    
    # Create submission
    submission_id = str(int(datetime.now(timezone.utc).timestamp() * 1000000))
    submission_doc = {
        "_id": submission_id,
        "user_id": user_id,
        "responses": EXAMPLE_QUESTIONNAIRE_RESPONSES,
        "submitted_at": datetime.now(timezone.utc),
        "plan_generated": False,
        "plan_id": None
    }
    
    await db.nutrition_questionnaire_submissions.insert_one(submission_doc)
    print(f"✓ Cuestionario guardado: {submission_id}")
    
    return user_id, submission_id


async def create_generation_job(user_id: str, submission_id: str) -> str:
    """
    Crea un job de generación de tipo 'training'.
    
    Returns:
        job_id
    """
    print("\n" + "="*60)
    print("PASO 2: Crear job de generación")
    print("="*60)
    
    job_id = f"job_{int(datetime.now(timezone.utc).timestamp() * 1000000)}"
    job_doc = {
        "_id": job_id,
        "user_id": user_id,
        "submission_id": submission_id,
        "type": "training",  # Solo training (E1-E9)
        "status": "pending",
        "progress": {
            "phase": "",
            "current_agent": "",
            "completed_steps": 0,
            "total_steps": 9,
            "percentage": 0,
            "message": "En cola..."
        },
        "result": {
            "training_plan_id": None,
            "nutrition_plan_id": None
        },
        "error_message": None,
        "error_reason": None,
        "token_usage": {
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_tokens": 0,
            "by_agent": {}
        },
        "execution_log": [],
        "created_at": datetime.now(timezone.utc),
        "started_at": None,
        "completed_at": None
    }
    
    await db.generation_jobs.insert_one(job_doc)
    print(f"✓ Job creado: {job_id}")
    print(f"  User ID: {user_id}")
    print(f"  Submission ID: {submission_id}")
    print(f"  Type: training (E1-E9)")
    print(f"  Status: pending")
    
    return job_id


async def monitor_job_progress(job_id: str, timeout_minutes: int = 15):
    """
    Monitorea el progreso de un job hasta que termine o timeout.
    
    Returns:
        final_job_doc
    """
    print("\n" + "="*60)
    print("PASO 3: Monitorear progreso del job")
    print("="*60)
    print(f"⏱️  Timeout: {timeout_minutes} minutos")
    print(f"🔄 Polling cada 5 segundos...\n")
    
    start_time = datetime.now(timezone.utc)
    timeout = start_time.timestamp() + (timeout_minutes * 60)
    
    last_status = None
    last_agent = None
    
    while datetime.now(timezone.utc).timestamp() < timeout:
        job = await db.generation_jobs.find_one({"_id": job_id})
        
        if not job:
            print("❌ Job no encontrado")
            return None
        
        status = job["status"]
        progress = job.get("progress", {})
        current_agent = progress.get("current_agent", "")
        percentage = progress.get("percentage", 0)
        message = progress.get("message", "")
        
        # Print updates
        if status != last_status or current_agent != last_agent:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            print(f"[{elapsed:05.1f}s] Status: {status:10s} | Agent: {current_agent:5s} | {percentage:3.0f}% | {message}")
            last_status = status
            last_agent = current_agent
        
        # Check if finished
        if status in ["completed", "failed"]:
            print(f"\n{'✅' if status == 'completed' else '❌'} Job {status}")
            return job
        
        await asyncio.sleep(5)
    
    print(f"\n⚠️  Timeout después de {timeout_minutes} minutos")
    return await db.generation_jobs.find_one({"_id": job_id})


async def extract_metrics_and_outputs(job_id: str):
    """
    Extrae métricas y outputs del job completado.
    
    Returns:
        metrics_report (dict)
    """
    print("\n" + "="*60)
    print("PASO 4: Extraer métricas y outputs")
    print("="*60)
    
    job = await db.generation_jobs.find_one({"_id": job_id})
    
    if not job:
        print("❌ Job no encontrado")
        return None
    
    if job["status"] != "completed":
        print(f"⚠️  Job no completado (status: {job['status']})")
        if job.get("error_message"):
            print(f"   Error: {job['error_message']}")
        return None
    
    # Extract basic metrics
    report = {
        "job_id": job_id,
        "status": job["status"],
        "execution_time": {},"token_usage": {},
        "outputs": {},
        "coherence_analysis": {}
    }
    
    # Calculate execution time
    if job.get("started_at") and job.get("completed_at"):
        started = job["started_at"]
        completed = job["completed_at"]
        duration = (completed - started).total_seconds()
        report["execution_time"] = {
            "started_at": started.isoformat(),
            "completed_at": completed.isoformat(),
            "duration_seconds": duration,
            "duration_minutes": duration / 60
        }
        print(f"\n⏱️  TIEMPO DE EJECUCIÓN")
        print(f"   Inicio: {started.strftime('%H:%M:%S')}")
        print(f"   Fin: {completed.strftime('%H:%M:%S')}")
        print(f"   Duración: {duration/60:.2f} minutos ({duration:.1f} segundos)")
    
    # Extract token usage
    token_usage = job.get("token_usage", {})
    if token_usage:
        total_tokens = token_usage.get("total_tokens", 0)
        prompt_tokens = token_usage.get("total_prompt_tokens", 0)
        completion_tokens = token_usage.get("total_completion_tokens", 0)
        
        # Calculate cost (assuming GPT-5-mini pricing)
        # Input: $0.075 per 1M tokens
        # Output: $0.30 per 1M tokens
        input_cost = (prompt_tokens / 1_000_000) * 0.075
        output_cost = (completion_tokens / 1_000_000) * 0.30
        total_cost = input_cost + output_cost
        
        report["token_usage"] = {
            "total_tokens": total_tokens,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "input_cost_usd": round(input_cost, 4),
            "output_cost_usd": round(output_cost, 4),
            "total_cost_usd": round(total_cost, 4),
            "by_agent": token_usage.get("by_agent", {})
        }
        
        print(f"\n💰 CONSUMO DE TOKENS Y COSTOS")
        print(f"   Total tokens: {total_tokens:,}")
        print(f"   - Input: {prompt_tokens:,} tokens")
        print(f"   - Output: {completion_tokens:,} tokens")
        print(f"   Costo total: ${total_cost:.4f} USD")
        print(f"   - Input cost: ${input_cost:.4f}")
        print(f"   - Output cost: ${output_cost:.4f}")
        
        # Per-agent breakdown
        by_agent = token_usage.get("by_agent", {})
        if by_agent:
            print(f"\n   📊 Desglose por agente:")
            for agent_id, agent_tokens in sorted(by_agent.items()):
                agent_total = agent_tokens.get("total_tokens", 0)
                agent_prompt = agent_tokens.get("prompt_tokens", 0)
                agent_completion = agent_tokens.get("completion_tokens", 0)
                print(f"      {agent_id}: {agent_total:,} tokens (in: {agent_prompt:,}, out: {agent_completion:,})")
    
    # Extract training plan outputs
    training_plan_id = job.get("result", {}).get("training_plan_id")
    
    if training_plan_id:
        training_plan = await db.training_plans.find_one({"_id": training_plan_id})
        
        if training_plan:
            print(f"\n📋 PLAN DE ENTRENAMIENTO")
            print(f"   Plan ID: {training_plan_id}")
            
            # Extract key outputs
            training_data = training_plan.get("training", {})
            
            # E5: sessions
            sessions = training_data.get("sessions")
            if sessions:
                report["outputs"]["sessions"] = sessions
                print(f"   ✓ Sessions (E5): {len(sessions)} sesiones")
                print(f"      Preview: {json.dumps(sessions[0] if sessions else {}, indent=2)[:200]}...")
            
            # E7: formatted_plan
            formatted_plan = training_data.get("formatted_plan")
            if formatted_plan:
                report["outputs"]["formatted_plan"] = formatted_plan
                plan_str = str(formatted_plan)
                print(f"   ✓ Formatted Plan (E7): {len(plan_str)} caracteres")
                print(f"      Preview: {plan_str[:200]}...")
            
            # E8: audit
            audit = training_data.get("audit")
            if audit:
                report["outputs"]["audit"] = audit
                audit_str = str(audit)
                print(f"   ✓ Audit (E8): {len(audit_str)} caracteres")
                print(f"      Preview: {audit_str[:200]}...")
            
            # E9: bridge_for_nutrition
            bridge = training_data.get("bridge_for_nutrition")
            if bridge:
                report["outputs"]["bridge_for_nutrition"] = bridge
                bridge_str = str(bridge)
                print(f"   ✓ Bridge for Nutrition (E9): {len(bridge_str)} caracteres")
                print(f"      Preview: {bridge_str[:200]}...")
            
            # Additional context
            mesocycle = training_data.get("mesocycle")
            if mesocycle:
                print(f"\n   📅 Mesocycle structure:")
                print(f"      Weeks: {len(mesocycle.get('weeks', []))}")
                print(f"      Duration: {mesocycle.get('duration_weeks', 'N/A')} weeks")
        else:
            print(f"⚠️  Training plan not found: {training_plan_id}")
    else:
        print("⚠️  No training_plan_id in job result")
    
    return report


async def validate_coherence(report: dict):
    """
    Valida la coherencia entre los diferentes outputs.
    """
    print("\n" + "="*60)
    print("PASO 5: Validación de coherencia")
    print("="*60)
    
    outputs = report.get("outputs", {})
    
    # Check that all key outputs exist
    required_outputs = ["sessions", "formatted_plan", "audit", "bridge_for_nutrition"]
    missing = [o for o in required_outputs if o not in outputs]
    
    if missing:
        print(f"❌ Outputs faltantes: {missing}")
        return
    
    print("✅ Todos los outputs principales están presentes\n")
    
    # Coherence checks
    coherence_results = []
    
    # 1. Sessions existence
    sessions = outputs.get("sessions", [])
    if sessions:
        coherence_results.append(f"✓ Sessions: {len(sessions)} sesiones generadas")
    else:
        coherence_results.append("✗ Sessions: Lista vacía")
    
    # 2. Formatted plan references sessions
    formatted_plan = str(outputs.get("formatted_plan", ""))
    if formatted_plan:
        if "session" in formatted_plan.lower() or "día" in formatted_plan.lower():
            coherence_results.append("✓ Formatted Plan: Referencia a sesiones detectada")
        else:
            coherence_results.append("⚠ Formatted Plan: No se detectan referencias claras a sesiones")
    
    # 3. Audit mentions plan elements
    audit = str(outputs.get("audit", ""))
    if audit:
        if "plan" in audit.lower() or "entrenamiento" in audit.lower():
            coherence_results.append("✓ Audit: Referencia al plan detectada")
        else:
            coherence_results.append("⚠ Audit: No se detectan referencias al plan")
    
    # 4. Bridge includes training summary
    bridge = str(outputs.get("bridge_for_nutrition", ""))
    if bridge:
        if "entrenamiento" in bridge.lower() or "training" in bridge.lower():
            coherence_results.append("✓ Bridge: Referencia al entrenamiento detectada")
        else:
            coherence_results.append("⚠ Bridge: No se detectan referencias al entrenamiento")
    
    print("📊 Análisis de coherencia:")
    for result in coherence_results:
        print(f"   {result}")
    
    report["coherence_analysis"] = {
        "results": coherence_results,
        "all_outputs_present": len(missing) == 0
    }


async def save_report(report: dict):
    """
    Guarda el reporte en un archivo JSON.
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"/app/backend/validation_report_{timestamp}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n💾 Reporte guardado: {filename}")


async def print_schema_documentation():
    """
    Imprime la documentación del schema del cuestionario.
    """
    print("\n" + "="*60)
    print("DOCUMENTACIÓN DEL SCHEMA DEL CUESTIONARIO")
    print("="*60)
    print("\n📋 FORMATO ESPERADO EN MONGODB:")
    print(json.dumps(QUESTIONNAIRE_SCHEMA, indent=2, ensure_ascii=False))
    print("\n✅ CAMPOS REQUERIDOS MÍNIMOS:")
    for field in QUESTIONNAIRE_SCHEMA["required_fields"]:
        print(f"   - {field}")
    print("\n📝 NOTAS IMPORTANTES:")
    for note in QUESTIONNAIRE_SCHEMA["notes"]:
        print(f"   • {note}")


async def main():
    """
    Función principal de validación.
    """
    print("\n" + "="*70)
    print("   VALIDACIÓN COMPLETA DEL PIPELINE E1-E9 - E.D.N.360")
    print("="*70)
    
    # Print schema documentation
    await print_schema_documentation()
    
    # Step 1: Create test data
    user_id, submission_id = await create_test_user_and_submission()
    
    if not user_id or not submission_id:
        print("\n❌ No se pudo crear el usuario o cuestionario de prueba")
        return
    
    # Step 2: Create generation job
    job_id = await create_generation_job(user_id, submission_id)
    
    print(f"\n{'='*60}")
    print("⚠️  NOTA IMPORTANTE: El job worker debe estar corriendo")
    print("   Verificar con: sudo supervisorctl status job_worker")
    print("   Si no está corriendo: sudo supervisorctl start job_worker")
    print(f"{'='*60}")
    
    input("\nPresiona ENTER cuando el job_worker esté corriendo...")
    
    # Step 3: Monitor job progress
    final_job = await monitor_job_progress(job_id, timeout_minutes=15)
    
    if not final_job:
        print("\n❌ No se pudo monitorear el job")
        return
    
    # Step 4: Extract metrics and outputs
    report = await extract_metrics_and_outputs(job_id)
    
    if not report:
        print("\n❌ No se pudieron extraer métricas")
        return
    
    # Step 5: Validate coherence
    await validate_coherence(report)
    
    # Save report
    await save_report(report)
    
    print("\n" + "="*70)
    print("   ✅ VALIDACIÓN COMPLETADA")
    print("="*70)
    print(f"\n📊 RESUMEN:")
    print(f"   Job ID: {job_id}")
    print(f"   Status: {report['status']}")
    print(f"   Duración: {report['execution_time'].get('duration_minutes', 0):.2f} minutos")
    print(f"   Tokens totales: {report['token_usage'].get('total_tokens', 0):,}")
    print(f"   Costo total: ${report['token_usage'].get('total_cost_usd', 0):.4f} USD")
    print(f"   Outputs generados: {len(report['outputs'])}")
    

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⛔ Validación cancelada por usuario")
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
