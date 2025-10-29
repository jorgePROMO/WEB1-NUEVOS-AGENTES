#!/usr/bin/env python3
"""
Backend API Testing for Jorge Calcerrada System
Tests all backend endpoints according to the review request flow
"""

import requests
import json
import sys
import os
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://client-hub-52.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.user_token = None
        self.admin_token = None
        self.test_user_id = None
        self.results = []
        
    def log_result(self, test_name, success, message, response_data=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "response_data": response_data
        }
        self.results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if response_data and not success:
            print(f"   Response: {response_data}")
    
    def test_1_register_new_user(self):
        """Test 1: Register new user"""
        url = f"{BACKEND_URL}/auth/register"
        payload = {
            "username": "test_user",
            "email": "test@example.com", 
            "password": "Test123!"
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.user_token = data["token"]
                    self.test_user_id = data["user"]["id"]
                    self.log_result("Register New User", True, 
                                  f"User registered successfully. ID: {self.test_user_id}")
                    return True
                else:
                    self.log_result("Register New User", False, 
                                  "Response missing user or token", data)
            else:
                self.log_result("Register New User", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Register New User", False, f"Exception: {str(e)}")
        
        return False
    
    def test_2_admin_login(self):
        """Test 2: Admin login"""
        url = f"{BACKEND_URL}/auth/login"
        params = {
            "email": "jorge@jorgecalcerrada.com",
            "password": "Admin123!"
        }
        
        try:
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data and data["user"].get("role") == "admin":
                    self.admin_token = data["token"]
                    self.log_result("Admin Login", True, 
                                  f"Admin logged in successfully. Role: {data['user']['role']}")
                    return True
                else:
                    self.log_result("Admin Login", False, 
                                  "Response missing user/token or not admin role", data)
            else:
                self.log_result("Admin Login", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin Login", False, f"Exception: {str(e)}")
        
        return False
    
    def test_3_user_dashboard(self):
        """Test 3: User dashboard"""
        if not self.user_token:
            self.log_result("User Dashboard", False, "No user token available")
            return False
            
        url = f"{BACKEND_URL}/users/dashboard"
        headers = {"Authorization": f"Bearer {self.user_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["user", "forms", "pdfs", "alerts"]
                if all(field in data for field in required_fields):
                    self.log_result("User Dashboard", True, 
                                  f"Dashboard data retrieved. Forms: {len(data['forms'])}, PDFs: {len(data['pdfs'])}, Alerts: {len(data['alerts'])}")
                    return True
                else:
                    missing = [f for f in required_fields if f not in data]
                    self.log_result("User Dashboard", False, 
                                  f"Missing fields: {missing}", data)
            else:
                self.log_result("User Dashboard", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("User Dashboard", False, f"Exception: {str(e)}")
        
        return False
    
    def test_4_admin_list_clients(self):
        """Test 4: Admin list clients"""
        if not self.admin_token:
            self.log_result("Admin List Clients", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "clients" in data and "stats" in data:
                    stats = data["stats"]
                    self.log_result("Admin List Clients", True, 
                                  f"Clients retrieved. Total: {stats.get('total', 0)}, Active: {stats.get('active', 0)}, Pending: {stats.get('pending', 0)}")
                    return True
                else:
                    self.log_result("Admin List Clients", False, 
                                  "Response missing clients or stats", data)
            else:
                self.log_result("Admin List Clients", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin List Clients", False, f"Exception: {str(e)}")
        
        return False
    
    def test_5_admin_send_form(self):
        """Test 5: Admin send form"""
        if not self.admin_token or not self.test_user_id:
            self.log_result("Admin Send Form", False, "No admin token or test user ID available")
            return False
            
        url = f"{BACKEND_URL}/forms/send"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "user_id": self.test_user_id,
            "title": "Formulario de prueba",
            "url": "https://forms.gle/test"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "title" in data and "url" in data and "user_id" in data:
                    self.log_result("Admin Send Form", True, 
                                  f"Form sent successfully. ID: {data.get('id', 'N/A')}")
                    return True
                else:
                    self.log_result("Admin Send Form", False, 
                                  "Response missing required fields", data)
            else:
                self.log_result("Admin Send Form", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin Send Form", False, f"Exception: {str(e)}")
        
        return False
    
    def test_6_admin_verify_payment(self):
        """Test 6: Admin verify payment"""
        if not self.admin_token or not self.test_user_id:
            self.log_result("Admin Verify Payment", False, "No admin token or test user ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/verify-payment/{self.test_user_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.post(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Admin Verify Payment", True, 
                                  f"Payment verified successfully: {data.get('message', '')}")
                    return True
                else:
                    self.log_result("Admin Verify Payment", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Admin Verify Payment", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin Verify Payment", False, f"Exception: {str(e)}")
        
        return False
    
    def test_7_diagnostic_questionnaire(self):
        """Test 7: Diagnostic Questionnaire Submission"""
        url = f"{BACKEND_URL}/questionnaire/submit"
        
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
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    message = data.get("message", "")
                    self.log_result("Diagnostic Questionnaire", True, 
                                  f"Questionnaire submitted successfully. Response: {message}")
                    return True
                else:
                    self.log_result("Diagnostic Questionnaire", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Diagnostic Questionnaire", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Diagnostic Questionnaire", False, f"Exception: {str(e)}")
        
        return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 Starting Backend API Tests")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Run tests in order
        tests = [
            self.test_1_register_new_user,
            self.test_2_admin_login,
            self.test_3_user_dashboard,
            self.test_4_admin_list_clients,
            self.test_5_admin_send_form,
            self.test_6_admin_verify_payment,
            self.test_7_diagnostic_questionnaire
        ]
        
        for test in tests:
            test()
            print()
        
        # Summary
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        print("=" * 60)
        print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests PASSED!")
        else:
            print("⚠️  Some tests FAILED!")
            failed_tests = [r["test"] for r in self.results if not r["success"]]
            print(f"Failed tests: {', '.join(failed_tests)}")
        
        return passed == total

def main():
    """Main function"""
    tester = BackendTester()
    success = tester.run_all_tests()
    
    # Save results to file
    with open("/app/backend_test_results.json", "w") as f:
        json.dump(tester.results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/backend_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())