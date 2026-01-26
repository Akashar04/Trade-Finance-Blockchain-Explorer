# Trade Finance Blockchain Explorer - Backend

FastAPI backend for Trade Finance Blockchain Explorer with document management, ledger tracking, and JWT authentication.

## Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL or SQLite

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the backend root:
```
DATABASE_URL=sqlite:///./test.db
JWT_SECRET_KEY=your-secret-key-here-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

3. Initialize the database:
```bash
python -c "from app.db.session import engine; from app.db.models import SQLModel; SQLModel.metadata.create_all(engine)"
```

4. Run the server:
```bash
python -m uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Documentation

Interactive API docs available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Features

### Authentication
- User signup/login with JWT tokens
- Refresh token support
- Role-based access control (buyer, seller, auditor, bank)

### Documents
- Upload documents with SHA-256 hashing
- File storage in `/files` directory
- Document metadata tracking
- Download files via secure URLs

### Ledger System
- Track document actions and state changes
- Immutable ledger entries with timestamps
- Actor tracking for audit trails
- Role-based action validation

## Libraries & Documentation

- [JWT](https://jwt.io/)
- [Pydantic](https://docs.pydantic.dev/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [FastAPI](https://fastapi.tiangolo.com/)