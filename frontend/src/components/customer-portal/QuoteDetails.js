import React, { useState, useEffect } from 'react';
import { useCustomerPortal } from '../../contexts/CustomerPortalContext';
import { Row, Col, Button, Spin, Alert, Steps, Divider, Typography, Tag, List } from 'antd';
import { 
  CheckCircleOutlined, 
  CloseCircleOutlined,
  FileTextOutlined,
  DollarOutlined,
  CalendarOutlined,
  UserOutlined,
  EnvironmentOutlined,
  PhoneOutlined,
  MailOutlined
} from '@ant-design/icons';
import ResponsiveCard from '../common/ResponsiveCard';
import { useMediaQuery } from 'react-responsive';
import './QuoteDetails.css';

const { Title, Text, Paragraph } = Typography;
const { Step } = Steps;

const QuoteDetails = ({ quoteId, onApprove, onDecline }) => {
  const { 
    currentQuote, 
    loading, 
    error, 
    fetchQuoteById,
    updateQuoteStatus
  } = useCustomerPortal();
  
  const [feedback] = useState(""); // setFeedback removed as it was unused
  const [submitting, setSubmitting] = useState(false);
  const isMobile = useMediaQuery({ maxWidth: 576 });
  
  useEffect(() => {
    fetchQuoteById(quoteId);
  }, [fetchQuoteById, quoteId]);
  
  const handleApprove = async () => {
    setSubmitting(true);
    try {
      await updateQuoteStatus(quoteId, 'approved', feedback);
      if (onApprove) onApprove();
    } finally {
      setSubmitting(false);
    }
  };
  
  const handleDecline = async () => {
    setSubmitting(true);
    try {
      await updateQuoteStatus(quoteId, 'declined', feedback);
      if (onDecline) onDecline();
    } finally {
      setSubmitting(false);
    }
  };
  
  if (loading) {
    return (
      <div className="quote-details-loading">
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
  
  if (!currentQuote) {
    return (
      <Alert
        message="Quote Not Found"
        description="The requested quote could not be found."
        type="warning"
        showIcon
      />
    );
  }
  
  // Determine current step based on quote status
  const getCurrentStep = (status) => {
    switch (status) {
      case 'draft':
        return 0;
      case 'sent':
        return 1;
      case 'approved':
        return 2;
      case 'declined':
        return 2;
      default:
        return 0;
    }
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
  
  return (
    <div className="quote-details">
      <ResponsiveCard
        title={
          <div className="quote-details-header">
            <span>Quote #{currentQuote.quote_number}</span>
            <Tag color={getStatusColor(currentQuote.status)}>
              {currentQuote.status.toUpperCase()}
            </Tag>
          </div>
        }
        icon={<FileTextOutlined />}
        className="quote-details-card"
      >
        <Steps
          current={getCurrentStep(currentQuote.status)}
          status={currentQuote.status === 'declined' ? 'error' : 'process'}
          size={isMobile ? 'small' : 'default'}
          className="quote-steps"
          direction={isMobile ? 'vertical' : 'horizontal'}
        >
          <Step title="Created" description={formatDate(currentQuote.created_at)} />
          <Step title="Sent" description={formatDate(currentQuote.sent_at)} />
          <Step 
            title={currentQuote.status === 'approved' ? 'Approved' : (currentQuote.status === 'declined' ? 'Declined' : 'Awaiting Response')} 
            description={currentQuote.status === 'approved' || currentQuote.status === 'declined' ? formatDate(currentQuote.updated_at) : 'Pending'} 
          />
        </Steps>
        
        <Divider />
        
        <Row gutter={[24, 24]} className="quote-info-section">
          <Col xs={24} md={12}>
            <div className="quote-section">
              <Title level={4}>Customer Information</Title>
              <div className="info-item">
                <UserOutlined className="info-icon" />
                <div className="info-content">
                  <Text strong>Name</Text>
                  <Text>{currentQuote.customer.name}</Text>
                </div>
              </div>
              <div className="info-item">
                <MailOutlined className="info-icon" />
                <div className="info-content">
                  <Text strong>Email</Text>
                  <Text>{currentQuote.customer.email}</Text>
                </div>
              </div>
              <div className="info-item">
                <PhoneOutlined className="info-icon" />
                <div className="info-content">
                  <Text strong>Phone</Text>
                  <Text>{currentQuote.customer.phone}</Text>
                </div>
              </div>
              <div className="info-item">
                <EnvironmentOutlined className="info-icon" />
                <div className="info-content">
                  <Text strong>Address</Text>
                  <Text>{currentQuote.customer.address}</Text>
                </div>
              </div>
            </div>
          </Col>
          
          <Col xs={24} md={12}>
            <div className="quote-section">
              <Title level={4}>Quote Information</Title>
              <div className="info-item">
                <CalendarOutlined className="info-icon" />
                <div className="info-content">
                  <Text strong>Valid Until</Text>
                  <Text>{formatDate(currentQuote.valid_until)}</Text>
                </div>
              </div>
              <div className="info-item">
                <UserOutlined className="info-icon" />
                <div className="info-content">
                  <Text strong>Created By</Text>
                  <Text>{currentQuote.created_by}</Text>
                </div>
              </div>
              <div className="info-item">
                <EnvironmentOutlined className="info-icon" />
                <div className="info-content">
                  <Text strong>Service Location</Text>
                  <Text>{currentQuote.service_location}</Text>
                </div>
              </div>
              <div className="info-item">
                <DollarOutlined className="info-icon" />
                <div className="info-content">
                  <Text strong>Total Amount</Text>
                  <Text className="quote-total">${currentQuote.total_amount.toLocaleString()}</Text>
                </div>
              </div>
            </div>
          </Col>
        </Row>
        
        <Divider />
        
        <div className="quote-section">
          <Title level={4}>Tree Operations</Title>
          <List
            dataSource={currentQuote.operations}
            renderItem={item => (
              <List.Item className="operation-item">
                <div className="operation-details">
                  <div className="operation-name">
                    <Text strong>{item.operation_type}</Text>
                    <Text type="secondary"> - {item.tree_species}</Text>
                  </div>
                  <div className="operation-description">
                    <Text>{item.description}</Text>
                  </div>
                </div>
                <div className="operation-price">
                  <Text strong>${item.price.toLocaleString()}</Text>
                </div>
              </List.Item>
            )}
          />
          
          <div className="quote-summary">
            <div className="quote-summary-item">
              <Text>Subtotal</Text>
              <Text>${currentQuote.subtotal.toLocaleString()}</Text>
            </div>
            <div className="quote-summary-item">
              <Text>Tax ({currentQuote.tax_rate}%)</Text>
              <Text>${currentQuote.tax_amount.toLocaleString()}</Text>
            </div>
            <div className="quote-summary-item total">
              <Text strong>Total</Text>
              <Text strong>${currentQuote.total_amount.toLocaleString()}</Text>
            </div>
          </div>
        </div>
        
        <Divider />
        
        <div className="quote-section">
          <Title level={4}>Notes</Title>
          <Paragraph>{currentQuote.notes || 'No additional notes.'}</Paragraph>
        </div>
        
        {currentQuote.status === 'sent' && (
          <>
            <Divider />
            
            <div className="quote-actions">
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                size="large"
                onClick={handleApprove}
                loading={submitting}
                className="approve-button"
              >
                Approve Quote
              </Button>
              
              <Button
                danger
                icon={<CloseCircleOutlined />}
                size="large"
                onClick={handleDecline}
                loading={submitting}
                className="decline-button"
              >
                Decline Quote
              </Button>
            </div>
          </>
        )}
      </ResponsiveCard>
    </div>
  );
};

export default QuoteDetails;
