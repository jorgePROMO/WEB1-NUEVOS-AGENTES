#!/bin/bash
echo "======================================"
echo "ÚLTIMOS LOGS DEL BACKEND (EDN360)"
echo "======================================"
tail -150 /var/log/supervisor/backend.err.log | grep -A 30 "EDN360\|Respuesta"
