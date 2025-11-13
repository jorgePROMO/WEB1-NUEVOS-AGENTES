"""N3 - Template Snapper"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N3TemplateSnapper(BaseAgent):
    def __init__(self):
        super().__init__("N3", "Template Snapper")
    def get_system_prompt(self) -> str:
        return '''# N3 — SNAP A PLANTILLA
Ajustar kcal objetivo a paquete comercial (1100-3500).

OUTPUT JSON:
{"status":"ok","paquete_kcal":2200,"macros_pct":{"proteinas":30,"carbohidratos":40,"grasas":30}}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return len(input_data) > 0
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
