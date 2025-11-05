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
BACKEND_URL = "https://nutriplan-app-14.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.user_token = None
        self.admin_token = None
        self.test_user_id = None
        self.test_external_client_id = None
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

    # ==================== CRM EXTERNAL CLIENTS TESTS ====================
    
    def test_8_admin_login_for_crm(self):
        """Test 8: Admin login with correct credentials for CRM testing"""
        url = f"{BACKEND_URL}/auth/login"
        params = {
            "email": "ecjtrainer@gmail.com",
            "password": "jorge3007"
        }
        
        try:
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data and data["user"].get("role") == "admin":
                    self.admin_token = data["token"]
                    self.log_result("Admin Login for CRM", True, 
                                  f"Admin logged in successfully with correct credentials. Role: {data['user']['role']}")
                    return True
                else:
                    self.log_result("Admin Login for CRM", False, 
                                  "Response missing user/token or not admin role", data)
            else:
                self.log_result("Admin Login for CRM", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin Login for CRM", False, f"Exception: {str(e)}")
        
        return False

    def test_9_create_external_client(self):
        """Test 9: Create external client for testing"""
        if not self.admin_token:
            self.log_result("Create External Client", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "nombre": "Cliente Test CRM",
            "email": "cliente.test@example.com",
            "whatsapp": "+34 666 777 888",
            "objetivo": "Perder peso y tonificar",
            "plan_weeks": 12,
            "start_date": "2025-01-15T00:00:00Z",
            "amount_paid": 150.0,
            "notes": "Cliente de prueba para testing CRM"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "client_id" in data:
                    self.test_external_client_id = data["client_id"]
                    self.log_result("Create External Client", True, 
                                  f"External client created successfully. ID: {self.test_external_client_id}")
                    return True
                else:
                    self.log_result("Create External Client", False, 
                                  "Response missing client ID", data)
            else:
                self.log_result("Create External Client", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Create External Client", False, f"Exception: {str(e)}")
        
        return False

    def test_10_get_external_clients_list(self):
        """Test 10: GET /api/admin/external-clients (list)"""
        if not self.admin_token:
            self.log_result("Get External Clients List", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "clients" in data and "total" in data:
                    self.log_result("Get External Clients List", True, 
                                  f"External clients list retrieved. Total: {data['total']}")
                    return True
                else:
                    self.log_result("Get External Clients List", False, 
                                  "Response missing clients or total", data)
            else:
                self.log_result("Get External Clients List", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get External Clients List", False, f"Exception: {str(e)}")
        
        return False

    def test_11_get_external_client_detail(self):
        """Test 11: GET /api/admin/external-clients/{client_id} (detail)"""
        if not self.admin_token or not hasattr(self, 'test_external_client_id'):
            self.log_result("Get External Client Detail", False, "No admin token or client ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients/{self.test_external_client_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "nombre" in data:
                    self.log_result("Get External Client Detail", True, 
                                  f"External client detail retrieved. Name: {data.get('nombre')}")
                    return True
                else:
                    self.log_result("Get External Client Detail", False, 
                                  "Response missing required fields", data)
            else:
                self.log_result("Get External Client Detail", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get External Client Detail", False, f"Exception: {str(e)}")
        
        return False

    def test_12_update_external_client_basic_info(self):
        """Test 12: PATCH /api/admin/external-clients/{client_id} - Update basic info"""
        if not self.admin_token or not hasattr(self, 'test_external_client_id'):
            self.log_result("Update External Client Basic Info", False, "No admin token or client ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients/{self.test_external_client_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "nombre": "Cliente Test CRM Actualizado",
            "email": "cliente.actualizado@example.com",
            "whatsapp": "+34 999 888 777"
        }
        
        try:
            response = requests.patch(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Update External Client Basic Info", True, 
                                  f"Basic info updated successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("Update External Client Basic Info", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Update External Client Basic Info", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update External Client Basic Info", False, f"Exception: {str(e)}")
        
        return False

    def test_13_update_external_client_plan_weeks(self):
        """Test 13: PATCH /api/admin/external-clients/{client_id} - Update plan_weeks (should recalculate next_payment_date)"""
        if not self.admin_token or not hasattr(self, 'test_external_client_id'):
            self.log_result("Update External Client Plan Weeks", False, "No admin token or client ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients/{self.test_external_client_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "plan_weeks": 16
        }
        
        try:
            response = requests.patch(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Update External Client Plan Weeks", True, 
                                  f"Plan weeks updated successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("Update External Client Plan Weeks", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Update External Client Plan Weeks", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update External Client Plan Weeks", False, f"Exception: {str(e)}")
        
        return False

    def test_14_update_external_client_start_date(self):
        """Test 14: PATCH /api/admin/external-clients/{client_id} - Update start_date (should recalculate next_payment_date)"""
        if not self.admin_token or not hasattr(self, 'test_external_client_id'):
            self.log_result("Update External Client Start Date", False, "No admin token or client ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients/{self.test_external_client_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "start_date": "2025-02-01T00:00:00Z"
        }
        
        try:
            response = requests.patch(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Update External Client Start Date", True, 
                                  f"Start date updated successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("Update External Client Start Date", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Update External Client Start Date", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update External Client Start Date", False, f"Exception: {str(e)}")
        
        return False

    def test_15_update_external_client_weeks_completed(self):
        """Test 15: PATCH /api/admin/external-clients/{client_id} - Update weeks_completed"""
        if not self.admin_token or not hasattr(self, 'test_external_client_id'):
            self.log_result("Update External Client Weeks Completed", False, "No admin token or client ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients/{self.test_external_client_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "weeks_completed": 8
        }
        
        try:
            response = requests.patch(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Update External Client Weeks Completed", True, 
                                  f"Weeks completed updated successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("Update External Client Weeks Completed", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Update External Client Weeks Completed", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update External Client Weeks Completed", False, f"Exception: {str(e)}")
        
        return False

    def test_16_update_external_client_partial(self):
        """Test 16: PATCH /api/admin/external-clients/{client_id} - Partial update (only some fields)"""
        if not self.admin_token or not hasattr(self, 'test_external_client_id'):
            self.log_result("Update External Client Partial", False, "No admin token or client ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients/{self.test_external_client_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "objetivo": "Ganar masa muscular y definir"
        }
        
        try:
            response = requests.patch(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Update External Client Partial", True, 
                                  f"Partial update successful: {data.get('message')}")
                    return True
                else:
                    self.log_result("Update External Client Partial", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Update External Client Partial", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update External Client Partial", False, f"Exception: {str(e)}")
        
        return False

    def test_17_update_external_client_404(self):
        """Test 17: PATCH /api/admin/external-clients/{client_id} - Test 404 for non-existent client"""
        if not self.admin_token:
            self.log_result("Update External Client 404", False, "No admin token available")
            return False
            
        fake_client_id = "nonexistent_client_id_12345"
        url = f"{BACKEND_URL}/admin/external-clients/{fake_client_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "nombre": "Should not work"
        }
        
        try:
            response = requests.patch(url, json=payload, headers=headers)
            
            if response.status_code == 404:
                self.log_result("Update External Client 404", True, 
                              "Correctly returned 404 for non-existent client")
                return True
            else:
                self.log_result("Update External Client 404", False, 
                              f"Expected 404, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update External Client 404", False, f"Exception: {str(e)}")
        
        return False

    def test_18_verify_updates_applied(self):
        """Test 18: Verify that all updates were applied correctly"""
        if not self.admin_token or not hasattr(self, 'test_external_client_id'):
            self.log_result("Verify Updates Applied", False, "No admin token or client ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients/{self.test_external_client_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if updates were applied
                expected_values = {
                    "nombre": "Cliente Test CRM Actualizado",
                    "email": "cliente.actualizado@example.com",
                    "whatsapp": "+34 999 888 777",
                    "plan_weeks": 16,
                    "weeks_completed": 8,
                    "objetivo": "Ganar masa muscular y definir"
                }
                
                all_correct = True
                errors = []
                
                for field, expected in expected_values.items():
                    actual = data.get(field)
                    if actual != expected:
                        all_correct = False
                        errors.append(f"{field}: expected '{expected}', got '{actual}'")
                
                if all_correct:
                    self.log_result("Verify Updates Applied", True, 
                                  "All updates were applied correctly")
                    return True
                else:
                    self.log_result("Verify Updates Applied", False, 
                                  f"Some updates not applied correctly: {'; '.join(errors)}")
            else:
                self.log_result("Verify Updates Applied", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Verify Updates Applied", False, f"Exception: {str(e)}")
        
        return False

    def test_19_update_external_client_status(self):
        """Test 19: PATCH /api/admin/external-clients/{client_id}/status"""
        if not self.admin_token or not hasattr(self, 'test_external_client_id'):
            self.log_result("Update External Client Status", False, "No admin token or client ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients/{self.test_external_client_id}/status"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "status": "inactive"
        }
        
        try:
            response = requests.patch(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Update External Client Status", True, 
                                  f"Status updated successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("Update External Client Status", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Update External Client Status", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Update External Client Status", False, f"Exception: {str(e)}")
        
        return False

    def test_20_delete_external_client(self):
        """Test 20: DELETE /api/admin/external-clients/{client_id} - Clean up test data"""
        if not self.admin_token or not hasattr(self, 'test_external_client_id'):
            self.log_result("Delete External Client", False, "No admin token or client ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients/{self.test_external_client_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Delete External Client", True, 
                                  f"Test client deleted successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("Delete External Client", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Delete External Client", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Delete External Client", False, f"Exception: {str(e)}")
        
        return False

    # ==================== GPT REPORT GENERATION TESTS ====================
    
    def test_21_admin_login_for_gpt_tests(self):
        """Test 21: Admin login with correct credentials for GPT report testing"""
        url = f"{BACKEND_URL}/auth/login"
        params = {
            "email": "admin@jorgecalcerrada.com",
            "password": "Admin123!"
        }
        
        try:
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data and data["user"].get("role") == "admin":
                    self.admin_token = data["token"]
                    self.log_result("Admin Login for GPT Tests", True, 
                                  f"Admin logged in successfully. Role: {data['user']['role']}")
                    return True
                else:
                    self.log_result("Admin Login for GPT Tests", False, 
                                  "Response missing user/token or not admin role", data)
            else:
                self.log_result("Admin Login for GPT Tests", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin Login for GPT Tests", False, f"Exception: {str(e)}")
        
        return False

    def test_22_submit_questionnaire_with_gpt_report(self):
        """Test 22: Submit questionnaire and verify GPT report is generated immediately"""
        url = f"{BACKEND_URL}/questionnaire/submit"
        
        # Test data as specified in the review request
        payload = {
            "nombre": "Carlos Prueba",
            "edad": "35",
            "email": "carlos.prueba@test.com",
            "whatsapp": "+34612345678",
            "objetivo": "Perder 10kg y ganar músculo",
            "intentos_previos": "He probado varias dietas pero siempre vuelvo a los malos hábitos",
            "dificultades": ["Falta de tiempo", "Desmotivación"],
            "dificultades_otro": None,
            "tiempo_semanal": "3-4 días/semana",
            "entrena": "Sí, 2 veces por semana",
            "alimentacion": "Como de todo pero muy desordenado",
            "salud_info": "Ningún problema",
            "por_que_ahora": "Quiero sentirme mejor y tener más energía",
            "dispuesto_invertir": "Sí, es prioritario",
            "tipo_acompanamiento": "Acompañamiento cercano",
            "presupuesto": "Hasta 200€/mes",
            "comentarios_adicionales": "Necesito motivación constante"
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    message = data.get("message", "")
                    self.log_result("Submit Questionnaire with GPT Report", True, 
                                  f"Questionnaire submitted successfully. Response: {message}")
                    
                    # Store prospect email for later tests
                    self.test_prospect_email = payload["email"]
                    return True
                else:
                    self.log_result("Submit Questionnaire with GPT Report", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Submit Questionnaire with GPT Report", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Submit Questionnaire with GPT Report", False, f"Exception: {str(e)}")
        
        return False

    def test_23_get_prospect_detail_verify_report(self):
        """Test 23: Get prospect detail and verify report was generated"""
        if not self.admin_token:
            self.log_result("Get Prospect Detail - Verify Report", False, "No admin token available")
            return False
            
        # First, get all prospects to find our test prospect
        url = f"{BACKEND_URL}/admin/prospects"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                prospects = data.get("prospects", [])
                
                # Find our test prospect by email
                test_prospect = None
                for prospect in prospects:
                    if prospect.get("email") == getattr(self, 'test_prospect_email', 'carlos.prueba@test.com'):
                        test_prospect = prospect
                        break
                
                if not test_prospect:
                    self.log_result("Get Prospect Detail - Verify Report", False, 
                                  "Test prospect not found in prospects list")
                    return False
                
                # Store prospect ID for later tests
                self.test_prospect_id = test_prospect["id"]
                
                # Get detailed prospect information
                detail_url = f"{BACKEND_URL}/admin/prospects/{self.test_prospect_id}"
                detail_response = requests.get(detail_url, headers=headers)
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    
                    # Verify report fields
                    report_generated = detail_data.get("report_generated", False)
                    report_content = detail_data.get("report_content")
                    report_generated_at = detail_data.get("report_generated_at")
                    
                    if report_generated and report_content and report_generated_at:
                        self.log_result("Get Prospect Detail - Verify Report", True, 
                                      f"GPT report verified: generated={report_generated}, content_length={len(report_content) if report_content else 0}, generated_at={report_generated_at}")
                        return True
                    else:
                        self.log_result("Get Prospect Detail - Verify Report", False, 
                                      f"Report not properly generated: generated={report_generated}, has_content={bool(report_content)}, has_timestamp={bool(report_generated_at)}")
                else:
                    self.log_result("Get Prospect Detail - Verify Report", False, 
                                  f"Failed to get prospect detail: HTTP {detail_response.status_code}")
            else:
                self.log_result("Get Prospect Detail - Verify Report", False, 
                              f"Failed to get prospects list: HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Get Prospect Detail - Verify Report", False, f"Exception: {str(e)}")
        
        return False

    def test_24_send_report_via_email(self):
        """Test 24: Send GPT report via email"""
        if not self.admin_token or not hasattr(self, 'test_prospect_id'):
            self.log_result("Send Report via Email", False, "No admin token or prospect ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/prospects/{self.test_prospect_id}/send-report-email"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.post(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    message = data.get("message", "")
                    self.log_result("Send Report via Email", True, 
                                  f"Report sent via email successfully: {message}")
                    return True
                else:
                    self.log_result("Send Report via Email", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Send Report via Email", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Send Report via Email", False, f"Exception: {str(e)}")
        
        return False

    def test_25_verify_email_sent_status(self):
        """Test 25: Verify prospect was updated with email sent status"""
        if not self.admin_token or not hasattr(self, 'test_prospect_id'):
            self.log_result("Verify Email Sent Status", False, "No admin token or prospect ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/prospects/{self.test_prospect_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                report_sent_at = data.get("report_sent_at")
                report_sent_via = data.get("report_sent_via")
                
                if report_sent_at and report_sent_via == "email":
                    self.log_result("Verify Email Sent Status", True, 
                                  f"Email status verified: sent_at={report_sent_at}, sent_via={report_sent_via}")
                    return True
                else:
                    self.log_result("Verify Email Sent Status", False, 
                                  f"Email status not updated: sent_at={report_sent_at}, sent_via={report_sent_via}")
            else:
                self.log_result("Verify Email Sent Status", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Verify Email Sent Status", False, f"Exception: {str(e)}")
        
        return False

    def test_26_generate_whatsapp_link(self):
        """Test 26: Generate WhatsApp link with pre-filled report"""
        if not self.admin_token or not hasattr(self, 'test_prospect_id'):
            self.log_result("Generate WhatsApp Link", False, "No admin token or prospect ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/prospects/{self.test_prospect_id}/whatsapp-link"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                success = data.get("success")
                whatsapp_link = data.get("whatsapp_link")
                phone = data.get("phone")
                
                if success and whatsapp_link and phone:
                    # Verify link format
                    expected_format = f"https://wa.me/{phone}?text="
                    if whatsapp_link.startswith(expected_format):
                        self.log_result("Generate WhatsApp Link", True, 
                                      f"WhatsApp link generated successfully: phone={phone}, link_length={len(whatsapp_link)}")
                        return True
                    else:
                        self.log_result("Generate WhatsApp Link", False, 
                                      f"WhatsApp link format incorrect: {whatsapp_link[:100]}...")
                else:
                    self.log_result("Generate WhatsApp Link", False, 
                                  f"Response missing required fields: success={success}, has_link={bool(whatsapp_link)}, phone={phone}")
            else:
                self.log_result("Generate WhatsApp Link", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Generate WhatsApp Link", False, f"Exception: {str(e)}")
        
        return False

    def test_27_verify_whatsapp_sent_status(self):
        """Test 27: Verify prospect was updated with WhatsApp sent status"""
        if not self.admin_token or not hasattr(self, 'test_prospect_id'):
            self.log_result("Verify WhatsApp Sent Status", False, "No admin token or prospect ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/prospects/{self.test_prospect_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                report_sent_at = data.get("report_sent_at")
                report_sent_via = data.get("report_sent_via")
                
                if report_sent_at and report_sent_via == "whatsapp":
                    self.log_result("Verify WhatsApp Sent Status", True, 
                                  f"WhatsApp status verified: sent_at={report_sent_at}, sent_via={report_sent_via}")
                    return True
                else:
                    self.log_result("Verify WhatsApp Sent Status", False, 
                                  f"WhatsApp status not updated: sent_at={report_sent_at}, sent_via={report_sent_via}")
            else:
                self.log_result("Verify WhatsApp Sent Status", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Verify WhatsApp Sent Status", False, f"Exception: {str(e)}")
        
        return False

    # ==================== CRITICAL PRODUCTION TESTS ====================
    
    def test_28_admin_login_production_credentials(self):
        """Test 28: Admin login with production credentials"""
        url = f"{BACKEND_URL}/auth/login"
        params = {
            "email": "ecjtrainer@gmail.com",
            "password": "jorge3007"
        }
        
        try:
            response = requests.post(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data and data["user"].get("role") == "admin":
                    self.admin_token = data["token"]
                    self.log_result("Admin Login Production Credentials", True, 
                                  f"Admin logged in successfully with production credentials. Role: {data['user']['role']}")
                    return True
                else:
                    self.log_result("Admin Login Production Credentials", False, 
                                  "Response missing user/token or not admin role", data)
            else:
                self.log_result("Admin Login Production Credentials", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin Login Production Credentials", False, f"Exception: {str(e)}")
        
        return False

    def test_29_soft_delete_consistency_register_user(self):
        """Test 29: Register test user for soft delete testing"""
        url = f"{BACKEND_URL}/auth/register"
        
        # Use unique timestamp for test user
        timestamp = str(int(datetime.now().timestamp()))
        test_email = f"test_softdelete_{timestamp}@example.com"
        
        payload = {
            "username": f"test_softdelete_{timestamp}",
            "email": test_email,
            "password": "Test123!",
            "phone": "+34600000000"
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.soft_delete_user_id = data["user"]["id"]
                    self.soft_delete_user_token = data["token"]
                    self.soft_delete_user_email = test_email
                    self.log_result("Soft Delete - Register User", True, 
                                  f"Test user registered for soft delete testing. ID: {self.soft_delete_user_id}")
                    return True
                else:
                    self.log_result("Soft Delete - Register User", False, 
                                  "Response missing user or token", data)
            else:
                self.log_result("Soft Delete - Register User", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Soft Delete - Register User", False, f"Exception: {str(e)}")
        
        return False

    def test_30_verify_user_in_admin_clients(self):
        """Test 30: Verify registered user appears in admin clients list"""
        if not self.admin_token or not hasattr(self, 'soft_delete_user_id'):
            self.log_result("Verify User in Admin Clients", False, "No admin token or user ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get("clients", [])
                
                # Check if our test user is in the list
                user_found = False
                for client in clients:
                    if client.get("id") == self.soft_delete_user_id:
                        user_found = True
                        break
                
                if user_found:
                    self.log_result("Verify User in Admin Clients", True, 
                                  f"Test user found in admin clients list. Total clients: {len(clients)}")
                    return True
                else:
                    self.log_result("Verify User in Admin Clients", False, 
                                  f"Test user NOT found in admin clients list. Total clients: {len(clients)}")
            else:
                self.log_result("Verify User in Admin Clients", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Verify User in Admin Clients", False, f"Exception: {str(e)}")
        
        return False

    def test_31_soft_delete_user(self):
        """Test 31: Soft delete the test user"""
        if not self.admin_token or not hasattr(self, 'soft_delete_user_id'):
            self.log_result("Soft Delete User", False, "No admin token or user ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/delete-client/{self.soft_delete_user_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("Soft Delete User", True, 
                                  f"User soft deleted successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("Soft Delete User", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Soft Delete User", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Soft Delete User", False, f"Exception: {str(e)}")
        
        return False

    def test_32_verify_deleted_user_not_in_clients(self):
        """Test 32: Verify deleted user does NOT appear in admin clients list"""
        if not self.admin_token:
            self.log_result("Verify Deleted User Not in Clients", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get("clients", [])
                
                # Check if our deleted user is NOT in the list
                user_found = False
                for client in clients:
                    if client.get("id") == getattr(self, 'soft_delete_user_id', None):
                        user_found = True
                        break
                
                if not user_found:
                    self.log_result("Verify Deleted User Not in Clients", True, 
                                  f"Deleted user correctly NOT found in admin clients list. Total clients: {len(clients)}")
                    return True
                else:
                    self.log_result("Verify Deleted User Not in Clients", False, 
                                  f"CRITICAL: Deleted user still appears in admin clients list!")
            else:
                self.log_result("Verify Deleted User Not in Clients", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Verify Deleted User Not in Clients", False, f"Exception: {str(e)}")
        
        return False

    def test_33_deleted_user_auth_me_fails(self):
        """Test 33: Verify deleted user cannot access /auth/me endpoint"""
        if not hasattr(self, 'soft_delete_user_token'):
            self.log_result("Deleted User Auth Me Fails", False, "No deleted user token available")
            return False
            
        url = f"{BACKEND_URL}/auth/me"
        headers = {"Authorization": f"Bearer {self.soft_delete_user_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 403:
                self.log_result("Deleted User Auth Me Fails", True, 
                              "Deleted user correctly blocked from /auth/me with 403 Forbidden")
                return True
            elif response.status_code == 401:
                self.log_result("Deleted User Auth Me Fails", True, 
                              "Deleted user correctly blocked from /auth/me with 401 Unauthorized")
                return True
            else:
                self.log_result("Deleted User Auth Me Fails", False, 
                              f"CRITICAL: Deleted user can still access /auth/me! HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Deleted User Auth Me Fails", False, f"Exception: {str(e)}")
        
        return False

    def test_34_deleted_user_dashboard_fails(self):
        """Test 34: Verify deleted user cannot access dashboard"""
        if not hasattr(self, 'soft_delete_user_token'):
            self.log_result("Deleted User Dashboard Fails", False, "No deleted user token available")
            return False
            
        url = f"{BACKEND_URL}/users/dashboard"
        headers = {"Authorization": f"Bearer {self.soft_delete_user_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 403:
                self.log_result("Deleted User Dashboard Fails", True, 
                              "Deleted user correctly blocked from dashboard with 403 Forbidden")
                return True
            elif response.status_code == 401:
                self.log_result("Deleted User Dashboard Fails", True, 
                              "Deleted user correctly blocked from dashboard with 401 Unauthorized")
                return True
            else:
                self.log_result("Deleted User Dashboard Fails", False, 
                              f"CRITICAL: Deleted user can still access dashboard! HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Deleted User Dashboard Fails", False, f"Exception: {str(e)}")
        
        return False

    def test_35_cache_headers_verification(self):
        """Test 35: Verify no-cache headers are present in API responses"""
        if not self.admin_token:
            self.log_result("Cache Headers Verification", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                # Check for required cache control headers
                cache_control = response.headers.get("Cache-Control", "")
                pragma = response.headers.get("Pragma", "")
                expires = response.headers.get("Expires", "")
                
                required_cache_directives = ["no-store", "no-cache", "must-revalidate", "max-age=0"]
                has_all_directives = all(directive in cache_control for directive in required_cache_directives)
                
                if has_all_directives and pragma == "no-cache" and expires == "0":
                    self.log_result("Cache Headers Verification", True, 
                                  f"All required no-cache headers present: Cache-Control='{cache_control}', Pragma='{pragma}', Expires='{expires}'")
                    return True
                else:
                    self.log_result("Cache Headers Verification", False, 
                                  f"Missing cache headers: Cache-Control='{cache_control}', Pragma='{pragma}', Expires='{expires}'")
            else:
                self.log_result("Cache Headers Verification", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Cache Headers Verification", False, f"Exception: {str(e)}")
        
        return False

    def test_36_email_verification_register_user(self):
        """Test 36: Register user for email verification testing"""
        url = f"{BACKEND_URL}/auth/register"
        
        # Use unique timestamp for test user
        timestamp = str(int(datetime.now().timestamp()))
        test_email = f"test_verify_email_{timestamp}@example.com"
        
        payload = {
            "username": f"test_verify_{timestamp}",
            "email": test_email,
            "password": "Test123!",
            "phone": "+34600000001"
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "message" in data:
                    self.verify_user_email = test_email
                    message = data.get("message", "")
                    if "verifica tu email" in message.lower():
                        self.log_result("Email Verification - Register User", True, 
                                      f"User registered with email verification message: {message}")
                        return True
                    else:
                        self.log_result("Email Verification - Register User", False, 
                                      f"Registration successful but no verification message: {message}")
                else:
                    self.log_result("Email Verification - Register User", False, 
                                  "Response missing user or message", data)
            else:
                self.log_result("Email Verification - Register User", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Email Verification - Register User", False, f"Exception: {str(e)}")
        
        return False

    def test_37_verify_unverified_user_in_clients(self):
        """Test 37: Verify unverified user appears in admin clients with email_verified=false"""
        if not self.admin_token or not hasattr(self, 'verify_user_email'):
            self.log_result("Verify Unverified User in Clients", False, "No admin token or user email available")
            return False
            
        url = f"{BACKEND_URL}/admin/clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get("clients", [])
                
                # Find our test user
                test_user = None
                for client in clients:
                    if client.get("email") == self.verify_user_email:
                        test_user = client
                        break
                
                if test_user:
                    email_verified = test_user.get("email_verified", True)  # Default True if not present
                    if email_verified == False:
                        self.log_result("Verify Unverified User in Clients", True, 
                                      f"Unverified user found with email_verified=false")
                        return True
                    else:
                        self.log_result("Verify Unverified User in Clients", False, 
                                      f"User found but email_verified={email_verified} (should be false)")
                else:
                    self.log_result("Verify Unverified User in Clients", False, 
                                  f"Test user with email {self.verify_user_email} not found in clients list")
            else:
                self.log_result("Verify Unverified User in Clients", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Verify Unverified User in Clients", False, f"Exception: {str(e)}")
        
        return False

    def test_38_unverified_user_login_fails(self):
        """Test 38: Verify unverified user cannot login"""
        if not hasattr(self, 'verify_user_email'):
            self.log_result("Unverified User Login Fails", False, "No test user email available")
            return False
            
        url = f"{BACKEND_URL}/auth/login"
        params = {
            "email": self.verify_user_email,
            "password": "Test123!"
        }
        
        try:
            response = requests.post(url, params=params)
            
            if response.status_code == 403:
                data = response.json()
                detail = data.get("detail", "")
                if "verifica tu email" in detail.lower():
                    self.log_result("Unverified User Login Fails", True, 
                                  f"Unverified user correctly blocked from login: {detail}")
                    return True
                else:
                    self.log_result("Unverified User Login Fails", False, 
                                  f"403 returned but wrong message: {detail}")
            else:
                self.log_result("Unverified User Login Fails", False, 
                              f"CRITICAL: Unverified user can login! HTTP {response.status_code}")
        except Exception as e:
            self.log_result("Unverified User Login Fails", False, f"Exception: {str(e)}")
        
        return False

    def test_39_admin_clients_consistency_multiple_calls(self):
        """Test 39: Verify admin clients endpoint returns consistent data across multiple calls"""
        if not self.admin_token:
            self.log_result("Admin Clients Consistency", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Make 3 consecutive calls
            responses = []
            for i in range(3):
                response = requests.get(url, headers=headers)
                if response.status_code == 200:
                    responses.append(response.json())
                else:
                    self.log_result("Admin Clients Consistency", False, 
                                  f"Call {i+1} failed: HTTP {response.status_code}")
                    return False
            
            # Check consistency
            first_total = responses[0].get("stats", {}).get("total", 0)
            first_clients_count = len(responses[0].get("clients", []))
            
            consistent = True
            for i, resp in enumerate(responses[1:], 2):
                total = resp.get("stats", {}).get("total", 0)
                clients_count = len(resp.get("clients", []))
                
                if total != first_total or clients_count != first_clients_count:
                    consistent = False
                    self.log_result("Admin Clients Consistency", False, 
                                  f"Inconsistent data: Call 1 total={first_total}, Call {i} total={total}")
                    return False
            
            # Check no deleted users
            all_clients = []
            for resp in responses:
                all_clients.extend(resp.get("clients", []))
            
            deleted_users = [c for c in all_clients if c.get("status") == "deleted"]
            
            if deleted_users:
                self.log_result("Admin Clients Consistency", False, 
                              f"CRITICAL: Found {len(deleted_users)} clients with status='deleted'")
                return False
            
            if consistent:
                self.log_result("Admin Clients Consistency", True, 
                              f"Admin clients data consistent across 3 calls. Total: {first_total}, No deleted users found")
                return True
                
        except Exception as e:
            self.log_result("Admin Clients Consistency", False, f"Exception: {str(e)}")
        
        return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print(f"🚀 TESTING EXHAUSTIVO PARA PRODUCCIÓN - Sistema Jorge Calcerrada")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Run tests in order - focusing on CRITICAL PRODUCTION TESTS
        tests = [
            # CRITICAL PRODUCTION TESTS (HIGH PRIORITY)
            self.test_28_admin_login_production_credentials,
            self.test_29_soft_delete_consistency_register_user,
            self.test_30_verify_user_in_admin_clients,
            self.test_31_soft_delete_user,
            self.test_32_verify_deleted_user_not_in_clients,
            self.test_33_deleted_user_auth_me_fails,
            self.test_34_deleted_user_dashboard_fails,
            self.test_35_cache_headers_verification,
            self.test_36_email_verification_register_user,
            self.test_37_verify_unverified_user_in_clients,
            self.test_38_unverified_user_login_fails,
            self.test_39_admin_clients_consistency_multiple_calls,
            
            # Basic system tests
            self.test_1_register_new_user,
            self.test_2_admin_login,
            self.test_3_user_dashboard,
            self.test_4_admin_list_clients,
            self.test_5_admin_send_form,
            self.test_6_admin_verify_payment,
            self.test_7_diagnostic_questionnaire,
            
            # CRM External Clients tests
            self.test_8_admin_login_for_crm,
            self.test_9_create_external_client,
            self.test_10_get_external_clients_list,
            self.test_11_get_external_client_detail,
            self.test_12_update_external_client_basic_info,
            self.test_13_update_external_client_plan_weeks,
            self.test_14_update_external_client_start_date,
            self.test_15_update_external_client_weeks_completed,
            self.test_16_update_external_client_partial,
            self.test_17_update_external_client_404,
            self.test_18_verify_updates_applied,
            self.test_19_update_external_client_status,
            self.test_20_delete_external_client,
            
            # GPT Report Generation tests
            self.test_21_admin_login_for_gpt_tests,
            self.test_22_submit_questionnaire_with_gpt_report,
            self.test_23_get_prospect_detail_verify_report,
            self.test_24_send_report_via_email,
            self.test_25_verify_email_sent_status,
            self.test_26_generate_whatsapp_link,
            self.test_27_verify_whatsapp_sent_status
        ]
        
        for test in tests:
            test()
            print()
        
        # Summary
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        print("=" * 80)
        print(f"📊 TEST SUMMARY: {passed}/{total} tests passed")
        
        # CRITICAL PRODUCTION TESTS summary
        critical_keywords = ["Soft Delete", "Cache Headers", "Email Verification", "Admin Clients Consistency", "Production Credentials"]
        critical_tests = [r for r in self.results if any(keyword in r["test"] for keyword in critical_keywords)]
        critical_passed = sum(1 for r in critical_tests if r["success"])
        critical_total = len(critical_tests)
        
        print(f"🚨 CRITICAL PRODUCTION TESTS: {critical_passed}/{critical_total} passed")
        
        # Separate GPT tests summary
        gpt_tests = [r for r in self.results if "GPT" in r["test"] or "Report" in r["test"] or "WhatsApp" in r["test"] or "Email" in r["test"]]
        gpt_passed = sum(1 for r in gpt_tests if r["success"])
        gpt_total = len(gpt_tests)
        
        print(f"🤖 GPT REPORT GENERATION TESTS: {gpt_passed}/{gpt_total} passed")
        
        # Separate CRM tests summary
        crm_tests = [r for r in self.results if "External Client" in r["test"] or "CRM" in r["test"]]
        crm_passed = sum(1 for r in crm_tests if r["success"])
        crm_total = len(crm_tests)
        
        print(f"🎯 CRM EXTERNAL CLIENTS TESTS: {crm_passed}/{crm_total} passed")
        
        # Show critical test failures first
        if critical_passed < critical_total:
            print("🚨 CRITICAL PRODUCTION TEST FAILURES:")
            critical_failures = [r["test"] for r in critical_tests if not r["success"]]
            for failure in critical_failures:
                print(f"   ❌ {failure}")
        
        if passed == total:
            print("🎉 All tests PASSED! System ready for production.")
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