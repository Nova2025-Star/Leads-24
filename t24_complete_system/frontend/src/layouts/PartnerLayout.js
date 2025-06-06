import React from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const PartnerLayout = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Navigation */}
      <nav className="bg-gradient-to-r from-green-700 to-green-900 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-xl font-bold">T24 Partner Portal</span>
              </div>
              <div className="ml-6 flex space-x-8">
                <NavLink 
                  to="/partner" 
                  end
                  className={({ isActive }) => 
                    `inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive ? "border-green-300 text-white" : "border-transparent text-green-100 hover:border-green-200 hover:text-white"}`
                  }
                >
                  Dashboard
                </NavLink>
                <NavLink 
                  to="/partner/leads" 
                  className={({ isActive }) => 
                    `inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive ? "border-green-300 text-white" : "border-transparent text-green-100 hover:border-green-200 hover:text-white"}`
                  }
                >
                  Leads
                </NavLink>
                <NavLink 
                  to="/partner/quotes" 
                  className={({ isActive }) => 
                    `inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${isActive ? "border-green-300 text-white" : "border-transparent text-green-100 hover:border-green-200 hover:text-white"}`
                  }
                >
                  Quotes
                </NavLink>
              </div>
            </div>
            <div className="flex items-center">
              <div className="mr-4 flex items-center">
                <div className="h-8 w-8 rounded-full bg-green-500 flex items-center justify-center mr-2">
                  <span className="text-sm font-medium">{user?.email?.charAt(0).toUpperCase()}</span>
                </div>
                <span className="text-sm">
                  {user?.email}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white text-sm font-medium py-2 px-4 rounded transition-colors duration-200"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8 fade-in">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-white shadow-inner py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-gray-500 text-sm">
            &copy; {new Date().getFullYear()} T24 Arborist Lead System. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default PartnerLayout;
