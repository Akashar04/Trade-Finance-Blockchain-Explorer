# 📊 Trade Finance Blockchain Explorer - API Status & Reference

## ✅ System Status

| Component | URL | Status | Port |
|-----------|-----|--------|------|
| Backend | http://127.0.0.1:8000 | ✅ Running | 8000 |
| Frontend | http://localhost:3000 | ✅ Running | 3000 |
| API Docs | http://127.0.0.1:8000/docs | ✅ Available | 8000 |
| ReDoc | http://127.0.0.1:8000/redoc | ✅ Available | 8000 |

---

## 🔐 Authentication Endpoints

### POST /auth/login
**Description**: Authenticate user with email and password

**Request**:
```bash
POST http://127.0.0.1:8000/auth/login
Content-Type: application/json

{
  "email": "seller@example.com",
  "password": "password123"
}
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response (401 Unauthorized)**:
```json
{
  "detail": "Invalid credentials"
}
```

**Status**: ✅ **Working**

---

### POST /auth/signup
**Description**: Register new user with role

**Request**:
```bash
POST http://127.0.0.1:8000/auth/signup
Content-Type: application/json

{
  "name": "Alice Seller",
  "email": "seller@example.com",
  "password": "password123",
  "org": "Seller Corp",
  "role": "seller"
}
```

**Response (200 OK)**:
```json
{
  "message": "Signup successful"
}
```

**Response (400 Bad Request)**:
```json
{
  "detail": "User already exists"
}
```

**Valid Roles**:
- `buyer`
- `seller`
- `auditor`
- `bank`

**Status**: ✅ **Working**

---

### GET /auth/user
**Description**: Get current authenticated user data

**Request**:
```bash
GET http://127.0.0.1:8000/auth/user
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "name": "Alice Seller",
  "email": "seller@example.com",
  "role": "seller",
  "organization_id": 1
}
```

**Response (401 Unauthorized)**:
```json
{
  "detail": "Missing or invalid authorization header"
}
```

**Status**: ✅ **Working** (NEW - Added for frontend)

---

### POST /auth/refresh
**Description**: Refresh expired access token

**Request**:
```bash
POST http://127.0.0.1:8000/auth/refresh
Cookie: refresh_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK)**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Response (401 Unauthorized)**:
```json
{
  "detail": "Refresh token expired"
}
```

**Status**: ✅ **Working**

---

## 📄 Document Endpoints

### POST /api/documents/upload
**Description**: Upload a new document with file

**Request**:
```bash
POST http://127.0.0.1:8000/api/documents/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Form Data:
- doc_number: "BOL-2024-001"
- seller_id: 1
- file: <binary file>
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "doc_number": "BOL-2024-001",
  "file_url": "files/550e8400-e29b-41d4-a716-446655440000.pdf",
  "hash": "d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2...",
  "doc_type": "BOL",
  "owner_id": 1,
  "created_at": "2026-01-26T10:30:00"
}
```

**Response (401 Unauthorized)**:
```json
{
  "detail": "Invalid token"
}
```

**Response (400 Bad Request)**:
```json
{
  "detail": "All fields are required"
}
```

**Doc Type Detection**:
- `"PO-..."` → `doc_type = "PO"`
- `"BOL-..."` → `doc_type = "BOL"`
- `"LOC-..."` → `doc_type = "LOC"`
- `"INV-..."` → `doc_type = "INVOICE"`

**Status**: ✅ **Working**

---

### GET /api/documents/list
**Description**: Get list of all documents belonging to current user

**Request**:
```bash
GET http://127.0.0.1:8000/api/documents/list
Authorization: Bearer <access_token>
```

**Response (200 OK)**:
```json
[
  {
    "id": 1,
    "doc_number": "BOL-2024-001",
    "doc_type": "BOL",
    "hash": "d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2...",
    "created_at": "2026-01-26T10:30:00"
  },
  {
    "id": 2,
    "doc_number": "PO-2024-001",
    "doc_type": "PO",
    "hash": "a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1a1...",
    "created_at": "2026-01-26T11:00:00"
  }
]
```

**Response (401 Unauthorized)**:
```json
{
  "detail": "Invalid token"
}
```

**Status**: ✅ **Working**

---

### GET /api/documents/document
**Description**: Get full document details with ledger entries

**Request**:
```bash
GET http://127.0.0.1:8000/api/documents/document?id=1
Authorization: Bearer <access_token>
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "doc_number": "BOL-2024-001",
  "file_url": "files/550e8400-e29b-41d4-a716-446655440000.pdf",
  "hash": "d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2d2...",
  "doc_type": "BOL",
  "owner_id": 1,
  "created_at": "2026-01-26T10:30:00",
  "ledger_entries": [
    {
      "id": 1,
      "action": "ISSUED",
      "actor_id": 1,
      "created_at": "2026-01-26T10:30:00",
      "entry_metadata": null
    },
    {
      "id": 2,
      "action": "SHIPPED",
      "actor_id": 1,
      "created_at": "2026-01-26T10:35:00",
      "entry_metadata": null
    }
  ]
}
```

**Response (401 Unauthorized)**:
```json
{
  "detail": "Invalid token"
}
```

**Response (404 Not Found)**:
```json
{
  "detail": "Document not found"
}
```

**Status**: ✅ **Working**

---

### POST /api/documents/action
**Description**: Perform an action on a document

**Request**:
```bash
POST http://127.0.0.1:8000/api/documents/action
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "doc_id": 1,
  "action": "SHIPPED"
}
```

**Response (200 OK)**:
```json
{
  "message": "Action performed successfully"
}
```

**Response (401 Unauthorized)**:
```json
{
  "detail": "Invalid token"
}
```

**Response (403 Forbidden)**:
```json
{
  "detail": "Not authorized to perform this action"
}
```

**Response (404 Not Found)**:
```json
{
  "detail": "Document not found"
}
```

**Valid Actions by Role**:

| Role | Document Type | Actions |
|------|---|---|
| buyer | BOL | RECEIVED |
| seller | BOL | SHIPPED, ISSUE_INVOICE |
| seller | PO | ISSUE_BOL |
| auditor | PO | VERIFY |
| auditor | LOC | VERIFY |
| bank | LOC | ISSUE_LOC |
| bank | INVOICE | PAID |

**Status**: ✅ **Working**

---

### GET /api/documents/file
**Description**: Download a document file

**Request**:
```bash
GET http://127.0.0.1:8000/api/documents/file?file_url=files/550e8400-e29b-41d4-a716-446655440000.pdf
Authorization: Bearer <access_token>
```

**Response (200 OK)**:
```
<binary file content>
```

**Response (401 Unauthorized)**:
```json
{
  "detail": "Invalid token"
}
```

**Response (404 Not Found)**:
```json
{
  "detail": "File not found"
}
```

**Status**: ✅ **Working**

---

## 🔍 Endpoint Summary

### Total Endpoints: 7

| Method | Endpoint | Auth | Status | Used By |
|--------|----------|------|--------|---------|
| POST | /auth/login | ❌ | ✅ | Login Page |
| POST | /auth/signup | ❌ | ✅ | Signup Page |
| GET | /auth/user | ✅ | ✅ | Login/Signup (NEW) |
| POST | /auth/refresh | ✅ | ✅ | Auto-refresh |
| POST | /api/documents/upload | ✅ | ✅ | Upload Page |
| GET | /api/documents/list | ✅ | ✅ | Documents List |
| GET | /api/documents/document | ✅ | ✅ | Document Details |
| POST | /api/documents/action | ✅ | ✅ | Action Buttons |
| GET | /api/documents/file | ✅ | ✅ | Download Button |

---

## 🧪 Test Curl Commands

### Test Login
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "seller@example.com",
    "password": "password123"
  }'
```

### Test Get User
```bash
curl -X GET "http://127.0.0.1:8000/auth/user" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test List Documents
```bash
curl -X GET "http://127.0.0.1:8000/api/documents/list" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test Get Document Details
```bash
curl -X GET "http://127.0.0.1:8000/api/documents/document?id=1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Test Perform Action
```bash
curl -X POST "http://127.0.0.1:8000/api/documents/action" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": 1,
    "action": "SHIPPED"
  }'
```

### Test Upload Document
```bash
curl -X POST "http://127.0.0.1:8000/api/documents/upload" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "doc_number=BOL-2024-001" \
  -F "seller_id=1" \
  -F "file=@/path/to/file.pdf"
```

---

## 📊 Error Codes Reference

| Code | Meaning | Common Causes |
|------|---------|---------------|
| 200 | OK | Successful request |
| 400 | Bad Request | Invalid input, missing fields |
| 401 | Unauthorized | Invalid/missing JWT token |
| 403 | Forbidden | User not authorized for action |
| 404 | Not Found | Resource doesn't exist |
| 422 | Validation Error | Invalid data format |
| 500 | Internal Server Error | Backend error |

---

## 🔐 JWT Token Format

**Token Structure**:
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNjM2NzUwMzAwfQ.abc123...
```

**Decoded Payload**:
```json
{
  "sub": "1",
  "exp": 1636750300
}
```

**Token Expiration**: 15 minutes (900 seconds)

**Refresh Token**: Stored in httpOnly cookie, expires in 7 days

---

## 📱 Frontend API Calls

### In src/services/api.js

**Auth API**:
```javascript
authAPI.login(email, password)        // POST /auth/login
authAPI.signup(data)                  // POST /auth/signup
authAPI.getUser()                     // GET /auth/user (NEW)
```

**Documents API**:
```javascript
documentsAPI.uploadDocument(formData)     // POST /api/documents/upload
documentsAPI.listDocuments()              // GET /api/documents/list
documentsAPI.getDocumentDetails(id)       // GET /api/documents/document?id=
documentsAPI.performAction(data)          // POST /api/documents/action
documentsAPI.downloadFile(fileUrl)        // GET /api/documents/file?file_url=
```

---

## ✅ Implementation Checklist

- [x] All endpoints implemented
- [x] All endpoints tested
- [x] CORS configured
- [x] JWT validation working
- [x] Role-based permissions enforced
- [x] Error handling implemented
- [x] File upload working
- [x] File download working
- [x] Ledger entries created
- [x] Frontend integration complete
- [x] Documentation complete

---

## 🚀 Deployment Checklist

- [x] All endpoints working locally
- [x] Database migrations applied
- [x] Environment variables configured
- [x] CORS properly configured
- [x] Error handling comprehensive
- [ ] Rate limiting configured (optional)
- [ ] API monitoring setup (optional)
- [ ] Logging configured (optional)
- [ ] Database backups configured (for production)
- [ ] SSL/HTTPS enabled (for production)

---

## 📞 API Support

**API Documentation**: `http://127.0.0.1:8000/docs`  
**Interactive Testing**: Available at the URL above (Swagger UI)

**Rate Limiting**: None (implement in production)  
**Authentication**: JWT Bearer token  
**CORS**: Configured for localhost:3000

---

**Status**: ✅ **All Endpoints Working**  
**Last Updated**: January 26, 2026  
**Version**: 1.0.0
