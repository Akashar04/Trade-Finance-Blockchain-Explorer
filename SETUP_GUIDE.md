# Setup and Installation Guide

## Prerequisites

- Python 3.9+ (for backend)
- Node.js 16+ (for frontend)
- pip (Python package manager)
- npm (Node package manager)

## Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create virtual environment (optional but recommended)
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create .env file
Create a file named `.env` in the `backend` directory:

```
DATABASE_URL=sqlite:///./test.db
JWT_SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

For production, use a proper database like PostgreSQL:
```
DATABASE_URL=postgresql://user:password@localhost/trade_finance_db
```

### 5. Initialize the database
```bash
python -c "from app.db.session import engine; from app.db.models import SQLModel; SQLModel.metadata.create_all(engine)"
```

### 6. Run the backend server
```bash
python -m uvicorn app.main:app --reload
```

The backend will be available at: **http://localhost:8000**

Access the interactive API documentation at: **http://localhost:8000/docs**

## Frontend Setup

### 1. Navigate to frontend directory (in a new terminal)
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Start the development server
```bash
npm start
```

The frontend will automatically open at: **http://localhost:3000**

## Verify Everything is Working

### 1. Check Backend
- Visit: http://localhost:8000/docs
- You should see the Swagger UI with all available API endpoints

### 2. Check Frontend
- Visit: http://localhost:3000
- You should be redirected to login page

## Create Test Data

### 1. Sign up as Seller
Go to http://localhost:3000/signup and create account:
- Name: Alice Seller
- Email: seller@test.com
- Password: password123
- Organization: TestOrg
- Role: seller

### 2. Sign up as Buyer
Create another account:
- Name: Bob Buyer
- Email: buyer@test.com
- Password: password123
- Organization: TestOrg
- Role: buyer

### 3. Sign up as Bank
Create another account:
- Name: Charlie Bank
- Email: bank@test.com
- Password: password123
- Organization: TestOrg
- Role: bank

## Test the Document Workflow

### 1. Login as Seller
- Use seller@test.com / password123
- Click "Upload Document"
- Fill in:
  - Doc Number: PO-2024-001
  - Seller ID: 1 (the ID of the seller user)
  - File: Any PDF file
- Click "Upload Document"

### 2. View Document
- Click "View Details" on the uploaded document
- You should see:
  - Document details (number, type, hash)
  - "Download File" button
  - "Available Actions" section (if role allows)
  - "Document Timeline" showing ISSUED ledger entry

### 3. Perform Actions (based on role)
- As Seller on a BOL: Click "SHIPPED"
- As Buyer on a BOL: Click "RECEIVED"
- As Bank on an INVOICE: Click "PAID"
- As Auditor on a PO: Click "VERIFY"

Each action creates an immutable ledger entry visible in the timeline.

## Troubleshooting

### Backend won't start
- Ensure Python 3.9+ is installed: `python --version`
- Check if port 8000 is available
- Verify .env file exists and has correct values

### Frontend won't start
- Ensure Node.js 16+ is installed: `node --version`
- Delete node_modules and run `npm install` again
- Check if port 3000 is available

### Database errors
- Delete the `test.db` file to reset the database
- Re-run the initialization command

### CORS errors
- Ensure backend is running on http://localhost:8000
- Ensure frontend is running on http://localhost:3000
- Check that CORS middleware is properly configured in backend/app/main.py

## File Locations

- Backend API Routes: `backend/app/api/routes/`
- Database Models: `backend/app/db/models.py`
- Frontend Components: `frontend/src/pages/` and `frontend/src/components/`
- Uploaded Files: `backend/files/`
- Database: `backend/test.db`

## API Endpoints

### Authentication
- `POST /auth/login` - Login user
- `POST /auth/signup` - Register user
- `POST /auth/refresh` - Refresh access token

### Documents
- `POST /api/documents/upload` - Upload new document
- `GET /api/documents/list` - List user's documents
- `GET /api/documents/document?id=<id>` - Get document details
- `POST /api/documents/action` - Perform action on document
- `GET /api/documents/file?file_url=<filename>` - Download file

## Next Steps

1. Explore the API documentation at http://localhost:8000/docs
2. Try uploading different document types (PO, BOL, LOC, INVOICE)
3. Test different roles and their permissions
4. Check the database by inspecting test.db with a SQLite viewer
