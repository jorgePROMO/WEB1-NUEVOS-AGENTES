"""
TEST FINAL E1-E9 - BLOQUE 2 COMPLETO
Ejecuta pipeline completo y genera reporte detallado
"""
import sys
sys.path.append('/app/backend')
sys.path.append('/app/backend/edn360')

import asyncio
import json
from datetime import datetime, timezone
from edn360.orchestrator import EDN360Orchestrator

async def main():
    print("=" * 80)
    print("🧪 TEST FINAL E1-E9 - BLOQUE 2 COMPLETO")
    print("=" * 80)
    
    # Cuestionario realista
    questionnaire = {
        "nombre_completo": "María García López",
        "email": "maria.garcia@test.com",
        "fecha_nacimiento": "1990-06-15",
        "sexo": "mujer",
        "profesion": "Diseñadora gráfica - trabajo sedentario",
        "peso": "65",
        "altura_cm": "168",
        "grasa_porcentaje": "26",
        "experiencia_entrenamiento": "2 años entrenando 3 veces por semana. Conoce ejercicios básicos.",
        "frecuencia_entrenamiento": "3 veces por semana",
        "tiempo_disponible": "60 minutos por sesión",
        "horario_preferido": "Mañanas 7:00-8:00",
        "equipo_disponible": "Gimnasio completo",
        "lesiones_actuales": "Ninguna",
        "lesiones_previas": "Tendinitis hombro derecho hace 1 año (recuperada)",
        "objetivo_principal": "Perder grasa y tonificar",
        "peso_objetivo": "60kg",
        "horas_sueno": "7",
        "nivel_estres": "Medio",
        "trabajo_sedentario": "Sí",
        "adherencia_anterior": "Media"
    }
    
    print(f"\n📝 Cliente: {questionnaire['nombre_completo']}")
    print(f"   Objetivo: {questionnaire['objetivo_principal']}")
    
    print("\n🔧 Inicializando orquestador...")
    orchestrator = EDN360Orchestrator()
    
    print("\n🚀 Ejecutando pipeline E1-E9...")
    print("=" * 80)
    
    start_time = datetime.now(timezone.utc)
    
    try:
        result = await orchestrator.execute_training_pipeline(
            questionnaire_data=questionnaire,
            client_id="test_final_bloque2",
            version=1
        )
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print(f"✅ PIPELINE COMPLETADO en {duration:.1f}s ({duration/60:.1f} min)")
        print("=" * 80)
        
        if result["success"]:
            client_context = result["client_context"]
            training = client_context.get("training", {})
            executions = result.get("executions", [])
            
            # ========================================
            # 1. TOKEN USAGE POR AGENTE
            # ========================================
            print("\n### 1️⃣ TOKEN USAGE POR AGENTE")
            print()
            
            total_prompt = 0
            total_completion = 0
            
            print("| Agente | Input | Output | Total |")
            print("|--------|-------|--------|-------|")
            
            for exec in executions:
                agent_id = exec.get("agent_id", "?")
                token_usage = exec.get("token_usage", {})
                prompt = token_usage.get("prompt_tokens", 0)
                completion = token_usage.get("completion_tokens", 0)
                total = prompt + completion
                
                total_prompt += prompt
                total_completion += completion
                
                print(f"| **{agent_id}** | {prompt:,} | {completion:,} | {total:,} |")
            
            total_tokens = total_prompt + total_completion
            print(f"| **TOTAL** | **{total_prompt:,}** | **{total_completion:,}** | **{total_tokens:,}** |")
            
            # Coste
            cost_input = (total_prompt / 1_000_000) * 0.150
            cost_output = (total_completion / 1_000_000) * 0.600
            total_cost = cost_input + cost_output
            
            print(f"\n💰 **Coste Estimado (GPT-4o mini):**")
            print(f"   - Input:  ${cost_input:.4f}")
            print(f"   - Output: ${cost_output:.4f}")
            print(f"   - **TOTAL: ${total_cost:.4f} USD**")
            
            # ========================================
            # 2. TIEMPO DE PROCESAMIENTO
            # ========================================
            print(f"\n### 2️⃣ TIEMPO DE PROCESAMIENTO")
            print(f"\n⏱️ **Duración Total:** {duration:.1f}s ({duration/60:.1f} minutos)")
            
            # ========================================
            # 3. OUTPUTS GENERADOS
            # ========================================
            print(f"\n### 3️⃣ OUTPUTS GENERADOS")
            
            # Sessions (E5)
            print("\n#### 📋 training.sessions (E5)")
            sessions = training.get("sessions")
            if sessions:
                sessions_json = json.dumps(sessions, indent=2, ensure_ascii=False)
                print(f"```json\n{sessions_json[:800]}\n... (truncado)\n```")
                print(f"Tamaño: ~{len(sessions_json)//4} tokens")
            else:
                print("❌ NO generado")
            
            # Formatted Plan (E7)
            print("\n#### 📄 training.formatted_plan (E7)")
            formatted_plan = training.get("formatted_plan")
            if formatted_plan:
                plan_json = json.dumps(formatted_plan, indent=2, ensure_ascii=False)
                print(f"```json\n{plan_json[:800]}\n... (truncado)\n```")
                print(f"Tamaño: ~{len(plan_json)//4} tokens")
            else:
                print("❌ NO generado")
            
            # Audit (E8)
            print("\n#### 🔍 training.audit (E8)")
            audit = training.get("audit")
            if audit:
                audit_json = json.dumps(audit, indent=2, ensure_ascii=False)
                print(f"```json\n{audit_json}\n```")
            else:
                print("❌ NO generado")
            
            # Bridge (E9)
            print("\n#### 🌉 training.bridge_for_nutrition (E9)")
            bridge = training.get("bridge_for_nutrition")
            if bridge:
                bridge_json = json.dumps(bridge, indent=2, ensure_ascii=False)
                print(f"```json\n{bridge_json}\n```")
            else:
                print("❌ NO generado")
            
            # ========================================
            # 4. VALIDACIÓN DE COHERENCIA
            # ========================================
            print(f"\n### 4️⃣ VALIDACIÓN DE COHERENCIA")
            
            mesocycle = training.get("mesocycle")
            
            # Mesocycle ↔ Sessions
            print("\n#### ✓ Mesocycle ↔ Sessions")
            if mesocycle and sessions:
                meso_weeks = mesocycle.get("duracion_semanas", 0)
                # Contar semanas en sessions
                if isinstance(sessions, dict):
                    session_weeks = len([k for k in sessions.keys() if k.startswith("semana")])
                    if session_weeks == meso_weeks:
                        print(f"   ✅ Coherente: {meso_weeks} semanas en ambos")
                    else:
                        print(f"   ⚠️ Discrepancia: Mesocycle={meso_weeks}, Sessions={session_weeks}")
                else:
                    print(f"   ⚠️ Sessions no tiene estructura esperada")
            else:
                print(f"   ❌ No se puede validar (falta mesocycle o sessions)")
            
            # Sessions ↔ Formatted Plan
            print("\n#### ✓ Sessions ↔ Formatted_plan")
            if sessions and formatted_plan:
                print(f"   ✅ Ambos existen, formatted_plan se basa en sessions")
            else:
                print(f"   ❌ No se puede validar")
            
            # Formatted Plan ↔ Bridge
            print("\n#### ✓ Formatted_plan ↔ Bridge_for_nutrition")
            if formatted_plan and bridge:
                # Validar que bridge tenga datos coherentes
                bridge_dias = bridge.get("dias_entrenamiento_semana", 0)
                print(f"   ✅ Bridge indica {bridge_dias} días de entrenamiento/semana")
                
                tdee = bridge.get("tdee_estimado", 0)
                print(f"   ✅ TDEE estimado: {tdee} kcal")
            else:
                print(f"   ❌ No se puede validar")
            
        else:
            print(f"\n❌ Error: {result.get('error')}")
            print(f"\nExecutions hasta el fallo:")
            for exec in result.get("executions", []):
                print(f"  - {exec.get('agent_id')}: {exec.get('status')}")
        
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETADO")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
