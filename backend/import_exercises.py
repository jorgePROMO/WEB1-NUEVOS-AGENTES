"""
Import exercise database from CSV to MongoDB
One-time script to populate the exercises collection
"""

import csv
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.environ.get("DB_NAME", "test_database")

async def import_exercises_from_csv(csv_file_path):
    """Import exercises from CSV file to MongoDB"""
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DATABASE_NAME]
    exercises_collection = db["exercises"]
    
    try:
        # Clear existing exercises
        result = await exercises_collection.delete_many({})
        print(f"✅ Cleared {result.deleted_count} existing exercises")
        
        # Read CSV and import
        imported_count = 0
        
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            # Use csv.DictReader to automatically use first row as headers
            reader = csv.DictReader(csvfile)
            
            exercises = []
            for row in reader:
                # Skip empty rows
                if not row.get('Nombre ejercicio') or not row['Nombre ejercicio'].strip():
                    continue
                    
                # Create exercise document
                # Handle malformed column names (with newlines or extra characters)
                url_video_key = None
                for key in row.keys():
                    if 'URL video' in key:
                        url_video_key = key
                        break
                
                exercise_doc = {
                    "_id": f"ex_{imported_count + 1}",  # Simple ID format
                    "nombre_ejercicio": row['Nombre ejercicio'].strip(),
                    "grupo_muscular_principal": row['Grupo muscular principal'].strip() if row.get('Grupo muscular principal') else "",
                    "grupo_muscular_secundario": row['Grupo muscular secundario'].strip() if row.get('Grupo muscular secundario') else "",
                    "lugar_entrenamiento": row['Lugar de entrenamiento: casa/gimnasio'].strip() if row.get('Lugar de entrenamiento: casa/gimnasio') else "",
                    "nivel_dificultad": row['Nivel de dificultad'].strip() if row.get('Nivel de dificultad') else "",
                    "material_necesario": row['Material necesario'].strip() if row.get('Material necesario') else "",
                    "equipamiento_opcional": row['Equipamiento opcional'].strip() if row.get('Equipamiento opcional') else "",
                    "tags_gpt": row['Tags GPT'].strip() if row.get('Tags GPT') else "",
                    "url_video": row[url_video_key].strip() if url_video_key and row.get(url_video_key) else "",
                    "created_at": datetime.utcnow().isoformat()
                }
                
                exercises.append(exercise_doc)
                imported_count += 1
        
        # Bulk insert
        if exercises:
            await exercises_collection.insert_many(exercises)
            print(f"✅ Successfully imported {imported_count} exercises to MongoDB")
            print(f"📊 Collection: {DATABASE_NAME}.exercises")
        else:
            print("⚠️ No exercises found in CSV file")
            
    except Exception as e:
        print(f"❌ Error importing exercises: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_exercises.py <path_to_csv_file>")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        sys.exit(1)
    
    print(f"📥 Importing exercises from: {csv_file}")
    asyncio.run(import_exercises_from_csv(csv_file))
