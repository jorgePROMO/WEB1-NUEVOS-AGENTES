#!/bin/bash
# Script para instalar dependencias de WeasyPrint automáticamente
# Este script se ejecuta al inicio del contenedor para asegurar que las librerías estén disponibles

echo "🔧 Instalando dependencias de WeasyPrint..."

# Actualizar lista de paquetes e instalar librerías necesarias
apt-get update -qq > /dev/null 2>&1
apt-get install -y -qq \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libcairo2 \
    libffi-dev \
    shared-mime-info \
    > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Dependencias de WeasyPrint instaladas correctamente"
else
    echo "❌ Error instalando dependencias de WeasyPrint"
    exit 1
fi

# Verificar que WeasyPrint funciona
python3 -c "from weasyprint import HTML; print('✅ WeasyPrint verificado y funcional')" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "⚠️ WeasyPrint instalado pero con advertencias"
fi
