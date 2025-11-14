#!/usr/bin/env python3
"""
CRM External Clients Testing - Focused Test Suite
Tests the newly implemented CRM system endpoints for External Clients
"""

import requests
import json
import sys
import os
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://aicoach-360.preview.emergentagent.com/api"

class CRMExternalClientsTester:
    def __init__(self):
        self.admin_token = None
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

    def test_2_create_external_client(self):
        """Test 2: Create external client for testing"""
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

    def test_3_get_external_clients_list(self):
        """Test 3: GET /api/admin/external-clients (list)"""
        if not self.admin_token:
            self.log_result("GET External Clients List", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "clients" in data and "total" in data:
                    self.log_result("GET External Clients List", True, 
                                  f"External clients list retrieved. Total: {data['total']}")
                    return True
                else:
                    self.log_result("GET External Clients List", False, 
                                  "Response missing clients or total", data)
            else:
                self.log_result("GET External Clients List", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET External Clients List", False, f"Exception: {str(e)}")
        
        return False

    def test_4_get_external_client_detail(self):
        """Test 4: GET /api/admin/external-clients/{client_id} (detail)"""
        if not self.admin_token or not self.test_external_client_id:
            self.log_result("GET External Client Detail", False, "No admin token or client ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients/{self.test_external_client_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if "id" in data and "nombre" in data:
                    self.log_result("GET External Client Detail", True, 
                                  f"External client detail retrieved. Name: {data.get('nombre')}")
                    return True
                else:
                    self.log_result("GET External Client Detail", False, 
                                  "Response missing required fields", data)
            else:
                self.log_result("GET External Client Detail", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("GET External Client Detail", False, f"Exception: {str(e)}")
        
        return False

    def test_5_update_basic_info(self):
        """Test 5: PATCH /api/admin/external-clients/{client_id} - Update nombre, email, whatsapp"""
        if not self.admin_token or not self.test_external_client_id:
            self.log_result("PATCH Update Basic Info", False, "No admin token or client ID available")
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
                    self.log_result("PATCH Update Basic Info", True, 
                                  f"Basic info updated successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("PATCH Update Basic Info", False, 
                                  "Response success not True", data)
            else:
                self.log_result("PATCH Update Basic Info", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("PATCH Update Basic Info", False, f"Exception: {str(e)}")
        
        return False

    def test_6_update_plan_weeks(self):
        """Test 6: PATCH /api/admin/external-clients/{client_id} - Update plan_weeks (should recalculate next_payment_date)"""
        if not self.admin_token or not self.test_external_client_id:
            self.log_result("PATCH Update Plan Weeks", False, "No admin token or client ID available")
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
                    self.log_result("PATCH Update Plan Weeks", True, 
                                  f"Plan weeks updated successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("PATCH Update Plan Weeks", False, 
                                  "Response success not True", data)
            else:
                self.log_result("PATCH Update Plan Weeks", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("PATCH Update Plan Weeks", False, f"Exception: {str(e)}")
        
        return False

    def test_7_update_start_date(self):
        """Test 7: PATCH /api/admin/external-clients/{client_id} - Update start_date (should recalculate next_payment_date)"""
        if not self.admin_token or not self.test_external_client_id:
            self.log_result("PATCH Update Start Date", False, "No admin token or client ID available")
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
                    self.log_result("PATCH Update Start Date", True, 
                                  f"Start date updated successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("PATCH Update Start Date", False, 
                                  "Response success not True", data)
            else:
                self.log_result("PATCH Update Start Date", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("PATCH Update Start Date", False, f"Exception: {str(e)}")
        
        return False

    def test_8_update_weeks_completed(self):
        """Test 8: PATCH /api/admin/external-clients/{client_id} - Update weeks_completed"""
        if not self.admin_token or not self.test_external_client_id:
            self.log_result("PATCH Update Weeks Completed", False, "No admin token or client ID available")
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
                    self.log_result("PATCH Update Weeks Completed", True, 
                                  f"Weeks completed updated successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("PATCH Update Weeks Completed", False, 
                                  "Response success not True", data)
            else:
                self.log_result("PATCH Update Weeks Completed", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("PATCH Update Weeks Completed", False, f"Exception: {str(e)}")
        
        return False

    def test_9_partial_update(self):
        """Test 9: PATCH /api/admin/external-clients/{client_id} - Partial update (only some fields)"""
        if not self.admin_token or not self.test_external_client_id:
            self.log_result("PATCH Partial Update", False, "No admin token or client ID available")
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
                    self.log_result("PATCH Partial Update", True, 
                                  f"Partial update successful: {data.get('message')}")
                    return True
                else:
                    self.log_result("PATCH Partial Update", False, 
                                  "Response success not True", data)
            else:
                self.log_result("PATCH Partial Update", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("PATCH Partial Update", False, f"Exception: {str(e)}")
        
        return False

    def test_10_update_404_error(self):
        """Test 10: PATCH /api/admin/external-clients/{client_id} - Test 404 for non-existent client"""
        if not self.admin_token:
            self.log_result("PATCH 404 Error Test", False, "No admin token available")
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
                self.log_result("PATCH 404 Error Test", True, 
                              "Correctly returned 404 for non-existent client")
                return True
            else:
                self.log_result("PATCH 404 Error Test", False, 
                              f"Expected 404, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("PATCH 404 Error Test", False, f"Exception: {str(e)}")
        
        return False

    def test_11_verify_updates_applied(self):
        """Test 11: Verify that all updates were applied correctly"""
        if not self.admin_token or not self.test_external_client_id:
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

    def test_12_update_status(self):
        """Test 12: PATCH /api/admin/external-clients/{client_id}/status"""
        if not self.admin_token or not self.test_external_client_id:
            self.log_result("PATCH Update Status", False, "No admin token or client ID available")
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
                    self.log_result("PATCH Update Status", True, 
                                  f"Status updated successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("PATCH Update Status", False, 
                                  "Response success not True", data)
            else:
                self.log_result("PATCH Update Status", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("PATCH Update Status", False, f"Exception: {str(e)}")
        
        return False

    def test_13_delete_external_client(self):
        """Test 13: DELETE /api/admin/external-clients/{client_id} - Clean up test data"""
        if not self.admin_token or not self.test_external_client_id:
            self.log_result("DELETE External Client", False, "No admin token or client ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/external-clients/{self.test_external_client_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.delete(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    self.log_result("DELETE External Client", True, 
                                  f"Test client deleted successfully: {data.get('message')}")
                    return True
                else:
                    self.log_result("DELETE External Client", False, 
                                  "Response success not True", data)
            else:
                self.log_result("DELETE External Client", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("DELETE External Client", False, f"Exception: {str(e)}")
        
        return False

    def run_all_tests(self):
        """Run all CRM External Clients tests in sequence"""
        print(f"🎯 CRM External Clients Testing Suite")
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Credentials: ecjtrainer@gmail.com / jorge3007")
        print("=" * 80)
        
        # Run tests in order
        tests = [
            self.test_1_admin_login,
            self.test_2_create_external_client,
            self.test_3_get_external_clients_list,
            self.test_4_get_external_client_detail,
            self.test_5_update_basic_info,
            self.test_6_update_plan_weeks,
            self.test_7_update_start_date,
            self.test_8_update_weeks_completed,
            self.test_9_partial_update,
            self.test_10_update_404_error,
            self.test_11_verify_updates_applied,
            self.test_12_update_status,
            self.test_13_delete_external_client
        ]
        
        for test in tests:
            test()
            print()
        
        # Summary
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        print("=" * 80)
        print(f"📊 CRM EXTERNAL CLIENTS TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All CRM External Clients tests PASSED!")
            print("✅ The newly implemented CRM system endpoints are working correctly")
        else:
            print("⚠️  Some CRM External Clients tests FAILED!")
            failed_tests = [r["test"] for r in self.results if not r["success"]]
            print(f"Failed tests: {', '.join(failed_tests)}")
        
        return passed == total

def main():
    """Main function"""
    tester = CRMExternalClientsTester()
    success = tester.run_all_tests()
    
    # Save results to file
    with open("/app/crm_external_clients_test_results.json", "w") as f:
        json.dump(tester.results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/crm_external_clients_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())