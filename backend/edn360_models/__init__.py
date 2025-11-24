"""
Models package for EDN360 Architecture

Contains:
- client_drawer.py: ClientDrawer model (TO-BE architecture)
- Legacy models from models.py (AS-IS architecture)
"""

from .client_drawer import (
    ClientDrawer,
    Services,
    SharedQuestionnaire,
    TrainingModule,
    NutritionModule
)

__all__ = [
    "ClientDrawer",
    "Services",
    "SharedQuestionnaire",
    "TrainingModule",
    "NutritionModule"
]
