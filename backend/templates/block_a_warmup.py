"""
Block A - Calentamiento/Warmup Template
========================================
Template paramétrico para generar bloque de calentamiento

Adapta según:
- Nivel de experiencia (principiante, intermedio, avanzado)
- Tipo de entrenamiento (upper, lower, full_body)
- Lesiones (shoulder, low_back, knee)
- Entorno (gym, home)

Autor: E1 Agent
Fecha: Diciembre 2025
"""

from typing import Dict, List, Optional
from exercise_catalog_loader import (
    filter_exercises,
    check_health_safety,
    enrich_exercise_with_variant
)


def generate_warmup_block(
    training_focus: str,  # "upper", "lower", "full_body"
    nivel: str = "intermedio",  # principiante, intermedio, avanzado
    injuries: Optional[List[str]] = None,  # ["shoulder", "low_back", "knee"]
    environment: str = "gym",  # gym, home
    session_duration_min: int = 60
) -> Dict:
    """
    Genera Block A (Calentamiento) adaptado al contexto
    
    Estructura:
    1. Movilidad general (5-8 min)
    2. Activación específica según focus (3-5 min)
    3. Preparación cardiovascular ligera (2-3 min)
    
    Args:
        training_focus: upper, lower, full_body
        nivel: principiante, intermedio, avanzado
        injuries: Lista de lesiones a respetar
        environment: gym, home
        session_duration_min: Duración total de sesión
    
    Returns:
        Dict con estructura del Block A
    """
    
    injuries = injuries or []
    
    # Ajustar duración según tiempo disponible
    if session_duration_min < 45:
        warmup_duration = 5  # Sesiones cortas
    elif session_duration_min < 60:
        warmup_duration = 8
    else:
        warmup_duration = 10  # Sesiones largas
    
    # Estructura base
    block_a = {
        "id": "A",
        "block_name": "Bloque A - Calentamiento/Activación",
        "duration_min": warmup_duration,
        "components": []
    }
    
    # === COMPONENTE 1: MOVILIDAD GENERAL ===
    mobility_component = {
        "name": "Movilidad General",
        "duration_min": int(warmup_duration * 0.5),
        "exercises": []
    }
    
    # Movilidad articular básica (siempre segura)
    basic_mobility = [
        {
            "name": "Rotaciones de cuello",
            "description": "Rotaciones suaves del cuello en ambas direcciones",
            "duration": "30 segundos cada dirección",
            "notes": "Movimientos controlados, sin forzar"
        },
        {
            "name": "Círculos de hombros",
            "description": "Rotaciones de hombros hacia adelante y atrás",
            "duration": "30 segundos cada dirección",
            "notes": "Rango de movimiento completo pero sin dolor" if "shoulder" not in injuries else "Rango limitado, sin molestias"
        },
        {
            "name": "Rotaciones de tronco",
            "description": "Giros de torso de pie, brazos extendidos",
            "duration": "30 segundos",
            "notes": "Movimiento fluido, core activado" if "low_back" not in injuries else "Amplitud reducida, sin forzar lumbar"
        }
    ]
    
    # Movilidad específica según focus
    if training_focus in ["upper", "full_body"]:
        basic_mobility.append({
            "name": "Dislocaciones de hombro con banda/palo",
            "description": "Pasar banda/palo por encima de la cabeza",
            "duration": "10 repeticiones",
            "notes": "Agarre amplio, movimiento controlado" if "shoulder" not in injuries else "OPCIONAL - Solo si no hay molestias"
        })
    
    if training_focus in ["lower", "full_body"]:
        basic_mobility.extend([
            {
                "name": "Círculos de cadera",
                "description": "Rotaciones de cadera en ambas direcciones",
                "duration": "30 segundos cada dirección",
                "notes": "Movimiento fluido, manos en cintura"
            },
            {
                "name": "Balanceos de pierna (frontal/lateral)",
                "description": "Balanceos dinámicos de pierna",
                "duration": "10 repeticiones cada pierna",
                "notes": "Amplitud progresiva" if "knee" not in injuries else "Amplitud reducida inicialmente"
            }
        ])
    
    mobility_component["exercises"] = basic_mobility
    block_a["components"].append(mobility_component)
    
    # === COMPONENTE 2: ACTIVACIÓN ESPECÍFICA ===
    activation_component = {
        "name": "Activación Neuromuscular",
        "duration_min": int(warmup_duration * 0.3),
        "exercises": []
    }
    
    # Buscar ejercicios del catálogo para activación
    activation_exercises = []
    
    if training_focus in ["upper", "full_body"]:
        # Activación de hombro/escapular
        # Buscar ejercicios ligeros de empuje o tracción
        safe_patterns = ["empuje_horizontal", "traccion_horizontal"]
        for pattern in safe_patterns:
            candidates = filter_exercises(
                movement_pattern=pattern,
                difficulty="principiante" if nivel == "principiante" else "intermedio",
                environment=environment,
                usable_for_plans=True
            )
            
            # Filtrar por seguridad si hay lesiones
            if "shoulder" in injuries:
                candidates = [ex for ex in candidates if check_health_safety(ex, 'shoulder') == 'seguro']
            
            if candidates:
                # Tomar el primero que sea bodyweight o banda si es posible
                for ex in candidates:
                    if 'bodyweight' in ex.get('load_type_clean', []) or 'banda' in ex.get('load_type_clean', []):
                        activation_exercises.append({
                            "exercise_code": ex['exercise_code'],
                            "reps": "10-12 reps",
                            "sets": "1-2",
                            "load": "muy_ligera",
                            "notes": "Activación, no fatiga. Enfoque en conexión mente-músculo"
                        })
                        break
                if len(activation_exercises) >= 2:
                    break
    
    if training_focus in ["lower", "full_body"]:
        # Activación de glúteos/core
        # Buscar ejercicios de core antirotación básicos
        core_exercises = filter_exercises(
            movement_pattern="core_antirotacion",
            difficulty="principiante",
            environment=environment,
            usable_for_plans=True
        )
        
        if "low_back" in injuries:
            core_exercises = [ex for ex in core_exercises if check_health_safety(ex, 'low_back') == 'seguro']
        
        if core_exercises:
            activation_exercises.append({
                "exercise_code": core_exercises[0]['exercise_code'],
                "reps": "8-10 reps por lado" if "lado" in core_exercises[0]['exercise_code'] else "10 reps",
                "sets": "1-2",
                "load": "bodyweight",
                "notes": "Activación de core, movimiento controlado"
            })
    
    # Si no encontramos ejercicios del catálogo, usar descripciones generales
    if not activation_exercises:
        if training_focus in ["upper", "full_body"]:
            activation_component["exercises"].append({
                "name": "Flexiones de pared o push-ups",
                "description": "Versión ligera de flexión",
                "reps": "10-12 reps",
                "sets": "1-2",
                "notes": "Activación de pectoral, hombro, tríceps"
            })
        
        if training_focus in ["lower", "full_body"]:
            activation_component["exercises"].append({
                "name": "Peso muerto rumano con barra vacía/ligera",
                "description": "Patrón de bisagra de cadera",
                "reps": "10 reps",
                "sets": "1-2",
                "notes": "Activación de glúteos e isquiotibiales" if "low_back" not in injuries else "Rango reducido, sin molestias lumbares"
            })
    else:
        activation_component["exercises"] = activation_exercises
    
    block_a["components"].append(activation_component)
    
    # === COMPONENTE 3: CARDIO LIGERO ===
    cardio_component = {
        "name": "Preparación Cardiovascular",
        "duration_min": int(warmup_duration * 0.2),
        "exercises": [
            {
                "name": "Cardio ligero (caminadora, bici, remo)",
                "description": "Ejercicio cardiovascular de baja intensidad",
                "duration": f"{int(warmup_duration * 0.2)} minutos",
                "intensity": "50-60% FCMax (conversacional)",
                "notes": "Aumentar temperatura corporal, preparar sistema cardiovascular"
            }
        ]
    }
    
    # Ajustar según lesiones
    if "knee" in injuries:
        cardio_component["exercises"][0]["notes"] += " | PREFERIR bicicleta o remo (menos impacto en rodillas)"
    
    if "low_back" in injuries:
        cardio_component["exercises"][0]["notes"] += " | EVITAR remo si hay molestias lumbares"
    
    block_a["components"].append(cardio_component)
    
    # Notas generales del bloque
    block_a["general_notes"] = [
        f"Calentamiento diseñado para sesión de {session_duration_min} min ({training_focus})",
        "Objetivo: preparar el cuerpo para el Bloque B sin generar fatiga",
        "Intensidad: 40-60% de esfuerzo máximo",
        "Progresión: de general a específico, de bajo a moderado"
    ]
    
    if injuries:
        injury_notes = []
        if "shoulder" in injuries:
            injury_notes.append("Hombro: evitar elevaciones extremas, respetar dolor")
        if "low_back" in injuries:
            injury_notes.append("Lumbar: evitar flexión/extensión extremas, mantener neutro")
        if "knee" in injuries:
            injury_notes.append("Rodilla: evitar impactos, preferir rango parcial si hay molestias")
        
        block_a["general_notes"].extend(injury_notes)
    
    return block_a


def format_warmup_for_display(warmup_block: Dict) -> str:
    """
    Formatea el bloque de calentamiento para visualización
    
    Args:
        warmup_block: Diccionario con estructura del Block A
    
    Returns:
        String formateado para mostrar
    """
    
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"{warmup_block['block_name']}")
    output.append(f"Duración estimada: {warmup_block['duration_min']} minutos")
    output.append(f"{'='*60}\n")
    
    for component in warmup_block['components']:
        output.append(f"\n📍 {component['name']} ({component['duration_min']} min)")
        output.append("-" * 60)
        
        for i, exercise in enumerate(component['exercises'], 1):
            if 'exercise_code' in exercise:
                # Ejercicio del catálogo
                output.append(f"\n{i}. {exercise['exercise_code']}")
                output.append(f"   Sets: {exercise.get('sets', 'N/A')}")
                output.append(f"   Reps: {exercise.get('reps', 'N/A')}")
                output.append(f"   Carga: {exercise.get('load', 'N/A')}")
                if exercise.get('notes'):
                    output.append(f"   📝 {exercise['notes']}")
            else:
                # Descripción general
                output.append(f"\n{i}. {exercise.get('name', 'Ejercicio')}")
                if exercise.get('description'):
                    output.append(f"   {exercise['description']}")
                if exercise.get('duration'):
                    output.append(f"   Duración: {exercise['duration']}")
                if exercise.get('reps'):
                    output.append(f"   Repeticiones: {exercise['reps']}")
                if exercise.get('intensity'):
                    output.append(f"   Intensidad: {exercise['intensity']}")
                if exercise.get('notes'):
                    output.append(f"   📝 {exercise['notes']}")
    
    if warmup_block.get('general_notes'):
        output.append(f"\n\n📋 NOTAS GENERALES:")
        for note in warmup_block['general_notes']:
            output.append(f"   • {note}")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Test del template
    print("🧪 Probando Block A Template...")
    
    # Test 1: Upper body, intermedio, sin lesiones
    print("\n" + "="*60)
    print("TEST 1: Upper Body - Intermedio - Sin lesiones")
    print("="*60)
    warmup1 = generate_warmup_block("upper", "intermedio", [], "gym", 60)
    print(format_warmup_for_display(warmup1))
    
    # Test 2: Lower body, principiante, con lesión lumbar
    print("\n" + "="*60)
    print("TEST 2: Lower Body - Principiante - Lesión lumbar")
    print("="*60)
    warmup2 = generate_warmup_block("lower", "principiante", ["low_back"], "gym", 45)
    print(format_warmup_for_display(warmup2))
    
    # Test 3: Full body, avanzado, con hombro inestable
    print("\n" + "="*60)
    print("TEST 3: Full Body - Avanzado - Hombro inestable")
    print("="*60)
    warmup3 = generate_warmup_block("full_body", "avanzado", ["shoulder"], "home", 60)
    print(format_warmup_for_display(warmup3))
    
    print("\n✅ Tests completados")
