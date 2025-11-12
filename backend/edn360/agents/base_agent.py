"""
Clase base para todos los agentes del sistema E.D.N.360
Proporciona funcionalidad común y estructura estándar
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod
from emergentintegrations.llm.chat import LlmChat

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Clase base abstracta para agentes E.D.N.360"""
    
    def __init__(self, agent_id: str, agent_name: str):
        """
        Inicializa el agente
        
        Args:
            agent_id: ID único del agente (E1, E2, N0, etc.)
            agent_name: Nombre descriptivo del agente
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.llm_key = os.getenv("EMERGENT_LLM_KEY")
        
        if not self.llm_key:
            raise ValueError("EMERGENT_LLM_KEY no configurada en el entorno")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Retorna el prompt del sistema para este agente
        Debe ser implementado por cada agente específico
        """
        pass
    
    @abstractmethod
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Valida que los datos de entrada sean correctos
        
        Args:
            input_data: Datos de entrada para el agente
            
        Returns:
            bool: True si los datos son válidos
        """
        pass
    
    @abstractmethod
    def process_output(self, raw_output: str) -> Dict[str, Any]:
        """
        Procesa la salida del LLM y la convierte al formato esperado
        
        Args:
            raw_output: Salida cruda del LLM
            
        Returns:
            Dict con la salida estructurada
        """
        pass
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el agente con los datos de entrada
        
        Args:
            input_data: Datos de entrada para el agente
            
        Returns:
            Dict con el resultado de la ejecución
        """
        start_time = datetime.now()
        
        try:
            # Validar entrada
            if not self.validate_input(input_data):
                raise ValueError(f"Datos de entrada inválidos para {self.agent_id}")
            
            logger.info(f"🤖 {self.agent_id} ({self.agent_name}) - Iniciando ejecución")
            
            # Preparar prompt
            system_prompt = self.get_system_prompt()
            user_message = self._format_input_message(input_data)
            
            # Ejecutar LLM
            llm_chat = LlmChat(
                api_key=self.llm_key,
                model="gpt-4o",
                temperature=0.7,
                max_tokens=8000
            )
            
            response = await llm_chat.async_send_message_stream(
                message=user_message,
                system_prompt=system_prompt
            )
            
            # Procesar salida
            output_data = self.process_output(response)
            
            # Calcular duración
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ {self.agent_id} completado en {duration:.2f}s")
            
            return {
                "success": True,
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "output": output_data,
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ {self.agent_id} falló: {str(e)}")
            
            return {
                "success": False,
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "error": str(e),
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat()
            }
    
    def _format_input_message(self, input_data: Dict[str, Any]) -> str:
        """
        Formatea los datos de entrada en un mensaje para el LLM
        
        Args:
            input_data: Datos de entrada
            
        Returns:
            str: Mensaje formateado
        """
        return f"""# INPUT DATA

```json
{json.dumps(input_data, indent=2, ensure_ascii=False)}
```

Procesa estos datos siguiendo las instrucciones del sistema y genera la salida en formato JSON estructurado.
"""
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """
        Extrae JSON de la respuesta del LLM
        Maneja casos donde el JSON está envuelto en markdown
        
        Args:
            response: Respuesta del LLM
            
        Returns:
            Dict con el JSON parseado
        """
        # Intentar parsear directamente
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Buscar JSON en bloques de código markdown
        import re
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        # Buscar JSON sin bloques de código
        json_pattern = r'\{.*\}'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                pass
        
        raise ValueError(f"No se pudo extraer JSON válido de la respuesta del agente {self.agent_id}")
    
    def log_execution(self, input_data: Dict[str, Any], output_data: Dict[str, Any]):
        """
        Registra la ejecución del agente (para debugging)
        
        Args:
            input_data: Datos de entrada
            output_data: Datos de salida
        """
        log_entry = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "timestamp": datetime.now().isoformat(),
            "input_keys": list(input_data.keys()),
            "output_keys": list(output_data.keys()) if isinstance(output_data, dict) else [],
        }
        logger.debug(f"Agent execution log: {json.dumps(log_entry, indent=2)}")
