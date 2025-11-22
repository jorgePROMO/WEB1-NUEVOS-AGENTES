#!/bin/bash

# Script autónomo que ejecuta job y genera reporte
cd /app

JOB_ID="job_bloque2_validation_1763803330"
OUTPUT_FILE="/tmp/job_final_report.txt"

echo "=== INICIANDO EJECUCIÓN JOB E1-E9 ===" > $OUTPUT_FILE
echo "Job ID: $JOB_ID" >> $OUTPUT_FILE
echo "Inicio: $(date)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Ejecutar job
python force_job_execution.py >> $OUTPUT_FILE 2>&1

echo "" >> $OUTPUT_FILE
echo "Fin: $(date)" >> $OUTPUT_FILE
echo "" >> $OUTPUT_FILE

# Extraer resultados
echo "=== RESULTADOS FINALES ===" >> $OUTPUT_FILE
python check_job_status.py $JOB_ID >> $OUTPUT_FILE 2>&1

echo "" >> $OUTPUT_FILE
echo "=== REPORTE COMPLETO EN: $OUTPUT_FILE ===" >> $OUTPUT_FILE

# Mostrar en pantalla también
cat $OUTPUT_FILE
