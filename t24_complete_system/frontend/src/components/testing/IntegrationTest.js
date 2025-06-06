import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import { useAccounting } from '../contexts/AccountingContext';
import { useAnalytics } from '../contexts/AnalyticsContext';
import { Button, Spin, Alert, Result } from 'antd';
import { CheckCircleOutlined } from '@ant-design/icons';
import './IntegrationTest.css';

const IntegrationTest = () => {
  const { user, isAuthenticated } = useAuth();
  const { notifications } = useNotification();
  const { accountingSystems } = useAccounting();
  const { performanceMetrics } = useAnalytics();
  
  const [testResults, setTestResults] = useState({
    auth: { status: 'pending', message: 'Not tested yet' },
    notification: { status: 'pending', message: 'Not tested yet' },
    analytics: { status: 'pending', message: 'Not tested yet' },
    accounting: { status: 'pending', message: 'Not tested yet' }
  });
  
  const [loading, setLoading] = useState(false);
  const [allPassed, setAllPassed] = useState(false);
  
  useEffect(() => {
    // Check if all tests have passed
    const allTestsPassed = Object.values(testResults).every(
      result => result.status === 'success'
    );
    
    setAllPassed(allTestsPassed);
  }, [testResults]);
  
  const runAuthTest = () => {
    setLoading(true);
    
    // Test authentication context
    if (isAuthenticated && user) {
      setTestResults(prev => ({
        ...prev,
        auth: { 
          status: 'success', 
          message: `Authentication successful. User: ${user.email}, Role: ${user.role}` 
        }
      }));
    } else {
      setTestResults(prev => ({
        ...prev,
        auth: { 
          status: 'error', 
          message: 'Authentication failed. User not authenticated or user data missing.' 
        }
      }));
    }
    
    setLoading(false);
  };
  
  const runNotificationTest = () => {
    setLoading(true);
    
    // Test notification context
    if (notifications !== undefined) {
      setTestResults(prev => ({
        ...prev,
        notification: { 
          status: 'success', 
          message: `Notification system connected. ${notifications.length} notifications available.` 
        }
      }));
    } else {
      setTestResults(prev => ({
        ...prev,
        notification: { 
          status: 'error', 
          message: 'Notification system not connected or data missing.' 
        }
      }));
    }
    
    setLoading(false);
  };
  
  const runAnalyticsTest = () => {
    setLoading(true);
    
    // Test analytics context
    if (performanceMetrics !== undefined) {
      setTestResults(prev => ({
        ...prev,
        analytics: { 
          status: 'success', 
          message: 'Analytics system connected. Performance metrics available.' 
        }
      }));
    } else {
      setTestResults(prev => ({
        ...prev,
        analytics: { 
          status: 'error', 
          message: 'Analytics system not connected or data missing.' 
        }
      }));
    }
    
    setLoading(false);
  };
  
  const runAccountingTest = () => {
    setLoading(true);
    
    // Test accounting context
    if (accountingSystems !== undefined) {
      setTestResults(prev => ({
        ...prev,
        accounting: { 
          status: 'success', 
          message: `Accounting system connected. ${accountingSystems.length} accounting systems available.` 
        }
      }));
    } else {
      setTestResults(prev => ({
        ...prev,
        accounting: { 
          status: 'error', 
          message: 'Accounting system not connected or data missing.' 
        }
      }));
    }
    
    setLoading(false);
  };
  
  const runAllTests = () => {
    runAuthTest();
    runNotificationTest();
    runAnalyticsTest();
    runAccountingTest();
  };
  
  return (
    <div className="integration-test">
      <h2>Backend Integration Test</h2>
      
      {allPassed ? (
        <Result
          status="success"
          title="All Integration Tests Passed!"
          subTitle="The frontend is successfully connected to all backend services."
          icon={<CheckCircleOutlined />}
        />
      ) : (
        <div className="test-container">
          <div className="test-controls">
            <Button type="primary" onClick={runAllTests} loading={loading}>
              Run All Tests
            </Button>
            <div className="individual-tests">
              <Button onClick={runAuthTest} loading={loading}>Test Authentication</Button>
              <Button onClick={runNotificationTest} loading={loading}>Test Notifications</Button>
              <Button onClick={runAnalyticsTest} loading={loading}>Test Analytics</Button>
              <Button onClick={runAccountingTest} loading={loading}>Test Accounting</Button>
            </div>
          </div>
          
          <div className="test-results">
            <div className="test-result-item">
              <h3>Authentication</h3>
              {testResults.auth.status === 'pending' ? (
                <span className="status pending">Not tested</span>
              ) : testResults.auth.status === 'success' ? (
                <span className="status success">Success</span>
              ) : (
                <span className="status error">Failed</span>
              )}
              <p>{testResults.auth.message}</p>
            </div>
            
            <div className="test-result-item">
              <h3>Notification System</h3>
              {testResults.notification.status === 'pending' ? (
                <span className="status pending">Not tested</span>
              ) : testResults.notification.status === 'success' ? (
                <span className="status success">Success</span>
              ) : (
                <span className="status error">Failed</span>
              )}
              <p>{testResults.notification.message}</p>
            </div>
            
            <div className="test-result-item">
              <h3>Analytics System</h3>
              {testResults.analytics.status === 'pending' ? (
                <span className="status pending">Not tested</span>
              ) : testResults.analytics.status === 'success' ? (
                <span className="status success">Success</span>
              ) : (
                <span className="status error">Failed</span>
              )}
              <p>{testResults.analytics.message}</p>
            </div>
            
            <div className="test-result-item">
              <h3>Accounting Integration</h3>
              {testResults.accounting.status === 'pending' ? (
                <span className="status pending">Not tested</span>
              ) : testResults.accounting.status === 'success' ? (
                <span className="status success">Success</span>
              ) : (
                <span className="status error">Failed</span>
              )}
              <p>{testResults.accounting.message}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default IntegrationTest;
