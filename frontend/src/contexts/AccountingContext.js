import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const AccountingContext = createContext();

export const useAccounting = () => useContext(AccountingContext);

export const AccountingProvider = ({ children }) => {
  const [accountingSystems, setAccountingSystems] = useState([]);
  const [connectedSystems, setConnectedSystems] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [payments, setPayments] = useState([]);
  const [syncStatus, setSyncStatus] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { token } = useAuth();

  // Fetch available accounting systems
  const fetchAccountingSystems = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/v1/accounting/systems', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setAccountingSystems(response.data);
    } catch (err) {
      console.error('Error fetching accounting systems:', err);
      setError('Failed to load accounting systems');
    } finally {
      setLoading(false);
    }
  };

  // Fetch connected accounting systems
  const fetchConnectedSystems = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/v1/accounting/connected', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setConnectedSystems(response.data);
    } catch (err) {
      console.error('Error fetching connected systems:', err);
      setError('Failed to load connected accounting systems');
    } finally {
      setLoading(false);
    }
  };

  // Connect to an accounting system
  const connectAccountingSystem = async (systemId, credentials) => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`/api/v1/accounting/connect/${systemId}`, credentials, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update connected systems list
      await fetchConnectedSystems();
      
      return response.data;
    } catch (err) {
      console.error('Error connecting to accounting system:', err);
      setError('Failed to connect to accounting system');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Disconnect from an accounting system
  const disconnectAccountingSystem = async (connectionId) => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      await axios.delete(`/api/v1/accounting/disconnect/${connectionId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update connected systems list
      await fetchConnectedSystems();
      
      return true;
    } catch (err) {
      console.error('Error disconnecting from accounting system:', err);
      setError('Failed to disconnect from accounting system');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Fetch invoices from accounting system
  const fetchInvoices = async (connectionId, filters = {}) => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/v1/accounting/${connectionId}/invoices`, {
        headers: { Authorization: `Bearer ${token}` },
        params: filters
      });
      
      setInvoices(response.data);
      return response.data;
    } catch (err) {
      console.error('Error fetching invoices:', err);
      setError('Failed to load invoices');
      return [];
    } finally {
      setLoading(false);
    }
  };

  // Create invoice from quote
  const createInvoiceFromQuote = async (connectionId, quoteId) => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.post(`/api/v1/accounting/${connectionId}/invoices`, {
        quote_id: quoteId
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update invoices list
      await fetchInvoices(connectionId);
      
      return response.data;
    } catch (err) {
      console.error('Error creating invoice:', err);
      setError('Failed to create invoice from quote');
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Fetch payments from accounting system
  const fetchPayments = async (connectionId, filters = {}) => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`/api/v1/accounting/${connectionId}/payments`, {
        headers: { Authorization: `Bearer ${token}` },
        params: filters
      });
      
      setPayments(response.data);
      return response.data;
    } catch (err) {
      console.error('Error fetching payments:', err);
      setError('Failed to load payments');
      return [];
    } finally {
      setLoading(false);
    }
  };

  // Sync data with accounting system
  const syncWithAccountingSystem = async (connectionId, entities = ['customers', 'invoices', 'payments']) => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    setSyncStatus(prev => ({ ...prev, [connectionId]: 'syncing' }));
    
    try {
      const response = await axios.post(`/api/v1/accounting/${connectionId}/sync`, {
        entities
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setSyncStatus(prev => ({ ...prev, [connectionId]: 'success' }));
      return response.data;
    } catch (err) {
      console.error('Error syncing with accounting system:', err);
      setError('Failed to sync with accounting system');
      setSyncStatus(prev => ({ ...prev, [connectionId]: 'error' }));
      return null;
    } finally {
      setLoading(false);
      // Reset sync status after 5 seconds
      setTimeout(() => {
        setSyncStatus(prev => ({ ...prev, [connectionId]: null }));
      }, 5000);
    }
  };

  // Load initial data when component mounts
  useEffect(() => {
    if (token) {
      fetchAccountingSystems();
      fetchConnectedSystems();
    }
  }, [token, fetchAccountingSystems, fetchConnectedSystems]);

  const value = {
    accountingSystems,
    connectedSystems,
    invoices,
    payments,
    syncStatus,
    loading,
    error,
    fetchAccountingSystems,
    fetchConnectedSystems,
    connectAccountingSystem,
    disconnectAccountingSystem,
    fetchInvoices,
    createInvoiceFromQuote,
    fetchPayments,
    syncWithAccountingSystem
  };

  return (
    <AccountingContext.Provider value={value}>
      {children}
    </AccountingContext.Provider>
  );
};

export default AccountingContext;
