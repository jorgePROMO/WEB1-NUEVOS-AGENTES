"""
PROOF OF CONCEPT - FASE 2
Test del flujo E1 → E5 → E8 con client_context unificado

Este script:
1. Crea un cuestionario realista
2. Ejecuta el flujo completo de entrenamiento inicial
3. Guarda client_context antes y después
4. Muestra logs de validaciones
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Cargar variables de entorno del .env
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

# Verificar que OPENAI_API_KEY está cargada
if not os.getenv('OPENAI_API_KEY'):
    print("❌ ERROR: OPENAI_API_KEY no encontrada en el entorno")
    sys.exit(1)

# Añadir path del backend
sys.path.insert(0, '/app/backend')

from edn360.orchestrator import EDN360Orchestrator
from edn360.client_context_utils import client_context_to_dict

# Configurar logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_realistic_questionnaire():
    """Crea un cuestionario realista de ejemplo"""
    return {
        "client_id": "client_juan_perez_test",
        "version": 1,
        "timestamp": datetime.now().isoformat(),
        
        # Datos personales
        "nombre": "Juan Pérez",
        "edad": 32,
        "sexo": "M",
        "peso_actual_kg": 78,
        "altura_cm": 175,
        
        # Objetivo
        "objetivo_principal": "hipertrofia",
        "objetivo_secundario": "mejorar composicion corporal",
        "plazo": "6 meses",
        
        # Experiencia
        "experiencia_entrenamiento": "3 años gym intermitente",
        "nivel_estimado": "intermedio",
        "deportes_previos": ["futbol", "gym"],
        
        # Disponibilidad
        "dias_disponibles": 4,
        "minutos_por_sesion": 60,
        "horario_preferido": "tarde",
        "hora_especifica": "18:00",
        "flexibilidad_horaria": "media",
        
        # Equipo
        "equipo_disponible": "gym completo",
        "equipamiento_especifico": [
            "mancuernas", "barra", "rack", "maquinas", 
            "poleas", "banco", "discos"
        ],
        
        # Lesiones y limitaciones
        "lesiones_previas": "dolor lumbar leve ocasional",
        "lesiones_activas": [
            {
                "zona": "lumbar",
                "tipo": "dolor_ocasional",
                "gravedad": "leve",
                "descripcion": "Aparece con mala técnica o sobrecarga"
            }
        ],
        "restricciones_medicas": [],
        
        # Estilo de vida
        "trabajo": "oficina sedentario",
        "nivel_estres": "medio",
        "horas_sueno_promedio": 7,
        "calidad_sueno": "buena",
        
        # Nutrición actual
        "nutricion_actual": "desordenada, sin seguimiento",
        "comidas_dia": 3,
        "agua_litros": 2,
        
        # Adherencia histórica
        "adherencia_historica": "irregular",
        "motivo_abandono_previo": "falta de plan estructurado",
        
        # Contexto adicional
        "motivacion": "alta",
        "apoyo_familiar": "bueno",
        "presupuesto_suplementos": "medio",
        
        # Notas del entrenador
        "notas_entrenador": "Cliente motivado, necesita estructura y seguimiento. Buen potencial."
    }


async def run_poc_test():
    """
    Ejecuta el Proof of Concept completo
    """
    logger.info("=" * 80)
    logger.info("🚀 INICIANDO PROOF OF CONCEPT - FASE 2")
    logger.info("=" * 80)
    
    # PASO 1: Crear cuestionario de prueba
    logger.info("\n📋 PASO 1: Creando cuestionario realista...")
    questionnaire = create_realistic_questionnaire()
    
    # Guardar cuestionario de input
    with open('/app/debug_input_questionnaire.json', 'w', encoding='utf-8') as f:
        json.dump(questionnaire, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Cuestionario guardado en: /app/debug_input_questionnaire.json")
    logger.info(f"   Cliente: {questionnaire['nombre']}, {questionnaire['edad']} años")
    logger.info(f"   Objetivo: {questionnaire['objetivo_principal']}")
    logger.info(f"   Disponibilidad: {questionnaire['dias_disponibles']} días x {questionnaire['minutos_por_sesion']} min")
    
    # PASO 2: Inicializar orchestrator
    logger.info("\n🔧 PASO 2: Inicializando orchestrator...")
    orchestrator = EDN360Orchestrator()
    logger.info("✅ Orchestrator inicializado")
    logger.info(f"   KBs cargadas: Training ({len(orchestrator.knowledge_bases['training'])} chars)")
    
    # PASO 3: Ejecutar flujo de entrenamiento inicial
    logger.info("\n⚙️ PASO 3: Ejecutando flujo E1 → E9...")
    logger.info("   Nota: E2, E3, E4, E6, E7, E9 son legacy, se simularán con datos dummy")
    logger.info("")
    
    try:
        result = await orchestrator._execute_training_initial(
            questionnaire_data=questionnaire,
            previous_plan=None
        )
        
        if not result["success"]:
            logger.error(f"❌ Flujo falló: {result.get('error')}")
            return False
        
        logger.info("\n✅ FLUJO COMPLETADO EXITOSAMENTE")
        
        # PASO 4: Guardar client_context final
        logger.info("\n💾 PASO 4: Guardando resultados...")
        
        client_context_final = result.get("client_context")
        
        if client_context_final:
            # Guardar client_context completo
            with open('/app/debug_client_context_final.json', 'w', encoding='utf-8') as f:
                json.dump(client_context_final, f, indent=2, ensure_ascii=False)
            logger.info("✅ client_context final guardado en: /app/debug_client_context_final.json")
            
            # Verificar campos llenados
            training = client_context_final.get("training", {})
            
            logger.info("\n📊 VERIFICACIÓN DE CAMPOS:")
            logger.info(f"   ✅ E1 - profile: {'✓ Llenado' if training.get('profile') else '✗ Vacío'}")
            logger.info(f"   ✅ E1 - constraints: {'✓ Llenado' if training.get('constraints') else '✗ Vacío'}")
            logger.info(f"   ✅ E1 - prehab: {'✓ Llenado' if training.get('prehab') else '✗ Vacío'}")
            logger.info(f"   ⚠️  E2 - capacity: {'✓ Llenado' if training.get('capacity') else '✗ Vacío (legacy)'}")
            logger.info(f"   ⚠️  E3 - adaptation: {'✓ Llenado' if training.get('adaptation') else '✗ Vacío (legacy)'}")
            logger.info(f"   ⚠️  E4 - mesocycle: {'✓ Llenado' if training.get('mesocycle') else '✗ Vacío (legacy)'}")
            logger.info(f"   ✅ E5 - sessions: {'✓ Llenado' if training.get('sessions') else '✗ Vacío'}")
            logger.info(f"   ⚠️  E6 - safe_sessions: {'✓ Llenado' if training.get('safe_sessions') else '✗ Vacío (legacy)'}")
            logger.info(f"   ⚠️  E7 - formatted_plan: {'✓ Llenado' if training.get('formatted_plan') else '✗ Vacío (legacy)'}")
            logger.info(f"   ✅ E8 - audit: {'✓ Llenado' if training.get('audit') else '✗ Vacío'}")
            logger.info(f"   ⚠️  E9 - bridge: {'✓ Llenado' if training.get('bridge_for_nutrition') else '✗ Vacío (legacy)'}")
        
        # PASO 5: Resumen de ejecuciones
        logger.info("\n🔍 PASO 5: Resumen de ejecuciones:")
        executions = result.get("executions", [])
        for execution in executions:
            agent_id = execution.get("agent_id", "Unknown")
            success = execution.get("success", False)
            duration = execution.get("duration_seconds", 0)
            status_icon = "✅" if success else "❌"
            logger.info(f"   {status_icon} {agent_id}: {duration:.2f}s")
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 PROOF OF CONCEPT COMPLETADO")
        logger.info("=" * 80)
        logger.info("\n📁 Archivos generados:")
        logger.info("   1. /app/debug_input_questionnaire.json - Input del test")
        logger.info("   2. /app/debug_client_context_final.json - Output completo")
        logger.info("\n✅ Revisa estos archivos para validar el flujo")
        
        return True
        
    except Exception as e:
        logger.error(f"\n❌ ERROR EN EL FLUJO: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


async def main():
    """Función principal"""
    success = await run_poc_test()
    
    if success:
        print("\n✅ PoC ejecutado exitosamente")
        sys.exit(0)
    else:
        print("\n❌ PoC falló")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
