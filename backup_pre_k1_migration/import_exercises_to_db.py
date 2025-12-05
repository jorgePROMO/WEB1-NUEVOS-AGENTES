#!/usr/bin/env python3
"""
Script para importar ejercicios de las plantillas a MongoDB
y prepararlos con URLs de video
"""
import os
import asyncio
import json
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone

async def import_exercises():
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    edn360_db = client['edn360_app']
    
    # Load plantillas
    with open('/app/PLANTILLAS_BLOQUES_V3_FINAL.json', 'r', encoding='utf-8') as f:
        plantillas = json.load(f)
    
    # Extract all unique exercises
    all_exercises = {}
    
    def extract_exercises(bloques, block_type):
        for bloque in bloques:
            if 'ejercicios' in bloque:
                for ejercicio in bloque['ejercicios']:
                    nombre = ejercicio.get('nombre', '')
                    if nombre:
                        # Use nombre as unique ID (normalized)
                        exercise_id = nombre.lower().strip()
                        
                        if exercise_id not in all_exercises:
                            all_exercises[exercise_id] = {
                                'id': exercise_id,
                                'nombre': nombre,
                                'tipo': block_type,
                                'video_url': ejercicio.get('video_url'),
                                'grupo_muscular': ejercicio.get('grupo_muscular', ''),
                                'instrucciones': ejercicio.get('instrucciones', ''),
                                'series': ejercicio.get('series'),
                                'reps': ejercicio.get('reps'),
                                'duracion_segundos': ejercicio.get('duracion_segundos'),
                                'duracion_minutos': ejercicio.get('duracion_minutos'),
                                'descanso_segundos': ejercicio.get('descanso_segundos'),
                                'created_at': datetime.now(timezone.utc),
                                'updated_at': datetime.now(timezone.utc)
                            }
    
    # Extract from warmup, core
    if 'calentamiento' in plantillas:
        extract_exercises(plantillas['calentamiento'], 'calentamiento')
    
    if 'core_abs' in plantillas:
        extract_exercises(plantillas['core_abs'], 'core')
    
    print(f"📊 Total ejercicios únicos encontrados: {len(all_exercises)}")
    
    # Insert or update in MongoDB
    exercises_collection = edn360_db.exercises
    
    inserted = 0
    updated = 0
    
    for exercise_id, exercise_data in all_exercises.items():
        # Check if exists
        existing = await exercises_collection.find_one({'id': exercise_id})
        
        if existing:
            # Update
            await exercises_collection.update_one(
                {'id': exercise_id},
                {'$set': exercise_data}
            )
            updated += 1
        else:
            # Insert
            await exercises_collection.insert_one(exercise_data)
            inserted += 1
    
    print(f"✅ Importación completada:")
    print(f"   - Nuevos ejercicios insertados: {inserted}")
    print(f"   - Ejercicios actualizados: {updated}")
    
    # Show some examples
    print(f"\n📋 Ejemplos de ejercicios en BD:")
    exercises = await exercises_collection.find({}, {'_id': 0, 'nombre': 1, 'tipo': 1, 'video_url': 1}).limit(5).to_list(5)
    for ex in exercises:
        video_status = "✅ Con video" if ex.get('video_url') else "❌ Sin video"
        print(f"   - {ex['nombre']} ({ex['tipo']}) - {video_status}")

if __name__ == "__main__":
    asyncio.run(import_exercises())
