"""
Repositories package for EDN360 Architecture

Contains data access layers for:
- client_drawer_repository: Access to client_drawers collection (TO-BE)
"""

from .client_drawer_repository import (
    get_drawer_by_user_id,
    create_empty_drawer_for_user,
    upsert_drawer,
    add_questionnaire_to_drawer,
    get_or_create_drawer,
    get_global_telemetry
)

__all__ = [
    "get_drawer_by_user_id",
    "create_empty_drawer_for_user",
    "upsert_drawer",
    "add_questionnaire_to_drawer",
    "get_or_create_drawer",
    "get_global_telemetry"
]
