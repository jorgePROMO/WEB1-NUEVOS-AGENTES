"""
N3 - Snap a Plantilla
"""

from typing import Dict, Any
from ..base_agent import BaseAgent

class N3TemplateSnap(BaseAgent):
    def __init__(self):
        super().__init__("N3", "Snap a Plantilla")
    
    def get_system_prompt(self) -> str:
        return """# N3 - Snap Plantilla\nAsigna plantilla comercial.
        
Procesa el input y genera output JSON estructurado siguiendo las especificaciones del sistema E.D.N.360."""
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
