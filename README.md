# Trade Finance Blockchain Explorer

A modern web application for managing trade finance documents with blockchain-inspired immutable ledger tracking. Built with FastAPI + React.

## 🏗️ Architecture

- **Backend**: FastAPI (Python) with SQLModel ORM
- **Frontend**: React with TailwindCSS
- **Database**: SQLite (development) or PostgreSQL (production)
- **Authentication**: JWT tokens with refresh mechanism
- **Document Storage**: Local file system with SHA-256 hashing

## 🚀 Quick Start

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
DATABASE_URL=sqlite:///./test.db
JWT_SECRET_KEY=change-this-to-a-random-secret-key
EOF

# Initialize database
python -c "from app.db.session import engine; from app.db.models import SQLModel; SQLModel.metadata.create_all(engine)"

# Start server
python -m uvicorn app.main:app --reload
```

Backend runs on: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend runs on: `http://localhost:3000`

## 📋 Features

### Milestone 1: Authentication ✅
- User registration with role selection
- JWT login/logout
- Refresh token support
- Organizations with multiple users

### Milestone 2: Documents & Ledger ✅
- Document upload with SHA-256 hashing
- File storage and secure downloads
- Immutable ledger entries
- Role-based action validation
- Document timeline tracking

## 👥 Roles & Permissions

**Document Types**: PO (Purchase Order), BOL (Bill of Lading), LOC (Letter of Credit), INVOICE

**Role Actions**:
- **Buyer**: RECEIVED on BOL
- **Seller**: SHIPPED on BOL, ISSUE_BOL on PO, ISSUE_INVOICE
- **Auditor**: VERIFY on PO and LOC
- **Bank**: PAID on INVOICE, ISSUE_LOC on LOC

## 📁 Project Structure

```
Trade-Finance-Blockchain-Explorer/
├── backend/
│   ├── app/
│   │   ├── api/routes/         # API route handlers
│   │   │   ├── auth.py
│   │   │   └── documents.py
│   │   ├── db/
│   │   │   ├── models.py       # SQLModel definitions
│   │   │   └── session.py
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/           # Business logic
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   └── main.py
│   ├── files/                  # Uploaded documents
│   ├── requirements.txt
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── pages/              # React pages
│   │   ├── components/         # Reusable components
│   │   ├── services/           # API calls
│   │   ├── App.js
│   │   └── index.js
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   └── README.md
└── README.md
```

## 🔐 Security Features

- JWT authentication with expiration
- SHA-256 document hashing for integrity
- Role-based access control (RBAC)
- Immutable ledger for audit trails
- Secure file path validation
- Bearer token validation

## 📚 API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/signup` - User registration
- `POST /auth/refresh` - Refresh access token

### Documents
- `POST /api/documents/upload` - Upload document
- `GET /api/documents/file?file_url=...` - Download file
- `GET /api/documents/document?id=...` - Get document details
- `POST /api/documents/action` - Perform document action
- `GET /api/documents/list` - List user documents

## 🧪 Testing

### Create Test Users

```bash
# Seller
POST /auth/signup
{
  "name": "Alice Seller",
  "email": "seller@example.com",
  "password": "password123",
  "org": "Seller Corp",
  "role": "seller"
}

# Buyer
POST /auth/signup
{
  "name": "Bob Buyer",
  "email": "buyer@example.com",
  "password": "password123",
  "org": "Buyer Corp",
  "role": "buyer"
}

# Bank
POST /auth/signup
{
  "name": "Charlie Bank",
  "email": "bank@example.com",
  "password": "password123",
  "org": "Bank Corp",
  "role": "bank"
}
```

### Test Document Workflow

1. Login as seller
2. Upload a document (creates ISSUED ledger entry)
3. Seller performs SHIPPED action on BOL
4. Buyer performs RECEIVED action on BOL
5. Seller performs ISSUE_INVOICE action
6. Bank performs PAID action on INVOICE

## 🔗 Documentation

- [Backend Documentation](./backend/README.md)
- [Frontend Documentation](./frontend/README.md)
- [API Specification](http://localhost:8000/docs)

## 📝 License

See [LICENSE](./LICENSE) file

## 🤝 Contributing

Contributions are welcome! Please follow the existing code style and structure.