"""
Google Calendar Integration Service
Gestión de eventos de calendario para revisiones con clientes
"""
import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest
import requests

load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

SCOPES = ['https://www.googleapis.com/auth/calendar']


def get_authorization_url():
    """
    Genera URL para iniciar OAuth de Google Calendar
    """
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=https://www.googleapis.com/auth/calendar&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    return auth_url


async def exchange_code_for_tokens(code: str) -> dict:
    """
    Intercambia código de autorización por tokens
    """
    token_url = "https://oauth2.googleapis.com/token"
    
    response = requests.post(token_url, data={
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code'
    })
    
    if response.status_code != 200:
        raise Exception(f"Error getting tokens: {response.text}")
    
    return response.json()


async def get_calendar_service(tokens: dict):
    """
    Crea servicio de Google Calendar con tokens
    Maneja refresh automático si es necesario
    """
    creds = Credentials(
        token=tokens.get('access_token'),
        refresh_token=tokens.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        scopes=SCOPES
    )
    
    # Refresh si es necesario
    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        # Actualizar token en BD es responsabilidad del caller
    
    return build('calendar', 'v3', credentials=creds), creds


async def create_calendar_event(
    tokens: dict,
    summary: str,
    start_datetime: datetime,
    end_datetime: datetime,
    attendee_email: str = None,
    description: str = None,
    location: str = None
) -> dict:
    """
    Crea un evento en Google Calendar
    
    Args:
        tokens: Tokens de autenticación de Google
        summary: Título del evento
        start_datetime: Fecha/hora de inicio
        end_datetime: Fecha/hora de fin
        attendee_email: Email del cliente (opcional)
        description: Descripción del evento
        location: Ubicación (opcional)
        
    Returns:
        dict: Datos del evento creado
    """
    service, updated_creds = await get_calendar_service(tokens)
    
    # Construir evento
    event = {
        'summary': summary,
        'description': description or '',
        'start': {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'Europe/Madrid',
        },
        'end': {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'Europe/Madrid',
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},  # 1 día antes
                {'method': 'popup', 'minutes': 60},  # 1 hora antes
            ],
        },
    }
    
    # Añadir ubicación si existe
    if location:
        event['location'] = location
    
    # Añadir asistente (cliente)
    if attendee_email:
        event['attendees'] = [
            {'email': attendee_email, 'responseStatus': 'needsAction'}
        ]
        event['sendUpdates'] = 'all'  # Enviar invitación por email
    
    # Crear evento
    created_event = service.events().insert(
        calendarId='primary',
        body=event,
        sendUpdates='all' if attendee_email else 'none'
    ).execute()
    
    return {
        'event': created_event,
        'updated_tokens': {
            'access_token': updated_creds.token,
            'refresh_token': updated_creds.refresh_token
        } if updated_creds.token != tokens.get('access_token') else None
    }


async def list_upcoming_events(tokens: dict, max_results: int = 50) -> list:
    """
    Lista eventos próximos del calendario
    """
    service, _ = await get_calendar_service(tokens)
    
    now = datetime.now(timezone.utc).isoformat()
    
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    return events_result.get('items', [])


async def delete_calendar_event(tokens: dict, event_id: str) -> bool:
    """
    Elimina un evento del calendario
    """
    try:
        service, _ = await get_calendar_service(tokens)
        service.events().delete(
            calendarId='primary',
            eventId=event_id,
            sendUpdates='all'
        ).execute()
        return True
    except Exception as e:
        print(f"Error deleting event: {e}")
        return False


async def update_calendar_event(
    tokens: dict,
    event_id: str,
    summary: str = None,
    start_datetime: datetime = None,
    end_datetime: datetime = None,
    description: str = None
) -> dict:
    """
    Actualiza un evento existente
    """
    service, _ = await get_calendar_service(tokens)
    
    # Obtener evento actual
    event = service.events().get(calendarId='primary', eventId=event_id).execute()
    
    # Actualizar campos
    if summary:
        event['summary'] = summary
    if description:
        event['description'] = description
    if start_datetime:
        event['start'] = {
            'dateTime': start_datetime.isoformat(),
            'timeZone': 'Europe/Madrid'
        }
    if end_datetime:
        event['end'] = {
            'dateTime': end_datetime.isoformat(),
            'timeZone': 'Europe/Madrid'
        }
    
    # Actualizar evento
    updated_event = service.events().update(
        calendarId='primary',
        eventId=event_id,
        body=event,
        sendUpdates='all'
    ).execute()
    
    return updated_event
