"""
Exercise Catalog Loader
=======================
Módulo para cargar y consultar el catálogo oficial de ejercicios EDN360

Archivos fuente:
- exercise_catalog_edn360.json: Catálogo de ejercicios con propiedades abstractas
- exercise_variants_edn360.json: Variantes concretas con nombres y videos
- substitution_rules_edn360.json: Reglas de sustitución inteligente

Autor: E1 Agent
Fecha: Diciembre 2025
"""

import json
import os
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Rutas a los archivos del catálogo
CATALOG_DIR = os.path.dirname(__file__)
EXERCISE_CATALOG_PATH = os.path.join(CATALOG_DIR, 'exercise_catalog_edn360.json')
EXERCISE_VARIANTS_PATH = os.path.join(CATALOG_DIR, 'exercise_variants_edn360.json')
SUBSTITUTION_RULES_PATH = os.path.join(CATALOG_DIR, 'substitution_rules_edn360.json')

# Cache global
_catalog_cache = None
_variants_cache = None
_substitution_rules_cache = None


def load_exercise_catalog() -> List[Dict]:
    """
    Carga el catálogo de ejercicios
    
    Returns:
        Lista de ejercicios con propiedades abstractas
    """
    global _catalog_cache
    
    if _catalog_cache is not None:
        return _catalog_cache
    
    try:
        with open(EXERCISE_CATALOG_PATH, 'r', encoding='utf-8') as f:
            _catalog_cache = json.load(f)
        logger.info(f"✅ Catálogo de ejercicios cargado: {len(_catalog_cache)} ejercicios")
        return _catalog_cache
    except Exception as e:
        logger.error(f"❌ Error cargando catálogo de ejercicios: {e}")
        raise


def load_exercise_variants() -> List[Dict]:
    """
    Carga las variantes de ejercicios
    
    Returns:
        Lista de variantes con nombres, videos, etc.
    """
    global _variants_cache
    
    if _variants_cache is not None:
        return _variants_cache
    
    try:
        with open(EXERCISE_VARIANTS_PATH, 'r', encoding='utf-8') as f:
            _variants_cache = json.load(f)
        logger.info(f"✅ Variantes de ejercicios cargadas: {len(_variants_cache)} variantes")
        return _variants_cache
    except Exception as e:
        logger.error(f"❌ Error cargando variantes de ejercicios: {e}")
        raise


def load_substitution_rules() -> Dict:
    """
    Carga las reglas de sustitución
    
    Returns:
        Diccionario con reglas de sustitución
    """
    global _substitution_rules_cache
    
    if _substitution_rules_cache is not None:
        return _substitution_rules_cache
    
    try:
        with open(SUBSTITUTION_RULES_PATH, 'r', encoding='utf-8') as f:
            _substitution_rules_cache = json.load(f)
        logger.info(f"✅ Reglas de sustitución cargadas")
        return _substitution_rules_cache
    except Exception as e:
        logger.error(f"❌ Error cargando reglas de sustitución: {e}")
        raise


def get_exercise_by_code(exercise_code: str) -> Optional[Dict]:
    """
    Busca un ejercicio por su código
    
    Args:
        exercise_code: Código del ejercicio (ej: "press_banca_barra")
    
    Returns:
        Diccionario con datos del ejercicio o None si no existe
    """
    catalog = load_exercise_catalog()
    
    for exercise in catalog:
        if exercise.get('exercise_code') == exercise_code:
            return exercise
    
    logger.warning(f"⚠️ Ejercicio no encontrado: {exercise_code}")
    return None


def get_variants_by_code(exercise_code: str) -> List[Dict]:
    """
    Obtiene todas las variantes de un ejercicio
    
    Args:
        exercise_code: Código del ejercicio
    
    Returns:
        Lista de variantes del ejercicio
    """
    variants = load_exercise_variants()
    
    matching_variants = [
        v for v in variants 
        if v.get('exercise_code') == exercise_code
    ]
    
    return matching_variants


def filter_exercises(
    movement_pattern: Optional[str] = None,
    difficulty: Optional[str] = None,
    environment: Optional[str] = None,
    load_type: Optional[str] = None,
    usable_for_plans: bool = True
) -> List[Dict]:
    """
    Filtra ejercicios por criterios
    
    Args:
        movement_pattern: Patrón de movimiento (ej: "empuje_horizontal")
        difficulty: Nivel de dificultad (principiante, intermedio, avanzado)
        environment: Entorno (gym, home)
        load_type: Tipo de carga (barra, mancuernas, maquina, etc.)
        usable_for_plans: Solo ejercicios usables en planes
    
    Returns:
        Lista de ejercicios que cumplen los criterios
    """
    catalog = load_exercise_catalog()
    filtered = catalog
    
    if usable_for_plans:
        filtered = [e for e in filtered if e.get('usable_for_plans', False)]
    
    if movement_pattern:
        filtered = [e for e in filtered if e.get('movement_pattern') == movement_pattern]
    
    if difficulty:
        filtered = [e for e in filtered if e.get('difficulty_clean') == difficulty]
    
    if environment:
        filtered = [e for e in filtered if environment in e.get('environments', [])]
    
    if load_type:
        filtered = [e for e in filtered if load_type in e.get('load_type_clean', [])]
    
    return filtered


def check_health_safety(exercise: Dict, injury_type: str) -> str:
    """
    Verifica la seguridad de un ejercicio para una lesión específica
    
    Args:
        exercise: Diccionario del ejercicio
        injury_type: Tipo de lesión (shoulder, low_back, knee)
    
    Returns:
        "seguro", "precaucion", o "evitar"
    """
    health_flags = exercise.get('health_flags', {})
    
    flag_map = {
        'shoulder': 'shoulder_unstable',
        'low_back': 'low_back_sensitive',
        'knee': 'knee_sensitive'
    }
    
    flag_key = flag_map.get(injury_type)
    if not flag_key:
        return "seguro"
    
    return health_flags.get(flag_key, "seguro")


def enrich_exercise_with_variant(exercise_code: str) -> Dict:
    """
    Enriquece un ejercicio con información de su mejor variante
    
    Args:
        exercise_code: Código del ejercicio
    
    Returns:
        Diccionario con ejercicio + variante
    """
    exercise = get_exercise_by_code(exercise_code)
    if not exercise:
        return None
    
    variants = get_variants_by_code(exercise_code)
    
    # Seleccionar la mejor variante (primera usable)
    best_variant = None
    for variant in variants:
        if variant.get('usable_for_plans', False):
            best_variant = variant
            break
    
    if not best_variant and variants:
        best_variant = variants[0]
    
    # Combinar datos
    enriched = {
        **exercise,
        'variant_id': best_variant.get('id') if best_variant else None,
        'name_std': best_variant.get('name_std') if best_variant else exercise_code,
        'video_url': best_variant.get('video_url') if best_variant else ""
    }
    
    return enriched


def get_catalog_stats() -> Dict:
    """
    Obtiene estadísticas del catálogo
    
    Returns:
        Diccionario con estadísticas
    """
    catalog = load_exercise_catalog()
    variants = load_exercise_variants()
    
    # Contar por patrón de movimiento
    patterns = {}
    for ex in catalog:
        pattern = ex.get('movement_pattern', 'unknown')
        patterns[pattern] = patterns.get(pattern, 0) + 1
    
    # Contar por dificultad
    difficulties = {}
    for ex in catalog:
        diff = ex.get('difficulty_clean', 'unknown')
        difficulties[diff] = difficulties.get(diff, 0) + 1
    
    # Contar usables
    usable_count = len([e for e in catalog if e.get('usable_for_plans', False)])
    
    return {
        'total_exercises': len(catalog),
        'total_variants': len(variants),
        'usable_for_plans': usable_count,
        'by_movement_pattern': patterns,
        'by_difficulty': difficulties
    }


if __name__ == "__main__":
    # Test básico
    print("🧪 Probando exercise_catalog_loader.py...")
    
    catalog = load_exercise_catalog()
    print(f"✅ Catálogo cargado: {len(catalog)} ejercicios")
    
    variants = load_exercise_variants()
    print(f"✅ Variantes cargadas: {len(variants)} variantes")
    
    rules = load_substitution_rules()
    print(f"✅ Reglas de sustitución cargadas")
    
    # Buscar ejercicio de ejemplo
    example = get_exercise_by_code("press_banca_barra")
    if example:
        print(f"✅ Ejercicio encontrado: {example.get('exercise_code')}")
    
    # Filtrar ejercicios
    horizontal_push = filter_exercises(movement_pattern="empuje_horizontal")
    print(f"✅ Ejercicios de empuje horizontal: {len(horizontal_push)}")
    
    # Estadísticas
    stats = get_catalog_stats()
    print(f"✅ Estadísticas: {stats['total_exercises']} ejercicios, {stats['usable_for_plans']} usables")
