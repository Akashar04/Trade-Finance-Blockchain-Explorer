# Implementation Details - Milestone 2

## Backend Implementation

### 1. Database Models

#### Document Model
```python
class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doc_number: str = Field(index=True)
    file_url: str
    hash: str
    doc_type: str  # PO, BOL, LOC, INVOICE
    owner_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Key Points:**
- Indexed doc_number for fast searches
- Hash field stores SHA-256 of the file
- Foreign key to User for ownership tracking
- Immutable created_at timestamp

#### LedgerEntry Model
```python
class LedgerEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    doc_id: int = Field(foreign_key="document.id")
    actor_id: int = Field(foreign_key="user.id")
    action: str  # ISSUED, SHIPPED, RECEIVED, VERIFIED, PAID, ISSUE_LOC, ISSUE_INVOICE
    metadata: Optional[str] = Field(default=None)  # JSON stored as string
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

**Key Points:**
- Immutable record of all document actions
- actor_id tracks who performed the action
- metadata stores JSON (e.g., seller_id for ISSUED action)
- Ordered by created_at for timeline visualization

### 2. File Upload Implementation

**Endpoint:** `POST /api/documents/upload`

**Flow:**
1. Authenticate user via JWT bearer token
2. Read file content from multipart request
3. Compute SHA-256 hash using `hashlib.sha256()`
4. Generate unique filename using `uuid.uuid4()`
5. Save file to `backend/files/` directory
6. Create Document record in database
7. Create initial ISSUED LedgerEntry with seller_id in metadata

**Security:**
- JWT authentication required
- File path validation prevents directory traversal
- Unique filenames prevent collisions

### 3. File Fetch Implementation

**Endpoint:** `GET /api/documents/file?file_url=filename.pdf`

**Flow:**
1. Validate file_url parameter
2. Resolve full path and verify it's within FILES_DIR
3. Return file as StreamingResponse with PDF media type

**Security:**
- Path validation checks that resolved path is within FILES_DIR
- Prevents directory traversal attacks
- No authentication required (files are identified by UUID anyway)

### 4. Document Details API

**Endpoint:** `GET /api/documents/document?id=<doc_id>`

**Flow:**
1. Authenticate user
2. Fetch document by ID
3. Fetch all LedgerEntries for document, ordered by created_at
4. Return DocumentDetailResponse with ledger_entries

**Authorization:**
- User must be document owner or in same organization

### 5. Action API

**Endpoint:** `POST /api/documents/action`

**Request Body:**
```json
{
  "doc_id": 123,
  "action": "SHIPPED"
}
```

**Flow:**
1. Authenticate user
2. Fetch document
3. Validate action is allowed:
   - Check user role against ACCESS_MAPPING
   - Check document doc_type against allowed actions
4. Create LedgerEntry with action and current user as actor
5. Return ActionResponse with ledger_entry_id

**Access Mapping:**
```python
ACCESS_MAPPING = {
    "buyer": {
        "BOL": ["RECEIVED"],
    },
    "seller": {
        "BOL": ["SHIPPED"],
        "PO": ["ISSUE_BOL"],
        "BOL": ["ISSUE_INVOICE"],
    },
    "auditor": {
        "PO": ["VERIFY"],
        "LOC": ["VERIFY"],
    },
    "bank": {
        "INVOICE": ["PAID"],
        "LOC": ["ISSUE_LOC"],
    },
}
```

### 6. Security Features

**JWT Authentication:**
- All document routes (except file fetch) require Bearer token
- `get_current_user()` extracts and validates token
- Returns 401 if token missing, expired, or invalid

**CORS Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Frontend Implementation

### 1. Component Structure

**Protected Routes:**
- DocumentsListPage
- UploadDocumentPage
- DocumentDetailsPage

**Public Routes:**
- LoginPage
- SignupPage

**Protected Route Wrapper:**
```javascript
const ProtectedRoute = ({ element }) => {
  return token ? element : <Navigate to="/login" />;
};
```

### 2. API Service Layer

**axios Instance with Interceptor:**
```javascript
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**Benefits:**
- Automatic token injection into all requests
- Centralized API logic
- Easy error handling

### 3. File Upload

**Multipart Form Data:**
```javascript
const form = new FormData();
form.append('doc_number', formData.doc_number);
form.append('seller_id', formData.seller_id);
form.append('file', formData.file);

return axios.post(`${API_BASE_URL}/documents/upload`, form, {
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});
```

### 4. Document Details Page

**Role-Based Actions:**
```javascript
const getAvailableActions = () => {
  const roleActionsMapping = {
    buyer: { BOL: ['RECEIVED'] },
    seller: { BOL: ['SHIPPED'], PO: ['ISSUE_BOL'], INVOICE: ['ISSUE_INVOICE'] },
    auditor: { PO: ['VERIFY'], LOC: ['VERIFY'] },
    bank: { INVOICE: ['PAID'], LOC: ['ISSUE_LOC'] },
  };

  const roleActions = roleActionsMapping[userRole] || {};
  return roleActions[document.doc_type] || [];
};
```

**Timeline Visualization:**
```javascript
<div className="space-y-6">
  {ledgerEntries.map((entry, index) => (
    <div key={entry.id} className="flex">
      <div className="flex flex-col items-center mr-6">
        <div className="bg-blue-600 text-white rounded-full h-10 w-10 flex items-center justify-center font-bold">
          {index + 1}
        </div>
        {index < ledgerEntries.length - 1 && (
          <div className="w-1 h-12 bg-gray-300 mt-2"></div>
        )}
      </div>
      {/* Entry details */}
    </div>
  ))}
</div>
```

## Data Flow

### Document Upload Flow
```
User (Frontend)
    ↓
POST /api/documents/upload (with JWT)
    ↓
Backend validates JWT
    ↓
Compute SHA-256 hash
    ↓
Save file to /files/
    ↓
Create Document record
    ↓
Create ISSUED LedgerEntry
    ↓
Return DocumentResponse
    ↓
Frontend redirects to /documents
```

### Document Action Flow
```
User (Frontend) clicks action button
    ↓
POST /api/documents/action (with JWT)
    ↓
Backend validates JWT and action
    ↓
Check ACCESS_MAPPING (role + doc_type)
    ↓
Create LedgerEntry with action
    ↓
Return ActionResponse
    ↓
Frontend fetches updated document details
    ↓
Timeline refreshes with new entry
```

## Database Schema

```sql
-- User (from Milestone 1)
CREATE TABLE user (
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  role TEXT NOT NULL,
  organization_id INTEGER FOREIGN KEY,
  created_at TIMESTAMP
);

-- Document (NEW)
CREATE TABLE document (
  id INTEGER PRIMARY KEY,
  doc_number TEXT NOT NULL,
  file_url TEXT NOT NULL,
  hash TEXT NOT NULL,
  doc_type TEXT NOT NULL,
  owner_id INTEGER FOREIGN KEY,
  created_at TIMESTAMP
);

-- LedgerEntry (NEW)
CREATE TABLE ledger_entry (
  id INTEGER PRIMARY KEY,
  doc_id INTEGER FOREIGN KEY,
  actor_id INTEGER FOREIGN KEY,
  action TEXT NOT NULL,
  metadata TEXT,
  created_at TIMESTAMP
);
```

## Testing Guide

### Manual Testing

1. **Test Role Permissions:**
   - Create users with different roles
   - Try to perform actions that are not allowed
   - Verify 403 Forbidden response

2. **Test File Integrity:**
   - Upload document
   - Download file
   - Verify file hash matches SHA-256

3. **Test Ledger Immutability:**
   - Perform multiple actions
   - Verify ledger entries cannot be modified
   - Verify timestamps are in order

4. **Test File Security:**
   - Try to access files with invalid paths
   - Verify 403 Forbidden response

### API Testing with cURL

```bash
# Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "password": "password",
    "org": "TestOrg",
    "role": "seller"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password"
  }'

# Upload document
curl -X POST http://localhost:8000/api/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "doc_number=PO-001" \
  -F "seller_id=1" \
  -F "file=@test.pdf"

# Get document details
curl http://localhost:8000/api/documents/document?id=1 \
  -H "Authorization: Bearer <token>"

# Perform action
curl -X POST http://localhost:8000/api/documents/action \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"doc_id": 1, "action": "SHIPPED"}'
```

## Future Enhancements

1. PostgreSQL for production database
2. S3/Cloud storage for files instead of local filesystem
3. File encryption for sensitive documents
4. Document versioning
5. Advanced search and filtering
6. Real-time notifications
7. Document signing
8. Integration with blockchain
