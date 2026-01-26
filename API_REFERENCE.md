# API Reference - Complete Endpoint Documentation

## Base URLs
- **Backend API**: `http://localhost:8000`
- **Frontend**: `http://localhost:3000`

## Authentication Endpoints

### POST /auth/signup
Create a new user account

**Request:**
```json
{
  "name": "John Seller",
  "email": "john@example.com",
  "password": "securepassword123",
  "org": "Acme Corp",
  "role": "seller"
}
```

**Response (200):**
```json
{
  "message": "Signup successful"
}
```

**Roles**: `buyer`, `seller`, `auditor`, `bank`

---

### POST /auth/login
Authenticate user and get access token

**Request:**
```json
{
  "email": "john@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Note**: Refresh token is set as HTTP-only cookie

---

### POST /auth/refresh
Refresh the access token

**Headers:**
```
Cookie: refresh_token=<refresh_token>
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Document Endpoints

### POST /api/documents/upload
Upload a new document

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**Form Data:**
- `doc_number` (string, required) - Unique document number
- `seller_id` (integer, required) - ID of the seller (user)
- `file` (file, required) - PDF or document file

**Response (200):**
```json
{
  "id": 1,
  "doc_number": "PO-2024-001",
  "file_url": "550e8400-e29b-41d4-a716-446655440000.pdf",
  "hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
  "doc_type": "INVOICE",
  "owner_id": 1,
  "created_at": "2024-01-26T10:30:00"
}
```

**Example with cURL:**
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer eyJ..." \
  -F "doc_number=PO-2024-001" \
  -F "seller_id=1" \
  -F "file=@document.pdf"
```

---

### GET /api/documents/file
Download a document file

**Query Parameters:**
- `file_url` (string, required) - The file URL from document response

**Response (200):**
- Binary file data
- Content-Type: application/pdf
- Content-Disposition: attachment

**Example:**
```bash
curl "http://localhost:8000/api/documents/file?file_url=550e8400-e29b-41d4-a716-446655440000.pdf" \
  -o downloaded_file.pdf
```

---

### GET /api/documents/list
Get all documents for the logged-in user

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
[
  {
    "id": 1,
    "doc_number": "PO-2024-001",
    "file_url": "550e8400-e29b-41d4-a716-446655440000.pdf",
    "hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
    "doc_type": "INVOICE",
    "owner_id": 1,
    "created_at": "2024-01-26T10:30:00"
  },
  {
    "id": 2,
    "doc_number": "BOL-2024-002",
    "file_url": "660e8400-e29b-41d4-a716-446655440001.pdf",
    "hash": "b775b56a31533g0e528f5978gfed5fc9b15b2g4ggf2gb08f009f97g8b38bf4",
    "doc_type": "BOL",
    "owner_id": 1,
    "created_at": "2024-01-26T11:45:00"
  }
]
```

**Example with cURL:**
```bash
curl "http://localhost:8000/api/documents/list" \
  -H "Authorization: Bearer eyJ..."
```

---

### GET /api/documents/document
Get document details with ledger history

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `id` (integer, required) - Document ID

**Response (200):**
```json
{
  "id": 1,
  "doc_number": "PO-2024-001",
  "file_url": "550e8400-e29b-41d4-a716-446655440000.pdf",
  "hash": "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3",
  "doc_type": "INVOICE",
  "owner_id": 1,
  "created_at": "2024-01-26T10:30:00",
  "ledger_entries": [
    {
      "id": 1,
      "doc_id": 1,
      "actor_id": 1,
      "action": "ISSUED",
      "metadata": "{\"seller_id\": 1}",
      "created_at": "2024-01-26T10:30:00"
    },
    {
      "id": 2,
      "doc_id": 1,
      "actor_id": 2,
      "action": "RECEIVED",
      "metadata": null,
      "created_at": "2024-01-26T11:15:00"
    }
  ]
}
```

**Example with cURL:**
```bash
curl "http://localhost:8000/api/documents/document?id=1" \
  -H "Authorization: Bearer eyJ..."
```

---

### POST /api/documents/action
Perform an action on a document (creates ledger entry)

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request Body:**
```json
{
  "doc_id": 1,
  "action": "SHIPPED"
}
```

**Response (200):**
```json
{
  "message": "Action 'SHIPPED' performed successfully",
  "ledger_entry_id": 3
}
```

**Response (403) - Invalid Action:**
```json
{
  "detail": "Action 'SHIPPED' not allowed for role 'buyer' on document type 'INVOICE'"
}
```

**Valid Actions by Role:**

| Role | Doc Type | Actions |
|------|----------|---------|
| buyer | BOL | RECEIVED |
| seller | BOL | SHIPPED, ISSUE_INVOICE |
| seller | PO | ISSUE_BOL |
| auditor | PO, LOC | VERIFY |
| bank | INVOICE | PAID |
| bank | LOC | ISSUE_LOC |

**Example with cURL:**
```bash
curl -X POST http://localhost:8000/api/documents/action \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": 1,
    "action": "SHIPPED"
  }'
```

---

## Error Responses

### 400 - Bad Request
```json
{
  "detail": "All fields are required"
}
```

### 401 - Unauthorized
```json
{
  "detail": "Invalid token"
}
```

### 403 - Forbidden
```json
{
  "detail": "Action 'SHIPPED' not allowed for role 'buyer' on document type 'INVOICE'"
}
```

### 404 - Not Found
```json
{
  "detail": "Document not found"
}
```

### 422 - Unprocessable Entity
```json
{
  "detail": "Invalid request format"
}
```

### 500 - Internal Server Error
```json
{
  "detail": "Failed to process request"
}
```

---

## Complete Example Workflow

### Step 1: Sign up as Seller
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Seller",
    "email": "alice@example.com",
    "password": "password123",
    "org": "SellerCorp",
    "role": "seller"
  }'
```

### Step 2: Sign up as Buyer
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob Buyer",
    "email": "bob@example.com",
    "password": "password123",
    "org": "BuyerCorp",
    "role": "buyer"
  }'
```

### Step 3: Login as Seller
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "password123"
  }'
# Get: {"access_token": "TOKEN1", "token_type": "bearer"}
```

### Step 4: Upload Document (as Seller)
```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer TOKEN1" \
  -F "doc_number=BOL-2024-001" \
  -F "seller_id=1" \
  -F "file=@document.pdf"
# Get: {"id": 1, ...}
```

### Step 5: Seller performs SHIPPED action
```bash
curl -X POST http://localhost:8000/api/documents/action \
  -H "Authorization: Bearer TOKEN1" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": 1,
    "action": "SHIPPED"
  }'
# Creates ledger entry with action "SHIPPED"
```

### Step 6: Login as Buyer
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bob@example.com",
    "password": "password123"
  }'
# Get: {"access_token": "TOKEN2", "token_type": "bearer"}
```

### Step 7: Buyer performs RECEIVED action
```bash
curl -X POST http://localhost:8000/api/documents/action \
  -H "Authorization: Bearer TOKEN2" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": 1,
    "action": "RECEIVED"
  }'
# Creates ledger entry with action "RECEIVED"
```

### Step 8: View complete document with timeline
```bash
curl http://localhost:8000/api/documents/document?id=1 \
  -H "Authorization: Bearer TOKEN2"
# Shows document with 3 ledger entries:
# 1. ISSUED (from upload)
# 2. SHIPPED (from seller)
# 3. RECEIVED (from buyer)
```

---

## Response Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request (validation error) |
| 401 | Unauthorized (missing/invalid token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 422 | Unprocessable Entity (invalid data format) |
| 500 | Internal Server Error |

---

## Authentication

All endpoints except `/api/documents/file` require JWT authentication.

**Header Format:**
```
Authorization: Bearer <access_token>
```

**Token obtained from:**
- `/auth/login` - Login with email/password
- `/auth/signup` - Create new account (then login)
- `/auth/refresh` - Refresh expired token

**Token expiration:** 15 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in .env)

---

## Rate Limiting

Not currently implemented. Add for production if needed.

---

## API Documentation

Interactive documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

**Last Updated**: January 26, 2024
**API Version**: 1.0.0 (Milestone 2)
