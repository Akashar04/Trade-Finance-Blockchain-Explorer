import requests
import json
import random
import os

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token(role="buyer"):
    rand_id = random.randint(10000, 99999)
    email = f"test_{role}_{rand_id}@example.com"
    password = "Test@123"
    
    payload = {
        "name": f"Test {role} {rand_id}",
        "email": email,
        "password": password,
        "org": "Test Org",
        "role": role
    }
    
    # Signup
    requests.post(f"{BASE_URL}/auth/signup", json=payload)
    
    # Login
    response = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return None
        
    return response.json()["access_token"]

def test_upload():
    token = get_auth_token("buyer")
    if not token:
        return

    print("Authenticaton successful. Testing upload...")
    
    # Create a dummy file
    with open("test_doc.pdf", "wb") as f:
        f.write(b"%PDF-1.4 dummy content")
        
    files = {'file': open('test_doc.pdf', 'rb')}
    data = {
        'doc_number': f"PO-{random.randint(100,999)}",
        'seller_id': 123
    }
    headers = {'Authorization': f"Bearer {token}"}
    
    try:
        response = requests.post(f"{BASE_URL}/documents/upload", files=files, data=data, headers=headers)
        print(f"Upload Status Code: {response.status_code}")
        
        if response.status_code == 200:
            doc = response.json()
            print("Upload Response JSON:")
            print(json.dumps(doc, indent=2))
            
            # Verify Ledger Entry
            # Ideally the upload response is DocumentDetailResponse which has ledger_entries?
            # Wait, the route definition says response_model=DocumentDetailResponse.
            # But in the code:
            # session.refresh(document)
            # return document
            # Document model usually doesn't eager load ledger_entries unless specified or response model handles lazy load?
            # SQLModel relationships are lazy by default. 
            # If the response model expects it, FastAPI will try to serialize.
            # Let's see if it's there.
            
            # We might need to manually force loading or fetch details again if it's missing.
            
            # Getting details to be sure
            doc_id = doc["id"]
            detail_response = requests.get(f"{BASE_URL}/documents/{doc_id}", headers=headers)
            details = detail_response.json()
             
            entries = details.get("ledger_entries", [])
            print(f"\nLedger Entries found: {len(entries)}")
            for entry in entries:
                print(f"- Action: {entry['action']}")
                print(f"  Metadata: {entry['entry_metadata']}")
                
                if entry['action'] == "ISSUED" and "123" in entry['entry_metadata']:
                     print("\nSUCCESS: Ledger entry created with correct metadata!")
        else:
            print(f"Upload Failed: {response.text}")
            
    except Exception as e:
        print(f"Test failed: {e}")
    finally:
        if os.path.exists("test_doc.pdf"):
            os.remove("test_doc.pdf")

if __name__ == "__main__":
    test_upload()
