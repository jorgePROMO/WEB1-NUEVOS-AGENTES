"""N4 - A/M/B Synchronizer"""
from typing import Dict, Any
from ..base_agent import BaseAgent

class N4AMBSynchronizer(BaseAgent):
    def __init__(self):
        super().__init__("N4", "A/M/B Synchronizer")
    def get_system_prompt(self) -> str:
        return '''# N4 — SINCRONIZADOR A/M/B
Crear calendario mensual con días altos/medios/bajos sincronizado con entrenamiento.

OUTPUT JSON:
{"status":"ok","calendario":[{"dia":1,"tipo":"A","kcal":2400},{"dia":2,"tipo":"B","kcal":2000}],"deltas":{"A":"+10%","M":"0%","B":"-10%"}}'''
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        return "n3_output" in input_data
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        return self._extract_json_from_response(raw_output)
