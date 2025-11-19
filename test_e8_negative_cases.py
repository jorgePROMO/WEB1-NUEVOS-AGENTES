"""
Tests de E8 - Casos Negativos
Verifica que E8 detecta problemas en planes mal diseñados
"""

import asyncio
import json
import sys
import os

from dotenv import load_dotenv
load_dotenv('/app/backend/.env')

sys.path.insert(0, '/app/backend')

from edn360.client_context_models import ClientContext
from edn360.client_context_utils import initialize_client_context, client_context_to_dict
from edn360.agents.training_initial.e8_auditor import E8TechnicalAuditor

import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_base_context():
    """Crea un client_context base"""
    questionnaire = {
        "client_id": "test_negative",
        "nombre": "Test User",
        "edad": 30,
        "sexo": "M",
        "peso_actual_kg": 75,
        "altura_cm": 175,
        "objetivo_principal": "hipertrofia",
        "dias_disponibles": 4,
        "minutos_por_sesion": 60,
    }
    
    context = initialize_client_context(
        client_id="test_negative",
        version=1,
        cuestionario_data=questionnaire,
        is_followup=False
    )
    
    # Añadir datos base de otros agentes
    context.training.profile = {
        "nombre": "Test User",
        "edad": 30,
        "objetivo": "hipertrofia",
        "nivel": "intermedio"
    }
    
    context.training.constraints = {
        "lesiones": [
            {
                "zona": "hombro_derecho",
                "gravedad": "moderada",
                "ejercicios_prohibidos": ["press_militar", "press_banca_plano"]
            }
        ]
    }
    
    context.training.capacity = {
        "volumen_semanal_recomendado": {
            "pecho": "16-20 series",
            "espalda": "16-20 series",
            "piernas": "16-20 series"
        }
    }
    
    context.training.mesocycle = {
        "duracion_semanas": 4,
        "split": "upper/lower",
        "volumen_objetivo": "medio-alto"
    }
    
    return context


async def test_caso_1_volumen_excesivo():
    """Test: Volumen semanal excesivo (más de 30 series por grupo)"""
    logger.info("\n" + "="*80)
    logger.info("🧪 CASO 1: VOLUMEN EXCESIVO")
    logger.info("="*80)
    
    context = create_base_context()
    
    # Crear sessions con VOLUMEN EXCESIVO para pecho
    # Cliente es INTERMEDIO, recomendación: 14-20 series/semana
    # Vamos a darle 35 series/semana de pecho (75% por encima del máximo)
    context.training.sessions = {
        "semana_1": {
            "dia_1_upper": {
                "grupo_principal": "pecho_espalda",
                "ejercicios": [
                    # PECHO: 7 ejercicios x 5 series = 35 series en la semana
                    {"nombre": "Press Banca", "series": 5, "reps": "8-10", "grupo_muscular": "pecho"},
                    {"nombre": "Press Inclinado Mancuernas", "series": 5, "reps": "8-10", "grupo_muscular": "pecho"},
                    {"nombre": "Aperturas con Mancuernas", "series": 5, "reps": "10-12", "grupo_muscular": "pecho"},
                    {"nombre": "Fondos en Paralelas", "series": 4, "reps": "8-10", "grupo_muscular": "pecho"},
                    {"nombre": "Press Banca Declinado", "series": 4, "reps": "8-10", "grupo_muscular": "pecho"},
                    {"nombre": "Cruces en Polea Alta", "series": 4, "reps": "12-15", "grupo_muscular": "pecho"},
                    {"nombre": "Pullover con Mancuerna", "series": 3, "reps": "10-12", "grupo_muscular": "pecho"},
                    # Espalda mínima
                    {"nombre": "Remo con Barra", "series": 3, "reps": "8-10", "grupo_muscular": "espalda"}
                ]
            },
            "dia_2_lower": {
                "ejercicios": [
                    {"nombre": "Sentadilla", "series": 4, "grupo_muscular": "cuadriceps"},
                    {"nombre": "Prensa", "series": 4, "grupo_muscular": "cuadriceps"}
                ]
            },
            "dia_3_upper": {
                "ejercicios": [
                    # Más pecho (ya no hace falta, pero para enfatizar)
                    {"nombre": "Press Banca", "series": 5, "grupo_muscular": "pecho"},
                    {"nombre": "Dominadas", "series": 3, "grupo_muscular": "espalda"}
                ]
            },
            "dia_4_lower": {
                "ejercicios": [
                    {"nombre": "Peso Muerto", "series": 4, "grupo_muscular": "femoral"}
                ]
            }
        }
    }
    # TOTAL PECHO: 30+5 = 35 series/semana
    # Para INTERMEDIO, máximo recomendado: 20 series
    # Exceso: +75% → CLARAMENTE EXCESIVO
    
    context.training.safe_sessions = context.training.sessions
    
    # Ejecutar E8
    e8 = E8TechnicalAuditor()
    result = await e8.execute(client_context_to_dict(context), knowledge_base="")
    
    if result["success"]:
        audit = ClientContext.model_validate(result["output"]["client_context"]).training.audit
        
        logger.info(f"\n📊 Resultado Auditoría:")
        logger.info(f"   Status: {audit.get('status', 'N/A')}")
        logger.info(f"   Warnings: {len(audit.get('warnings', []))}")
        logger.info(f"   Recomendaciones: {len(audit.get('recomendaciones', []))}")
        
        # Verificar que detectó el problema
        warnings = audit.get('warnings', [])
        if any('volumen' in str(w).lower() or 'excesivo' in str(w).lower() for w in warnings):
            logger.info("   ✅ E8 DETECTÓ volumen excesivo")
            return True
        else:
            logger.warning("   ⚠️ E8 NO detectó volumen excesivo")
            logger.info(f"   Warnings: {warnings}")
            return False
    else:
        logger.error(f"   ❌ E8 falló: {result.get('error')}")
        return False


async def test_caso_2_patron_faltante():
    """Test: Falta trabajo de un patrón importante (espalda)"""
    logger.info("\n" + "="*80)
    logger.info("🧪 CASO 2: PATRÓN MUSCULAR FALTANTE")
    logger.info("="*80)
    
    context = create_base_context()
    
    # Crear sessions SIN trabajo de espalda (desequilibrio push/pull)
    context.training.sessions = {
        "semana_1": {
            "dia_1_upper": {
                "ejercicios": [
                    {"nombre": "Press Banca", "series": 4, "grupo": "pecho"},
                    {"nombre": "Press Inclinado", "series": 4, "grupo": "pecho"},
                    {"nombre": "Press Arnold", "series": 3, "grupo": "hombros"},
                    # SOLO PUSH, NADA DE PULL
                ]
            },
            "dia_2_lower": {
                "ejercicios": [
                    {"nombre": "Sentadilla", "series": 4, "grupo": "cuadriceps"}
                ]
            },
            "dia_3_upper": {
                "ejercicios": [
                    {"nombre": "Fondos", "series": 4, "grupo": "pecho"},
                    {"nombre": "Aperturas", "series": 3, "grupo": "pecho"},
                    # SOLO PUSH, NADA DE PULL
                ]
            },
            "dia_4_lower": {
                "ejercicios": [
                    {"nombre": "Peso Muerto", "series": 4, "grupo": "femoral"}
                ]
            }
        }
    }
    
    context.training.safe_sessions = context.training.sessions
    
    # Ejecutar E8
    e8 = E8TechnicalAuditor()
    result = await e8.execute(client_context_to_dict(context), knowledge_base="")
    
    if result["success"]:
        audit = ClientContext.model_validate(result["output"]["client_context"]).training.audit
        
        logger.info(f"\n📊 Resultado Auditoría:")
        logger.info(f"   Status: {audit.get('status', 'N/A')}")
        logger.info(f"   Warnings: {len(audit.get('warnings', []))}")
        
        # Verificar que detectó desequilibrio
        warnings = audit.get('warnings', [])
        if any('equilibrio' in str(w).lower() or 'pull' in str(w).lower() or 'espalda' in str(w).lower() for w in warnings):
            logger.info("   ✅ E8 DETECTÓ desequilibrio push/pull")
            return True
        else:
            logger.warning("   ⚠️ E8 NO detectó desequilibrio")
            logger.info(f"   Warnings: {warnings}")
            return False
    else:
        logger.error(f"   ❌ E8 falló: {result.get('error')}")
        return False


async def test_caso_3_ejercicios_prohibidos():
    """Test: Ejercicios prohibidos por constraints no respetados"""
    logger.info("\n" + "="*80)
    logger.info("🧪 CASO 3: EJERCICIOS PROHIBIDOS NO RESPETADOS")
    logger.info("="*80)
    
    context = create_base_context()
    
    # safe_sessions tiene ejercicios PROHIBIDOS (debería haber sido filtrado por E6)
    context.training.sessions = {
        "semana_1": {
            "dia_1_upper": {
                "ejercicios": [
                    {"nombre": "Press Militar", "series": 4},  # PROHIBIDO!
                    {"nombre": "Press Banca Plano", "series": 4},  # PROHIBIDO!
                    {"nombre": "Remo", "series": 4}
                ]
            }
        }
    }
    
    context.training.safe_sessions = context.training.sessions  # Mismo contenido (E6 falló)
    
    # Ejecutar E8
    e8 = E8TechnicalAuditor()
    result = await e8.execute(client_context_to_dict(context), knowledge_base="")
    
    if result["success"]:
        audit = ClientContext.model_validate(result["output"]["client_context"]).training.audit
        
        logger.info(f"\n📊 Resultado Auditoría:")
        logger.info(f"   Status: {audit.get('status', 'N/A')}")
        logger.info(f"   Warnings: {len(audit.get('warnings', []))}")
        
        # Verificar que detectó ejercicios prohibidos
        warnings = audit.get('warnings', [])
        checks = audit.get('checks', {})
        
        detected = (
            any('prohibido' in str(w).lower() or 'restriccion' in str(w).lower() for w in warnings) or
            checks.get('restricciones') == 'fallido' or
            audit.get('status') == 'bloqueado'
        )
        
        if detected:
            logger.info("   ✅ E8 DETECTÓ ejercicios prohibidos")
            return True
        else:
            logger.warning("   ⚠️ E8 NO detectó ejercicios prohibidos")
            logger.info(f"   Warnings: {warnings}")
            logger.info(f"   Checks: {checks}")
            return False
    else:
        logger.error(f"   ❌ E8 falló: {result.get('error')}")
        return False


async def main():
    """Ejecuta todos los tests de casos negativos"""
    logger.info("\n🚀 TESTS DE E8 - CASOS NEGATIVOS")
    logger.info("Verificando que E8 detecta problemas en planes mal diseñados\n")
    
    results = {}
    
    try:
        results['volumen_excesivo'] = await test_caso_1_volumen_excesivo()
        results['patron_faltante'] = await test_caso_2_patron_faltante()
        results['ejercicios_prohibidos'] = await test_caso_3_ejercicios_prohibidos()
        
        # Resumen
        logger.info("\n" + "="*80)
        logger.info("📊 RESUMEN DE TESTS")
        logger.info("="*80)
        
        total = len(results)
        passed = sum(1 for v in results.values() if v)
        
        for test_name, passed_test in results.items():
            status = "✅ PASS" if passed_test else "❌ FAIL"
            logger.info(f"   {status}: {test_name}")
        
        logger.info(f"\n   Total: {passed}/{total} tests pasados")
        
        if passed == total:
            logger.info("\n🎉 TODOS LOS TESTS PASARON")
            logger.info("E8 detecta correctamente problemas en planes mal diseñados")
            return True
        else:
            logger.warning(f"\n⚠️ {total - passed} tests fallaron")
            logger.warning("E8 necesita mejorar detección de problemas")
            return False
            
    except Exception as e:
        logger.error(f"\n❌ ERROR: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
