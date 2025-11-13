"""N6 - Menu Generator"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N6MenuGenerator(BaseAgent):
    def __init__(self):
        super().__init__("N6", "Menu Generator")
    def get_system_prompt(self) -> str:
        return '''# N6 — MENÚS & EQUIVALENCIAS
Generar menús A/M/B con ejemplos de comidas y swaps.

OUTPUT JSON:
{"status":"ok","menus":{"A":[{"comida":"Desayuno","alimentos":["3 huevos","100g avena","1 plátano"]}],"M":[],"B":[]},"swaps":{"avena":"arroz","huevos":"pavo"}}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "n5_output" in input_data
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
