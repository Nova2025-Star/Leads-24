import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import api from '../services/api'; // Import the updated API service

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Check if user is already logged in on mount
  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');
    
    if (token && storedUser) {
      setUser(JSON.parse(storedUser));
      setIsAuthenticated(true);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      api.setAuthToken(token); // Use the API service to set token
    }
    
    setLoading(false);
  }, []);

  // Login function - updated for FastAPI 0.88.0 compatibility
  const login = async (email, password) => {
    try {
      setLoading(true);
      setError(null);
      
      // Use the compatibility wrapper from our updated API service
      const response = await axios.post('/api/v1/auth/token', {
        username: email,
        password: password
      }, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      // Handle potential differences in response format between FastAPI versions
      const { access_token } = response.data;
      
      if (!access_token) {
        throw new Error('Invalid response format: access_token not found');
      }
      
      // Store token in localStorage and axios defaults
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      api.setAuthToken(access_token); // Use the API service to set token
      
      // Decode token to get user info (in a real app, you might want to fetch user data)
      // This is a simplified example
      try {
        const base64Url = access_token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(atob(base64).split('').map(function(c) {
          return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
        }).join(''));
        
        const userData = JSON.parse(jsonPayload);
        const userObj = {
          id: userData.id || userData.sub, // Handle different token formats
          email: userData.sub || userData.email,
          role: userData.role
        };
        
        localStorage.setItem('user', JSON.stringify(userObj));
        setUser(userObj);
        setIsAuthenticated(true);
        
        return userObj;
      } catch (decodeError) {
        console.error('Error decoding token:', decodeError);
        // If token decoding fails, try to get user info from a different endpoint
        // This is a fallback mechanism for compatibility
        try {
          const userResponse = await api.getUserInfo();
          const userObj = userResponse.data;
          
          localStorage.setItem('user', JSON.stringify(userObj));
          setUser(userObj);
          setIsAuthenticated(true);
          
          return userObj;
        } catch (userInfoError) {
          console.error('Error fetching user info:', userInfoError);
          // If all else fails, create a minimal user object
          const minimalUser = { email };
          localStorage.setItem('user', JSON.stringify(minimalUser));
          setUser(minimalUser);
          setIsAuthenticated(true);
          
          return minimalUser;
        }
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    delete axios.defaults.headers.common['Authorization'];
    api.setAuthToken(null); // Use the API service to clear token
    setUser(null);
    setIsAuthenticated(false);
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    error,
    login,
    logout
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
