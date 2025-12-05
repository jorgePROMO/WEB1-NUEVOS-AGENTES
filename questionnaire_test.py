#!/usr/bin/env python3
"""
Focused test for Diagnostic Questionnaire endpoint
Tests the POST /api/questionnaire/submit endpoint specifically
"""

import requests
import json
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://fitness-modular.preview.emergentagent.com/api"

def test_questionnaire_endpoint():
    """Test the diagnostic questionnaire endpoint with the exact data from review request"""
    
    print("🧪 Testing Diagnostic Questionnaire Endpoint")
    print(f"URL: {BACKEND_URL}/questionnaire/submit")
    print("=" * 60)
    
    # Test data as specified in the review request
    payload = {
        "nombre": "Test User",
        "edad": "30", 
        "email": "test@example.com",
        "whatsapp": "+34 600 000 000",
        "objetivo": "Perder peso y ganar músculo",
        "intentos_previos": "He probado varias dietas pero no he tenido éxito",
        "dificultades": ["La dieta", "La constancia"],
        "dificultades_otro": "",
        "tiempo_semanal": "3 a 5h",
        "entrena": "Sí, en gimnasio",
        "alimentacion": "Como 3 veces al día, principalmente comida casera",
        "salud_info": "Sin problemas de salud",
        "por_que_ahora": "Quiero mejorar mi salud y verme mejor",
        "dispuesto_invertir": "Sí, si el servicio encaja conmigo",
        "tipo_acompanamiento": "Quiero un seguimiento intensivo, correcciones, soporte 1 a 1",
        "presupuesto": "100-200€/mes",
        "comentarios_adicionales": "Me gustaría empezar lo antes posible"
    }
    
    print("📤 Sending questionnaire data...")
    print(f"   - Nombre: {payload['nombre']}")
    print(f"   - Email: {payload['email']}")
    print(f"   - Objetivo: {payload['objetivo']}")
    print()
    
    try:
        response = requests.post(f"{BACKEND_URL}/questionnaire/submit", json=payload)
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📄 Response Data: {json.dumps(data, indent=2)}")
            
            # Check expected behavior
            if data.get("success") == True:
                message = data.get("message", "")
                print(f"✅ SUCCESS: Questionnaire submitted successfully!")
                print(f"   Message: {message}")
                
                # Check if email was sent or pending
                if "enviado correctamente" in message.lower():
                    print("📧 Email sent successfully to admin")
                elif "pendiente" in message.lower():
                    print("📧 Email pending (SMTP not configured - acceptable)")
                
                return True
            else:
                print(f"❌ FAIL: Response success not True")
                print(f"   Data: {data}")
                return False
        else:
            print(f"❌ FAIL: HTTP {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

def main():
    """Main function"""
    print(f"🚀 Diagnostic Questionnaire Test")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    success = test_questionnaire_endpoint()
    
    print()
    print("=" * 60)
    if success:
        print("🎉 TEST PASSED: Diagnostic questionnaire endpoint is working correctly!")
    else:
        print("💥 TEST FAILED: Issues found with diagnostic questionnaire endpoint")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())