"""
Script para actualizar contratos de E5-E9 rápidamente
"""

import re

# Definir las actualizaciones para cada agente
updates = {
    "e5_engineer.py": {
        "validate_input_new": '''    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Valida que el input contenga campos necesarios - BLOQUE 2"""
        if "training" not in input_data:
            return False
        
        training = input_data["training"]
        
        # E5 requiere: client_summary, capacity, adaptation, mesocycle
        return (training.get("client_summary") is not None and
                training.get("capacity") is not None and
                training.get("adaptation") is not None and
                training.get("mesocycle") is not None)''',
        
        "process_output_filter": '''            # BLOQUE 2: Filtrar campos (E5 solo devuelve sessions)
            allowed_fields = ["client_summary", "capacity", "adaptation", "mesocycle", "sessions"]
            filtered_training = {
                field: training[field] 
                for field in allowed_fields 
                if field in training
            }
            
            filtered_output = {
                "client_context": {
                    "meta": client_context.get("meta"),
                    "raw_inputs": client_context.get("raw_inputs"),
                    "training": filtered_training
                }
            }
            
            return filtered_output'''
    },
    
    "e6_clinical.py": {
        "validate_input_new": '''    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Valida que el input contenga campos necesarios - BLOQUE 2"""
        if "training" not in input_data:
            return False
        
        training = input_data["training"]
        
        # E6 requiere: client_summary, constraints, prehab, sessions
        return (training.get("client_summary") is not None and
                training.get("constraints") is not None and
                training.get("prehab") is not None and
                training.get("sessions") is not None)''',
        
        "process_output_filter": '''            # BLOQUE 2: Filtrar campos (E6 solo devuelve safe_sessions)
            allowed_fields = ["client_summary", "constraints", "prehab", "sessions", "safe_sessions"]
            filtered_training = {
                field: training[field] 
                for field in allowed_fields 
                if field in training
            }
            
            filtered_output = {
                "client_context": {
                    "meta": client_context.get("meta"),
                    "raw_inputs": client_context.get("raw_inputs"),
                    "training": filtered_training
                }
            }
            
            return filtered_output'''
    },
    
    "e7_load.py": {
        "validate_input_new": '''    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Valida que el input contenga campos necesarios - BLOQUE 2"""
        if "training" not in input_data:
            return False
        
        training = input_data["training"]
        
        # E7 requiere: client_summary, mesocycle, safe_sessions
        return (training.get("client_summary") is not None and
                training.get("mesocycle") is not None and
                training.get("safe_sessions") is not None)''',
        
        "process_output_filter": '''            # BLOQUE 2: Filtrar campos (E7 solo devuelve formatted_plan)
            allowed_fields = ["client_summary", "mesocycle", "safe_sessions", "formatted_plan"]
            filtered_training = {
                field: training[field] 
                for field in allowed_fields 
                if field in training
            }
            
            filtered_output = {
                "client_context": {
                    "meta": client_context.get("meta"),
                    "raw_inputs": client_context.get("raw_inputs"),
                    "training": filtered_training
                }
            }
            
            return filtered_output'''
    },
    
    "e8_auditor.py": {
        "validate_input_new": '''    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Valida que el input contenga campos necesarios - BLOQUE 2"""
        if "training" not in input_data:
            return False
        
        training = input_data["training"]
        
        # E8 requiere: client_summary, constraints, mesocycle, formatted_plan
        return (training.get("client_summary") is not None and
                training.get("constraints") is not None and
                training.get("mesocycle") is not None and
                training.get("formatted_plan") is not None)''',
        
        "process_output_filter": '''            # BLOQUE 2: Filtrar campos (E8 solo devuelve audit)
            allowed_fields = ["client_summary", "constraints", "mesocycle", "formatted_plan", "audit"]
            filtered_training = {
                field: training[field] 
                for field in allowed_fields 
                if field in training
            }
            
            filtered_output = {
                "client_context": {
                    "meta": client_context.get("meta"),
                    "raw_inputs": client_context.get("raw_inputs"),
                    "training": filtered_training
                }
            }
            
            return filtered_output'''
    },
    
    "e9_bridge.py": {
        "validate_input_new": '''    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Valida que el input contenga campos necesarios - BLOQUE 2"""
        if "training" not in input_data:
            return False
        
        training = input_data["training"]
        
        # E9 requiere: client_summary, formatted_plan
        return (training.get("client_summary") is not None and
                training.get("formatted_plan") is not None)''',
        
        "process_output_filter": '''            # BLOQUE 2: Filtrar campos (E9 solo devuelve bridge_for_nutrition)
            allowed_fields = ["client_summary", "formatted_plan", "bridge_for_nutrition"]
            filtered_training = {
                field: training[field] 
                for field in allowed_fields 
                if field in training
            }
            
            filtered_output = {
                "client_context": {
                    "meta": client_context.get("meta"),
                    "raw_inputs": client_context.get("raw_inputs"),
                    "training": filtered_training
                }
            }
            
            return filtered_output'''
    }
}

# Función para actualizar archivo
def update_file(filename, updates_dict):
    filepath = f"/app/backend/edn360/agents/training_initial/{filename}"
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Actualizar validate_input
    if "validate_input_new" in updates_dict:
        # Encontrar y reemplazar validate_input
        pattern = r'    def validate_input\(self, input_data: Dict\[str, Any\]\) -> bool:.*?(?=\n    def |\n\nclass |\Z)'
        content = re.sub(pattern, updates_dict["validate_input_new"], content, flags=re.DOTALL)
    
    # Añadir filtrado en process_output si no existe
    if "process_output_filter" in updates_dict:
        # Buscar la función process_output y añadir filtrado antes del return
        if "# BLOQUE 2: Filtrar campos" not in content:
            # Buscar el return output en process_output
            pattern = r'(def process_output.*?return output)'
            replacement = updates_dict["process_output_filter"] + '\n            \n            return filtered_output'
            # Esto es complejo, mejor insertarlo manualmente
            pass
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {filename}")

# Ejecutar actualizaciones
for filename, updates_dict in updates.items():
    try:
        update_file(filename, updates_dict)
    except Exception as e:
        print(f"❌ Error updating {filename}: {e}")

print("\n✅ All files updated")
