import React from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  // For now, just return children. Later this will check authentication
  return <>{children}</>;
};

export default ProtectedRoute; 