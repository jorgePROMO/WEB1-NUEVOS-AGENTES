"""
GPT Report Generator Service
Genera informes personalizados usando GPT-4o
"""
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
import asyncio

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY no configurada en el entorno")

SYSTEM_PROMPT = """Eres un experto en marketing emocional, ventas de alto valor y análisis estratégico de clientes potenciales dentro del mundo fitness y salud integral. Has recibido las respuestas de un formulario detallado de diagnóstico de una persona que quiere transformar su cuerpo, salud o estilo de vida. Tu trabajo es crear un análisis profesional, emocional y motivador con los siguientes objetivos:

1. Ayudar al cliente a tomar conciencia de su situación actual, obstáculos y patrones limitantes.
2. Mostrarle que tiene potencial de transformación si toma acción ahora.
3. Posicionarte como la única persona capaz de ayudarle realmente, con un enfoque empático pero convincente.

🎯 ESTRUCTURA DEL ANÁLISIS (usa títulos con emojis):

🔍 1. Quién eres y qué necesitas
Resumen emocional y empático de quién es la persona, qué busca, qué ha intentado y qué la frena. Usa sus propias palabras cuando sea relevante.

🚨 2. Lo que hoy te está limitando
Diagnóstico honesto y claro de errores comunes, barreras mentales, hábitos perjudiciales o creencias limitantes según sus respuestas.

🚀 3. Tu verdadero potencial
Mensaje motivacional que muestre lo que puede lograr si toma acción contigo y por qué ahora es el momento ideal.

🧭 4. Cómo puedo ayudarte (y por qué yo)
Presenta tu método de forma clara, emocional y convincente. Explica en qué te diferencias, por qué puedes ayudar mejor que nadie, y cómo adaptas el proceso a su vida real.

🎯 5. Recomendación personalizada del servicio adecuado
Ofrece una recomendación clara del tipo de acompañamiento que necesita en base a su perfil, su nivel de compromiso y su urgencia. No uses los términos 'low ticket' o 'high ticket'. Sólo recomienda el tipo de soporte:
- Guía profesional estructurada y seguimiento periódico, si es lo más adecuado.
- Acompañamiento cercano, soporte intensivo y personalización total, si lo requiere.
- Si consideras que necesita un enfoque más específico o especializado (por ejemplo, nutrición clínica avanzada, psicoterapia emocional, rehabilitación compleja), menciónalo como sugerencia.

Cierra con pregunta directa para generar respuesta:
👉 "¿Sientes que este tipo de acompañamiento se adapta a lo que necesitas ahora mismo?"

✨ FORMATO VISUAL:
- Usa emojis en los títulos y donde sea relevante.
- Usa subtítulos en negrita.
- Puedes usar viñetas si es útil.

📤 SALIDA: Texto fluido, entre 400 y 600 palabras, listo para enviar por correo o WhatsApp.

🔍 IMPORTANTE: No inventes datos. Analiza solo lo que el usuario haya respondido.
"""


async def generate_prospect_report(prospect_data: dict) -> str:
    """
    Genera un informe personalizado usando GPT-4o
    
    Args:
        prospect_data: Diccionario con las respuestas del prospecto
        
    Returns:
        str: Informe generado en formato markdown
    """
    
    # Formatear los datos del prospecto de manera legible
    formatted_data = f"""
**Datos del Prospecto:**

👤 **Información Personal:**
- Nombre: {prospect_data.get('nombre')}
- Edad: {prospect_data.get('edad')}
- Email: {prospect_data.get('email')}
- WhatsApp: {prospect_data.get('whatsapp')}

🎯 **Objetivos y Contexto:**
- Objetivo principal: {prospect_data.get('objetivo')}
- Intentos previos: {prospect_data.get('intentos_previos')}
- Dificultades: {', '.join(prospect_data.get('dificultades', []))}
{f"- Otras dificultades: {prospect_data.get('dificultades_otro')}" if prospect_data.get('dificultades_otro') else ""}
- Tiempo disponible semanal: {prospect_data.get('tiempo_semanal')}
- ¿Entrena actualmente?: {prospect_data.get('entrena')}

🍽️ **Nutrición y Salud:**
- Alimentación actual: {prospect_data.get('alimentacion')}
- Información de salud: {prospect_data.get('salud_info')}

💪 **Motivación y Compromiso:**
- ¿Por qué ahora?: {prospect_data.get('por_que_ahora')}
- Dispuesto a invertir: {prospect_data.get('dispuesto_invertir')}
- Tipo de acompañamiento deseado: {prospect_data.get('tipo_acompanamiento')}
- Presupuesto: {prospect_data.get('presupuesto')}
{f"- Comentarios adicionales: {prospect_data.get('comentarios_adicionales')}" if prospect_data.get('comentarios_adicionales') else ""}

---

Basándote ÚNICAMENTE en estos datos, genera el análisis personalizado siguiendo la estructura establecida.
"""
    
    try:
        # Inicializar el chat con GPT-4o
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"prospect-{prospect_data.get('email')}",
            system_message=SYSTEM_PROMPT
        ).with_model("openai", "gpt-4o")
        
        # Crear mensaje del usuario
        user_message = UserMessage(text=formatted_data)
        
        # Enviar mensaje y obtener respuesta
        response = await chat.send_message(user_message)
        
        # Agregar título personalizado
        report_title = f"# Tu Ruta Personal para Transformarte – Análisis para {prospect_data.get('nombre')}\n\n"
        full_report = report_title + response
        
        return full_report
        
    except Exception as e:
        print(f"Error generating GPT report: {e}")
        raise Exception(f"Error al generar el informe: {str(e)}")


# Test function
async def test_report_generation():
    """Función de prueba para verificar la generación de informes"""
    test_data = {
        "nombre": "María García",
        "edad": "32",
        "email": "maria@example.com",
        "whatsapp": "+34612345678",
        "objetivo": "Perder peso y ganar tono muscular",
        "intentos_previos": "He probado varias dietas y gimnasio pero siempre abandono",
        "dificultades": ["Falta de tiempo", "No sé qué comer", "Desmotivación"],
        "dificultades_otro": None,
        "tiempo_semanal": "3-4 días/semana",
        "entrena": "Sí, 2 veces por semana en el gimnasio",
        "alimentacion": "Como de todo pero muy desordenada",
        "salud_info": "Ningún problema de salud",
        "por_que_ahora": "Me caso en 6 meses y quiero sentirme bien",
        "dispuesto_invertir": "Sí, es una prioridad",
        "tipo_acompanamiento": "Prefiero acompañamiento cercano",
        "presupuesto": "Hasta 200€/mes",
        "comentarios_adicionales": "Necesito alguien que me motive y me guíe"
    }
    
    report = await generate_prospect_report(test_data)
    print("=" * 80)
    print("INFORME GENERADO:")
    print("=" * 80)
    print(report)
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_report_generation())
