import React, { useState } from 'react';
import { useCustomerPortal } from '../../contexts/CustomerPortalContext';
import { Button, Alert, Input, Form, Typography } from 'antd';
import { 
  FileTextOutlined, 
  LockOutlined,
  UserOutlined,
  MailOutlined
} from "@ant-design/icons";
import ResponsiveCard from "../common/ResponsiveCard";

import { useMediaQuery } from "react-responsive";
import './CustomerPortalLogin.css';

const { Title, Paragraph } = Typography;

const CustomerPortalLogin = ({ onLoginSuccess }) => {
  const { 
    verifyCustomerAccessToken,
    loading,
    error
  } = useCustomerPortal();
  
  const [form] = Form.useForm();
  // const [accessToken, setAccessToken] = useState("");
  // const isMobile = useMediaQuery({ maxWidth: 576 });
  
  const handleSubmit = async (values) => {
    try {
      const result = await verifyCustomerAccessToken(values.accessToken);
      if (result && result.valid) {
        if (onLoginSuccess) {
          onLoginSuccess(result.customer_id, result.quote_id);
        }
      }
    } catch (err) {
      console.error('Login error:', err);
    }
  };
  
  return (
    <div className="customer-portal-login">
      <ResponsiveCard
        title="Customer Quote Portal"
        icon={<FileTextOutlined />}
        className="login-card"
      >
        <div className="login-content">
          <div className="login-header">
            <Title level={3}>Welcome to T24 Arborist Quote Portal</Title>
            <Paragraph>
              Please enter the access token provided in your quote email to view and respond to your quote.
            </Paragraph>
          </div>
          
          <div className="login-form-container">
            <Form
              form={form}
              onFinish={handleSubmit}
              layout="vertical"
            >
              <Form.Item
                name="accessToken"
                label="Access Token"
                rules={[
                  { required: true, message: 'Please enter your access token' }
                ]}
              >
                <Input 
                  prefix={<LockOutlined />} 
                  placeholder="Enter your access token"
                  size="large"
                />
              </Form.Item>
              
              <Form.Item>
                <Button 
                  type="primary" 
                  htmlType="submit" 
                  loading={loading}
                  size="large"
                  block
                >
                  Access Quote
                </Button>
              </Form.Item>
            </Form>
            
            {error && (
              <Alert
                message="Error"
                description={error}
                type="error"
                showIcon
                style={{ marginTop: 16 }}
              />
            )}
          </div>
          
          <div className="login-help">
            <Title level={4}>Need Help?</Title>
            <Paragraph>
              If you've lost your access token or are experiencing issues accessing your quote, please contact us:
            </Paragraph>
            <div className="contact-info">
              <p><MailOutlined /> support@t24leads.se</p>
              <p><UserOutlined /> (555) 123-4567</p>
            </div>
          </div>
        </div>
      </ResponsiveCard>
    </div>
  );
};

export default CustomerPortalLogin;
