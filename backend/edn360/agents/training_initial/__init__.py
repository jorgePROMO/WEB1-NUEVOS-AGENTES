"""
Agentes de Entrenamiento Inicial (E1-E9)
"""

from .e1_analyst import E1Analyst
from .e2_capacity import E2CapacityEvaluator
from .e3_adaptation import E3AdaptationAnalyst
from .e4_architect import E4ProgramArchitect
from .e5_engineer import E5MicrocycleEngineer
from .e6_clinical import E6ClinicalTechnician
from .e7_load import E7LoadAnalyst
from .e8_auditor import E8TechnicalAuditor
from .e9_bridge import E9NutritionBridge

__all__ = [
    'E1Analyst',
    'E2CapacityEvaluator',
    'E3AdaptationAnalyst',
    'E4ProgramArchitect',
    'E5MicrocycleEngineer',
    'E6ClinicalTechnician',
    'E7LoadAnalyst',
    'E8TechnicalAuditor',
    'E9NutritionBridge',
]