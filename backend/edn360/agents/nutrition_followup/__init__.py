"""
Agentes de Nutrition Followup
"""

from .ns1metabolicns1_interpreter import NS1MetabolicInterpreter\nfrom .ns2ns2_evaluator import NS2EnergyEvaluator\nfrom .ns3ns3_adjuster import NS3MacroAdjuster\nfrom .ns4ns4_auditor import NS4NutritionAuditor

__all__ = ['NS1MetabolicInterpreter', 'NS2EnergyEvaluator', 'NS3MacroAdjuster', 'NS4NutritionAuditor']
