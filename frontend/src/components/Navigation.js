import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navigation() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link to="/documents" className="font-bold text-lg">
              Trade Finance Explorer
            </Link>
            <Link to="/documents" className="hover:bg-blue-700 px-3 py-2 rounded">
              Documents
            </Link>
            <Link to="/upload" className="hover:bg-blue-700 px-3 py-2 rounded">
              Upload
            </Link>
          </div>
          <div className="flex items-center">
            <button
              onClick={handleLogout}
              className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
            >
              Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
