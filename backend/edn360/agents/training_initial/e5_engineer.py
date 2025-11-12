from typing import Dict, Any
from ..base_agent import BaseAgent

class E5MicrocycleEngineer(BaseAgent):
    def __init__(self):
        super().__init__("E5", "Ingeniero de Microciclos")
    
    def get_system_prompt(self) -> str:
        return '''# E5 — INGENIERO DE MICROCICLOS
Crea sesiones detalladas con ejercicios específicos, series, reps, RIR y descansos.
Debes generar JSON con todas las sesiones del mesociclo incluyendo ejercicios concretos.'''
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "e4_output" in input_data
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)