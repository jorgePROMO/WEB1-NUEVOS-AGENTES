#!/usr/bin/env python3
"""
Debug script to check nutrition questionnaire submissions and plans
"""

import requests
import json

BACKEND_URL = "https://edn360-audit.preview.emergentagent.com/api"

def debug_nutrition():
    # Login as admin
    login_url = f"{BACKEND_URL}/auth/login"
    params = {
        "email": "ecjtrainer@gmail.com",
        "password": "jorge3007"
    }
    
    response = requests.post(login_url, params=params)
    if response.status_code != 200:
        print(f"Login failed: {response.status_code}")
        return
    
    data = response.json()
    admin_token = data["token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get clients
    clients_url = f"{BACKEND_URL}/admin/clients"
    response = requests.get(clients_url, headers=headers)
    clients = response.json()["clients"]
    
    if not clients:
        print("No clients found")
        return
    
    client = clients[0]
    client_id = client["id"]
    print(f"Testing with client: {client['email']} (ID: {client_id})")
    
    # Get client details to see forms and submissions
    client_detail_url = f"{BACKEND_URL}/admin/clients/{client_id}"
    response = requests.get(client_detail_url, headers=headers)
    
    if response.status_code == 200:
        client_data = response.json()
        forms = client_data.get("forms", [])
        
        print(f"\nClient has {len(forms)} forms:")
        nutrition_forms = []
        for form in forms:
            print(f"  - Form ID: {form.get('id')}, Type: {form.get('type', 'N/A')}")
            if form.get('type') == 'nutrition':
                nutrition_forms.append(form)
        
        print(f"\nNutrition forms: {len(nutrition_forms)}")
        for form in nutrition_forms:
            print(f"  - Nutrition Form ID: {form.get('id')}, Plan Generated: {form.get('plan_generated', False)}")
    
    # Get nutrition plans
    nutrition_url = f"{BACKEND_URL}/admin/users/{client_id}/nutrition"
    response = requests.get(nutrition_url, headers=headers)
    
    if response.status_code == 200:
        nutrition_data = response.json()
        plans = nutrition_data.get("plans", [])
        
        print(f"\nClient has {len(plans)} nutrition plans:")
        for plan in plans:
            print(f"  - Plan ID: {plan.get('id')}")
            print(f"    Generated: {plan.get('generated_at')}")
            print(f"    Submission ID: {plan.get('submission_id', 'N/A')}")
            print(f"    Has content: {bool(plan.get('plan_content'))}")
            print()
    else:
        print(f"Failed to get nutrition plans: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    debug_nutrition()