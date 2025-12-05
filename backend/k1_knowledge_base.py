"""
K1 Knowledge Base Module
=========================
Módulo para consultar y aplicar reglas del K1_ENTRENAMIENTO_ABSTRACTO

Este módulo proporciona funciones para:
- Cargar el K1 desde archivo JSON
- Consultar reglas por nivel de usuario, objetivo, etc.
- Aplicar lógica de decisión basada en el K1
- NO contiene ejercicios concretos, solo lógica abstracta
"""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Cache del K1 en memoria
_K1_CACHE: Optional[Dict] = None

def load_k1() -> Dict:
    """
    Carga el K1 desde archivo JSON
    
    Returns:
        Dict con toda la estructura del K1
    """
    global _K1_CACHE
    
    if _K1_CACHE is not None:
        return _K1_CACHE
    
    k1_path = Path(__file__).parent / 'k1_entrenamiento_abstracto.json'
    
    try:
        with open(k1_path, 'r', encoding='utf-8') as f:
            _K1_CACHE = json.load(f)
        logger.info(f"✅ K1 v{_K1_CACHE['metadata']['version']} cargado correctamente")
        return _K1_CACHE
    except Exception as e:
        logger.error(f"❌ Error cargando K1: {e}")
        raise

def get_taxonomia() -> Dict:
    """Retorna la taxonomía completa del K1"""
    k1 = load_k1()
    return k1['taxonomia']

def get_principios_fundamentales() -> List[Dict]:
    """Retorna los principios fundamentales del entrenamiento"""
    k1 = load_k1()
    return k1['principios_fundamentales']['principios_generales']

def get_reglas_por_nivel(nivel: str) -> Dict:
    """
    Obtiene las reglas específicas para un nivel de usuario
    
    Args:
        nivel: 'principiante', 'intermedio', 'avanzado'
        
    Returns:
        Dict con reglas del modelo_usuario para ese nivel
    """
    k1 = load_k1()
    reglas_generales = k1['modelo_usuario']['reglas_generales']
    
    for regla in reglas_generales:
        if regla['si'].get('nivel_experiencia') == nivel:
            return regla['entonces']
    
    return {}

def get_reglas_por_objetivo(objetivo: str) -> Dict:
    """
    Obtiene las reglas específicas para un objetivo
    
    Args:
        objetivo: 'perdida_grasa', 'hipertrofia', 'fuerza', 'potencia_rendimiento', 'mantenimiento_salud'
        
    Returns:
        Dict con reglas de volumen, intensidad, métodos para ese objetivo
    """
    k1 = load_k1()
    return k1['reglas_objetivo'].get(objetivo, {})

def get_metodos_permitidos(nivel: str, objetivo: str) -> Dict:
    """
    Determina qué métodos de entrenamiento están permitidos
    
    Args:
        nivel: Nivel de experiencia del usuario
        objetivo: Objetivo principal del usuario
        
    Returns:
        Dict con categorías permitidas, evitar, priorizar
    """
    k1 = load_k1()
    reglas_metodos = k1['reglas_metodos_entrenamiento']
    
    # Reglas por nivel
    metodos_nivel = {}
    for regla in reglas_metodos['reglas_por_nivel']:
        if regla['nivel_experiencia'] == nivel:
            metodos_nivel = regla
            break
    
    # Reglas por objetivo
    metodos_objetivo = {}
    for regla in reglas_metodos['reglas_por_objetivo']:
        if regla['objetivo'] == objetivo:
            metodos_objetivo = regla
            break
    
    return {
        'permitidas_por_nivel': metodos_nivel.get('permitir_categorias', []),
        'evitar_por_nivel': metodos_nivel.get('evitar_categorias', []),
        'priorizar_por_objetivo': metodos_objetivo.get('priorizar_categorias', []),
        'usar_con_moderacion': metodos_objetivo.get('usar_con_moderacion', []),
        'evitar_por_objetivo': metodos_objetivo.get('evitar', [])
    }

def get_volumen_recomendado(nivel: str, objetivo: str) -> Dict:
    """
    Determina el volumen abstracto recomendado
    
    Args:
        nivel: Nivel de experiencia
        objetivo: Objetivo principal
        
    Returns:
        Dict con categorías abstractas de volumen
    """
    k1 = load_k1()
    
    # Volumen por nivel
    volumen_nivel = {}
    for regla in k1['reglas_volumen_intensidad']['mapa_volumen_por_nivel']:
        if regla['nivel_experiencia'] == nivel:
            volumen_nivel = regla
            break
    
    # Tendencias por objetivo
    objetivo_data = get_reglas_por_objetivo(objetivo)
    volumen_objetivo = objetivo_data.get('tendencias', {})
    
    return {
        'volumen_por_sesion': volumen_objetivo.get('volumen_por_sesion', volumen_nivel.get('volumen_por_sesion')),
        'series_por_ejercicio': volumen_nivel.get('series_por_ejercicio'),
        'series_semanales_por_musculo': volumen_nivel.get('series_totales_por_musculo_en_semana')
    }

def get_intensidad_recomendada(objetivo: str) -> Dict:
    """
    Determina la intensidad abstracta recomendada
    
    Args:
        objetivo: Objetivo principal
        
    Returns:
        Dict con categorías abstractas de intensidad
    """
    k1 = load_k1()
    
    for regla in k1['reglas_volumen_intensidad']['mapa_intensidad_por_objetivo']:
        if regla['objetivo'] == objetivo:
            return {
                'intensidad_carga': regla['intensidad_carga_preferente'],
                'proximidad_fallo': regla['proximidad_fallo_preferente'],
                'comentarios': regla['comentarios']
            }
    
    return {}

def ajustar_por_fatiga(estado_fatiga: str, volumen_base: str, intensidad_base: str) -> Dict:
    """
    Ajusta volumen e intensidad según estado de fatiga
    
    Args:
        estado_fatiga: 'fatiga_baja', 'fatiga_media', 'fatiga_alta'
        volumen_base: Volumen abstracto base
        intensidad_base: Intensidad abstracta base
        
    Returns:
        Dict con ajustes recomendados
    """
    k1 = load_k1()
    reglas_fatiga = k1['reglas_volumen_intensidad']['reglas_ajuste_fatiga']
    
    for regla in reglas_fatiga:
        if regla['si'].get('estado_fatiga') == estado_fatiga:
            return regla['entonces']
    
    return {
        'ajustar_volumen_por_sesion': 'mantener',
        'ajustar_intensidad_carga': 'mantener',
        'ajustar_proximidad_fallo': 'mantener'
    }

def get_estructura_sesion() -> Dict:
    """Retorna la estructura básica recomendada para una sesión"""
    k1 = load_k1()
    return k1['reglas_diseno_sesion']

def get_reglas_seguridad() -> Dict:
    """Retorna los principios y reglas de seguridad"""
    k1 = load_k1()
    return k1['reglas_seguridad_y_restricciones']

def get_reglas_progresion() -> Dict:
    """Retorna las reglas de progresión"""
    k1 = load_k1()
    return k1['reglas_progresion']

def validate_user_profile(perfil_usuario: Dict) -> Dict:
    """
    Valida que el perfil del usuario tenga los campos necesarios
    
    Args:
        perfil_usuario: Dict con datos del usuario
        
    Returns:
        Dict con validación y errores si los hay
    """
    required_fields = [
        'nivel_experiencia',
        'objetivo_principal',
        'frecuencia_semanal_entrenamiento'
    ]
    
    errores = []
    for field in required_fields:
        if field not in perfil_usuario:
            errores.append(f"Campo requerido faltante: {field}")
    
    # Validar valores contra taxonomía
    taxonomia = get_taxonomia()
    
    if perfil_usuario.get('nivel_experiencia') not in taxonomia['niveles_usuario']:
        errores.append(f"Nivel de experiencia inválido: {perfil_usuario.get('nivel_experiencia')}")
    
    if perfil_usuario.get('objetivo_principal') not in taxonomia['objetivos_principales']:
        errores.append(f"Objetivo principal inválido: {perfil_usuario.get('objetivo_principal')}")
    
    return {
        'valido': len(errores) == 0,
        'errores': errores
    }

def generar_contexto_para_e4(perfil_usuario: Dict) -> str:
    """
    Genera el contexto completo del K1 que debe usarse en el prompt de E4
    
    Args:
        perfil_usuario: Perfil del usuario (nivel, objetivo, etc.)
        
    Returns:
        String con el contexto formateado para E4
    """
    k1 = load_k1()
    nivel = perfil_usuario.get('nivel_experiencia', 'intermedio')
    objetivo = perfil_usuario.get('objetivo_principal', 'mantenimiento_salud')
    
    # Obtener reglas relevantes
    reglas_nivel = get_reglas_por_nivel(nivel)
    reglas_objetivo = get_reglas_por_objetivo(objetivo)
    metodos = get_metodos_permitidos(nivel, objetivo)
    volumen = get_volumen_recomendado(nivel, objetivo)
    intensidad = get_intensidad_recomendada(objetivo)
    
    contexto = f"""
# CONTEXTO K1 PARA USUARIO

## Perfil del Usuario
- Nivel de experiencia: {nivel}
- Objetivo principal: {objetivo}

## Principios Fundamentales a Respetar
{json.dumps(k1['principios_fundamentales']['principios_generales'], indent=2, ensure_ascii=False)}

## Reglas para Nivel {nivel.upper()}
{json.dumps(reglas_nivel, indent=2, ensure_ascii=False)}

## Reglas para Objetivo {objetivo.upper()}
{json.dumps(reglas_objetivo, indent=2, ensure_ascii=False)}

## Métodos de Entrenamiento
{json.dumps(metodos, indent=2, ensure_ascii=False)}

## Volumen Recomendado (Abstracto)
{json.dumps(volumen, indent=2, ensure_ascii=False)}

## Intensidad Recomendada (Abstracta)
{json.dumps(intensidad, indent=2, ensure_ascii=False)}

## Estructura de Sesión
{json.dumps(k1['reglas_diseno_sesion'], indent=2, ensure_ascii=False)}

## Reglas de Seguridad
{json.dumps(k1['reglas_seguridad_y_restricciones'], indent=2, ensure_ascii=False)}

## Taxonomía de Patrones y Tipos
- Patrones de Movimiento: {', '.join(k1['taxonomia']['patrones_movimiento'])}
- Tipos de Ejercicio: {', '.join(k1['taxonomia']['tipos_ejercicio'])}
"""
    
    return contexto

# Función de utilidad para tests
if __name__ == "__main__":
    # Test básico
    k1 = load_k1()
    print(f"✅ K1 cargado: {k1['metadata']['nombre']} v{k1['metadata']['version']}")
    
    # Test de consultas
    reglas_principiante = get_reglas_por_nivel('principiante')
    print(f"\n📋 Reglas principiante: {reglas_principiante}")
    
    reglas_hipertrofia = get_reglas_por_objetivo('hipertrofia')
    print(f"\n💪 Reglas hipertrofia: {reglas_hipertrofia}")
    
    contexto = generar_contexto_para_e4({
        'nivel_experiencia': 'intermedio',
        'objetivo_principal': 'hipertrofia'
    })
    print(f"\n📄 Contexto generado ({len(contexto)} chars)")
