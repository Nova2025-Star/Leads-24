import axios from 'axios';

// Dynamically set API base URL at build time via REACT_APP_API_URL
const API_BASE_URL = process.env.REACT_APP_API_URL || '/api/v1';

// Create a pre-configured Axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Global error handling interceptor
api.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error);

    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    } else if (error.request) {
      console.error('No response received for request:', error.request);
    } else {
      console.error('Error setting up request:', error.message);
    }

    return Promise.reject(error);
  }
);

// Authentication
export const login = (credentials) => api.post('/auth/token', credentials);
export const refreshToken = () => api.post('/auth/refresh');

// Leads
export const getLeads = () => api.get('/leads');
export const getLead = (id) => api.get(`/leads/${id}`);
export const createLead = (data) => api.post('/leads', data);
export const updateLead = (id, data) => api.put(`/leads/${id}`, data);

// Quotes
export const getQuotes = () => api.get('/quotes');
export const getQuote = (id) => api.get(`/quotes/${id}`);
export const createQuote = (data) => api.post('/quotes', data);
export const updateQuote = (id, data) => api.put(`/quotes/${id}`, data);

// Analytics
export const getPerformanceMetrics = () => api.get('/analytics/performance');
export const getTimeSeriesData = (metric, params) => api.get(`/analytics/timeseries/${metric}`, { params });
export const getRegionalData = () => api.get('/analytics/regions');
export const getPartnerData = () => api.get('/analytics/partners');
export const getTreeOperationsData = () => api.get('/analytics/tree-operations');
export const getFinancialData = (params) => api.get('/analytics/financial', { params });

// Notifications
export const getNotifications = (userId) => api.get(`/notifications/user/${userId}`);
export const markNotificationAsRead = (id) => api.post(`/notifications/read/${id}`);
export const getNotificationPreferences = (userId) => api.get(`/notifications/preferences/${userId}`);
export const updateNotificationPreferences = (data) => api.post('/notifications/preferences', data);

// Customer Portal
export const getCustomerQuotes = (customerId) => api.get(`/customer-portal/quotes/${customerId}`);
export const respondToQuote = (quoteId, response) => api.post(`/customer-portal/quotes/${quoteId}/respond`, response);

// Accounting
export const getAccountingConnections = () => api.get('/accounting/connections');
export const connectAccountingSystem = (data) => api.post('/accounting/connect', data);
export const getInvoices = (connectionId) => api.get(`/accounting/invoices/${connectionId}`);
export const createInvoice = (data) => api.post('/accounting/invoices', data);

// Health Check
export const checkHealth = () => api.get('/health');

// Auth Token setter (for session management)
export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export default api;
