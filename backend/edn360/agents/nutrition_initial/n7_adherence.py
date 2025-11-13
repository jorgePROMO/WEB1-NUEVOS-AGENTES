"""N7 - Adherence Coach"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N7AdherenceCoach(BaseAgent):
    def __init__(self):
        super().__init__("N7", "Adherence Coach")
    def get_system_prompt(self) -> str:
        return '''# N7 — COACH DE ADHERENCIA
Protocolos 80/20, emergencias, rollback.

OUTPUT JSON:
{"status":"ok","protocolos":{"80_20":"80% estructura, 20% flexible","emergencia":"Si fallas 2 días seguidos, vuelve a base"},"recomendaciones":["Meal prep dominical","2 comidas libres/semana"]}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
