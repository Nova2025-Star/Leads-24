import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const AnalyticsContext = createContext();

export const useAnalytics = () => useContext(AnalyticsContext);

export const AnalyticsProvider = ({ children }) => {
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [timeSeriesData, setTimeSeriesData] = useState({});
  const [regionalData, setRegionalData] = useState([]);
  const [partnerData, setPartnerData] = useState([]);
  const [treeOperationsData, setTreeOperationsData] = useState([]);
  const [financialData, setFinancialData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { token } = useAuth();

  // Fetch performance metrics
  const fetchPerformanceMetrics = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/v1/analytics/performance', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setPerformanceMetrics(response.data);
    } catch (err) {
      console.error('Error fetching performance metrics:', err);
      setError('Failed to load performance metrics');
    } finally {
      setLoading(false);
    }
  };

  // Fetch time series data for a specific metric
  const fetchTimeSeriesData = async (metric, timeUnit = 'month', startDate, endDate) => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const params = {
        time_unit: timeUnit
      };
      
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      
      const response = await axios.get(`/api/v1/analytics/timeseries/${metric}`, {
        headers: { Authorization: `Bearer ${token}` },
        params
      });
      
      setTimeSeriesData(prev => ({
        ...prev,
        [metric]: response.data
      }));
      
      return response.data;
    } catch (err) {
      console.error(`Error fetching time series data for ${metric}:`, err);
      setError(`Failed to load time series data for ${metric}`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Fetch regional performance data
  const fetchRegionalData = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/v1/analytics/regions', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setRegionalData(response.data);
    } catch (err) {
      console.error('Error fetching regional data:', err);
      setError('Failed to load regional performance data');
    } finally {
      setLoading(false);
    }
  };

  // Fetch partner performance data
  const fetchPartnerData = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/v1/analytics/partners', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setPartnerData(response.data);
    } catch (err) {
      console.error('Error fetching partner data:', err);
      setError('Failed to load partner performance data');
    } finally {
      setLoading(false);
    }
  };

  // Fetch tree operations analysis data
  const fetchTreeOperationsData = async () => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/v1/analytics/tree-operations', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setTreeOperationsData(response.data);
    } catch (err) {
      console.error('Error fetching tree operations data:', err);
      setError('Failed to load tree operations analysis');
    } finally {
      setLoading(false);
    }
  };

  // Fetch financial report data
  const fetchFinancialData = async (period = 'month') => {
    if (!token) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('/api/v1/analytics/financial', {
        headers: { Authorization: `Bearer ${token}` },
        params: { period }
      });
      
      setFinancialData(response.data);
    } catch (err) {
      console.error('Error fetching financial data:', err);
      setError('Failed to load financial report');
    } finally {
      setLoading(false);
    }
  };

  // Export data as JSON
  const exportData = async (entityType) => {
    if (!token) return;
    
    try {
      const response = await axios.get(`/api/v1/analytics/export/${entityType}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      return response.data;
    } catch (err) {
      console.error(`Error exporting ${entityType} data:`, err);
      setError(`Failed to export ${entityType} data`);
      return null;
    }
  };

  // Load initial data when component mounts
  useEffect(() => {
    if (token) {
      fetchPerformanceMetrics();
    }
  }, [token, fetchPerformanceMetrics]);

  const value = {
    performanceMetrics,
    timeSeriesData,
    regionalData,
    partnerData,
    treeOperationsData,
    financialData,
    loading,
    error,
    fetchPerformanceMetrics,
    fetchTimeSeriesData,
    fetchRegionalData,
    fetchPartnerData,
    fetchTreeOperationsData,
    fetchFinancialData,
    exportData
  };

  return (
    <AnalyticsContext.Provider value={value}>
      {children}
    </AnalyticsContext.Provider>
  );
};

export default AnalyticsContext;
