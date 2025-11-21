"""
Test directo del orquestador - sin worker, sin jobs, solo ejecutar E1-E4
"""
import sys
sys.path.append('/app/backend')
sys.path.append('/app/backend/edn360')

import asyncio
import json
from datetime import datetime, timezone

# Import orquestrador
from edn360.orchestrator import EDN360Orchestrator

async def main():
    print("=" * 80)
    print("🧪 TEST DIRECTO E1-E4 - SIN WORKER")
    print("=" * 80)
    
    # Cuestionario de prueba
    questionnaire = {
        "nombre_completo": "Carlos Martínez Ruiz",
        "email": "carlos.martinez@test.com",
        "fecha_nacimiento": "1988-03-20",
        "sexo": "hombre",
        "profesion": "Arquitecto - trabajo de oficina",
        "peso": "82",
        "altura_cm": "178",
        "grasa_porcentaje": "22",
        "experiencia_entrenamiento": "He entrenado 2 años en gimnasio hace 5 años. Era constante (4 días/semana) con rutina de hipertrofia. Dejé por trabajo. Hace 6 meses volví sin plan específico.",
        "frecuencia_entrenamiento": "3-4 veces por semana",
        "tiempo_disponible": "60 minutos por sesión",
        "horario_preferido": "Tardes 19:00-20:00",
        "equipo_disponible": "Gimnasio completo",
        "lesiones_actuales": "Ninguna",
        "lesiones_previas": "Tendinitis codo derecho hace 3 años (recuperada)",
        "objetivo_principal": "Ganar masa muscular y perder grasa abdominal",
        "objetivo_secundario": "Mejorar fuerza en básicos",
        "peso_objetivo": "80kg con menos grasa",
        "horas_sueno": "7-8 horas",
        "nivel_estres": "Medio",
        "trabajo_sedentario": "Sí",
        "adherencia_anterior": "Media"
    }
    
    print("\n📝 Cuestionario preparado")
    print(f"   Cliente: {questionnaire['nombre_completo']}")
    print(f"   Objetivo: {questionnaire['objetivo_principal']}")
    
    # Inicializar orquestador
    print("\n🔧 Inicializando orquestador...")
    orchestrator = EDN360Orchestrator()
    print("   ✅ Orquestador listo")
    
    # Ejecutar pipeline de training
    print("\n🚀 Ejecutando pipeline E1-E4...")
    print("=" * 80)
    
    start_time = datetime.now(timezone.utc)
    
    try:
        result = await orchestrator.execute_training_pipeline(
            questionnaire_data=questionnaire,
            client_id="test_direct_bloque1",
            version=1
        )
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print(f"✅ PIPELINE COMPLETADO en {duration:.1f}s")
        print("=" * 80)
        
        if result["success"]:
            client_context = result["client_context"]
            training = client_context.get("training", {})
            
            # 1. Client Summary
            print("\n### 1️⃣ CLIENT_SUMMARY GENERADO")
            client_summary = training.get("client_summary")
            
            if client_summary:
                print("\n" + json.dumps(client_summary, indent=2, ensure_ascii=False))
                summary_size = len(json.dumps(client_summary, ensure_ascii=False)) // 4
                print(f"\n📏 Tamaño: ~{summary_size} tokens")
            else:
                print("❌ NO generado")
            
            # 2. Mesocycle
            print("\n### 2️⃣ MESOCYCLE GENERADO")
            mesocycle = training.get("mesocycle")
            
            if mesocycle:
                print(f"\nDuración: {mesocycle.get('duracion_semanas')} semanas")
                print(f"Objetivo: {mesocycle.get('objetivo')}")
                print(f"Split: {mesocycle.get('split')}")
                
                semanas = mesocycle.get('semanas', [])
                if semanas:
                    print(f"\nEstructura de {len(semanas)} semanas:")
                    for s in semanas:
                        print(f"  S{s.get('numero')}: {s.get('fase'):15} | Vol: {s.get('volumen_pct')}% | RIR: {s.get('rir_objetivo')}")
            else:
                print("❌ NO generado")
            
            # 3. Token Usage
            print("\n### 3️⃣ TOKEN USAGE")
            executions = result.get("executions", [])
            
            total_prompt = 0
            total_completion = 0
            
            print("\nPor agente:")
            for exec in executions:
                agent_id = exec.get("agent_id", "?")
                token_usage = exec.get("token_usage", {})
                prompt = token_usage.get("prompt_tokens", 0)
                completion = token_usage.get("completion_tokens", 0)
                total = prompt + completion
                
                total_prompt += prompt
                total_completion += completion
                
                print(f"  {agent_id}: {total:,} tokens (in: {prompt:,}, out: {completion:,})")
            
            total_tokens = total_prompt + total_completion
            print(f"\n  TOTAL: {total_tokens:,} tokens")
            print(f"  └─ Input: {total_prompt:,}")
            print(f"  └─ Output: {total_completion:,}")
            
            # Coste
            cost_input = (total_prompt / 1_000_000) * 0.150
            cost_output = (total_completion / 1_000_000) * 0.600
            total_cost = cost_input + cost_output
            
            print(f"\n  💰 Coste Estimado (GPT-4o mini):")
            print(f"     Input:  ${cost_input:.4f}")
            print(f"     Output: ${cost_output:.4f}")
            print(f"     TOTAL:  ${total_cost:.4f} USD")
            
        else:
            print(f"\n❌ Error: {result.get('error')}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
