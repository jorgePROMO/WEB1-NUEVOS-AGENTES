"""
Test K1 + Catalog Integration
==============================
Script para probar la integración completa del sistema K1 + Catálogo de Ejercicios

Verifica:
1. K1 Knowledge Base carga correctamente
2. Exercise Catalog carga correctamente
3. Filtrado de ejercicios por criterios K1
4. Traducción de términos abstractos a concretos
5. Validación de ejercicios por health_flags

Autor: E1 Agent
Fecha: Diciembre 2025
"""

import json
from k1_knowledge_base import (
    load_k1,
    get_reglas_por_nivel,
    get_reglas_por_objetivo,
    get_volumen_recomendado,
    get_intensidad_recomendada
)
from exercise_catalog_loader import (
    load_exercise_catalog,
    load_exercise_variants,
    get_exercise_by_code,
    filter_exercises,
    check_health_safety,
    enrich_exercise_with_variant,
    get_catalog_stats
)

def test_k1_loading():
    """Prueba 1: Cargar K1"""
    print("=" * 60)
    print("🧪 PRUEBA 1: Carga del K1 Knowledge Base")
    print("=" * 60)
    
    try:
        k1 = load_k1()
        print(f"✅ K1 cargado correctamente")
        print(f"   Versión: {k1['metadata']['version']}")
        print(f"   Descripción: {k1['metadata']['descripcion']}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_catalog_loading():
    """Prueba 2: Cargar Catálogo"""
    print("\n" + "=" * 60)
    print("🧪 PRUEBA 2: Carga del Catálogo de Ejercicios")
    print("=" * 60)
    
    try:
        catalog = load_exercise_catalog()
        variants = load_exercise_variants()
        stats = get_catalog_stats()
        
        print(f"✅ Catálogo cargado correctamente")
        print(f"   Total ejercicios: {stats['total_exercises']}")
        print(f"   Total variantes: {stats['total_variants']}")
        print(f"   Usables para planes: {stats['usable_for_plans']}")
        print(f"   Por dificultad:")
        for diff, count in stats['by_difficulty'].items():
            print(f"      - {diff}: {count}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_k1_rules():
    """Prueba 3: Consultar reglas K1"""
    print("\n" + "=" * 60)
    print("🧪 PRUEBA 3: Consulta de Reglas K1")
    print("=" * 60)
    
    try:
        # Perfil de prueba: intermedio, hipertrofia
        nivel = "intermedio"
        objetivo = "hipertrofia"
        
        reglas_nivel = get_reglas_por_nivel(nivel)
        reglas_objetivo = get_reglas_por_objetivo(objetivo)
        volumen = get_volumen_recomendado(nivel, objetivo)
        intensidad = get_intensidad_recomendada(objetivo)
        
        print(f"✅ Reglas K1 obtenidas para: {nivel} + {objetivo}")
        print(f"   Volumen recomendado: {volumen.get('volumen_por_sesion', 'N/A')}")
        print(f"   Series por ejercicio: {volumen.get('series_por_ejercicio', 'N/A')}")
        print(f"   Intensidad carga: {intensidad.get('intensidad_carga', 'N/A')}")
        print(f"   Proximidad fallo: {intensidad.get('proximidad_fallo', 'N/A')}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_exercise_filtering():
    """Prueba 4: Filtrar ejercicios según criterios K1"""
    print("\n" + "=" * 60)
    print("🧪 PRUEBA 4: Filtrado de Ejercicios por Criterios K1")
    print("=" * 60)
    
    try:
        # Buscar ejercicios de empuje horizontal para intermedio en gym
        exercises = filter_exercises(
            movement_pattern="empuje_horizontal",
            difficulty="intermedio",
            environment="gym",
            usable_for_plans=True
        )
        
        print(f"✅ Filtrado exitoso")
        print(f"   Patrón: empuje_horizontal")
        print(f"   Dificultad: intermedio")
        print(f"   Entorno: gym")
        print(f"   Ejercicios encontrados: {len(exercises)}")
        
        if exercises:
            example = exercises[0]
            print(f"\n   Ejemplo: {example['exercise_code']}")
            print(f"      - Familia: {example['exercise_family']}")
            print(f"      - Músculos primarios: {example['primary_muscles_clean']}")
            print(f"      - Tipo de carga: {example['load_type_clean']}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_health_safety():
    """Prueba 5: Verificar health_flags para lesiones"""
    print("\n" + "=" * 60)
    print("🧪 PRUEBA 5: Verificación de Seguridad (health_flags)")
    print("=" * 60)
    
    try:
        # Buscar ejercicios de empuje horizontal
        exercises = filter_exercises(
            movement_pattern="empuje_horizontal",
            usable_for_plans=True
        )[:10]
        
        print(f"✅ Verificando seguridad para hombro inestable...")
        
        safe_exercises = []
        unsafe_exercises = []
        
        for ex in exercises:
            safety = check_health_safety(ex, 'shoulder')
            if safety == 'seguro':
                safe_exercises.append(ex['exercise_code'])
            elif safety in ['precaucion', 'evitar']:
                unsafe_exercises.append((ex['exercise_code'], safety))
        
        print(f"   Ejercicios seguros: {len(safe_exercises)}")
        if safe_exercises[:3]:
            print(f"      Ejemplos: {', '.join(safe_exercises[:3])}")
        
        print(f"   Ejercicios con precaución/evitar: {len(unsafe_exercises)}")
        if unsafe_exercises[:3]:
            for code, flag in unsafe_exercises[:3]:
                print(f"      - {code}: {flag}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_exercise_enrichment():
    """Prueba 6: Enriquecer ejercicio con variante"""
    print("\n" + "=" * 60)
    print("🧪 PRUEBA 6: Enriquecimiento de Ejercicio con Variante")
    print("=" * 60)
    
    try:
        # Probar con un ejercicio conocido
        exercise_code = "press_banca_barra"
        
        enriched = enrich_exercise_with_variant(exercise_code)
        
        if enriched:
            print(f"✅ Ejercicio enriquecido correctamente")
            print(f"   Código: {enriched['exercise_code']}")
            print(f"   Nombre: {enriched['name_std']}")
            print(f"   Patrón: {enriched['movement_pattern']}")
            print(f"   Músculos: {enriched['primary_muscles_clean']}")
            print(f"   ID Variante: {enriched.get('variant_id', 'N/A')}")
            print(f"   Video URL: {enriched.get('video_url', 'N/A')[:50]}...")
            return True
        else:
            print(f"❌ Ejercicio no encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_full_integration():
    """Prueba 7: Integración completa K1 + Catálogo"""
    print("\n" + "=" * 60)
    print("🧪 PRUEBA 7: Integración Completa K1 + Catálogo")
    print("=" * 60)
    
    try:
        # 1. Consultar K1 para un perfil
        nivel = "intermedio"
        objetivo = "hipertrofia"
        
        print(f"📋 Perfil de usuario:")
        print(f"   - Nivel: {nivel}")
        print(f"   - Objetivo: {objetivo}")
        print(f"   - Lesión: hombro inestable")
        
        # 2. Obtener recomendaciones K1
        volumen = get_volumen_recomendado(nivel, objetivo)
        intensidad = get_intensidad_recomendada(objetivo)
        
        print(f"\n🧠 Recomendaciones K1:")
        print(f"   - Volumen: {volumen.get('volumen_por_sesion', 'N/A')}")
        print(f"   - Intensidad: {intensidad.get('intensidad_carga', 'N/A')}")
        
        # 3. Buscar ejercicios compatibles
        exercises = filter_exercises(
            movement_pattern="empuje_horizontal",
            difficulty=nivel,
            environment="gym",
            usable_for_plans=True
        )
        
        # 4. Filtrar por seguridad
        safe_exercises = []
        for ex in exercises:
            if check_health_safety(ex, 'shoulder') == 'seguro':
                safe_exercises.append(ex)
        
        print(f"\n💪 Ejercicios seleccionados:")
        print(f"   - Total encontrados: {len(exercises)}")
        print(f"   - Seguros para hombro: {len(safe_exercises)}")
        
        # 5. Enriquecer algunos ejercicios
        if safe_exercises:
            print(f"\n📝 Ejemplos de ejercicios enriquecidos:")
            for i, ex in enumerate(safe_exercises[:3], 1):
                enriched = enrich_exercise_with_variant(ex['exercise_code'])
                if enriched:
                    print(f"   {i}. {enriched['name_std']}")
                    print(f"      - Código: {enriched['exercise_code']}")
                    print(f"      - Patrón: {enriched['movement_pattern']}")
                    print(f"      - Health flags: shoulder={enriched['health_flags']['shoulder_unstable']}")
        
        print(f"\n✅ INTEGRACIÓN COMPLETA EXITOSA")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Ejecuta todas las pruebas"""
    print("\n" + "=" * 60)
    print("🚀 INICIANDO SUITE DE PRUEBAS K1 + CATÁLOGO")
    print("=" * 60)
    
    tests = [
        ("K1 Loading", test_k1_loading),
        ("Catalog Loading", test_catalog_loading),
        ("K1 Rules", test_k1_rules),
        ("Exercise Filtering", test_exercise_filtering),
        ("Health Safety", test_health_safety),
        ("Exercise Enrichment", test_exercise_enrichment),
        ("Full Integration", test_full_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Error crítico en {name}: {e}")
            results.append((name, False))
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n🎯 RESULTADO FINAL: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡TODAS LAS PRUEBAS PASARON!")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
