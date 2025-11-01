#!/bin/bash
# Cronjob para ejecutar el scheduler cada 30 minutos
# Agregar a crontab con: */30 * * * * /app/backend/run_scheduler.sh

cd /app/backend
source venv/bin/activate 2>/dev/null || true
python scheduler_service.py >> /var/log/gpt_scheduler.log 2>&1
