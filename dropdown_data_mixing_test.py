#!/usr/bin/env python3
"""
Dropdown Data Mixing Fix - Seguimiento Tab Testing
Tests the specific fix for dropdown data mixing in AdminDashboard Seguimiento tab
"""

import requests
import json
import sys
import os
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://flowsmart-agents.preview.emergentagent.com/api"

class DropdownDataMixingTester:
    def __init__(self):
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
    
    def test_1_admin_login(self):
        """Test 1: Admin login with ecjtrainer@gmail.com / jorge3007"""
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
    
    def test_2_get_clients_and_select_one(self):
        """Test 2: Get clients and select one with data"""
        if not self.admin_token:
            self.log_result("Get Clients", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "clients" in data and len(data["clients"]) > 0:
                    # Select the first client for testing
                    self.test_user_id = data["clients"][0]["id"]
                    client_email = data["clients"][0].get("email", "N/A")
                    self.log_result("Get Clients", True, 
                                  f"Found {len(data['clients'])} clients. Selected client: {client_email} (ID: {self.test_user_id})")
                    return True
                else:
                    self.log_result("Get Clients", False, 
                                  "No clients found in system", data)
            else:
                self.log_result("Get Clients", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get Clients", False, f"Exception: {str(e)}")
        
        return False
    
    def test_3_verify_training_plans_endpoint(self):
        """Test 3: Verify Training Plans Endpoint - Should return ONLY training plans"""
        if not self.admin_token or not self.test_user_id:
            self.log_result("Training Plans Endpoint", False, "No admin token or user ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/users/{self.test_user_id}/training-plans"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                plans = data if isinstance(data, list) else data.get("plans", [])
                
                # Verify each plan is a training plan
                training_plan_count = 0
                questionnaire_count = 0
                nutrition_plan_count = 0
                
                for plan in plans:
                    plan_type = plan.get("type", "").lower()
                    if "training" in plan_type or plan_type == "training_plan":
                        training_plan_count += 1
                        # Verify label format
                        label = plan.get("label", "")
                        if not ("PLAN ENTRENAMIENTO" in label.upper() or "TRAINING" in label.upper()):
                            self.log_result("Training Plans Endpoint", False, 
                                          f"Training plan has incorrect label format: {label}")
                            return False
                    elif "followup" in plan_type or "cuestionario" in plan_type.lower():
                        questionnaire_count += 1
                    elif "nutrition" in plan_type or plan_type == "nutrition_plan":
                        nutrition_plan_count += 1
                
                if questionnaire_count > 0 or nutrition_plan_count > 0:
                    self.log_result("Training Plans Endpoint", False, 
                                  f"❌ DATA MIXING DETECTED: Found {questionnaire_count} questionnaires and {nutrition_plan_count} nutrition plans in training plans endpoint")
                    return False
                else:
                    self.log_result("Training Plans Endpoint", True, 
                                  f"✅ CORRECT: Found {training_plan_count} training plans, 0 questionnaires, 0 nutrition plans")
                    return True
            else:
                self.log_result("Training Plans Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Training Plans Endpoint", False, f"Exception: {str(e)}")
        
        return False
    
    def test_4_verify_nutrition_plans_endpoint(self):
        """Test 4: Verify Nutrition Plans Endpoint - Should return ONLY nutrition plans"""
        if not self.admin_token or not self.test_user_id:
            self.log_result("Nutrition Plans Endpoint", False, "No admin token or user ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/users/{self.test_user_id}/nutrition-plans"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                plans = data if isinstance(data, list) else data.get("plans", [])
                
                # Verify each plan is a nutrition plan
                nutrition_plan_count = 0
                questionnaire_count = 0
                training_plan_count = 0
                
                for plan in plans:
                    plan_type = plan.get("type", "").lower()
                    if "nutrition" in plan_type or plan_type == "nutrition_plan":
                        nutrition_plan_count += 1
                        # Verify label format
                        label = plan.get("label", "")
                        if not ("PLAN NUTRICION" in label.upper() or "NUTRITION" in label.upper()):
                            self.log_result("Nutrition Plans Endpoint", False, 
                                          f"Nutrition plan has incorrect label format: {label}")
                            return False
                    elif "followup" in plan_type or "cuestionario" in plan_type.lower():
                        questionnaire_count += 1
                    elif "training" in plan_type or plan_type == "training_plan":
                        training_plan_count += 1
                
                if questionnaire_count > 0 or training_plan_count > 0:
                    self.log_result("Nutrition Plans Endpoint", False, 
                                  f"❌ DATA MIXING DETECTED: Found {questionnaire_count} questionnaires and {training_plan_count} training plans in nutrition plans endpoint")
                    return False
                else:
                    self.log_result("Nutrition Plans Endpoint", True, 
                                  f"✅ CORRECT: Found {nutrition_plan_count} nutrition plans, 0 questionnaires, 0 training plans")
                    return True
            else:
                self.log_result("Nutrition Plans Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Nutrition Plans Endpoint", False, f"Exception: {str(e)}")
        
        return False
    
    def test_5_verify_followup_questionnaires_endpoint(self):
        """Test 5: Verify Follow-up Questionnaires Endpoint - Should return ONLY follow-up questionnaires"""
        if not self.admin_token or not self.test_user_id:
            self.log_result("Follow-up Questionnaires Endpoint", False, "No admin token or user ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/users/{self.test_user_id}/follow-up-questionnaires"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                questionnaires = data if isinstance(data, list) else data.get("questionnaires", [])
                
                # Verify each item is a follow-up questionnaire
                followup_count = 0
                nutrition_plan_count = 0
                training_plan_count = 0
                
                for item in questionnaires:
                    source_type = item.get("source_type", "").lower()
                    item_type = item.get("type", "").lower()
                    
                    if "followup" in source_type or "seguimiento" in source_type.lower():
                        followup_count += 1
                    elif "nutrition" in item_type or item_type == "nutrition_plan":
                        nutrition_plan_count += 1
                    elif "training" in item_type or item_type == "training_plan":
                        training_plan_count += 1
                
                if nutrition_plan_count > 0 or training_plan_count > 0:
                    self.log_result("Follow-up Questionnaires Endpoint", False, 
                                  f"❌ DATA MIXING DETECTED: Found {nutrition_plan_count} nutrition plans and {training_plan_count} training plans in follow-up questionnaires endpoint")
                    return False
                else:
                    if followup_count == 0:
                        self.log_result("Follow-up Questionnaires Endpoint", True, 
                                      f"✅ CORRECT: Array is empty (no follow-up questionnaires exist for this user)")
                    else:
                        self.log_result("Follow-up Questionnaires Endpoint", True, 
                                      f"✅ CORRECT: Found {followup_count} follow-up questionnaires, 0 nutrition plans, 0 training plans")
                    return True
            else:
                self.log_result("Follow-up Questionnaires Endpoint", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Follow-up Questionnaires Endpoint", False, f"Exception: {str(e)}")
        
        return False
    
    def test_6_verify_data_separation(self):
        """Test 6: Verify Data Separation - Compare IDs across all 3 endpoints"""
        if not self.admin_token or not self.test_user_id:
            self.log_result("Data Separation Verification", False, "No admin token or user ID available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Get data from all 3 endpoints
            training_url = f"{BACKEND_URL}/admin/users/{self.test_user_id}/training-plans"
            nutrition_url = f"{BACKEND_URL}/admin/users/{self.test_user_id}/nutrition-plans"
            followup_url = f"{BACKEND_URL}/admin/users/{self.test_user_id}/follow-up-questionnaires"
            
            training_response = requests.get(training_url, headers=headers)
            nutrition_response = requests.get(nutrition_url, headers=headers)
            followup_response = requests.get(followup_url, headers=headers)
            
            if training_response.status_code != 200 or nutrition_response.status_code != 200 or followup_response.status_code != 200:
                self.log_result("Data Separation Verification", False, 
                              f"One or more endpoints failed: Training: {training_response.status_code}, Nutrition: {nutrition_response.status_code}, Follow-up: {followup_response.status_code}")
                return False
            
            # Extract IDs from each endpoint
            training_data = training_response.json()
            nutrition_data = nutrition_response.json()
            followup_data = followup_response.json()
            
            training_plans = training_data if isinstance(training_data, list) else training_data.get("plans", [])
            nutrition_plans = nutrition_data if isinstance(nutrition_data, list) else nutrition_data.get("plans", [])
            followup_questionnaires = followup_data if isinstance(followup_data, list) else followup_data.get("questionnaires", [])
            
            training_ids = set(plan.get("id") for plan in training_plans if plan.get("id"))
            nutrition_ids = set(plan.get("id") for plan in nutrition_plans if plan.get("id"))
            followup_ids = set(item.get("id") for item in followup_questionnaires if item.get("id"))
            
            # Check for overlapping IDs
            training_nutrition_overlap = training_ids.intersection(nutrition_ids)
            training_followup_overlap = training_ids.intersection(followup_ids)
            nutrition_followup_overlap = nutrition_ids.intersection(followup_ids)
            
            if training_nutrition_overlap or training_followup_overlap or nutrition_followup_overlap:
                overlaps = []
                if training_nutrition_overlap:
                    overlaps.append(f"Training-Nutrition: {training_nutrition_overlap}")
                if training_followup_overlap:
                    overlaps.append(f"Training-Followup: {training_followup_overlap}")
                if nutrition_followup_overlap:
                    overlaps.append(f"Nutrition-Followup: {nutrition_followup_overlap}")
                
                self.log_result("Data Separation Verification", False, 
                              f"❌ ID OVERLAP DETECTED: {'; '.join(overlaps)}")
                return False
            else:
                self.log_result("Data Separation Verification", True, 
                              f"✅ CORRECT: No ID overlaps detected. Training: {len(training_ids)} IDs, Nutrition: {len(nutrition_ids)} IDs, Follow-up: {len(followup_ids)} IDs")
                return True
                
        except Exception as e:
            self.log_result("Data Separation Verification", False, f"Exception: {str(e)}")
        
        return False
    
    def test_7_verify_object_structure(self):
        """Test 7: Verify object structure and format for each endpoint"""
        if not self.admin_token or not self.test_user_id:
            self.log_result("Object Structure Verification", False, "No admin token or user ID available")
            return False
        
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            # Test training plans structure
            training_url = f"{BACKEND_URL}/admin/users/{self.test_user_id}/training-plans"
            training_response = requests.get(training_url, headers=headers)
            
            if training_response.status_code == 200:
                training_data = training_response.json()
                training_plans = training_data if isinstance(training_data, list) else training_data.get("plans", [])
                
                for plan in training_plans:
                    if not plan.get("id"):
                        self.log_result("Object Structure Verification", False, 
                                      "Training plan missing 'id' field")
                        return False
                    if not plan.get("label"):
                        self.log_result("Object Structure Verification", False, 
                                      "Training plan missing 'label' field")
                        return False
            
            # Test nutrition plans structure
            nutrition_url = f"{BACKEND_URL}/admin/users/{self.test_user_id}/nutrition-plans"
            nutrition_response = requests.get(nutrition_url, headers=headers)
            
            if nutrition_response.status_code == 200:
                nutrition_data = nutrition_response.json()
                nutrition_plans = nutrition_data if isinstance(nutrition_data, list) else nutrition_data.get("plans", [])
                
                for plan in nutrition_plans:
                    if not plan.get("id"):
                        self.log_result("Object Structure Verification", False, 
                                      "Nutrition plan missing 'id' field")
                        return False
                    if not plan.get("label"):
                        self.log_result("Object Structure Verification", False, 
                                      "Nutrition plan missing 'label' field")
                        return False
            
            # Test follow-up questionnaires structure
            followup_url = f"{BACKEND_URL}/admin/users/{self.test_user_id}/follow-up-questionnaires"
            followup_response = requests.get(followup_url, headers=headers)
            
            if followup_response.status_code == 200:
                followup_data = followup_response.json()
                followup_questionnaires = followup_data if isinstance(followup_data, list) else followup_data.get("questionnaires", [])
                
                for item in followup_questionnaires:
                    if not item.get("id"):
                        self.log_result("Object Structure Verification", False, 
                                      "Follow-up questionnaire missing 'id' field")
                        return False
                    if not item.get("source_type"):
                        self.log_result("Object Structure Verification", False, 
                                      "Follow-up questionnaire missing 'source_type' field")
                        return False
            
            self.log_result("Object Structure Verification", True, 
                          "✅ CORRECT: All objects have required fields (id, label/source_type)")
            return True
            
        except Exception as e:
            self.log_result("Object Structure Verification", False, f"Exception: {str(e)}")
        
        return False
    
    def run_all_tests(self):
        """Run all dropdown data mixing tests"""
        print("🎯 TESTING CRÍTICO: Dropdown Data Mixing Fix - Seguimiento Tab")
        print("=" * 70)
        
        tests = [
            self.test_1_admin_login,
            self.test_2_get_clients_and_select_one,
            self.test_3_verify_training_plans_endpoint,
            self.test_4_verify_nutrition_plans_endpoint,
            self.test_5_verify_followup_questionnaires_endpoint,
            self.test_6_verify_data_separation,
            self.test_7_verify_object_structure
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
            print()  # Add spacing between tests
        
        print("=" * 70)
        print(f"RESULTS: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Dropdown data mixing fix is working correctly!")
        else:
            print("❌ SOME TESTS FAILED - Dropdown data mixing issue may still exist")
        
        return passed == total
    
    def print_summary(self):
        """Print detailed summary of test results"""
        print("\n" + "=" * 70)
        print("DETAILED TEST SUMMARY")
        print("=" * 70)
        
        for result in self.results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}")
            print(f"    Message: {result['message']}")
            if not result["success"] and result.get("response_data"):
                print(f"    Data: {str(result['response_data'])[:200]}...")
            print()

if __name__ == "__main__":
    tester = DropdownDataMixingTester()
    success = tester.run_all_tests()
    tester.print_summary()
    
    sys.exit(0 if success else 1)