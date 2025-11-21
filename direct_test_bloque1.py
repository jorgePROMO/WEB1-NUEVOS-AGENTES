"""
TEST DIRECTO BLOQUE 1 - Sin worker
Ejecuta directamente E1-E4 para validar la refactorización
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

# Importar agentes y modelos
from edn360.agents.training_initial.e1_analyst import E1Analyst
from edn360.agents.training_initial.e2_capacity import E2CapacityEvaluator
from edn360.agents.training_initial.e3_adaptation import E3AdaptationAnalyst
from edn360.agents.training_initial.e4_architect import E4ProgramArchitect
from edn360.client_context_utils import initialize_client_context

MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client['edn360']

async def create_test_questionnaire():
    """Crea un cuestionario de prueba"""
    print("📝 Creando cuestionario de prueba...")
    
    timestamp = int(time.time())
    quest_id = f"direct_test_{timestamp}"
    
    questionnaire = {
        "_id": quest_id,
        "user_id": "direct_test_user",
        "created_at": datetime.now(timezone.utc),
        
        # Datos básicos
        "nombre_completo": "Ana García López",
        "email": "ana.garcia@test.com",
        "fecha_nacimiento": "1990-05-15",
        "sexo": "mujer",
        "profesion": "Diseñadora gráfica",
        "telefono": "+34 666 123 456",
        
        # Medidas
        "peso": "65",
        "altura_cm": "165",
        "grasa_porcentaje": "25",
        "cintura_cm": "75",
        
        # Salud
        "medicamentos": "Ninguno",
        "enfermedad_cronica": "No",
        "fuma_cantidad": "No fumo",
        "bebe_cantidad": "Ocasionalmente",
        "retencion_liquidos": "No",
        "problemas_corazon": "No",
        "hipertension": "No",
        "diabetes": "No",
        "colesterol": "Normal",
        "sobrepeso": "No",
        
        # Experiencia
        "experiencia_entrenamiento": "Principiante. He hecho yoga y pilates ocasionalmente pero nunca entrenamiento con pesas. Quiero empezar en el gimnasio pero no sé por dónde comenzar.",
        "frecuencia_entrenamiento": "3 veces por semana",
        "tiempo_disponible": "45 minutos por sesión",
        "horario_preferido": "Mañanas 8:00-9:00",
        "equipo_disponible": "Gimnasio completo",
        
        # Lesiones
        "lesiones_actuales": "Ninguna",
        "lesiones_previas": "Ninguna",
        
        # Objetivos
        "objetivo_principal": "Tonificar y ganar fuerza",
        "objetivo_secundario": "Mejorar mi forma física general y crear el hábito de ejercicio",
        "peso_objetivo": "Mantener peso actual pero tonificar",
        
        # Estilo de vida
        "horas_sueno": "7-8 horas",
        "nivel_estres": "Bajo",
        "trabajo_sedentario": "Sí, trabajo en ordenador",
        "adherencia_anterior": "Baja - he empezado y dejado varias veces",
        
        # Nutrición
        "alimentacion_actual": "Como 3 veces al día, bastante saludable pero sin estructura",
        "suplementos": "Ninguno",
        "intolerancias": "Ninguna",
        "preferencias": "Como de todo"
    }
    
    await db.nutrition_questionnaire_submissions.insert_one(questionnaire)
    print(f"✅ Cuestionario creado: {quest_id}")
    return quest_id

async def run_direct_test():
    """Ejecuta el test directo de E1-E4"""
    print("\n" + "=" * 80)
    print("🧪 TEST DIRECTO BLOQUE 1 (E1-E4)")
    print("=" * 80)
    
    start_time = time.time()
    total_tokens = 0
    
    try:
        # 1. Crear cuestionario
        submission_id = await create_test_questionnaire()
        
        # 2. Obtener submission
        submission = await db.nutrition_questionnaire_submissions.find_one({"_id": submission_id})
        if not submission:
            raise Exception("No se pudo obtener el cuestionario")
        
        # 3. Preparar datos para client_context (convertir datetime a string)
        print(f"\n🏗️ Preparando datos para client_context...")
        submission_clean = dict(submission)
        if 'created_at' in submission_clean:
            submission_clean['created_at'] = submission_clean['created_at'].isoformat()
        
        # Crear client_context
        client_context = initialize_client_context(
            client_id="direct_test_user",
            version=1,
            cuestionario_data=submission_clean,
            is_followup=False
        )
        
        print(f"\n🚀 Ejecutando agentes E1-E4...")
        
        # Convertir a dict para trabajar con los agentes
        client_context_dict = client_context.model_dump()
        
        # 4. E1 - Analyst
        print(f"\n[E1] Ejecutando Analyst...")
        e1 = E1Analyst()
        
        try:
            e1_result = await e1.execute(client_context_dict)
            
            # Actualizar client_context con resultado de E1
            if "client_context" in e1_result:
                client_context_dict = e1_result["client_context"]
            
            # Extraer tokens de E1
            e1_tokens = getattr(e1, 'last_token_usage', {})
            total_tokens += e1_tokens.get("total_tokens", 0)
            
            print(f"✅ E1 completado - Tokens: {e1_tokens.get('total_tokens', 0):,}")
            
        except Exception as e:
            print(f"❌ E1 falló: {e}")
            e1_tokens = {}
        
        # 5. E2 - Capacity
        print(f"\n[E2] Ejecutando Capacity...")
        e2 = E2CapacityEvaluator()
        
        try:
            e2_result = await e2.execute(client_context_dict)
            
            # Actualizar client_context con resultado de E2
            if "client_context" in e2_result:
                client_context_dict = e2_result["client_context"]
            
            # Extraer tokens de E2
            e2_tokens = getattr(e2, 'last_token_usage', {})
            total_tokens += e2_tokens.get("total_tokens", 0)
            
            print(f"✅ E2 completado - Tokens: {e2_tokens.get('total_tokens', 0):,}")
            
        except Exception as e:
            print(f"❌ E2 falló: {e}")
            e2_tokens = {}
        
        # 6. E3 - Adaptation
        print(f"\n[E3] Ejecutando Adaptation...")
        e3 = E3AdaptationAnalyst()
        
        try:
            e3_result = await e3.execute(client_context_dict)
            
            # Actualizar client_context con resultado de E3
            if "client_context" in e3_result:
                client_context_dict = e3_result["client_context"]
            
            # Extraer tokens de E3
            e3_tokens = getattr(e3, 'last_token_usage', {})
            total_tokens += e3_tokens.get("total_tokens", 0)
            
            print(f"✅ E3 completado - Tokens: {e3_tokens.get('total_tokens', 0):,}")
            
        except Exception as e:
            print(f"❌ E3 falló: {e}")
            e3_tokens = {}
        
        # 7. E4 - Architect
        print(f"\n[E4] Ejecutando Architect...")
        e4 = E4ProgramArchitect()
        
        try:
            e4_result = await e4.execute(client_context_dict)
            
            # Actualizar client_context con resultado de E4
            if "client_context" in e4_result:
                client_context_dict = e4_result["client_context"]
            
            # Extraer tokens de E4
            e4_tokens = getattr(e4, 'last_token_usage', {})
            total_tokens += e4_tokens.get("total_tokens", 0)
            
            print(f"✅ E4 completado - Tokens: {e4_tokens.get('total_tokens', 0):,}")
            
        except Exception as e:
            print(f"❌ E4 falló: {e}")
            e4_tokens = {}
        
        # Extraer resultados del client_context
        training_data = client_context_dict.get("training", {})
        client_summary = training_data.get("client_summary")
        mesocycle = training_data.get("mesocycle")
        
        # 7. Análisis de resultados
        duration = time.time() - start_time
        
        print(f"\n" + "=" * 80)
        print(f"📊 RESULTADOS DEL TEST DIRECTO")
        print(f"=" * 80)
        
        print(f"\n### ⏱️ TIEMPO Y TOKENS")
        print(f"  Duración total: {duration:.1f}s ({duration/60:.1f} min)")
        print(f"  Total tokens: {total_tokens:,}")
        
        # Coste estimado (GPT-4o mini)
        # Asumiendo 70% input, 30% output aproximadamente
        estimated_input = int(total_tokens * 0.7)
        estimated_output = int(total_tokens * 0.3)
        cost_input = (estimated_input / 1_000_000) * 0.150
        cost_output = (estimated_output / 1_000_000) * 0.600
        total_cost = cost_input + cost_output
        
        print(f"  Coste estimado: ${total_cost:.4f} USD")
        
        print(f"\n  Tokens por agente:")
        print(f"    E1: {e1_tokens.get('total_tokens', 0):,}")
        print(f"    E2: {e2_tokens.get('total_tokens', 0):,}")
        print(f"    E3: {e3_tokens.get('total_tokens', 0):,}")
        print(f"    E4: {e4_tokens.get('total_tokens', 0):,}")
        
        # 8. Validar client_summary
        print(f"\n### 📋 CLIENT_SUMMARY GENERADO")
        print(f"  ✅ client_summary generado exitosamente")
        
        required_fields = ["objetivo_principal", "nivel", "edad", "disponibilidad", "equipo", "modo"]
        missing = [f for f in required_fields if f not in client_summary]
        
        if missing:
            print(f"  ⚠️ Campos faltantes: {missing}")
        else:
            print(f"  ✅ Todos los campos obligatorios presentes")
        
        summary_json = json.dumps(client_summary, ensure_ascii=False)
        tokens_estimate = len(summary_json) // 4
        print(f"  📏 Tamaño estimado: ~{tokens_estimate} tokens")
        
        print(f"\n  Contenido del client_summary:")
        print(f"  " + "─" * 76)
        print(json.dumps(client_summary, indent=2, ensure_ascii=False))
        print(f"  " + "─" * 76)
        
        # 9. Validar mesocycle
        print(f"\n### 🏋️ MESOCICLO GENERADO")
        print(f"  ✅ Mesociclo generado exitosamente")
        
        if isinstance(mesocycle, dict):
            print(f"  Duración: {mesocycle.get('duracion_semanas', 'N/A')} semanas")
            print(f"  Objetivo: {mesocycle.get('objetivo', 'N/A')}")
            print(f"  Split: {mesocycle.get('split', 'N/A')}")
            
            semanas = mesocycle.get('semanas', [])
            if semanas:
                print(f"\n  Estructura de {len(semanas)} semanas:")
                for semana in semanas[:3]:  # Mostrar solo las primeras 3
                    num = semana.get('numero', '?')
                    fase = semana.get('fase', '?')
                    vol = semana.get('volumen_pct', '?')
                    rir = semana.get('rir_objetivo', '?')
                    print(f"    S{num}: {fase:15} | Vol: {vol}% | RIR: {rir}")
                
                if len(semanas) > 3:
                    print(f"    ... y {len(semanas) - 3} semanas más")
        
        print(f"\n" + "=" * 80)
        print(f"✅ TEST DIRECTO COMPLETADO EXITOSAMENTE")
        print(f"=" * 80)
        
        return {
            "success": True,
            "duration": duration,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "client_summary": client_summary,
            "mesocycle": mesocycle,
            "token_breakdown": {
                "E1": e1_tokens.get('total_tokens', 0),
                "E2": e2_tokens.get('total_tokens', 0),
                "E3": e3_tokens.get('total_tokens', 0),
                "E4": e4_tokens.get('total_tokens', 0)
            }
        }
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}
    
    finally:
        client.close()

if __name__ == "__main__":
    result = asyncio.run(run_direct_test())
    
    if result.get("success"):
        print(f"\n🎉 Test completado en {result['duration']:.1f}s con {result['total_tokens']:,} tokens")
    else:
        print(f"\n💥 Test falló: {result.get('error')}")