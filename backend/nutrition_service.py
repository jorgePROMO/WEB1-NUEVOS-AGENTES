"""
Sistema de Nutrición con 2 Agentes GPT-5
Usa los prompts EXACTOS proporcionados por el usuario
"""
import os
import sys
import json
from pathlib import Path
from openai import AsyncOpenAI

# Cargar variables de entorno manualmente
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value.strip('"').strip("'")

# Obtener key de OpenAI (prioritario sobre Emergent)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

if not OPENAI_API_KEY:
    print("❌ ERROR: OPENAI_API_KEY no encontrada")
    sys.exit(1)
else:
    print(f"✅ OpenAI Key cargada correctamente")

# PROMPT AGENTE 1
AGENTE_1_PROMPT = """Eres un nutricionista experto calculando macros y creando menús personalizados.

⚠️ INSTRUCCIÓN CRÍTICA - LEER PRIMERO:
NUNCA incluyas alimentos que el cliente haya indicado que NO LE GUSTAN o que tenga INTOLERANCIAS/ALERGIAS.
Revisa CUIDADOSAMENTE las siguientes secciones del cuestionario:
- alimentos_no_gustan
- intolerancias
- alergias
- preferencias alimentarias
Si el cliente menciona algún alimento que no le gusta, BAJO NINGUNA CIRCUNSTANCIA lo incluyas en el plan.

DATOS DEL CLIENTE:
{client_data}

Genera EXACTAMENTE este formato:

PLAN DE NUTRICIÓN PERSONALIZADO

Hola [Nombre del cliente],

Gracias por tu paciencia. Mi equipo ha estado trabajando en tu plan de nutrición personalizado para que alcances tu objetivo de [objetivo del cliente], y yo personalmente he supervisado cada detalle para asegurarnos de que todo esté perfectamente ajustado a tus necesidades.

---

CÁLCULO DE KCAL Y MACROS

📢 Fórmula Mifflin–St Jeor:
- TMB ≈ [calcula según datos reales] kcal/día
- Factor de actividad: ×[factor según actividad] ≈ [resultado] kcal → TDEE ≈ [total] kcal/día
🎯 Objetivo: [déficit/superávit según objetivo] ≈ [porcentaje]%, para [objetivo específico].

📊 Macronutrientes:
CALORÍAS TOTALES | PROTEÍNA (g / %) | CARBOHIDRATOS (g / %) | GRASAS (g / %)
[total] kcal | [gramos] g / [%] % | [gramos] g / [%] % | [gramos] g / [%] %

✅ Resumen visual:
🔥 Objetivo: [objetivo específico]
✅ Calorías objetivo: [total] kcal/día
🥩 Proteínas: [g] g — 🥑 Grasas: [g] g — 🍞 Carbohidratos: [g] g

MENÚ NUTRICIONAL SEMANAL (CON GRAMOS) 🥗

**LUNES**
🥣 Desayuno: [plato con gramos exactos de cada ingrediente]
🍛 Comida: [plato con gramos exactos de cada ingrediente]
🧀 Merienda: [plato con gramos exactos de cada ingrediente]
🌙 Cena: [plato con gramos exactos de cada ingrediente]

**MARTES**
[Repite el formato para cada día de la semana (Martes a Domingo)]
[Varía los platos, no repitas el mismo menú]
[Usa alimentos comunes y conocidos del supermercado]
[Ajusta al nivel de actividad, horarios y preferencias del cliente]

**MIÉRCOLES**
[...]

**JUEVES**
[...]

**VIERNES**
[...]

**SÁBADO**
[...]

**DOMINGO**
[...]

LISTA DE LA COMPRA SEMANAL

🥩 PROTEÍNAS:
- [alimento]: [cantidad total semanal en kg o unidades]
- [alimento]: [cantidad total semanal en kg o unidades]
[Incluye: huevos, carnes, pescados, lácteos proteicos]

🥬 VERDURAS Y HORTALIZAS:
- [alimento]: [cantidad en kg o unidades]
- [alimento]: [cantidad en kg o unidades]
[Incluye todas las verduras del menú semanal]

🍞 CEREALES Y LEGUMBRES:
- [alimento]: [cantidad en kg]
- [alimento]: [cantidad en kg]
[Incluye: avena, arroz, pasta, pan, legumbres]

🥑 GRASAS SALUDABLES:
- [alimento]: [cantidad en ml o gramos]
- [alimento]: [cantidad en gramos]
[Incluye: aceites, frutos secos, aguacate, semillas]

🍎 FRUTAS:
- [alimento]: [cantidad en kg o unidades]
- [alimento]: [cantidad en kg o unidades]

🥛 LÁCTEOS:
- [alimento]: [cantidad en L o unidades]
- [alimento]: [cantidad en unidades]

IMPORTANTE: 
- USA GRAMOS ESPECÍFICOS en cada comida, no aproximaciones
- Los macros del menú semanal DEBEN coincidir con los calculados arriba
- Calcula las cantidades de cada alimento para que sumen los macros objetivo
- NO incluyas frases de cierre ni totales finales en la lista de compra
- Responde SOLO con este contenido, nada más"""

# PROMPT AGENTE 2 - Verificación nutricional
AGENTE_2_PROMPT = """Eres un verificador nutricional especializado. Tu misión es analizar el menú semanal y calcular con precisión los macronutrientes usando datos reales de alimentos.

⚠️ INSTRUCCIÓN CRÍTICA - VERIFICACIÓN DE PREFERENCIAS:
ANTES de aprobar el plan, verifica que NO se hayan incluido alimentos que el cliente indicó que NO LE GUSTAN o que tenga INTOLERANCIAS/ALERGIAS.
Si encuentras algún alimento prohibido, REEMPLÁZALO inmediatamente por alternativas similares que el cliente SÍ pueda comer.
Revisa especialmente: alimentos_no_gustan, intolerancias, alergias del cuestionario.

DATOS DEL CLIENTE:
{client_data}

MENÚ A VERIFICAR (del primer agente):
{menu_from_agent_1}

INSTRUCCIONES:
1. **EXTRAE** los macros objetivo que estableció el primer agente en su cálculo (busca la sección "Macronutrientes" o "Resumen visual")
2. Analiza CADA DÍA del menú con las cantidades especificadas
3. Calcula los macronutrientes reales usando valores nutricionales estándar:
   - Pollo: ~23g proteína/100g, ~165 kcal/100g
   - Arroz cocido: ~28g carbohidratos/100g, ~130 kcal/100g
   - Huevos: ~13g proteína/100g, ~155 kcal/100g
   - Salmón: ~20g proteína, ~13g grasas/100g
   - Aceite de oliva: ~100% grasas, ~900 kcal/100ml
   - Aguacate: ~15g grasas/100g
   - Avena: ~13g proteína, ~60g carbohidratos/100g
   [Usa valores nutricionales estándar para todos los alimentos]

4. Compara macros calculados vs macros objetivo del primer agente
5. Si hay desviaciones >±10g en algún macro:
   - Ajusta las cantidades de los alimentos en el menú
   - Mantén la estructura y los platos originales
   - Solo cambia los gramos de los ingredientes

6. Verifica que las cantidades de la lista de compra coincidan con los totales semanales del menú

FORMATO DE RESPUESTA:

Devuelve el contenido COMPLETO del plan manteniendo:
- Mismo formato exacto del primer agente
- Saludo personalizado al inicio (Hola [nombre], Gracias por tu paciencia, etc.)
- MANTÉN la sección completa "CÁLCULO DE KCAL Y MACROS" con todas las fórmulas, TMB, TDEE y tablas
- Mismos apartados y títulos
- Mismos emojis y estructura
- SOLO corrige cantidades en el menú si es necesario
- NO añadas secciones de verificación
- NO menciones correcciones realizadas
- NO añadas palabras como "VERIFICADO", "AGENTE", "REVISADO", "Plan Verificado" en ninguna parte del documento
- NO incluyas frases de cierre como "¡Este es el plan..." o "¡Espero que disfrutes..." al final
- NO incluyas totales o subtotales en la lista de compra

Responde ÚNICAMENTE con el plan de nutrición corregido (si fue necesario) en el formato original."""


async def generate_nutrition_plan(client_data: dict) -> dict:
    """
    Genera plan nutricional usando los 2 agentes en secuencia
    
    Args:
        client_data: Diccionario con todas las respuestas del cuestionario
    
    Returns:
        dict con el plan final verificado
    """
    
    try:
        # Formatear datos del cliente como JSON bonito
        client_data_json = json.dumps(client_data, indent=2, ensure_ascii=False)
        
        # AGENTE 1: Generar menú inicial
        print("🤖 Ejecutando AGENTE 1 (Nutricionista)...")
        agent_1_prompt = AGENTE_1_PROMPT.format(client_data=client_data_json)
        
        # Si hay contexto adicional del seguimiento, agregarlo
        if client_data.get('context_adicional'):
            agent_1_prompt += f"\n\n{client_data['context_adicional']}"
        
        # Inicializar cliente de OpenAI
        client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # AGENTE 1: Llamar a OpenAI GPT-4o-mini
        response_1 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un experto nutricionista. Sigue las instrucciones al pie de la letra."
                },
                {
                    "role": "user",
                    "content": agent_1_prompt
                }
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        menu_from_agent_1 = response_1.choices[0].message.content
        print("✅ AGENTE 1 completado")
        
        # AGENTE 2: Verificar y corregir
        print("🤖 Ejecutando AGENTE 2 (Verificador)...")
        agent_2_prompt = AGENTE_2_PROMPT.format(
            client_data=client_data_json,
            menu_from_agent_1=menu_from_agent_1
        )
        
        # AGENTE 2: Llamar a OpenAI GPT-4o-mini
        response_2 = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "Eres un verificador nutricional experto. Sigue las instrucciones al pie de la letra."
                },
                {
                    "role": "user",
                    "content": agent_2_prompt
                }
            ],
            temperature=0.7,
            max_tokens=3000
        )
        
        final_plan = response_2.choices[0].message.content
        print("✅ AGENTE 2 completado - Plan VERIFICADO")
        
        return {
            "success": True,
            "plan_inicial": menu_from_agent_1,
            "plan_verificado": final_plan,
            "client_data": client_data
        }
        
    except Exception as e:
        print(f"❌ Error en generación de plan: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Función de prueba
async def test_nutrition_service():
    """Prueba el servicio con datos de ejemplo"""
    test_data = {
        "nombre": "Juan Pérez",
        "edad": 30,
        "peso": 80,
        "altura": 175,
        "sexo": "HOMBRE",
        "objetivo_fisico": "perder grasa",
        "actividad_fisica": "Ejercicio moderado (3-5 días/semana)",
        "trabajo_fisico": "sedentario",
        "alergias": "Ninguna",
        "comidas_dia": "5 comidas"
    }
    
    result = await generate_nutrition_plan(test_data)
    
    if result["success"]:
        print("\n📊 PLAN GENERADO EXITOSAMENTE:")
        print("\n" + "="*80)
        print(result["plan_verificado"])
        print("="*80)
    else:
        print(f"\n❌ Error: {result['error']}")




async def generate_nutrition_plan_with_context(questionnaire: dict, follow_up_analysis: str, follow_up_data: dict, previous_plan: dict = None) -> dict:
    """
    Genera un nuevo plan de nutrición considerando el análisis del seguimiento mensual
    
    Args:
        questionnaire: Cuestionario inicial del cliente
        follow_up_analysis: Análisis generado por IA del seguimiento
        follow_up_data: Datos del seguimiento (mediciones, adherencia, etc.)
        previous_plan: Plan de nutrición anterior para referencia
    
    Returns:
        dict: Resultado con success, plan_verificado, plan_inicial
    """
    
    # Extraer datos actualizados del seguimiento
    current_measurements = {}
    if follow_up_data.get('measurements'):
        measurements = follow_up_data['measurements']
        current_measurements = {
            'peso': measurements.get('peso', questionnaire.get('peso_actual')),
            'grasa_corporal': measurements.get('grasa_corporal'),
            'masa_muscular': measurements.get('masa_muscular')
        }
    
    # Preparar datos del cliente con información actualizada
    client_data_parts = []
    client_data_parts.append(f"Nombre: {questionnaire.get('nombre', 'Cliente')}")
    client_data_parts.append(f"Edad: {questionnaire.get('edad', 'N/A')} años")
    client_data_parts.append(f"Altura: {questionnaire.get('altura', 'N/A')} cm")
    
    # Usar peso actualizado si existe
    peso_actual = current_measurements.get('peso') or questionnaire.get('peso_actual', 'N/A')
    client_data_parts.append(f"Peso actual: {peso_actual} kg")
    
    if current_measurements.get('grasa_corporal'):
        client_data_parts.append(f"Grasa corporal actual: {current_measurements['grasa_corporal']}%")
    if current_measurements.get('masa_muscular'):
        client_data_parts.append(f"Masa muscular actual: {current_measurements['masa_muscular']} kg")
    
    client_data_parts.append(f"Sexo: {questionnaire.get('sexo', 'N/A')}")
    client_data_parts.append(f"Objetivo: {questionnaire.get('objetivo_principal', 'N/A')}")
    client_data_parts.append(f"Nivel de actividad: {questionnaire.get('nivel_actividad', 'N/A')}")
    client_data_parts.append(f"Trabajo físico: {questionnaire.get('trabajo_fisico', 'N/A')}")
    client_data_parts.append(f"Alergias: {questionnaire.get('alergias_intolerancias', 'Ninguna')}")
    client_data_parts.append(f"Preferencia de comidas: {questionnaire.get('comidas_dia', 'N/A')}")
    
    # Agregar contexto del seguimiento
    client_data_parts.append(f"\n**CONTEXTO DEL SEGUIMIENTO (después de {follow_up_data.get('days_since_last_plan', 0)} días):**")
    
    adherence = follow_up_data.get('adherence', {})
    client_data_parts.append(f"- Adherencia al entrenamiento: {adherence.get('constancia_entrenamiento', 'N/A')}")
    client_data_parts.append(f"- Adherencia a la alimentación: {adherence.get('seguimiento_alimentacion', 'N/A')}")
    
    changes = follow_up_data.get('changes_perceived', {})
    client_data_parts.append(f"- Cambios corporales percibidos: {changes.get('cambios_corporales', 'N/A')}")
    client_data_parts.append(f"- Cambios en fuerza/rendimiento: {changes.get('fuerza_rendimiento', 'N/A')}")
    
    feedback = follow_up_data.get('feedback', {})
    client_data_parts.append(f"- Objetivo para próximo mes: {feedback.get('objetivo_proximo_mes', 'N/A')}")
    client_data_parts.append(f"- Cambios deseados: {feedback.get('cambios_deseados', 'N/A')}")
    
    # Agregar plan anterior si existe
    if previous_plan:
        client_data_parts.append(f"\n**PLAN DE NUTRICIÓN ANTERIOR:**")
        client_data_parts.append(f"Generado: {previous_plan.get('generated_at', 'N/A')}")
        client_data_parts.append(f"Contenido: {previous_plan.get('plan_verificado', 'N/A')[:500]}...")  # Primeros 500 caracteres
    
    client_data_parts.append(f"\n**ANÁLISIS PREVIO DEL ENTRENADOR:**\n{follow_up_analysis}")
    
    client_data = "\n".join(client_data_parts)
    
    # Contexto adicional con TODA la información
    context_adicional = f"""
**IMPORTANTE - GENERAR NUEVO PLAN BASADO EN SEGUIMIENTO:**

Tienes acceso a:
1. Cuestionario inicial del cliente
2. Plan de nutrición anterior (usado durante {follow_up_data.get('days_since_last_plan', 0)} días)
3. Seguimiento mensual con mediciones actuales
4. Análisis del entrenador

{follow_up_analysis}

**INSTRUCCIONES:**
- Usa el MISMO FORMATO que el plan anterior
- Ajusta calorías y macros según las recomendaciones del análisis
- Considera los cambios corporales y adherencia del cliente
- Mantén los alimentos que funcionaron bien, cambia los que no
- Genera un plan personalizado para el próximo mes
"""
    
    # Generar el plan usando la función existente con el contexto adicional
    result = await generate_nutrition_plan({
        'nombre': questionnaire.get('nombre', 'Cliente'),
        'edad': questionnaire.get('edad'),
        'altura': questionnaire.get('altura'),
        'peso_actual': peso_actual,
        'sexo': questionnaire.get('sexo'),
        'objetivo_principal': questionnaire.get('objetivo_principal'),
        'nivel_actividad': questionnaire.get('nivel_actividad'),
        'trabajo_fisico': questionnaire.get('trabajo_fisico'),
        'alergias_intolerancias': questionnaire.get('alergias_intolerancias', 'Ninguna'),
        'comidas_dia': questionnaire.get('comidas_dia'),
        'context_adicional': context_adicional
    })
    
    return result


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_nutrition_service())
