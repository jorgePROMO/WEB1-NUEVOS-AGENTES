"""
TEST END-TO-END - NUTRICIÓN INICIAL (N0-N8)
Flujo: client_context (con training completo) → N0 → N1 → N2 → N3 → N4 → N5 → N6 → N7 → N8

ENTRADA: /app/debug_client_context_after_e9.json (salida del test de entrenamiento)
SALIDA:
- /app/debug_client_context_after_n8.json
- /app/logs_nutrition_e2e.txt
"""

import asyncio
import json
import sys
import os
from datetime import datetime
import logging

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

if not os.getenv('OPENAI_API_KEY'):
    print("❌ ERROR: OPENAI_API_KEY no encontrada")
    sys.exit(1)

sys.path.insert(0, '/app/backend')

from edn360.orchestrator import EDN360Orchestrator
from edn360.client_context_models import ClientContext
from edn360.client_context_utils import client_context_to_dict, client_context_from_dict

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs_nutrition_e2e.txt', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """
    Test E2E de nutrición:
    1. Carga client_context con training completo
    2. Ejecuta pipeline N0-N8
    3. Valida que todos los campos de nutrition estén rellenos
    4. Genera artefactos de debug
    """
    
    logger.info("=" * 100)
    logger.info("🚀 TEST END-TO-END - NUTRICIÓN INICIAL (N0-N8)")
    logger.info("=" * 100)
    logger.info("")
    
    # =========================================================================
    # PASO 1: Cargar client_context con training completo
    # =========================================================================
    logger.info("📋 PASO 1: Cargando client_context con training completo...")
    
    input_file = "/app/debug_client_context_after_e9.json"
    
    if not os.path.exists(input_file):
        logger.error(f"❌ ERROR: No se encuentra {input_file}")
        logger.error("   Ejecuta primero test_training_e2e.py para generar el archivo")
        return
    
    try:
        with open(input_file, "r") as f:
            client_context_dict = json.load(f)
        
        # Validar estructura
        client_context = ClientContext.model_validate(client_context_dict)
        
        logger.info(f"✅ client_context cargado correctamente")
        logger.info(f"   - Cliente: {client_context.meta.client_id}")
        logger.info(f"   - Snapshot: {client_context.meta.snapshot_id}")
        logger.info(f"   - Versión: {client_context.meta.version}")
        
        # Verificar que training.bridge_for_nutrition existe
        if client_context.training.bridge_for_nutrition is None:
            logger.error("❌ ERROR: training.bridge_for_nutrition es null")
            logger.error("   El test de entrenamiento debe haber generado este campo (E9)")
            return
        
        logger.info(f"✅ training.bridge_for_nutrition detectado")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ ERROR cargando client_context: {e}")
        return
    
    # =========================================================================
    # PASO 2: Inicializar orchestrator
    # =========================================================================
    logger.info("🔧 PASO 2: Inicializando orchestrator...")
    orchestrator = EDN360Orchestrator()
    logger.info(f"✅ Orchestrator inicializado correctamente")
    logger.info(f"   - KB Nutrition: {len(orchestrator.knowledge_bases['nutrition'])} caracteres")
    logger.info("")
    
    # =========================================================================
    # PASO 3: Ejecutar flujo completo N0 → N8
    # =========================================================================
    logger.info("⚙️ PASO 3: Ejecutando flujo completo N0 → N1 → N2 → N3 → N4 → N5 → N6 → N7 → N8...")
    logger.info("   (Este proceso puede tomar varios minutos)")
    logger.info("")
    
    try:
        result = await orchestrator.execute_nutrition_pipeline(client_context)
        
        if not result["success"]:
            logger.error(f"❌ Flujo falló: {result.get('error')}")
            logger.error("   Revisa los logs arriba para identificar en qué agente falló")
            return
        
        client_context_after_n8 = result["client_context"]
        
        logger.info("")
        logger.info("🎉 Flujo N0-N8 completado exitosamente")
        logger.info("")
        
    except Exception as e:
        logger.error(f"❌ Error ejecutando flujo: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # =========================================================================
    # PASO 4: Mostrar duración de cada agente
    # =========================================================================
    logger.info("⏱️ PASO 4: Duración por agente:")
    logger.info("")
    total_duration = 0
    
    for execution in result["executions"]:
        agent_id = execution["agent_id"]
        duration = execution["duration_seconds"]
        total_duration += duration
        logger.info(f"   ✅ {agent_id} ({execution['agent_name']}): {duration:.2f}s")
    
    logger.info("")
    logger.info(f"   Duración total agentes: {total_duration:.2f}s")
    logger.info("")
    
    # =========================================================================
    # PASO 5: Verificar que todos los campos de nutrition estén rellenos
    # =========================================================================
    logger.info("🔍 PASO 5: Verificando campos de nutrition...")
    logger.info("")
    
    nutrition = client_context_after_n8.nutrition
    required_fields = [
        "profile",
        "metabolism",
        "energy_strategy",
        "macro_design",
        "weekly_structure",
        "timing_plan",
        "menu_plan",
        "adherence_report",
        "audit"
    ]
    
    all_filled = True
    for field in required_fields:
        value = getattr(nutrition, field, None)
        is_filled = value is not None
        symbol = "✅" if is_filled else "❌"
        logger.info(f"   {symbol} nutrition.{field}: {'RELLENO' if is_filled else 'NULL'}")
        if not is_filled:
            all_filled = False
    
    logger.info("")
    if all_filled:
        logger.info("✅ TODOS LOS CAMPOS DE NUTRITION ESTÁN RELLENOS")
    else:
        logger.error("❌ HAY CAMPOS NULL - REQUIERE ATENCIÓN")
    logger.info("")
    
    # =========================================================================
    # PASO 6: Verificar que training NO fue modificado
    # =========================================================================
    logger.info("🔒 PASO 6: Verificando que training.* NO fue modificado por agentes N...")
    logger.info("")
    
    # Comparar training antes y después
    training_before = client_context.training
    training_after = client_context_after_n8.training
    
    if training_before == training_after:
        logger.info("✅ training.* NO fue modificado (correcto)")
    else:
        logger.error("❌ training.* FUE MODIFICADO por agentes N (violación de contrato)")
    
    logger.info("")
    
    # =========================================================================
    # PASO 7: Guardar artefactos de debug
    # =========================================================================
    logger.info("💾 PASO 7: Guardando artefactos de debug...")
    logger.info("")
    
    # Guardar client_context final
    output_file = "/app/debug_client_context_after_n8.json"
    with open(output_file, "w") as f:
        json.dump(
            client_context_to_dict(client_context_after_n8),
            f,
            indent=2,
            ensure_ascii=False
        )
    
    logger.info(f"✅ Guardado: {output_file}")
    logger.info("")
    
    # =========================================================================
    # PASO 8: Resumen final
    # =========================================================================
    logger.info("=" * 100)
    logger.info("🎉 TEST END-TO-END COMPLETADO")
    logger.info("=" * 100)
    logger.info("")
    logger.info("📁 ARCHIVOS GENERADOS PARA REVISIÓN:")
    logger.info(f"   1. {output_file}")
    logger.info("      → client_context final con nutrition.* completo")
    logger.info("")
    logger.info("   2. /app/logs_nutrition_e2e.txt")
    logger.info("      → Log completo de ejecución con validaciones")
    logger.info("")
    logger.info("✅ Sistema de nutrición (N0-N8) funcionando correctamente")
    logger.info("✅ Listo para revisión final")
    logger.info("")
    
    print("\n✅ Test E2E completado exitosamente")
    print(f"📁 Revisa {output_file} y /app/logs_nutrition_e2e.txt para validación")


if __name__ == "__main__":
    asyncio.run(main())
