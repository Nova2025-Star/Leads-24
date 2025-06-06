import React from 'react';
import { Outlet } from 'react-router-dom';

const AuthLayout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100">
      <Outlet />
    </div>
  );
};

export default AuthLayout;
