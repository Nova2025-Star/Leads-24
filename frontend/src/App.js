import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';

// Contexts
import { AuthProvider } from './contexts/AuthContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { AnalyticsProvider } from './contexts/AnalyticsContext';
import { CustomerPortalProvider } from './contexts/CustomerPortalContext';
import { AccountingProvider } from './contexts/AccountingContext';

// Layouts
// import MobileResponsiveLayout from './layouts/MobileResponsiveLayout'; // Unused
import AdminLayout from './layouts/AdminLayout';
import PartnerLayout from './layouts/PartnerLayout';
import AuthLayout from './layouts/AuthLayout';

// Pages
import Login from './pages/Login';
import AdminDashboard from './pages/admin/Dashboard';
import PartnerDashboard from './pages/partner/Dashboard';
import CustomerPortalLogin from './components/customer-portal/CustomerPortalLogin';
import CustomerPortalDashboard from './components/customer-portal/CustomerPortalDashboard';

// Analytics Components
import PerformanceDashboard from './components/analytics/PerformanceDashboard';
import RegionalAnalysis from './components/analytics/RegionalAnalysis';
import PartnerPerformance from './components/analytics/PartnerPerformance';
import TreeOperationsAnalysis from './components/analytics/TreeOperationsAnalysis';

// Accounting Components
import AccountingIntegration from './components/accounting/AccountingIntegration';
import InvoiceManagement from './components/accounting/InvoiceManagement';

// Theme configuration
const theme = {
  token: {
    colorPrimary: '#2E7D32',
    fontFamily: 'Poppins, sans-serif',
    borderRadius: 4,
  },
};

function App() {
  return (
    <ConfigProvider theme={theme}>
      <AuthProvider>
        <NotificationProvider>
          <AnalyticsProvider>
            <CustomerPortalProvider>
              <AccountingProvider>
                <Router>
                  <Routes>
                    {/* Auth Routes */}
                    <Route path="/login" element={
                      <AuthLayout>
                        <Login />
                      </AuthLayout>
                    } />
                    
                    {/* Admin Routes */}
                    <Route path="/admin" element={<AdminLayout />}>
                      <Route index element={<AdminDashboard />} />
                      <Route path="analytics">
                        <Route index element={<PerformanceDashboard />} />
                        <Route path="regional" element={<RegionalAnalysis />} />
                        <Route path="partners" element={<PartnerPerformance />} />
                        <Route path="tree-operations" element={<TreeOperationsAnalysis />} />
                      </Route>
                      <Route path="accounting">
                        <Route index element={<AccountingIntegration />} />
                        <Route path="invoices/:connectionId" element={<InvoiceManagement />} />
                      </Route>
                    </Route>
                    
                    {/* Partner Routes */}
                    <Route path="/partner" element={<PartnerLayout />}>
                      <Route index element={<PartnerDashboard />} />
                      {/* Add other partner routes here if needed */}
                    </Route>
                    
                    {/* Customer Portal Routes */}
                    <Route path="/customer-portal">
                      <Route index element={<CustomerPortalLogin />} />
                      <Route path="dashboard/:customerId" element={<CustomerPortalDashboard />} />
                    </Route>
                    
                    {/* Default Route */}
                    <Route path="/" element={<Navigate to="/login" replace />} />
                  </Routes>
                </Router>
              </AccountingProvider>
            </CustomerPortalProvider>
          </AnalyticsProvider>
        </NotificationProvider>
      </AuthProvider>
    </ConfigProvider>
  );
}

export default App;
