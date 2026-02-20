import os
from dotenv import load_dotenv

load_dotenv()

# ----------------------
# Database
# ----------------------
DATABASE_URL = os.getenv("DATABASE_URL")

# ----------------------
# JWT Settings
# ----------------------
SECRET_KEY = "supersecretkey123"   # You can change this later
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# ----------------------
# File Upload Directory
# ----------------------
UPLOAD_DIR = "files"

# Create upload folder if not exists
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
