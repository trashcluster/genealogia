import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { FiLogOut, FiHome, FiUsers } from 'react-icons/fi';

export const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, logout, user } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) return null;

  return (
    <nav className="bg-indigo-600 text-white shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-8">
            <h1 className="text-2xl font-bold">Genealogy</h1>
            <div className="flex gap-4">
              <button
                onClick={() => navigate('/')}
                className="flex items-center gap-2 px-3 py-2 rounded hover:bg-indigo-500"
              >
                <FiHome /> Home
              </button>
              <button
                onClick={() => navigate('/individuals')}
                className="flex items-center gap-2 px-3 py-2 rounded hover:bg-indigo-500"
              >
                <FiUsers /> Family
              </button>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm">{user?.username}</span>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-3 py-2 rounded bg-red-600 hover:bg-red-700"
            >
              <FiLogOut /> Logout
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};
