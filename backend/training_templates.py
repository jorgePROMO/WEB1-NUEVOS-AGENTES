"""
Módulo de plantillas de bloques de entrenamiento EDN360
Versión 3.0 FINAL

Este módulo contiene:
- Plantillas de calentamiento (Bloque A)
- Plantillas de core/abs (Bloque C)  
- Plantillas de cardio (Bloque D)
- Sistema de selección automática basado en reglas jerárquicas

El Bloque B (entrenamiento principal) es generado por IA.
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)

# MongoDB connection for exercise enrichment
_mongo_client = None

def get_mongo_client():
    """Get or create MongoDB client"""
    global _mongo_client
    if _mongo_client is None:
        mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
        _mongo_client = AsyncIOMotorClient(mongo_url)
    return _mongo_client

async def enrich_exercises_with_videos(exercises: List[Dict]) -> List[Dict]:
    """
    Enrich exercises with video URLs from database
    
    Args:
        exercises: List of exercise dicts with 'nombre' field
        
    Returns:
        Same list but with video_url filled from DB if available
    """
    if not exercises:
        return exercises
    
    try:
        client = get_mongo_client()
        edn360_db = client['edn360_app']
        exercises_collection = edn360_db.exercises
        
        enriched = []
        for exercise in exercises:
            nombre = exercise.get('nombre', '')
            if nombre:
                # Normalize name for lookup
                exercise_id = nombre.lower().strip()
                
                # Look up in database
                db_exercise = await exercises_collection.find_one(
                    {'id': exercise_id},
                    {'_id': 0, 'video_url': 1}
                )
                
                # Make a copy and update video_url if found
                enriched_exercise = exercise.copy()
                if db_exercise and db_exercise.get('video_url'):
                    enriched_exercise['video_url'] = db_exercise['video_url']
                    logger.debug(f"✅ Video found for exercise: {nombre}")
                else:
                    logger.debug(f"⚠️ No video found for exercise: {nombre}")
                
                enriched.append(enriched_exercise)
            else:
                enriched.append(exercise)
        
        return enriched
    
    except Exception as e:
        logger.error(f"❌ Error enriching exercises with videos: {e}")
        # Return original list if error
        return exercises

# Cargar plantillas desde JSON
TEMPLATES_FILE = os.path.join(os.path.dirname(__file__), '..', 'PLANTILLAS_BLOQUES_V3_FINAL.json')

with open(TEMPLATES_FILE, 'r', encoding='utf-8') as f:
    TEMPLATES_DATA = json.load(f)

CALENTAMIENTOS = {t['id']: t for t in TEMPLATES_DATA['calentamientos']}
CORE_ABS = {t['id']: t for t in TEMPLATES_DATA['core_abs']}
CARDIO = {t['id']: t for t in TEMPLATES_DATA['cardio']}
REGLAS = TEMPLATES_DATA['reglas_asignacion']


def seleccionar_plantillas(
    user_data: Dict[str, Any],
    dia_entrenamiento: Dict[str, Any],
    session_number: int = 1,
    week_number: int = 1
) -> Dict[str, Any]:
    """
    Selecciona las plantillas apropiadas para un día de entrenamiento.
    
    Args:
        user_data: Datos del usuario (edad, nivel, lesiones, objetivo, etc.)
        dia_entrenamiento: Info del día (grupos musculares, tipo de sesión)
        session_number: Número de sesión para rotación de cardio
        week_number: Número de semana para rotación de abs
        
    Returns:
        Dict con las plantillas seleccionadas para cada bloque
    """
    
    resultado = {
        'calentamiento': None,
        'core_abs': None,
        'cardio': None,
        'reglas_aplicadas': [],
        'log': []
    }
    
    # Extraer datos del usuario
    edad = user_data.get('edad', 0)
    nivel = user_data.get('nivel', 'principiante').lower()
    objetivo = user_data.get('objetivo', 'mantenimiento').lower()
    lesion_hombro = user_data.get('lesion_hombro', False) or user_data.get('dolor_hombro', False)
    lesion_lumbar = user_data.get('lesion_lumbar', False) or user_data.get('hernia_discal', False)
    muy_sedentario = user_data.get('muy_sedentario', False)
    primera_sesion = user_data.get('primera_sesion', False)
    
    # Extraer datos del día
    grupos_musculares = dia_entrenamiento.get('grupos_musculares', [])
    tipo_sesion = dia_entrenamiento.get('tipo_sesion', 'normal')
    
    # Convertir grupos musculares a minúsculas para comparación
    grupos_musculares = [g.lower() for g in grupos_musculares]
    
    resultado['log'].append(f"Usuario: edad={edad}, nivel={nivel}, objetivo={objetivo}")
    resultado['log'].append(f"Día: grupos={grupos_musculares}, tipo={tipo_sesion}")
    
    # ========== PRIORIDAD 1: SEGURIDAD ==========
    bloques_asignados = {'calentamiento': False, 'core_abs': False, 'cardio': False}
    
    # REGLA: Edad >= 60 (MÁXIMA PRIORIDAD)
    if edad >= 60:
        resultado['calentamiento'] = CALENTAMIENTOS['calentamiento_bajo_impacto']
        resultado['core_abs'] = CORE_ABS['abs_basico_1']
        
        # Seleccionar cardio senior según objetivo
        if 'perdida' in objetivo or 'grasa' in objetivo:
            resultado['cardio'] = CARDIO['cardio_senior_perdida_grasa']
        else:
            resultado['cardio'] = CARDIO['cardio_senior_mantenimiento']
        
        bloques_asignados = {'calentamiento': True, 'core_abs': True, 'cardio': True}
        resultado['reglas_aplicadas'].append('regla_edad_senior (P1)')
        resultado['log'].append("✅ P1: Edad >= 60 - Todos los bloques asignados (bajo impacto)")
    
    # REGLA: Lesión lumbar
    if lesion_lumbar and not bloques_asignados['calentamiento']:
        resultado['calentamiento'] = CALENTAMIENTOS['calentamiento_bajo_impacto']
        bloques_asignados['calentamiento'] = True
        resultado['reglas_aplicadas'].append('regla_lesion_lumbar_calentamiento (P1)')
        resultado['log'].append("✅ P1: Lesión lumbar - Calentamiento bajo impacto")
    
    if lesion_lumbar and not bloques_asignados['core_abs']:
        resultado['core_abs'] = CORE_ABS['abs_basico_1']
        bloques_asignados['core_abs'] = True
        resultado['reglas_aplicadas'].append('regla_lesion_lumbar_core (P1)')
        resultado['log'].append("✅ P1: Lesión lumbar - Core básico")
    
    # REGLA: Muy sedentario o primera sesión
    if (muy_sedentario or primera_sesion) and not bloques_asignados['calentamiento']:
        resultado['calentamiento'] = CALENTAMIENTOS['calentamiento_bajo_impacto']
        bloques_asignados['calentamiento'] = True
        resultado['reglas_aplicadas'].append('regla_muy_sedentario (P1)')
        resultado['log'].append("✅ P1: Muy sedentario/primera sesión - Bajo impacto")
    
    if (muy_sedentario or primera_sesion) and not bloques_asignados['core_abs']:
        resultado['core_abs'] = CORE_ABS['abs_basico_1']
        bloques_asignados['core_abs'] = True
        resultado['reglas_aplicadas'].append('regla_muy_sedentario_core (P1)')
    
    if (muy_sedentario or primera_sesion) and not bloques_asignados['cardio']:
        resultado['cardio'] = CARDIO['cardio_principiante_mantenimiento']
        bloques_asignados['cardio'] = True
        resultado['reglas_aplicadas'].append('regla_muy_sedentario_cardio (P1)')
    
    # REGLA: Lesión de hombro (solo si día incluye hombros/push y no asignado por edad)
    dia_incluye_hombros = any(g in grupos_musculares for g in ['hombros', 'pecho', 'triceps', 'deltoides', 'push'])
    if lesion_hombro and dia_incluye_hombros and not bloques_asignados['calentamiento']:
        resultado['calentamiento'] = CALENTAMIENTOS['calentamiento_hombros_especifico']
        bloques_asignados['calentamiento'] = True
        resultado['reglas_aplicadas'].append('regla_lesion_hombro (P1)')
        resultado['log'].append("✅ P1: Lesión hombro + día push/hombros - Calentamiento específico")
    
    # ========== PRIORIDAD 2: ESPECIFICIDAD ==========
    if not bloques_asignados['calentamiento']:
        # Determinar tipo de calentamiento según grupos musculares
        if any(g in grupos_musculares for g in ['pecho', 'hombros', 'triceps', 'push']):
            resultado['calentamiento'] = CALENTAMIENTOS['calentamiento_push_1']
            resultado['reglas_aplicadas'].append('regla_push (P2)')
            resultado['log'].append("✅ P2: Día push - Calentamiento push")
        elif any(g in grupos_musculares for g in ['espalda', 'biceps', 'dorsales', 'pull']):
            resultado['calentamiento'] = CALENTAMIENTOS['calentamiento_pull_1']
            resultado['reglas_aplicadas'].append('regla_pull (P2)')
            resultado['log'].append("✅ P2: Día pull - Calentamiento pull")
        elif any(g in grupos_musculares for g in ['piernas', 'cuadriceps', 'gluteos', 'isquios', 'femoral']):
            resultado['calentamiento'] = CALENTAMIENTOS['calentamiento_piernas_1']
            resultado['reglas_aplicadas'].append('regla_piernas (P2)')
            resultado['log'].append("✅ P2: Día piernas - Calentamiento piernas")
        elif tipo_sesion == 'fullbody':
            resultado['calentamiento'] = CALENTAMIENTOS['calentamiento_fullbody_1']
            resultado['reglas_aplicadas'].append('regla_fullbody (P2)')
            resultado['log'].append("✅ P2: Full body - Calentamiento full body")
        else:
            # Default: push
            resultado['calentamiento'] = CALENTAMIENTOS['calentamiento_push_1']
            resultado['reglas_aplicadas'].append('regla_default_push (P2)')
            resultado['log'].append("⚠️ P2: Sin match específico - Default push")
    
    # ========== PRIORIDAD 3: OPTIMIZACIÓN ==========
    
    # CORE/ABS según nivel (si no asignado previamente)
    if not bloques_asignados['core_abs']:
        if nivel == 'principiante':
            resultado['core_abs'] = CORE_ABS['abs_basico_1']
            resultado['reglas_aplicadas'].append('abs_principiante (P3)')
            resultado['log'].append("✅ P3: Nivel principiante - Core básico")
        elif nivel == 'intermedio':
            # Rotación semanal entre oblicuos y antirotación
            opciones = ['abs_oblicuos_2', 'abs_antirotacion_3']
            idx = week_number % len(opciones)
            resultado['core_abs'] = CORE_ABS[opciones[idx]]
            resultado['reglas_aplicadas'].append(f'abs_intermedio_rotacion (P3, semana {week_number})')
            resultado['log'].append(f"✅ P3: Nivel intermedio - Rotación semana {week_number} → {opciones[idx]}")
        elif nivel == 'avanzado':
            # Rotación semanal entre antirotación y avanzado
            opciones = ['abs_antirotacion_3', 'abs_avanzado_4']
            idx = week_number % len(opciones)
            resultado['core_abs'] = CORE_ABS[opciones[idx]]
            resultado['reglas_aplicadas'].append(f'abs_avanzado_rotacion (P3, semana {week_number})')
            resultado['log'].append(f"✅ P3: Nivel avanzado - Rotación semana {week_number} → {opciones[idx]}")
        
        # Considerar quema grasa (1-2 veces por semana)
        if ('perdida' in objetivo or 'grasa' in objetivo) and nivel in ['intermedio', 'avanzado']:
            # Usar quema grasa cada 2-3 semanas
            if week_number % 3 == 0:
                resultado['core_abs'] = CORE_ABS['abs_quema_grasa_5']
                resultado['reglas_aplicadas'].append('abs_quema_grasa (P3)')
                resultado['log'].append(f"✅ P3: Pérdida grasa + semana {week_number} - Core metabólico")
    
    # CARDIO según nivel + objetivo (si no asignado previamente)
    if not bloques_asignados['cardio']:
        # Mapeo nivel x objetivo
        cardio_map = {
            'principiante': {
                'perdida_grasa': 'cardio_principiante_perdida_grasa',
                'mantenimiento': 'cardio_principiante_mantenimiento'
            },
            'intermedio': {
                'perdida_grasa': 'cardio_intermedio_perdida_grasa',
                'mantenimiento': 'cardio_intermedio_mantenimiento'
            },
            'avanzado': {
                'perdida_grasa': 'cardio_avanzado_perdida_grasa',
                'mantenimiento': 'cardio_avanzado_mantenimiento'
            }
        }
        
        # Normalizar objetivo
        objetivo_normalizado = 'perdida_grasa' if ('perdida' in objetivo or 'grasa' in objetivo) else 'mantenimiento'
        
        cardio_id = cardio_map.get(nivel, cardio_map['principiante']).get(objetivo_normalizado, 'cardio_principiante_mantenimiento')
        resultado['cardio'] = CARDIO[cardio_id]
        resultado['reglas_aplicadas'].append(f'cardio_{nivel}_{objetivo_normalizado} (P3)')
        resultado['log'].append(f"✅ P3: Cardio {nivel} + {objetivo_normalizado}")
    
    # Aplicar rotación de opciones de cardio (opción 1 o 2)
    if resultado['cardio'] and 'opciones' in resultado['cardio']:
        opcion_idx = session_number % 2  # 0 = opción 1, 1 = opción 2
        resultado['cardio_opcion_seleccionada'] = resultado['cardio']['opciones'][opcion_idx]
        resultado['log'].append(f"🔄 Cardio opción {opcion_idx + 1} (sesión {session_number})")
    
    return resultado


def get_calentamiento_by_id(calentamiento_id: str) -> Optional[Dict]:
    """Obtiene una plantilla de calentamiento por ID"""
    return CALENTAMIENTOS.get(calentamiento_id)


def get_core_abs_by_id(core_id: str) -> Optional[Dict]:
    """Obtiene una plantilla de core/abs por ID"""
    return CORE_ABS.get(core_id)


def get_cardio_by_id(cardio_id: str) -> Optional[Dict]:
    """Obtiene una plantilla de cardio por ID"""
    return CARDIO.get(cardio_id)


def listar_plantillas_disponibles() -> Dict[str, List[str]]:
    """Lista todas las plantillas disponibles por categoría"""
    return {
        'calentamientos': list(CALENTAMIENTOS.keys()),
        'core_abs': list(CORE_ABS.keys()),
        'cardio': list(CARDIO.keys())
    }


# Función de utilidad para testing
if __name__ == "__main__":
    # Test básico
    print("=== TEST DE SELECCIÓN DE PLANTILLAS ===\n")
    
    # Caso 1: Usuario senior
    print("Caso 1: Usuario senior (65 años)")
    resultado1 = seleccionar_plantillas(
        user_data={'edad': 65, 'nivel': 'intermedio', 'objetivo': 'perdida_grasa'},
        dia_entrenamiento={'grupos_musculares': ['pecho', 'triceps'], 'tipo_sesion': 'normal'},
        session_number=1,
        week_number=1
    )
    print(f"Calentamiento: {resultado1['calentamiento']['nombre']}")
    print(f"Core: {resultado1['core_abs']['nombre']}")
    print(f"Cardio: {resultado1['cardio']['nombre']}")
    print(f"Reglas: {resultado1['reglas_aplicadas']}")
    print()
    
    # Caso 2: Usuario joven intermedio
    print("Caso 2: Usuario intermedio (30 años) - día de espalda")
    resultado2 = seleccionar_plantillas(
        user_data={'edad': 30, 'nivel': 'intermedio', 'objetivo': 'mantenimiento'},
        dia_entrenamiento={'grupos_musculares': ['espalda', 'biceps'], 'tipo_sesion': 'normal'},
        session_number=2,
        week_number=2
    )
    print(f"Calentamiento: {resultado2['calentamiento']['nombre']}")
    print(f"Core: {resultado2['core_abs']['nombre']}")
    print(f"Cardio: {resultado2['cardio']['nombre']}")
    print(f"Reglas: {resultado2['reglas_aplicadas']}")
