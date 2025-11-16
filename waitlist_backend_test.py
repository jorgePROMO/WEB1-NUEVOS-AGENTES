#!/usr/bin/env python3
"""
Waitlist System Backend API Testing
Tests the new Waitlist System backend endpoints as specified in the review request
"""

import requests
import json
import sys
import os
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://edn360-fitness.preview.emergentagent.com/api"

class WaitlistTester:
    def __init__(self):
        self.admin_token = None
        self.test_waitlist_lead_id = None
        self.test_waitlist_email = None
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
    
    def test_1_submit_waitlist_public(self):
        """Test 1: POST /api/waitlist/submit (PUBLIC - no auth needed)"""
        url = f"{BACKEND_URL}/waitlist/submit"
        
        # Test data as specified in the review request
        payload = {
            "nombre_apellidos": "Test Lead Waitlist",
            "email": "testlead@example.com",
            "telefono": "+34 600 123 456",
            "edad": "28",
            "ciudad_pais": "Madrid, España",
            "como_conociste": "Instagram",
            "inversion_mensual": "100-200€/mes",
            "invierte_actualmente": "Gimnasio o suplementos",
            "frase_representa": "Busco resultados reales",
            "objetivo_principal": "Perder grasa",
            "por_que_ahora": "Cansado de posponer",
            "intentado_antes": "Dietas por mi cuenta",
            "como_verte_3_meses": "Con 10kg menos y más energía",
            "entrenas_actualmente": "Sí por mi cuenta",
            "dias_semana_entrenar": "3-4 días",
            "nivel_experiencia": "Intermedio",
            "limitaciones_fisicas": "",
            "tiempo_semanal": "5-6h",
            "nivel_compromiso": "9-10",
            "que_pasaria_sin_cambiar": "Me frustraría",
            "preferencia_comunicacion": "Directa y exigente",
            "que_motiva_mas": "Resultados visibles",
            "esperas_del_coach": "Que me exijas",
            "disponibilidad_llamada": "Sí puedo adaptarme"
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    message = data.get("message", "")
                    # Store lead email for later tests
                    self.test_waitlist_email = payload["email"]
                    self.log_result("POST /api/waitlist/submit (Public)", True, 
                                  f"Waitlist lead submitted successfully. Response: {message}")
                    return True
                else:
                    self.log_result("POST /api/waitlist/submit (Public)", False, 
                                  "Response success not True", data)
            else:
                self.log_result("POST /api/waitlist/submit (Public)", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("POST /api/waitlist/submit (Public)", False, f"Exception: {str(e)}")
        
        return False

    def test_2_admin_login(self):
        """Test 2: Admin login with credentials: ecjtrainer@gmail.com / jorge3007"""
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
                    self.log_result("Admin Login (ecjtrainer@gmail.com)", True, 
                                  f"Admin logged in successfully. Role: {data['user']['role']}")
                    return True
                else:
                    self.log_result("Admin Login (ecjtrainer@gmail.com)", False, 
                                  "Response missing user/token or not admin role", data)
            else:
                self.log_result("Admin Login (ecjtrainer@gmail.com)", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Admin Login (ecjtrainer@gmail.com)", False, f"Exception: {str(e)}")
        
        return False

    def test_3_get_all_waitlist_leads(self):
        """Test 3: GET /api/admin/waitlist/all (ADMIN only)"""
        if not self.admin_token:
            self.log_result("GET /api/admin/waitlist/all", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/waitlist/all"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Find our test lead
                    test_lead = None
                    for lead in data:
                        if lead.get("email") == getattr(self, 'test_waitlist_email', 'testlead@example.com'):
                            test_lead = lead
                            break
                    
                    if test_lead:
                        # Store lead ID for later tests
                        self.test_waitlist_lead_id = test_lead.get("id") or test_lead.get("_id")
                        
                        # Verify scoring fields
                        required_fields = ["score_total", "prioridad"]
                        scoring_fields = all(field in test_lead for field in required_fields)
                        
                        # Check for tags
                        tag_fields = ["capacidad_economica", "objetivo", "motivacion", "nivel_experiencia", "nivel_compromiso", "urgencia", "afinidad_estilo"]
                        tags_present = sum(1 for tag in tag_fields if tag in test_lead)
                        
                        self.log_result("GET /api/admin/waitlist/all", True, 
                                      f"Waitlist leads retrieved. Total: {len(data)}. Test lead found with ID: {self.test_waitlist_lead_id}. Score: {test_lead.get('score_total')}, Priority: {test_lead.get('prioridad')}. Scoring fields: {scoring_fields}, Tags present: {tags_present}/{len(tag_fields)}")
                        return True
                    else:
                        self.log_result("GET /api/admin/waitlist/all", False, 
                                      f"Test lead not found in {len(data)} leads")
                else:
                    self.log_result("GET /api/admin/waitlist/all", False, 
                                  "Response is not a list", data)
            else:
                self.log_result("GET /api/admin/waitlist/all", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET /api/admin/waitlist/all", False, f"Exception: {str(e)}")
        
        return False

    def test_4_get_waitlist_lead_detail(self):
        """Test 4: GET /api/admin/waitlist/{lead_id} (ADMIN only)"""
        if not self.admin_token or not hasattr(self, 'test_waitlist_lead_id'):
            self.log_result("GET /api/admin/waitlist/{lead_id}", False, "No admin token or lead ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/waitlist/{self.test_waitlist_lead_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify all required fields are present
                required_fields = ["nombre_apellidos", "email", "score_total", "prioridad"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Verify all original responses are included
                    original_responses = ["telefono", "edad", "ciudad_pais", "como_conociste", "inversion_mensual", 
                                        "invierte_actualmente", "frase_representa", "objetivo_principal", "por_que_ahora"]
                    responses_present = sum(1 for field in original_responses if field in data)
                    
                    self.log_result("GET /api/admin/waitlist/{lead_id}", True, 
                                  f"Lead detail retrieved successfully. Name: {data.get('nombre_apellidos')}, Score: {data.get('score_total')}, Priority: {data.get('prioridad')}. Original responses present: {responses_present}/{len(original_responses)}")
                    return True
                else:
                    self.log_result("GET /api/admin/waitlist/{lead_id}", False, 
                                  f"Missing required fields: {missing_fields}", data)
            else:
                self.log_result("GET /api/admin/waitlist/{lead_id}", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET /api/admin/waitlist/{lead_id}", False, f"Exception: {str(e)}")
        
        return False

    def test_5_update_lead_status(self):
        """Test 5: PUT /api/admin/waitlist/{lead_id}/status (ADMIN only)"""
        if not self.admin_token or not hasattr(self, 'test_waitlist_lead_id'):
            self.log_result("PUT /api/admin/waitlist/{lead_id}/status", False, "No admin token or lead ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/waitlist/{self.test_waitlist_lead_id}/status"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "estado": "contactado"
        }
        
        try:
            response = requests.put(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("PUT /api/admin/waitlist/{lead_id}/status", True, 
                                  f"Lead status updated successfully: {data.get('message', '')}")
                    return True
                else:
                    self.log_result("PUT /api/admin/waitlist/{lead_id}/status", False, 
                                  "Response success not True", data)
            else:
                self.log_result("PUT /api/admin/waitlist/{lead_id}/status", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("PUT /api/admin/waitlist/{lead_id}/status", False, f"Exception: {str(e)}")
        
        return False

    def test_6_add_lead_note(self):
        """Test 6: POST /api/admin/waitlist/{lead_id}/note (ADMIN only)"""
        if not self.admin_token or not hasattr(self, 'test_waitlist_lead_id'):
            self.log_result("POST /api/admin/waitlist/{lead_id}/note", False, "No admin token or lead ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/waitlist/{self.test_waitlist_lead_id}/note"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        payload = {
            "nota": "Test note added during backend testing - lead looks promising for conversion"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("POST /api/admin/waitlist/{lead_id}/note", True, 
                                  f"Lead note added successfully: {data.get('message', '')}")
                    return True
                else:
                    self.log_result("POST /api/admin/waitlist/{lead_id}/note", False, 
                                  "Response success not True", data)
            else:
                self.log_result("POST /api/admin/waitlist/{lead_id}/note", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("POST /api/admin/waitlist/{lead_id}/note", False, f"Exception: {str(e)}")
        
        return False

    def run_waitlist_tests(self):
        """Run all waitlist system tests in sequence"""
        print("🎯 WAITLIST SYSTEM BACKEND TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 60)
        
        # Waitlist System Tests (as requested in review)
        tests = [
            self.test_1_submit_waitlist_public,
            self.test_2_admin_login,
            self.test_3_get_all_waitlist_leads,
            self.test_4_get_waitlist_lead_detail,
            self.test_5_update_lead_status,
            self.test_6_add_lead_note,
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ EXCEPTION in {test.__name__}: {str(e)}")
                failed += 1
            print()
        
        # Summary
        print("=" * 60)
        print(f"📊 WAITLIST SYSTEM TEST SUMMARY")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%" if (passed+failed) > 0 else "0%")
        
        if failed == 0:
            print("\n🎉 ALL WAITLIST SYSTEM TESTS PASSED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed. Check the details above.")
        
        return failed == 0

def main():
    """Main function to run waitlist tests"""
    tester = WaitlistTester()
    success = tester.run_waitlist_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()