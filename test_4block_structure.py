#!/usr/bin/env python3
"""
Script to manually add 4-block structure to an existing training plan for testing
"""
import os
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import json

async def add_4block_structure():
    # Connect to database
    mongo_url = os.getenv('MONGO_URL', 'mongodb://localhost:27017')
    print(f"🔗 Connecting to: {mongo_url}")
    client = AsyncIOMotorClient(mongo_url)
    edn360_db_name = os.getenv('MONGO_EDN360_APP_DB_NAME', 'edn360_app')
    print(f"📦 Using database: {edn360_db_name}")
    edn360_db = client[edn360_db_name]
    
    # Get the latest draft plan
    plan_id = "6932dfc2adbfdd696113a5d8"
    
    # List collections to debug
    collections = await edn360_db.list_collection_names()
    print(f"📋 Available collections: {collections}")
    
    # Try to find the plan
    plan = await edn360_db.training_plans_v2.find_one({"_id": plan_id})
    
    if not plan:
        # Try with ObjectId
        from bson import ObjectId
        try:
            plan = await edn360_db.training_plans_v2.find_one({"_id": ObjectId(plan_id)})
        except:
            pass
    
    if not plan:
        # List some plans to see the format
        sample_plans = await edn360_db.training_plans_v2.find({}).limit(3).to_list(3)
        print(f"📋 Sample plan IDs: {[str(p['_id']) for p in sample_plans]}")
        print(f"❌ Plan {plan_id} not found")
        return
    
    print(f"✅ Found plan: {plan['plan']['title']}")
    
    # Add 4-block structure to each session
    for i, session in enumerate(plan['plan']['sessions']):
        print(f"🔧 Adding 4-block structure to session {i+1}: {session['name']}")
        
        # Create the 4-block structure
        bloques_estructurados = {
            'A': {
                'id': 'A',
                'nombre': 'Calentamiento',
                'descripcion': 'Preparación del cuerpo para el entrenamiento',
                'ejercicios': [
                    {
                        'nombre': 'Movilidad articular',
                        'series': 1,
                        'repeticiones': '10-15',
                        'descanso': '30s',
                        'notas': 'Movimientos suaves y controlados'
                    },
                    {
                        'nombre': 'Activación cardiovascular',
                        'series': 1,
                        'repeticiones': '5 min',
                        'descanso': '0s',
                        'notas': 'Intensidad moderada'
                    }
                ],
                'duracion_minutos': 10,
                'expandido': False
            },
            'B': {
                'id': 'B',
                'nombre': 'Entrenamiento Principal (Fuerza)',
                'descripcion': 'Ejercicios principales de fuerza y resistencia',
                'ejercicios': [],
                'duracion_minutos': 45,
                'expandido': True  # Block B should be expanded by default
            },
            'C': {
                'id': 'C',
                'nombre': 'Core/ABS',
                'descripcion': 'Fortalecimiento del core y abdominales',
                'ejercicios': [
                    {
                        'nombre': 'Plancha',
                        'series': 3,
                        'repeticiones': '30-60s',
                        'descanso': '30s',
                        'notas': 'Mantener posición correcta'
                    },
                    {
                        'nombre': 'Crunches',
                        'series': 3,
                        'repeticiones': '15-20',
                        'descanso': '30s',
                        'notas': 'Movimiento controlado'
                    }
                ],
                'duracion_minutos': 10,
                'expandido': False
            },
            'D': {
                'id': 'D',
                'nombre': 'Cardio',
                'descripcion': 'Ejercicio cardiovascular y enfriamiento',
                'ejercicios': [
                    {
                        'nombre': 'Caminata en cinta',
                        'series': 1,
                        'repeticiones': '10-15 min',
                        'descanso': '0s',
                        'notas': 'Intensidad moderada'
                    },
                    {
                        'nombre': 'Estiramientos',
                        'series': 1,
                        'repeticiones': '5-10 min',
                        'descanso': '0s',
                        'notas': 'Relajación y flexibilidad'
                    }
                ],
                'duracion_minutos': 15,
                'expandido': False
            }
        }
        
        # Move existing exercises to Block B
        if 'blocks' in session:
            for block in session['blocks']:
                if 'exercises' in block:
                    for exercise in block['exercises']:
                        bloques_estructurados['B']['ejercicios'].append({
                            'nombre': exercise.get('name', 'Ejercicio'),
                            'series': exercise.get('sets', 3),
                            'repeticiones': exercise.get('reps', '10-12'),
                            'descanso': exercise.get('rest', '60s'),
                            'notas': exercise.get('notes', '')
                        })
        
        # Add the new structure to the session
        session['bloques_estructurados'] = bloques_estructurados
    
    # Update the plan in the database
    result = await edn360_db.training_plans_v2.update_one(
        {"_id": plan_id},
        {"$set": {"plan": plan['plan']}}
    )
    
    if result.modified_count > 0:
        print("✅ Plan updated with 4-block structure successfully!")
        print("🔧 Sending plan to user panel...")
        
        # Send to user panel
        await edn360_db.training_plans_v2.update_one(
            {"_id": plan_id},
            {"$set": {"status": "sent_to_user"}}
        )
        
        print("✅ Plan sent to user panel!")
    else:
        print("❌ Failed to update plan")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(add_4block_structure())