"""
E.D.N.360 - Sistema de Entrenamiento Deportivo + Nutrición 360°
Sistema de generación automática de planes de entrenamiento y nutrición
con 26 agentes especializados
"""

__version__ = "1.0.0"
__author__ = "Jorge Calcerrada Training System"

# Exponer los módulos principales
from .orchestrator import EDN360Orchestrator
from .models import (
    EDN360Plan,
    QuestionnaireData,
    TrainingPlan,
    NutritionPlan,
    FollowUpPlan
)

__all__ = [
    'EDN360Orchestrator',
    'EDN360Plan',
    'QuestionnaireData',
    'TrainingPlan',
    'NutritionPlan',
    'FollowUpPlan'
]
