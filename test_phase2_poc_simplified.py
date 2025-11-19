"""
PROOF OF CONCEPT SIMPLIFICADO - FASE 2
Test de E1, E5 y E8 funcionando con client_context

Este script demuestra que los 3 agentes refactorizados funcionan correctamente:
1. E1 procesa el cuestionario y llena profile, constraints, prehab
2. E5 genera sesiones (usando datos dummy para mesocycle)
3. E8 audita el plan (usando datos dummy para los campos que necesita)
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

if not os.getenv('OPENAI_API_KEY'):
    print("❌ ERROR: OPENAI_API_KEY no encontrada")
    sys.exit(1)

sys.path.insert(0, '/app/backend')

from edn360.client_context_models import ClientContext
from edn360.client_context_utils import initialize_client_context, client_context_to_dict
from edn360.agents.training_initial.e1_analyst import E1Analyst
from edn360.agents.training_initial.e5_engineer import E5MicrocycleEngineer
from edn360.agents.training_initial.e8_auditor import E8TechnicalAuditor

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_realistic_questionnaire():
    """Crea cuestionario realista"""
    return {
        "client_id": "client_juan_test",
        "version": 1,
        "nombre": "Juan Pérez",
        "edad": 32,
        "sexo": "M",
        "peso_actual_kg": 78,
        "altura_cm": 175,
        "objetivo_principal": "hipertrofia",
        "experiencia_entrenamiento": "intermedio",
        "dias_disponibles": 4,
        "minutos_por_sesion": 60,
        "horario_preferido": "tarde",
        "hora_especifica": "18:00",
        "equipo_disponible": "gym completo",
        "lesiones_activas": [{"zona": "lumbar", "gravedad": "leve"}],
        "nivel_estres": "medio",
        "horas_sueno_promedio": 7,
    }


def load_training_kb():
    """Carga KB de entrenamiento"""
    kb_path = "/app/backend/edn360/knowledge_bases/training_knowledge_base_v1.0.txt"
    with open(kb_path, 'r', encoding='utf-8') as f:
        return f.read()


async def test_e1():
    """Test E1 - Analista"""
    logger.info("=" * 80)
    logger.info("🧪 TEST E1 - ANALISTA")
    logger.info("=" * 80)
    
    # Crear cuestionario
    questionnaire = create_realistic_questionnaire()
    logger.info(f"✅ Cuestionario: {questionnaire['nombre']}, {questionnaire['edad']} años")
    
    # Inicializar client_context
    client_context = initialize_client_context(
        client_id=questionnaire["client_id"],
        version=1,
        cuestionario_data=questionnaire,
        is_followup=False
    )
    logger.info(f"✅ client_context inicializado: {client_context.meta.snapshot_id}")
    
    # Guardar context inicial
    with open('/app/debug_context_before_e1.json', 'w') as f:
        json.dump(client_context_to_dict(client_context), f, indent=2)
    
    # Ejecutar E1
    kb = load_training_kb()
    e1 = E1Analyst()
    
    logger.info("\n▶️ Ejecutando E1...")
    result = await e1.execute(client_context_to_dict(client_context), knowledge_base=kb)
    
    if not result["success"]:
        logger.error(f"❌ E1 falló: {result.get('error')}")
        return None
    
    # Extraer client_context actualizado
    client_context_updated = ClientContext.model_validate(result["output"]["client_context"])
    
    logger.info("✅ E1 completado")
    logger.info(f"   - profile lleno: {client_context_updated.training.profile is not None}")
    logger.info(f"   - constraints lleno: {client_context_updated.training.constraints is not None}")
    logger.info(f"   - prehab lleno: {client_context_updated.training.prehab is not None}")
    
    # Guardar
    with open('/app/debug_context_after_e1.json', 'w') as f:
        json.dump(client_context_to_dict(client_context_updated), f, indent=2)
    
    return client_context_updated


async def test_e5(client_context: ClientContext):
    """Test E5 - Ingeniero de Sesiones"""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 TEST E5 - INGENIERO DE SESIONES")
    logger.info("=" * 80)
    
    # E5 necesita mesocycle, vamos a crear uno dummy
    dummy_mesocycle = {
        "duracion_semanas": 4,
        "split": "upper/lower",
        "fases": {
            "semana_1": {"intensidad": "acumulacion", "volumen": "100%"},
            "semana_2": {"intensidad": "acumulacion", "volumen": "105%"},
            "semana_3": {"intensidad": "intensificacion", "volumen": "95%"},
            "semana_4": {"intensidad": "deload", "volumen": "60%"}
        },
        "volumen_por_grupo": {
            "pecho": 16,
            "espalda": 16,
            "piernas": 16,
            "hombros": 12
        }
    }
    
    client_context.training.mesocycle = dummy_mesocycle
    logger.info("✅ Mesocycle dummy añadido para E5")
    
    # Ejecutar E5
    kb = load_training_kb()
    e5 = E5MicrocycleEngineer()
    
    logger.info("\n▶️ Ejecutando E5...")
    result = await e5.execute(client_context_to_dict(client_context), knowledge_base=kb)
    
    if not result["success"]:
        logger.error(f"❌ E5 falló: {result.get('error')}")
        return None
    
    client_context_updated = ClientContext.model_validate(result["output"]["client_context"])
    
    logger.info("✅ E5 completado")
    logger.info(f"   - sessions lleno: {client_context_updated.training.sessions is not None}")
    
    # Guardar
    with open('/app/debug_context_after_e5.json', 'w') as f:
        json.dump(client_context_to_dict(client_context_updated), f, indent=2)
    
    return client_context_updated


async def test_e8(client_context: ClientContext):
    """Test E8 - Auditor"""
    logger.info("\n" + "=" * 80)
    logger.info("🧪 TEST E8 - AUDITOR")
    logger.info("=" * 80)
    
    # E8 necesita safe_sessions y capacity, añadimos dummy
    client_context.training.safe_sessions = client_context.training.sessions  # Usar sessions como safe_sessions
    client_context.training.capacity = {
        "volumen_tolerable": "medio",
        "intensidad": "RIR 2-3"
    }
    logger.info("✅ Datos dummy añadidos para E8 (capacity, safe_sessions)")
    
    # Ejecutar E8
    kb = load_training_kb()
    e8 = E8TechnicalAuditor()
    
    logger.info("\n▶️ Ejecutando E8...")
    result = await e8.execute(client_context_to_dict(client_context), knowledge_base=kb)
    
    if not result["success"]:
        logger.error(f"❌ E8 falló: {result.get('error')}")
        return None
    
    client_context_updated = ClientContext.model_validate(result["output"]["client_context"])
    
    logger.info("✅ E8 completado")
    logger.info(f"   - audit lleno: {client_context_updated.training.audit is not None}")
    
    # Guardar
    with open('/app/debug_context_after_e8.json', 'w') as f:
        json.dump(client_context_to_dict(client_context_updated), f, indent=2)
    
    return client_context_updated


async def main():
    """Ejecuta el PoC completo"""
    logger.info("🚀 PROOF OF CONCEPT SIMPLIFICADO - FASE 2")
    logger.info("Probando E1 → E5 → E8 con client_context unificado\n")
    
    try:
        # Test E1
        context = await test_e1()
        if not context:
            return False
        
        # Test E5
        context = await test_e5(context)
        if not context:
            return False
        
        # Test E8
        context = await test_e8(context)
        if not context:
            return False
        
        # Resumen final
        logger.info("\n" + "=" * 80)
        logger.info("🎉 PoC COMPLETADO EXITOSAMENTE")
        logger.info("=" * 80)
        logger.info("\n📊 RESUMEN DE CAMPOS LLENADOS:")
        logger.info(f"   ✅ E1 - profile: {context.training.profile is not None}")
        logger.info(f"   ✅ E1 - constraints: {context.training.constraints is not None}")
        logger.info(f"   ✅ E1 - prehab: {context.training.prehab is not None}")
        logger.info(f"   ✅ E5 - sessions: {context.training.sessions is not None}")
        logger.info(f"   ✅ E8 - audit: {context.training.audit is not None}")
        
        logger.info("\n📁 ARCHIVOS GENERADOS:")
        logger.info("   1. /app/debug_context_before_e1.json")
        logger.info("   2. /app/debug_context_after_e1.json")
        logger.info("   3. /app/debug_context_after_e5.json")
        logger.info("   4. /app/debug_context_after_e8.json")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ ERROR: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
