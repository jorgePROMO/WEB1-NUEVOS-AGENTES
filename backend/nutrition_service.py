"""
Sistema de Nutrición con 2 Agentes GPT-5
Usa los prompts EXACTOS proporcionados por el usuario
"""
import os
import json
from emergentintegrations.llm.chat import LlmChat, UserMessage
from dotenv import load_dotenv

load_dotenv()

# Obtener key de Emergent
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# PROMPT AGENTE 1 - EXACTO como lo proporcionó el usuario
AGENTE_1_PROMPT = """NUTRI AGENTE 1

Eres un nutricionista experto calculando macros y creando menús personalizados.

1-DATOS COMPLETOS DEL CLIENTE:
{client_data}
Genera EXACTAMENTE este formato:

2- CÁLCULO DE KCAL Y MACROS

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

3- MENÚ NUTRICIONAL SEMANAL (CON GRAMOS) 🥗

**LUNES**
🥣 Desayuno: [plato con gramos aproximados usando alimentos comunes]
🍛 Comida: [plato con gramos aproximados usando alimentos comunes]
🧀 Merienda: [plato con gramos aproximados usando alimentos comunes]
🌙 Cena: [plato con gramos aproximados usando alimentos comunes]

**MARTES**
[Continúa para toda la semana sin repetir platos, adaptando a horarios y preferencias del cliente]

4- LISTA DE LA COMPRA SEMANAL CON TODAS LAS CANTIDADES SEMANALES, LAS CUENTAS, LAS SUMAS Y DAS EL TOTAL

🥩 PROTEÍNAS:
- [alimento común]: [cantidad] kg/unidades

🥬 VERDURAS Y HORTALIZAS:
- [alimento común]: [cantidad] kg/unidades

🍞 CEREALES Y LEGUMBRES:
- [alimento común]: [cantidad] kg/unidades

🥑 GRASAS SALUDABLES:
- [alimento común]: [cantidad] ml/unidades

🍎 FRUTAS:
- [alimento común]: [cantidad] kg/unidades

🥛 LÁCTEOS:
- [alimento común]: [cantidad] L/unidades

Usa alimentos comunes y conocidos. Adapta a horarios reales del cliente, restricciones alimentarias y preferencias. Responde SOLO con este contenido."""

# PROMPT AGENTE 2 - EXACTO como lo proporcionó el usuario
AGENTE_2_PROMPT = """NUTRI AGENTE 2

AGENTE 2

Eres un verificador nutricional especializado. Tu misión es analizar el menú semanal y calcular con precisión los macronutrientes usando datos reales de alimentos.

DATOS DEL CLIENTE:
{client_data}

MENÚ A VERIFICAR (del Agente 2):
{menu_from_agent_1}

INSTRUCCIONES:
1. **EXTRAE** los macros objetivo que estableció el AGENTE 2 en su cálculo (busca la sección "Macronutrientes" o "Resumen visual")
2. Analiza cada día del menú con las cantidades especificadas
3. Calcula macronutrientes reales
4. Compara macros calculados vs macros establecidos por el AGENTE 2
5. Si hay desviaciones >±10g en algún macro, corrige las cantidades
6. Devuelve el menú completo (original si está bien, o corregido)

FORMATO DE RESPUESTA:

Devuelve el contenido COMPLETO del AGENTE 2 manteniendo:
- Mismo formato exacto
- Mismos apartados y títulos
- Mismos emojis y estructura
- SOLO corrige cantidades si es necesario
- NO añadas secciones de verificación
- NO menciones correcciones realizadas
-AÑADE LA PALABRA "VERIFICADO" AL TÍTULO

Responde ÚNICAMENTE con el menú corregido en el formato original.

NOTA IMPORTANTE: La base de datos puede contener algunos alimentos como agua que no son relevantes para la verificación. Usa valores nutricionales estándar conocidos para alimentos comunes como:
- Pollo: ~23g proteína/100g, ~165 kcal/100g
- Arroz cocido: ~28g carbohidratos/100g, ~130 kcal/100g
- Huevos: ~13g proteína/100g, ~155 kcal/100g
- etc.

Combina la base de datos con conocimiento nutricional estándar para verificaciones precisas.

TAMBIEN QUIERO QUE VERIFIQUES SI LOS TOTALES DE ALIMENTOS DE LA LISTA DE LA COMPRA CINCIDEN CON LOS TOTALES SEMANALES DE LA DIETA"""


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
        
        # Inicializar chat para Agente 1
        chat_agent_1 = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"nutrition_agent1_{client_data.get('email', 'unknown')}",
            system_message="Eres un experto nutricionista. Sigue las instrucciones al pie de la letra."
        ).with_model("openai", "gpt-4o")
        
        user_message_1 = UserMessage(text=agent_1_prompt)
        menu_from_agent_1 = await chat_agent_1.send_message(user_message_1)
        print("✅ AGENTE 1 completado")
        
        # AGENTE 2: Verificar y corregir
        print("🤖 Ejecutando AGENTE 2 (Verificador)...")
        agent_2_prompt = AGENTE_2_PROMPT.format(
            client_data=client_data_json,
            menu_from_agent_1=menu_from_agent_1
        )
        
        # Inicializar chat para Agente 2
        chat_agent_2 = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"nutrition_agent2_{client_data.get('email', 'unknown')}",
            system_message="Eres un verificador nutricional experto. Sigue las instrucciones al pie de la letra."
        ).with_model("openai", "gpt-4o")
        
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
