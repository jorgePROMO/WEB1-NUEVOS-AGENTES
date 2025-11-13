"""
Orquestador Principal del Sistema E.D.N.360
Coordina la ejecución secuencial de los 26 agentes
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio

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

# Import agents
from .agents.training_initial import (
    E1Analyst, E2CapacityEvaluator, E3AdaptationAnalyst,
    E4ProgramArchitect, E5MicrocycleEngineer, E6ClinicalTechnician,
    E7LoadAnalyst, E8TechnicalAuditor, E9NutritionBridge
)
from .agents.nutrition_initial import (
    N0Triage, N1MetabolicAnalyst, N2EnergySelector,
    N3TemplateSnap, N4AMBSynchronizer, N5TimingDistributor,
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


class EDN360Orchestrator:
    """Orquestador principal que ejecuta la cadena de agentes"""
    
    def __init__(self):
        """Inicializa el orquestador con todos los agentes"""
        
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
            N0Triage(),
            N1MetabolicAnalyst(),
            N2EnergySelector(),
            N3TemplateSnap(),
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
    
    async def generate_initial_plan(
        self,
        questionnaire_data: Dict[str, Any],
        client_data: Dict[str, Any],
        plan_id: str
    ) -> Dict[str, Any]:
        """
        Genera un plan inicial completo (Entrenamiento + Nutrición)
        
        Args:
            questionnaire_data: Datos del cuestionario inicial
            client_data: Datos del cliente
            plan_id: ID del plan
            
        Returns:
            Dict con el plan completo generado
        """
        logger.info(f"🚀 Iniciando generación de plan inicial: {plan_id}")
        start_time = datetime.now()
        
        try:
            # Fase 1: Ejecutar agentes de entrenamiento (E1-E9)
            logger.info("📋 Fase 1: Entrenamiento Inicial (E1-E9)")
            training_result = await self._execute_training_initial(questionnaire_data)
            
            if not training_result["success"]:
                raise Exception(f"Error en fase entrenamiento: {training_result.get('error')}")
            
            # Fase 2: Ejecutar agentes de nutrición (N0-N8)
            logger.info("🍎 Fase 2: Nutrición Inicial (N0-N8)")
            nutrition_result = await self._execute_nutrition_initial(
                questionnaire_data,
                training_result["bridge_data"]  # Output de E9
            )
            
            if not nutrition_result["success"]:
                raise Exception(f"Error en fase nutrición: {nutrition_result.get('error')}")
            
            # Validación completa del plan
            logger.info("✅ Validando plan completo")
            valid, errors, warnings = self.validator.validate_complete_plan(
                training_result["plan_data"],
                nutrition_result["plan_data"],
                client_data
            )
            
            log_validation_results(plan_id, errors, warnings)
            
            if not valid:
                logger.error(f"❌ Plan tiene errores de validación: {errors}")
                # Aún así retornamos el plan pero marcado con errores
            
            # Calcular duración total
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                "success": True,
                "plan_id": plan_id,
                "training_plan": training_result["plan_data"],
                "nutrition_plan": nutrition_result["plan_data"],
                "agent_executions": training_result["executions"] + nutrition_result["executions"],
                "validation": {
                    "valid": valid,
                    "errors": errors,
                    "warnings": warnings
                },
                "total_duration_seconds": duration,
                "generated_at": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Plan inicial completado en {duration:.2f}s")
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
        questionnaire_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta la cadena de agentes E1-E9"""
        executions = []
        current_data = questionnaire_data
        outputs = {}
        
        for agent in self.training_initial_agents:
            logger.info(f"  ▶️ Ejecutando {agent.agent_id}...")
            
            # Preparar input según el agente
            if agent.agent_id == "E1":
                agent_input = current_data
            elif agent.agent_id == "E2":
                # E2 espera el output de E1 envuelto en "e1_output"
                agent_input = {
                    "e1_output": outputs.get("E1"),
                    **questionnaire_data
                }
            elif agent.agent_id == "E3":
                # E3 espera outputs de E1 y E2 envueltos
                agent_input = {
                    "e1_output": outputs.get("E1"),
                    "e2_output": outputs.get("E2")
                }
            else:
                # E4-E9 reciben outputs acumulados envueltos
                agent_input = {
                    f"e{i}_output": outputs.get(f"E{i}")
                    for i in range(1, int(agent.agent_id[1:]))
                }
            
            # Ejecutar agente
            result = await agent.execute(agent_input)
            
            # Guardar resultado
            if result["success"]:
                outputs[agent.agent_id] = result["output"]
                logger.info(f"  ✅ {agent.agent_id} completado")
            else:
                logger.error(f"  ❌ {agent.agent_id} falló: {result.get('error')}")
                return {
                    "success": False,
                    "error": f"{agent.agent_id} falló: {result.get('error')}",
                    "executions": executions
                }
            
            executions.append(result)
        
        return {
            "success": True,
            "plan_data": outputs,
            "bridge_data": outputs.get("E9"),  # Para pasar a nutrición
            "executions": executions
        }
    
    async def _execute_nutrition_initial(
        self,
        questionnaire_data: Dict[str, Any],
        training_bridge_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta la cadena de agentes N0-N8"""
        executions = []
        outputs = {}
        
        for agent in self.nutrition_initial_agents:
            logger.info(f"  ▶️ Ejecutando {agent.agent_id}...")
            
            # Preparar input
            if agent.agent_id == "N0":
                agent_input = {
                    **questionnaire_data,
                    "training_bridge": training_bridge_data
                }
            else:
                # N1-N8 reciben todos los outputs anteriores desempaquetados
                agent_input = {
                    **questionnaire_data,
                    "training_bridge": training_bridge_data
                }
                for i in range(0, int(agent.agent_id[1:])):
                    prev_output = outputs.get(f"N{i}", {})
                    agent_input.update(prev_output)
            
            # Ejecutar agente
            result = await agent.execute(agent_input)
            
            if result["success"]:
                outputs[agent.agent_id] = result["output"]
                logger.info(f"  ✅ {agent.agent_id} completado")
            else:
                logger.error(f"  ❌ {agent.agent_id} falló")
                return {
                    "success": False,
                    "error": f"{agent.agent_id} falló: {result.get('error')}",
                    "executions": executions
                }
            
            executions.append(result)
        
        return {
            "success": True,
            "plan_data": outputs,
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
            
            result = await agent.execute(agent_input)
            
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
            
            result = await agent.execute(agent_input)
            
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
