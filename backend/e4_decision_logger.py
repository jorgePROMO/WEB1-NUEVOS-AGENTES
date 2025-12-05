"""
E4 Decision Logger
==================
Sistema de logging para decisiones del agente E4 basadas en K1

Registra:
1. Qué reglas del K1 se aplicaron
2. Qué decisiones tomó el E4 (volumen, intensidad, ejercicios)
3. Por qué eligió esas opciones
4. Traducción de abstracto → concreto aplicada
5. Resultado de validación

Los logs se persisten en MongoDB para auditoría y mejora continua.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorClient
import os
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class E4DecisionLog(BaseModel):
    """Modelo de log de decisión E4"""
    log_id: str  # UUID del log
    timestamp: datetime
    user_id: str
    plan_id: str  # ID del plan generado
    
    # Perfil del usuario
    perfil_usuario: Dict[str, Any]
    
    # Reglas K1 aplicadas
    k1_rules_applied: Dict[str, Any]
    
    # Decisiones E4
    e4_decisions: Dict[str, Any]
    
    # Validación
    validation_result: Dict[str, Any]
    
    # Traducción abstracto → concreto
    traduccion: Dict[str, Any]
    
    # Metadata
    e4_version: str = "4.0_k1"
    k1_version: str = "1.0.0"
    intentos: int = 1
    exito: bool = True

class E4DecisionLogger:
    """Logger para decisiones del E4"""
    
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.collection_name = "e4_decision_logs"
        
    async def _get_collection(self):
        """Obtiene la colección de logs"""
        if self.mongo_client is None:
            mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
            self.mongo_client = AsyncIOMotorClient(mongo_url)
            self.db = self.mongo_client['edn360_app']
        
        return self.db[self.collection_name]
    
    async def log_decision(
        self,
        user_id: str,
        plan_id: str,
        perfil_usuario: Dict,
        k1_rules: Dict,
        e4_response: Dict,
        validation_result: Dict,
        traduccion: Dict,
        intentos: int = 1,
        exito: bool = True
    ) -> str:
        """
        Registra una decisión del E4
        
        Args:
            user_id: ID del usuario
            plan_id: ID del plan generado
            perfil_usuario: Perfil del usuario (nivel, objetivo, etc.)
            k1_rules: Reglas K1 que se aplicaron
            e4_response: Respuesta completa del E4
            validation_result: Resultado de la validación
            traduccion: Traducción abstracto → concreto
            intentos: Número de intentos necesarios
            exito: Si la generación fue exitosa
            
        Returns:
            log_id: ID del log creado
        """
        from uuid import uuid4
        
        log_id = str(uuid4())
        
        # Extraer decisiones clave del E4
        e4_decisions = self._extract_e4_decisions(e4_response)
        
        log_entry = {
            "log_id": log_id,
            "timestamp": datetime.now(timezone.utc),
            "user_id": user_id,
            "plan_id": plan_id,
            "perfil_usuario": perfil_usuario,
            "k1_rules_applied": k1_rules,
            "e4_decisions": e4_decisions,
            "validation_result": validation_result,
            "traduccion": traduccion,
            "e4_version": "4.0_k1",
            "k1_version": "1.0.0",
            "intentos": intentos,
            "exito": exito
        }
        
        try:
            collection = await self._get_collection()
            await collection.insert_one(log_entry)
            
            logger.info(f"✅ Log E4 guardado: {log_id}")
            return log_id
            
        except Exception as e:
            logger.error(f"❌ Error guardando log E4: {e}")
            raise
    
    def _extract_e4_decisions(self, e4_response: Dict) -> Dict:
        """Extrae las decisiones clave del E4"""
        plan = e4_response.get('training_plan', {})
        
        decisions = {
            "training_type": plan.get('training_type'),
            "days_per_week": plan.get('days_per_week'),
            "goal": plan.get('goal'),
            "num_sessions": len(plan.get('sessions', [])),
            "sessions_summary": []
        }
        
        # Resumir cada sesión
        for session in plan.get('sessions', []):
            session_summary = {
                "session_id": session.get('id'),
                "session_name": session.get('name'),
                "focus": session.get('focus', []),
                "num_exercises": 0,
                "patrones_cubiertos": [],
                "tipos_ejercicios": [],
                "volumenes": [],
                "intensidades": [],
                "metodos": [],
                "k1_decisions": session.get('k1_decisions', {})
            }
            
            # Analizar bloques
            for block in session.get('blocks', []):
                exercises = block.get('exercises', [])
                session_summary["num_exercises"] += len(exercises)
                
                # Extraer patrones y tipos
                for exercise in exercises:
                    patron = exercise.get('patron')
                    if patron and patron not in session_summary["patrones_cubiertos"]:
                        session_summary["patrones_cubiertos"].append(patron)
                    
                    tipo = exercise.get('tipo')
                    if tipo and tipo not in session_summary["tipos_ejercicios"]:
                        session_summary["tipos_ejercicios"].append(tipo)
                    
                    vol = exercise.get('volumen_abstracto')
                    if vol and vol not in session_summary["volumenes"]:
                        session_summary["volumenes"].append(vol)
                    
                    int_abs = exercise.get('intensidad_abstracta')
                    if int_abs and int_abs not in session_summary["intensidades"]:
                        session_summary["intensidades"].append(int_abs)
                
                # Método del bloque
                metodo = block.get('metodo_entrenamiento')
                if metodo and metodo not in session_summary["metodos"]:
                    session_summary["metodos"].append(metodo)
            
            decisions["sessions_summary"].append(session_summary)
        
        return decisions
    
    async def get_logs_by_user(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Obtiene los logs de decisiones para un usuario
        
        Args:
            user_id: ID del usuario
            limit: Número máximo de logs a retornar
            
        Returns:
            Lista de logs ordenados por fecha descendente
        """
        try:
            collection = await self._get_collection()
            
            logs = await collection.find(
                {"user_id": user_id},
                {"_id": 0}
            ).sort("timestamp", -1).limit(limit).to_list(limit)
            
            return logs
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo logs: {e}")
            return []
    
    async def get_log_by_plan_id(self, plan_id: str) -> Optional[Dict]:
        """
        Obtiene el log de decisión para un plan específico
        
        Args:
            plan_id: ID del plan
            
        Returns:
            Log del plan o None si no existe
        """
        try:
            collection = await self._get_collection()
            
            log = await collection.find_one(
                {"plan_id": plan_id},
                {"_id": 0}
            )
            
            return log
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo log por plan_id: {e}")
            return None
    
    async def get_stats_by_user(self, user_id: str) -> Dict:
        """
        Estadísticas de decisiones E4 para un usuario
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Dict con estadísticas agregadas
        """
        try:
            collection = await self._get_collection()
            
            # Contar total de generaciones
            total = await collection.count_documents({"user_id": user_id})
            
            # Contar exitosas
            exitosas = await collection.count_documents({
                "user_id": user_id,
                "exito": True
            })
            
            # Promedio de intentos
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$group": {
                    "_id": None,
                    "avg_intentos": {"$avg": "$intentos"},
                    "max_intentos": {"$max": "$intentos"}
                }}
            ]
            
            agg_result = await collection.aggregate(pipeline).to_list(1)
            
            avg_intentos = agg_result[0]["avg_intentos"] if agg_result else 0
            max_intentos = agg_result[0]["max_intentos"] if agg_result else 0
            
            # Reglas K1 más aplicadas
            pipeline_rules = [
                {"$match": {"user_id": user_id}},
                {"$unwind": "$e4_decisions.sessions_summary"},
                {"$unwind": "$e4_decisions.sessions_summary.patrones_cubiertos"},
                {"$group": {
                    "_id": "$e4_decisions.sessions_summary.patrones_cubiertos",
                    "count": {"$sum": 1}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            
            patrones_frecuentes = await collection.aggregate(pipeline_rules).to_list(5)
            
            return {
                "total_generaciones": total,
                "generaciones_exitosas": exitosas,
                "tasa_exito": (exitosas / total * 100) if total > 0 else 0,
                "promedio_intentos": round(avg_intentos, 2),
                "max_intentos": max_intentos,
                "patrones_mas_usados": [
                    {"patron": p["_id"], "veces": p["count"]}
                    for p in patrones_frecuentes
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Error obteniendo stats: {e}")
            return {}
    
    async def create_indexes(self):
        """Crea índices para optimizar consultas"""
        try:
            collection = await self._get_collection()
            
            # Índice por user_id y timestamp
            await collection.create_index([
                ("user_id", 1),
                ("timestamp", -1)
            ])
            
            # Índice por plan_id
            await collection.create_index("plan_id")
            
            logger.info("✅ Índices de e4_decision_logs creados")
            
        except Exception as e:
            logger.error(f"❌ Error creando índices: {e}")
    
    def format_decision_report(self, log: Dict) -> str:
        """Formatea reporte de decisión legible"""
        report = f"""
╔══════════════════════════════════════════════════════════
║ E4 DECISION LOG
╠══════════════════════════════════════════════════════════
║ Log ID: {log.get('log_id')}
║ Plan ID: {log.get('plan_id')}
║ User ID: {log.get('user_id')}
║ Timestamp: {log.get('timestamp')}
╠══════════════════════════════════════════════════════════
║ PERFIL USUARIO:
║   Nivel: {log.get('perfil_usuario', {}).get('nivel_experiencia')}
║   Objetivo: {log.get('perfil_usuario', {}).get('objetivo_principal')}
╠══════════════════════════════════════════════════════════
║ DECISIONES E4:
║   Training Type: {log.get('e4_decisions', {}).get('training_type')}
║   Days/Week: {log.get('e4_decisions', {}).get('days_per_week')}
║   Sesiones: {log.get('e4_decisions', {}).get('num_sessions')}
╠══════════════════════════════════════════════════════════
║ K1 RULES APPLIED:
"""
        
        k1_rules = log.get('k1_rules_applied', {})
        if 'volumen_recomendado' in k1_rules:
            vol = k1_rules['volumen_recomendado']
            report += f"║   Volumen: {vol.get('volumen_por_sesion')}\n"
        
        if 'intensidad_recomendada' in k1_rules:
            int_rec = k1_rules['intensidad_recomendada']
            report += f"║   Intensidad: {int_rec.get('intensidad_carga')}\n"
        
        report += "╠══════════════════════════════════════════════════════════\n"
        report += f"║ VALIDACIÓN:\n"
        
        validation = log.get('validation_result', {})
        report += f"║   Score: {validation.get('score', 0)}/100\n"
        report += f"║   Válido: {'✅' if validation.get('valido') else '❌'}\n"
        report += f"║   Errores: {len(validation.get('errores', []))}\n"
        
        report += "╠══════════════════════════════════════════════════════════\n"
        report += f"║ RESULTADO:\n"
        report += f"║   Éxito: {'✅' if log.get('exito') else '❌'}\n"
        report += f"║   Intentos: {log.get('intentos')}\n"
        report += "╚══════════════════════════════════════════════════════════"
        
        return report


# Singleton instance
_logger_instance = None

def get_logger() -> E4DecisionLogger:
    """Obtiene la instancia singleton del logger"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = E4DecisionLogger()
    return _logger_instance


# Test
if __name__ == "__main__":
    import asyncio
    
    async def test_logger():
        logger_inst = E4DecisionLogger()
        
        # Test log
        test_log_id = await logger_inst.log_decision(
            user_id="test_user_123",
            plan_id="test_plan_456",
            perfil_usuario={
                "nivel_experiencia": "intermedio",
                "objetivo_principal": "hipertrofia"
            },
            k1_rules={
                "volumen_recomendado": {"volumen_por_sesion": "medio"},
                "intensidad_recomendada": {"intensidad_carga": "moderada"}
            },
            e4_response={
                "training_plan": {
                    "training_type": "upper_lower",
                    "days_per_week": 4,
                    "goal": "Hypertrophy",
                    "sessions": []
                }
            },
            validation_result={
                "valido": True,
                "score": 95,
                "errores": []
            },
            traduccion={
                "volumen": {"abstracto": "medio", "concreto": "3-4 series"}
            },
            intentos=1,
            exito=True
        )
        
        print(f"✅ Log creado: {test_log_id}")
        
        # Obtener log
        log = await logger_inst.get_log_by_plan_id("test_plan_456")
        if log:
            print("\n" + logger_inst.format_decision_report(log))
        
        # Stats
        stats = await logger_inst.get_stats_by_user("test_user_123")
        print(f"\n📊 Stats: {stats}")
    
    asyncio.run(test_logger())
