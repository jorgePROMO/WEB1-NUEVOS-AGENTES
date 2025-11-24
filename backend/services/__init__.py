"""
Services package for EDN360 Architecture

Contains business logic and builders:
- edn360_input_builder: Construye EDN360Input desde BD Web + client_drawers
"""

from .edn360_input_builder import build_edn360_input_for_user

__all__ = [
    "build_edn360_input_for_user"
]
