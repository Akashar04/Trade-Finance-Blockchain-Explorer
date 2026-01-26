import sys
import os

# Add backend directory to sys.path so we can import app modules
sys.path.append(os.getcwd())

output_file = "reproduce_output.txt"

def log(msg):
    with open(output_file, "a") as f:
        f.write(msg + "\n")
    print(msg)

if os.path.exists(output_file):
    os.remove(output_file)

try:
    from app.services.auth import hash_password, verify_password
except ImportError as e:
    log(f"Error importing app modules: {e}")
    sys.exit(1)

def test_hashing():
    log("Starting test...")
    password = "Test@123"
    log(f"Testing password: '{password}'")
    
    try:
        hashed = hash_password(password)
        log(f"Success! Hash: {hashed}")
        log(f"Hash length: {len(hashed)}")
    except Exception as e:
        log(f"Error hashing simple password: {e}")
        hashed = None

    if hashed:
        # Test double hashing scenario
        try:
            log("\nTesting double hashing (hashing the hash)...")
            hashed_again = hash_password(hashed)
            log(f"Success! Hash of hash: {hashed_again}")
        except Exception as e:
            log(f"Error hashing the hash: {e}")

    # Test long password
    long_password = "A" * 73
    log(f"\nTesting long password (73 chars)...")
    try:
        hash_password(long_password)
        log("Success (Unexpected if 72 byte limit is enforced strict)")
    except Exception as e:
        log(f"Caught expected error for long password: {e}")

    # Test verification
    if hashed:
        is_valid = verify_password(password, hashed)
        log(f"Verification result: {is_valid}")
        if is_valid:
            log("SUCCESS: Password verified correctly")
        else:
            log("FAILURE: Password failed verification")

    # Test long password
    long_password = "A" * 73
    log(f"\nTesting long password (73 chars)...")
    try:
        hash_password(long_password)
        log("Success: Long password hashed (bcrypt handles truncation/long input internally usually)")
    except Exception as e:
        log(f"Caught error for long password: {e}")

if __name__ == "__main__":
    test_hashing()
