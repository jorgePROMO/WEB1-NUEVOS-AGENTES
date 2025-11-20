"""
Modelos Pydantic para el client_context según documento oficial:
"EMERGENT – SISTEMA DE AGENTES DE ENTRENAMIENTO"

IMPORTANTE: Esta es una traducción LITERAL del contrato definido en el documento.
NO se han añadido campos adicionales ni modificaciones.
"""

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


# ============================================================================
# META - Información de trazabilidad del snapshot
# ============================================================================

class SelectedInputs(BaseModel):
    """Referencias a los inputs usados para generar este plan"""
    cuestionario: str = Field(..., description="ID del cuestionario usado")
    entrenamiento_base: Optional[str] = Field(None, description="ID del entrenamiento base (para progresiones)")


class ClientContextMeta(BaseModel):
    """Metadatos de trazabilidad del snapshot"""
    client_id: str = Field(..., description="Identificador único del cliente")
    snapshot_id: str = Field(..., description="ID único de este snapshot/versión")
    version: int = Field(..., description="Número de versión (1 para inicial, 2+ para seguimientos)")
    selected_inputs: SelectedInputs = Field(..., description="Referencias a inputs usados")


# ============================================================================
# RAW_INPUTS - Datos crudos de entrada
# ============================================================================

class RawInputs(BaseModel):
    """Datos crudos de entrada antes de procesamiento por agentes"""
    cuestionario_inicial: Optional[str] = Field(None, description="Texto completo del cuestionario inicial")
    cuestionario_seguimiento: Optional[str] = Field(None, description="Texto completo del cuestionario de seguimiento")
    entrenamiento_base: Optional[Dict[str, Any]] = Field(None, description="Objeto del entrenamiento previo (para progresiones)")
    notas_entrenador: Optional[str] = Field(None, description="Notas adicionales del entrenador")


# ============================================================================
# TRAINING - Datos procesados por agentes E1-E9
# ============================================================================

class TrainingData(BaseModel):
    """
    Datos de entrenamiento procesados por la cadena de agentes E1-E9.
    Cada campo es responsabilidad de un agente específico.
    
    REGLAS:
    - Cada agente modifica SOLO su campo asignado
    - Los agentes NO pueden borrar ni modificar campos de otros agentes
    - El objeto completo viaja de E1 → E2 → ... → E9
    """
    
    # E1 - Analista de Datos del Cliente
    profile: Optional[Any] = Field(
        None, 
        description="Perfil del cliente generado por E1 (Analista)"
    )
    constraints: Optional[Any] = Field(
        None,
        description="Restricciones del cliente generado por E1 (Analista)"
    )
    prehab: Optional[Any] = Field(
        None,
        description="Protocolos de prehab generados por E1 (Analista)"
    )
    progress: Optional[Any] = Field(
        None,
        description="Progreso del cliente generado por E1 (Analista) - Solo en seguimientos"
    )
    
    # E2 - Evaluador de Capacidad
    capacity: Optional[Any] = Field(
        None,
        description="Capacidad de entrenamiento evaluada por E2 (Evaluador de Capacidad)"
    )
    
    # E3 - Adaptador (Estrés/Sueño/Vida Real)
    adaptation: Optional[Any] = Field(
        None,
        description="Adaptaciones necesarias generadas por E3 (Adaptador)"
    )
    
    # E4 - Arquitecto del Mesociclo
    mesocycle: Optional[Any] = Field(
        None,
        description="Estructura del mesociclo de 4 semanas generada por E4 (Arquitecto)"
    )
    
    # E5 - Ingeniero de Sesiones
    sessions: Optional[Any] = Field(
        None,
        description="Sesiones detalladas con ejercicios generadas por E5 (Ingeniero)"
    )
    
    # E6 - Técnico Clínico
    safe_sessions: Optional[Any] = Field(
        None,
        description="Sesiones seguras con sustituciones y prehab por E6 (Técnico Clínico)"
    )
    
    # E7 - Visualizador
    formatted_plan: Optional[Any] = Field(
        None,
        description="Plan formateado para el cliente por E7 (Visualizador)"
    )
    
    # E8 - Auditor de Calidad
    audit: Optional[Any] = Field(
        None,
        description="Auditoría de calidad del plan por E8 (Auditor)"
    )
    
    # E9 - Bridge para Nutrición
    bridge_for_nutrition: Optional[Any] = Field(
        None,
        description="Puente hacia agentes de nutrición generado por E9 (Bridge)"
    )


# ============================================================================
# NUTRITION - Datos procesados por agentes N0-N8
# ============================================================================

class NutritionData(BaseModel):
    """
    Datos de nutrición procesados por la cadena de agentes N0-N8.
    Cada campo es responsabilidad de un agente específico.
    
    REGLAS:
    - Cada agente modifica SOLO su campo asignado
    - Los agentes NO pueden borrar ni modificar campos de otros agentes
    - El objeto completo viaja de N0 → N1 → ... → N8
    - Usa training.bridge_for_nutrition como nexo con entrenamiento
    """
    
    # N0 - Analista de Triaje Nutricional
    profile: Optional[Any] = Field(
        None,
        description="Perfil nutricional del cliente generado por N0 (Analista de Triaje)"
    )
    
    # N1 - Analista Metabólico
    metabolism: Optional[Any] = Field(
        None,
        description="Análisis metabólico generado por N1 (Analista Metabólico)"
    )
    
    # N2 - Selector de Estrategia Energética
    energy_strategy: Optional[Any] = Field(
        None,
        description="Estrategia energética seleccionada por N2 (Selector de Estrategia)"
    )
    
    # N3 - Generador de Plantilla de Macros
    macro_design: Optional[Any] = Field(
        None,
        description="Diseño de macronutrientes generado por N3 (Generador de Plantilla)"
    )
    
    # N4 - Sincronizador A-M-B
    weekly_structure: Optional[Any] = Field(
        None,
        description="Estructura semanal sincronizada por N4 (Sincronizador A-M-B)"
    )
    
    # N5 - Distribuidor de Timing
    timing_plan: Optional[Any] = Field(
        None,
        description="Plan de timing de comidas generado por N5 (Distribuidor de Timing)"
    )
    
    # N6 - Generador de Menú
    menu_plan: Optional[Any] = Field(
        None,
        description="Menú detallado generado por N6 (Generador de Menú)"
    )
    
    # N7 - Coach de Adherencia
    adherence_report: Optional[Any] = Field(
        None,
        description="Reporte de adherencia y consejos por N7 (Coach de Adherencia)"
    )
    
    # N8 - Watchdog de Seguridad Nutricional
    audit: Optional[Any] = Field(
        None,
        description="Auditoría de seguridad nutricional por N8 (Watchdog)"
    )


# ============================================================================
# CLIENT_CONTEXT - Objeto principal que viaja entre agentes
# ============================================================================

class ClientContext(BaseModel):
    """
    Objeto principal que contiene TODO el estado del cliente.
    
    Este objeto:
    - Es recibido por TODOS los agentes E1-E9
    - Cada agente modifica SOLO su sección en 'training'
    - Viaja completo de agente en agente sin pérdida de información
    - Permite trazabilidad completa del proceso
    
    Basado en documento oficial:
    "EMERGENT – SISTEMA DE AGENTES DE ENTRENAMIENTO"
    """
    meta: ClientContextMeta = Field(..., description="Metadatos de trazabilidad")
    raw_inputs: RawInputs = Field(..., description="Datos crudos de entrada")
    training: TrainingData = Field(default_factory=TrainingData, description="Datos procesados por agentes E1-E9")
    
    class Config:
        """Configuración de Pydantic"""
        # Permitir campos extra para futura extensibilidad
        extra = "forbid"  # NO permitir campos no definidos (seguridad)
        # Validar al asignar valores
        validate_assignment = True


# ============================================================================
# WRAPPER - Según estructura del documento
# ============================================================================

class ClientContextWrapper(BaseModel):
    """
    Wrapper según estructura exacta del documento:
    { "client_context": { ... } }
    """
    client_context: ClientContext = Field(..., description="Objeto de contexto del cliente")


# ============================================================================
# NOTAS DE IMPLEMENTACIÓN
# ============================================================================

"""
NOTAS IMPORTANTES PARA EL DESARROLLO:

1. ESTRUCTURA INTERNA DE CAMPOS
   - El documento NO especifica la estructura interna de cada campo (profile, capacity, etc.)
   - Por ahora usamos Optional[Any] para máxima flexibilidad
   - En el futuro, cuando tengamos ejemplos reales, podemos crear modelos específicos

2. VALIDACIÓN
   - Cada agente debe validar que recibió los campos que necesita de agentes anteriores
   - Ejemplo: E2 debe verificar que training.profile existe antes de procesar
   - Si falta un campo crítico, el agente debe devolver error técnico

3. REGLAS DE MODIFICACIÓN
   - SOLO el agente asignado puede llenar/modificar su campo
   - E1 modifica: profile, constraints, prehab, progress
   - E2 modifica: capacity
   - E3 modifica: adaptation
   - E4 modifica: mesocycle
   - E5 modifica: sessions
   - E6 modifica: safe_sessions
   - E7 modifica: formatted_plan
   - E8 modifica: audit
   - E9 modifica: bridge_for_nutrition

4. FLUJO DE DATOS
   client_context → E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8 → E9 → client_context completo

5. KNOWLEDGE BASE (K1)
   - K1 NO está dentro de client_context
   - K1 se pasa como parámetro separado en execute(client_context, knowledge_base=kb)
   - Ya implementado correctamente en BaseAgent

6. EXTENSIBILIDAD FUTURA
   - Si necesitamos añadir campos nuevos, se hace mediante actualización del modelo
   - NO se deben añadir campos ad-hoc sin actualizar este archivo
   - Mantener siempre sincronizado con documento oficial
"""
