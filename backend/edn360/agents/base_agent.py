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
    
    
    def normalize_agent_output(
        self,
        parsed_response: Dict[str, Any],
        original_client_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        POST-PROCESADOR: Normaliza la salida del agente al formato esperado.
        
        PROBLEMA RESUELTO:
        - Algunos agentes pueden devolver formato antiguo por influencia de la KB
        - Ej: {"status": "ok", "metabolism": {...}} en lugar de {"client_context": {...}}
        
        COMPORTAMIENTO:
        1. Si ya tiene "client_context" → No tocar, devolver tal cual ✅
        2. Si tiene formato antiguo → Convertir automáticamente 🔁
        3. Si no encaja en ninguno → Error claro ❌
        
        Args:
            parsed_response: JSON parseado de la respuesta del LLM
            original_client_context: client_context que se envió al LLM (vista completa o compacta)
            
        Returns:
            Dict normalizado con formato {"client_context": {...}}
        """
        # CASO 1: Ya tiene el formato correcto
        if "client_context" in parsed_response:
            logger.debug(f"✅ {self.agent_id} devolvió formato correcto")
            return parsed_response
        
        # CASO 2: Formato antiguo - intentar convertir
        logger.warning(f"🔁 {self.agent_id} devolvió formato antiguo. Normalizando...")
        
        # Determinar si es agente E o N
        is_nutrition_agent = self.agent_id.startswith("N")
        
        if is_nutrition_agent:
            # Agente N: El formato antiguo suele tener campos de nutrition directamente
            # Necesitamos extraer esos campos y meterlos en client_context.nutrition
            
            # Campos típicos del formato antiguo de nutrición
            old_format_fields = [
                "status", "perfil_metabolico", "tdee_estimado", "bmr_estimado",
                "objetivo", "estrategia", "ciclado_calorico", "macros_iniciales",
                "distribucion_dias_A", "menu_tipo_A", "factores_riesgo",
                "resultado_general", "checks"
            ]
            
            # Verificar si tiene campos del formato antiguo
            has_old_format = any(field in parsed_response for field in old_format_fields)
            
            if has_old_format:
                # Construir client_context normalizado
                # Usar el original como base y solo actualizar nutrition
                normalized = {
                    "client_context": {
                        "meta": original_client_context.get("meta", {}),
                        "raw_inputs": original_client_context.get("raw_inputs", {}),
                        "training": original_client_context.get("training", {}),
                        "nutrition": original_client_context.get("nutrition", {})
                    }
                }
                
                # Mapear campos antiguos según el agente
                # Por ahora, metemos todo lo que devolvió en el campo correspondiente
                nutrition_field = self._get_nutrition_field_for_agent()
                
                if nutrition_field:
                    # Actualizar solo el campo que este agente debe llenar
                    normalized["client_context"]["nutrition"][nutrition_field] = parsed_response
                    logger.info(f"✅ {self.agent_id} - Formato antiguo convertido a client_context.nutrition.{nutrition_field}")
                    return normalized
        
        else:
            # Agente E: Similar pero para training
            logger.warning(f"⚠️ {self.agent_id} (training agent) devolvió formato no reconocido")
        
        # CASO 3: No se pudo normalizar
        logger.error(f"❌ {self.agent_id} - No se pudo normalizar el formato de salida")
        logger.error(f"   Respuesta recibida (keys): {list(parsed_response.keys())}")
        raise ValueError(
            f"{self.agent_id} devolvió formato no reconocido. "
            f"Se esperaba {{'client_context': {{...}}}} pero recibió: {list(parsed_response.keys())}"
        )
    
    def _get_nutrition_field_for_agent(self) -> Optional[str]:
        """
        Retorna el campo de nutrition.* que este agente debe llenar.
        Usado por el post-procesador para normalizar formato antiguo.
        """
        mapping = {
            "N0": "profile",
            "N1": "metabolism",
            "N2": "energy_strategy",
            "N3": "macro_design",
            "N4": "weekly_structure",
            "N5": "timing_plan",
            "N6": "menu_plan",
            "N7": "adherence_report",
            "N8": "audit"
        }
        return mapping.get(self.agent_id)

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
            
            # Llamada síncrona a OpenAI con control de coste
            completion = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": json_system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=6000,
                timeout=120
            )
            
            response = completion.choices[0].message.content
            
            # Capturar uso de tokens para control de coste
            usage = getattr(completion, "usage", None)
            token_usage = None
            if usage:
                token_usage = {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
                logger.info(f"📊 {self.agent_id} tokens: prompt={usage.prompt_tokens}, completion={usage.completion_tokens}, total={usage.total_tokens}")
            
            # Log de respuesta para debug
            logger.info(f"📝 {self.agent_id} respuesta (primeros 500 chars): {response[:500]}")
            
            # Guardar respuesta completa para debugging (solo en caso de error posterior)
            _full_response = response
            
            # Procesar salida con post-procesador de normalización y retry robusto
            try:
                # 1. Extraer JSON de la respuesta con sistema mejorado
                parsed_json = self._extract_json_from_response_robust(response)
                
                # 2. Normalizar formato (convierte formato antiguo a nuevo si es necesario)
                normalized_json = self.normalize_agent_output(parsed_json, input_data)
                
                # 3. Validar estructura básica
                if "client_context" not in normalized_json:
                    raise ValueError("Normalized output no contiene client_context")
                
                # 4. Validación específica del agente (si es necesaria)
                # La mayoría de validaciones ya se hacen en normalize_agent_output
                output_data = normalized_json
                
            except Exception as parse_error:
                # RETRY AUTOMÁTICO: Si falla el parseo, intentar corrección con LLM
                logger.warning(f"⚠️ {self.agent_id} - Parseo JSON falló en primer intento. Activando corrección automática...")
                
                try:
                    # Guardar respuesta problemática para debugging
                    debug_file = f"/app/debug_response_{self.agent_id}_broken.txt"
                    with open(debug_file, 'w') as f:
                        f.write(_full_response)
                    logger.info(f"📁 Respuesta problemática guardada en {debug_file}")
                    
                    # Intentar corrección automática mediante prompt forzado
                    output_data = self._auto_fix_json_response(_full_response, input_data, system_prompt, user_message)
                    logger.info(f"✅ {self.agent_id} - Corrección automática de JSON exitosa")
                    
                except Exception as fix_error:
                    # Si la corrección también falla, entonces es error definitivo
                    logger.error(f"❌ {self.agent_id} - Corrección automática falló: {str(fix_error)}")
                    raise ValueError(f"No se pudo extraer JSON válido de la respuesta del agente {self.agent_id}") from parse_error
            
            # Calcular duración
            duration = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ {self.agent_id} completado en {duration:.2f}s")
            
            result = {
                "success": True,
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "output": output_data,
                "duration_seconds": duration,
                "timestamp": datetime.now().isoformat()
            }
            
            # Añadir token usage si está disponible
            if token_usage:
                result["token_usage"] = token_usage
            
            return result
            
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
        # Usar patrón no-greedy pero que capture todo hasta las últimas comillas de cierre
        json_pattern = r'```(?:json)?\s*(\{[\s\S]*\})\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        if matches:
            # Intentar con cada match (tomar el más largo, que suele ser el completo)
            matches_sorted = sorted(matches, key=len, reverse=True)
            for match in matches_sorted:
                try:
                    return json.loads(match)
                except json.JSONDecodeError as e:
                    # Intentar reparar errores comunes de cierre de llaves
                    if "Expecting ',' delimiter" in str(e) or "Expecting" in str(e):
                        # El LLM a veces omite llaves de cierre en objetos anidados grandes
                        # Intentar agregar llaves faltantes
                        repaired = match.rstrip()
                        if repaired.count('{') > repaired.count('}'):
                            # Faltan llaves de cierre
                            missing = repaired.count('{') - repaired.count('}')
                            repaired = repaired + ('\n}' * missing)
                            try:
                                return json.loads(repaired)
                            except json.JSONDecodeError:
                                pass
                    continue
        
        # Si no hay matches con el patrón completo, buscar JSON truncado sin closing backticks
        # (Caso: ```json {...  sin ``` al final)
        truncated_pattern = r'```(?:json)?\s*(\{[\s\S]*)'
        truncated_matches = re.findall(truncated_pattern, response, re.DOTALL)
        
        if truncated_matches:
            for match in truncated_matches:
                # Limpiar y reparar
                match = match.rstrip()
                if match.count('{') > match.count('}'):
                    missing = match.count('{') - match.count('}')
                    match = match + ('\n}' * missing)
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
    
    def _extract_json_from_response_robust(self, response: str) -> Dict[str, Any]:
        """
        Sistema ROBUSTO de extracción de JSON con múltiples estrategias.
        Incluye validación de estructura y reparación automática.
        
        Args:
            response: Respuesta del LLM
            
        Returns:
            Dict con el JSON parseado y validado
        """
        import re
        
        # ESTRATEGIA 1: Parseo directo
        try:
            parsed = json.loads(response.strip())
            self._validate_json_structure(parsed)
            return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        
        # ESTRATEGIA 2: Markdown con ```json```
        json_pattern = r'```(?:json)?\s*(\{[\s\S]*?\})\s*```'
        matches = re.findall(json_pattern, response, re.DOTALL)
        
        if matches:
            for match in sorted(matches, key=len, reverse=True):
                try:
                    parsed = json.loads(match)
                    self._validate_json_structure(parsed)
                    return parsed
                except (json.JSONDecodeError, ValueError):
                    # Intentar reparar
                    repaired = self._repair_json(match)
                    if repaired:
                        try:
                            parsed = json.loads(repaired)
                            self._validate_json_structure(parsed)
                            logger.info(f"✅ {self.agent_id} - JSON reparado exitosamente")
                            return parsed
                        except (json.JSONDecodeError, ValueError):
                            continue
        
        # ESTRATEGIA 3: Markdown truncado sin closing ```
        truncated_pattern = r'```(?:json)?\s*(\{[\s\S]*)'
        truncated_matches = re.findall(truncated_pattern, response, re.DOTALL)
        
        if truncated_matches:
            for match in truncated_matches:
                repaired = self._repair_json(match.rstrip())
                if repaired:
                    try:
                        parsed = json.loads(repaired)
                        self._validate_json_structure(parsed)
                        logger.info(f"✅ {self.agent_id} - JSON truncado reparado")
                        return parsed
                    except (json.JSONDecodeError, ValueError):
                        continue
        
        # ESTRATEGIA 4: Buscar JSON sin markdown
        stack = []
        start_idx = -1
        candidates = []
        
        for i, char in enumerate(response):
            if char == '{':
                if not stack:
                    start_idx = i
                stack.append(char)
            elif char == '}':
                if stack:
                    stack.pop()
                    if not stack and start_idx != -1:
                        json_str = response[start_idx:i+1]
                        candidates.append(json_str)
        
        # Intentar con cada candidato (más largo primero)
        for candidate in sorted(candidates, key=len, reverse=True):
            try:
                parsed = json.loads(candidate)
                self._validate_json_structure(parsed)
                return parsed
            except (json.JSONDecodeError, ValueError):
                repaired = self._repair_json(candidate)
                if repaired:
                    try:
                        parsed = json.loads(repaired)
                        self._validate_json_structure(parsed)
                        logger.info(f"✅ {self.agent_id} - JSON sin markdown reparado")
                        return parsed
                    except (json.JSONDecodeError, ValueError):
                        continue
        
        # Si nada funcionó, lanzar error que activará auto-corrección
        logger.error(f"❌ {self.agent_id} - Todas las estrategias de parseo fallaron")
        raise ValueError(f"No se pudo extraer JSON válido con estrategias robustas")
    
    def _repair_json(self, json_str: str) -> str:
        """
        Intenta reparar JSON malformado con técnicas comunes.
        
        Args:
            json_str: String JSON potencialmente malformado
            
        Returns:
            String JSON reparado o None si no se pudo reparar
        """
        try:
            json_str = json_str.strip()
            
            # 1. Añadir llaves de cierre faltantes
            open_braces = json_str.count('{')
            close_braces = json_str.count('}')
            
            if open_braces > close_braces:
                missing = open_braces - close_braces
                json_str = json_str + ('\n}' * missing)
                logger.debug(f"🔧 Añadidas {missing} llaves de cierre")
            
            # 2. Remover trailing commas
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            # 3. Intentar parsear
            json.loads(json_str)
            return json_str
            
        except:
            return None
    
    def _validate_json_structure(self, data: Dict[str, Any]) -> None:
        """
        Valida que el JSON tenga la estructura mínima esperada.
        
        Args:
            data: Dict parseado del JSON
            
        Raises:
            ValueError: Si la estructura no es válida
        """
        # Para agentes E.D.N.360, esperamos al menos un dict
        if not isinstance(data, dict):
            raise ValueError(f"JSON no es un diccionario: {type(data)}")
        
        # Verificar que tenga al menos una clave
        if not data:
            raise ValueError("JSON está vacío")
        
        # Log de validación exitosa
        logger.debug(f"✅ {self.agent_id} - Estructura JSON validada: {len(data)} claves principales")
    
    def _auto_fix_json_response(
        self,
        broken_response: str,
        original_input: Dict[str, Any],
        system_prompt: str,
        user_message: str
    ) -> Dict[str, Any]:
        """
        CORRECCIÓN AUTOMÁTICA: Re-ejecuta el LLM con prompt forzado para corregir JSON.
        
        Esta es la estrategia de último recurso cuando el parseo robusto falla.
        
        Args:
            broken_response: Respuesta original que falló al parsear
            original_input: Input data original
            system_prompt: Prompt del sistema original
            user_message: Mensaje del usuario original
            
        Returns:
            Dict con el output normalizado
        """
        logger.warning(f"🔄 {self.agent_id} - Iniciando corrección automática mediante re-ejecución LLM")
        
        # Crear prompt de corrección forzada
        correction_prompt = f"""# CORRECCIÓN DE FORMATO JSON

La respuesta anterior tenía problemas de formato. Por favor, genera SOLO el JSON válido sin ningún texto adicional.

**REGLAS ESTRICTAS:**
1. Solo JSON puro, sin markdown (sin ``` ni explicaciones)
2. Asegúrate de cerrar todas las llaves y corchetes
3. No incluyas trailing commas
4. Formato compacto pero válido

**RESPUESTA ORIGINAL PROBLEMÁTICA:**
{broken_response[:500]}...

**AHORA GENERA EL JSON CORRECTO COMPLETO:**
"""
        
        try:
            # Re-ejecutar LLM con prompt de corrección
            completion = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                    {"role": "assistant", "content": broken_response[:1000]},  # Contexto parcial
                    {"role": "user", "content": correction_prompt}
                ],
                temperature=0.3,  # Más determinista para corrección
                max_tokens=6000,
                timeout=120
            )
            
            corrected_response = completion.choices[0].message.content
            logger.info(f"🔄 {self.agent_id} - Respuesta de corrección recibida ({len(corrected_response)} chars)")
            
            # Intentar parsear la respuesta corregida
            parsed_json = self._extract_json_from_response_robust(corrected_response)
            
            # Normalizar
            normalized_json = self.normalize_agent_output(parsed_json, original_input)
            
            if "client_context" not in normalized_json:
                raise ValueError("Respuesta corregida no contiene client_context")
            
            return normalized_json
            
        except Exception as e:
            logger.error(f"❌ {self.agent_id} - Auto-corrección falló: {str(e)}")
            raise

    
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
