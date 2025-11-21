"""
TEST SIMPLE BLOQUE 1 - Verificar que build_scoped_input_for_agent funciona
"""

import sys
import json
sys.path.append('/app/backend')
sys.path.append('/app/backend/edn360')

from edn360.client_context_models import ClientContext, ClientContextMeta, RawInputs, TrainingData, SelectedInputs
from edn360.orchestrator import build_scoped_input_for_agent

def estimate_tokens(data):
    """Estimación de tokens"""
    text = json.dumps(data, ensure_ascii=False, default=str)
    return len(text) // 4

# Crear un client_context de prueba
print("=" * 80)
print("🧪 TEST BLOQUE 1 - build_scoped_input_for_agent()")
print("=" * 80)

# Mock data
meta = ClientContextMeta(
    client_id="test_123",
    snapshot_id="snap_456",
    version=1,
    selected_inputs=SelectedInputs(cuestionario="q1")
)

raw_inputs = RawInputs(
    cuestionario_inicial=json.dumps({
        "nombre": "Ana López",
        "edad": 32,
        "peso": 68,
        "altura_cm": 165,
        "objetivo": "perdida_grasa",
        "experiencia": "3 años gym intermitente",
        "lesiones": "dolor lumbar ocasional",
        "equipo": "gym completo",
        "dias_semana": 4,
        "minutos_sesion": 60,
        "horario": "tarde 18:00"
    })
)

training = TrainingData(
    client_summary={
        "id_cliente": "test_123",
        "objetivo_principal": "perdida_grasa",
        "nivel": "intermedio",
        "edad": 32,
        "sexo": "mujer",
        "imc": 25.0,
        "clasificacion_imc": "sobrepeso",
        "limitaciones_clave": ["dolor_lumbar_ocasional"],
        "ejercicios_prohibidos": ["peso_muerto_convencional"],
        "disponibilidad": {
            "dias_semana": 4,
            "minutos_sesion": 60,
            "horario": "tarde_18:00"
        },
        "equipo": "gym_completo",
        "modo": "inicial",
        "alertas": [],
        "experiencia_resumen": "3 años gym intermitente",
        "factores_vida": {
            "sueno_h": 7,
            "estres": "medio",
            "adherencia_historica": "baja"
        }
    },
    profile={
        "perfil_tecnico": {
            "edad": 32,
            "peso_kg": 68,
            "altura_cm": 165,
            "imc": 25.0
        },
        "experiencia": {"nivel": "intermedio"},
        "objetivo": {"principal": "perdida_grasa"}
    },
    capacity={
        "seg_score": 7.5,
        "split_recomendado": {"tipo": "upper-lower"},
        "rir_objetivo": {"semanas_1_2": 5}
    },
    adaptation={
        "ia_score": 6.5,
        "tipo_adaptador": "medio",
        "factor_conservadurismo": 0.9
    }
)

client_context = ClientContext(
    meta=meta,
    raw_inputs=raw_inputs,
    training=training
)

print("\n### TAMAÑOS DE INPUT POR AGENTE\n")

agents = ["E1", "E2", "E3", "E4"]
results = {}

for agent_id in agents:
    input_data = build_scoped_input_for_agent(agent_id, client_context)
    tokens = estimate_tokens(input_data)
    results[agent_id] = tokens
    
    print(f"{agent_id}:")
    print(f"  Tokens estimados: ~{tokens:,}")
    print(f"  Campos en training: {list(input_data.get('training', {}).keys())}")
    print(f"  Tiene raw_inputs: {'Sí' if input_data.get('raw_inputs') else 'No'}")
    print()

print("\n### REDUCCIÓN DE CONTEXTO\n")

e1_tokens = results["E1"]
for agent_id in ["E2", "E3", "E4"]:
    agent_tokens = results[agent_id]
    reduction = ((e1_tokens - agent_tokens) / e1_tokens) * 100 if e1_tokens > 0 else 0
    print(f"E1 → {agent_id}: Reducción de {reduction:.1f}% ({e1_tokens:,} → {agent_tokens:,} tokens)")

print("\n### VERIFICACIÓN DE client_summary\n")

# Verificar que E2-E4 tienen client_summary
for agent_id in ["E2", "E3", "E4"]:
    input_data = build_scoped_input_for_agent(agent_id, client_context)
    has_summary = "client_summary" in input_data.get("training", {})
    has_raw = bool(input_data.get("raw_inputs"))
    
    status = "✅" if has_summary and not has_raw else "❌"
    print(f"{agent_id}: {status} client_summary={has_summary}, raw_inputs={has_raw}")

print("\n" + "=" * 80)
print("✅ TEST COMPLETADO")
print("=" * 80)
