# Trade Finance Blockchain Explorer - Frontend Testing Guide

## 🚀 System Status

**Backend Server**: ✅ Running on `http://127.0.0.1:8000`
**Frontend Server**: ✅ Running on `http://localhost:3000`
**Database**: ✅ SQLite initialized

---

## 📋 Testing Checklist

### Phase 1: Authentication

#### Test 1.1: User Signup
1. Go to `http://localhost:3000`
2. Click "Sign up" link on the login page
3. Fill in the signup form:
   - **Name**: Alice Seller
   - **Email**: seller@example.com
   - **Password**: password123
   - **Organization**: Seller Corp
   - **Role**: Seller
4. Click "Sign Up" button
5. **Expected Result**: Auto-login and redirect to `/documents` page

**Test Data**:
```json
{
  "name": "Alice Seller",
  "email": "seller@example.com",
  "password": "password123",
  "org": "Seller Corp",
  "role": "seller"
}
```

#### Test 1.2: User Login
1. After signup, you'll be redirected to documents page
2. Click "Logout" button in the navigation
3. You'll be redirected to `/login`
4. Login with:
   - **Email**: seller@example.com
   - **Password**: password123
5. **Expected Result**: Redirected to `/documents` page, user_data stored in localStorage

**Verification**:
- Open Browser DevTools (F12)
- Go to Application > Local Storage
- Verify `access_token` and `user_data` are stored
- Check `user_data` contains: `{ id, name, email, role, organization_id }`

---

### Phase 2: Document Management

#### Test 2.1: Upload Document
1. From `/documents` page, click "Upload Document" button
2. Fill the upload form:
   - **Document Number**: PO-2024-001
   - **Seller ID**: 1 (or the user ID of a seller from signup)
   - **File**: Choose any file (PDF, DOC, or text)
3. Click "Upload Document" button
4. **Expected Result**: Success message, redirect to document details page

**Expected Document Type Auto-Detection**:
- Document number starting with "PO-" → doc_type = "PO"
- Document number starting with "BOL-" → doc_type = "BOL"
- Document number starting with "LOC-" → doc_type = "LOC"
- Document number starting with "INV-" → doc_type = "INVOICE"

#### Test 2.2: View Documents List
1. Go to `/documents`
2. **Expected Display**:
   - Table with columns: Doc Number, Type, Created, Hash (first 16 chars), Actions
   - Document uploaded in Test 2.1 appears in the list
   - "Upload Document" button is visible
3. Click "View Details" on any document
4. **Expected Result**: Navigate to `/documents/:id` page

#### Test 2.3: View Document Details
1. From documents list, click "View Details" on the document
2. **Expected Display**:
   - Document number (e.g., "PO-2024-001")
   - Document Type badge (e.g., "PO")
   - Created date/time
   - Full SHA-256 hash in monospace font
   - "Download File" button
   - "Available Actions" section (role-specific)
   - Document Timeline section

#### Test 2.4: Download File
1. From document details page, click "Download File" button
2. **Expected Result**: File is downloaded to your Downloads folder
3. **Verification**: File content matches the uploaded file

---

### Phase 3: Document Actions & Ledger Timeline

#### Test 3.1: Perform Document Action (Seller)
**Setup**: Logged in as seller, viewing a BOL document

1. From document details, click action button (e.g., "SHIPPED")
2. **Expected Result**:
   - Success alert message
   - Page refreshes automatically
   - New entry appears in "Document Timeline" section
   - Timeline shows: Step number, Action name, Timestamp, Actor ID

#### Test 3.2: View Ledger Timeline
1. After performing actions, verify timeline displays:
   - **Initial Entry**: Action "ISSUED" (created when document was uploaded)
   - **Recent Entry**: Action "SHIPPED" (created after performing action)
   - Entries numbered sequentially (1, 2, 3, ...)
   - Vertical line connecting entries
   - Timestamps in correct order (oldest to newest)

#### Test 3.3: Multiple Users Workflow
**Setup**: Create multiple test users with different roles

1. **Create Seller** (if not done):
   ```json
   {
     "name": "Alice Seller",
     "email": "seller@example.com",
     "password": "password123",
     "org": "Seller Corp",
     "role": "seller"
   }
   ```

2. **Create Buyer**:
   ```json
   {
     "name": "Bob Buyer",
     "email": "buyer@example.com",
     "password": "password123",
     "org": "Buyer Corp",
     "role": "buyer"
   }
   ```

3. **Create Bank**:
   ```json
   {
     "name": "Charlie Bank",
     "email": "bank@example.com",
     "password": "password123",
     "org": "Bank Corp",
     "role": "bank"
   }
   ```

4. **Create Auditor**:
   ```json
   {
     "name": "Diana Auditor",
     "email": "auditor@example.com",
     "password": "password123",
     "org": "Audit Firm",
     "role": "auditor"
   }
   ```

---

### Phase 4: Role-Based Actions

#### Test 4.1: Seller Actions

**As Seller, upload a BOL document**:
1. Login as seller
2. Upload document: "BOL-2024-001"
3. Go to document details
4. **Expected Available Actions**: SHIPPED, ISSUE_INVOICE
5. Click "SHIPPED" action
6. **Expected Result**: New ledger entry with action "SHIPPED"

**As Seller, upload a PO document**:
1. Upload document: "PO-2024-002"
2. **Expected Available Actions**: ISSUE_BOL, VERIFY (if auditor can verify PO)

#### Test 4.2: Buyer Actions

**As Buyer, view BOL document**:
1. Login as buyer
2. Go to `/documents`
3. Should see documents uploaded by others
4. Click on a BOL document
5. **Expected Available Action**: RECEIVED (only if logged in as buyer on BOL doc)
6. Click "RECEIVED" button
7. **Expected Result**: Ledger entry created with action "RECEIVED"

#### Test 4.3: Auditor Actions

**As Auditor, verify PO**:
1. Login as auditor
2. View a PO document
3. **Expected Available Action**: VERIFY
4. Click "VERIFY" button
5. **Expected Result**: Ledger entry created with action "VERIFY"

**As Auditor, verify LOC**:
1. View a LOC document
2. **Expected Available Action**: VERIFY
3. Perform action

#### Test 4.4: Bank Actions

**As Bank, issue LOC**:
1. Login as bank
2. View a LOC document
3. **Expected Available Action**: ISSUE_LOC
4. Click action button
5. **Expected Result**: Ledger entry created

**As Bank, mark INVOICE as PAID**:
1. View an INVOICE document
2. **Expected Available Action**: PAID
3. Click action button
4. **Expected Result**: Ledger entry created

---

### Phase 5: Permission Testing

#### Test 5.1: Unauthorized Actions

**Test**: Seller tries to perform buyer-only action

1. Login as seller
2. Upload/view a BOL document
3. **Expected Available Actions**: SHIPPED, ISSUE_INVOICE (NOT RECEIVED)
4. Verify "RECEIVED" button doesn't appear

**Test**: Buyer tries to perform seller-only action

1. Login as buyer
2. View a BOL document uploaded by seller
3. **Expected Available Action**: RECEIVED
4. Verify "SHIPPED" and "ISSUE_INVOICE" buttons don't appear

#### Test 5.2: Unauthenticated Access

1. Open DevTools and clear localStorage
2. Manually navigate to `http://localhost:3000/documents`
3. **Expected Result**: Redirect to `/login` page
4. Same for `/upload`, `/documents/:id`, etc.

#### Test 5.3: Invalid Token

1. Login normally
2. Open DevTools > Application > Local Storage
3. Modify `access_token` to an invalid value (e.g., "invalid_token_123")
4. Try to access `/documents` or perform any action
5. **Expected Result**: 401 error, redirect to login

---

### Phase 6: Error Handling

#### Test 6.1: Invalid Login

1. Go to `/login`
2. Enter wrong email/password
3. Click "Login"
4. **Expected Result**: Error message displays: "Invalid credentials"

#### Test 6.2: Duplicate Email Signup

1. Sign up with email: `test@example.com`
2. Try to sign up again with same email
3. **Expected Result**: Error message: "User already exists"

#### Test 6.3: Network Error Handling

1. Login and go to `/documents`
2. Open DevTools > Network > throttle to "Offline"
3. Try to upload document or perform action
4. **Expected Result**: Error message displayed to user
5. Re-enable network and retry

#### Test 6.4: File Upload Errors

1. Try to upload without selecting a file
2. **Expected Result**: "All fields are required" error

2. Try to upload with empty doc_number
3. **Expected Result**: "All fields are required" error

---

### Phase 7: UI/UX Verification

#### Test 7.1: Navigation

1. Verify Navigation bar appears on all pages (except login/signup)
2. Navigation contains:
   - Brand name: "Trade Finance Explorer"
   - Links: Documents, Upload
   - Logout button
3. Click each navigation item
4. Verify routing works correctly

#### Test 7.2: Responsive Design

1. Open page on different screen sizes
2. Verify layout is responsive:
   - Mobile (320px): Single column, stacked elements
   - Tablet (768px): Two columns where appropriate
   - Desktop (1024px+): Full layout with sidebar space

#### Test 7.3: Loading States

1. Upload a document
2. While uploading, button shows "Uploading..."
3. While fetching data, page shows "Loading documents..."
4. **Verification**: Loading states provide user feedback

#### Test 7.4: Error Display

1. Trigger various errors (wrong password, network error, etc.)
2. Verify error messages:
   - Display with red background
   - Clear and helpful
   - Dismiss properly

---

## 🧪 Complete Workflow Test

### Scenario: Purchase Order to Invoice Payment

**Users Involved**:
- Alice (Seller)
- Bob (Buyer)
- Diana (Auditor)
- Charlie (Bank)

**Steps**:

1. **Alice (Seller) uploads PO**:
   ```
   - Document Number: PO-2024-100
   - Seller ID: <Alice's ID>
   - Creates initial ISSUED ledger entry
   ```

2. **Diana (Auditor) verifies PO**:
   ```
   - Login as Diana
   - View PO-2024-100
   - Click VERIFY
   - Ledger: [ISSUED, VERIFY]
   ```

3. **Alice (Seller) issues BOL**:
   ```
   - Login as Alice
   - View PO-2024-100
   - Click ISSUE_BOL
   - Creates BOL-2024-100
   - Ledger: [ISSUED, VERIFY, ISSUE_BOL]
   ```

4. **Alice (Seller) ships**:
   ```
   - View BOL-2024-100
   - Click SHIPPED
   - Ledger: [ISSUED, SHIPPED]
   ```

5. **Bob (Buyer) receives**:
   ```
   - Login as Bob
   - View BOL-2024-100
   - Click RECEIVED
   - Ledger: [ISSUED, SHIPPED, RECEIVED]
   ```

6. **Alice (Seller) issues invoice**:
   ```
   - View BOL-2024-100
   - Click ISSUE_INVOICE
   - Creates INV-2024-100
   - Ledger: [ISSUED, ISSUE_INVOICE]
   ```

7. **Charlie (Bank) marks paid**:
   ```
   - Login as Charlie
   - View INV-2024-100
   - Click PAID
   - Ledger: [ISSUED, ISSUE_INVOICE, PAID]
   ```

**Verification**:
- All ledger entries visible in correct order
- Timeline shows all actions with timestamps
- No unauthorized actions allowed
- All documents appear in respective user's document list

---

## 📊 Test Results Template

### Tester Name: ___________
### Test Date: ___________
### Browser: ___________
### OS: ___________

| Test ID | Test Name | Expected | Actual | Status | Notes |
|---------|-----------|----------|--------|--------|-------|
| 1.1 | User Signup | Redirect to /documents | | ✅/❌ | |
| 1.2 | User Login | Redirect to /documents | | ✅/❌ | |
| 2.1 | Upload Document | Redirect to details | | ✅/❌ | |
| 2.2 | View Documents List | Table displays | | ✅/❌ | |
| 2.3 | View Document Details | Full details display | | ✅/❌ | |
| 2.4 | Download File | File downloads | | ✅/❌ | |
| 3.1 | Perform Action | Ledger entry created | | ✅/❌ | |
| 3.2 | View Timeline | Timeline displays | | ✅/❌ | |
| 4.1 | Seller Actions | Correct actions show | | ✅/❌ | |
| 4.2 | Buyer Actions | Correct actions show | | ✅/❌ | |
| 4.3 | Auditor Actions | Correct actions show | | ✅/❌ | |
| 4.4 | Bank Actions | Correct actions show | | ✅/❌ | |
| 5.1 | Unauthorized Actions | Actions hidden | | ✅/❌ | |
| 5.2 | Unauthenticated Access | Redirect to login | | ✅/❌ | |
| 5.3 | Invalid Token | Redirect to login | | ✅/❌ | |
| 6.1 | Invalid Login | Error displays | | ✅/❌ | |
| 6.2 | Duplicate Email | Error displays | | ✅/❌ | |
| 7.1 | Navigation | Works correctly | | ✅/❌ | |
| 7.2 | Responsive Design | Adapts to screen | | ✅/❌ | |

---

## 🐛 Known Issues & Workarounds

### Issue 1: CORS Errors
**Symptom**: "Access to XMLHttpRequest blocked by CORS"
**Solution**: Backend CORS middleware is configured for localhost:3000. Ensure frontend is running on port 3000.

### Issue 2: Token Expiration
**Symptom**: 401 errors after 15 minutes
**Solution**: Refresh token is set in httpOnly cookie. Frontend will need to implement refresh token logic for production.

### Issue 3: File Download Not Working
**Symptom**: Download button doesn't trigger download
**Solution**: Browser may block file downloads. Check DevTools console for errors.

---

## 📞 Quick Reference

### API Endpoints

**Auth**:
```
POST   /auth/login      - { email, password }
POST   /auth/signup     - { name, email, password, org, role }
GET    /auth/user       - Returns current user data
POST   /auth/refresh    - Refresh access token
```

**Documents**:
```
POST   /api/documents/upload      - Upload document
GET    /api/documents/list        - List user documents
GET    /api/documents/document    - Get document details
POST   /api/documents/action      - Perform action
GET    /api/documents/file        - Download file
```

### Document Types
- **PO**: Purchase Order
- **BOL**: Bill of Lading
- **LOC**: Letter of Credit
- **INVOICE**: Invoice

### Role Actions Matrix

| Role | Document Type | Available Actions |
|------|-----------------|------------------|
| Buyer | BOL | RECEIVED |
| Seller | BOL | SHIPPED, ISSUE_INVOICE |
| Seller | PO | ISSUE_BOL |
| Auditor | PO | VERIFY |
| Auditor | LOC | VERIFY |
| Bank | LOC | ISSUE_LOC |
| Bank | INVOICE | PAID |

---

## ✅ Sign-Off

- [ ] All tests completed
- [ ] No critical issues found
- [ ] System is production-ready
- [ ] Documentation is complete

**Tester Signature**: ___________
**Date**: ___________
