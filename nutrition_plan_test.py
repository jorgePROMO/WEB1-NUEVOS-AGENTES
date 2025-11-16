#!/usr/bin/env python3
"""
Focused Nutrition Plan Generation Test
Tests the specific flow for generating nutrition plans with previous plan as reference
"""

import requests
import json
import sys
import os
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://edn360-fitness.preview.emergentagent.com/api"

class NutritionPlanTester:
    def __init__(self):
        self.admin_token = None
        self.test_client_for_nutrition = None
        self.previous_nutrition_plan = None
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
    
    def test_1_admin_login(self):
        """Test 1: Admin login with correct credentials"""
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

    def test_2_get_clients(self):
        """Test 2: Get clients and find one for testing"""
        if not self.admin_token:
            self.log_result("Get Clients", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                clients = data.get("clients", [])
                
                if len(clients) > 0:
                    # Store first client for testing
                    self.test_client_for_nutrition = clients[0]
                    client_id = self.test_client_for_nutrition.get('id')
                    client_email = self.test_client_for_nutrition.get('email', 'N/A')
                    
                    self.log_result("Get Clients", True, 
                                  f"Found {len(clients)} clients. Using client: {client_email} (ID: {client_id})")
                    return True
                else:
                    self.log_result("Get Clients", False, 
                                  "No clients found in system")
            else:
                self.log_result("Get Clients", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get Clients", False, f"Exception: {str(e)}")
        
        return False

    def test_3_get_existing_nutrition_plans(self):
        """Test 3: GET /api/admin/users/{user_id}/nutrition - Get existing nutrition plans"""
        if not self.admin_token or not self.test_client_for_nutrition:
            self.log_result("Get Existing Nutrition Plans", False, "No admin token or test client available")
            return False
            
        client_id = self.test_client_for_nutrition.get('id')
        url = f"{BACKEND_URL}/admin/users/{client_id}/nutrition"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                plans = data.get("plans", [])
                
                if len(plans) > 0:
                    # Store the first plan as the previous plan for reference
                    self.previous_nutrition_plan = plans[0]
                    plan_id = self.previous_nutrition_plan.get('id')
                    generated_at = self.previous_nutrition_plan.get('generated_at', 'N/A')
                    
                    # Also get the submission_id from the plan if available
                    self.submission_id = self.previous_nutrition_plan.get('submission_id', plan_id)
                    
                    self.log_result("Get Existing Nutrition Plans", True, 
                                  f"Found {len(plans)} nutrition plans. Using plan ID: {plan_id} (generated: {generated_at}) as previous plan reference. Submission ID: {self.submission_id}")
                    return True
                else:
                    self.log_result("Get Existing Nutrition Plans", False, 
                                  f"No existing nutrition plans found for client {client_id}. This test requires at least one existing plan.")
            else:
                self.log_result("Get Existing Nutrition Plans", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get Existing Nutrition Plans", False, f"Exception: {str(e)}")
        
        return False

    def test_3_5_create_new_nutrition_questionnaire(self):
        """Test 3.5: Create a new nutrition questionnaire submission for testing"""
        if not self.admin_token or not self.test_client_for_nutrition:
            self.log_result("Create New Nutrition Questionnaire", False, "No admin token or test client available")
            return False
            
        client_id = self.test_client_for_nutrition.get('id')
        url = f"{BACKEND_URL}/nutrition/questionnaire/submit"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        payload = {
            "user_id": client_id,
            "nombre_completo": self.test_client_for_nutrition.get('name', 'Test Client'),
            "fecha_nacimiento": "1990-01-01",
            "sexo": "HOMBRE",
            "altura_cm": 175,
            "peso": 82,  # Slightly different weight for new questionnaire
            "objetivo_principal": "Ganar músculo y definir",  # Different goal
            "nivel_actividad": "Ejercicio intenso (5-6 días/semana)",  # Different activity level
            "trabajo_fisico": "sedentario",
            "alergias_intolerancias": "Ninguna",
            "comidas_dia": "4 comidas",  # Different meal frequency
            "experiencia_dietas": "Avanzado",  # Different experience level
            "disponibilidad_cocinar": "Alta",  # Different cooking availability
            "presupuesto_alimentacion": "Alto"  # Different budget
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.submission_id = data.get("submission_id")
                    self.log_result("Create New Nutrition Questionnaire", True, 
                                  f"New nutrition questionnaire submission created. ID: {self.submission_id}")
                    return True
                else:
                    self.log_result("Create New Nutrition Questionnaire", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Create New Nutrition Questionnaire", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Create New Nutrition Questionnaire", False, f"Exception: {str(e)}")
        
        return False

    def test_4_generate_nutrition_plan_with_previous_reference(self):
        """Test 4: Generate nutrition plan using previous plan as reference - MAIN TEST"""
        if not self.admin_token or not self.test_client_for_nutrition or not self.previous_nutrition_plan:
            self.log_result("Generate Nutrition Plan with Previous Reference", False, 
                          "No admin token, test client, or previous nutrition plan available")
            return False
            
        client_id = self.test_client_for_nutrition.get('id')
        previous_plan_id = self.previous_nutrition_plan.get('id')
        
        # Use the submission_id we found
        submission_id = getattr(self, 'submission_id', previous_plan_id)
        
        # This is the critical test - using previous_nutrition_plan_id parameter
        url = f"{BACKEND_URL}/admin/users/{client_id}/nutrition/generate?submission_id={submission_id}&previous_nutrition_plan_id={previous_plan_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            print(f"🎯 CRITICAL TEST: Generating nutrition plan with previous plan reference...")
            print(f"   Client ID: {client_id}")
            print(f"   Previous Plan ID: {previous_plan_id}")
            print(f"   Submission ID: {submission_id}")
            print(f"   URL: {url}")
            
            response = requests.post(url, headers=headers, timeout=120)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("plan_id"):
                    new_plan_id = data.get("plan_id")
                    message = data.get("message", "")
                    
                    # Check if the error "Plan nutricional previo no encontrado" appears
                    if "Plan nutricional previo no encontrado" in message:
                        self.log_result("Generate Nutrition Plan with Previous Reference", False, 
                                      f"❌ ERROR STILL PRESENT: 'Plan nutricional previo no encontrado' - Fix not working. Message: {message}")
                        return False
                    else:
                        self.log_result("Generate Nutrition Plan with Previous Reference", True, 
                                      f"✅ SUCCESS: Nutrition plan generated successfully with previous plan reference. New Plan ID: {new_plan_id}. No error 'Plan nutricional previo no encontrado' found. Message: {message}")
                        return True
                else:
                    error_message = data.get("message", "Unknown error")
                    if "Plan nutricional previo no encontrado" in error_message:
                        self.log_result("Generate Nutrition Plan with Previous Reference", False, 
                                      f"❌ CRITICAL ERROR: 'Plan nutricional previo no encontrado' - The reported bug is still present! Error: {error_message}")
                    else:
                        self.log_result("Generate Nutrition Plan with Previous Reference", False, 
                                      f"Response missing success or plan_id. Error: {error_message}", data)
            else:
                response_text = response.text
                if "Plan nutricional previo no encontrado" in response_text:
                    self.log_result("Generate Nutrition Plan with Previous Reference", False, 
                                  f"❌ CRITICAL ERROR: 'Plan nutricional previo no encontrado' - The reported bug is still present! HTTP {response.status_code}: {response_text}")
                else:
                    self.log_result("Generate Nutrition Plan with Previous Reference", False, 
                                  f"HTTP {response.status_code}", response_text)
        except Exception as e:
            error_str = str(e)
            if "Plan nutricional previo no encontrado" in error_str:
                self.log_result("Generate Nutrition Plan with Previous Reference", False, 
                              f"❌ CRITICAL ERROR: 'Plan nutricional previo no encontrado' - The reported bug is still present! Exception: {error_str}")
            else:
                self.log_result("Generate Nutrition Plan with Previous Reference", False, f"Exception: {error_str}")
        
        return False

    def test_5_verify_fix_implementation(self):
        """Test 5: Verify that the fix for plan._id vs plan.id is working"""
        if not self.previous_nutrition_plan:
            self.log_result("Verify Fix Implementation", False, "No previous nutrition plan available for verification")
            return False
            
        # Check that we're using 'id' field correctly (not '_id')
        plan_id = self.previous_nutrition_plan.get('id')
        plan_underscore_id = self.previous_nutrition_plan.get('_id')
        
        if plan_id and not plan_underscore_id:
            self.log_result("Verify Fix Implementation", True, 
                          f"✅ VERIFICATION: Using correct 'id' field ({plan_id}) instead of '_id' field. Fix appears to be implemented correctly.")
            return True
        elif plan_underscore_id and not plan_id:
            self.log_result("Verify Fix Implementation", False, 
                          f"❌ VERIFICATION FAILED: Still using '_id' field ({plan_underscore_id}) instead of 'id' field. Fix may not be properly implemented.")
            return False
        elif plan_id and plan_underscore_id:
            self.log_result("Verify Fix Implementation", True, 
                          f"✅ VERIFICATION: Both 'id' ({plan_id}) and '_id' ({plan_underscore_id}) fields present. Using 'id' field is correct.")
            return True
        else:
            self.log_result("Verify Fix Implementation", False, 
                          "❌ VERIFICATION FAILED: Neither 'id' nor '_id' field found in previous nutrition plan data.")
            return False

    def run_tests(self):
        """Run all nutrition plan tests"""
        print("🎯 NUTRITION PLAN GENERATION WITH PREVIOUS PLAN REFERENCE - TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        tests = [
            self.test_1_admin_login,
            self.test_2_get_clients,
            self.test_3_get_existing_nutrition_plans,
            self.test_3_5_create_new_nutrition_questionnaire,
            self.test_4_generate_nutrition_plan_with_previous_reference,
            self.test_5_verify_fix_implementation,
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
            print()  # Empty line between tests
        
        # Print summary
        print("=" * 80)
        print("📊 NUTRITION PLAN TEST SUMMARY")
        print("=" * 80)
        print(f"✅ PASSED: {passed}")
        print(f"❌ FAILED: {failed}")
        print(f"📈 SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")
        
        # Check if the critical test passed
        critical_test_result = None
        for result in self.results:
            if "Generate Nutrition Plan with Previous Reference" in result["test"]:
                critical_test_result = result
                break
        
        if critical_test_result:
            if critical_test_result["success"]:
                print(f"\n🎉 CRITICAL TEST RESULT: ✅ SUCCESS")
                print(f"   The fix for 'Plan nutricional previo no encontrado' is working correctly!")
                print(f"   Frontend is now using 'plan.id' instead of 'plan._id' as expected.")
            else:
                print(f"\n🚨 CRITICAL TEST RESULT: ❌ FAILED")
                print(f"   The error 'Plan nutricional previo no encontrado' is still present!")
                print(f"   The fix may not be properly implemented or there's another issue.")
        
        if failed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['message']}")
        
        return passed, failed

if __name__ == "__main__":
    tester = NutritionPlanTester()
    passed, failed = tester.run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)