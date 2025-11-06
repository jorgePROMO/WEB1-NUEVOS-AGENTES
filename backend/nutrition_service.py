"""
Sistema de Nutrición con 2 Agentes GPT-5
Usa los prompts EXACTOS proporcionados por el usuario
"""
import os
import sys
import json
from pathlib import Path
from emergentintegrations.llm.chat import LlmChat, UserMessage

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
    print(f"✅ OpenAI Key cargada: {OPENAI_API_KEY[:20]}...")

# PROMPT AGENTE 1
AGENTE_1_PROMPT = """Eres un nutricionista experto calculando macros y creando menús personalizados.

DATOS DEL CLIENTE:
{client_data}

Genera EXACTAMENTE este formato:

**PLAN DE NUTRICIÓN PERSONALIZADO**

Hola [Nombre del cliente],

Gracias por tu paciencia. Mi equipo ha estado trabajando en tu plan de nutrición personalizado para que alcances tu objetivo de [objetivo del cliente], y yo personalmente he supervisado cada detalle para asegurarnos de que todo esté perfectamente ajustado a tus necesidades.

He calculado que necesitas aproximadamente [cantidad] kcal diarias, distribuidas en: [X]g de proteínas, [X]g de carbohidratos y [X]g de grasas saludables. A continuación encontrarás tu menú semanal diseñado específicamente para cumplir con estos requerimientos:

---

**TU MENÚ SEMANAL** 🥗

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
- Mismos apartados y títulos
- Mismos emojis y estructura
- SOLO corrige cantidades si es necesario
- NO añadas secciones de verificación
- NO menciones correcciones realizadas
- NO añadas palabras como "VERIFICADO", "AGENTE", "REVISADO" en ninguna parte del documento
- NO incluyas frases de cierre como "¡Este es el plan..." o "¡Espero que disfrutes..." al final
- NO incluyas totales o subtotales en la lista de compra
- NO añadas información de cliente, fecha u objetivo después del saludo inicial

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
        
        # Inicializar chat para Agente 1 con GPT-4o mini
        chat_agent_1 = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=f"nutrition_agent1_{client_data.get('email', 'unknown')}",
            system_message="Eres un experto nutricionista. Sigue las instrucciones al pie de la letra."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message_1 = UserMessage(text=agent_1_prompt)
        menu_from_agent_1 = await chat_agent_1.send_message(user_message_1)
        print("✅ AGENTE 1 completado")
        
        # AGENTE 2: Verificar y corregir
        print("🤖 Ejecutando AGENTE 2 (Verificador)...")
        agent_2_prompt = AGENTE_2_PROMPT.format(
            client_data=client_data_json,
            menu_from_agent_1=menu_from_agent_1
        )
        
        # Inicializar chat para Agente 2 con GPT-4o mini
        chat_agent_2 = LlmChat(
            api_key=OPENAI_API_KEY,
            session_id=f"nutrition_agent2_{client_data.get('email', 'unknown')}",
            system_message="Eres un verificador nutricional experto. Sigue las instrucciones al pie de la letra."
        ).with_model("openai", "gpt-4o-mini")
        
        user_message_2 = UserMessage(text=agent_2_prompt)
        final_plan = await chat_agent_2.send_message(user_message_2)
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


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_nutrition_service())
