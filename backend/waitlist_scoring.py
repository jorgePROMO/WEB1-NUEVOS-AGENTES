"""
Waitlist Lead Scoring System
Calcula scores y tags automáticos basados en las respuestas del formulario
"""

def calculate_waitlist_score(responses: dict) -> dict:
    """
    Calcula el score total y todos los sub-scores
    Retorna un diccionario con todos los scores y tags
    """
    
    scores = {
        "score_capacidad_economica": 0,
        "score_objetivos_motivacion": 0,
        "score_experiencia_habitos": 0,
        "score_disponibilidad_compromiso": 0,
        "score_personalidad_afinidad": 0,
        "score_disponibilidad_entrevista": 0,
    }
    
    tags = {}
    
    # ==================== 1. CAPACIDAD ECONÓMICA (25 pts) ====================
    
    # 1.1. Inversión mensual (10 pts)
    inversion = responses.get("inversion_mensual", "")
    if "< 50" in inversion:
        scores["score_capacidad_economica"] += 0
        tags["capacidad_economica"] = "baja"
    elif "100-200" in inversion:
        scores["score_capacidad_economica"] += 4
        tags["capacidad_economica"] = "media"
    elif "200-500" in inversion:
        scores["score_capacidad_economica"] += 7
        tags["capacidad_economica"] = "media"
    elif "500" in inversion:
        scores["score_capacidad_economica"] += 10
        tags["capacidad_economica"] = "alta"
    
    # 1.2. Invierte actualmente (8 pts)
    invierte = responses.get("invierte_actualmente", "")
    if "No invierto" in invierte:
        scores["score_capacidad_economica"] += 0
    elif "Gimnasio o suplementos" in invierte:
        scores["score_capacidad_economica"] += 3
    elif "Comidas, entrenadores" in invierte or "hábitos" in invierte:
        scores["score_capacidad_economica"] += 5
    elif "activamente" in invierte:
        scores["score_capacidad_economica"] += 8
    
    # 1.3. Frase que representa (7 pts)
    frase = responses.get("frase_representa", "")
    if "económico" in frase.lower():
        scores["score_capacidad_economica"] += 2
    elif "resultados reales" in frase.lower():
        scores["score_capacidad_economica"] += 5
    elif "dispuesto a invertir" in frase.lower():
        scores["score_capacidad_economica"] += 7
    
    # ==================== 2. OBJETIVOS Y MOTIVACIÓN (25 pts) ====================
    
    # 2.1. Objetivo principal (7 pts)
    objetivo = responses.get("objetivo_principal", "")
    if "Perder grasa" in objetivo:
        scores["score_objetivos_motivacion"] += 6
        tags["objetivo"] = "definicion"
    elif "Ganar músculo" in objetivo or "Ganar mÃºsculo" in objetivo:
        scores["score_objetivos_motivacion"] += 6
        tags["objetivo"] = "volumen"
    elif "Cambiar hábitos" in objetivo or "hÃ¡bitos" in objetivo:
        scores["score_objetivos_motivacion"] += 4
        tags["objetivo"] = "habitos"
    elif "Prepararme" in objetivo or "competición" in objetivo or "competiciÃ³n" in objetivo:
        scores["score_objetivos_motivacion"] += 7
        tags["objetivo"] = "preparacion"
    elif "No lo tengo claro" in objetivo:
        scores["score_objetivos_motivacion"] += 2
        tags["objetivo"] = "indefinido"
    
    # 2.2. Por qué ahora (7 pts)
    por_que = responses.get("por_que_ahora", "")
    if "razón clara" in por_que.lower() or "razÃ³n clara" in por_que.lower() or "fecha" in por_que.lower():
        scores["score_objetivos_motivacion"] += 7
        tags["urgencia"] = "alta"
    elif "cansado" in por_que.lower():
        scores["score_objetivos_motivacion"] += 5
        tags["urgencia"] = "media"
    elif "salud" in por_que.lower():
        scores["score_objetivos_motivacion"] += 4
        tags["urgencia"] = "media"
    elif "No tengo" in por_que:
        scores["score_objetivos_motivacion"] += 2
        tags["urgencia"] = "baja"
    
    # 2.3. Intentado antes (7 pts)
    intentado = responses.get("intentado_antes", "")
    if "No he hecho nada" in intentado:
        scores["score_objetivos_motivacion"] += 2
    elif "Dietas o rutinas por mi cuenta" in intentado:
        scores["score_objetivos_motivacion"] += 4
    elif "He tenido entrenador" in intentado:
        scores["score_objetivos_motivacion"] += 5
    elif "He invertido antes" in intentado or "más profesional" in intentado or "mÃ¡s profesional" in intentado:
        scores["score_objetivos_motivacion"] += 7
    
    # 2.4. Cómo verte en 3 meses (evaluación manual, asumimos 4 pts por defecto)
    como_verte = responses.get("como_verte_3_meses", "")
    if len(como_verte) < 30:
        scores["score_objetivos_motivacion"] += 2
        tags["motivacion"] = "baja"
    elif len(como_verte) < 100:
        scores["score_objetivos_motivacion"] += 4
        tags["motivacion"] = "media"
    else:
        scores["score_objetivos_motivacion"] += 6
        tags["motivacion"] = "alta"
    
    # ==================== 3. EXPERIENCIA Y HÁBITOS (15 pts) ====================
    
    # 3.1. Entrenas actualmente (8 pts)
    entrenas = responses.get("entrenas_actualmente", "")
    if "con entrenador" in entrenas.lower():
        scores["score_experiencia_habitos"] += 7
    elif "por mi cuenta" in entrenas.lower():
        scores["score_experiencia_habitos"] += 5
    elif "quiero retomarlo" in entrenas.lower():
        scores["score_experiencia_habitos"] += 3
    elif "No entreno" in entrenas:
        scores["score_experiencia_habitos"] += 2
    
    # 3.2. Días a la semana (7 pts - ajustado para llegar a 15)
    dias = responses.get("dias_semana_entrenar", "")
    if "1-2" in dias:
        scores["score_experiencia_habitos"] += 2
    elif "3-4" in dias:
        scores["score_experiencia_habitos"] += 5
    elif "5" in dias or "más" in dias or "mÃ¡s" in dias:
        scores["score_experiencia_habitos"] += 7
    
    # 3.3. Nivel de experiencia (no suma, solo tag)
    nivel_exp = responses.get("nivel_experiencia", "")
    if "Principiante" in nivel_exp:
        tags["nivel_experiencia"] = "bajo"
    elif "Intermedio" in nivel_exp:
        tags["nivel_experiencia"] = "medio"
    elif "Avanzado" in nivel_exp:
        tags["nivel_experiencia"] = "alto"
    
    # ==================== 4. DISPONIBILIDAD Y COMPROMISO (20 pts) ====================
    
    # 4.1. Tiempo semanal (7 pts)
    tiempo = responses.get("tiempo_semanal", "")
    if "< 2" in tiempo or "Menos de 2" in tiempo:
        scores["score_disponibilidad_compromiso"] += 2
    elif "3-4" in tiempo:
        scores["score_disponibilidad_compromiso"] += 4
    elif "5-6" in tiempo:
        scores["score_disponibilidad_compromiso"] += 5
    elif "6" in tiempo or "más" in tiempo or "Más" in tiempo or "MÃ¡s" in tiempo:
        scores["score_disponibilidad_compromiso"] += 7
    
    # 4.2. Nivel de compromiso (8 pts)
    compromiso = responses.get("nivel_compromiso", "")
    if "1-4" in compromiso:
        scores["score_disponibilidad_compromiso"] += 2
        tags["nivel_compromiso"] = "bajo"
    elif "5-6" in compromiso:
        scores["score_disponibilidad_compromiso"] += 4
        tags["nivel_compromiso"] = "medio"
    elif "7-8" in compromiso:
        scores["score_disponibilidad_compromiso"] += 6
        tags["nivel_compromiso"] = "alto"
    elif "9-10" in compromiso:
        scores["score_disponibilidad_compromiso"] += 8
        tags["nivel_compromiso"] = "alto"
    
    # 4.3. Qué pasaría sin cambiar (5 pts)
    sin_cambiar = responses.get("que_pasaria_sin_cambiar", "")
    if "No pasaría" in sin_cambiar or "No pasarÃ­a" in sin_cambiar:
        scores["score_disponibilidad_compromiso"] += 0
    elif "frustraría" in sin_cambiar.lower() or "frustrarÃ­a" in sin_cambiar.lower():
        scores["score_disponibilidad_compromiso"] += 3
    elif "empeoraría" in sin_cambiar.lower() or "empeorarÃ­a" in sin_cambiar.lower():
        scores["score_disponibilidad_compromiso"] += 4
    elif "no quiero" in sin_cambiar.lower() or "imaginarlo" in sin_cambiar.lower():
        scores["score_disponibilidad_compromiso"] += 5
    
    # ==================== 5. PERSONALIDAD Y AFINIDAD (10 pts) ====================
    
    # 5.1. Preferencia comunicación (4 pts)
    comunicacion = responses.get("preferencia_comunicacion", "")
    if "Directa y exigente" in comunicacion:
        scores["score_personalidad_afinidad"] += 4
        tags["afinidad_estilo"] = "alta"
    elif "intermedio" in comunicacion.lower():
        scores["score_personalidad_afinidad"] += 2
        tags["afinidad_estilo"] = "media"
    elif "flexible" in comunicacion.lower() or "progresiva" in comunicacion.lower():
        scores["score_personalidad_afinidad"] += 1
        tags["afinidad_estilo"] = "baja"
    
    # 5.2. Qué motiva más (3 pts)
    motiva = responses.get("que_motiva_mas", "")
    if "Resultados visibles" in motiva:
        scores["score_personalidad_afinidad"] += 3
    elif "Sentirme mejor" in motiva:
        scores["score_personalidad_afinidad"] += 2
    elif "No lo tengo claro" in motiva:
        scores["score_personalidad_afinidad"] += 1
    
    # 5.3. Esperas del coach (3 pts)
    esperas = responses.get("esperas_del_coach", "")
    if "exijas" in esperas.lower() or "límite" in esperas.lower() or "lÃ­mite" in esperas.lower():
        scores["score_personalidad_afinidad"] += 3
    elif "acompañes" in esperas.lower() or "acompaÃ±es" in esperas.lower() or "estructura" in esperas.lower():
        scores["score_personalidad_afinidad"] += 2
    elif "apoyes" in esperas.lower():
        scores["score_personalidad_afinidad"] += 1
    
    # ==================== 6. DISPONIBILIDAD ENTREVISTA (5 pts) ====================
    
    disponibilidad = responses.get("disponibilidad_llamada", "")
    if "Sí" in disponibilidad or "SÃ­" in disponibilidad or "adaptarme" in disponibilidad:
        scores["score_disponibilidad_entrevista"] += 5
    elif "WhatsApp" in disponibilidad:
        scores["score_disponibilidad_entrevista"] += 3
    elif "No lo sé" in disponibilidad or "No lo sÃ©" in disponibilidad:
        scores["score_disponibilidad_entrevista"] += 1
    
    # ==================== CALCULAR SCORE TOTAL Y PRIORIDAD ====================
    
    score_total = sum(scores.values())
    
    # Determinar prioridad
    if score_total >= 66:
        prioridad = "alta"
    elif score_total >= 41:
        prioridad = "media"
    else:
        prioridad = "baja"
    
    # Asegurar que todos los tags existen (valores por defecto)
    tags.setdefault("capacidad_economica", "media")
    tags.setdefault("objetivo", "indefinido")
    tags.setdefault("motivacion", "media")
    tags.setdefault("nivel_experiencia", "medio")
    tags.setdefault("nivel_compromiso", "medio")
    tags.setdefault("urgencia", "media")
    tags.setdefault("afinidad_estilo", "media")
    
    return {
        **scores,
        "score_total": score_total,
        "prioridad": prioridad,
        **tags
    }
