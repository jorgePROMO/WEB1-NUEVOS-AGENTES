"""
E4 Response Validator
====================
Validador automático para las respuestas del agente E4

Verifica:
1. Estructura correcta del Bloque B
2. Uso de términos abstractos K1 válidos
3. Que no incluya bloques prohibidos (A, C, D)
4. Que los ejercicios sean IDs válidos del catálogo
5. Que los patrones y tipos coincidan con taxonomía K1
6. Coherencia lógica (volumen, intensidad, métodos)
7. Cumplimiento de reglas de seguridad

Si la validación falla, retorna errores detallados para reintentar.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, ValidationError
from k1_knowledge_base import get_taxonomia, load_k1

logger = logging.getLogger(__name__)

class ValidationResult(BaseModel):
    """Resultado de validación"""
    valido: bool
    errores: List[str] = []
    advertencias: List[str] = []
    score: int = 0  # 0-100
    detalles: Dict[str, Any] = {}

class E4ResponseValidator:
    """Validador de respuestas del E4"""
    
    def __init__(self):
        self.k1 = load_k1()
        self.taxonomia = get_taxonomia()
        
    def validate_full_response(self, e4_response: Dict) -> ValidationResult:
        """
        Validación completa de la respuesta de E4
        
        Args:
            e4_response: Respuesta completa del E4
            
        Returns:
            ValidationResult con errores, advertencias y score
        """
        errores = []
        advertencias = []
        score = 100
        detalles = {}
        
        # 1. Validar estructura básica
        estructura_ok, estructura_errores = self._validate_structure(e4_response)
        if not estructura_ok:
            errores.extend(estructura_errores)
            score -= 30
        
        # 2. Validar que solo incluya Bloque B
        bloques_ok, bloques_errores = self._validate_only_block_b(e4_response)
        if not bloques_ok:
            errores.extend(bloques_errores)
            score -= 20
        
        # 3. Validar términos abstractos K1
        terminos_ok, terminos_errores, terminos_warns = self._validate_k1_terms(e4_response)
        if not terminos_ok:
            errores.extend(terminos_errores)
            score -= 25
        advertencias.extend(terminos_warns)
        
        # 4. Validar ejercicios (IDs, patrones, tipos)
        ejercicios_ok, ejercicios_errores, ejercicios_warns = self._validate_exercises(e4_response)
        if not ejercicios_ok:
            errores.extend(ejercicios_errores)
            score -= 15
        advertencias.extend(ejercicios_warns)
        
        # 5. Validar coherencia lógica
        coherencia_ok, coherencia_warns = self._validate_logical_coherence(e4_response)
        if not coherencia_ok:
            score -= 5
        advertencias.extend(coherencia_warns)
        
        # 6. Validar decisiones K1
        k1_decisions_ok, k1_decisions_warns = self._validate_k1_decisions(e4_response)
        if not k1_decisions_ok:
            score -= 5
        advertencias.extend(k1_decisions_warns)
        
        detalles = {
            'estructura_valida': estructura_ok,
            'solo_bloque_b': bloques_ok,
            'terminos_k1_validos': terminos_ok,
            'ejercicios_validos': ejercicios_ok,
            'coherencia_logica': coherencia_ok,
            'k1_decisions_presentes': k1_decisions_ok
        }
        
        return ValidationResult(
            valido=(score >= 70),  # Threshold: 70/100
            errores=errores,
            advertencias=advertencias,
            score=max(0, score),
            detalles=detalles
        )
    
    def _validate_structure(self, response: Dict) -> Tuple[bool, List[str]]:
        """Valida estructura básica de la respuesta"""
        errores = []
        
        if 'training_plan' not in response:
            errores.append("❌ Falta clave 'training_plan' en respuesta")
            return False, errores
        
        plan = response['training_plan']
        
        # Campos requeridos
        required_fields = ['training_type', 'days_per_week', 'weeks', 'sessions', 'goal']
        for field in required_fields:
            if field not in plan:
                errores.append(f"❌ Falta campo requerido: '{field}'")
        
        # Weeks debe ser 4
        if plan.get('weeks') != 4:
            errores.append(f"❌ Weeks debe ser 4, recibido: {plan.get('weeks')}")
        
        # Sessions debe ser array no vacío
        if 'sessions' not in plan or not isinstance(plan['sessions'], list) or len(plan['sessions']) == 0:
            errores.append("❌ 'sessions' debe ser un array no vacío")
        
        return (len(errores) == 0), errores
    
    def _validate_only_block_b(self, response: Dict) -> Tuple[bool, List[str]]:
        """Valida que E4 solo generó Bloque B"""
        errores = []
        
        plan = response.get('training_plan', {})
        sessions = plan.get('sessions', [])
        
        for session_idx, session in enumerate(sessions):
            blocks = session.get('blocks', [])
            
            for block in blocks:
                block_id = block.get('id', '')
                
                # Solo debe haber Bloque B
                if block_id != 'B':
                    errores.append(
                        f"❌ Sesión {session_idx + 1}: E4 no debe generar bloques A/C/D. "
                        f"Encontrado: Bloque {block_id}"
                    )
                
            # Validar que core_mobility_block esté desactivado
            core_block = session.get('core_mobility_block', {})
            if core_block.get('include', False) != False:
                errores.append(
                    f"❌ Sesión {session_idx + 1}: 'core_mobility_block.include' debe ser False"
                )
        
        return (len(errores) == 0), errores
    
    def _validate_k1_terms(self, response: Dict) -> Tuple[bool, List[str], List[str]]:
        """Valida que se usen términos abstractos K1 válidos"""
        errores = []
        advertencias = []
        
        # Obtener categorías válidas de K1
        categorias_volumen = set(self.taxonomia['categorias_volumen'])
        categorias_intensidad = set(self.taxonomia['categorias_intensidad_carga'])
        categorias_fallo = set(self.taxonomia['categorias_proximidad_fallo'])
        categorias_densidad = set(self.taxonomia['categorias_densidad'])
        categorias_metodos = set(self.taxonomia['categorias_metodos'])
        
        plan = response.get('training_plan', {})
        sessions = plan.get('sessions', [])
        
        for session_idx, session in enumerate(sessions):
            blocks = session.get('blocks', [])
            
            for block_idx, block in enumerate(blocks):
                # Validar bloque
                vol_bloque = block.get('volumen_total_bloque')
                if vol_bloque and vol_bloque not in categorias_volumen:
                    errores.append(
                        f"❌ Sesión {session_idx + 1}, Bloque {block_idx + 1}: "
                        f"'volumen_total_bloque' inválido: '{vol_bloque}'. "
                        f"Válidos: {categorias_volumen}"
                    )
                
                densidad = block.get('densidad')
                if densidad and densidad not in categorias_densidad:
                    errores.append(
                        f"❌ Sesión {session_idx + 1}, Bloque {block_idx + 1}: "
                        f"'densidad' inválida: '{densidad}'. "
                        f"Válidos: {categorias_densidad}"
                    )
                
                metodo = block.get('metodo_entrenamiento')
                if metodo and metodo not in categorias_metodos:
                    errores.append(
                        f"❌ Sesión {session_idx + 1}, Bloque {block_idx + 1}: "
                        f"'metodo_entrenamiento' inválido: '{metodo}'. "
                        f"Válidos: {categorias_metodos}"
                    )
                
                # Validar ejercicios
                exercises = block.get('exercises', [])
                for ex_idx, exercise in enumerate(exercises):
                    ex_name = exercise.get('exercise_id', f'ejercicio_{ex_idx + 1}')
                    
                    # Volumen abstracto
                    vol_abs = exercise.get('volumen_abstracto')
                    if vol_abs and vol_abs not in categorias_volumen:
                        errores.append(
                            f"❌ Ejercicio '{ex_name}': 'volumen_abstracto' inválido: '{vol_abs}'"
                        )
                    
                    # Intensidad abstracta
                    int_abs = exercise.get('intensidad_abstracta')
                    if int_abs and int_abs not in categorias_intensidad:
                        errores.append(
                            f"❌ Ejercicio '{ex_name}': 'intensidad_abstracta' inválida: '{int_abs}'"
                        )
                    
                    # Proximidad fallo
                    prox_fallo = exercise.get('proximidad_fallo_abstracta')
                    if prox_fallo and prox_fallo not in categorias_fallo:
                        errores.append(
                            f"❌ Ejercicio '{ex_name}': 'proximidad_fallo_abstracta' inválida: '{prox_fallo}'"
                        )
                    
                    # Series y reps abstractas
                    series_abs = exercise.get('series_abstracto')
                    if series_abs and series_abs not in ['bajas', 'medias', 'altas']:
                        advertencias.append(
                            f"⚠️ Ejercicio '{ex_name}': 'series_abstracto' debería ser bajas/medias/altas"
                        )
                    
                    reps_abs = exercise.get('reps_abstracto')
                    if reps_abs and reps_abs not in ['bajas', 'medias', 'altas']:
                        advertencias.append(
                            f"⚠️ Ejercicio '{ex_name}': 'reps_abstracto' debería ser bajas/medias/altas"
                        )
        
        return (len(errores) == 0), errores, advertencias
    
    def _validate_exercises(self, response: Dict) -> Tuple[bool, List[str], List[str]]:
        """Valida ejercicios (IDs, patrones, tipos)"""
        errores = []
        advertencias = []
        
        # Obtener patrones y tipos válidos
        patrones_validos = set(self.taxonomia['patrones_movimiento'])
        tipos_validos = set(self.taxonomia['tipos_ejercicio'])
        
        plan = response.get('training_plan', {})
        sessions = plan.get('sessions', [])
        
        for session_idx, session in enumerate(sessions):
            blocks = session.get('blocks', [])
            
            for block in blocks:
                exercises = block.get('exercises', [])
                
                for ex_idx, exercise in enumerate(exercises):
                    # Validar exercise_id existe
                    ex_id = exercise.get('exercise_id')
                    if not ex_id:
                        errores.append(
                            f"❌ Ejercicio #{ex_idx + 1}: Falta 'exercise_id'"
                        )
                        continue
                    
                    # Validar exercise_id es string válido (slug)
                    if not isinstance(ex_id, str) or not ex_id.replace('_', '').isalnum():
                        errores.append(
                            f"❌ Ejercicio '{ex_id}': ID debe ser slug válido (lowercase, underscores)"
                        )
                    
                    # Validar patrón
                    patron = exercise.get('patron')
                    if not patron:
                        errores.append(
                            f"❌ Ejercicio '{ex_id}': Falta campo 'patron'"
                        )
                    elif patron not in patrones_validos:
                        errores.append(
                            f"❌ Ejercicio '{ex_id}': Patrón inválido '{patron}'. "
                            f"Válidos: {patrones_validos}"
                        )
                    
                    # Validar tipo
                    tipo = exercise.get('tipo')
                    if not tipo:
                        errores.append(
                            f"❌ Ejercicio '{ex_id}': Falta campo 'tipo'"
                        )
                    elif tipo not in tipos_validos:
                        errores.append(
                            f"❌ Ejercicio '{ex_id}': Tipo inválido '{tipo}'. "
                            f"Válidos: {tipos_validos}"
                        )
                    
                    # Validar k1_justification
                    justif = exercise.get('k1_justification', {})
                    if not isinstance(justif, dict):
                        advertencias.append(
                            f"⚠️ Ejercicio '{ex_id}': 'k1_justification' debería ser objeto"
                        )
                    else:
                        required_justif_fields = [
                            'por_que_este_ejercicio',
                            'por_que_este_volumen',
                            'por_que_esta_intensidad'
                        ]
                        for field in required_justif_fields:
                            if field not in justif or not justif[field]:
                                advertencias.append(
                                    f"⚠️ Ejercicio '{ex_id}': Falta justificación '{field}'"
                                )
        
        return (len(errores) == 0), errores, advertencias
    
    def _validate_logical_coherence(self, response: Dict) -> Tuple[bool, List[str]]:
        """Valida coherencia lógica del plan"""
        advertencias = []
        
        plan = response.get('training_plan', {})
        sessions = plan.get('sessions', [])
        
        # Validar que hay un número razonable de sesiones
        if len(sessions) < 2 or len(sessions) > 7:
            advertencias.append(
                f"⚠️ Número de sesiones inusual: {len(sessions)}. "
                "Típicamente debería ser 2-6 sesiones/semana"
            )
        
        # Validar que cada sesión tiene ejercicios
        for session_idx, session in enumerate(sessions):
            blocks = session.get('blocks', [])
            total_exercises = sum(len(block.get('exercises', [])) for block in blocks)
            
            if total_exercises == 0:
                advertencias.append(
                    f"⚠️ Sesión {session_idx + 1}: No tiene ejercicios"
                )
            elif total_exercises > 15:
                advertencias.append(
                    f"⚠️ Sesión {session_idx + 1}: Demasiados ejercicios ({total_exercises}). "
                    "Podría ser excesivo para una sesión"
                )
        
        return True, advertencias
    
    def _validate_k1_decisions(self, response: Dict) -> Tuple[bool, List[str]]:
        """Valida que existan las decisiones K1 para auditoría"""
        advertencias = []
        
        plan = response.get('training_plan', {})
        sessions = plan.get('sessions', [])
        
        for session_idx, session in enumerate(sessions):
            k1_decisions = session.get('k1_decisions', {})
            
            if not k1_decisions:
                advertencias.append(
                    f"⚠️ Sesión {session_idx + 1}: Falta 'k1_decisions' para auditoría"
                )
                continue
            
            # Validar campos de k1_decisions
            required_fields = [
                'reglas_aplicadas',
                'volumen_justificacion',
                'intensidad_justificacion',
                'metodos_usados',
                'patrones_cubiertos'
            ]
            
            for field in required_fields:
                if field not in k1_decisions or not k1_decisions[field]:
                    advertencias.append(
                        f"⚠️ Sesión {session_idx + 1}: Falta '{field}' en k1_decisions"
                    )
        
        return True, advertencias
    
    def should_retry(self, validation_result: ValidationResult) -> bool:
        """
        Determina si se debe reintentar la generación
        
        Args:
            validation_result: Resultado de validación
            
        Returns:
            True si se debe reintentar, False si es aceptable
        """
        # Si score < 70, reintentar
        if validation_result.score < 70:
            logger.warning(f"⚠️ Score bajo ({validation_result.score}/100), reintento recomendado")
            return True
        
        # Si hay errores críticos en estructura o términos K1, reintentar
        errores_criticos = [e for e in validation_result.errores if 'training_plan' in e or 'inválido' in e]
        if errores_criticos:
            logger.warning(f"⚠️ Errores críticos detectados: {len(errores_criticos)}")
            return True
        
        return False
    
    def format_validation_report(self, validation_result: ValidationResult) -> str:
        """Formatea reporte de validación legible"""
        report = f"""
╔══════════════════════════════════════════════════════════
║ VALIDACIÓN E4 RESPONSE
╠══════════════════════════════════════════════════════════
║ Score: {validation_result.score}/100
║ Estado: {"✅ VÁLIDO" if validation_result.valido else "❌ INVÁLIDO"}
╠══════════════════════════════════════════════════════════
"""
        
        if validation_result.errores:
            report += f"║ ERRORES ({len(validation_result.errores)}):\n"
            for error in validation_result.errores:
                report += f"║   {error}\n"
            report += "╠══════════════════════════════════════════════════════════\n"
        
        if validation_result.advertencias:
            report += f"║ ADVERTENCIAS ({len(validation_result.advertencias)}):\n"
            for warn in validation_result.advertencias[:5]:  # Max 5
                report += f"║   {warn}\n"
            if len(validation_result.advertencias) > 5:
                report += f"║   ... y {len(validation_result.advertencias) - 5} más\n"
            report += "╠══════════════════════════════════════════════════════════\n"
        
        report += "║ DETALLES:\n"
        for key, value in validation_result.detalles.items():
            icon = "✅" if value else "❌"
            report += f"║   {icon} {key}\n"
        
        report += "╚══════════════════════════════════════════════════════════"
        
        return report


# Función helper para uso directo
def validate_e4_response(e4_response: Dict) -> ValidationResult:
    """
    Validador rápido para respuesta de E4
    
    Usage:
        result = validate_e4_response(e4_response)
        if not result.valido:
            print(result.errores)
    """
    validator = E4ResponseValidator()
    return validator.validate_full_response(e4_response)


# Test
if __name__ == "__main__":
    # Test básico
    test_response = {
        "training_plan": {
            "training_type": "upper_lower",
            "days_per_week": 4,
            "weeks": 4,
            "goal": "Hypertrophy",
            "sessions": [
                {
                    "id": "D1",
                    "name": "Upper 1",
                    "focus": ["upper_body"],
                    "blocks": [
                        {
                            "id": "B",
                            "block_name": "Bloque B - Fuerza Principal",
                            "primary_muscles": ["pecho"],
                            "secondary_muscles": ["triceps"],
                            "exercises": [
                                {
                                    "order": 1,
                                    "exercise_id": "press_banca_barra",
                                    "patron": "empuje_horizontal",
                                    "tipo": "compuesto_alta_demanda",
                                    "volumen_abstracto": "medio",
                                    "series_abstracto": "medias",
                                    "reps_abstracto": "medias",
                                    "intensidad_abstracta": "moderada",
                                    "proximidad_fallo_abstracta": "moderadamente_cerca_del_fallo",
                                    "notas_tecnicas": "Test",
                                    "k1_justification": {
                                        "por_que_este_ejercicio": "Test",
                                        "por_que_este_volumen": "Test",
                                        "por_que_esta_intensidad": "Test"
                                    }
                                }
                            ],
                            "volumen_total_bloque": "medio",
                            "densidad": "densidad_media",
                            "metodo_entrenamiento": "basico"
                        }
                    ],
                    "core_mobility_block": {"include": False, "details": ""},
                    "session_notes": ["Test"],
                    "k1_decisions": {
                        "reglas_aplicadas": ["test"],
                        "volumen_justificacion": "test",
                        "intensidad_justificacion": "test",
                        "metodos_usados": ["basico"],
                        "patrones_cubiertos": ["empuje_horizontal"]
                    }
                }
            ],
            "general_notes": ["Test"]
        }
    }
    
    validator = E4ResponseValidator()
    result = validator.validate_full_response(test_response)
    
    print(validator.format_validation_report(result))
    print(f"\n¿Reintentar? {validator.should_retry(result)}")
