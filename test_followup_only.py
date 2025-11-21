#!/usr/bin/env python3
"""
Monthly Follow-up System Testing Only
Tests the newly implemented monthly follow-up system endpoints
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://edn-job-runner.preview.emergentagent.com/api"

class FollowUpTester:
    def __init__(self):
        self.admin_token = None
        self.user_token = None
        self.followup_test_user_id = None
        self.dashboard_test_user_id = None
        self.dashboard_test_user_token = None
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

    def test_admin_login(self):
        """Admin login with correct credentials for follow-up testing"""
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

    def test_get_pending_reviews(self):
        """GET /api/admin/pending-reviews - Get clients with nutrition plans >= 30 days old"""
        if not self.admin_token:
            self.log_result("Get Pending Reviews", False, "No admin token available")
            return False
            
        url = f"{BACKEND_URL}/admin/pending-reviews"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                if "pending_reviews" in data and "count" in data:
                    pending_reviews = data["pending_reviews"]
                    count = data["count"]
                    
                    # Verify each review has required fields
                    required_fields = ["user_id", "name", "email", "phone", "days_since_plan", 
                                     "last_plan_date", "status", "status_date", "followup_activated", "last_followup_id"]
                    
                    all_valid = True
                    for review in pending_reviews:
                        missing_fields = [field for field in required_fields if field not in review]
                        if missing_fields:
                            all_valid = False
                            self.log_result("Get Pending Reviews", False, 
                                          f"Review missing fields: {missing_fields}")
                            break
                    
                    if all_valid:
                        # Store a user_id for follow-up tests (preferably with status="pending")
                        self.followup_test_user_id = None
                        for review in pending_reviews:
                            if review.get("status") == "pending":
                                self.followup_test_user_id = review["user_id"]
                                break
                        
                        # If no pending, use any available user
                        if not self.followup_test_user_id and pending_reviews:
                            self.followup_test_user_id = pending_reviews[0]["user_id"]
                        
                        self.log_result("Get Pending Reviews", True, 
                                      f"Pending reviews retrieved successfully. Count: {count}, Reviews: {len(pending_reviews)}")
                        return True
                    
                else:
                    self.log_result("Get Pending Reviews", False, 
                                  "Response missing pending_reviews or count", data)
            else:
                self.log_result("Get Pending Reviews", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get Pending Reviews", False, f"Exception: {str(e)}")
        
        return False

    def test_activate_followup_for_user(self):
        """POST /api/admin/users/{user_id}/activate-followup - Activate follow-up questionnaire"""
        if not self.admin_token:
            self.log_result("Activate Follow-up for User", False, "No admin token available")
            return False
        
        # If no user from pending reviews, use the dashboard test user
        if not self.followup_test_user_id:
            if hasattr(self, 'dashboard_test_user_id'):
                self.followup_test_user_id = self.dashboard_test_user_id
                self.log_result("Activate Follow-up for User", True, 
                              f"Using dashboard test user ID: {self.followup_test_user_id}")
            else:
                self.log_result("Activate Follow-up for User", False, "No test user ID available")
                return False
            
        url = f"{BACKEND_URL}/admin/users/{self.followup_test_user_id}/activate-followup"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.post(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    message = data.get("message", "")
                    expected_message = "Cuestionario de seguimiento activado correctamente"
                    if expected_message in message:
                        self.log_result("Activate Follow-up for User", True, 
                                      f"Follow-up activated successfully: {message}")
                        return True
                    else:
                        self.log_result("Activate Follow-up for User", False, 
                                      f"Unexpected message: {message}")
                else:
                    self.log_result("Activate Follow-up for User", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Activate Follow-up for User", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Activate Follow-up for User", False, f"Exception: {str(e)}")
        
        return False

    def test_verify_status_changed_to_activated(self):
        """Verify status changed to 'activated' after activation"""
        if not self.admin_token:
            self.log_result("Verify Status Changed to Activated", False, "No admin token available")
            return False
        
        if not self.followup_test_user_id:
            self.log_result("Verify Status Changed to Activated", False, "No test user ID available")
            return False
            
        # Check user directly via admin/clients endpoint since user might not have nutrition plan
        url = f"{BACKEND_URL}/admin/clients/{self.followup_test_user_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                
                followup_activated = user_data.get("followup_activated", False)
                followup_activated_at = user_data.get("followup_activated_at")
                followup_activated_by = user_data.get("followup_activated_by")
                
                if followup_activated == True and followup_activated_by == "admin":
                    self.log_result("Verify Status Changed to Activated", True, 
                                  f"Follow-up correctly activated: followup_activated={followup_activated}, activated_by={followup_activated_by}, activated_at={followup_activated_at}")
                    return True
                else:
                    self.log_result("Verify Status Changed to Activated", False, 
                                  f"Follow-up not activated correctly: followup_activated={followup_activated}, activated_by={followup_activated_by}")
            else:
                self.log_result("Verify Status Changed to Activated", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Verify Status Changed to Activated", False, f"Exception: {str(e)}")
        
        return False

    def test_register_user_for_dashboard_test(self):
        """Register a regular user to test dashboard followup_activated field"""
        url = f"{BACKEND_URL}/auth/register"
        
        # Use unique timestamp for test user
        timestamp = str(int(datetime.now().timestamp()))
        test_email = f"test_followup_dashboard_{timestamp}@example.com"
        
        payload = {
            "username": f"test_followup_{timestamp}",
            "email": test_email,
            "password": "Test123!",
            "phone": "+34600000002"
        }
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                if "user" in data and "token" in data:
                    self.dashboard_test_user_token = data["token"]
                    self.dashboard_test_user_id = data["user"]["id"]
                    self.log_result("Register User for Dashboard Test", True, 
                                  f"Test user registered for dashboard testing. ID: {self.dashboard_test_user_id}")
                    return True
                else:
                    self.log_result("Register User for Dashboard Test", False, 
                                  "Response missing user or token", data)
            else:
                self.log_result("Register User for Dashboard Test", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Register User for Dashboard Test", False, f"Exception: {str(e)}")
        
        return False

    def test_get_user_dashboard_followup_status(self):
        """GET /api/users/dashboard - Verify followup_activated field is included"""
        if not self.dashboard_test_user_token:
            self.log_result("Get User Dashboard Follow-up Status", False, "No user token available")
            return False
            
        url = f"{BACKEND_URL}/users/dashboard"
        headers = {"Authorization": f"Bearer {self.dashboard_test_user_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                if "user" in data:
                    user_data = data["user"]
                    if "followup_activated" in user_data:
                        followup_activated = user_data["followup_activated"]
                        self.log_result("Get User Dashboard Follow-up Status", True, 
                                      f"Dashboard includes followup_activated field: {followup_activated}")
                        return True
                    else:
                        self.log_result("Get User Dashboard Follow-up Status", False, 
                                      "Dashboard user data missing followup_activated field")
                else:
                    self.log_result("Get User Dashboard Follow-up Status", False, 
                                  "Dashboard response missing user data", data)
            else:
                self.log_result("Get User Dashboard Follow-up Status", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Get User Dashboard Follow-up Status", False, f"Exception: {str(e)}")
        
        return False

    def test_deactivate_followup_for_user(self):
        """POST /api/admin/users/{user_id}/deactivate-followup - Deactivate follow-up questionnaire"""
        if not self.admin_token:
            self.log_result("Deactivate Follow-up for User", False, "No admin token available")
            return False
        
        if not self.followup_test_user_id:
            self.log_result("Deactivate Follow-up for User", False, "No test user ID available")
            return False
            
        url = f"{BACKEND_URL}/admin/users/{self.followup_test_user_id}/deactivate-followup"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.post(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") == True:
                    message = data.get("message", "")
                    expected_message = "Cuestionario de seguimiento desactivado"
                    if expected_message in message:
                        self.log_result("Deactivate Follow-up for User", True, 
                                      f"Follow-up deactivated successfully: {message}")
                        return True
                    else:
                        self.log_result("Deactivate Follow-up for User", False, 
                                      f"Unexpected message: {message}")
                else:
                    self.log_result("Deactivate Follow-up for User", False, 
                                  "Response success not True", data)
            else:
                self.log_result("Deactivate Follow-up for User", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Deactivate Follow-up for User", False, f"Exception: {str(e)}")
        
        return False

    def test_verify_status_changed_back_after_deactivation(self):
        """Verify status changed back after deactivation"""
        if not self.admin_token:
            self.log_result("Verify Status Changed Back After Deactivation", False, "No admin token available")
            return False
        
        if not self.followup_test_user_id:
            self.log_result("Verify Status Changed Back After Deactivation", False, "No test user ID available")
            return False
            
        # Check user directly via admin/clients endpoint
        url = f"{BACKEND_URL}/admin/clients/{self.followup_test_user_id}"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get("user", {})
                
                followup_activated = user_data.get("followup_activated", False)
                
                if followup_activated == False:
                    self.log_result("Verify Status Changed Back After Deactivation", True, 
                                  f"Follow-up correctly deactivated: followup_activated={followup_activated}")
                    return True
                else:
                    self.log_result("Verify Status Changed Back After Deactivation", False, 
                                  f"Follow-up not deactivated: followup_activated={followup_activated}")
            else:
                self.log_result("Verify Status Changed Back After Deactivation", False, 
                              f"HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Verify Status Changed Back After Deactivation", False, f"Exception: {str(e)}")
        
        return False

    def test_404_for_nonexistent_user_activate(self):
        """Test 404 error for non-existent user_id in activate endpoint"""
        if not self.admin_token:
            self.log_result("Test 404 for Non-existent User Activate", False, "No admin token available")
            return False
            
        fake_user_id = "nonexistent_user_id_12345"
        url = f"{BACKEND_URL}/admin/users/{fake_user_id}/activate-followup"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.post(url, headers=headers)
            
            if response.status_code == 404:
                self.log_result("Test 404 for Non-existent User Activate", True, 
                              "Correctly returned 404 for non-existent user in activate endpoint")
                return True
            else:
                self.log_result("Test 404 for Non-existent User Activate", False, 
                              f"Expected 404, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Test 404 for Non-existent User Activate", False, f"Exception: {str(e)}")
        
        return False

    def test_404_for_nonexistent_user_deactivate(self):
        """Test 404 error for non-existent user_id in deactivate endpoint"""
        if not self.admin_token:
            self.log_result("Test 404 for Non-existent User Deactivate", False, "No admin token available")
            return False
            
        fake_user_id = "nonexistent_user_id_12345"
        url = f"{BACKEND_URL}/admin/users/{fake_user_id}/deactivate-followup"
        headers = {"Authorization": f"Bearer {self.admin_token}"}
        
        try:
            response = requests.post(url, headers=headers)
            
            if response.status_code == 404:
                self.log_result("Test 404 for Non-existent User Deactivate", True, 
                              "Correctly returned 404 for non-existent user in deactivate endpoint")
                return True
            else:
                self.log_result("Test 404 for Non-existent User Deactivate", False, 
                              f"Expected 404, got HTTP {response.status_code}", response.text)
        except Exception as e:
            self.log_result("Test 404 for Non-existent User Deactivate", False, f"Exception: {str(e)}")
        
        return False

    def run_all_tests(self):
        """Run all monthly follow-up tests"""
        print(f"🚀 MONTHLY FOLLOW-UP SYSTEM TESTING")
        print(f"Backend URL: {BACKEND_URL}")
        print("=" * 80)
        
        # Run tests in order
        tests = [
            self.test_admin_login,
            self.test_get_pending_reviews,
            self.test_register_user_for_dashboard_test,
            self.test_activate_followup_for_user,
            self.test_verify_status_changed_to_activated,
            self.test_get_user_dashboard_followup_status,
            self.test_deactivate_followup_for_user,
            self.test_verify_status_changed_back_after_deactivation,
            self.test_404_for_nonexistent_user_activate,
            self.test_404_for_nonexistent_user_deactivate
        ]
        
        for test in tests:
            test()
            print()
        
        # Summary
        passed = sum(1 for r in self.results if r["success"])
        total = len(self.results)
        
        print("=" * 80)
        print(f"📊 MONTHLY FOLLOW-UP SYSTEM TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All monthly follow-up tests PASSED!")
        else:
            print("⚠️  Some tests FAILED!")
            failed_tests = [r["test"] for r in self.results if not r["success"]]
            print(f"Failed tests: {', '.join(failed_tests)}")
        
        return passed == total

def main():
    """Main function"""
    tester = FollowUpTester()
    success = tester.run_all_tests()
    
    # Save results to file
    with open("/app/followup_test_results.json", "w") as f:
        json.dump(tester.results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: /app/followup_test_results.json")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())