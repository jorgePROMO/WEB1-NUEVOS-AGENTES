"""
Orquestador Principal del Sistema E.D.N.360
Coordina la ejecución secuencial de los 26 agentes
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio
import json

from .models import (
    EDN360Plan,
    PlanType,
    PlanStatus,
    AgentExecution,
    AgentStatus,
    TrainingPlan,
    NutritionPlan,
    FollowUpPlan
)
from .validators import EDN360Validator, log_validation_results
from .client_context_models import ClientContext
from .client_context_utils import (
    initialize_client_context,
    validate_agent_contract,
    validate_agent_input,
    get_agent_requirements,
    client_context_to_dict,
    build_nutrition_llm_context,
    update_nutrition_from_llm_response
)

# Import agents
from .agents.training_initial import (
    E1Analyst, E2CapacityEvaluator, E3AdaptationAnalyst,
    E4ProgramArchitect, E5MicrocycleEngineer, E6ClinicalTechnician,
    E7LoadAnalyst, E8TechnicalAuditor, E9NutritionBridge
)
from .agents.nutrition_initial import (
    N0TriageAnalyst, N1MetabolicAnalyst, N2EnergySelector,
    N3TemplateSnapper, N4AMBSynchronizer, N5TimingDistributor,
    N6MenuGenerator, N7AdherenceCoach, N8Watchdog
)
from .agents.training_followup import (
    ES1Interpreter, ES2PerformanceEvaluator,
    ES3AdjustmentArchitect, ES4ContinuityAuditor
)
from .agents.nutrition_followup import (
    NS1MetabolicInterpreter, NS2EnergyEvaluator,
    NS3MacroAdjuster, NS4NutritionAuditor
)

logger = logging.getLogger(__name__)


def _serialize_datetime_fields(data: Any) -> Any:
    """
    Recursively convert datetime objects to ISO format strings for JSON serialization
    """
    if isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, dict):
        return {key: _serialize_datetime_fields(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_serialize_datetime_fields(item) for item in data]
    else:
        return data


def build_scoped_input_for_agent(agent_id: str, client_context: ClientContext) -> Dict[str, Any]:
    """
    Construye input mínimo para cada agente según su ID.
    
    ARQUITECTURA DE CAJONES (Bloque 1 - E1-E4):
    - E1: Único agente que recibe raw_inputs completos
    - E2-E4: Reciben client_summary + cajones específicos necesarios
    - E5-E9: [Por implementar en Bloque 2]
    
    Esta función elimina la "bola de nieve" de contexto, pasando solo
    la información mínima necesaria a cada agente.
    
    Args:
        agent_id: ID del agente (E1, E2, E3, etc.)
        client_context: ClientContext completo actual
        
    Returns:
        Dict con input reducido para el agente
    """
    from .client_context_models import TrainingData
    
    # ========================================
    # E1 - ÚNICO QUE RECIBE raw_inputs
    # ========================================
    if agent_id == "E1":
        return {
            "meta": client_context.meta.model_dump(),
            "raw_inputs": client_context.raw_inputs.model_dump(),
            "training": TrainingData().model_dump()  # Vacío, E1 inicializa
        }
    
    # ========================================
    # E2 - Recibe client_summary + profile
    # ========================================
    elif agent_id == "E2":
        return {
            "meta": client_context.meta.model_dump(),
            "raw_inputs": {},  # Ya NO recibe raw_inputs
            "training": {
                "client_summary": client_context.training.client_summary,
                "profile": client_context.training.profile,
                "constraints": client_context.training.constraints,
                "prehab": client_context.training.prehab,
                "progress": client_context.training.progress,
                "capacity": None  # Lo que él va a llenar
            }
        }
    
    # ========================================
    # E3 - Recibe client_summary + capacity
    # ========================================
    elif agent_id == "E3":
        return {
            "meta": client_context.meta.model_dump(),
            "raw_inputs": {},  # Ya NO recibe raw_inputs
            "training": {
                "client_summary": client_context.training.client_summary,
                # E3 NO necesita profile completo, solo client_summary es suficiente
                "capacity": client_context.training.capacity,
                "adaptation": None  # Lo que él va a llenar
            }
        }
    
    # ========================================
    # E4 - Recibe client_summary + capacity + adaptation
    # ========================================
    elif agent_id == "E4":
        return {
            "meta": client_context.meta.model_dump(),
            "raw_inputs": {},  # Ya NO recibe raw_inputs
            "training": {
                "client_summary": client_context.training.client_summary,
                # E4 NO necesita profile, solo datos de E2 y E3
                "capacity": client_context.training.capacity,
                "adaptation": client_context.training.adaptation,
                "mesocycle": None  # Lo que él va a llenar
            }
        }
    
    # ========================================
    # E5 - ENGINEER (Generador de Sesiones)
    # ========================================
    elif agent_id == "E5":
        return {
            "meta": client_context.meta.model_dump(),
            "raw_inputs": {},
            "training": {
                "client_summary": client_context.training.client_summary,
                "capacity": client_context.training.capacity,
                "adaptation": client_context.training.adaptation,
                "mesocycle": client_context.training.mesocycle,
                "sessions": None  # Lo que él va a llenar
            }
        }
    
    # ========================================
    # E6 - SAFETY OFFICER (Validador de Seguridad)
    # ========================================
    elif agent_id == "E6":
        return {
            "meta": client_context.meta.model_dump(),
            "raw_inputs": {},
            "training": {
                "client_summary": client_context.training.client_summary,
                "constraints": client_context.training.constraints,
                "prehab": client_context.training.prehab,
                "sessions": client_context.training.sessions,
                "safe_sessions": None  # Lo que él va a llenar
            }
        }
    
    # ========================================
    # E7 - FORMATTER (Formateador de Plan)
    # ========================================
    elif agent_id == "E7":
        return {
            "meta": client_context.meta.model_dump(),
            "raw_inputs": {},
            "training": {
                "client_summary": client_context.training.client_summary,
                "mesocycle": client_context.training.mesocycle,
                "safe_sessions": client_context.training.safe_sessions,
                "formatted_plan": None  # Lo que él va a llenar
            }
        }
    
    # ========================================
    # E8 - AUDITOR (Control de Calidad)
    # ========================================
    elif agent_id == "E8":
        return {
            "meta": client_context.meta.model_dump(),
            "raw_inputs": {},
            "training": {
                "client_summary": client_context.training.client_summary,
                "constraints": client_context.training.constraints,
                "mesocycle": client_context.training.mesocycle,
                "formatted_plan": client_context.training.formatted_plan,
                "audit": None  # Lo que él va a llenar
            }
        }
    
    # ========================================
    # E9 - BRIDGE (Puente a Nutrición)
    # ========================================
    elif agent_id == "E9":
        return {
            "meta": client_context.meta.model_dump(),
            "raw_inputs": {},
            "training": {
                "client_summary": client_context.training.client_summary,
                "formatted_plan": client_context.training.formatted_plan,
                "bridge_for_nutrition": None  # Lo que él va a llenar
            }
        }
    
    # ========================================
    # Agente no reconocido
    # ========================================
    else:
        logger.warning(f"⚠️ {agent_id} no tiene input definido en arquitectura de cajones")
        return client_context_to_dict(client_context)


class EDN360Orchestrator:
    """Orquestador principal que ejecuta la cadena de agentes"""
    
    def __init__(self):
        """Inicializa el orquestador con todos los agentes y carga las bases de conocimiento"""
        
        # Training Initial Agents (E1-E9)
        self.training_initial_agents = [
            E1Analyst(),
            E2CapacityEvaluator(),
            E3AdaptationAnalyst(),
            E4ProgramArchitect(),
            E5MicrocycleEngineer(),
            E6ClinicalTechnician(),
            E7LoadAnalyst(),
            E8TechnicalAuditor(),
            E9NutritionBridge(),
        ]
        
        # Nutrition Initial Agents (N0-N8)
        self.nutrition_initial_agents = [
            N0TriageAnalyst(),
            N1MetabolicAnalyst(),
            N2EnergySelector(),
            N3TemplateSnapper(),
            N4AMBSynchronizer(),
            N5TimingDistributor(),
            N6MenuGenerator(),
            N7AdherenceCoach(),
            N8Watchdog(),
        ]
        
        # Training Followup Agents (ES1-ES4)
        self.training_followup_agents = [
            ES1Interpreter(),
            ES2PerformanceEvaluator(),
            ES3AdjustmentArchitect(),
            ES4ContinuityAuditor(),
        ]
        
        # Nutrition Followup Agents (NS1-NS4)
        self.nutrition_followup_agents = [
            NS1MetabolicInterpreter(),
            NS2EnergyEvaluator(),
            NS3MacroAdjuster(),
            NS4NutritionAuditor(),
        ]
        
        self.validator = EDN360Validator()
        
        # Cargar las bases de conocimiento en memoria
        self.knowledge_bases = self._load_knowledge_bases()
        logger.info(f"✅ Bases de conocimiento cargadas: Training KB ({len(self.knowledge_bases['training'])} chars), Nutrition KB ({len(self.knowledge_bases['nutrition'])} chars)")
    
    def _load_knowledge_bases(self) -> Dict[str, str]:
        """
        Carga las bases de conocimiento desde el sistema de archivos
        
        Returns:
            Dict con las bases de conocimiento de training y nutrition
        """
        import os
        
        kb_dir = os.path.join(os.path.dirname(__file__), "knowledge_bases")
        
        training_kb_path = os.path.join(kb_dir, "training_knowledge_base_v1.0.txt")
        nutrition_kb_path = os.path.join(kb_dir, "nutrition_knowledge_base_v1.0.txt")
        
        try:
            with open(training_kb_path, 'r', encoding='utf-8') as f:
                training_kb = f.read()
            
            with open(nutrition_kb_path, 'r', encoding='utf-8') as f:
                nutrition_kb = f.read()
            
            return {
                "training": training_kb,
                "nutrition": nutrition_kb
            }
        except Exception as e:
            logger.error(f"❌ Error cargando bases de conocimiento: {str(e)}")
            # Retornar diccionario vacío si hay error
            return {
                "training": "",
                "nutrition": ""
            }
    
    async def execute_training_pipeline(
        self,
        questionnaire_data: Dict[str, Any],
        client_id: str,
        version: int = 1
    ) -> Dict[str, Any]:
        """
        Ejecuta SOLO el pipeline de entrenamiento (E1-E9) de forma independiente.
        
        NUEVA ARQUITECTURA (Fase 2 completada):
        - Inicializa client_context desde cuestionario
        - Ejecuta E1 → E2 → E3 → E4 → E5 → E6 → E7 → E8 → E9
        - Devuelve client_context con training.* completo
        - Puede usarse de forma independiente o como input para nutrición
        
        Args:
            questionnaire_data: Datos del cuestionario del cliente
            client_id: ID único del cliente
            version: Número de versión del plan (default: 1)
            
        Returns:
            Dict con:
                - success: bool
                - client_context: ClientContext con training completo
                - executions: lista de ejecuciones de cada agente
        """
        logger.info(f"🏋️ EJECUTANDO PIPELINE DE ENTRENAMIENTO INDEPENDIENTE")
        logger.info(f"   Cliente: {client_id}, Versión: {version}")
        
        # Ejecutar pipeline de entrenamiento (incluye inicialización de client_context)
        result = await self._execute_training_initial(questionnaire_data, previous_plan=None)
        
        return result
    
    async def execute_nutrition_pipeline(
        self,
        client_context: ClientContext
    ) -> Dict[str, Any]:
        """
        Ejecuta SOLO el pipeline de nutrición (N0-N8) de forma independiente.
        
        NUEVA ARQUITECTURA (Fase N2):
        - Recibe client_context con training.* ya completo
        - Ejecuta N0 → N1 → N2 → N3 → N4 → N5 → N6 → N7 → N8
        - Devuelve client_context con nutrition.* completo
        - Puede ejecutarse sobre cualquier client_context con training completo
        
        Args:
            client_context: ClientContext con training completo (salida de E1-E9)
            
        Returns:
            Dict con:
                - success: bool
                - client_context: ClientContext con nutrition completo
                - executions: lista de ejecuciones de cada agente
        """
        logger.info(f"🥗 EJECUTANDO PIPELINE DE NUTRICIÓN INDEPENDIENTE")
        logger.info(f"   Client: {client_context.meta.client_id}, Snapshot: {client_context.meta.snapshot_id}")
        
        # Ejecutar pipeline de nutrición
        result = await self._execute_nutrition_initial(client_context)
        
        return result
    
    async def generate_initial_plan(
        self,
        questionnaire_data: Dict[str, Any],
        client_data: Dict[str, Any],
        plan_id: str
    ) -> Dict[str, Any]:
        """
        Genera un plan inicial completo (Entrenamiento + Nutrición) en cadena.
        
        NUEVA ARQUITECTURA:
        - Ejecuta primero training pipeline (E1-E9)
        - Luego ejecuta nutrition pipeline (N0-N8) sobre el resultado
        - Devuelve client_context completo con training.* y nutrition.*
        
        Args:
            questionnaire_data: Datos del cuestionario inicial
            client_data: Datos del cliente
            plan_id: ID del plan
            
        Returns:
            Dict con el plan completo generado
        """
        logger.info(f"🚀 Iniciando generación de plan completo: {plan_id}")
        start_time = datetime.now()
        
        try:
            # Fase 1: Ejecutar pipeline de entrenamiento (E1-E9)
            logger.info("=" * 80)
            logger.info("📋 FASE 1: ENTRENAMIENTO (E1-E9)")
            logger.info("=" * 80)
            
            client_id = client_data.get("client_id", plan_id)
            training_result = await self.execute_training_pipeline(
                questionnaire_data=questionnaire_data,
                client_id=client_id,
                version=1
            )
            
            if not training_result["success"]:
                raise Exception(f"Error en fase entrenamiento: {training_result.get('error')}")
            
            client_context_after_training = training_result["client_context"]
            
            # Fase 2: Ejecutar pipeline de nutrición (N0-N8)
            logger.info("")
            logger.info("=" * 80)
            logger.info("🥗 FASE 2: NUTRICIÓN (N0-N8)")
            logger.info("=" * 80)
            
            nutrition_result = await self.execute_nutrition_pipeline(
                client_context=client_context_after_training
            )
            
            if not nutrition_result["success"]:
                raise Exception(f"Error en fase nutrición: {nutrition_result.get('error')}")
            
            client_context_final = nutrition_result["client_context"]
            
            # Calcular duración total
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "plan_id": plan_id,
                "client_context": client_context_to_dict(client_context_final),
                "training_executions": training_result["executions"],
                "nutrition_executions": nutrition_result["executions"],
                "total_duration_seconds": duration,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info("")
            logger.info("=" * 80)
            logger.info(f"✅ PLAN COMPLETO GENERADO EN {duration:.2f}s")
            logger.info("=" * 80)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generando plan inicial: {str(e)}")
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": False,
                "plan_id": plan_id,
                "error": str(e),
                "total_duration_seconds": duration
            }
    
    async def generate_followup_plan(
        self,
        followup_questionnaire: Dict[str, Any],
        previous_plan: Dict[str, Any],
        client_data: Dict[str, Any],
        plan_id: str
    ) -> Dict[str, Any]:
        """
        Genera un plan de seguimiento mensual
        
        Args:
            followup_questionnaire: Cuestionario de seguimiento
            previous_plan: Plan anterior del cliente
            client_data: Datos del cliente
            plan_id: ID del nuevo plan
            
        Returns:
            Dict con el plan de seguimiento
        """
        logger.info(f"🔄 Iniciando generación de seguimiento: {plan_id}")
        start_time = datetime.now()
        
        try:
            # Fase 1: Seguimiento Entrenamiento (ES1-ES4)
            logger.info("📋 Fase 1: Seguimiento Entrenamiento (ES1-ES4)")
            training_followup = await self._execute_training_followup(
                followup_questionnaire,
                previous_plan["training_plan"]
            )
            
            if not training_followup["success"]:
                raise Exception(f"Error en seguimiento entrenamiento: {training_followup.get('error')}")
            
            # Fase 2: Seguimiento Nutrición (NS1-NS4)
            logger.info("🍎 Fase 2: Seguimiento Nutrición (NS1-NS4)")
            nutrition_followup = await self._execute_nutrition_followup(
                followup_questionnaire,
                previous_plan["nutrition_plan"],
                training_followup["handoff_data"]  # Output de ES4
            )
            
            if not nutrition_followup["success"]:
                raise Exception(f"Error en seguimiento nutrición: {nutrition_followup.get('error')}")
            
            # Validación de ajustes
            logger.info("✅ Validando ajustes de seguimiento")
            valid, conditions = self.validator.validate_followup_conditions(
                irg=training_followup["plan_data"].get("irg", 7),
                adherencia_pct=followup_questionnaire.get("adherencia_pct", 85),
                peso_perdido_kg=followup_questionnaire.get("peso_perdido_kg", 0),
                semanas=4
            )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "plan_id": plan_id,
                "training_adjustments": training_followup["plan_data"],
                "nutrition_adjustments": nutrition_followup["plan_data"],
                "agent_executions": training_followup["executions"] + nutrition_followup["executions"],
                "validation": {
                    "can_intensify": valid,
                    "conditions": conditions
                },
                "total_duration_seconds": duration,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Plan de seguimiento completado en {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error generando seguimiento: {str(e)}")
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": False,
                "plan_id": plan_id,
                "error": str(e),
                "total_duration_seconds": duration
            }
    
    async def _execute_training_initial(
        self,
        questionnaire_data: Dict[str, Any],
        previous_plan: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta la cadena de agentes E1-E9 usando client_context unificado
        
        ARQUITECTURA NUEVA (Fase 2):
        - Inicializa client_context con meta + raw_inputs
        - Pasa el MISMO client_context a TODOS los agentes
        - Cada agente modifica SOLO su campo en training
        - Valida contratos antes y después de cada agente
        
        Args:
            questionnaire_data: Datos del cuestionario del cliente
            previous_plan: (Opcional) Plan previo para progresión/referencia
        """
        executions = []
        
        # PASO 1: Inicializar client_context
        logger.info("  🔧 Inicializando client_context...")
        
        # Determinar si es seguimiento o inicial
        is_followup = previous_plan is not None
        version = questionnaire_data.get("version", 1) if not is_followup else (previous_plan.get("meta", {}).get("version", 1) + 1)
        
        # Serializar plan previo si existe
        previous_training = None
        if previous_plan:
            logger.info("  📋 Plan previo incluido como contexto para progresión")
            previous_training = _serialize_datetime_fields(previous_plan)
        
        # Inicializar el client_context
        client_context = initialize_client_context(
            client_id=questionnaire_data.get("client_id", "unknown"),
            version=version,
            cuestionario_data=questionnaire_data,
            previous_training=previous_training,
            is_followup=is_followup
        )
        
        logger.info(f"  ✅ client_context inicializado: v{version}, snapshot_id={client_context.meta.snapshot_id}")
        
        # PASO 2: Ejecutar cada agente secuencialmente (E1-E9)
        for agent in self.training_initial_agents:
            logger.info(f"  ▶️ Ejecutando {agent.agent_id} ({agent.agent_name})...")
            
            # VALIDACIÓN PRE-EJECUCIÓN: ¿Tiene los inputs requeridos?
            requirements = get_agent_requirements(agent.agent_id)
            if requirements["requires"]:
                logger.info(f"    🔍 Validando inputs requeridos: {requirements['requires']}")
                from .client_context_utils import validate_agent_input
                valid_input, error_msg = validate_agent_input(
                    agent.agent_id,
                    client_context,
                    requirements["requires"]
                )
                if not valid_input:
                    logger.error(f"  ❌ {agent.agent_id} - Validación de input falló: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "executions": executions
                    }
            
            # EJECUTAR AGENTE con client_context + KB
            # ARQUITECTURA DE CAJONES: E1-E9 usan inputs reducidos
            agents_with_scoped_input = ["E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9"]
            
            if agent.agent_id in agents_with_scoped_input:
                # ARQUITECTURA DE CAJONES: Input reducido específico por agente
                agent_input = build_scoped_input_for_agent(agent.agent_id, client_context)
                logger.info(f"    📦 Usando input reducido (cajones) para {agent.agent_id}")
                
                # client_context_before = input que el agente recibe (para validación)
                client_context_before = ClientContext.model_validate(agent_input)
            else:
                # Agente legacy: pasar formato antiguo (e1_output, e2_output, etc.)
                logger.info(f"    ⚠️ Preparando input legacy para {agent.agent_id}")
                
                # Para legacy, client_context_before es el contexto completo
                client_context_before = ClientContext.model_validate(client_context.model_dump())
                
                # Construir outputs en formato legacy
                # E1 llena múltiples campos, así que consolidamos todo
                legacy_outputs = {}
                
                # E1 output: consolidar profile, constraints, prehab, progress
                if client_context.training.profile:
                    legacy_outputs["E1"] = {
                        "profile": client_context.training.profile,
                        "constraints": client_context.training.constraints,
                        "prehab": client_context.training.prehab,
                        "progress": client_context.training.progress
                    }
                
                # E2-E9: mapeo directo
                field_map = {
                    "E2": "capacity",
                    "E3": "adaptation",
                    "E4": "mesocycle",
                    "E5": "sessions",
                    "E6": "safe_sessions",
                    "E7": "formatted_plan",
                    "E8": "audit",
                    "E9": "bridge_for_nutrition"
                }
                
                for agent_num, field in field_map.items():
                    value = getattr(client_context.training, field, None)
                    if value:
                        legacy_outputs[agent_num] = value
                
                # Preparar input según el agente legacy
                if agent.agent_id == "E2":
                    agent_input = {
                        "e1_output": legacy_outputs.get("E1"),
                        **questionnaire_data
                    }
                elif agent.agent_id == "E3":
                    agent_input = {
                        "e1_output": legacy_outputs.get("E1"),
                        "e2_output": legacy_outputs.get("E2")
                    }
                elif agent.agent_id in ["E4", "E6", "E7", "E9"]:
                    # E4-E9 reciben outputs acumulados
                    agent_input = {
                        f"e{i}_output": legacy_outputs.get(f"E{i}")
                        for i in range(1, int(agent.agent_id[1:]))
                    }
                else:
                    agent_input = legacy_outputs
            
            # Decidir si pasar KB según el agente
            # E5-E9 NO necesitan KB completa (optimización de contexto + límite de tokens)
            # Ya tienen toda la info del cliente en el client_context de E1-E4
            agents_without_kb = ["E5", "E6", "E7", "E8", "E9"]
            if agent.agent_id in agents_without_kb:
                kb_to_pass = ""  # Estos agentes no reciben KB
                logger.info(f"    ℹ️ {agent.agent_id} no recibe KB (optimización de contexto)")
            else:
                kb_to_pass = self.knowledge_bases.get("training", "")
            
            result = await agent.execute(
                agent_input,
                knowledge_base=kb_to_pass
            )
            
            # Verificar éxito de ejecución
            if not result["success"]:
                logger.error(f"  ❌ {agent.agent_id} falló: {result.get('error')}")
                return {
                    "success": False,
                    "error": f"{agent.agent_id} falló: {result.get('error')}",
                    "executions": executions
                }
            
            # Actualizar client_context con el output del agente
            # El agente debe devolver el client_context completo actualizado
            if "client_context" in result.get("output", {}):
                output_context = result.get("output", {})["client_context"]
                
                # BLOQUE 1: Filtrar campos para E3 y E4 (contrato estricto de cajones)
                if agent.agent_id == "E3":
                    # E3 solo puede tener: client_summary, capacity, adaptation
                    training = output_context.get("training", {})
                    filtered_training = {
                        k: v for k, v in training.items()
                        if k in ["client_summary", "capacity", "adaptation"]
                    }
                    output_context["training"] = filtered_training
                    logger.info(f"    🔒 E3: Campos filtrados (solo client_summary + capacity + adaptation)")
                
                elif agent.agent_id == "E4":
                    # E4 solo puede tener: client_summary, capacity, adaptation, mesocycle
                    training = output_context.get("training", {})
                    filtered_training = {
                        k: v for k, v in training.items()
                        if k in ["client_summary", "capacity", "adaptation", "mesocycle"]
                    }
                    output_context["training"] = filtered_training
                    logger.info(f"    🔒 E4: Campos filtrados (solo client_summary + capacity + adaptation + mesocycle)")
                
                client_context = ClientContext.model_validate(output_context)
                logger.info(f"  ✅ {agent.agent_id} devolvió client_context actualizado")
            else:
                # Compatibilidad: agente legacy (E2, E3, E4, E6, E7, E9)
                logger.warning(f"  ⚠️ {agent.agent_id} es legacy, simulando output con datos dummy")
                
                # Llenar el campo del agente legacy con datos dummy para que el flujo continúe
                legacy_output = result.get("output", {})
                
                # Mapeo de agentes a campos
                agent_fields = {
                    "E2": "capacity",
                    "E3": "adaptation",
                    "E4": "mesocycle",
                    "E6": "safe_sessions",
                    "E7": "formatted_plan",
                    "E9": "bridge_for_nutrition"
                }
                
                field_to_fill = agent_fields.get(agent.agent_id)
                if field_to_fill:
                    # Crear datos dummy mínimos
                    dummy_data = {
                        "_legacy": True,
                        "_agent_id": agent.agent_id,
                        "_timestamp": datetime.now().isoformat(),
                        "data": legacy_output  # Preservar output legacy si existe
                    }
                    
                    # Actualizar el campo en client_context
                    setattr(client_context.training, field_to_fill, dummy_data)
                    logger.info(f"    → Campo '{field_to_fill}' llenado con datos dummy")
                
                # Este bloque es temporal hasta refactorizar todos los agentes
            
            # VALIDACIÓN POST-EJECUCIÓN: ¿Llenó sus campos? ¿No modificó otros?
            logger.info(f"    🔍 Validando contrato de {agent.agent_id}...")
            valid_contract, errors = validate_agent_contract(
                agent.agent_id,
                client_context_before,
                client_context
            )
            
            if not valid_contract:
                logger.error(f"  ❌ {agent.agent_id} - Violación de contrato:")
                for error in errors:
                    logger.error(f"      • {error}")
                return {
                    "success": False,
                    "error": f"{agent.agent_id} violó su contrato: {'; '.join(errors)}",
                    "executions": executions
                }
            
            logger.info(f"  ✅ {agent.agent_id} completado y validado")
            executions.append(result)
        
        # PASO 3: Retornar resultado con client_context completo
        logger.info("  🎉 Cadena de agentes E1-E9 completada exitosamente")
        
        return {
            "success": True,
            "client_context": client_context_to_dict(client_context),
            "plan_data": client_context.training.model_dump(),  # Para compatibilidad con código existente
            "bridge_data": client_context.training.bridge_for_nutrition,  # Para N0
            "executions": executions
        }
    
    async def _execute_nutrition_initial(
        self,
        client_context: ClientContext
    ) -> Dict[str, Any]:
        """
        Ejecuta la cadena de agentes N0-N8 usando client_context unificado.
        
        NUEVA ARQUITECTURA (Fase N2):
        - Recibe client_context con training.* ya completo (debe tener training.bridge_for_nutrition)
        - Ejecuta N0 → N1 → N2 → N3 → N4 → N5 → N6 → N7 → N8
        - Cada agente modifica SOLO nutrition.*
        - Usa misma validación que entrenamiento (validate_agent_contract)
        - Devuelve client_context con nutrition.* completo
        
        Args:
            client_context: ClientContext con training completo (salida de E1-E9)
            
        Returns:
            Dict con:
                - success: bool
                - client_context: ClientContext actualizado con nutrition.*
                - executions: list de resultados de cada agente
        """
        logger.info("  🥗 INICIANDO PIPELINE DE NUTRICIÓN (N0-N8)")
        logger.info("  ═══════════════════════════════════════════")
        
        # Verificar que training.bridge_for_nutrition existe
        if client_context.training.bridge_for_nutrition is None:
            logger.error("  ❌ FALTA training.bridge_for_nutrition (debe ser generado por E9)")
            return {
                "success": False,
                "error": "Cannot execute nutrition without training.bridge_for_nutrition from E9",
                "client_context": None,
                "executions": []
            }
        
        logger.info(f"  ✅ training.bridge_for_nutrition detectado")
        
        executions = []
        
        # Ejecutar agentes N0-N8 secuencialmente
        for agent in self.nutrition_initial_agents:
            logger.info(f"  ▶️ Ejecutando {agent.agent_id} ({agent.agent_name})...")
            
            # Guardar estado antes para validación de contrato
            client_context_before = ClientContext.model_validate(
                client_context.model_dump()
            )
            
            # VALIDACIÓN PRE-EJECUCIÓN: Verificar inputs requeridos
            requirements = get_agent_requirements(agent.agent_id)
            
            if requirements.get("requires"):
                logger.info(f"    🔍 Validando inputs requeridos: {requirements['requires']}")
                valid_input, error_msg = validate_agent_input(
                    agent.agent_id,
                    client_context,
                    requirements["requires"]
                )
                if not valid_input:
                    logger.error(f"  ❌ {agent.agent_id} - Validación de input falló: {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg,
                        "client_context": client_context,
                        "executions": executions
                    }
            
            # Preparar input: VISTA COMPACTA para agentes N (sin training.sessions pesado)
            # Los agentes N NO necesitan ver cada ejercicio del plan de entrenamiento
            # Trabajan principalmente con training.bridge_for_nutrition
            agent_input = build_nutrition_llm_context(client_context)
            
            # Decidir si pasar KB de nutrición
            # OPTIMIZACIÓN: Solo N1, N2, N3 reciben KB (son los que más la necesitan)
            # N0 lee del cuestionario, N4-N8 ya tienen todo en client_context
            agents_with_kb = ["N1", "N2", "N3"]
            if agent.agent_id in agents_with_kb:
                kb_to_pass = self.knowledge_bases.get("nutrition", "")
            else:
                kb_to_pass = ""
                logger.info(f"    ℹ️ {agent.agent_id} no recibe KB (optimización de contexto)")
            
            # EJECUTAR AGENTE
            result = await agent.execute(
                agent_input,
                knowledge_base=kb_to_pass
            )
            
            # Verificar éxito de ejecución
            if not result["success"]:
                logger.error(f"  ❌ {agent.agent_id} falló: {result.get('error')}")
                return {
                    "success": False,
                    "error": f"{agent.agent_id} falló: {result.get('error')}",
                    "client_context": client_context,
                    "executions": executions
                }
            
            # Actualizar SOLO los campos específicos de nutrition.* según el contrato del agente
            # SOLO se copian los campos definidos en AGENT_FIELD_MAPPING[agent_id]["fills"]
            # Esto evita que el LLM modifique campos de otros agentes
            if "client_context" in result.get("output", {}):
                try:
                    client_context = update_nutrition_from_llm_response(
                        agent_id=agent.agent_id,
                        client_context_real=client_context,
                        llm_response=result["output"]
                    )
                    logger.info(f"  ✅ {agent.agent_id} actualizó nutrition.* correctamente")
                except Exception as e:
                    logger.error(f"  ❌ {agent.agent_id} - Error actualizando nutrition: {e}")
                    return {
                        "success": False,
                        "error": f"{agent.agent_id} update error: {e}",
                        "client_context": client_context,
                        "executions": executions
                    }
            else:
                logger.error(f"  ❌ {agent.agent_id} no devolvió client_context")
                return {
                    "success": False,
                    "error": f"{agent.agent_id} did not return client_context",
                    "client_context": client_context,
                    "executions": executions
                }
            
            # VALIDACIÓN POST-EJECUCIÓN: Verificar contrato
            logger.info(f"    🔍 Validando contrato de {agent.agent_id}...")
            valid_contract, contract_errors = validate_agent_contract(
                agent.agent_id,
                client_context_before,
                client_context
            )
            
            if not valid_contract:
                logger.error(f"  ❌ {agent.agent_id} violó su contrato:")
                for error in contract_errors:
                    logger.error(f"     - {error}")
                return {
                    "success": False,
                    "error": f"{agent.agent_id} contract violation: {contract_errors}",
                    "client_context": client_context,
                    "executions": executions
                }
            
            logger.info(f"  ✅ {agent.agent_id} completado y validado")
            executions.append(result)
        
        logger.info("  ═══════════════════════════════════════════")
        logger.info("  🎉 PIPELINE DE NUTRICIÓN COMPLETADO")
        
        return {
            "success": True,
            "client_context": client_context,
            "executions": executions
        }
    
    async def _execute_training_followup(
        self,
        followup_data: Dict[str, Any],
        previous_training_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta la cadena ES1-ES4"""
        executions = []
        outputs = {}
        
        for agent in self.training_followup_agents:
            logger.info(f"  ▶️ Ejecutando {agent.agent_id}...")
            
            agent_input = {
                "followup_questionnaire": followup_data,
                "previous_plan": previous_training_plan,
                **{f"es{i}_output": outputs.get(f"ES{i}") for i in range(1, int(agent.agent_id[2:]))}
            }
            
            result = await agent.execute(agent_input, knowledge_base=self.knowledge_bases.get("training", ""))
            
            if result["success"]:
                outputs[agent.agent_id] = result["output"]
                logger.info(f"  ✅ {agent.agent_id} completado")
            else:
                return {
                    "success": False,
                    "error": f"{agent.agent_id} falló",
                    "executions": executions
                }
            
            executions.append(result)
        
        return {
            "success": True,
            "plan_data": outputs,
            "handoff_data": outputs.get("ES4"),
            "executions": executions
        }
    
    async def _execute_nutrition_followup(
        self,
        followup_data: Dict[str, Any],
        previous_nutrition_plan: Dict[str, Any],
        training_handoff: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta la cadena NS1-NS4"""
        executions = []
        outputs = {}
        
        for agent in self.nutrition_followup_agents:
            logger.info(f"  ▶️ Ejecutando {agent.agent_id}...")
            
            agent_input = {
                "followup_questionnaire": followup_data,
                "previous_plan": previous_nutrition_plan,
                "training_handoff": training_handoff,
                **{f"ns{i}_output": outputs.get(f"NS{i}") for i in range(1, int(agent.agent_id[2:]))}
            }
            
            result = await agent.execute(agent_input, knowledge_base=self.knowledge_bases.get("nutrition", ""))
            
            if result["success"]:
                outputs[agent.agent_id] = result["output"]
                logger.info(f"  ✅ {agent.agent_id} completado")
            else:
                return {
                    "success": False,
                    "error": f"{agent.agent_id} falló",
                    "executions": executions
                }
            
            executions.append(result)
        
        return {
            "success": True,
            "plan_data": outputs,
            "executions": executions
        }
