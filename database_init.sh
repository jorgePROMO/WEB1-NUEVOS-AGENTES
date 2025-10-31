#!/bin/bash

# ============================================
# Script de Inicialización de Base de Datos
# Jorge Calcerrada Trainer Platform
# ============================================

echo "🚀 Iniciando configuración de base de datos..."

# Variables
DB_NAME="ecj_trainer"
MONGO_URI="mongodb://localhost:27017"
EXPORT_DIR="/app/database_export"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "📊 Base de datos: $DB_NAME"
echo "📁 Directorio de datos: $EXPORT_DIR"
echo ""

# Verificar que MongoDB está corriendo
echo "🔍 Verificando MongoDB..."
if ! pgrep -x "mongod" > /dev/null; then
    echo -e "${RED}❌ MongoDB no está corriendo${NC}"
    echo "   Inicia MongoDB con: sudo systemctl start mongodb"
    exit 1
fi
echo -e "${GREEN}✅ MongoDB está corriendo${NC}"
echo ""

# Verificar que el directorio de exportación existe
if [ ! -d "$EXPORT_DIR" ]; then
    echo -e "${RED}❌ Directorio de exportación no existe: $EXPORT_DIR${NC}"
    exit 1
fi

# Lista de colecciones
COLLECTIONS=("users" "prospects" "team_clients" "external_clients" "sessions" "pdfs" "alerts" "templates" "tags")

echo "📥 Importando datos a MongoDB..."
echo ""

# Importar cada colección
for collection in "${COLLECTIONS[@]}"; do
    file="$EXPORT_DIR/$collection.json"
    
    if [ -f "$file" ]; then
        echo "   Importando $collection..."
        
        mongoimport --uri="$MONGO_URI/$DB_NAME" \
            --collection="$collection" \
            --file="$file" \
            --jsonArray \
            --drop 2>&1 | grep -E "imported|dropped" | sed 's/^/      /'
        
        if [ $? -eq 0 ]; then
            echo -e "   ${GREEN}✅ $collection importado correctamente${NC}"
        else
            echo -e "   ${RED}❌ Error al importar $collection${NC}"
        fi
    else
        echo -e "   ${YELLOW}⚠️  Archivo no encontrado: $file${NC}"
    fi
    echo ""
done

echo "📊 Resumen de la base de datos:"
echo ""

mongosh "$MONGO_URI/$DB_NAME" --quiet --eval '
  var collections = db.getCollectionNames();
  collections.forEach(function(collName) {
    var count = db[collName].countDocuments();
    print("   " + collName + ": " + count + " documentos");
  });
'

echo ""
echo -e "${GREEN}🎉 Inicialización completada!${NC}"
echo ""
echo "📝 Credenciales de acceso:"
echo "   Admin Email: admin@ecjtrainer.com"
echo "   Admin Password: admin123"
echo ""
echo "🚀 Para iniciar la aplicación:"
echo "   Backend:  cd backend && source venv/bin/activate && uvicorn server:app --reload"
echo "   Frontend: cd frontend && yarn start"
echo ""
