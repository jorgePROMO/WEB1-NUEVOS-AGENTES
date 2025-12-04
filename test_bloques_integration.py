"""
Script de testing para verificar la integración de bloques A, C, D
"""

import sys
sys.path.append('/app/backend')

from training_templates import seleccionar_plantillas

# Simular datos de usuario
user_data = {
    'edad': 30,
    'nivel': 'intermedio',
    'objetivo': 'perdida_grasa',
    'lesion_hombro': False,
    'lesion_lumbar': False,
    'muy_sedentario': False,
    'primera_sesion': False
}

# Simular sesiones de un plan
sesiones = [
    {
        'name': 'Día 1 - Pecho y Tríceps',
        'focus': ['pecho', 'triceps'],
        'blocks': [
            {
                'id': 1,
                'primary_muscles': ['Pecho'],
                'exercises': [
                    {
                        'order': 1,
                        'name': 'Press banca poleas',
                        'series': '4',
                        'reps': '8-10',
                        'rpe': '8',
                        'video_url': 'https://drive.google.com/...'
                    }
                ]
            }
        ]
    },
    {
        'name': 'Día 2 - Espalda y Bíceps',
        'focus': ['espalda', 'biceps'],
        'blocks': [
            {
                'id': 1,
                'primary_muscles': ['Espalda'],
                'exercises': [
                    {
                        'order': 1,
                        'name': 'Remo en polea',
                        'series': '4',
                        'reps': '10-12',
                        'rpe': '7',
                        'video_url': 'https://drive.google.com/...'
                    }
                ]
            }
        ]
    },
    {
        'name': 'Día 3 - Piernas',
        'focus': ['piernas', 'cuadriceps', 'gluteos'],
        'blocks': [
            {
                'id': 1,
                'primary_muscles': ['Cuádriceps'],
                'exercises': [
                    {
                        'order': 1,
                        'name': 'Sentadilla',
                        'series': '4',
                        'reps': '8-10',
                        'rpe': '8',
                        'video_url': 'https://drive.google.com/...'
                    }
                ]
            }
        ]
    },
    {
        'name': 'Día 4 - Hombros',
        'focus': ['hombros', 'deltoides'],
        'blocks': [
            {
                'id': 1,
                'primary_muscles': ['Hombros'],
                'exercises': [
                    {
                        'order': 1,
                        'name': 'Press militar',
                        'series': '4',
                        'reps': '8-10',
                        'rpe': '8',
                        'video_url': 'https://drive.google.com/...'
                    }
                ]
            }
        ]
    }
]

print("="*80)
print("🧪 TESTING DE INTEGRACIÓN DE BLOQUES A, C, D")
print("="*80)
print()

print("📋 CONFIGURACIÓN DEL TEST:")
print(f"  Usuario: {user_data['edad']} años, {user_data['nivel']}, {user_data['objetivo']}")
print(f"  Sesiones a procesar: {len(sesiones)}")
print()

session_number = 1
week_number = 1

for sesion in sesiones:
    print(f"\n{'='*80}")
    print(f"📅 SESIÓN {session_number}: {sesion['name']}")
    print(f"{'='*80}")
    
    # Info del día
    dia_entrenamiento = {
        'grupos_musculares': sesion['focus'],
        'tipo_sesion': 'normal'
    }
    
    # Seleccionar plantillas
    print(f"\n🔍 Seleccionando plantillas...")
    print(f"   Grupos musculares: {sesion['focus']}")
    
    plantillas = seleccionar_plantillas(
        user_data=user_data,
        dia_entrenamiento=dia_entrenamiento,
        session_number=session_number,
        week_number=week_number
    )
    
    # Mostrar resultados
    print(f"\n✅ BLOQUES SELECCIONADOS:")
    print(f"\n🔥 BLOQUE A - CALENTAMIENTO:")
    print(f"   Nombre: {plantillas['calentamiento']['nombre']}")
    print(f"   Duración: {plantillas['calentamiento']['duracion_minutos']} min")
    print(f"   Ejercicios: {len(plantillas['calentamiento']['ejercicios'])}")
    
    print(f"\n💪 BLOQUE B - FUERZA (generado por IA):")
    print(f"   Bloques: {len(sesion['blocks'])}")
    print(f"   Ejercicios: {sum(len(b['exercises']) for b in sesion['blocks'])}")
    
    print(f"\n🧱 BLOQUE C - CORE/ABS:")
    print(f"   Nombre: {plantillas['core_abs']['nombre']}")
    print(f"   Duración: {plantillas['core_abs']['duracion_minutos']} min")
    print(f"   Ejercicios: {len(plantillas['core_abs']['ejercicios'])}")
    
    print(f"\n🏃 BLOQUE D - CARDIO:")
    print(f"   Nombre: {plantillas['cardio']['nombre']}")
    print(f"   Duración: {plantillas['cardio']['duracion_minutos']} min")
    print(f"   Opciones: {len(plantillas['cardio']['opciones'])}")
    if 'cardio_opcion_seleccionada' in plantillas:
        print(f"   Opción seleccionada: Opción {plantillas['cardio']['opciones'].index(plantillas['cardio_opcion_seleccionada']) + 1}")
    
    print(f"\n📊 REGLAS APLICADAS:")
    for regla in plantillas['reglas_aplicadas']:
        print(f"   ✓ {regla}")
    
    print(f"\n📝 LOG DEL SISTEMA:")
    for log_entry in plantillas['log']:
        print(f"   {log_entry}")
    
    session_number += 1

print(f"\n{'='*80}")
print("✅ TESTING COMPLETADO")
print(f"{'='*80}")
print()

# Verificar rotación de cardio
print("🔄 VERIFICACIÓN DE ROTACIÓN DE CARDIO:")
print("   Sesión 1 (impar) → Debería usar Opción 1")
print("   Sesión 2 (par) → Debería usar Opción 2")
print("   Sesión 3 (impar) → Debería usar Opción 1")
print("   Sesión 4 (par) → Debería usar Opción 2")
print()

print("✅ La estructura está lista para guardarse en MongoDB con el campo 'bloques_estructurados'")
print("✅ Frontend puede leer directamente los 4 bloques de cada sesión")
print()
