import React from 'react';
import { Link } from 'react-router-dom';
import '../index.css';

const NotFound = () => {
  return (
    <div className="container fade-in">
      <div className="card" style={{ textAlign: 'center', marginTop: '100px' }}>
        <h1>404</h1>
        <h2>Page Not Found</h2>
        <p>The page you are looking for does not exist or has been moved.</p>
        <Link to="/" className="btn btn-primary">
          Go to Dashboard
        </Link>
      </div>
    </div>
  );
};

export default NotFound;
