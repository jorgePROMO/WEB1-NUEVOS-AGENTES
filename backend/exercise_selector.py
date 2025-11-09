"""
Exercise Selection Helper for Training Plans
Interfaces with MongoDB exercise database to provide contextu al exercise recommendations
"""

import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.environ.get("DB_NAME", "test_database")

# Initialize MongoDB client
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client[DATABASE_NAME]


async def get_exercises_for_muscle_group(
    muscle_group: str,
    difficulty_level: str = None,
    location: str = None,
    limit: int = 50
) -> List[Dict]:
    """
    Get exercises from database filtered by muscle group and optional criteria
    
    Args:
        muscle_group: Primary or secondary muscle group (e.g., "Pectoral", "Bíceps")
        difficulty_level: Optional filter by difficulty (Principiante/Intermedio/Avanzado)
        location: Optional filter by location (Casa/Gimnasio)
        limit: Maximum number of exercises to return
        
    Returns:
        List of exercise dictionaries
    """
    try:
        # Build query
        query = {
            "$or": [
                {"grupo_muscular_principal": {"$regex": muscle_group, "$options": "i"}},
                {"grupo_muscular_secundario": {"$regex": muscle_group, "$options": "i"}}
            ]
        }
        
        if difficulty_level:
            # Normalize difficulty level (AVANZADO -> Avanzado, INTERMEDIO -> Intermedio)
            difficulty_normalized = difficulty_level.capitalize() if difficulty_level else None
            if difficulty_normalized:
                query["nivel_dificultad"] = {"$regex": difficulty_normalized, "$options": "i"}
        
        if location:
            query["lugar_entrenamiento"] = {"$regex": location, "$options": "i"}
        
        exercises = await db.exercises.find(query).limit(limit).to_list(length=limit)
        
        logger.info(f"Found {len(exercises)} exercises for {muscle_group} (difficulty: {difficulty_level}, location: {location})")
        
        return exercises
    
    except Exception as e:
        logger.error(f"Error fetching exercises for {muscle_group}: {e}")
        return []


async def get_exercises_by_tags(
    tags: List[str],
    difficulty_level: str = None,
    limit: int = 30
) -> List[Dict]:
    """
    Get exercises matching specific tags from GPT tags field
    
    Args:
        tags: List of tags to search for (e.g., ["empuje", "pectoral", "hipertrofia"])
        difficulty_level: Optional filter by difficulty
        limit: Maximum number of exercises to return
        
    Returns:
        List of exercise dictionaries
    """
    try:
        # Build regex pattern for tags
        tag_patterns = [{"tags_gpt": {"$regex": tag, "$options": "i"}} for tag in tags]
        
        query = {"$and": tag_patterns}
        
        if difficulty_level:
            # Normalize difficulty level (AVANZADO -> Avanzado, INTERMEDIO -> Intermedio)
            difficulty_normalized = difficulty_level.capitalize() if difficulty_level else None
            if difficulty_normalized:
                query["nivel_dificultad"] = {"$regex": difficulty_normalized, "$options": "i"}
        
        exercises = await db.exercises.find(query).limit(limit).to_list(length=limit)
        
        logger.info(f"Found {len(exercises)} exercises for tags {tags} (difficulty: {difficulty_level})")
        
        return exercises
    
    except Exception as e:
        logger.error(f"Error fetching exercises by tags {tags}: {e}")
        return []


async def format_exercises_for_llm(exercises: List[Dict]) -> str:
    """
    Format exercise list for LLM consumption
    
    Args:
        exercises: List of exercise dictionaries
        
    Returns:
        Formatted string with exercise information including video URLs
    """
    if not exercises:
        return "No se encontraron ejercicios en la base de datos."
    
    formatted_lines = []
    formatted_lines.append("=== EJERCICIOS DISPONIBLES EN LA BASE DE DATOS ===\n")
    
    for idx, exercise in enumerate(exercises, 1):
        formatted_lines.append(f"{idx}. {exercise.get('nombre_ejercicio', 'Sin nombre')}")
        formatted_lines.append(f"   • Grupo muscular: {exercise.get('grupo_muscular_principal', 'N/A')}")
        if exercise.get('grupo_muscular_secundario'):
            formatted_lines.append(f"   • Secundario: {exercise.get('grupo_muscular_secundario')}")
        formatted_lines.append(f"   • Dificultad: {exercise.get('nivel_dificultad', 'N/A')}")
        formatted_lines.append(f"   • Lugar: {exercise.get('lugar_entrenamiento', 'N/A')}")
        formatted_lines.append(f"   • Material: {exercise.get('material_necesario', 'N/A')}")
        formatted_lines.append(f"   • Video URL: {exercise.get('url_video', 'Sin video')}")
        formatted_lines.append("")
    
    return "\n".join(formatted_lines)


async def get_comprehensive_exercise_database_for_training(
    difficulty_level: str,
    location: str = "Gimnasio / Casa equipada"
) -> str:
    """
    Get a comprehensive set of exercises organized by muscle groups for training plan generation
    
    Args:
        difficulty_level: Client's difficulty level (Principiante/Intermedio/Avanzado)
        location: Training location preference
        
    Returns:
        Formatted string with exercises organized by muscle groups
    """
    try:
        muscle_groups = [
            "Pectoral", "Espalda", "Hombros", "Bíceps", "Tríceps",
            "Cuádriceps", "Femoral", "Glúteo", "Gemelo", "Core", "Abdominales"
        ]
        
        formatted_output = []
        formatted_output.append("=" * 80)
        formatted_output.append("BASE DE DATOS DE EJERCICIOS DISPONIBLES")
        formatted_output.append(f"Nivel: {difficulty_level} | Ubicación: {location}")
        formatted_output.append("=" * 80)
        formatted_output.append("")
        
        for muscle_group in muscle_groups:
            exercises = await get_exercises_for_muscle_group(
                muscle_group=muscle_group,
                difficulty_level=difficulty_level,
                location=location,
                limit=15  # Limit per muscle group to keep context manageable
            )
            
            if exercises:
                formatted_output.append(f"\n## {muscle_group.upper()}")
                formatted_output.append("-" * 80)
                
                for idx, ex in enumerate(exercises, 1):
                    formatted_output.append(
                        f"{idx}. {ex.get('nombre_ejercicio')} "
                        f"[Material: {ex.get('material_necesario')}] "
                        f"[Video: {ex.get('url_video')}]"
                    )
                
                formatted_output.append("")
        
        formatted_output.append("=" * 80)
        formatted_output.append("INSTRUCCIONES:")
        formatted_output.append("- SOLO usar ejercicios de esta lista")
        formatted_output.append("- SIEMPRE incluir la URL del video en el plan")
        formatted_output.append("- Formato: Nombre del Ejercicio (Video: URL)")
        formatted_output.append("=" * 80)
        
        return "\n".join(formatted_output)
    
    except Exception as e:
        logger.error(f"Error generating comprehensive exercise database: {e}")
        return "Error al cargar base de datos de ejercicios."


async def get_exercise_by_name(exercise_name: str) -> Optional[Dict]:
    """
    Get a specific exercise by name (for video URL lookups)
    
    Args:
        exercise_name: Name of the exercise
        
    Returns:
        Exercise dictionary or None
    """
    try:
        exercise = await db.exercises.find_one({
            "nombre_ejercicio": {"$regex": exercise_name, "$options": "i"}
        })
        
        return exercise
    
    except Exception as e:
        logger.error(f"Error fetching exercise {exercise_name}: {e}")
        return None
