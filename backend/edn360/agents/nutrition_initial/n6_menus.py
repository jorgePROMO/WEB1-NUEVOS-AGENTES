"""
N6 - Menús & Equivalencias
"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class N6MenuGenerator(BaseAgent):
    def __init__(self):
        super().__init__("N6", "Menús & Equivalencias")
    
    def get_system_prompt(self) -> str:
        return """# N6 - Menús\nGenera menús reales.
        
Procesa el input y genera output JSON estructurado siguiendo las especificaciones del sistema E.D.N.360."""
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
