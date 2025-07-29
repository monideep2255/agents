import React from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, User, LogOut } from 'lucide-react';

const Navbar: React.FC = () => {
  // For now, we'll use a simple state. Later this will come from AuthContext
  const isAuthenticated = false;
  const user = null;

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <Briefcase className="w-8 h-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">JobFinder</span>
          </Link>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              to="/jobs"
              className="text-gray-600 hover:text-blue-600 transition-colors"
            >
              Search Jobs
            </Link>
            <Link
              to="/jobs/remote"
              className="text-gray-600 hover:text-blue-600 transition-colors"
            >
              Remote Jobs
            </Link>
            <Link
              to="/jobs/recent"
              className="text-gray-600 hover:text-blue-600 transition-colors"
            >
              Recent Jobs
            </Link>
          </div>

          {/* Auth Buttons */}
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link
                  to="/profile"
                  className="flex items-center space-x-2 text-gray-600 hover:text-blue-600 transition-colors"
                >
                  <User className="w-5 h-5" />
                  <span>{user?.full_name || user?.username}</span>
                </Link>
                <button className="flex items-center space-x-2 text-gray-600 hover:text-red-600 transition-colors">
                  <LogOut className="w-5 h-5" />
                  <span>Logout</span>
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-gray-600 hover:text-blue-600 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 