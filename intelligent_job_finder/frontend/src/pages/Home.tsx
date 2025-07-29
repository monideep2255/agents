import React from 'react';
import { Link } from 'react-router-dom';
import { Search, Briefcase, User, TrendingUp } from 'lucide-react';

const Home: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto">
      {/* Hero Section */}
      <div className="text-center py-16">
        <h1 className="text-5xl font-bold text-gray-900 mb-6">
          Find Your Dream Job with
          <span className="text-blue-600"> AI Intelligence</span>
        </h1>
        <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
          Discover, apply, and land your perfect job with our AI-powered platform. 
          We analyze thousands of opportunities to find the best matches for your skills and career goals.
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            to="/jobs"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            <Search className="inline-block w-5 h-5 mr-2" />
            Search Jobs
          </Link>
          <Link
            to="/register"
            className="border border-blue-600 text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-blue-50 transition-colors"
          >
            Get Started
          </Link>
        </div>
      </div>

      {/* Features Section */}
      <div className="grid md:grid-cols-3 gap-8 py-16">
        <div className="text-center p-6">
          <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-blue-600" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Smart Job Matching</h3>
          <p className="text-gray-600">
            Our AI analyzes your skills and preferences to find the perfect job matches.
          </p>
        </div>
        
        <div className="text-center p-6">
          <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <Briefcase className="w-8 h-8 text-green-600" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Automated Applications</h3>
          <p className="text-gray-600">
            Apply to multiple jobs with customized resumes and cover letters.
          </p>
        </div>
        
        <div className="text-center p-6">
          <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
            <TrendingUp className="w-8 h-8 text-purple-600" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Career Growth</h3>
          <p className="text-gray-600">
            Track your applications and get insights to improve your success rate.
          </p>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-gray-100 rounded-lg p-8 mb-16">
        <div className="grid md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-3xl font-bold text-blue-600 mb-2">10,000+</div>
            <div className="text-gray-600">Active Jobs</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-green-600 mb-2">5,000+</div>
            <div className="text-gray-600">Happy Users</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-purple-600 mb-2">85%</div>
            <div className="text-gray-600">Success Rate</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-orange-600 mb-2">24/7</div>
            <div className="text-gray-600">AI Support</div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center py-16">
        <h2 className="text-3xl font-bold mb-4">Ready to Find Your Dream Job?</h2>
        <p className="text-gray-600 mb-8">
          Join thousands of professionals who have already found their perfect match.
        </p>
        <Link
          to="/register"
          className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
        >
          <User className="inline-block w-5 h-5 mr-2" />
          Create Free Account
        </Link>
      </div>
    </div>
  );
};

export default Home; 