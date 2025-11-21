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
        # Datos básicos (realistas)
        "nombre_completo": "Ana López García",
        "email": "ana.lopez@test.com",
        "fecha_nacimiento": "1992-05-15",
        "sexo": "mujer",
        "profesion": "Ingeniera de software, trabajo 8h/día sentada frente al ordenador. Estrés moderado por deadlines.",
        "direccion": "Calle Mayor 123, Madrid, España",
        "telefono": "+34 600 123 456",
        
        # Medidas corporales
        "peso": "68",
        "altura_cm": "165",
        "grasa_porcentaje": "28",
        "cintura_cm": "78",
        "cadera_cm": "98",
        "biceps_relajado_cm": "28",
        "biceps_flexionado_cm": "30",
        "muslo_cm": "58",
        
        # Salud y medicación
        "medicamentos": "Ninguno actualmente. Anteriormente tomé anticonceptivos pero los dejé hace 6 meses.",
        "enfermedad_cronica": "No tengo enfermedades crónicas diagnosticadas.",
        "fuma_cantidad": "No fumo desde hace 2 años. Antes fumaba ocasionalmente en fiestas.",
        "bebe_cantidad": "Bebo socialmente, 1-2 copas de vino los fines de semana. A veces cerveza después del gym.",
        "retencion_liquidos": "Sí, especialmente en las piernas al final del día y durante el periodo menstrual.",
        "problemas_corazon": "No",
        "hipertension": "No. Presión normal en últimas revisiones.",
        "diabetes": "No",
        "colesterol": "Nivel normal según analítica del año pasado.",
        "sobrepeso": "Sí, según IMC estoy en sobrepeso. Quiero perder 6kg.",
        
        # Experiencia entrenamiento (LARGO - común en cuestionarios reales)
        "experiencia_entrenamiento": """He entrenado durante 3 años en el gimnasio pero de forma muy intermitente. 
        Empecé en 2019 con un entrenador personal durante 6 meses, luego por pandemia dejé de ir casi 1 año. 
        En 2021 volví al gym pero sin seguir ningún plan específico, hacía lo que me apetecía cada día. 
        A veces iba 4 días seguidos y luego dejaba 2 semanas sin ir. En 2022 probé clases de crossfit durante 
        3 meses pero me lesioné la espalda y tuve que parar. Desde entonces he vuelto al gym tradicional pero 
        siento que no veo progreso porque no tengo constancia ni estructura. Conozco los ejercicios básicos 
        (sentadillas, press banca, peso muerto) pero no estoy segura de mi técnica, especialmente en peso muerto 
        porque me duele la lumbar cuando lo hago pesado. Me gustaría tener un plan estructurado que me motive 
        a ser constante y ver resultados reales.""",
        
        "frecuencia_entrenamiento": "Actualmente 3-4 veces por semana cuando soy constante, pero a veces bajo a 2 veces o incluso 1 semana completa sin ir por trabajo.",
        
        "tiempo_disponible": "Puedo entrenar 60 minutos por sesión. A veces 70 si no tengo mucho trabajo. Los fines de semana podría hacer 90 minutos pero prefiero entrenar entre semana.",
        
        "horario_preferido": "Tarde, entre 18:00 y 19:30. Trabajo hasta las 18:00 y el gym me queda cerca de casa. Los viernes a veces voy a las 17:00 porque salgo antes. Nunca puedo ir por la mañana porque entro a trabajar a las 9:00.",
        
        "equipo_disponible": "Gimnasio completo: barras olímpicas, mancuernas hasta 40kg, máquinas (prensa, poleas, smith), rack para sentadillas, bancos ajustables, TRX, kettlebells, bandas elásticas. También hay zona de cardio con cintas y bicicletas pero no me gusta mucho el cardio. Prefiero pesas.",
        
        # Lesiones (DETALLADO - muy común)
        "lesiones_actuales": """Tengo dolor lumbar ocasional, sobre todo cuando hago peso muerto convencional 
        o buenos días. El dolor aparece al día siguiente, no durante el ejercicio. Es un dolor sordo en la zona 
        baja de la espalda, lado derecho principalmente. A veces también me molesta al estar mucho tiempo sentada 
        en el trabajo. He ido al fisio 2 veces y me dijo que tenía la musculatura lumbar débil y el core poco 
        activado. Me recomendó hacer planchas y ejercicios de bird-dog pero no los hago con regularidad. 
        El dolor no es constante, solo aparece cuando hago ejercicios pesados de espalda baja o cuando estoy 
        muy estresada. Escala de dolor: 4-5 de 10 cuando aparece.""",
        
        "lesiones_previas": """Esguince de tobillo derecho hace 1 año jugando al pádel. Estuve 3 semanas con 
        férula y luego hice rehabilitación durante 2 meses. Ahora está recuperado al 100%, no tengo molestias. 
        Además, en 2020 tuve tendinitis en el hombro derecho por hacer demasiado press de hombro sin calentar bien. 
        Estuve 2 meses sin entrenar hombro y se me pasó. Ahora puedo entrenar hombro normal pero intento calentar 
        bien antes con rotaciones y face pulls.""",
        
        # Objetivos
        "objetivo_principal": "Quiero perder grasa corporal y definir el músculo. Mi objetivo es verme tonificada, especialmente en brazos y abdomen. También quiero mejorar mi fuerza general porque me siento débil.",
        
        "objetivo_secundario": "Mejorar mi composición corporal (menos grasa, más músculo), aumentar mi energía diaria, y sobre todo crear el hábito de entrenar de forma constante. Quiero un plan que me motive y que pueda seguir sin aburrirme.",
        
        "peso_objetivo": "62kg en 3-4 meses. Actualmente peso 68kg.",
        
        # Estilo de vida
        "horas_sueno": "7 horas entre semana (duermo de 00:00 a 07:00). Los fines de semana duermo 8-9 horas. A veces me cuesta dormir por estrés del trabajo.",
        
        "nivel_estres": "Medio-alto. Trabajo en una startup tecnológica con mucha presión y deadlines ajustados. Algunos días llego a casa muy cansada mentalmente.",
        
        "trabajo_sedentario": "Sí, 100% sedentario. Paso 8-9 horas al día sentada frente al ordenador. Solo me levanto para ir al baño o comer. Intento dar paseos en la hora de comer pero no siempre lo consigo.",
        
        "adherencia_anterior": "Baja. He empezado y dejado el gym muchas veces. Mi récord de constancia fue 4 meses seguidos con el entrenador personal. Después de eso nunca he sido constante más de 6-8 semanas. Creo que me falta motivación y un plan claro que seguir.",
        
        # Nutrición
        "alimentacion_actual": """Bastante desordenada. Desayuno café con tostadas. Como en el trabajo (menú 
        del día, no muy saludable). Ceno en casa, intento cocinar pero a veces pido comida a domicilio por 
        cansancio. Picoteo bastante entre horas (galletas, frutos secos, chocolate). Los fines de semana 
        como fuera con amigos. No cuento calorías ni macros, no tengo idea de cuánto como realmente.""",
        
        "suplementos": "Solo tomo whey protein después de entrenar, cuando me acuerdo. A veces tomo multivitamínico.",
        
        "intolerancias": "No tengo intolerancias alimentarias. Puedo comer de todo.",
        
        "preferencias": "Me gusta la comida mediterránea. No me gusta el pescado azul (salmón, atún) pero sí el pescado blanco. Me encanta la pasta y el arroz. No soy fan de las verduras crudas pero me gustan cocinadas."
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
