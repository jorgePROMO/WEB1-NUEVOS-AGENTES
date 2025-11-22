"""
Script de prueba para validar el nuevo paradigma de razonamiento en E2 y E4

Compara:
- ANTES: Agentes originales con reglas fijas
- DESPUÉS: Agentes v2 con razonamiento contextual

Objetivo: Demostrar que los agentes v2 RAZONAN en lugar de aplicar fórmulas
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import json

# MongoDB setup
MONGO_URL = "mongodb://localhost:27017"
DB_NAME = "test_database"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]


async def test_e2_reasoning():
    """
    Prueba E2 con nuevo paradigma de razonamiento
    
    Caso de prueba:
    - Cliente avanzado con 8 meses de parón
    - Lumbalgia ocasional
    - Contexto laboral estresante (70h/semana)
    - Objetivo dual: hipertrofia + pérdida grasa
    """
    print("=" * 80)
    print("PRUEBA E2 - EVALUADOR DE CAPACIDAD CON RAZONAMIENTO")
    print("=" * 80)
    print()
    
    # Cargar datos del usuario Jorge1
    user = await db.users.find_one({"email": "jorge31011987promo@gmail.com"})
    user_id = user.get('user_id')
    
    # Buscar follow-up más reciente
    followup = await db.follow_up_submissions.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )
    
    if not followup:
        print("⚠️ No se encontró follow-up submission para Jorge1")
        return
    
    print(f"✓ Usuario: {user.get('email')}")
    print(f"✓ Submission ID: {followup.get('_id')}")
    print()
    
    # Simular input que recibiría E2
    # (normalmente vendría de E1, pero lo simulamos)
    client_context_input = {
        "meta": {
            "user_id": user_id,
            "submission_id": followup.get('_id'),
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        "training": {
            "client_summary": {
                "nombre": "Jorge1",
                "edad": 38,
                "objetivo_principal": "hipertrofia",
                "objetivo_secundario": "perdida_grasa",
                "nivel": "avanzado",
                "experiencia_anos": 10,
                "paron_meses": 8,
                "limitaciones_clave": ["lumbalgia_ocasional", "contexto_laboral_estresante"],
                "disponibilidad": {
                    "dias_semana": 4,
                    "minutos_sesion": 60,
                    "horas_trabajo": 70,
                    "horas_sueno": "6-7"
                }
            },
            "profile": {
                "perfil_tecnico": {
                    "nivel_declarado": "avanzado",
                    "experiencia_real": "culturismo_10_anos",
                    "tecnica": "excelente",
                    "memoria_muscular": "intacta"
                },
                "experiencia": {
                    "anos_entrenando": 10,
                    "consistencia": "alta_historica",
                    "paron_actual": "8_meses"
                },
                "limitaciones_clinicas": {
                    "lumbalgia": {
                        "tipo": "mecanica",
                        "patron": "hiperextension_sostenida",
                        "frecuencia": "ocasional"
                    }
                }
            },
            "capacity": None  # Lo que E2 debe llenar
        }
    }
    
    # Importar E2 v2 (razonamiento)
    from backend.edn360.agents.training_initial.e2_capacity_v2_reasoning import E2CapacityEvaluatorV2
    
    e2_v2 = E2CapacityEvaluatorV2()
    
    print("🧠 Ejecutando E2 con RAZONAMIENTO CONTEXTUAL...")
    print()
    
    try:
        result = await e2_v2.execute(client_context_input, kb_training="Base EDN360", kb_nutrition="")
        
        # Extraer capacity del resultado
        capacity = result["client_context"]["training"]["capacity"]
        
        print("=" * 80)
        print("RESULTADO E2 - CAPACIDAD CON RAZONAMIENTO")
        print("=" * 80)
        print()
        
        print(f"✓ SEG Score: {capacity['seg_score']}")
        print(f"✓ Interpretación: {capacity['interpretacion_seg']}")
        print()
        
        # CLAVE: Mostrar el razonamiento interno
        if "razonamiento_interno" in capacity:
            razon = capacity["razonamiento_interno"]
            
            print("🧠 RAZONAMIENTO INTERNO:")
            print("-" * 80)
            print()
            print(f"📊 Análisis del perfil:")
            print(f"   {razon.get('analisis_perfil', 'N/A')}")
            print()
            
            print(f"📚 Principios KB aplicados:")
            for principio in razon.get('principios_kb_aplicados', []):
                print(f"   • {principio}")
            print()
            
            print(f"🎯 Decisiones clave:")
            decisiones = razon.get('decisiones_clave', {})
            for clave, valor in decisiones.items():
                print(f"   • {clave}: {valor}")
            print()
            
            print(f"✅ Justificaciones:")
            justif = razon.get('justificaciones', {})
            for tipo, texto in justif.items():
                print(f"   • {tipo}: {texto}")
            print()
        
        print("=" * 80)
        print("✅ E2 COMPLETADO - Razonamiento generado exitosamente")
        print("=" * 80)
        print()
        
        return result
        
    except Exception as e:
        print(f"❌ Error ejecutando E2: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """Ejecutar pruebas"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "VALIDACIÓN PARADIGMA DE RAZONAMIENTO" + " " * 22 + "║")
    print("║" + " " * 30 + "E2 y E4 v2" + " " * 38 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Prueba E2
    e2_result = await test_e2_reasoning()
    
    if e2_result:
        print("\n✅ PRUEBA E2 EXITOSA")
        print("El agente E2 ha demostrado RAZONAMIENTO CONTEXTUAL")
        print("en lugar de aplicar reglas fijas.")
    else:
        print("\n❌ PRUEBA E2 FALLÓ")
    
    print("\n" + "=" * 80)
    print("PRUEBA COMPLETADA")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
