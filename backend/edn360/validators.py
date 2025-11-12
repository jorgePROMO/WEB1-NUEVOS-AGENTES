"""
Validadores transversales del sistema E.D.N.360
Reglas duras que deben cumplirse en todos los planes
"""

from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Error de validación"""
    pass


class EDN360Validator:
    """Validador de reglas transversales del sistema"""
    
    # ==================== REGLAS DURAS ENTRENAMIENTO ====================
    
    SESION_MAX_MINUTOS = 90
    DESEQUILIBRIO_MAX_PCT = 10
    
    @staticmethod
    def validate_session_duration(sesiones: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        """
        Valida que ninguna sesión exceda 90 minutos
        
        Args:
            sesiones: Lista de sesiones con duración
            
        Returns:
            Tuple[bool, List[str]]: (válido, errores)
        """
        errores = []
        
        for i, sesion in enumerate(sesiones):
            duracion = sesion.get("duracion_minutos", 0)
            if duracion > EDN360Validator.SESION_MAX_MINUTOS:
                errores.append(
                    f"Sesión {i+1} excede {EDN360Validator.SESION_MAX_MINUTOS} min: {duracion} min"
                )
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validate_muscle_balance(volumen_por_grupo: Dict[str, int]) -> Tuple[bool, List[str]]:
        """
        Valida equilibrios musculares (push/pull, cadera/rodilla)
        
        Args:
            volumen_por_grupo: Series por grupo muscular
            
        Returns:
            Tuple[bool, List[str]]: (válido, errores)
        """
        errores = []
        
        # Ratio Push/Pull (0.9-1.1)
        push_series = volumen_por_grupo.get("pecho", 0) + volumen_por_grupo.get("hombros", 0) + volumen_por_grupo.get("triceps", 0)
        pull_series = volumen_por_grupo.get("espalda", 0) + volumen_por_grupo.get("biceps", 0)
        
        if pull_series > 0:
            ratio_push_pull = push_series / pull_series
            if ratio_push_pull < 0.9 or ratio_push_pull > 1.1:
                errores.append(
                    f"Ratio Push/Pull fuera de rango (0.9-1.1): {ratio_push_pull:.2f}"
                )
        
        # Ratio Cadera/Rodilla (0.8-1.2)
        cadera_series = volumen_por_grupo.get("gluteos", 0) + volumen_por_grupo.get("isquios", 0)
        rodilla_series = volumen_por_grupo.get("cuadriceps", 0)
        
        if rodilla_series > 0:
            ratio_cadera_rodilla = cadera_series / rodilla_series
            if ratio_cadera_rodilla < 0.8 or ratio_cadera_rodilla > 1.2:
                errores.append(
                    f"Ratio Cadera/Rodilla fuera de rango (0.8-1.2): {ratio_cadera_rodilla:.2f}"
                )
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validate_cit_irg(cit: float, irg: float) -> Tuple[bool, List[str]]:
        """
        Valida CIT e IRG están en rangos seguros
        
        Args:
            cit: Carga Interna Total
            irg: Índice Recuperación Global
            
        Returns:
            Tuple[bool, List[str]]: (válido, advertencias)
        """
        advertencias = []
        
        # CIT óptimo: 35-55, riesgo: >65
        if cit > 65:
            advertencias.append(f"CIT en zona de riesgo: {cit} (>65)")
        elif cit > 55:
            advertencias.append(f"CIT elevado: {cit} (óptimo: 35-55)")
        
        # IRG óptimo: ≥7, riesgo: <5
        if irg < 5:
            advertencias.append(f"IRG bajo - riesgo de fatiga: {irg} (<5)")
        elif irg < 7:
            advertencias.append(f"IRG subóptimo: {irg} (óptimo: ≥7)")
        
        return len(advertencias) == 0, advertencias
    
    @staticmethod
    def validate_amb_distribution(dias_amb: Dict[str, int]) -> Tuple[bool, List[str]]:
        """
        Valida distribución de días A/M/B
        
        Args:
            dias_amb: {"A": 12, "M": 10, "B": 8}
            
        Returns:
            Tuple[bool, List[str]]: (válido, errores)
        """
        errores = []
        
        total_dias = sum(dias_amb.values())
        if total_dias != 30 and total_dias != 28:  # Mes completo
            errores.append(f"Total de días incorrecto: {total_dias} (esperado: 28-30)")
        
        dias_a = dias_amb.get("A", 0)
        dias_m = dias_amb.get("M", 0)
        dias_b = dias_amb.get("B", 0)
        
        # No más de 40% días A
        if dias_a / total_dias > 0.4:
            errores.append(f"Demasiados días Alta demanda: {dias_a}/{total_dias} (>40%)")
        
        # Al menos 20% días B (recuperación)
        if dias_b / total_dias < 0.2:
            errores.append(f"Insuficientes días Baja demanda: {dias_b}/{total_dias} (<20%)")
        
        return len(errores) == 0, errores
    
    # ==================== REGLAS DURAS NUTRICIÓN ====================
    
    PROTEINA_MIN_GKG = 1.8
    GRASA_MIN_GKG = 0.6
    CALORIAS_MIN_HOMBRE = 1600
    CALORIAS_MIN_MUJER = 1300
    
    @staticmethod
    def validate_protein_intake(proteina_gkg: float, peso_kg: float) -> Tuple[bool, List[str]]:
        """
        Valida ingesta mínima de proteína
        
        Args:
            proteina_gkg: Proteína en g/kg
            peso_kg: Peso corporal
            
        Returns:
            Tuple[bool, List[str]]: (válido, errores)
        """
        errores = []
        
        if proteina_gkg < EDN360Validator.PROTEINA_MIN_GKG:
            errores.append(
                f"Proteína insuficiente: {proteina_gkg} g/kg (mínimo: {EDN360Validator.PROTEINA_MIN_GKG} g/kg)"
            )
        
        proteina_total = proteina_gkg * peso_kg
        if proteina_total < 120 and peso_kg > 60:  # Mínimo absoluto
            errores.append(f"Proteína total muy baja: {proteina_total}g")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validate_fat_intake(grasa_gkg: float) -> Tuple[bool, List[str]]:
        """
        Valida ingesta mínima de grasas
        
        Args:
            grasa_gkg: Grasa en g/kg
            
        Returns:
            Tuple[bool, List[str]]: (válido, errores)
        """
        errores = []
        
        if grasa_gkg < EDN360Validator.GRASA_MIN_GKG:
            errores.append(
                f"Grasa insuficiente: {grasa_gkg} g/kg (mínimo: {EDN360Validator.GRASA_MIN_GKG} g/kg)"
            )
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validate_calories_minimum(kcal: float, sexo: str) -> Tuple[bool, List[str]]:
        """
        Valida calorías mínimas según sexo
        
        Args:
            kcal: Calorías objetivo
            sexo: "hombre" o "mujer"
            
        Returns:
            Tuple[bool, List[str]]: (válido, errores)
        """
        errores = []
        
        min_kcal = EDN360Validator.CALORIAS_MIN_HOMBRE if sexo.lower() == "hombre" else EDN360Validator.CALORIAS_MIN_MUJER
        
        if kcal < min_kcal:
            errores.append(
                f"Calorías por debajo del mínimo seguro: {kcal} kcal (mínimo: {min_kcal} kcal para {sexo})"
            )
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validate_macro_distribution(macros: Dict[str, float], peso_kg: float) -> Tuple[bool, List[str]]:
        """
        Valida distribución completa de macros
        
        Args:
            macros: {"P": 2.2, "G": 0.9, "C": 3.5} en g/kg
            peso_kg: Peso corporal
            
        Returns:
            Tuple[bool, List[str]]: (válido, errores)
        """
        errores = []
        
        # Validar proteína
        valido_p, errores_p = EDN360Validator.validate_protein_intake(macros.get("P", 0), peso_kg)
        errores.extend(errores_p)
        
        # Validar grasa
        valido_g, errores_g = EDN360Validator.validate_fat_intake(macros.get("G", 0))
        errores.extend(errores_g)
        
        # Validar carbohidratos no sean negativos
        if macros.get("C", 0) < 0:
            errores.append("Carbohidratos no pueden ser negativos")
        
        return len(errores) == 0, errores
    
    @staticmethod
    def validate_weekly_calorie_variance(kcal_dias: List[float], kcal_objetivo: float) -> Tuple[bool, List[str]]:
        """
        Valida que la variación semanal de calorías no exceda ±10%
        
        Args:
            kcal_dias: Lista de calorías por día
            kcal_objetivo: Calorías objetivo promedio
            
        Returns:
            Tuple[bool, List[str]]: (válido, errores)
        """
        errores = []
        
        kcal_promedio = sum(kcal_dias) / len(kcal_dias)
        variacion_pct = abs((kcal_promedio - kcal_objetivo) / kcal_objetivo * 100)
        
        if variacion_pct > 10:
            errores.append(
                f"Variación semanal de calorías excede ±10%: {variacion_pct:.1f}%"
            )
        
        return len(errores) == 0, errores
    
    # ==================== VALIDACIÓN COMPLETA DE PLAN ====================
    
    @staticmethod
    def validate_complete_plan(
        training_data: Dict[str, Any],
        nutrition_data: Dict[str, Any],
        client_data: Dict[str, Any]
    ) -> Tuple[bool, List[str], List[str]]:
        """
        Valida un plan completo (entrenamiento + nutrición)
        
        Args:
            training_data: Datos del plan de entrenamiento
            nutrition_data: Datos del plan de nutrición
            client_data: Datos del cliente
            
        Returns:
            Tuple[bool, List[str], List[str]]: (válido, errores_criticos, advertencias)
        """
        errores = []
        advertencias = []
        
        # Validaciones de entrenamiento
        if training_data:
            sesiones = training_data.get("sesiones", [])
            if sesiones:
                valido, errs = EDN360Validator.validate_session_duration(sesiones)
                errores.extend(errs)
            
            volumen = training_data.get("volumen_por_grupo", {})
            if volumen:
                valido, errs = EDN360Validator.validate_muscle_balance(volumen)
                advertencias.extend(errs)
            
            cit = training_data.get("cit", 0)
            irg = training_data.get("irg", 10)
            if cit > 0:
                valido, warns = EDN360Validator.validate_cit_irg(cit, irg)
                advertencias.extend(warns)
        
        # Validaciones de nutrición
        if nutrition_data:
            peso = client_data.get("peso_kg", 70)
            sexo = client_data.get("sexo", "hombre")
            
            macros = nutrition_data.get("macros_gkg", {})
            if macros:
                valido, errs = EDN360Validator.validate_macro_distribution(macros, peso)
                errores.extend(errs)
            
            kcal = nutrition_data.get("kcal_objetivo", 0)
            if kcal > 0:
                valido, errs = EDN360Validator.validate_calories_minimum(kcal, sexo)
                errores.extend(errs)
        
        return len(errores) == 0, errores, advertencias
    
    @staticmethod
    def validate_followup_conditions(
        irg: float,
        adherencia_pct: float,
        peso_perdido_kg: float,
        semanas: int
    ) -> Tuple[bool, List[str]]:
        """
        Valida condiciones para ajustes de seguimiento
        
        Args:
            irg: Índice Recuperación Global
            adherencia_pct: % de adherencia
            peso_perdido_kg: Kg perdidos
            semanas: Semanas del plan
            
        Returns:
            Tuple[bool, List[str]]: (puede_intensificar, condiciones)
        """
        condiciones = []
        puede_intensificar = True
        
        # No intensificar si IRG < 6
        if irg < 6:
            puede_intensificar = False
            condiciones.append(f"IRG bajo ({irg}) - no intensificar")
        
        # Requiere adherencia ≥85% para ajustar
        if adherencia_pct < 85:
            puede_intensificar = False
            condiciones.append(f"Adherencia insuficiente ({adherencia_pct}%) - primero mejorar adherencia")
        
        # Validar tasa de pérdida segura (máx 1% peso corporal/semana)
        if semanas > 0:
            tasa_semanal = peso_perdido_kg / semanas
            if tasa_semanal > 1.0:  # Muy agresivo
                condiciones.append(f"Pérdida muy rápida ({tasa_semanal:.2f}kg/sem) - considerar descanso")
        
        return puede_intensificar, condiciones


# ==================== FUNCIONES DE UTILIDAD ====================

def log_validation_results(
    plan_id: str,
    errores: List[str],
    advertencias: List[str]
):
    """Registra resultados de validación en logs"""
    if errores:
        logger.error(f"Plan {plan_id} - Errores de validación: {errores}")
    if advertencias:
        logger.warning(f"Plan {plan_id} - Advertencias: {advertencias}")
    if not errores and not advertencias:
        logger.info(f"Plan {plan_id} - Validación exitosa ✓")
