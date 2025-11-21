#!/usr/bin/env python3
"""Verifica si el reporte final está listo"""
import os
import json
from datetime import datetime

REPORT_PATH = "/app/backend/final_report.json"

if os.path.exists(REPORT_PATH):
    print("✅ REPORTE FINAL DISPONIBLE")
    print(f"📅 Generado: {datetime.fromtimestamp(os.path.getmtime(REPORT_PATH)).strftime('%Y-%m-%d %H:%M:%S')}")
    
    with open(REPORT_PATH, 'r') as f:
        report = json.load(f)
    
    print(f"\n📊 RESUMEN RÁPIDO:")
    print(f"   Completados: {report['summary']['completed']}/{report['summary']['total_jobs']}")
    print(f"   Fallados: {report['summary']['failed']}")
    
    if report['summary'].get('duration'):
        print(f"   Duración promedio: {report['summary']['duration']['average_minutes']:.2f} min")
    
    if report['summary'].get('cost_estimate_usd'):
        print(f"   Coste total: ${report['summary']['cost_estimate_usd']['total_cost']:.4f}")
    
    print(f"\nREADY:True")
else:
    print("⏳ Reporte aún no disponible")
    print("READY:False")
