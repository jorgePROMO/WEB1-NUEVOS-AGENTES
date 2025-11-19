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
from openai import OpenAI

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
        self.llm_key = os.getenv("OPENAI_API_KEY")
        
        if not self.llm_key:
            raise ValueError("OPENAI_API_KEY no configurada en el entorno")
        
        # Inicializar cliente de OpenAI
        self.openai_client = OpenAI(api_key=self.llm_key)
    
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
    
    async def execute(self, input_data: Dict[str, Any], knowledge_base: str = "") -> Dict[str, Any]:
        """
        Ejecuta el agente con los datos de entrada y opcionalmente una base de conocimiento
        
        Args:
            input_data: Datos de entrada para el agente (client_context)
            knowledge_base: (Opcional) Base de conocimiento global como referencia
            
        Returns:
            Dict con el resultado de la ejecución
        """
        start_time = datetime.now()
        
        try:
            # Validar entrada
            if not self.validate_input(input_data):
                raise ValueError(f"Datos de entrada inválidos para {self.agent_id}")
            
            logger.info(f"🤖 {self.agent_id} ({self.agent_name}) - Iniciando ejecución")
            
            # Preparar prompt del sistema con instrucciones de jerarquía de datos
            system_prompt = self.get_system_prompt()
            
            # Si se proporciona una base de conocimiento, añadirla al sistema con instrucciones claras
            if knowledge_base:
                kb_instructions = """

# BASES DE CONOCIMIENTO GLOBAL (REFERENCIA)

A continuación tienes acceso a una base de conocimiento global que sirve como **MANUAL DE REFERENCIA TEÓRICO**. 

⚠️ **JERARQUÍA CRÍTICA DE INFORMACIÓN**:
1. **PRIORIDAD ABSOLUTA**: Los datos específicos del cliente en el CLIENT_CONTEXT (cuestionarios, planes previos, datos personales)
2. **PRIORIDAD SECUNDARIA**: Esta base de conocimiento sirve como guía teórica general

**REGLAS OBLIGATORIAS**:
- SIEMPRE adapta la teoría de la KB a la realidad específica del cliente
- Si hay conflicto entre los datos del cliente y la teoría general → el cliente tiene prioridad absoluta
- La KB NO debe ser almacenada ni mezclada con los datos del cliente
- Usa la KB como referencia para fundamentar decisiones, pero personaliza siempre según el cliente

---

## KNOWLEDGE BASE:

"""
                system_prompt = system_prompt + kb_instructions + knowledge_base
                logger.info(f"📚 {self.agent_id} usando KB de {len(knowledge_base)} caracteres")
            
            user_message = self._format_input_message(input_data)
            
            # Ejecutar LLM con OpenAI directamente
            # Añadir instrucción explícita de JSON al system prompt
            json_system_prompt = system_prompt + "\n\n**CRÍTICO: Tu respuesta DEBE ser ÚNICAMENTE un objeto JSON válido. No incluyas texto adicional, explicaciones, ni markdown. Solo el JSON puro.**"
            
            # Llamada síncrona a OpenAI
            completion = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": json_system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=16000
            )
            
            response = completion.choices[0].message.content
            
            # Log de respuesta para debug
            logger.info(f"📝 {self.agent_id} respuesta (primeros 500 chars): {response[:500]}")
            
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
        Maneja casos donde el JSON está envuelto en markdown o texto adicional
        
        Args:
            response: Respuesta del LLM
            
        Returns:
            Dict con el JSON parseado
        """
        import re
        
        # Intentar parsear directamente
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            pass
        
        # Buscar JSON en bloques de código markdown (```json ... ``` o ``` ... ```)
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        if matches:
            # Intentar con cada match (tomar el más largo, que suele ser el completo)
            matches_sorted = sorted(matches, key=len, reverse=True)
            for match in matches_sorted:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Buscar JSON sin bloques de código (buscar el objeto más grande y anidado)
        # Usar una estrategia más sofisticada: encontrar { y su } correspondiente
        stack = []
        start_idx = -1
        end_idx = -1
        
        for i, char in enumerate(response):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack:  # Encontramos un JSON completo
                        end_idx = i + 1
                        # Intentar parsear este JSON
                        try:
                            json_str = response[start_idx:end_idx]
                            return json.loads(json_str)
                        except json.JSONDecodeError:
                            continue
        
        # Si nada funcionó, registrar el error con más detalle
        logger.error(f"❌ No se pudo extraer JSON de la respuesta de {self.agent_id}")
        logger.error(f"Respuesta completa (primeros 1000 chars): {response[:1000]}")
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
