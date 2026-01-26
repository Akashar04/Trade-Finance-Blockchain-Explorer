import requests
import json
import random

BASE_URL = "http://127.0.0.1:8000"

def test_signup():
    # specialized email to avoid collision if possible, or just expect collision
    # using random int
    rand_id = random.randint(1000, 9999)
    email = f"testuser{rand_id}@example.com"
    password = "Test@123"
    
    payload = {
        "name": f"Test User {rand_id}",
        "email": email,
        "password": password,
        "org": "Test Bank",
        "role": "buyer"
    }
    
    print(f"Attempting signup with {email}...")
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    print("\nAttempting duplicate signup (expecting 400)...")
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

def test_signup_collision():
    # If we knew a user that exists... let's assume the one from valid login usage
    # But I don't valid creds.
    pass

if __name__ == "__main__":
    test_signup()
