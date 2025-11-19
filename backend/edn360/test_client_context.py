"""
Tests para validar modelos de client_context

Estos tests verifican que:
1. Los modelos Pydantic se construyen correctamente
2. Las utilidades funcionan como esperado
3. La validación de contratos detecta violaciones
"""

import pytest
import json
from .client_context_models import (
    ClientContext,
    ClientContextMeta,
    SelectedInputs,
    RawInputs,
    TrainingData
)
from .client_context_utils import (
    initialize_client_context,
    validate_agent_output,
    validate_agent_input,
    client_context_to_dict,
    client_context_from_dict,
    get_agent_requirements,
    validate_agent_contract
)


def test_client_context_meta_creation():
    """Test que ClientContextMeta se crea correctamente"""
    meta = ClientContextMeta(
        client_id="client_123",
        snapshot_id="snapshot_123",
        version=1,
        selected_inputs=SelectedInputs(
            cuestionario="quest_456",
            entrenamiento_base=None
        )
    )
    
    assert meta.client_id == "client_123"
    assert meta.version == 1
    assert meta.selected_inputs.cuestionario == "quest_456"


def test_raw_inputs_creation():
    """Test que RawInputs se crea correctamente"""
    raw_inputs = RawInputs(
        cuestionario_inicial="Texto del cuestionario",
        cuestionario_seguimiento=None,
        entrenamiento_base=None,
        notas_entrenador="Algunas notas"
    )
    
    assert raw_inputs.cuestionario_inicial == "Texto del cuestionario"
    assert raw_inputs.cuestionario_seguimiento is None
    assert raw_inputs.notas_entrenador == "Algunas notas"


def test_training_data_defaults():
    """Test que TrainingData inicia con todos los campos en None"""
    training = TrainingData()
    
    assert training.profile is None
    assert training.constraints is None
    assert training.prehab is None
    assert training.progress is None
    assert training.capacity is None
    assert training.adaptation is None
    assert training.mesocycle is None
    assert training.sessions is None
    assert training.safe_sessions is None
    assert training.formatted_plan is None
    assert training.audit is None
    assert training.bridge_for_nutrition is None


def test_full_client_context_creation():
    """Test que ClientContext completo se crea correctamente"""
    client_context = ClientContext(
        meta=ClientContextMeta(
            client_id="client_123",
            snapshot_id="snapshot_123",
            version=1,
            selected_inputs=SelectedInputs(
                cuestionario="quest_456",
                entrenamiento_base=None
            )
        ),
        raw_inputs=RawInputs(
            cuestionario_inicial="Texto del cuestionario",
            cuestionario_seguimiento=None,
            entrenamiento_base=None,
            notas_entrenador=None
        ),
        training=TrainingData()
    )
    
    assert client_context.meta.client_id == "client_123"
    assert client_context.training.profile is None


def test_initialize_client_context():
    """Test función de inicialización de client_context"""
    cuestionario_data = {
        "id": "quest_123",
        "nombre": "Juan Pérez",
        "edad": 30,
        "objetivo": "hipertrofia"
    }
    
    client_context = initialize_client_context(
        client_id="client_456",
        version=1,
        cuestionario_data=cuestionario_data,
        is_followup=False
    )
    
    assert client_context.meta.client_id == "client_456"
    assert client_context.meta.version == 1
    assert client_context.raw_inputs.cuestionario_inicial is not None
    assert "Juan Pérez" in client_context.raw_inputs.cuestionario_inicial
    assert client_context.raw_inputs.cuestionario_seguimiento is None


def test_validate_agent_output_success():
    """Test validación exitosa de output de agente"""
    # Crear context con profile llenado (como si E1 lo hubiera completado)
    client_context = ClientContext(
        meta=ClientContextMeta(
            client_id="test",
            snapshot_id="test",
            version=1,
            selected_inputs=SelectedInputs(cuestionario="test")
        ),
        raw_inputs=RawInputs(),
        training=TrainingData(
            profile={"nombre": "Juan", "edad": 30}
        )
    )
    
    valid, error = validate_agent_output("E1", client_context, ["profile"])
    assert valid is True
    assert error is None


def test_validate_agent_output_failure():
    """Test validación fallida cuando falta campo requerido"""
    # Crear context sin profile
    client_context = ClientContext(
        meta=ClientContextMeta(
            client_id="test",
            snapshot_id="test",
            version=1,
            selected_inputs=SelectedInputs(cuestionario="test")
        ),
        raw_inputs=RawInputs(),
        training=TrainingData()
    )
    
    valid, error = validate_agent_output("E1", client_context, ["profile"])
    assert valid is False
    assert "profile" in error


def test_validate_agent_input():
    """Test validación de inputs requeridos por agente"""
    # E2 requiere profile de E1
    client_context = ClientContext(
        meta=ClientContextMeta(
            client_id="test",
            snapshot_id="test",
            version=1,
            selected_inputs=SelectedInputs(cuestionario="test")
        ),
        raw_inputs=RawInputs(),
        training=TrainingData(
            profile={"nombre": "Juan"}
        )
    )
    
    valid, error = validate_agent_input("E2", client_context, ["profile"])
    assert valid is True
    assert error is None


def test_client_context_serialization():
    """Test serialización y deserialización de client_context"""
    original = initialize_client_context(
        client_id="test_123",
        version=1,
        cuestionario_data={"id": "quest_1", "nombre": "Test"},
        is_followup=False
    )
    
    # Serializar
    dict_data = client_context_to_dict(original)
    assert isinstance(dict_data, dict)
    assert "meta" in dict_data
    assert "raw_inputs" in dict_data
    assert "training" in dict_data
    
    # Deserializar
    restored = client_context_from_dict(dict_data)
    assert restored.meta.client_id == original.meta.client_id
    assert restored.meta.version == original.meta.version


def test_agent_field_mapping():
    """Test que el mapeo de agentes a campos está correcto"""
    e1_reqs = get_agent_requirements("E1")
    assert "profile" in e1_reqs["fills"]
    assert "constraints" in e1_reqs["fills"]
    assert len(e1_reqs["requires"]) == 0  # E1 no requiere nada
    
    e2_reqs = get_agent_requirements("E2")
    assert "capacity" in e2_reqs["fills"]
    assert "profile" in e2_reqs["requires"]  # E2 requiere profile de E1


def test_validate_agent_contract_success():
    """Test validación exitosa del contrato de un agente"""
    # Context antes de E1
    before = ClientContext(
        meta=ClientContextMeta(
            client_id="test",
            snapshot_id="test",
            version=1,
            selected_inputs=SelectedInputs(cuestionario="test")
        ),
        raw_inputs=RawInputs(cuestionario_inicial="Test questionnaire"),
        training=TrainingData()
    )
    
    # Context después de E1 (con profile llenado)
    after = ClientContext(
        meta=before.meta,
        raw_inputs=before.raw_inputs,
        training=TrainingData(
            profile={"nombre": "Juan", "edad": 30},
            constraints={"lesiones": []},
            prehab={"protocolos": []}
        )
    )
    
    valid, errors = validate_agent_contract("E1", before, after)
    assert valid is True
    assert len(errors) == 0


def test_validate_agent_contract_missing_output():
    """Test detección de campo no llenado por agente"""
    before = ClientContext(
        meta=ClientContextMeta(
            client_id="test",
            snapshot_id="test",
            version=1,
            selected_inputs=SelectedInputs(cuestionario="test")
        ),
        raw_inputs=RawInputs(),
        training=TrainingData()
    )
    
    # E1 no llenó constraints (debería haber llenado profile, constraints, prehab)
    after = ClientContext(
        meta=before.meta,
        raw_inputs=before.raw_inputs,
        training=TrainingData(
            profile={"nombre": "Juan"},
            # constraints faltante!
            prehab={"protocolos": []}
        )
    )
    
    valid, errors = validate_agent_contract("E1", before, after)
    assert valid is False
    assert any("constraints" in error for error in errors)


def test_validate_agent_contract_illegal_modification():
    """Test detección de modificación ilegal de campo de otro agente"""
    # Context con profile ya llenado por E1
    before = ClientContext(
        meta=ClientContextMeta(
            client_id="test",
            snapshot_id="test",
            version=1,
            selected_inputs=SelectedInputs(cuestionario="test")
        ),
        raw_inputs=RawInputs(),
        training=TrainingData(
            profile={"nombre": "Juan", "edad": 30}
        )
    )
    
    # E2 intentó modificar profile (¡NO PERMITIDO!)
    after = ClientContext(
        meta=before.meta,
        raw_inputs=before.raw_inputs,
        training=TrainingData(
            profile={"nombre": "Pedro", "edad": 25},  # Modificado ilegalmente!
            capacity={"volumen": 10}
        )
    )
    
    valid, errors = validate_agent_contract("E2", before, after)
    assert valid is False
    assert any("illegally modified" in error and "profile" in error for error in errors)


if __name__ == "__main__":
    # Ejecutar tests básicos
    print("🧪 Ejecutando tests de client_context...")
    
    test_client_context_meta_creation()
    print("✅ Meta creation")
    
    test_raw_inputs_creation()
    print("✅ Raw inputs creation")
    
    test_training_data_defaults()
    print("✅ Training data defaults")
    
    test_full_client_context_creation()
    print("✅ Full context creation")
    
    test_initialize_client_context()
    print("✅ Initialize function")
    
    test_validate_agent_output_success()
    print("✅ Validate output success")
    
    test_validate_agent_output_failure()
    print("✅ Validate output failure")
    
    test_validate_agent_input()
    print("✅ Validate input")
    
    test_client_context_serialization()
    print("✅ Serialization")
    
    test_agent_field_mapping()
    print("✅ Agent field mapping")
    
    test_validate_agent_contract_success()
    print("✅ Contract validation success")
    
    test_validate_agent_contract_missing_output()
    print("✅ Contract validation - missing output")
    
    test_validate_agent_contract_illegal_modification()
    print("✅ Contract validation - illegal modification")
    
    print("\n🎉 Todos los tests pasaron!")
