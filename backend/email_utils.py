import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str, text_body: str = None):
    """
    Send email using Gmail SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_body: HTML content of the email
        text_body: Plain text fallback (optional)
    """
    smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    smtp_user = os.environ.get('SMTP_USER', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    smtp_from_name = os.environ.get('SMTP_FROM_NAME', 'Jorge Calcerrada')
    
    # Check if SMTP credentials are configured
    if not smtp_user or not smtp_password:
        logger.warning("SMTP credentials not configured. Email not sent.")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{smtp_from_name} <{smtp_user}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add plain text and HTML parts
        if text_body:
            text_part = MIMEText(text_body, 'plain')
            msg.attach(text_part)
        
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Connect to SMTP server and send
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_session_created_email(user_email: str, user_name: str, session_date: datetime, session_title: str):
    """Send email notification when a new session is created"""
    subject = f"Nueva Sesión Programada - {session_title}"
    
    formatted_date = session_date.strftime("%d de %B de %Y a las %H:%M")
    
    # Get frontend URL from environment
    frontend_url = os.environ.get('FRONTEND_URL', 'https://coach-connect-47.preview.emergentagent.com')
    dashboard_url = f"{frontend_url}/dashboard"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3B82F6; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
            .session-info {{ background-color: white; padding: 20px; border-left: 4px solid #3B82F6; margin: 20px 0; }}
            .button {{ display: inline-block; padding: 14px 28px; background-color: #3B82F6; color: white !important; text-decoration: none; border-radius: 5px; margin-top: 20px; font-weight: bold; }}
            .button:hover {{ background-color: #2563EB; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✓ Nueva Sesión Programada</h1>
            </div>
            <div class="content">
                <p>Hola {user_name},</p>
                <p>Se ha programado una nueva sesión para ti:</p>
                
                <div class="session-info">
                    <p style="margin: 5px 0;"><strong>📋 Título:</strong> {session_title}</p>
                    <p style="margin: 5px 0;"><strong>📅 Fecha y Hora:</strong> {formatted_date}</p>
                </div>
                
                <p>Para ver todos los detalles de tu sesión y confirmarla, haz clic en el siguiente botón:</p>
                
                <div style="text-align: center;">
                    <a href="{dashboard_url}" class="button">Ver Mi Calendario y Confirmar</a>
                </div>
                
                <p style="margin-top: 20px;">También puedes reagendar la sesión si el horario no te viene bien.</p>
                
                <p>¡Nos vemos pronto!</p>
                <p>Saludos,<br><strong>Jorge Calcerrada</strong></p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                <p>Si tienes alguna duda, accede a tu panel de usuario.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Hola {user_name},
    
    Se ha programado una nueva sesión para ti:
    
    Título: {session_title}
    Fecha y Hora: {formatted_date}
    
    Para ver los detalles y confirmar tu sesión, accede a tu panel:
    {dashboard_url}
    
    También puedes reagendar la sesión si el horario no te viene bien.
    
    ¡Nos vemos pronto!
    
    Saludos,
    Jorge Calcerrada
    
    ---
    Este es un correo automático, por favor no respondas a este mensaje.
    """
    
    return send_email(user_email, subject, html_body, text_body)


def send_session_rescheduled_email(user_email: str, user_name: str, new_date: datetime, session_title: str):
    """Send email notification when a session is rescheduled"""
    subject = f"Sesión Reagendada - {session_title}"
    
    formatted_date = new_date.strftime("%d de %B de %Y a las %H:%M")
    
    # Get frontend URL from environment
    frontend_url = os.environ.get('FRONTEND_URL', 'https://coach-connect-47.preview.emergentagent.com')
    dashboard_url = f"{frontend_url}/dashboard"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #F59E0B; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
            .session-info {{ background-color: white; padding: 20px; border-left: 4px solid #F59E0B; margin: 20px 0; }}
            .button {{ display: inline-block; padding: 14px 28px; background-color: #F59E0B; color: white !important; text-decoration: none; border-radius: 5px; margin-top: 20px; font-weight: bold; }}
            .button:hover {{ background-color: #D97706; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔄 Sesión Reagendada</h1>
            </div>
            <div class="content">
                <p>Hola {user_name},</p>
                <p>Tu sesión ha sido reagendada exitosamente:</p>
                
                <div class="session-info">
                    <p style="margin: 5px 0;"><strong>📋 Título:</strong> {session_title}</p>
                    <p style="margin: 5px 0;"><strong>📅 Nueva Fecha y Hora:</strong> {formatted_date}</p>
                </div>
                
                <p>Para ver todos los detalles de tu sesión actualizada, haz clic en el siguiente botón:</p>
                
                <div style="text-align: center;">
                    <a href="{dashboard_url}" class="button">Ver Mi Calendario</a>
                </div>
                
                <p style="margin-top: 20px;">Si tienes alguna duda o necesitas hacer cambios adicionales, puedes acceder a tu panel de usuario.</p>
                
                <p>¡Nos vemos pronto!</p>
                <p>Saludos,<br><strong>Jorge Calcerrada</strong></p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                <p>Si tienes alguna duda, accede a tu panel de usuario.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Hola {user_name},
    
    Tu sesión ha sido reagendada exitosamente:
    
    Título: {session_title}
    Nueva Fecha y Hora: {formatted_date}
    
    Para ver los detalles actualizados de tu sesión, accede a tu panel:
    {dashboard_url}
    
    Si tienes alguna duda o necesitas hacer cambios adicionales, no dudes en contactarnos.
    
    ¡Nos vemos pronto!
    
    Saludos,
    Jorge Calcerrada
    
    ---
    Este es un correo automático, por favor no respondas a este mensaje.
    """
    
    return send_email(user_email, subject, html_body, text_body)



# ==================== ADMIN NOTIFICATION EMAILS ====================

def send_admin_session_created_email(client_name: str, client_email: str, session_date: datetime, session_title: str):
    """Send email notification to admin when a new session is created"""
    admin_email = os.environ.get('SMTP_USER', 'ecjtrainer@gmail.com')
    subject = f"Nueva Sesión Creada - {client_name}"
    
    formatted_date = session_date.strftime("%d de %B de %Y a las %H:%M")
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #10B981; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
            .session-info {{ background-color: white; padding: 20px; border-left: 4px solid #10B981; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✓ Nueva Sesión Creada</h1>
            </div>
            <div class="content">
                <p>Hola Jorge,</p>
                <p>Se ha creado una nueva sesión con los siguientes detalles:</p>
                
                <div class="session-info">
                    <p style="margin: 5px 0;"><strong>👤 Cliente:</strong> {client_name}</p>
                    <p style="margin: 5px 0;"><strong>📧 Email:</strong> {client_email}</p>
                    <p style="margin: 5px 0;"><strong>📋 Título:</strong> {session_title}</p>
                    <p style="margin: 5px 0;"><strong>📅 Fecha y Hora:</strong> {formatted_date}</p>
                </div>
                
                <p>El cliente ha sido notificado por email.</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático de notificación.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Nueva Sesión Creada
    
    Cliente: {client_name}
    Email: {client_email}
    Título: {session_title}
    Fecha y Hora: {formatted_date}
    
    El cliente ha sido notificado por email.
    
    ---
    Este es un correo automático de notificación.
    """
    
    return send_email(admin_email, subject, html_body, text_body)


def send_admin_session_rescheduled_email(client_name: str, client_email: str, old_date: datetime, new_date: datetime, session_title: str):
    """Send email notification to admin when a session is rescheduled"""
    admin_email = os.environ.get('SMTP_USER', 'ecjtrainer@gmail.com')
    subject = f"Sesión Reagendada - {client_name}"
    
    formatted_old_date = old_date.strftime("%d de %B de %Y a las %H:%M")
    formatted_new_date = new_date.strftime("%d de %B de %Y a las %H:%M")
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #F59E0B; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
            .session-info {{ background-color: white; padding: 20px; border-left: 4px solid #F59E0B; margin: 20px 0; }}
            .date-change {{ background-color: #FEF3C7; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔄 Sesión Reagendada</h1>
            </div>
            <div class="content">
                <p>Hola Jorge,</p>
                <p>Una sesión ha sido reagendada:</p>
                
                <div class="session-info">
                    <p style="margin: 5px 0;"><strong>👤 Cliente:</strong> {client_name}</p>
                    <p style="margin: 5px 0;"><strong>📧 Email:</strong> {client_email}</p>
                    <p style="margin: 5px 0;"><strong>📋 Título:</strong> {session_title}</p>
                </div>
                
                <div class="date-change">
                    <p style="margin: 5px 0;"><strong>📅 Fecha Anterior:</strong> <span style="text-decoration: line-through;">{formatted_old_date}</span></p>
                    <p style="margin: 5px 0;"><strong>📅 Nueva Fecha:</strong> <strong>{formatted_new_date}</strong></p>
                </div>
                
                <p>El cliente ha sido notificado por email del cambio.</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático de notificación.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Sesión Reagendada
    
    Cliente: {client_name}
    Email: {client_email}
    Título: {session_title}
    
    Fecha Anterior: {formatted_old_date}
    Nueva Fecha: {formatted_new_date}
    
    El cliente ha sido notificado por email del cambio.
    
    ---
    Este es un correo automático de notificación.
    """
    
    return send_email(admin_email, subject, html_body, text_body)


def send_admin_session_cancelled_email(client_name: str, client_email: str, session_date: datetime, session_title: str):
    """Send email notification to admin when a session is cancelled"""
    admin_email = os.environ.get('SMTP_USER', 'ecjtrainer@gmail.com')
    subject = f"Sesión Cancelada - {client_name}"
    
    formatted_date = session_date.strftime("%d de %B de %Y a las %H:%M")
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #EF4444; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
            .session-info {{ background-color: white; padding: 20px; border-left: 4px solid #EF4444; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✗ Sesión Cancelada</h1>
            </div>
            <div class="content">
                <p>Hola Jorge,</p>
                <p>Se ha cancelado una sesión:</p>
                
                <div class="session-info">
                    <p style="margin: 5px 0;"><strong>👤 Cliente:</strong> {client_name}</p>
                    <p style="margin: 5px 0;"><strong>📧 Email:</strong> {client_email}</p>
                    <p style="margin: 5px 0;"><strong>📋 Título:</strong> {session_title}</p>
                    <p style="margin: 5px 0;"><strong>📅 Fecha que fue cancelada:</strong> {formatted_date}</p>
                </div>
                
                <p>La sesión ha sido eliminada del calendario.</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático de notificación.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Sesión Cancelada
    
    Cliente: {client_name}
    Email: {client_email}
    Título: {session_title}
    Fecha que fue cancelada: {formatted_date}
    
    La sesión ha sido eliminada del calendario.
    
    ---
    Este es un correo automático de notificación.
    """
    
    return send_email(admin_email, subject, html_body, text_body)




def send_password_reset_email(user_email: str, user_name: str, reset_token: str):
    """Send password reset email to user"""
    subject = "Recupera tu Contraseña - Jorge Calcerrada"
    
    # Get frontend URL from environment
    frontend_url = os.environ.get('FRONTEND_URL', 'https://coach-connect-47.preview.emergentagent.com')
    reset_url = f"{frontend_url}/reset-password?token={reset_token}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3B82F6; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
            .button {{ display: inline-block; padding: 14px 28px; background-color: #3B82F6; color: white !important; text-decoration: none; border-radius: 5px; margin-top: 20px; font-weight: bold; }}
            .button:hover {{ background-color: #2563EB; }}
            .warning {{ background-color: #FEF3C7; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #F59E0B; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Recuperación de Contraseña</h1>
            </div>
            <div class="content">
                <p>Hola {user_name},</p>
                <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
                
                <p>Para crear una nueva contraseña, haz clic en el siguiente botón:</p>
                
                <div style="text-align: center;">
                    <a href="{reset_url}" class="button">Restablecer Contraseña</a>
                </div>
                
                <div class="warning">
                    <p style="margin: 5px 0;"><strong>⚠️ Importante:</strong></p>
                    <p style="margin: 5px 0;">Este enlace expirará en <strong>1 hora</strong>.</p>
                    <p style="margin: 5px 0;">Si no solicitaste este cambio, ignora este correo.</p>
                </div>
                
                <p>Si el botón no funciona, copia y pega este enlace en tu navegador:</p>
                <p style="word-break: break-all; font-size: 12px; color: #666;">{reset_url}</p>
                
                <p>Saludos,<br><strong>Jorge Calcerrada</strong></p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Recuperación de Contraseña
    
    Hola {user_name},
    
    Hemos recibido una solicitud para restablecer tu contraseña.
    
    Para crear una nueva contraseña, accede al siguiente enlace:
    {reset_url}
    
    ⚠️ Importante:
    - Este enlace expirará en 1 hora.
    - Si no solicitaste este cambio, ignora este correo.
    
    Saludos,
    Jorge Calcerrada
    
    ---
    Este es un correo automático, por favor no respondas a este mensaje.
    """
    
    return send_email(user_email, subject, html_body, text_body)

