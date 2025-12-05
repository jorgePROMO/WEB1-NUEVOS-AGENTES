"""
Block C - Core/ABS Template
============================
Template paramétrico para generar bloque de trabajo de core

Enfoque K1:
- Anti-rotación
- Anti-extensión
- Anti-flexión (limitado por catálogo)

Adapta según:
- Nivel de experiencia
- Volumen del Bloque B (no sobrecargar)
- Lesiones (especialmente lumbar)
- Objetivo principal

Autor: E1 Agent
Fecha: Diciembre 2025
"""

from typing import Dict, List, Optional
from exercise_catalog_loader import (
    filter_exercises,
    check_health_safety,
    enrich_exercise_with_variant
)


def generate_core_block(
    nivel: str = "intermedio",  # principiante, intermedio, avanzado
    objetivo: str = "hipertrofia",  # perdida_grasa, hipertrofia, fuerza
    volumen_bloque_b: str = "medio",  # bajo, medio, alto
    injuries: Optional[List[str]] = None,
    environment: str = "gym"
) -> Dict:
    """
    Genera Block C (Core/ABS) adaptado al contexto
    
    Filosofía:
    - Core como COMPLEMENTO del B, no como trabajo principal
    - Si B fue alto volumen → C más ligero
    - Si hay lesión lumbar → ejercicios ultra-seguros (antirotación, estabilidad)
    
    Patrones priorizados:
    1. Anti-rotación (Pallof press, bird dog, etc.)
    2. Anti-extensión (Plancha, dead bug, etc.)
    3. Anti-flexión (Menos común, más para avanzados)
    
    Args:
        nivel: principiante, intermedio, avanzado
        objetivo: perdida_grasa, hipertrofia, fuerza
        volumen_bloque_b: bajo, medio, alto (para ajustar volumen de C)
        injuries: Lista de lesiones
        environment: gym, home
    
    Returns:
        Dict con estructura del Block C
    """
    
    injuries = injuries or []
    has_back_injury = "low_back" in injuries
    
    # Ajustar volumen según Bloque B
    if volumen_bloque_b == "alto":
        num_exercises = 2  # B fue demandante, C ligero
        sets_per_exercise = 2
    elif volumen_bloque_b == "medio":
        num_exercises = 2 if nivel == "principiante" else 3
        sets_per_exercise = 2 if nivel == "principiante" else 3
    else:  # bajo
        num_exercises = 3
        sets_per_exercise = 3
    
    # Si nivel es avanzado, puede manejar más
    if nivel == "avanzado" and volumen_bloque_b != "alto":
        num_exercises = min(num_exercises + 1, 4)
    
    # Si hay lesión lumbar, reducir volumen y ser conservador
    if has_back_injury:
        num_exercises = max(2, num_exercises - 1)
        sets_per_exercise = min(sets_per_exercise, 2)
    
    block_c = {
        "id": "C",
        "block_name": "Bloque C - Core & Estabilidad",
        "focus": ["core", "estabilidad"],
        "exercises": []
    }
    
    # === SELECCIÓN DE EJERCICIOS DEL CATÁLOGO ===
    
    # PATRÓN 1: Anti-rotación (siempre incluir, es el más seguro)
    antirot_exercises = filter_exercises(
        movement_pattern="core_antirotacion",
        difficulty=nivel if nivel != "avanzado" else "intermedio",  # Avanzados pueden hacer intermedios
        environment=environment,
        usable_for_plans=True
    )
    
    # Filtrar por seguridad lumbar
    if has_back_injury:
        antirot_exercises = [ex for ex in antirot_exercises if check_health_safety(ex, 'low_back') == 'seguro']
    
    # Priorizar bird_dog (clásico y seguro)
    antirot_selected = None
    for ex in antirot_exercises:
        if 'bird' in ex['exercise_code'].lower() or 'dog' in ex['exercise_code'].lower():
            antirot_selected = ex
            break
    
    if not antirot_selected and antirot_exercises:
        antirot_selected = antirot_exercises[0]
    
    if antirot_selected:
        enriched = enrich_exercise_with_variant(antirot_selected['exercise_code'])
        block_c['exercises'].append({
            "order": 1,
            "exercise_code": antirot_selected['exercise_code'],
            "name": enriched.get('name_std', antirot_selected['exercise_code']) if enriched else antirot_selected['exercise_code'],
            "video_url": enriched.get('video_url', '') if enriched else '',
            "patron": "core_antirotacion",
            "series": sets_per_exercise,
            "reps": "10-12 por lado" if "lado" in antirot_selected['exercise_code'] else "30-45 seg",
            "rest": "45-60 seg",
            "notes": "Control total, core activado. Sin compensaciones" if not has_back_injury else "CRÍTICO: Mantener columna neutra, sin dolor"
        })
    
    # PATRÓN 2: Anti-extensión (plancha frontal y variantes)
    if num_exercises >= 2:
        antiext_exercises = filter_exercises(
            movement_pattern="core_antiextension",
            difficulty="principiante" if nivel == "principiante" else "intermedio",
            environment=environment,
            usable_for_plans=True
        )
        
        if has_back_injury:
            antiext_exercises = [ex for ex in antiext_exercises if check_health_safety(ex, 'low_back') == 'seguro']
        
        # Priorizar plancha frontal
        antiext_selected = None
        for ex in antiext_exercises:
            if 'plancha_frontal' in ex['exercise_code'].lower() or 'plank' in ex['exercise_code'].lower():
                antiext_selected = ex
                break
        
        if not antiext_selected and antiext_exercises:
            antiext_selected = antiext_exercises[0]
        
        if antiext_selected:
            enriched = enrich_exercise_with_variant(antiext_selected['exercise_code'])
            
            # Ajustar tiempo según nivel
            if nivel == "principiante":
                time_spec = "20-30 seg"
            elif nivel == "intermedio":
                time_spec = "30-45 seg"
            else:
                time_spec = "45-60 seg"
            
            block_c['exercises'].append({
                "order": 2,
                "exercise_code": antiext_selected['exercise_code'],
                "name": enriched.get('name_std', antiext_selected['exercise_code']) if enriched else antiext_selected['exercise_code'],
                "video_url": enriched.get('video_url', '') if enriched else '',
                "patron": "core_antiextension",
                "series": sets_per_exercise,
                "reps": time_spec,
                "rest": "45-60 seg",
                "notes": "Cuerpo alineado, glúteos apretados, no dejar caer cadera" if not has_back_injury else "Versión reducida si hay molestias (rodillas apoyadas OK)"
            })
    
    # PATRÓN 3: Otro ejercicio anti-rotación o anti-extensión (variedad)
    if num_exercises >= 3:
        # Buscar otro ejercicio diferente
        remaining_antirot = [ex for ex in antirot_exercises if ex['exercise_code'] != (antirot_selected['exercise_code'] if antirot_selected else None)]
        
        if remaining_antirot:
            third_exercise = remaining_antirot[0]
            enriched = enrich_exercise_with_variant(third_exercise['exercise_code'])
            
            block_c['exercises'].append({
                "order": 3,
                "exercise_code": third_exercise['exercise_code'],
                "name": enriched.get('name_std', third_exercise['exercise_code']) if enriched else third_exercise['exercise_code'],
                "video_url": enriched.get('video_url', '') if enriched else '',
                "patron": "core_antirotacion",
                "series": sets_per_exercise,
                "reps": "10-12 por lado" if "lado" in third_exercise['exercise_code'] else "30-45 seg",
                "rest": "45 seg",
                "notes": "Variación para trabajar core desde otro ángulo"
            })
    
    # PATRÓN 4: Si nivel avanzado y no hay lesión, agregar un cuarto ejercicio más desafiante
    if num_exercises >= 4 and nivel == "avanzado" and not has_back_injury:
        advanced_exercises = filter_exercises(
            movement_pattern="core_antiextension",
            difficulty="avanzado",
            environment=environment,
            usable_for_plans=True
        )
        
        if advanced_exercises:
            fourth_exercise = advanced_exercises[0]
            enriched = enrich_exercise_with_variant(fourth_exercise['exercise_code'])
            
            block_c['exercises'].append({
                "order": 4,
                "exercise_code": fourth_exercise['exercise_code'],
                "name": enriched.get('name_std', fourth_exercise['exercise_code']) if enriched else fourth_exercise['exercise_code'],
                "video_url": enriched.get('video_url', '') if enriched else '',
                "patron": "core_antiextension",
                "series": 2,
                "reps": "8-10 reps" if "elevacion" in fourth_exercise['exercise_code'] else "30-40 seg",
                "rest": "60 seg",
                "notes": "Ejercicio avanzado, mantener técnica perfecta"
            })
    
    # Densidad del bloque
    if objetivo == "perdida_grasa":
        block_c["densidad"] = "alta"
        block_c["rest_note"] = "Descansos cortos (30-45 seg) para mantener FC elevada"
    else:
        block_c["densidad"] = "media"
        block_c["rest_note"] = "Descansos moderados (45-60 seg) para recuperación completa"
    
    # Notas generales
    block_c["general_notes"] = [
        f"Core diseñado como complemento del Bloque B ({volumen_bloque_b} volumen)",
        "Objetivo: estabilidad y transferencia, no fatiga extrema",
        f"Enfoque: {sets_per_exercise} series x {num_exercises} ejercicios",
        "Técnica > Volumen: Mantener calidad en cada repetición"
    ]
    
    if has_back_injury:
        block_c["general_notes"].extend([
            "⚠️ ADAPTACIÓN LUMBAR: Ejercicios seleccionados para máxima seguridad",
            "REGLA: Si hay dolor, reducir rango o cambiar ejercicio",
            "Priorizar antirotación sobre flexión/extensión"
        ])
    
    block_c["duration_estimate_min"] = num_exercises * sets_per_exercise * 1.5  # ~1.5 min por serie
    
    return block_c


def format_core_for_display(core_block: Dict) -> str:
    """
    Formatea el bloque de core para visualización
    
    Args:
        core_block: Diccionario con estructura del Block C
    
    Returns:
        String formateado para mostrar
    """
    
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"{core_block['block_name']}")
    output.append(f"Duración estimada: {core_block.get('duration_estimate_min', 'N/A')} minutos")
    output.append(f"Focus: {', '.join(core_block['focus'])}")
    output.append(f"{'='*60}\n")
    
    for exercise in core_block['exercises']:
        output.append(f"\n{exercise['order']}. {exercise['name']}")
        output.append(f"   Código: {exercise['exercise_code']}")
        output.append(f"   Patrón: {exercise['patron']}")
        output.append(f"   Series: {exercise['series']} x Reps: {exercise['reps']}")
        output.append(f"   Descanso: {exercise['rest']}")
        if exercise.get('video_url'):
            output.append(f"   🎥 Video: {exercise['video_url'][:50]}...")
        if exercise.get('notes'):
            output.append(f"   📝 {exercise['notes']}")
    
    if core_block.get('rest_note'):
        output.append(f"\n⏱️ {core_block['rest_note']}")
    
    if core_block.get('general_notes'):
        output.append(f"\n\n📋 NOTAS GENERALES:")
        for note in core_block['general_notes']:
            output.append(f"   • {note}")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Test del template
    print("🧪 Probando Block C Template...")
    
    # Test 1: Intermedio, hipertrofia, volumen medio, sin lesiones
    print("\n" + "="*60)
    print("TEST 1: Intermedio - Hipertrofia - Volumen medio - Sin lesiones")
    print("="*60)
    core1 = generate_core_block("intermedio", "hipertrofia", "medio", [], "gym")
    print(format_core_for_display(core1))
    
    # Test 2: Principiante, pérdida grasa, volumen bajo, sin lesiones
    print("\n" + "="*60)
    print("TEST 2: Principiante - Pérdida grasa - Volumen bajo")
    print("="*60)
    core2 = generate_core_block("principiante", "perdida_grasa", "bajo", [], "gym")
    print(format_core_for_display(core2))
    
    # Test 3: Intermedio, hipertrofia, volumen alto, CON LESIÓN LUMBAR
    print("\n" + "="*60)
    print("TEST 3: Intermedio - Volumen alto - LESIÓN LUMBAR")
    print("="*60)
    core3 = generate_core_block("intermedio", "hipertrofia", "alto", ["low_back"], "gym")
    print(format_core_for_display(core3))
    
    # Test 4: Avanzado, fuerza, volumen medio, sin lesiones
    print("\n" + "="*60)
    print("TEST 4: Avanzado - Fuerza - Volumen medio")
    print("="*60)
    core4 = generate_core_block("avanzado", "fuerza", "medio", [], "gym")
    print(format_core_for_display(core4))
    
    print("\n✅ Tests completados")
