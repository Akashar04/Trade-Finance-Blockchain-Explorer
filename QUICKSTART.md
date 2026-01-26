# ⚡ Quick Start Guide - Trade Finance Blockchain Explorer

## 🚀 Start the System

### Prerequisites
- Python 3.9+
- Node.js 14+
- npm 6+

### Option 1: Automatic Start (Windows)

Create a file `start-all.bat` in the project root:

```batch
@echo off
start cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 3
start cmd /k "cd frontend && npm start"
echo Both servers are starting. Please wait 30 seconds for them to fully initialize.
echo Frontend will open automatically at http://localhost:3000
echo Backend API docs at http://localhost:8000/docs
pause
```

Then double-click `start-all.bat`.

### Option 2: Manual Start

**Terminal 1 - Backend**:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm install  # Only first time
npm start
```

The frontend will automatically open at `http://localhost:3000`.

---

## ✅ Verify Setup

### Backend Health Check
1. Go to `http://127.0.0.1:8000/docs`
2. Should see Swagger API documentation
3. Endpoints listed:
   - POST /auth/login
   - POST /auth/signup
   - GET /auth/user
   - POST /api/documents/upload
   - GET /api/documents/list
   - GET /api/documents/document
   - POST /api/documents/action
   - GET /api/documents/file

### Frontend Health Check
1. Go to `http://localhost:3000`
2. Should see login page
3. Verify all links work

---

## 🧪 Test the System (5 minutes)

### 1. Create Users

**Signup as Seller**:
1. Click "Sign up"
2. Fill:
   - Name: Alice Seller
   - Email: seller@example.com
   - Password: password123
   - Organization: Seller Corp
   - Role: Seller
3. Click Sign Up → Auto-login
4. You're now on `/documents` page

**Create Buyer** (in separate browser/incognito):
1. Repeat signup with:
   - Name: Bob Buyer
   - Email: buyer@example.com
   - Password: password123
   - Organization: Buyer Corp
   - Role: Buyer

### 2. Upload Document

1. As Seller, click "Upload Document"
2. Fill:
   - Document Number: `BOL-2024-001`
   - Seller ID: `1` (Alice's ID)
   - File: Any file
3. Click Upload
4. See document details page

### 3. Perform Action

1. Click "SHIPPED" button (seller action on BOL)
2. Success alert appears
3. Timeline shows 2 entries:
   - ISSUED (created on upload)
   - SHIPPED (just performed)

### 4. Check as Buyer

1. Open new browser/incognito
2. Login as buyer (bob@example.com)
3. Go to `/documents`
4. You should see the BOL document
5. Click to view details
6. See "RECEIVED" button (buyer action)
7. Click "RECEIVED"
8. Timeline shows 3 entries:
   - ISSUED
   - SHIPPED
   - RECEIVED

---

## 📁 Project Structure

```
Trade-Finance-Blockchain-Explorer/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── auth.py          # Login, signup, user endpoint
│   │   │   └── documents.py     # Document CRUD + actions
│   │   ├── db/
│   │   │   ├── models.py        # SQLModel definitions
│   │   │   └── session.py       # Database session
│   │   ├── schemas/
│   │   │   └── auth.py          # Request/response schemas
│   │   ├── services/
│   │   │   └── auth.py          # Auth logic
│   │   ├── core/
│   │   │   ├── config.py        # Settings
│   │   │   └── security.py      # JWT utils
│   │   └── main.py              # FastAPI app
│   ├── files/                   # Uploaded documents
│   ├── .env                     # Environment variables
│   ├── requirements.txt         # Python dependencies
│   └── README.md
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.js
│   │   │   ├── SignupPage.js
│   │   │   ├── DocumentsListPage.js
│   │   │   ├── UploadDocumentPage.js
│   │   │   └── DocumentDetailsPage.js
│   │   ├── components/
│   │   │   └── Navigation.js
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.js               # Main router
│   │   ├── index.js             # Entry point
│   │   └── index.css
│   ├── package.json
│   ├── tailwind.config.js
│   └── README.md
│
├── FRONTEND_TESTING.md          # Comprehensive test guide
├── FINAL_REPORT.md              # Project completion report
└── README.md
```

---

## 🔑 Key Features

### Authentication
- ✅ Email/password signup and login
- ✅ Role selection (buyer, seller, auditor, bank)
- ✅ JWT tokens with 15-minute expiration
- ✅ Refresh tokens stored in httpOnly cookies

### Documents
- ✅ Upload documents with metadata
- ✅ SHA-256 file hashing
- ✅ Secure file storage
- ✅ File download support

### Ledger
- ✅ Immutable action tracking
- ✅ Actor tracking (who performed action)
- ✅ Timestamp recording
- ✅ Timeline visualization

### Role-Based Access Control
- ✅ 4 roles: buyer, seller, auditor, bank
- ✅ Role-specific action buttons
- ✅ Permission validation on backend
- ✅ Unauthorized actions blocked

---

## 🐛 Troubleshooting

### Backend won't start
```bash
cd backend
# Check Python is installed
python --version

# Check dependencies installed
pip install -r requirements.txt

# Check port 8000 is free
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows
```

### Frontend won't start
```bash
cd frontend
# Clear node_modules
rm -rf node_modules
npm install

# Clear npm cache
npm cache clean --force
npm install

npm start
```

### CORS errors
- Ensure backend is on `http://127.0.0.1:8000`
- Ensure frontend is on `http://localhost:3000`
- Check backend CORS middleware includes `localhost:3000`

### Login doesn't work
- Check backend is running (`http://127.0.0.1:8000/docs`)
- Check credentials are correct
- Clear browser localStorage and retry

### Documents don't appear
- Ensure you're logged in
- Ensure user uploaded documents or is in same organization
- Check browser console for API errors
- Verify JWT token is valid

---

## 📊 API Quick Reference

### Authentication

**Login**:
```bash
POST http://127.0.0.1:8000/auth/login
Content-Type: application/json

{
  "email": "seller@example.com",
  "password": "password123"
}

Response: { "access_token": "...", "token_type": "bearer" }
```

**Get Current User**:
```bash
GET http://127.0.0.1:8000/auth/user
Authorization: Bearer <access_token>

Response: { "id": 1, "name": "Alice", "role": "seller", ... }
```

### Documents

**Upload**:
```bash
POST http://127.0.0.1:8000/api/documents/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Form Data:
- doc_number: BOL-2024-001
- seller_id: 1
- file: <binary>

Response: Document details
```

**List**:
```bash
GET http://127.0.0.1:8000/api/documents/list
Authorization: Bearer <access_token>

Response: [{ id, doc_number, doc_type, created_at, ... }, ...]
```

**Get Details**:
```bash
GET http://127.0.0.1:8000/api/documents/document?id=1
Authorization: Bearer <access_token>

Response: { id, doc_number, doc_type, ledger_entries: [...], ... }
```

**Perform Action**:
```bash
POST http://127.0.0.1:8000/api/documents/action
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "doc_id": 1,
  "action": "SHIPPED"
}

Response: Success message
```

---

## 🎯 Development Workflow

### Making Changes

**Backend**:
1. Edit files in `backend/app/`
2. Server auto-reloads (uvicorn reload mode)
3. Check `http://127.0.0.1:8000/docs` for changes

**Frontend**:
1. Edit files in `frontend/src/`
2. Page auto-reloads (react-scripts watch mode)
3. Changes appear instantly

### Testing in Browser DevTools

**Check JWT Token**:
```javascript
// In browser console
localStorage.getItem('access_token')
JSON.parse(localStorage.getItem('user_data'))
```

**Test API Endpoint**:
```javascript
fetch('http://127.0.0.1:8000/api/documents/list', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
})
.then(r => r.json())
.then(console.log)
```

---

## 📚 Documentation

- **[FRONTEND_TESTING.md](FRONTEND_TESTING.md)** - Comprehensive testing guide
- **[API_REFERENCE.md](API_REFERENCE.md)** - Detailed API documentation
- **[backend/README.md](backend/README.md)** - Backend setup and structure
- **[frontend/README.md](frontend/README.md)** - Frontend setup and features

---

## ✨ Next Steps

1. ✅ Start both servers
2. ✅ Create test users
3. ✅ Upload a document
4. ✅ Perform actions as different roles
5. ✅ Verify ledger timeline
6. 📖 See [FRONTEND_TESTING.md](FRONTEND_TESTING.md) for comprehensive testing
7. 🚀 Deploy to production (see documentation)

---

**Questions?** Check the README or FRONTEND_TESTING.md files.

**Ready to test?** Go to `http://localhost:3000` now! 🚀
