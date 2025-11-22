#!/usr/bin/env python3
"""
Test the second client to ensure consistency across different users
"""

import requests
import json

BACKEND_URL = "https://state-manager-1.preview.emergentagent.com/api"

def test_second_client():
    # Login as admin
    login_url = f"{BACKEND_URL}/auth/login"
    params = {
        "email": "ecjtrainer@gmail.com",
        "password": "jorge3007"
    }
    
    response = requests.post(login_url, params=params)
    if response.status_code != 200:
        print("❌ Admin login failed")
        return
    
    admin_token = response.json()["token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get all clients
    clients_url = f"{BACKEND_URL}/admin/clients"
    response = requests.get(clients_url, headers=headers)
    if response.status_code != 200:
        print("❌ Failed to get clients")
        return
    
    clients = response.json()["clients"]
    if len(clients) < 2:
        print("❌ Not enough clients to test second client")
        return
    
    # Test second client
    second_client = clients[1]
    user_id = second_client["id"]
    client_email = second_client.get("email", "N/A")
    
    print(f"🔍 Testing second client: {client_email} (ID: {user_id})")
    
    # Test all three endpoints
    endpoints = [
        ("training-plans", "Training Plans"),
        ("nutrition-plans", "Nutrition Plans"), 
        ("follow-up-questionnaires", "Follow-up Questionnaires")
    ]
    
    for endpoint, name in endpoints:
        url = f"{BACKEND_URL}/admin/users/{user_id}/{endpoint}"
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            items = data if isinstance(data, list) else data.get("plans", data.get("questionnaires", []))
            print(f"✅ {name}: {len(items)} items returned")
            
            # Check for data mixing
            for item in items:
                item_type = item.get("type", "").lower()
                source_type = item.get("source_type", "").lower()
                
                if endpoint == "training-plans" and "training" not in item_type:
                    print(f"❌ {name}: Found non-training item: {item_type}")
                elif endpoint == "nutrition-plans" and "nutrition" not in item_type:
                    print(f"❌ {name}: Found non-nutrition item: {item_type}")
                elif endpoint == "follow-up-questionnaires" and "followup" not in source_type:
                    print(f"❌ {name}: Found non-followup item: {source_type}")
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
    
    print("✅ Second client test completed")

if __name__ == "__main__":
    test_second_client()