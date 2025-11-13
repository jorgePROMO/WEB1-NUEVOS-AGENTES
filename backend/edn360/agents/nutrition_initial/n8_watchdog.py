"""N8 - Watchdog"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N8Watchdog(BaseAgent):
    def __init__(self):
        super().__init__("N8", "Watchdog")
    def get_system_prompt(self) -> str:
        return '''# N8 — WATCHDOG
Validación final, aprobación o bloqueo con correcciones.

OUTPUT JSON:
{"status":"ok","aprobacion":true,"validaciones":{"coherencia_macros":true,"timing_correcto":true,"adherencia_viable":true},"plan_aprobado":true,"recomendaciones_finales":["Plan coherente y ejecutable"]}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "n7_output" in input_data
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
