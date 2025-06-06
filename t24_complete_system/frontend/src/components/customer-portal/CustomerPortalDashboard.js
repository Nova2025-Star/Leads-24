import React, { useState, useEffect } from 'react';
import { useCustomerPortal } from '../../contexts/CustomerPortalContext';
import { Button, Spin, Alert, List, Tag, Empty, Typography, Result } from 'antd';
import { 
  FileTextOutlined, 
  CheckCircleOutlined,
  CalendarOutlined,
  DollarOutlined
} from '@ant-design/icons';
import ResponsiveCard from '../common/ResponsiveCard';
import { useMediaQuery } from 'react-responsive';
import QuoteDetails from './QuoteDetails';
import './CustomerPortalDashboard.css';

const { Text } = Typography;

const CustomerPortalDashboard = ({ customerId, quoteId }) => {
  const { 
    customerQuotes, 
    loading, 
    error, 
    fetchCustomerQuotes
  } = useCustomerPortal();
  
  const [selectedQuoteId, setSelectedQuoteId] = useState(quoteId || null);
  const [viewMode, setViewMode] = useState(quoteId ? "details" : "list");
  // const isMobile = useMediaQuery({ maxWidth: 576 });
  
  useEffect(() => {
    if (customerId) {
      fetchCustomerQuotes(customerId);
    }
  }, [fetchCustomerQuotes, customerId]);
  
  const handleViewQuote = (id) => {
    setSelectedQuoteId(id);
    setViewMode('details');
  };
  
  const handleBackToList = () => {
    setViewMode('list');
  };
  
  const handleQuoteAction = () => {
    // Refresh quotes after action
    fetchCustomerQuotes(customerId);
    setViewMode('list');
  };
  
  // Get status tag color
  const getStatusColor = (status) => {
    switch (status) {
      case 'draft':
        return 'default';
      case 'sent':
        return 'processing';
      case 'approved':
        return 'success';
      case 'declined':
        return 'error';
      case 'expired':
        return 'warning';
      default:
        return 'default';
    }
  };
  
  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };
  
  if (loading && customerQuotes.length === 0) {
    return (
      <div className="customer-portal-loading">
        <Spin size="large" />
      </div>
    );
  }
  
  if (error) {
    return (
      <Alert
        message="Error"
        description={error}
        type="error"
        showIcon
      />
    );
  }
  
  if (viewMode === 'details' && selectedQuoteId) {
    return (
      <div className="customer-portal-dashboard">
        <div className="dashboard-header">
          <Button 
            onClick={handleBackToList}
            className="back-button"
          >
            Back to Quotes
          </Button>
        </div>
        
        <QuoteDetails 
          quoteId={selectedQuoteId} 
          onApprove={handleQuoteAction}
          onDecline={handleQuoteAction}
        />
      </div>
    );
  }
  
  return (
    <div className="customer-portal-dashboard">
      <ResponsiveCard
        title="Your Quotes"
        icon={<FileTextOutlined />}
        className="dashboard-card"
      >
        {customerQuotes.length === 0 ? (
          <Empty 
            description="No quotes found for your account." 
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <List
            className="quotes-list"
            itemLayout="vertical"
            dataSource={customerQuotes}
            renderItem={quote => (
              <List.Item
                key={quote.id}
                className="quote-list-item"
                actions={[
                  <Button 
                    type="primary" 
                    onClick={() => handleViewQuote(quote.id)}
                  >
                    View Details
                  </Button>
                ]}
              >
                <div className="quote-list-content">
                  <div className="quote-list-header">
                    <div className="quote-list-title">
                      <Text strong>Quote #{quote.quote_number}</Text>
                      <Tag color={getStatusColor(quote.status)}>
                        {quote.status.toUpperCase()}
                      </Tag>
                    </div>
                    <div className="quote-list-amount">
                      <DollarOutlined />
                      <Text strong>${quote.total_amount.toLocaleString()}</Text>
                    </div>
                  </div>
                  
                  <div className="quote-list-details">
                    <div className="quote-list-date">
                      <CalendarOutlined />
                      <Text>Created: {formatDate(quote.created_at)}</Text>
                    </div>
                    <div className="quote-list-date">
                      <CalendarOutlined />
                      <Text>Valid Until: {formatDate(quote.valid_until)}</Text>
                    </div>
                  </div>
                  
                  <div className="quote-list-description">
                    <Text>{quote.description || `Quote for tree services at ${quote.service_location}`}</Text>
                  </div>
                </div>
              </List.Item>
            )}
          />
        )}
        
        {customerQuotes.some(quote => quote.status === 'approved') && (
          <div className="approved-message">
            <Result
              status="success"
              title="Thank you for your business!"
              subTitle="We've received your approval and will be in touch shortly to schedule your service."
              icon={<CheckCircleOutlined />}
            />
          </div>
        )}
      </ResponsiveCard>
    </div>
  );
};

export default CustomerPortalDashboard;
