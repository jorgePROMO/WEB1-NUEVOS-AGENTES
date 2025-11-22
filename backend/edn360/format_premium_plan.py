"""
Post-procesador determinista para generar el formatted_plan premium en Markdown.

Este módulo NO depende del LLM. Toma los datos estructurados de safe_sessions,
mesocycle y client_summary, y genera un plan en Markdown profesional y operativo.

Ubicación: /app/backend/edn360/format_premium_plan.py
"""

from typing import Dict, Any, List


def generate_premium_markdown(
    safe_sessions: Dict[str, List[Dict]],
    mesocycle: Dict[str, Any],
    client_summary: Dict[str, Any]
) -> str:
    """
    Genera el formatted_plan premium en Markdown a partir de datos estructurados.
    
    Args:
        safe_sessions: Dict con semana_1, semana_2, etc. Cada semana tiene lista de sesiones
        mesocycle: Dict con información del bloque (duración, objetivo, estrategia, etc.)
        client_summary: Dict con resumen del cliente (nombre, objetivo, nivel, etc.)
    
    Returns:
        String con el plan completo en Markdown
    """
    
    markdown_lines = []
    
    # ========== 1. CABECERA DEL PLAN ==========
    markdown_lines.append("# PLAN DE ENTRENAMIENTO PERSONALIZADO – EDN360")
    markdown_lines.append("")
    
    # Datos del cliente
    nombre = client_summary.get("id_cliente", "Cliente")
    if nombre == "unknown":
        nombre = "Cliente"
    
    objetivo = client_summary.get("objetivo_principal", "mejora_general")
    objetivo_texto = {
        "recomposicion": "Recomposición corporal",
        "ganancia_muscular": "Ganancia muscular",
        "perdida_grasa": "Pérdida de grasa",
        "fuerza": "Ganancia de fuerza",
        "mejora_general": "Mejora general"
    }.get(objetivo, objetivo.replace("_", " ").title())
    
    nivel = client_summary.get("nivel", "intermedio").title()
    
    markdown_lines.append(f"**Cliente:** {nombre}")
    markdown_lines.append(f"**Objetivo principal:** {objetivo_texto}")
    
    # Datos del mesocycle
    duracion = mesocycle.get("duracion_semanas", 4)
    frecuencia = mesocycle.get("frecuencia_semanal", 3)
    split = mesocycle.get("split", "full-body").replace("-", " ").replace("_", " ").title()
    
    markdown_lines.append(f"**Duración:** {duracion} semanas")
    markdown_lines.append(f"**Frecuencia:** {frecuencia} días/semana")
    markdown_lines.append(f"**Tipo de bloque:** {split}")
    markdown_lines.append(f"**Nivel:** {nivel}")
    markdown_lines.append("")
    markdown_lines.append("---")
    markdown_lines.append("")
    
    # ========== 2. RESUMEN ESTRATÉGICO DEL BLOQUE ==========
    markdown_lines.append("## 📋 Resumen del Bloque")
    markdown_lines.append("")
    
    # Generar resumen basado en datos reales
    estrategia = mesocycle.get("estrategia", "estandar")
    objetivo_meso = mesocycle.get("objetivo", objetivo)
    
    # Construir resumen dinámicamente
    resumen_partes = []
    
    # Frase 1: Objetivo
    if objetivo_meso == "recomposicion":
        resumen_partes.append(f"Este bloque de {duracion} semanas está diseñado para mejorar tu composición corporal, ganando músculo y reduciendo grasa de forma simultánea.")
    elif objetivo_meso == "ganancia_muscular":
        resumen_partes.append(f"Este bloque de {duracion} semanas se centra en maximizar la ganancia de masa muscular mediante un estímulo progresivo y controlado.")
    elif objetivo_meso == "perdida_grasa":
        resumen_partes.append(f"Este bloque de {duracion} semanas está optimizado para la pérdida de grasa, manteniendo la masa muscular y el rendimiento.")
    else:
        resumen_partes.append(f"Este bloque de {duracion} semanas está diseñado para mejorar tu condición física general de forma progresiva y sostenible.")
    
    # Frase 2: Estructura temporal
    if duracion >= 4:
        resumen_partes.append(f"Las primeras semanas se centran en la adaptación y consolidación del volumen, seguidas de una fase de intensificación, y finalizando con una semana de descarga para optimizar la recuperación.")
    else:
        resumen_partes.append(f"El plan progresa de forma gradual, controlando la fatiga y optimizando la recuperación entre sesiones.")
    
    # Frase 3: Frecuencia y split
    if split.lower() == "full body":
        resumen_partes.append(f"Con {frecuencia} sesiones semanales de cuerpo completo, cada músculo recibirá estímulo frecuente para maximizar la adaptación.")
    elif "upper" in split.lower() or "lower" in split.lower():
        resumen_partes.append(f"El split de tren superior/inferior con {frecuencia} sesiones por semana permite un volumen óptimo por grupo muscular con buena recuperación.")
    else:
        resumen_partes.append(f"Con {frecuencia} sesiones semanales, el plan equilibra volumen, intensidad y recuperación para maximizar resultados.")
    
    markdown_lines.append(" ".join(resumen_partes))
    markdown_lines.append("")
    markdown_lines.append("---")
    markdown_lines.append("")
    
    # ========== 3. TABLA RESUMEN DE SEMANAS ==========
    markdown_lines.append("## 📊 Vista General del Programa")
    markdown_lines.append("")
    
    # Analizar RIR por semana desde safe_sessions
    semanas_info = []
    for semana_key in sorted(safe_sessions.keys()):
        sesiones = safe_sessions[semana_key]
        if not sesiones:
            continue
        
        # Extraer RIR promedio de la primera sesión
        primera_sesion = sesiones[0]
        ejercicios = primera_sesion.get("ejercicios", [])
        
        if ejercicios:
            rir_values = []
            for ej in ejercicios:
                rir = ej.get("rir", "")
                if rir and rir != "-":
                    try:
                        rir_values.append(int(str(rir)))
                    except:
                        pass
            
            rir_promedio = sum(rir_values) // len(rir_values) if rir_values else 4
        else:
            rir_promedio = 4
        
        semana_num = int(semana_key.split("_")[1])
        
        # Determinar enfoque basado en la semana
        if semana_num == 1:
            enfoque = "Adaptación técnica"
            objetivo_semana = "Aprender ejercicios y ritmo"
        elif semana_num == 2:
            enfoque = "Consolidación"
            objetivo_semana = "Mejorar técnica con más carga"
        elif semana_num == duracion and duracion >= 4:
            enfoque = "Descarga"
            objetivo_semana = "Reducir fatiga y consolidar"
        elif semana_num == duracion - 1 and duracion >= 4:
            enfoque = "Intensificación"
            objetivo_semana = "Aumentar esfuerzo controlado"
        else:
            enfoque = "Acumulación"
            objetivo_semana = "Consolidar volumen"
        
        semanas_info.append({
            "numero": semana_num,
            "enfoque": enfoque,
            "dias": len(sesiones),
            "rir": rir_promedio,
            "objetivo": objetivo_semana
        })
    
    # Generar tabla
    markdown_lines.append("| Semana | Enfoque | Días de entreno | RIR aproximado | Objetivo principal |")
    markdown_lines.append("|--------|---------|-----------------|----------------|--------------------|")
    
    for info in semanas_info:
        markdown_lines.append(f"| {info['numero']} | {info['enfoque']} | {info['dias']} | RIR {info['rir']} | {info['objetivo']} |")
    
    markdown_lines.append("")
    markdown_lines.append("---")
    markdown_lines.append("")
    
    # ========== 4. DETALLE SEMANA POR SEMANA ==========
    for semana_key in sorted(safe_sessions.keys()):
        sesiones = safe_sessions[semana_key]
        if not sesiones:
            continue
        
        semana_num = int(semana_key.split("_")[1])
        
        # Obtener enfoque de la tabla anterior
        enfoque_semana = next((s["enfoque"] for s in semanas_info if s["numero"] == semana_num), "")
        
        markdown_lines.append(f"## 🗓️ Semana {semana_num} – {enfoque_semana}")
        markdown_lines.append("")
        
        # Para cada sesión de la semana
        for sesion in sesiones:
            nombre_sesion = sesion.get("nombre", "Entrenamiento")
            dia_semana = sesion.get("dia_semana", "")
            duracion = sesion.get("duracion_min", 60)
            hora = sesion.get("hora_recomendada", "")
            ejercicios = sesion.get("ejercicios", [])
            
            markdown_lines.append(f"### {dia_semana} – {nombre_sesion}")
            
            info_linea = f"**Duración estimada:** {duracion} minutos"
            if hora:
                info_linea += f" | **Hora recomendada:** {hora}"
            markdown_lines.append(info_linea)
            markdown_lines.append("")
            
            # Tabla de ejercicios
            if ejercicios:
                markdown_lines.append("| Ejercicio | Series x Reps | RIR | Descanso | Notas |")
                markdown_lines.append("|-----------|----------------|-----|---------|-------|")
                
                for ej in ejercicios:
                    nombre_ej = ej.get("nombre", "Ejercicio")
                    series = ej.get("series", 3)
                    reps = ej.get("reps", "8-10")
                    rir = ej.get("rir", "4")
                    descanso_seg = ej.get("descanso", 90)
                    
                    # Formatear descanso
                    if descanso_seg >= 60:
                        descanso_str = f"{descanso_seg // 60}:{descanso_seg % 60:02d} min"
                    else:
                        descanso_str = f"{descanso_seg}s"
                    
                    # Series x Reps
                    series_reps = f"{series}x{reps}"
                    
                    # RIR
                    rir_str = str(rir) if rir != "-" else "-"
                    
                    # Notas (vacío por ahora, se puede añadir en el futuro)
                    notas = "-"
                    
                    markdown_lines.append(f"| {nombre_ej} | {series_reps} | {rir_str} | {descanso_str} | {notas} |")
                
                markdown_lines.append("")
            
        markdown_lines.append("---")
        markdown_lines.append("")
    
    # ========== 5. PROGRESIÓN DEL BLOQUE ==========
    markdown_lines.append("## 📈 Progresión del Bloque")
    markdown_lines.append("")
    
    # Analizar progresión real desde las semanas
    if len(semanas_info) >= 4:
        rir_s1 = semanas_info[0]["rir"]
        rir_s2 = semanas_info[1]["rir"]
        rir_s3 = semanas_info[2]["rir"] if len(semanas_info) > 2 else rir_s2
        rir_s4 = semanas_info[3]["rir"] if len(semanas_info) > 3 else rir_s3
        
        markdown_lines.append(f"- **Semanas 1-2 (Adaptación/Consolidación):** Mantén un RIR {rir_s1}-{rir_s2}. La prioridad es controlar la técnica y establecer el ritmo de entrenamiento. No busques el fallo, deja repeticiones en reserva.")
        markdown_lines.append("")
        markdown_lines.append(f"- **Semana 3 (Intensificación):** Aumenta ligeramente la carga (RIR {rir_s3}) si te has sentido bien las semanas anteriores. Este es el pico de intensidad del bloque.")
        markdown_lines.append("")
        markdown_lines.append(f"- **Semana 4 (Descarga):** Reduce el volumen y/o intensidad (RIR {rir_s4}) para facilitar la recuperación y llegar fresco al siguiente bloque. No es una semana perdida, es estratégica.")
    else:
        markdown_lines.append("- El plan progresa de forma gradual semana a semana.")
        markdown_lines.append("- Aumenta la carga cuando puedas completar todas las repeticiones con buena técnica y el RIR indicado.")
        markdown_lines.append("- Respeta los días de descanso, son parte esencial del progreso.")
    
    markdown_lines.append("")
    markdown_lines.append("---")
    markdown_lines.append("")
    
    # ========== 6. INSTRUCCIONES PRÁCTICAS ==========
    markdown_lines.append("## 🧭 Instrucciones Importantes")
    markdown_lines.append("")
    
    instrucciones = [
        "**Calentamiento:** Realiza siempre 1-2 series de calentamiento con poco peso en el primer ejercicio de cada sesión antes de empezar las series de trabajo.",
        "",
        "**RIR (Reps in Reserve):** Es el número de repeticiones que podrías hacer antes del fallo muscular. RIR 4 = podrías hacer 4 reps más. RIR 3 = 3 reps más. Usa este indicador para controlar tu esfuerzo, no vayas siempre al fallo.",
        "",
        "**Progresión:** Aumenta el peso cuando puedas completar todas las series y repeticiones con el RIR indicado y buena técnica. Incrementos de 2.5-5kg en ejercicios grandes, 1-2.5kg en accesorios.",
        "",
        "**Descansos:** Respeta los tiempos de descanso indicados. Son parte del diseño del plan. Si necesitas 10-15s más en alguna serie pesada, no pasa nada, pero no los acortes demasiado.",
        "",
        "**Señales de alerta:** Si sientes dolor articular (no confundir con ardor muscular), para inmediatamente. Si un día estás muy fatigado, mantén el peso o reduce ligeramente el volumen, no fuerces.",
        "",
        "**Técnica primero:** La buena técnica es más importante que la carga. Si tienes dudas sobre algún ejercicio, consulta videos o pregunta a un entrenador antes de cargar mucho peso."
    ]
    
    for instruccion in instrucciones:
        markdown_lines.append(instruccion)
    
    markdown_lines.append("")
    markdown_lines.append("---")
    markdown_lines.append("")
    
    # Nota final
    markdown_lines.append("*Este plan ha sido generado específicamente para ti por el sistema EDN360. Para dudas o ajustes, consulta con tu entrenador.*")
    
    # Unir todas las líneas
    return "\n".join(markdown_lines)


def normalize_sessions_structure(sessions_data: Dict) -> Dict[str, list]:
    """
    Normaliza la estructura de sessions/safe_sessions a un formato estándar.
    
    E5 genera: {"semana_1": [lista_sesiones], ...}
    E6 genera: {"semana_1": {"dia_1": {...}, "dia_2": {...}}, ...}
    
    Esta función convierte ambos al formato de E5 (lista de sesiones).
    """
    normalized = {}
    
    for week_key, week_data in sessions_data.items():
        if not week_key.startswith("semana_"):
            continue
        
        # Si ya es una lista, usar directamente
        if isinstance(week_data, list):
            normalized[week_key] = week_data
        
        # Si es un dict con dias, convertir
        elif isinstance(week_data, dict):
            sesiones = []
            
            # Ordenar los días (dia_1, dia_2, etc.)
            dias_ordenados = sorted(
                [k for k in week_data.keys() if k.startswith("dia_")],
                key=lambda x: int(x.split("_")[1])
            )
            
            for dia_key in dias_ordenados:
                dia_data = week_data[dia_key]
                
                # Extraer info de la sesión
                ejercicios_adaptados = dia_data.get("ejercicios_adaptados", [])
                
                if not ejercicios_adaptados:
                    continue
                
                # Reconstruir sesión en formato E5
                sesion = {
                    "dia": int(dia_key.split("_")[1]),
                    "dia_semana": _get_dia_semana(int(dia_key.split("_")[1])),
                    "hora_recomendada": "18:00",  # Default
                    "nombre": f"Sesión {dia_key.split('_')[1]}",
                    "duracion_min": 60,  # Default
                    "ejercicios": []
                }
                
                # Convertir ejercicios
                for ej in ejercicios_adaptados:
                    ejercicio = {
                        "nombre": ej.get("nombre", "Ejercicio"),
                        "series": ej.get("series", 3),
                        "reps": ej.get("reps", "8-10"),
                        "rir": ej.get("rir", "4"),
                        "descanso": ej.get("descanso", 90)
                    }
                    sesion["ejercicios"].append(ejercicio)
                
                if sesion["ejercicios"]:
                    sesiones.append(sesion)
            
            normalized[week_key] = sesiones
    
    return normalized


def _get_dia_semana(dia_num: int) -> str:
    """Convierte número de día a nombre del día."""
    dias = {
        1: "Lunes",
        2: "Martes",
        3: "Miércoles",
        4: "Jueves",
        5: "Viernes",
        6: "Sábado",
        7: "Domingo"
    }
    return dias.get(dia_num, f"Día {dia_num}")


def validate_sessions_exist(sessions_data: Dict) -> tuple[bool, str]:
    """
    Valida que existan sesiones completas.
    
    Returns:
        (is_valid, error_message)
    """
    if not sessions_data:
        return False, "No hay datos de sesiones (sessions_data vacío)"
    
    total_sesiones = 0
    semanas_con_datos = 0
    
    for week_key, week_data in sessions_data.items():
        if not week_key.startswith("semana_"):
            continue
        
        if isinstance(week_data, list):
            if week_data:
                semanas_con_datos += 1
                total_sesiones += len(week_data)
        elif isinstance(week_data, dict):
            dias_con_ejercicios = 0
            for dia_key, dia_data in week_data.items():
                if dia_key.startswith("dia_"):
                    ejercicios = dia_data.get("ejercicios_adaptados", [])
                    if ejercicios:
                        dias_con_ejercicios += 1
            if dias_con_ejercicios > 0:
                semanas_con_datos += 1
                total_sesiones += dias_con_ejercicios
    
    if total_sesiones == 0:
        return False, f"No hay sesiones con ejercicios (0 sesiones encontradas)"
    
    if semanas_con_datos == 0:
        return False, f"No hay semanas con datos de entrenamiento"
    
    return True, f"{total_sesiones} sesiones en {semanas_con_datos} semanas"


def format_plan_for_client(training_data: Dict[str, Any]) -> str:
    """
    Genera el formatted_plan premium a partir de training.sessions (E5).
    
    DECISIÓN DE ARQUITECTURA:
    - training.sessions (E5) es la FUENTE DE VERDAD para el contenido del cliente
    - training.safe_sessions (E6) se usa SOLO para auditoría y validación interna
    - El formatted_plan NUNCA debe generarse a partir de safe_sessions
    
    Args:
        training_data: Dict con client_summary, mesocycle, sessions, etc.
    
    Returns:
        String con el plan completo en Markdown
        
    Raises:
        ValueError: Si training.sessions no contiene las 4 semanas completas
    """
    # USAR SOLO training.sessions (E5) - NO safe_sessions
    raw_sessions = training_data.get("sessions")
    
    if not raw_sessions:
        raise ValueError("training.sessions (E5) no existe. El plan no puede generarse sin las sesiones base.")
    
    # Validar que existan sesiones completas
    is_valid, message = validate_sessions_exist(raw_sessions)
    if not is_valid:
        raise ValueError(f"training.sessions (E5) inválido: {message}")
    
    # Normalizar estructura (por si E5 genera formato diferente)
    normalized_sessions = normalize_sessions_structure(raw_sessions)
    
    # Validar normalización
    is_valid, message = validate_sessions_exist(normalized_sessions)
    if not is_valid:
        raise ValueError(f"Error normalizando training.sessions: {message}")
    
    # Validar que haya al menos 3 semanas (mínimo aceptable para un plan)
    num_semanas = len([k for k in normalized_sessions.keys() if k.startswith("semana_")])
    if num_semanas < 3:
        raise ValueError(f"Plan incompleto: solo {num_semanas} semanas encontradas. Se requieren al menos 3 semanas.")
    
    mesocycle = training_data.get("mesocycle", {})
    client_summary = training_data.get("client_summary", {})
    
    return generate_premium_markdown(normalized_sessions, mesocycle, client_summary)
