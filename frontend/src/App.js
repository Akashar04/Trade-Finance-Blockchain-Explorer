import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DocumentsListPage from './pages/DocumentsListPage';
import UploadDocumentPage from './pages/UploadDocumentPage';
import DocumentDetailsPage from './pages/DocumentDetailsPage';
import Navigation from './components/Navigation';

import { AuthProvider, useAuth } from './context/AuthContext';

function AppContent() {
  const { token } = useAuth();

  const ProtectedRoute = ({ element }) => {
    return token ? element : <Navigate to="/login" />;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {token && <Navigation />}
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route
          path="/documents"
          element={<ProtectedRoute element={<DocumentsListPage />} />}
        />
        <Route
          path="/upload"
          element={<ProtectedRoute element={<UploadDocumentPage />} />}
        />
        <Route
          path="/documents/:id"
          element={<ProtectedRoute element={<DocumentDetailsPage />} />}
        />
        <Route path="/" element={token ? <Navigate to="/documents" /> : <Navigate to="/login" />} />
      </Routes>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppContent />
      </Router>
    </AuthProvider>
  );
}

export default App;
