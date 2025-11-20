"""
Script para refactorizar E2, E3, E6, E7, E9
Aplica el mismo patrón que E1, E5, E8
"""

import re

# Definir los cambios necesarios para cada agente
AGENT_CONFIGS = {
    "e2_capacity": {
        "agent_id": "E2",
        "agent_name": "Evaluador de Capacidad",
        "fills": "capacity",
        "requires": ["profile"],
        "description": "Evalúa capacidad de entrenamiento y determina volumen/intensidad tolerable"
    },
    "e3_adaptation": {
        "agent_id": "E3",
        "agent_name": "Analista de Adaptación",
        "fills": "adaptation",
        "requires": ["capacity", "profile"],
        "description": "Analiza vida real del cliente y ajusta plan según estrés/sueño"
    },
    "e6_clinical": {
        "agent_id": "E6",
        "agent_name": "Técnico Clínico",
        "fills": "safe_sessions",
        "requires": ["sessions", "constraints", "prehab"],
        "description": "Adapta sesiones para seguridad, sustituye ejercicios prohibidos"
    },
    "e7_load": {
        "agent_id": "E7",
        "agent_name": "Visualizador de Carga",
        "fills": "formatted_plan",
        "requires": ["safe_sessions", "mesocycle"],
        "description": "Formatea plan para presentación al cliente"
    },
    "e9_bridge": {
        "agent_id": "E9",
        "agent_name": "Puente a Nutrición",
        "fills": "bridge_for_nutrition",
        "requires": ["safe_sessions", "mesocycle", "profile"],
        "description": "Genera información para agentes de nutrición"
    }
}


def get_new_docstring(config):
    """Genera docstring actualizado"""
    return f'''"""
{config["agent_id"]} - {config["agent_name"]}
{config["description"]}

ARQUITECTURA NUEVA (Fase 2):
- Recibe client_context completo
- Lee de: {", ".join(f"training.{r}" for r in config["requires"])}
- Llena SOLO: training.{config["fills"]}
- Devuelve client_context completo actualizado
"""'''


def get_new_validate_input(config):
    """Genera método validate_input actualizado"""
    requires_check = " and\n                ".join(
        f'training.get("{req}") is not None'
        for req in config["requires"]
    )
    
    return f'''    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Valida que el input contenga client_context con campos necesarios
        
        NUEVO (Fase 2): Validamos client_context
        """
        if "training" not in input_data:
            return False
        
        training = input_data["training"]
        
        # Debe tener campos requeridos
        return ({requires_check})'''


def get_new_process_output(config):
    """Genera método process_output actualizado"""
    return f'''    def process_output(self, raw_output: str) -> Dict[str, Any]:
        """
        Valida que devuelva client_context con {config["fills"]} lleno
        
        NUEVO (Fase 2): Validamos estructura de salida
        """
        try:
            output = self._extract_json_from_response(raw_output)
            
            if "client_context" not in output:
                raise ValueError("Output no contiene client_context")
            
            client_context = output["client_context"]
            training = client_context.get("training", {})
            
            # Validar que {config["agent_id"]} llenó {config["fills"]}
            if training.get("{config["fills"]}") is None:
                raise ValueError("{config["agent_id"]} no llenó training.{config["fills"]}")
            
            return output
            
        except Exception as e:
            raise ValueError(f"Error procesando output de {config['agent_id']}: {{str(e)}}")'''


def refactor_agent_file(filepath, config):
    """Refactoriza un archivo de agente"""
    print(f"\n🔧 Refactorizando {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Actualizar docstring inicial
    old_docstring_pattern = r'^"""[^"]*"""'
    new_docstring = get_new_docstring(config)
    content = re.sub(old_docstring_pattern, new_docstring, content, count=1, flags=re.MULTILINE | re.DOTALL)
    
    # 2. Actualizar validate_input
    validate_pattern = r'    def validate_input\(self, input_data: Dict\[str, Any\]\) -> bool:.*?(?=\n    def |\nclass |\Z)'
    new_validate = get_new_validate_input(config)
    content = re.sub(validate_pattern, new_validate, content, count=1, flags=re.DOTALL)
    
    # 3. Actualizar process_output
    process_pattern = r'    def process_output\(self, raw_output: str\) -> Dict\[str, Any\]:.*?(?=\n    def |\nclass |\Z)'
    new_process = get_new_process_output(config)
    content = re.sub(process_pattern, new_process, content, count=1, flags=re.DOTALL)
    
    # Guardar
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {config['agent_id']} refactorizado")


def main():
    """Refactoriza todos los agentes pendientes"""
    print("🚀 Refactorizando agentes E2, E3, E6, E7, E9...")
    
    base_path = "/app/backend/edn360/agents/training_initial"
    
    for filename, config in AGENT_CONFIGS.items():
        filepath = f"{base_path}/{filename}.py"
        try:
            refactor_agent_file(filepath, config)
        except Exception as e:
            print(f"❌ Error en {filename}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n✅ Refactor completado")


if __name__ == "__main__":
    main()
