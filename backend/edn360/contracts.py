"""
Contratos JSON para validación de entrada/salida de agentes
Define las estructuras esperadas para cada agente del sistema
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ==================== TRAINING AGENTS CONTRACTS ====================

class E1ProfileContract(BaseModel):
    """Contrato de salida para E1 - Analista del Atleta"""
    perfil_tecnico: Dict[str, Any]
    datos_limpios: Dict[str, Any]
    clasificacion_experiencia: str
    notas_relevantes: List[str]


class E2CapacityContract(BaseModel):
    """Contrato de salida para E2 - Evaluador de Capacidad y Riesgo"""
    seg_score: float  # Seguridad Estructural General
    split_recomendado: str  # "full-body", "upper-lower", "ppl"
    tiempo_maximo_sesion: int  # minutos
    rir_objetivo: int
    banderas_clinicas: List[str]
    restricciones: List[str]


class E3AdaptationContract(BaseModel):
    """Contrato de salida para E3 - Analista de Historial y Adaptación"""
    ia_score: float  # Índice de Adaptación
    tipo_adaptador: str  # "lento", "medio", "rápido"
    resiliencia_lesiones: str  # "baja", "media", "alta"
    estrategia_progresion: str
    factor_conservadurismo: float


class E4ProgramContract(BaseModel):
    """Contrato de salida para E4 - Arquitecto del Programa"""
    plan_mesociclo: Dict[str, Any]  # 4 semanas
    semanas: List[Dict[str, Any]]
    volumen_por_grupo: Dict[str, int]  # series por grupo muscular
    kpis_objetivo: Dict[str, float]
    estrategia_periodizacion: str


class E5MicrocycleContract(BaseModel):
    """Contrato de salida para E5 - Ingeniero de Microciclos"""
    sesiones_detalladas: List[Dict[str, Any]]
    ejercicios_por_sesion: Dict[str, List[Dict[str, Any]]]
    volumen_total_series: int
    tiempo_estimado_total: int


class E6ClinicalContract(BaseModel):
    """Contrato de salida para E6 - Técnico Clínico-Preventivo"""
    sustituciones_realizadas: List[Dict[str, Any]]
    correctivos_añadidos: List[Dict[str, Any]]
    validacion_equilibrios: Dict[str, bool]
    plan_seguro: Dict[str, Any]


class E7LoadContract(BaseModel):
    """Contrato de salida para E7 - Analista de Carga Interna"""
    cit_semanal: float  # Carga Interna Total
    irg_score: float  # Índice Recuperación Global
    distribucion_carga: Dict[str, float]
    recomendaciones_recuperacion: List[str]


class E8AuditContract(BaseModel):
    """Contrato de salida para E8 - Auditor Técnico"""
    auditoria_completa: Dict[str, Any]
    validaciones: Dict[str, bool]
    errores_detectados: List[str]
    plan_aprobado: bool
    correcciones_aplicadas: List[str]


class E9BridgeContract(BaseModel):
    """Contrato de salida para E9 - Bridge hacia Nutrición"""
    mapa_energetico: Dict[str, Any]
    tdee_estimado: float
    dias_amb: Dict[str, str]  # {"lunes": "A", "martes": "M", ...}
    prioridad_metabolica: str  # "perdida", "ganancia", "mantenimiento"
    demanda_calorica_entrenamiento: Dict[str, float]


# ==================== NUTRITION AGENTS CONTRACTS ====================

class N0TriageContract(BaseModel):
    """Contrato de salida para N0 - Triage"""
    elegibilidad: str  # "apto", "requiere_supervision", "no_apto"
    nivel_impaciencia: str  # "leve", "moderada", "alta"
    rango_deficit_permitido: Dict[str, float]
    señales_alerta: List[str]


class N1MetabolicContract(BaseModel):
    """Contrato de salida para N1 - Analista Metabólico"""
    tdee: float
    bmr: float
    ta: float  # Termogénesis Adaptativa
    perfil_metabolico: str
    adherencia_fisiologica: float


class N2EnergyContract(BaseModel):
    """Contrato de salida para N2 - Selector Energético"""
    kcal_objetivo: float
    deficit_pct: float
    macros_gkg: Dict[str, float]  # {"P": 2.2, "G": 0.9, "C": 3.5}
    estrategia_calorica: str


class N3TemplateContract(BaseModel):
    """Contrato de salida para N3 - Snap a Plantilla"""
    plantilla_asignada: str  # "1500kcal", "2000kcal", etc.
    kcal_plantilla: float
    macros_oficiales: Dict[str, float]
    ajuste_necesario: str


class N4SyncContract(BaseModel):
    """Contrato de salida para N4 - Sincronizador A/M/B"""
    calendario_mensual: List[Dict[str, Any]]  # 4 semanas con días A/M/B
    distribucion_amb: Dict[str, int]  # {"A": 12, "M": 10, "B": 8}
    sincronizacion_entrenamiento: bool
    patron_semanal: str


class N5TimingContract(BaseModel):
    """Contrato de salida para N5 - Reparto & Timing"""
    comidas_por_dia: int
    horarios_comidas: List[str]
    distribucion_macros: Dict[str, Dict[str, float]]
    ventana_alimentaria: str
    timing_pre_post_entreno: Dict[str, Any]


class N6MenusContract(BaseModel):
    """Contrato de salida para N6 - Menús & Equivalencias"""
    menus_semanales: Dict[str, List[Dict[str, Any]]]
    equivalencias: Dict[str, List[str]]
    lista_compra: List[str]
    batch_cooking_sugerencias: List[str]


class N7AdherenceContract(BaseModel):
    """Contrato de salida para N7 - Coach de Adherencia"""
    friccion_detectada: str  # "baja", "media", "alta"
    estrategias_simplificacion: List[str]
    swaps_sugeridos: List[Dict[str, Any]]
    mensaje_motivacional: str


class N8WatchdogContract(BaseModel):
    """Contrato de salida para N8 - Watchdog"""
    auditoria_seguridad: Dict[str, bool]
    validaciones_cumplidas: List[str]
    alertas: List[str]
    plan_aprobado: bool
    recomendaciones_finales: List[str]


# ==================== FOLLOWUP TRAINING CONTRACTS ====================

class ES1InterpreterContract(BaseModel):
    """Contrato de salida para ES1 - Intérprete de Seguimiento"""
    diagnostico: str  # "progreso", "estancamiento", "regresion", "bloqueo"
    causas_identificadas: List[str]
    metricas_clave: Dict[str, float]
    cambios_necesarios: bool


class ES2PerformanceContract(BaseModel):
    """Contrato de salida para ES2 - Evaluador de Rendimiento"""
    decision: str  # "mantener", "intensificar", "descargar", "bloquear"
    irg_actual: float
    cit_actual: float
    justificacion: str
    nivel_fatiga: str


class ES3AdjustmentsContract(BaseModel):
    """Contrato de salida para ES3 - Arquitecto de Ajustes"""
    ajustes_aplicados: Dict[str, Any]
    cambios_volumen: Dict[str, float]
    cambios_intensidad: Dict[str, float]
    nuevos_ejercicios: List[Dict[str, Any]]
    plan_ajustado: Dict[str, Any]


class ES4ContinuityContract(BaseModel):
    """Contrato de salida para ES4 - Auditor de Continuidad"""
    validacion_coherencia: Dict[str, bool]
    plan_aprobado: bool
    handoff_nutricion: Dict[str, Any]
    mensaje_cliente: str


# ==================== FOLLOWUP NUTRITION CONTRACTS ====================

class NS1InterpreterContract(BaseModel):
    """Contrato de salida para NS1 - Intérprete Metabólico"""
    diagnostico_metabolico: str  # "homeostasis", "adaptacion", "fatiga", "bloqueo"
    cambio_peso_semanal: float
    tasa_perdida: float
    señales_ta: List[str]
    requiere_ajuste: bool


class NS2EnergyEvaluatorContract(BaseModel):
    """Contrato de salida para NS2 - Evaluador de Energía"""
    tdee_actualizado: float
    ta_detectada: float
    decision_kcal: str  # "mantener", "subir", "bajar", "refeed"
    nuevas_kcal_objetivo: float
    nuevos_macros: Dict[str, float]


class NS3MacroAdjusterContract(BaseModel):
    """Contrato de salida para NS3 - Ajustador de Macros A/M/B"""
    plan_amb_actualizado: List[Dict[str, Any]]
    kcal_promedio_semanal: float
    modulacion_dias: Dict[str, Dict[str, float]]
    sincronizacion_ok: bool


class NS4NutritionAuditorContract(BaseModel):
    """Contrato de salida para NS4 - Auditor Nutricional"""
    veredicto: str  # "aprobado", "correcciones_menores", "correcciones_obligatorias", "bloqueado"
    validaciones: Dict[str, str]
    metricas_finales: Dict[str, float]
    plan_definitivo: Dict[str, Any]
    mensaje_cliente: str


# ==================== VALIDATION HELPERS ====================

def validate_agent_output(agent_id: str, output_data: Dict[str, Any]) -> bool:
    """
    Valida que la salida de un agente cumpla con su contrato
    
    Args:
        agent_id: ID del agente (E1, E2, N0, etc.)
        output_data: Datos de salida del agente
        
    Returns:
        bool: True si la validación es exitosa
    """
    contract_map = {
        # Training Initial
        "E1": E1ProfileContract,
        "E2": E2CapacityContract,
        "E3": E3AdaptationContract,
        "E4": E4ProgramContract,
        "E5": E5MicrocycleContract,
        "E6": E6ClinicalContract,
        "E7": E7LoadContract,
        "E8": E8AuditContract,
        "E9": E9BridgeContract,
        
        # Nutrition Initial
        "N0": N0TriageContract,
        "N1": N1MetabolicContract,
        "N2": N2EnergyContract,
        "N3": N3TemplateContract,
        "N4": N4SyncContract,
        "N5": N5TimingContract,
        "N6": N6MenusContract,
        "N7": N7AdherenceContract,
        "N8": N8WatchdogContract,
        
        # Training Followup
        "ES1": ES1InterpreterContract,
        "ES2": ES2PerformanceContract,
        "ES3": ES3AdjustmentsContract,
        "ES4": ES4ContinuityContract,
        
        # Nutrition Followup
        "NS1": NS1InterpreterContract,
        "NS2": NS2EnergyEvaluatorContract,
        "NS3": NS3MacroAdjusterContract,
        "NS4": NS4NutritionAuditorContract,
    }
    
    contract_class = contract_map.get(agent_id)
    if not contract_class:
        return False
    
    try:
        contract_class(**output_data)
        return True
    except Exception:
        return False
