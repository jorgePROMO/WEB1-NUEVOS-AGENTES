"""
Agentes especializados del sistema E.D.N.360
26 agentes organizados en 4 dominios
"""

# Training Initial Agents (E1-E9)
from .training_initial.e1_analyst import E1Analyst
from .training_initial.e2_capacity import E2CapacityEvaluator
from .training_initial.e3_adaptation import E3AdaptationAnalyst

# TODO: Import rest of agents as they are implemented

__all__ = [
    'E1Analyst',
    'E2CapacityEvaluator',
    'E3AdaptationAnalyst',
]
