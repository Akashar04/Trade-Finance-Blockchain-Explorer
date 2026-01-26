# Trade Finance Blockchain Explorer - Frontend

React frontend for Trade Finance Blockchain Explorer with document management and ledger tracking UI.

## Setup Instructions

### Prerequisites
- Node.js 16+ (includes npm)

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

The app will open at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

## Features

### Pages

- **Login/Signup**: Authentication with role selection (buyer, seller, auditor, bank)
- **Documents List**: View all your documents with type, creation date, and hash preview
- **Upload Document**: Upload new documents with doc number and seller information
- **Document Details**: 
  - View full document metadata
  - Download files
  - See complete ledger timeline
  - Perform role-based actions on documents

### Role-Based Actions

Documents can have the following actions based on user role:

- **Buyer**: RECEIVED on BOL
- **Seller**: SHIPPED on BOL, ISSUE_BOL on PO, ISSUE_INVOICE on BOL
- **Auditor**: VERIFY on PO and LOC
- **Bank**: PAID on INVOICE, ISSUE_LOC on LOC

## Libraries & Documentation

- [React](https://react.dev/)
- [TailwindCSS](https://tailwindcss.com/docs)
- [React Router](https://reactrouter.com/)
- [Axios](https://axios-http.com/)