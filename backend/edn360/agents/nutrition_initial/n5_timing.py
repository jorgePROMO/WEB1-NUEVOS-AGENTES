"""N5 - Timing & Distribution"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N5TimingDistributor(BaseAgent):
    def __init__(self):
        super().__init__("N5", "Timing Distributor")
    def get_system_prompt(self) -> str:
        return '''# N5 — TIMING & REPARTO
Distribuir macros en comidas (2-4 tomas) con timing pre/post entreno.

OUTPUT JSON:
{"status":"ok","comidas":[{"nombre":"Desayuno","hora":"08:00","proteinas_g":40,"carbohidratos_g":60,"grasas_g":20}],"timing":{"pre_entreno":"2h antes","post_entreno":"30min después"}}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "n4_output" in input_data
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
