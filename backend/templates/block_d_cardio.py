"""
Block D - Cardio/Conditioning Template
=======================================
Template paramétrico para generar bloque de trabajo cardiovascular

Adapta según:
- Objetivo principal (pérdida grasa, hipertrofia, fuerza)
- Nivel de experiencia
- Volumen del Bloque B
- Lesiones (rodilla especialmente)
- Disponibilidad de tiempo

Tipos de cardio:
- LISS: Low Intensity Steady State (recuperación activa)
- MISS: Medium Intensity Steady State (salud cardiovascular)
- HIIT: High Intensity Interval Training (pérdida grasa, condicionamiento)

Autor: E1 Agent
Fecha: Diciembre 2025
"""

from typing import Dict, List, Optional


def generate_cardio_block(
    objetivo: str = "hipertrofia",  # perdida_grasa, hipertrofia, fuerza, mantenimiento
    nivel: str = "intermedio",
    volumen_bloque_b: str = "medio",  # bajo, medio, alto
    injuries: Optional[List[str]] = None,
    session_duration_min: int = 60,
    dias_por_semana: int = 4
) -> Dict:
    """
    Genera Block D (Cardio/Conditioning) adaptado al contexto
    
    Filosofía K1:
    - Si objetivo es FUERZA o HIPERTROFIA → cardio mínimo o LISS (no interferir)
    - Si objetivo es PÉRDIDA GRASA → cardio más presente (MISS o HIIT)
    - Si Bloque B fue alto volumen → cardio ligero o LISS
    - Siempre respetar lesiones (especialmente rodilla)
    
    Args:
        objetivo: perdida_grasa, hipertrofia, fuerza, mantenimiento
        nivel: principiante, intermedio, avanzado
        volumen_bloque_b: bajo, medio, alto
        injuries: Lista de lesiones
        session_duration_min: Duración total de sesión
        dias_por_semana: Frecuencia semanal de entrenamiento
    
    Returns:
        Dict con estructura del Block D
    """
    
    injuries = injuries or []
    has_knee_injury = "knee" in injuries
    has_back_injury = "low_back" in injuries
    
    block_d = {
        "id": "D",
        "block_name": "Bloque D - Cardio/Acondicionamiento",
        "focus": ["cardiovascular", "recuperacion_activa"],
        "recommendations": []
    }
    
    # === LÓGICA DE PRESCRIPCIÓN SEGÚN OBJETIVO ===
    
    if objetivo == "fuerza":
        # FUERZA: Cardio mínimo, solo para salud
        cardio_type = "LISS"
        cardio_frequency = "2-3x/semana (días de descanso o post-entrenamiento)"
        cardio_duration = "15-20 minutos"
        cardio_intensity = "50-60% FCMax"
        
        block_d["recommendations"].append({
            "type": "LISS (Low Intensity Steady State)",
            "frequency": cardio_frequency,
            "duration": cardio_duration,
            "intensity": cardio_intensity,
            "modalities": [
                "Caminata inclinada en caminadora",
                "Bicicleta estática (ritmo cómodo)",
                "Elíptica (bajo impacto)" if not has_knee_injury else "Bicicleta reclinada (cero impacto)",
                "Remo a baja intensidad" if not has_back_injury else None
            ],
            "notes": "Objetivo: salud cardiovascular SIN interferir con recuperación de fuerza",
            "timing": "Preferiblemente en días OFF o al final de sesión (mínimo 4h después del B si es posible)"
        })
    
    elif objetivo == "hipertrofia":
        # HIPERTROFIA: Cardio moderado, no excesivo
        if volumen_bloque_b == "alto":
            # B fue demandante, cardio muy ligero
            cardio_type = "LISS"
            cardio_duration = "15-20 minutos"
            cardio_intensity = "55-65% FCMax"
            cardio_frequency = "2-3x/semana"
        else:
            # B moderado, puede hacer MISS
            cardio_type = "MISS"
            cardio_duration = "20-25 minutos"
            cardio_intensity = "65-75% FCMax"
            cardio_frequency = "3x/semana"
        
        block_d["recommendations"].append({
            "type": f"{cardio_type} (Recuperación activa + salud)",
            "frequency": cardio_frequency,
            "duration": cardio_duration,
            "intensity": cardio_intensity,
            "modalities": [
                "Bicicleta estática (ritmo moderado)",
                "Caminata inclinada (6-8% inclinación)" if not has_knee_injury else "Bicicleta sin resistencia alta",
                "Elíptica" if not has_knee_injury else None,
                "Natación (excelente opción)" if not has_knee_injury and not has_back_injury else None
            ],
            "notes": f"Objetivo: mantener salud cardiovascular sin comprometer hipertrofia. Volumen B fue {volumen_bloque_b}, cardio ajustado.",
            "timing": "Al final de sesión o días OFF. Si es post-entrenamiento, mantener intensidad baja."
        })
    
    elif objetivo == "perdida_grasa":
        # PÉRDIDA GRASA: Cardio más agresivo, pero inteligente
        
        if nivel == "principiante":
            # Principiante: MISS mayormente, introducir HIIT gradualmente
            block_d["recommendations"].append({
                "type": "MISS (Medium Intensity Steady State)",
                "frequency": "4-5x/semana",
                "duration": "25-30 minutos",
                "intensity": "65-75% FCMax (puedes hablar, pero con esfuerzo)",
                "modalities": [
                    "Caminata rápida inclinada",
                    "Bicicleta estática (ritmo constante)",
                    "Elíptica" if not has_knee_injury else "Bicicleta reclinada",
                    "Remo (ritmo moderado)" if not has_back_injury else None
                ],
                "notes": "Principal herramienta para déficit calórico. Intensidad sostenible.",
                "timing": "Post-entrenamiento o días OFF. Priorizar consistencia sobre intensidad."
            })
            
            # Opcional: 1 sesión HIIT por semana
            if dias_por_semana >= 4:
                block_d["recommendations"].append({
                    "type": "HIIT (Opcional, 1x/semana)",
                    "frequency": "1x/semana",
                    "duration": "15-20 minutos total",
                    "protocol": "20 seg trabajo : 40 seg descanso x 10-12 rondas",
                    "intensity": "85-90% FCMax en intervalos",
                    "modalities": [
                        "Bicicleta (sprints)",
                        "Remo (intervalos cortos)" if not has_back_injury else None,
                        "Assault bike" if not has_knee_injury else None
                    ],
                    "notes": "OPCIONAL para principiantes. Solo si toleran bien el MISS.",
                    "timing": "Día separado del entrenamiento pesado de piernas"
                })
        
        else:  # intermedio o avanzado
            # Combinar MISS + HIIT
            block_d["recommendations"].append({
                "type": "MISS (Steady State)",
                "frequency": "3-4x/semana",
                "duration": "25-30 minutos",
                "intensity": "65-75% FCMax",
                "modalities": [
                    "Caminata inclinada",
                    "Bicicleta",
                    "Elíptica" if not has_knee_injury else "Bicicleta",
                    "Natación"
                ],
                "notes": "Base del trabajo cardiovascular. Quema calorías sin fatiga excesiva.",
                "timing": "Post-entrenamiento o días OFF"
            })
            
            block_d["recommendations"].append({
                "type": "HIIT (High Intensity Intervals)",
                "frequency": "2x/semana",
                "duration": "15-20 minutos total",
                "protocol": nivel == "intermedio" and "30 seg trabajo : 30 seg descanso x 10 rondas" or "30 seg trabajo : 20 seg descanso x 12 rondas",
                "intensity": "85-95% FCMax en intervalos",
                "modalities": [
                    "Sprints en bicicleta",
                    "Remo (intervalos)" if not has_back_injury else None,
                    "Assault bike" if not has_knee_injury else None,
                    "Battle ropes (alternativa sin impacto)"
                ],
                "notes": f"HIIT para maximizar gasto calórico post-ejercicio (EPOC). Nivel {nivel} puede manejarlo.",
                "timing": "Días separados de piernas pesadas. Mínimo 48h entre HIITs."
            })
    
    else:  # mantenimiento_salud
        cardio_type = "MISS"
        cardio_duration = "20-30 minutos"
        cardio_intensity = "60-70% FCMax"
        cardio_frequency = "3-4x/semana"
        
        block_d["recommendations"].append({
            "type": "MISS (Salud cardiovascular general)",
            "frequency": cardio_frequency,
            "duration": cardio_duration,
            "intensity": cardio_intensity,
            "modalities": [
                "Caminata (ritmo cómodo-moderado)",
                "Bicicleta",
                "Natación",
                "Clases grupales (Zumba, spinning, etc.)"
            ],
            "notes": "Objetivo: salud general y bienestar. Intensidad agradable y sostenible.",
            "timing": "Flexible: antes, después o días separados"
        })
    
    # === AJUSTES POR LESIONES ===
    injury_adjustments = []
    
    if has_knee_injury:
        injury_adjustments.append({
            "injury": "Rodilla",
            "avoid": ["Correr", "Sprints", "Saltos", "Elíptica con resistencia alta"],
            "prefer": ["Bicicleta estática (preferir reclinada)", "Remo (si tolera)", "Natación", "Caminata en plano"],
            "notes": "Priorizar ejercicios sin impacto. Ajustar resistencia según tolerancia."
        })
    
    if has_back_injury:
        injury_adjustments.append({
            "injury": "Lumbar",
            "avoid": ["Remo (puede agravar)", "Correr (impacto)", "Bicicleta con torso muy flexionado"],
            "prefer": ["Bicicleta reclinada", "Caminata", "Elíptica (torso erguido)", "Natación (crol o espalda)"],
            "notes": "Mantener columna neutra. Evitar flexión sostenida."
        })
    
    if injury_adjustments:
        block_d["injury_adaptations"] = injury_adjustments
    
    # === NOTAS GENERALES ===
    block_d["general_notes"] = [
        f"Cardio diseñado para objetivo: {objetivo}",
        f"Volumen del Bloque B: {volumen_bloque_b} → Cardio ajustado para no interferir",
        "Progresión: aumentar duración antes que intensidad",
        "Monitorear: si recuperación del B se ve afectada, reducir cardio"
    ]
    
    if objetivo in ["fuerza", "hipertrofia"]:
        block_d["general_notes"].append("⚠️ NO exceder recomendaciones: cardio excesivo puede interferir con ganancias")
    
    if objetivo == "perdida_grasa":
        block_d["general_notes"].append("💡 Cardio es herramienta, no solución única. Priorizar déficit calórico (dieta) + preservar músculo (B)")
    
    # Timing general
    block_d["optimal_timing"] = {
        "post_strength": "Después del Bloque B (si tiempo y energía permiten)",
        "separate_session": "Días OFF o sesión separada (AM/PM split)",
        "fasted": "Opcional: cardio en ayunas (LISS únicamente, no HIIT)",
        "note": "La consistencia es más importante que el timing perfecto"
    }
    
    return block_d


def format_cardio_for_display(cardio_block: Dict) -> str:
    """
    Formatea el bloque de cardio para visualización
    
    Args:
        cardio_block: Diccionario con estructura del Block D
    
    Returns:
        String formateado para mostrar
    """
    
    output = []
    output.append(f"\n{'='*60}")
    output.append(f"{cardio_block['block_name']}")
    output.append(f"Focus: {', '.join(cardio_block['focus'])}")
    output.append(f"{'='*60}\n")
    
    for i, rec in enumerate(cardio_block['recommendations'], 1):
        output.append(f"\n{'─'*60}")
        output.append(f"📍 RECOMENDACIÓN {i}: {rec['type']}")
        output.append(f"{'─'*60}")
        output.append(f"   Frecuencia: {rec['frequency']}")
        output.append(f"   Duración: {rec['duration']}")
        
        if 'intensity' in rec:
            output.append(f"   Intensidad: {rec['intensity']}")
        
        if 'protocol' in rec:
            output.append(f"   Protocolo: {rec['protocol']}")
        
        output.append(f"\n   Modalidades sugeridas:")
        for mod in rec['modalities']:
            if mod:  # Filtrar None
                output.append(f"      • {mod}")
        
        if rec.get('notes'):
            output.append(f"\n   📝 {rec['notes']}")
        
        if rec.get('timing'):
            output.append(f"   ⏰ Timing: {rec['timing']}")
    
    # Adaptaciones por lesiones
    if cardio_block.get('injury_adaptations'):
        output.append(f"\n\n{'='*60}")
        output.append("⚠️ ADAPTACIONES POR LESIONES")
        output.append(f"{'='*60}")
        
        for adaptation in cardio_block['injury_adaptations']:
            output.append(f"\n🩹 {adaptation['injury']}:")
            output.append(f"   ❌ Evitar: {', '.join(adaptation['avoid'])}")
            output.append(f"   ✅ Preferir: {', '.join(adaptation['prefer'])}")
            if adaptation.get('notes'):
                output.append(f"   📝 {adaptation['notes']}")
    
    # Timing óptimo
    if cardio_block.get('optimal_timing'):
        timing = cardio_block['optimal_timing']
        output.append(f"\n\n{'='*60}")
        output.append("⏰ TIMING ÓPTIMO")
        output.append(f"{'='*60}")
        output.append(f"   Post-entrenamiento: {timing['post_strength']}")
        output.append(f"   Sesión separada: {timing['separate_session']}")
        output.append(f"   En ayunas: {timing['fasted']}")
        output.append(f"   💡 {timing['note']}")
    
    # Notas generales
    if cardio_block.get('general_notes'):
        output.append(f"\n\n📋 NOTAS GENERALES:")
        for note in cardio_block['general_notes']:
            output.append(f"   • {note}")
    
    return "\n".join(output)


if __name__ == "__main__":
    # Test del template
    print("🧪 Probando Block D Template...")
    
    # Test 1: Pérdida grasa, intermedio, volumen medio
    print("\n" + "="*60)
    print("TEST 1: Pérdida Grasa - Intermedio - Volumen medio")
    print("="*60)
    cardio1 = generate_cardio_block("perdida_grasa", "intermedio", "medio", [], 60, 4)
    print(format_cardio_for_display(cardio1))
    
    # Test 2: Hipertrofia, avanzado, volumen alto
    print("\n" + "="*60)
    print("TEST 2: Hipertrofia - Avanzado - Volumen alto")
    print("="*60)
    cardio2 = generate_cardio_block("hipertrofia", "avanzado", "alto", [], 60, 4)
    print(format_cardio_for_display(cardio2))
    
    # Test 3: Fuerza, intermedio, volumen medio
    print("\n" + "="*60)
    print("TEST 3: Fuerza - Intermedio")
    print("="*60)
    cardio3 = generate_cardio_block("fuerza", "intermedio", "medio", [], 60, 3)
    print(format_cardio_for_display(cardio3))
    
    # Test 4: Pérdida grasa, principiante, CON LESIÓN RODILLA
    print("\n" + "="*60)
    print("TEST 4: Pérdida Grasa - Principiante - LESIÓN RODILLA")
    print("="*60)
    cardio4 = generate_cardio_block("perdida_grasa", "principiante", "medio", ["knee"], 45, 4)
    print(format_cardio_for_display(cardio4))
    
    print("\n✅ Tests completados")
