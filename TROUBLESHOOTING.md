# Troubleshooting Guide

## Common Issues and Solutions

### Backend Issues

#### 1. "ModuleNotFoundError: No module named 'fastapi'"
**Problem**: Dependencies not installed
**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

#### 2. "DatabaseError: table Document already exists"
**Problem**: Database schema conflict
**Solution**:
```bash
# Delete the old database
rm backend/test.db

# Reinitialize
python -c "from app.db.session import engine; from app.db.models import SQLModel; SQLModel.metadata.create_all(engine)"
```

#### 3. "KeyError: 'DATABASE_URL' or 'JWT_SECRET_KEY'"
**Problem**: Missing .env file or environment variables
**Solution**:
```bash
cd backend
cat > .env << EOF
DATABASE_URL=sqlite:///./test.db
JWT_SECRET_KEY=your-secret-key-change-in-production
EOF
```

#### 4. "Address already in use" on port 8000
**Problem**: Another process using port 8000
**Solution**:
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or use different port
python -m uvicorn app.main:app --reload --port 8001
```

#### 5. "CORS error when calling API from frontend"
**Problem**: CORS middleware not properly configured
**Solution**:
Check `backend/app/main.py` has:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 6. File upload returns 422 (Unprocessable Entity)
**Problem**: Form field names don't match API expectations
**Solution**: Ensure form has exact fields:
- `doc_number` (string)
- `seller_id` (integer)
- `file` (file)

#### 7. "Invalid token" error on API calls
**Problem**: Token expired or JWT_SECRET_KEY mismatch
**Solution**:
- Get a fresh token by logging in again
- Ensure JWT_SECRET_KEY in .env is the same
- Check token hasn't expired (15 minutes default)

### Frontend Issues

#### 1. "npm: command not found"
**Problem**: Node.js/npm not installed
**Solution**:
```bash
# Install Node.js from https://nodejs.org/
node --version  # Should be 16+
npm --version   # Should be 7+
```

#### 2. "Cannot find module 'react'"
**Problem**: Dependencies not installed
**Solution**:
```bash
cd frontend
rm -rf node_modules
npm install
```

#### 3. "Module not found: Can't resolve './services/api'"
**Problem**: File not created in correct location
**Solution**: Ensure `frontend/src/services/api.js` exists
```bash
# Verify file exists
ls -la frontend/src/services/api.js
```

#### 4. "Cannot GET /documents" in browser
**Problem**: React Router or frontend not running
**Solution**:
```bash
# Make sure you're on http://localhost:3000
# And frontend is running in terminal:
npm start
```

#### 5. "API calls return 401 Unauthorized"
**Problem**: Token not sent or expired
**Solution**:
- Make sure you're logged in
- Token stored in `localStorage.access_token`
- Check browser DevTools → Application → LocalStorage
- Try logging in again

#### 6. "Form submission does nothing"
**Problem**: API endpoint not responding
**Solution**:
- Check backend is running on :8000
- Check API endpoint in `frontend/src/services/api.js`
- Open browser DevTools → Network tab
- See exact error response

#### 7. "Cannot download file"
**Problem**: File not saved on backend
**Solution**:
- Check `backend/files/` directory exists
- Verify file was uploaded successfully
- Check file_url in document response

### Authentication Issues

#### 1. "Invalid credentials" on login
**Problem**: Wrong email or password
**Solution**:
- Double-check email and password
- Try signing up again
- Check database has user (if using SQLite GUI)

#### 2. "User already exists" on signup
**Problem**: Email already registered
**Solution**:
- Use different email
- Or reset database (delete test.db)

#### 3. "Missing or invalid authorization header"
**Problem**: No token sent to protected endpoint
**Solution**: 
- Ensure logged in
- Check API request includes: `Authorization: Bearer <token>`
- Check token in localStorage

#### 4. "Refresh token expired"
**Problem**: Refresh token has expired
**Solution**:
- Login again
- Default refresh token expires after 7 days
- Can adjust `REFRESH_TOKEN_EXPIRE_DAYS` in .env

### Database Issues

#### 1. "sqlite3.OperationalError: database is locked"
**Problem**: Another process accessing database
**Solution**:
```bash
# Close other database connections
# Restart backend server
python -m uvicorn app.main:app --reload
```

#### 2. "Foreign key constraint failed"
**Problem**: Referenced user/document doesn't exist
**Solution**:
- Make sure seller_id exists
- Check user was created first
- Verify IDs in form data

#### 3. "No data returned" from queries
**Problem**: Database empty or filters too strict
**Solution**:
- Create test data via signup/upload
- Check database directly with SQLite viewer
- Verify user/document IDs

### File Upload Issues

#### 1. "File not found" when downloading
**Problem**: File deleted or invalid file_url
**Solution**:
- Check `backend/files/` directory
- Verify file_url value in database
- Try uploading file again

#### 2. "Failed to save file"
**Problem**: Permission denied or directory doesn't exist
**Solution**:
```bash
# Create files directory
mkdir -p backend/files
chmod 755 backend/files
```

#### 3. "SHA-256 hash mismatch"
**Problem**: File corrupted or modified
**Solution**:
- Delete and re-upload file
- Check network connection stability
- Verify file size reasonable

### CORS Issues

#### 1. "No 'Access-Control-Allow-Origin' header"
**Problem**: CORS not configured in backend
**Solution**: Add CORS middleware to `backend/app/main.py`

#### 2. "CORS preflight request failed"
**Problem**: DELETE, PUT, or other methods not allowed
**Solution**:
Update CORS to allow all methods:
```python
allow_methods=["*"]
```

#### 3. "Credentials not sent with request"
**Problem**: `allow_credentials=False` in CORS
**Solution**:
```python
allow_credentials=True
```

## Debugging Steps

### 1. Check Logs
**Backend**:
```bash
# Look at terminal where backend is running
# Errors will be printed there
```

**Frontend**:
```bash
# Open browser DevTools (F12)
# Check Console tab for errors
```

### 2. Check Network Requests
```bash
# Browser DevTools → Network tab
# See all API calls
# Check response status and body
```

### 3. Check Database
```bash
# Use SQLite GUI viewer
# Open backend/test.db
# Check documents and ledger_entries tables
```

### 4. Check Environment Variables
```bash
# Backend
cat backend/.env

# Frontend (if using)
cat frontend/.env
```

### 5. Check Ports
```bash
# macOS/Linux
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Windows
netstat -ano | findstr :8000
netstat -ano | findstr :3000
```

## Performance Troubleshooting

### 1. API calls are slow
- Check database query performance
- Verify backend isn't CPU-bound
- Check network latency
- May need to add database indexes

### 2. File uploads are slow
- Check file size
- Verify network speed
- Large files may need chunking
- Consider compression

### 3. Frontend is sluggish
- Check React DevTools for re-renders
- Verify TailwindCSS build is optimized
- Check for console errors
- Profile with Chrome DevTools

## Testing Checklist

- [ ] Backend starts on :8000
- [ ] Frontend starts on :3000
- [ ] Can login with existing account
- [ ] Can sign up with new account
- [ ] Can upload document
- [ ] Can see document in list
- [ ] Can view document details
- [ ] Can see ledger timeline
- [ ] Can perform allowed actions
- [ ] Cannot perform disallowed actions
- [ ] Can download file
- [ ] File hash matches
- [ ] Logout works
- [ ] Protected routes redirect to login

## Getting Help

1. **Check logs**: Look at terminal output for exact error
2. **Check documentation**: See SETUP_GUIDE.md and IMPLEMENTATION_DETAILS.md
3. **Check API docs**: Visit http://localhost:8000/docs
4. **Check browser console**: F12 → Console tab
5. **Try resetting**: Delete database and node_modules, reinstall

## Emergency Fixes

### Reset Everything
```bash
# Backend
cd backend
rm test.db
rm -rf __pycache__ app/__pycache__ app/**/__pycache__
python -c "from app.db.session import engine; from app.db.models import SQLModel; SQLModel.metadata.create_all(engine)"

# Frontend
cd ../frontend
rm -rf node_modules
npm install
```

### Kill and Restart Services
```bash
# Kill all Python/Node processes
killall python
killall node

# Restart backend
cd backend
python -m uvicorn app.main:app --reload

# Restart frontend (in new terminal)
cd frontend
npm start
```

---

**Still having issues?** 
- Review the error message carefully
- Check exact file paths and names
- Verify all prerequisites are installed
- See if similar issue mentioned above
