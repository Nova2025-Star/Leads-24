import React, { createContext, useState, useContext } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const CustomerPortalContext = createContext();

export const useCustomerPortal = () => useContext(CustomerPortalContext);

export const CustomerPortalProvider = ({ children }) => {
  const [customerQuotes, setCustomerQuotes] = useState([]);
  const [currentQuote, setCurrentQuote] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { token } = useAuth();

  // Fetch quotes for a specific customer
  const fetchCustomerQuotes = async (customerId) => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/v1/customer-portal/quotes/${customerId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setCustomerQuotes(response.data);
    } catch (err) {
      console.error('Error fetching customer quotes:', err);
      setError('Failed to load customer quotes');
    } finally {
      setLoading(false);
    }
  };

  // Fetch a specific quote by ID
  const fetchQuoteById = async (quoteId) => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/v1/customer-portal/quote/${quoteId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setCurrentQuote(response.data);
      return response.data;
    } catch (err) {
      console.error('Error fetching quote details:', err);
      setError('Failed to load quote details');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Update quote status (approve/decline)
  const updateQuoteStatus = async (quoteId, status, feedback = '') => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`/api/v1/customer-portal/quote/${quoteId}/status`, {
        status,
        feedback
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update the current quote with the new status
      setCurrentQuote(response.data);
      
      // Update the quote in the list
      setCustomerQuotes(prev => 
        prev.map(quote => 
          quote.id === quoteId ? { ...quote, status } : quote
        )
      );
      
      return response.data;
    } catch (err) {
      console.error('Error updating quote status:', err);
      setError('Failed to update quote status');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Generate a secure access token for a customer
  const generateCustomerAccessToken = async (quoteId, customerEmail) => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('/api/v1/customer-portal/generate-token', {
        quote_id: quoteId,
        customer_email: customerEmail
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      return response.data.access_token;
    } catch (err) {
      console.error('Error generating customer access token:', err);
      setError('Failed to generate customer access token');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Verify a customer access token
  const verifyCustomerAccessToken = async (accessToken) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post('/api/v1/customer-portal/verify-token', {
        access_token: accessToken
      });
      
      return response.data;
    } catch (err) {
      console.error('Error verifying customer access token:', err);
      setError('Failed to verify customer access token');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    customerQuotes,
    currentQuote,
    loading,
    error,
    fetchCustomerQuotes,
    fetchQuoteById,
    updateQuoteStatus,
    generateCustomerAccessToken,
    verifyCustomerAccessToken
  };

  return (
    <CustomerPortalContext.Provider value={value}>
      {children}
    </CustomerPortalContext.Provider>
  );
};

export default CustomerPortalContext;
