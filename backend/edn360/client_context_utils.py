"""
Utilidades para trabajar con client_context

Funciones auxiliares para:
- Inicializar client_context desde cuestionarios
- Validar que agentes completaron sus campos
- Serializar/deserializar para JSON
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from .client_context_models import (
    ClientContext,
    ClientContextMeta,
    SelectedInputs,
    RawInputs,
    TrainingData,
    NutritionData,
    ClientContextWrapper
)


def initialize_client_context(
    client_id: str,
    version: int,
    cuestionario_data: Dict[str, Any],
    previous_training: Optional[Dict[str, Any]] = None,
    is_followup: bool = False
) -> ClientContext:
    """
    Inicializa un client_context desde los datos del cuestionario.
    
    Args:
        client_id: ID único del cliente
        version: Número de versión (1 para inicial, 2+ para seguimientos)
        cuestionario_data: Datos del cuestionario (inicial o seguimiento)
        previous_training: Entrenamiento previo (para progresiones)
        is_followup: True si es un seguimiento, False si es inicial
        
    Returns:
        ClientContext inicializado con meta y raw_inputs llenos
    """
    # Generar snapshot_id único
    snapshot_id = f"snapshot_{client_id}_{version}_{uuid.uuid4().hex[:8]}"
    
    # Crear meta
    meta = ClientContextMeta(
        client_id=client_id,
        snapshot_id=snapshot_id,
        version=version,
        selected_inputs=SelectedInputs(
            cuestionario=cuestionario_data.get("id", "unknown"),
            entrenamiento_base=previous_training.get("id") if previous_training else None
        )
    )
    
    # Crear raw_inputs
    # Serializar el cuestionario a string JSON para mantenerlo crudo
    cuestionario_str = json.dumps(cuestionario_data, ensure_ascii=False, indent=2)
    
    raw_inputs = RawInputs(
        cuestionario_inicial=cuestionario_str if not is_followup else None,
        cuestionario_seguimiento=cuestionario_str if is_followup else None,
        entrenamiento_base=previous_training,
        notas_entrenador=cuestionario_data.get("notas_entrenador")
    )
    
    # Crear training y nutrition vacíos (los agentes los llenarán)
    training = TrainingData()
    nutrition = NutritionData()
    
    # Construir client_context
    client_context = ClientContext(
        meta=meta,
        raw_inputs=raw_inputs,
        training=training,
        nutrition=nutrition
    )
    
    return client_context


def validate_agent_output(
    agent_id: str,
    client_context: ClientContext,
    required_fields: list[str]
) -> tuple[bool, Optional[str]]:
    """
    Valida que un agente completó sus campos requeridos.
    
    Args:
        agent_id: ID del agente (E1, E2, N0, etc.)
        client_context: Objeto client_context después de la ejecución del agente
        required_fields: Lista de campos que el agente debe haber llenado
        
    Returns:
        (valid, error_message): True si válido, False con mensaje de error si no
    """
    # Determinar si es agente E o N
    is_nutrition_agent = agent_id.startswith("N")
    data_section = client_context.nutrition if is_nutrition_agent else client_context.training
    section_name = "nutrition" if is_nutrition_agent else "training"
    
    for field in required_fields:
        value = getattr(data_section, field, None)
        if value is None:
            return False, f"{agent_id} did not fill required field: {section_name}.{field}"
    
    return True, None


def validate_agent_input(
    agent_id: str,
    client_context: ClientContext,
    required_fields: list[str]
) -> tuple[bool, Optional[str]]:
    """
    Valida que un agente tiene los campos necesarios de agentes anteriores.
    
    Args:
        agent_id: ID del agente (E1, E2, N0, etc.)
        client_context: Objeto client_context antes de la ejecución del agente
        required_fields: Lista de campos que deben existir de agentes anteriores
        
    Returns:
        (valid, error_message): True si válido, False con mensaje de error si no
    """
    # Determinar si es agente E o N
    is_nutrition_agent = agent_id.startswith("N")
    data_section = client_context.nutrition if is_nutrition_agent else client_context.training
    section_name = "nutrition" if is_nutrition_agent else "training"
    
    for field in required_fields:
        value = getattr(data_section, field, None)
        if value is None:
            return False, f"{agent_id} missing required input: {section_name}.{field} (should be populated by previous agent)"
    
    return True, None


def client_context_to_dict(client_context: ClientContext) -> Dict[str, Any]:
    """
    Convierte client_context a diccionario para serialización JSON.
    
    Args:
        client_context: Objeto ClientContext
        
    Returns:
        Dict serializable a JSON
    """
    return client_context.model_dump(mode='json', exclude_none=False)


def client_context_from_dict(data: Dict[str, Any]) -> ClientContext:
    """
    Crea client_context desde diccionario.
    
    Args:
        data: Diccionario con estructura de ClientContext
        
    Returns:
        Objeto ClientContext
    """
    return ClientContext.model_validate(data)


def wrap_client_context(client_context: ClientContext) -> Dict[str, Any]:
    """
    Envuelve el client_context según estructura del documento:
    { "client_context": { ... } }
    
    Args:
        client_context: Objeto ClientContext
        
    Returns:
        Dict con estructura { "client_context": {...} }
    """
    return {
        "client_context": client_context_to_dict(client_context)
    }


def unwrap_client_context(data: Dict[str, Any]) -> ClientContext:
    """
    Desenvuelve client_context desde estructura del documento.
    
    Args:
        data: Dict con estructura { "client_context": {...} }
        
    Returns:
        Objeto ClientContext
    """
    if "client_context" in data:
        return client_context_from_dict(data["client_context"])
    else:
        return client_context_from_dict(data)


# ============================================================================
# MAPEO DE AGENTES A CAMPOS (según documento)
# ============================================================================

AGENT_FIELD_MAPPING = {
    "E1": {
        "fills": ["profile", "constraints", "prehab"],  # progress es opcional (solo seguimientos)
        "optional_fills": ["progress"],  # progress solo si es seguimiento
        "requires": []  # E1 es el primero, no requiere nada
    },
    "E2": {
        "fills": ["capacity"],
        "requires": ["profile"]  # Necesita el profile de E1
    },
    "E3": {
        "fills": ["adaptation"],
        "requires": ["capacity", "profile"]  # Necesita capacity de E2 y profile de E1
    },
    "E4": {
        "fills": ["mesocycle"],
        "requires": ["capacity", "adaptation", "profile"]
    },
    "E5": {
        "fills": ["sessions"],
        "requires": ["mesocycle", "profile"]
    },
    "E6": {
        "fills": ["safe_sessions"],
        "requires": ["sessions", "constraints", "prehab"]
    },
    "E7": {
        "fills": ["formatted_plan"],
        "requires": ["safe_sessions", "mesocycle"]
    },
    "E8": {
        "fills": ["audit"],
        "requires": ["safe_sessions", "mesocycle", "capacity", "constraints"]
    },
    "E9": {
        "fills": ["bridge_for_nutrition"],
        "requires": ["safe_sessions", "mesocycle", "profile"]
    },
    
    # AGENTES DE NUTRICIÓN (N0-N8)
    # Estos agentes trabajan sobre nutrition.* y leen training.bridge_for_nutrition
    "N0": {
        "fills": ["profile"],  # nutrition.profile
        "requires": [],  # N0 es el primero en nutrition, lee de raw_inputs y training.bridge
        "reads_from_training": ["bridge_for_nutrition"]  # Lee el bridge de E9
    },
    "N1": {
        "fills": ["metabolism"],  # nutrition.metabolism
        "requires": ["profile"],  # Necesita nutrition.profile de N0
        "reads_from_training": ["bridge_for_nutrition"]
    },
    "N2": {
        "fills": ["energy_strategy"],  # nutrition.energy_strategy
        "requires": ["metabolism", "profile"],  # Necesita N1 y N0
        "reads_from_training": ["bridge_for_nutrition"]
    },
    "N3": {
        "fills": ["macro_design"],  # nutrition.macro_design
        "requires": ["energy_strategy", "metabolism"],  # Necesita N2 y N1
        "reads_from_training": ["bridge_for_nutrition"]
    },
    "N4": {
        "fills": ["weekly_structure"],  # nutrition.weekly_structure
        "requires": ["macro_design", "energy_strategy"],  # Necesita N3 y N2
        "reads_from_training": ["bridge_for_nutrition"]
    },
    "N5": {
        "fills": ["timing_plan"],  # nutrition.timing_plan
        "requires": ["weekly_structure", "macro_design"],  # Necesita N4 y N3
        "reads_from_training": ["bridge_for_nutrition"]
    },
    "N6": {
        "fills": ["menu_plan"],  # nutrition.menu_plan
        "requires": ["timing_plan", "weekly_structure", "macro_design", "profile"],  # Necesita N5, N4, N3, N0
        "reads_from_training": []  # No necesita leer de training directamente
    },
    "N7": {
        "fills": ["adherence_report"],  # nutrition.adherence_report
        "requires": ["menu_plan", "profile"],  # Necesita N6 y N0
        "reads_from_training": []
    },
    "N8": {
        "fills": ["audit"],  # nutrition.audit
        "requires": ["menu_plan", "macro_design", "profile"],  # Necesita N6, N3, N0 para auditar
        "reads_from_training": []
    }
}


def get_agent_requirements(agent_id: str) -> Dict[str, list]:
    """
    Obtiene los campos que un agente llena y requiere.
    
    Args:
        agent_id: ID del agente (E1, E2, etc.)
        
    Returns:
        Dict con "fills" y "requires"
    """
    return AGENT_FIELD_MAPPING.get(agent_id, {"fills": [], "requires": []})


def validate_agent_contract(
    agent_id: str,
    client_context_before: ClientContext,
    client_context_after: ClientContext
) -> tuple[bool, list[str]]:
    """
    Valida que un agente cumplió su contrato:
    1. Tiene los inputs requeridos antes de ejecutar
    2. Llenó sus campos asignados después de ejecutar
    3. NO modificó campos de otros agentes
    4. Los agentes E NO tocan nutrition.*, los agentes N NO tocan training.*
    
    Args:
        agent_id: ID del agente (E1-E9, N0-N8)
        client_context_before: Context antes de la ejecución
        client_context_after: Context después de la ejecución
        
    Returns:
        (valid, errors): True si válido, lista de errores si no
    """
    errors = []
    requirements = get_agent_requirements(agent_id)
    is_nutrition_agent = agent_id.startswith("N")
    
    # 1. Validar que tenía inputs requeridos
    valid_input, error_msg = validate_agent_input(
        agent_id, 
        client_context_before, 
        requirements["requires"]
    )
    if not valid_input:
        errors.append(error_msg)
    
    # 2. Validar que llenó sus campos
    valid_output, error_msg = validate_agent_output(
        agent_id,
        client_context_after,
        requirements["fills"]
    )
    if not valid_output:
        errors.append(error_msg)
    
    # 3. Validar que NO modificó campos de otros agentes EN SU PROPIA RAMA
    # (comparar campos que NO son suyos pero están en su misma rama: training o nutrition)
    other_agents_fields = []
    for other_agent_id, mapping in AGENT_FIELD_MAPPING.items():
        # Solo validar agentes de la misma categoría (E con E, N con N)
        other_is_nutrition = other_agent_id.startswith("N")
        if other_agent_id != agent_id and other_is_nutrition == is_nutrition_agent:
            other_agents_fields.extend(mapping["fills"])
    
    # Obtener la sección correcta según el tipo de agente
    before_section = client_context_before.nutrition if is_nutrition_agent else client_context_before.training
    after_section = client_context_after.nutrition if is_nutrition_agent else client_context_after.training
    section_name = "nutrition" if is_nutrition_agent else "training"
    
    for field in other_agents_fields:
        before_value = getattr(before_section, field, None)
        after_value = getattr(after_section, field, None)
        
        # Si el campo ya existía antes y cambió, es un error
        if before_value is not None and before_value != after_value:
            errors.append(
                f"{agent_id} illegally modified field: {section_name}.{field} "
                f"(belongs to another agent)"
            )
    
    # 4. Validar que agentes E NO tocan nutrition.* y agentes N NO tocan training.*
    if is_nutrition_agent:
        # Agentes N no deben modificar training
        before_training = client_context_before.training
        after_training = client_context_after.training
        if before_training != after_training:
            errors.append(f"{agent_id} (nutrition agent) illegally modified training.* fields")
    else:
        # Agentes E no deben modificar nutrition (excepto si nutrition todavía no ha sido inicializada)
        before_nutrition = client_context_before.nutrition
        after_nutrition = client_context_after.nutrition
        # Solo validar si nutrition ya tiene algún campo lleno
        if any(getattr(before_nutrition, field, None) is not None for field in ["profile", "metabolism", "energy_strategy", "macro_design", "weekly_structure", "timing_plan", "menu_plan", "adherence_report", "audit"]):
            if before_nutrition != after_nutrition:
                errors.append(f"{agent_id} (training agent) illegally modified nutrition.* fields")
    
    return len(errors) == 0, errors
