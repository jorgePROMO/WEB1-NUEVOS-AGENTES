"""
Script para actualizar prompts de E3, E6, E7, E9
Añade sección de arquitectura y cambia output a client_context
"""

import re

AGENTS = {
    "e3_adaptation": {
        "old_mission": "## 🎯 Misión\nRecibes:",
        "new_mission": """## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `training.capacity`: Capacidad de E2
   - `training.profile`: Perfil de E1

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `training.adaptation`: Adaptaciones necesarias

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- SOLO llena training.adaptation

---

## 🎯 Misión
Analizas:""",
        "old_output": '## 📤 Output (JSON estructurado)\n\n```json\n{\n  "status": "ok",',
        "new_output": '''## 📤 Output (client_context actualizado)

**CRÍTICO**: Devuelve `client_context` completo con tu campo lleno.

```json
{
  "client_context": {
    "meta": { ... },
    "raw_inputs": { ... },
    "training": {
      "profile": { ... },
      "constraints": { ... },
      "prehab": { ... },
      "progress": null,
      "capacity": { ... },
      // TU CAMPO:
      "adaptation": {'''
    },
    "e6_clinical": {
        "old_mission": "## 🎯 Misión\nRecibes",
        "new_mission": """## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `training.sessions`: Sesiones de E5
   - `training.constraints`: Restricciones de E1
   - `training.prehab`: Protocolos de E1

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `training.safe_sessions`: Sesiones adaptadas para seguridad

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- SOLO llena training.safe_sessions

---

## 🎯 Misión
Adaptas""",
        "old_output": '## 📤 Output\n\n```json\n{\n  "status": "ok",',
        "new_output": '''## 📤 Output (client_context actualizado)

**CRÍTICO**: Devuelve `client_context` completo.

```json
{
  "client_context": {
    "meta": { ... },
    "raw_inputs": { ... },
    "training": {
      "profile": { ... },
      "constraints": { ... },
      "prehab": { ... },
      "progress": null,
      "capacity": { ... },
      "adaptation": { ... },
      "mesocycle": { ... },
      "sessions": { ... },
      // TU CAMPO:
      "safe_sessions": {'''
    },
    "e7_load": {
        "old_mission": "## 🎯 Misión\nTransformas",
        "new_mission": """## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `training.safe_sessions`: Sesiones de E6
   - `training.mesocycle`: Estructura de E4

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `training.formatted_plan`: Plan formateado

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- SOLO llena training.formatted_plan

---

## 🎯 Misión
Transformas""",
        "old_output": '## 📤 Output\n\n```json\n{\n  "status": "ok",',
        "new_output": '''## 📤 Output (client_context actualizado)

**CRÍTICO**: Devuelve `client_context` completo.

```json
{
  "client_context": {
    "meta": { ... },
    "raw_inputs": { ... },
    "training": {
      // ... campos anteriores ...
      "safe_sessions": { ... },
      // TU CAMPO:
      "formatted_plan": {'''
    },
    "e9_bridge": {
        "old_mission": "## 🎯 Misión",
        "new_mission": """## 🏗️ ARQUITECTURA (NUEVO - CRÍTICO)

### TU CONTRATO:
1. **RECIBES**: `client_context` completo con:
   - `training.safe_sessions`: Sesiones de E6
   - `training.mesocycle`: Estructura de E4
   - `training.profile`: Perfil de E1

2. **TU RESPONSABILIDAD**: Llenar SOLO este campo:
   - `training.bridge_for_nutrition`: Puente para nutrición

3. **DEBES DEVOLVER**: El `client_context` COMPLETO con tu campo lleno

### REGLA CRÍTICA:
- NO modifiques campos de otros agentes
- SOLO llena training.bridge_for_nutrition

---

## 🎯 Misión""",
        "old_output": '## 📤 Output\n\n```json\n{\n  "status": "ok",',
        "new_output": '''## 📤 Output (client_context actualizado)

**CRÍTICO**: Devuelve `client_context` completo.

```json
{
  "client_context": {
    "meta": { ... },
    "raw_inputs": { ... },
    "training": {
      // ... campos anteriores ...
      // TU CAMPO:
      "bridge_for_nutrition": {'''
    }
}


def update_agent(filepath, config):
    """Actualiza un agente"""
    print(f"Actualizando {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazar misión
    if config["old_mission"] in content:
        content = content.replace(config["old_mission"], config["new_mission"], 1)
        print(f"  ✅ Sección de misión actualizada")
    else:
        print(f"  ⚠️ No se encontró sección de misión")
    
    # Reemplazar output
    if config["old_output"] in content:
        content = content.replace(config["old_output"], config["new_output"], 1)
        print(f"  ✅ Sección de output actualizada")
    else:
        print(f"  ⚠️ No se encontró sección de output")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  ✅ Archivo guardado")


def main():
    base_path = "/app/backend/edn360/agents/training_initial"
    
    for filename, config in AGENTS.items():
        filepath = f"{base_path}/{filename}.py"
        try:
            update_agent(filepath, config)
        except Exception as e:
            print(f"❌ Error en {filename}: {str(e)}")
    
    print("\n✅ Prompts actualizados")


if __name__ == "__main__":
    main()
