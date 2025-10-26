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
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3B82F6; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #3B82F6; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Nueva Sesión Programada</h1>
            </div>
            <div class="content">
                <p>Hola {user_name},</p>
                <p>Se ha programado una nueva sesión para ti:</p>
                <p><strong>Título:</strong> {session_title}</p>
                <p><strong>Fecha y Hora:</strong> {formatted_date}</p>
                <p>Si necesitas reagendar esta sesión, puedes hacerlo desde tu panel de usuario.</p>
                <p>¡Nos vemos pronto!</p>
                <p>Saludos,<br>Jorge Calcerrada</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
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
    
    Si necesitas reagendar esta sesión, puedes hacerlo desde tu panel de usuario.
    
    ¡Nos vemos pronto!
    
    Saludos,
    Jorge Calcerrada
    """
    
    return send_email(user_email, subject, html_body, text_body)


def send_session_rescheduled_email(user_email: str, user_name: str, new_date: datetime, session_title: str):
    """Send email notification when a session is rescheduled"""
    subject = f"Sesión Reagendada - {session_title}"
    
    formatted_date = new_date.strftime("%d de %B de %Y a las %H:%M")
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #F59E0B; color: white; padding: 20px; text-align: center; border-radius: 5px 5px 0 0; }}
            .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 0 0 5px 5px; }}
            .button {{ display: inline-block; padding: 12px 24px; background-color: #F59E0B; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
            .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Sesión Reagendada</h1>
            </div>
            <div class="content">
                <p>Hola {user_name},</p>
                <p>Tu sesión ha sido reagendada para:</p>
                <p><strong>Título:</strong> {session_title}</p>
                <p><strong>Nueva Fecha y Hora:</strong> {formatted_date}</p>
                <p>Si tienes alguna duda o necesitas hacer cambios adicionales, no dudes en contactarnos.</p>
                <p>¡Nos vemos pronto!</p>
                <p>Saludos,<br>Jorge Calcerrada</p>
            </div>
            <div class="footer">
                <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Hola {user_name},
    
    Tu sesión ha sido reagendada para:
    
    Título: {session_title}
    Nueva Fecha y Hora: {formatted_date}
    
    Si tienes alguna duda o necesitas hacer cambios adicionales, no dudes en contactarnos.
    
    ¡Nos vemos pronto!
    
    Saludos,
    Jorge Calcerrada
    """
    
    return send_email(user_email, subject, html_body, text_body)
