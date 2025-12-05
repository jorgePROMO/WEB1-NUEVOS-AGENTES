"""
E4 Debug Endpoint
=================
Endpoint para auditar y depurar la salida del agente E4

Muestra:
- Salida cruda de E4
- Reglas K1 aplicadas
- Decisiones de volumen/intensidad
- Traducción abstracto → concreto
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from k1_knowledge_base import (
    get_reglas_por_nivel,
    get_reglas_por_objetivo,
    get_metodos_permitidos,
    get_volumen_recomendado,
    get_intensidad_recomendada,
    generar_contexto_para_e4
)

logger = logging.getLogger(__name__)

debug_router = APIRouter()

class DebugUserProfile(BaseModel):
    """Perfil simplificado para debug"""
    nivel_experiencia: str  # principiante, intermedio, avanzado
    objetivo_principal: str  # perdida_grasa, hipertrofia, fuerza, etc.
    edad: Optional[int] = 30
    frecuencia_semanal: Optional[int] = 4
    tiempo_por_sesion: Optional[int] = 60
    lesiones: Optional[List[str]] = []

class K1RulesDebugResponse(BaseModel):
    """Respuesta con reglas K1 aplicables"""
    perfil_usuario: Dict[str, Any]
    reglas_nivel: Dict[str, Any]
    reglas_objetivo: Dict[str, Any]
    metodos_permitidos: Dict[str, Any]
    volumen_recomendado: Dict[str, Any]
    intensidad_recomendada: Dict[str, Any]
    contexto_completo_e4: str
    traduccion_abstracto_concreto: Dict[str, Any]

@debug_router.post("/debug/k1-rules", response_model=K1RulesDebugResponse)
async def debug_k1_rules(profile: DebugUserProfile):
    """
    Endpoint de debug para ver qué reglas K1 se aplicarían a un perfil
    
    Este endpoint permite a Jorge auditar:
    - Qué reglas del K1 se activan para un perfil dado
    - Cómo se traducen los términos abstractos a concretos
    - Qué contexto recibiría el agente E4
    
    Ejemplo:
    ```
    POST /api/debug/k1-rules
    {
      "nivel_experiencia": "intermedio",
      "objetivo_principal": "hipertrofia",
      "edad": 35,
      "frecuencia_semanal": 4
    }
    ```
    """
    try:
        # Obtener reglas del K1
        reglas_nivel = get_reglas_por_nivel(profile.nivel_experiencia)
        reglas_objetivo = get_reglas_por_objetivo(profile.objetivo_principal)
        metodos = get_metodos_permitidos(profile.nivel_experiencia, profile.objetivo_principal)
        volumen = get_volumen_recomendado(profile.nivel_experiencia, profile.objetivo_principal)
        intensidad = get_intensidad_recomendada(profile.objetivo_principal)
        
        # Generar contexto completo para E4
        perfil_para_e4 = {
            'nivel_experiencia': profile.nivel_experiencia,
            'objetivo_principal': profile.objetivo_principal,
            'edad': profile.edad,
            'frecuencia_semanal_entrenamiento': profile.frecuencia_semanal,
            'tiempo_disponible_por_sesion': profile.tiempo_por_sesion
        }
        
        contexto_e4 = generar_contexto_para_e4(perfil_para_e4)
        
        # Traducción de abstracto → concreto (ejemplo)
        traduccion = traducir_abstracto_a_concreto(volumen, intensidad)
        
        return K1RulesDebugResponse(
            perfil_usuario=perfil_para_e4,
            reglas_nivel=reglas_nivel,
            reglas_objetivo=reglas_objetivo,
            metodos_permitidos=metodos,
            volumen_recomendado=volumen,
            intensidad_recomendada=intensidad,
            contexto_completo_e4=contexto_e4,
            traduccion_abstracto_concreto=traduccion
        )
        
    except Exception as e:
        logger.error(f"❌ Error en debug K1: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def traducir_abstracto_a_concreto(volumen: Dict, intensidad: Dict) -> Dict:
    """
    Traduce términos abstractos del K1 a valores concretos
    
    Esta es la lógica que el backend aplicará para convertir:
    - volumen: medio → 3-4 series
    - intensidad: moderada → 70-80% 1RM, RPE 7-8
    """
    
    # Mapeo de volumen abstracto → concreto
    mapeo_volumen = {
        'muy_bajo': {'series': '1-2', 'rango': 'minimal'},
        'bajo': {'series': '2-3', 'rango': 'low'},
        'medio': {'series': '3-4', 'rango': 'moderate'},
        'alto': {'series': '4-5', 'rango': 'high'},
        'muy_alto': {'series': '5-6+', 'rango': 'very_high'}
    }
    
    # Mapeo de series abstractas → concreto
    mapeo_series = {
        'bajas': '2-3 series',
        'medias': '3-4 series',
        'altas': '4-5 series'
    }
    
    # Mapeo de reps abstractas → concreto
    mapeo_reps = {
        'bajas': '3-6 reps (fuerza)',
        'medias': '6-12 reps (hipertrofia)',
        'altas': '12-20 reps (resistencia/hipertrofia metabólica)'
    }
    
    # Mapeo de intensidad abstracta → concreto
    mapeo_intensidad = {
        'muy_ligera': {'porcentaje_1rm': '40-50%', 'rpe': '4-5', 'descripcion': 'muy_facil'},
        'ligera': {'porcentaje_1rm': '50-60%', 'rpe': '5-6', 'descripcion': 'facil'},
        'moderada': {'porcentaje_1rm': '60-75%', 'rpe': '6-7', 'descripcion': 'moderado'},
        'alta': {'porcentaje_1rm': '75-85%', 'rpe': '7-8', 'descripcion': 'dificil'},
        'muy_alta': {'porcentaje_1rm': '85-95%+', 'rpe': '8-9', 'descripcion': 'muy_dificil'}
    }
    
    # Mapeo de proximidad al fallo → concreto
    mapeo_fallo = {
        'muy_lejos_del_fallo': {'rir': '5-6', 'rpe': '4-5', 'descripcion': 'muy lejos del fallo'},
        'lejos_del_fallo': {'rir': '3-4', 'rpe': '6-7', 'descripcion': 'lejos del fallo'},
        'moderadamente_cerca_del_fallo': {'rir': '2-3', 'rpe': '7-8', 'descripcion': 'moderadamente cerca del fallo'},
        'cerca_del_fallo': {'rir': '1-2', 'rpe': '8-9', 'descripcion': 'cerca del fallo'},
        'muy_cerca_o_en_fallo': {'rir': '0-1', 'rpe': '9-10', 'descripcion': 'en fallo o muy cerca'}
    }
    
    # Mapeo de densidad → descanso
    mapeo_densidad = {
        'densidad_baja': {'descanso_segundos': '120-180', 'descripcion': 'descanso largo'},
        'densidad_media': {'descanso_segundos': '60-90', 'descripcion': 'descanso moderado'},
        'densidad_alta': {'descanso_segundos': '30-45', 'descripcion': 'descanso corto'}
    }
    
    # Construir traducción
    volumen_sesion = volumen.get('volumen_por_sesion', 'medio')
    series_ejercicio = volumen.get('series_por_ejercicio', 'medias')
    intensidad_carga = intensidad.get('intensidad_carga', 'moderada')
    proximidad_fallo = intensidad.get('proximidad_fallo', 'moderadamente_cerca_del_fallo')
    
    traduccion = {
        'volumen': {
            'abstracto': volumen_sesion,
            'concreto': mapeo_volumen.get(volumen_sesion.split('_')[0] if '_' in volumen_sesion else volumen_sesion, mapeo_volumen['medio'])
        },
        'series': {
            'abstracto': series_ejercicio,
            'concreto': mapeo_series.get(series_ejercicio, '3-4 series')
        },
        'intensidad': {
            'abstracto': intensidad_carga,
            'concreto': mapeo_intensidad.get(intensidad_carga.split('_')[0] if '_' in intensidad_carga else intensidad_carga, mapeo_intensidad['moderada'])
        },
        'proximidad_fallo': {
            'abstracto': proximidad_fallo,
            'concreto': mapeo_fallo.get(proximidad_fallo, mapeo_fallo['moderadamente_cerca_del_fallo'])
        },
        'ejemplo_aplicacion': {
            'descripcion': f"Usuario {volumen.get('volumen_por_sesion', 'medio')} volumen, {intensidad_carga} intensidad",
            'plan_ejemplo': f"{mapeo_series.get(series_ejercicio, '3-4')} de {mapeo_reps.get('medias', '6-12 reps')}, RPE {mapeo_fallo.get(proximidad_fallo, {}).get('rpe', '7-8')}"
        }
    }
    
    return traduccion


@debug_router.get("/debug/k1-taxonomy")
async def get_k1_taxonomy():
    """
    Endpoint para ver toda la taxonomía del K1
    
    Útil para verificar:
    - Qué patrones de movimiento existen
    - Qué tipos de ejercicio hay
    - Qué categorías de volumen/intensidad son válidas
    """
    from k1_knowledge_base import get_taxonomia
    
    try:
        taxonomia = get_taxonomia()
        return {
            "taxonomia": taxonomia,
            "nota": "Estos son los ÚNICOS valores válidos para patrones, tipos, volumen, intensidad, etc."
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo taxonomía: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@debug_router.get("/debug/k1-version")
async def get_k1_version():
    """Información de versión del K1"""
    from k1_knowledge_base import load_k1
    
    try:
        k1 = load_k1()
        return {
            "nombre": k1['metadata']['nombre'],
            "version": k1['metadata']['version'],
            "descripcion": k1['metadata']['descripcion'],
            "notas": k1['metadata']['notas']
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo versión K1: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@debug_router.post("/debug/validate-e4-response")
async def validate_e4_response_endpoint(e4_response: Dict):
    """
    Endpoint para validar una respuesta de E4
    
    Útil para:
    - Testear el validador con respuestas de prueba
    - Verificar que una respuesta cumple los requisitos
    - Ver score y errores detallados
    
    Ejemplo:
    ```
    POST /api/debug/validate-e4-response
    {
      "training_plan": { ... }
    }
    ```
    """
    from e4_response_validator import E4ResponseValidator
    
    try:
        validator = E4ResponseValidator()
        result = validator.validate_full_response(e4_response)
        
        return {
            "validation_result": result.dict(),
            "should_retry": validator.should_retry(result),
            "formatted_report": validator.format_validation_report(result)
        }
    except Exception as e:
        logger.error(f"❌ Error validando respuesta E4: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@debug_router.get("/debug/e4-logs/{user_id}")
async def get_e4_logs_by_user(user_id: str, limit: int = 10):
    """
    Obtiene los logs de decisiones E4 para un usuario
    
    Args:
        user_id: ID del usuario
        limit: Número máximo de logs (default: 10)
        
    Returns:
        Lista de logs con decisiones K1
    """
    from e4_decision_logger import get_logger
    
    try:
        logger_inst = get_logger()
        logs = await logger_inst.get_logs_by_user(user_id, limit)
        
        return {
            "user_id": user_id,
            "total_logs": len(logs),
            "logs": logs
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo logs E4: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@debug_router.get("/debug/e4-logs/plan/{plan_id}")
async def get_e4_log_by_plan(plan_id: str):
    """
    Obtiene el log de decisión para un plan específico
    
    Args:
        plan_id: ID del plan
        
    Returns:
        Log completo con todas las decisiones K1 aplicadas
    """
    from e4_decision_logger import get_logger
    
    try:
        logger_inst = get_logger()
        log = await logger_inst.get_log_by_plan_id(plan_id)
        
        if not log:
            raise HTTPException(status_code=404, detail=f"No se encontró log para plan_id: {plan_id}")
        
        return {
            "log": log,
            "formatted_report": logger_inst.format_decision_report(log)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo log por plan_id: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@debug_router.get("/debug/e4-stats/{user_id}")
async def get_e4_stats_by_user(user_id: str):
    """
    Estadísticas agregadas de decisiones E4 para un usuario
    
    Muestra:
    - Total de generaciones
    - Tasa de éxito
    - Promedio de intentos
    - Patrones más usados
    """
    from e4_decision_logger import get_logger
    
    try:
        logger_inst = get_logger()
        stats = await logger_inst.get_stats_by_user(user_id)
        
        return {
            "user_id": user_id,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"❌ Error obteniendo stats E4: {e}")
        raise HTTPException(status_code=500, detail=str(e))
