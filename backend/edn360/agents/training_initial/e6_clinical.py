"""
E6 - Técnico Clínico-Preventivo
"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class E6ClinicalTechnician(BaseAgent):
    def __init__(self):
        super().__init__("E6", "Técnico Clínico-Preventivo")
    
    def get_system_prompt(self) -> str:
        return """# E6 - Técnico Clínico-Preventivo\nAdapta ejercicios para lesiones y añade correctivos.
        
Procesa el input y genera output JSON estructurado siguiendo las especificaciones del sistema E.D.N.360."""
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
