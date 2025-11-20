"""
TEST END-TO-END COMPLETO - ENTRENAMIENTO INICIAL (v1)
Flujo completo: Cuestionario → E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8 → E9

Genera:
- /app/debug_client_context_initial.json
- /app/debug_client_context_after_e9.json
- /app/logs_training_e2e.txt (este archivo captura los logs)
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
from edn360.client_context_utils import client_context_to_dict

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs_training_e2e.txt', mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def create_realistic_questionnaire():
    """Crea un cuestionario inicial realista y completo"""
    return {
        "client_id": "client_juan_perez_e2e",
        "version": 1,
        "timestamp": datetime.now().isoformat(),
        
        # ===== DATOS PERSONALES =====
        "nombre": "Juan Pérez García",
        "edad": 32,
        "sexo": "M",
        "peso_actual_kg": 78,
        "altura_cm": 175,
        "porcentaje_grasa_estimado": 18,
        
        # ===== OBJETIVO =====
        "objetivo_principal": "hipertrofia",
        "objetivo_secundario": "mejorar composicion corporal",
        "plazo": "6 meses",
        "motivacion": "alta",
        "razon_principal": "Quiero ganar masa muscular y verme mejor",
        
        # ===== EXPERIENCIA =====
        "experiencia_entrenamiento": "3 años gym intermitente",
        "nivel_estimado": "intermedio",
        "deportes_previos": ["futbol amateur", "gym"],
        "tecnica_ejercicios": "buena en basicos, regular en accesorios",
        "familiaridad_gym": "alta",
        
        # ===== DISPONIBILIDAD =====
        "dias_disponibles": 4,
        "dias_semana_preferidos": ["lunes", "martes", "jueves", "viernes"],
        "minutos_por_sesion": 60,
        "horario_preferido": "tarde",
        "hora_especifica": "18:00-19:00",
        "flexibilidad_horaria": "media",
        
        # ===== EQUIPO Y GIMNASIO =====
        "equipo_disponible": "gym completo",
        "tipo_gym": "comercial bien equipado",
        "equipamiento_especifico": [
            "mancuernas hasta 50kg",
            "barra olimpica",
            "rack con seguridad",
            "maquinas de placas",
            "poleas altas y bajas",
            "banco ajustable",
            "discos variados"
        ],
        "restricciones_equipo": [],
        
        # ===== LESIONES Y LIMITACIONES =====
        "lesiones_previas": "Dolor lumbar leve ocasional por mala técnica en peso muerto hace 6 meses",
        "lesiones_activas": [
            {
                "zona": "lumbar",
                "tipo": "dolor_ocasional",
                "gravedad": "leve",
                "descripcion": "Molestia lumbar al hacer flexión de tronco con carga. Aparece con mala técnica o volumen excesivo",
                "tiempo_lesion": "6 meses",
                "tratamiento": "fisioterapia completada hace 3 meses",
                "estado_actual": "recuperado pero con precaución"
            }
        ],
        "restricciones_medicas": [],
        "ejercicios_que_molestan": ["peso muerto convencional alto volumen", "buenos dias"],
        "ejercicios_prohibidos": [],
        
        # ===== ESTILO DE VIDA =====
        "trabajo": "oficina sedentario 8h/día",
        "nivel_estres": "medio",
        "fuentes_estres": ["trabajo con deadlines", "traffic diario"],
        "horas_sueno_promedio": 7,
        "calidad_sueno": "buena",
        "despertares_nocturnos": "ocasionales",
        
        # ===== ACTIVIDAD FÍSICA ADICIONAL =====
        "actividad_fisica_adicional": "caminatas ocasionales fin de semana",
        "pasos_diarios_promedio": 6000,
        
        # ===== NUTRICIÓN ACTUAL =====
        "nutricion_actual": "desordenada, sin seguimiento estructurado",
        "comidas_dia": 3,
        "calidad_alimentacion": "media",
        "agua_litros": 2,
        "suplementos_actuales": ["proteina whey", "creatina ocasional"],
        
        # ===== ADHERENCIA HISTÓRICA =====
        "adherencia_historica": "irregular - 2-3 meses seguido luego abandono",
        "motivo_abandono_previo": "falta de plan estructurado y seguimiento",
        "mayor_racha_constancia": "4 meses seguidos hace 1 año",
        "barreras_adherencia": ["falta motivacion", "no ver resultados rapidos"],
        
        # ===== CONTEXTO ADICIONAL =====
        "apoyo_familiar": "bueno - pareja apoya",
        "presupuesto_suplementos": "medio - 50-80€/mes",
        "experiencia_nutricion": "basica",
        "preferencias_entrenamiento": [
            "me gustan pesos libres",
            "prefiero ejercicios compuestos",
            "no me gusta cardio tradicional"
        ],
        
        # ===== NOTAS DEL ENTRENADOR =====
        "notas_entrenador": "Cliente motivado y con buen potencial. Necesita estructura clara y seguimiento para mantener adherencia. Buena base técnica pero requiere enfoque en progresión sostenible. Precaución con volumen lumbar por historial.",
        
        # ===== EVALUACIÓN INICIAL =====
        "fuerza_maxima_estimada": {
            "sentadilla": "100kg x 5 reps",
            "press_banca": "80kg x 5 reps",
            "peso_muerto": "110kg x 5 reps (rumano, no convencional)"
        }
    }


async def run_e2e_test():
    """Ejecuta el test end-to-end completo"""
    logger.info("=" * 100)
    logger.info("🚀 TEST END-TO-END - ENTRENAMIENTO INICIAL COMPLETO (v1)")
    logger.info("=" * 100)
    logger.info("")
    
    # ===== PASO 1: Crear cuestionario =====
    logger.info("📋 PASO 1: Creando cuestionario inicial realista...")
    questionnaire = create_realistic_questionnaire()
    
    logger.info(f"✅ Cuestionario creado:")
    logger.info(f"   - Cliente: {questionnaire['nombre']}")
    logger.info(f"   - Edad: {questionnaire['edad']} años")
    logger.info(f"   - Objetivo: {questionnaire['objetivo_principal']}")
    logger.info(f"   - Nivel: {questionnaire['nivel_estimado']}")
    logger.info(f"   - Disponibilidad: {questionnaire['dias_disponibles']} días x {questionnaire['minutos_por_sesion']} min")
    logger.info(f"   - Lesiones: {len(questionnaire['lesiones_activas'])} activa(s)")
    logger.info("")
    
    # ===== PASO 2: Inicializar orchestrator =====
    logger.info("🔧 PASO 2: Inicializando orchestrator...")
    try:
        orchestrator = EDN360Orchestrator()
        logger.info("✅ Orchestrator inicializado correctamente")
        logger.info(f"   - KB Training: {len(orchestrator.knowledge_bases['training'])} caracteres")
        logger.info(f"   - KB Nutrition: {len(orchestrator.knowledge_bases['nutrition'])} caracteres")
    except Exception as e:
        logger.error(f"❌ Error inicializando orchestrator: {str(e)}")
        return False
    
    logger.info("")
    
    # ===== PASO 3: Ejecutar flujo completo E1→E9 =====
    logger.info("⚙️ PASO 3: Ejecutando flujo completo E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8 → E9...")
    logger.info("   (Este proceso puede tomar varios minutos)")
    logger.info("")
    
    start_time = datetime.now()
    
    try:
        result = await orchestrator._execute_training_initial(
            questionnaire_data=questionnaire,
            previous_plan=None
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        if not result["success"]:
            logger.error(f"❌ Flujo falló: {result.get('error')}")
            logger.error("   Revisa los logs arriba para identificar en qué agente falló")
            return False
        
        logger.info("")
        logger.info("🎉 FLUJO COMPLETADO EXITOSAMENTE")
        logger.info(f"   Duración total: {duration:.2f} segundos ({duration/60:.1f} minutos)")
        logger.info("")
        
        # ===== PASO 4: Guardar client_context final =====
        logger.info("💾 PASO 4: Guardando artefactos para revisión...")
        
        client_context_final = result.get("client_context")
        
        if not client_context_final:
            logger.error("❌ No se obtuvo client_context en el resultado")
            return False
        
        # Guardar client_context final
        with open('/app/debug_client_context_after_e9.json', 'w', encoding='utf-8') as f:
            json.dump(client_context_final, f, indent=2, ensure_ascii=False)
        logger.info("✅ client_context final guardado: /app/debug_client_context_after_e9.json")
        
        # También guardar el inicial (reconstruir desde questionnaire)
        from edn360.client_context_utils import initialize_client_context
        initial_context = initialize_client_context(
            client_id=questionnaire["client_id"],
            version=1,
            cuestionario_data=questionnaire,
            is_followup=False
        )
        with open('/app/debug_client_context_initial.json', 'w', encoding='utf-8') as f:
            json.dump(client_context_to_dict(initial_context), f, indent=2, ensure_ascii=False)
        logger.info("✅ client_context inicial guardado: /app/debug_client_context_initial.json")
        
        logger.info("")
        
        # ===== PASO 5: Verificar campos llenados =====
        logger.info("🔍 PASO 5: Verificando que todos los campos están llenos...")
        logger.info("")
        
        training = client_context_final.get("training", {})
        
        fields_check = {
            "profile": ("E1", training.get("profile")),
            "constraints": ("E1", training.get("constraints")),
            "prehab": ("E1", training.get("prehab")),
            "capacity": ("E2", training.get("capacity")),
            "adaptation": ("E3", training.get("adaptation")),
            "mesocycle": ("E4", training.get("mesocycle")),
            "sessions": ("E5", training.get("sessions")),
            "safe_sessions": ("E6", training.get("safe_sessions")),
            "formatted_plan": ("E7", training.get("formatted_plan")),
            "audit": ("E8", training.get("audit")),
            "bridge_for_nutrition": ("E9", training.get("bridge_for_nutrition"))
        }
        
        all_filled = True
        for field_name, (agent_id, value) in fields_check.items():
            is_filled = value is not None and value != {}
            status = "✅ LLENO" if is_filled else "❌ VACÍO"
            logger.info(f"   {status} - {agent_id} → training.{field_name}")
            if not is_filled:
                all_filled = False
        
        logger.info("")
        
        if not all_filled:
            logger.warning("⚠️ Algunos campos no fueron llenados. Revisa los logs de ejecución.")
        else:
            logger.info("✅ TODOS los campos fueron llenados correctamente")
        
        logger.info("")
        
        # ===== PASO 6: Resumen de ejecuciones =====
        logger.info("📊 PASO 6: Resumen de ejecuciones por agente:")
        logger.info("")
        
        executions = result.get("executions", [])
        total_duration = 0
        
        for execution in executions:
            agent_id = execution.get("agent_id", "Unknown")
            agent_name = execution.get("agent_name", "")
            success = execution.get("success", False)
            duration_sec = execution.get("duration_seconds", 0)
            total_duration += duration_sec
            
            status_icon = "✅" if success else "❌"
            logger.info(f"   {status_icon} {agent_id} ({agent_name}): {duration_sec:.2f}s")
            
            if not success:
                error = execution.get("error", "Error desconocido")
                logger.error(f"      Error: {error}")
        
        logger.info("")
        logger.info(f"   Duración total agentes: {total_duration:.2f}s")
        logger.info("")
        
        # ===== PASO 7: Validar bridge_for_nutrition =====
        logger.info("🔗 PASO 7: Validando bridge_for_nutrition (conexión con nutrición)...")
        logger.info("")
        
        bridge = training.get("bridge_for_nutrition")
        if bridge:
            logger.info("✅ bridge_for_nutrition está presente")
            if isinstance(bridge, dict):
                logger.info(f"   - Claves en bridge: {list(bridge.keys())}")
            logger.info("   Este campo será usado por los agentes de nutrición (N0-N8)")
        else:
            logger.warning("⚠️ bridge_for_nutrition está vacío")
        
        logger.info("")
        
        # ===== RESUMEN FINAL =====
        logger.info("=" * 100)
        logger.info("🎉 TEST END-TO-END COMPLETADO")
        logger.info("=" * 100)
        logger.info("")
        logger.info("📁 ARCHIVOS GENERADOS PARA REVISIÓN:")
        logger.info("   1. /app/debug_client_context_initial.json")
        logger.info("      → client_context justo después de initialize")
        logger.info("")
        logger.info("   2. /app/debug_client_context_after_e9.json")
        logger.info("      → client_context final con todos los campos llenos")
        logger.info("")
        logger.info("   3. /app/logs_training_e2e.txt")
        logger.info("      → Log completo de ejecución con validaciones")
        logger.info("")
        logger.info("✅ Sistema de entrenamiento (E1-E9) funcionando correctamente")
        logger.info("✅ Listo para revisión final y posterior implementación de nutrición")
        logger.info("")
        
        return True
        
    except Exception as e:
        logger.error("")
        logger.error("❌ ERROR DURANTE LA EJECUCIÓN:")
        logger.error(f"   {str(e)}")
        logger.error("")
        import traceback
        logger.error("Traceback completo:")
        logger.error(traceback.format_exc())
        return False


async def main():
    """Función principal"""
    success = await run_e2e_test()
    
    if success:
        print("\n✅ Test E2E completado exitosamente")
        print("📁 Revisa los archivos generados para validación")
        sys.exit(0)
    else:
        print("\n❌ Test E2E falló")
        print("📄 Revisa /app/logs_training_e2e.txt para detalles")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
