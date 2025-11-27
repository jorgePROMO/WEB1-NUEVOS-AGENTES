#!/usr/bin/env python3
"""
Script de verificación de configuración EDN360
"""
import sys
import os

# Agregar path del backend
sys.path.insert(0, '/app/backend')

def verify_config():
    print("=" * 60)
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN EDN360")
    print("=" * 60)
    
    # Leer variables de entorno desde el archivo .env
    env_vars = {}
    try:
        with open('/app/backend/.env', 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value.strip('"')
    except Exception as e:
        print(f"❌ Error leyendo .env: {e}")
        return False
    
    print("\n📋 Variables de Entorno:")
    print("-" * 60)
    
    # Verificar API Key
    api_key = env_vars.get('EDN360_OPENAI_API_KEY', '')
    if api_key and api_key != 'TU_API_KEY_AQUI':
        print(f"✅ EDN360_OPENAI_API_KEY: {api_key[:15]}...{api_key[-4:]}")
    else:
        print("❌ EDN360_OPENAI_API_KEY: NO CONFIGURADA")
        return False
    
    # Verificar Core Assistant ID
    core_assistant = env_vars.get('EDN360_CORE_ASSISTANT_ID', '')
    if core_assistant and core_assistant.startswith('asst_'):
        print(f"✅ EDN360_CORE_ASSISTANT_ID: {core_assistant}")
    else:
        print(f"❌ EDN360_CORE_ASSISTANT_ID: {core_assistant or 'NO CONFIGURADA'}")
        return False
    
    # Verificar Workflow ID
    workflow_id = env_vars.get('EDN360_TRAINING_WORKFLOW_ID', '')
    if workflow_id and workflow_id.startswith('wf_'):
        print(f"✅ EDN360_TRAINING_WORKFLOW_ID: {workflow_id}")
    else:
        print(f"⚠️  EDN360_TRAINING_WORKFLOW_ID: {workflow_id or 'NO CONFIGURADA'}")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN")
    print("=" * 60)
    
    # Verificar que el servicio puede importarse
    try:
        from services.training_workflow_service import get_training_workflow_config
        config = get_training_workflow_config()
        
        print("\n🔧 Configuración del Servicio:")
        for key, value in config.items():
            icon = "✅" if value else "❌"
            if isinstance(value, str) and (value.startswith('asst_') or value.startswith('wf_') or value.startswith('sk-')):
                # Mostrar solo parte del valor sensible
                if value.startswith('sk-'):
                    display_value = f"{value[:15]}...{value[-4:]}"
                else:
                    display_value = value
                print(f"  {icon} {key}: {display_value}")
            else:
                print(f"  {icon} {key}: {value}")
    except Exception as e:
        print(f"❌ Error importando servicio: {e}")
        return False
    
    print("\n" + "=" * 60)
    
    # Verificación final
    all_ok = (
        api_key and api_key != 'TU_API_KEY_AQUI' and
        core_assistant and core_assistant.startswith('asst_')
    )
    
    if all_ok:
        print("✅ CONFIGURACIÓN COMPLETA Y CORRECTA")
        print("\n🚀 El sistema está listo para ejecutar el workflow EDN360")
        print("   Endpoint: POST /api/training-plan")
        return True
    else:
        print("❌ CONFIGURACIÓN INCOMPLETA")
        print("\n⚠️  Por favor, revisa las variables marcadas con ❌")
        return False

if __name__ == "__main__":
    success = verify_config()
    sys.exit(0 if success else 1)
