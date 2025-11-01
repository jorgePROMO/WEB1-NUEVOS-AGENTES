"""
Scheduler Service - Envío automático de informes GPT
Procesa prospectos pendientes y envía informes 2 horas después del cuestionario
"""
import asyncio
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from email_utils import send_email
from gpt_service import generate_prospect_report
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "test_database")

async def process_pending_prospects():
    """
    Procesa prospectos que necesitan recibir su informe
    Verifica si han pasado 2 horas desde su envío
    """
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    try:
        # Buscar prospectos que:
        # - No tienen informe generado (report_generated = False o no existe)
        # - Han enviado el cuestionario hace más de 2 horas
        two_hours_ago = datetime.now(timezone.utc) - timedelta(hours=2)
        
        prospects = await db.prospects.find({
            "$or": [
                {"report_generated": {"$exists": False}},
                {"report_generated": False}
            ],
            "submitted_at": {"$lte": two_hours_ago}
        }).to_list(length=None)
        
        print(f"✅ Encontrados {len(prospects)} prospectos pendientes de informe")
        
        for prospect in prospects:
            try:
                print(f"\n📧 Procesando: {prospect.get('nombre')} ({prospect.get('email')})")
                
                # Generar informe con GPT
                print("🤖 Generando informe con GPT-4o...")
                report_content = await generate_prospect_report(prospect)
                
                # Enviar email
                print("📨 Enviando informe por email...")
                subject = f"Tu Análisis Personalizado - {prospect.get('nombre')}"
                
                # Convertir markdown a HTML simple
                html_report = report_content.replace("\n\n", "<br><br>").replace("\n", "<br>")
                html_report = html_report.replace("**", "<strong>").replace("**", "</strong>")
                
                email_body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <div style="text-align: center; margin-bottom: 30px;">
                            <h2 style="color: #3B82F6;">Jorge Calcerrada</h2>
                            <p style="color: #666;">Entrenador Personal</p>
                        </div>
                        
                        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
                            {html_report}
                        </div>
                        
                        <div style="margin-top: 30px; text-align: center;">
                            <p>¿Listo para empezar tu transformación?</p>
                            <a href="https://wa.me/{prospect.get('whatsapp').replace('+', '')}" 
                               style="display: inline-block; background: #10B981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                                Contáctame por WhatsApp
                            </a>
                        </div>
                        
                        <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #666; font-size: 12px;">
                            <p>Jorge Calcerrada - Entrenamiento Personal<br>
                            <a href="https://crm-fusion-2.preview.emergentagent.com">crmmgr.preview.emergentagent.com</a></p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                send_email(
                    to_email=prospect.get('email'),
                    subject=subject,
                    body=email_body
                )
                
                print("✅ Email enviado correctamente")
                
                # Actualizar prospect en la base de datos
                now = datetime.now(timezone.utc)
                await db.prospects.update_one(
                    {"_id": prospect.get("_id")},
                    {
                        "$set": {
                            "report_generated": True,
                            "report_sent_at": now,
                            "report_content": report_content,
                            "stage_name": "Diagnóstico OK"
                        }
                    }
                )
                
                print(f"✅ Prospecto actualizado: Estado → 'Diagnóstico OK'")
                
                # También enviar copia al admin
                admin_email = "ecjtrainer@gmail.com"
                admin_subject = f"[ADMIN] Informe enviado a {prospect.get('nombre')}"
                admin_body = f"""
                <html>
                <body>
                    <h3>Informe enviado al prospecto</h3>
                    <p><strong>Nombre:</strong> {prospect.get('nombre')}</p>
                    <p><strong>Email:</strong> {prospect.get('email')}</p>
                    <p><strong>WhatsApp:</strong> {prospect.get('whatsapp')}</p>
                    <p><strong>Enviado:</strong> {now.strftime('%d/%m/%Y %H:%M')}</p>
                    <hr>
                    {html_report}
                </body>
                </html>
                """
                
                send_email(
                    to_email=admin_email,
                    subject=admin_subject,
                    body=admin_body
                )
                
                print(f"✅ Copia enviada al admin\n")
                
            except Exception as e:
                print(f"❌ Error procesando {prospect.get('email')}: {e}")
                continue
        
        print(f"\n✅ Proceso completado: {len(prospects)} informes procesados")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    print("🚀 Iniciando procesamiento de informes...")
    asyncio.run(process_pending_prospects())
