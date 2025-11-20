"""
Añade instrucciones explícitas de formato a todos los agentes
"""

AGENTS = ["e3_adaptation", "e4_architect", "e6_clinical", "e7_load", "e9_bridge"]

FORMAT_INSTRUCTIONS = '''

---

**⚠️ FORMATO DE SALIDA OBLIGATORIO ⚠️**

Tu respuesta DEBE ser EXACTAMENTE:

```json
{
  "client_context": {
    // TODO el objeto completo aquí
  }
}
```

**NO devuelvas**:
- ❌ `{"status": "ok", ...}`
- ❌ Solo el contenido de training
- ❌ Texto explicativo fuera del JSON

**SÍ devuelve**:
- ✅ `{"client_context": { "meta": {...}, "raw_inputs": {...}, "training": {...} }}`

**CRÍTICO:** JSON válido sin texto adicional, comenzando con `{"client_context":`
'''

def add_format_instructions(filepath):
    """Añade instrucciones de formato"""
    print(f"Actualizando {filepath}...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el cierre del prompt antes de def validate_input
    # Añadir las instrucciones antes del cierre
    if "def validate_input" in content:
        # Buscar el ''' que cierra el prompt
        pattern = "'''\n    \n    def validate_input"
        if pattern in content:
            content = content.replace(
                pattern,
                FORMAT_INSTRUCTIONS + "\n'''\n    \n    def validate_input",
                1
            )
            print(f"  ✅ Instrucciones añadidas")
        else:
            print(f"  ⚠️ Patrón no encontrado, buscando alternativa...")
            # Intentar otro patrón
            pattern2 = "'''\n\n    def validate_input"
            if pattern2 in content:
                content = content.replace(
                    pattern2,
                    FORMAT_INSTRUCTIONS + "\n'''\n\n    def validate_input",
                    1
                )
                print(f"  ✅ Instrucciones añadidas (patrón alternativo)")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    base_path = "/app/backend/edn360/agents/training_initial"
    
    for agent in AGENTS:
        filepath = f"{base_path}/{agent}.py"
        try:
            add_format_instructions(filepath)
        except Exception as e:
            print(f"❌ Error en {agent}: {str(e)}")
    
    print("\n✅ Instrucciones añadidas a todos los agentes")


if __name__ == "__main__":
    main()
