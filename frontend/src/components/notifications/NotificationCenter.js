import React, { useState, useEffect } from 'react';
import { useNotifications } from '../../contexts/NotificationContext';
import { Badge, Button, Card, Dropdown, List, Spin, Tabs, Typography, Empty, Switch, Form } from 'antd';
import { BellOutlined, CheckOutlined, SettingOutlined } from '@ant-design/icons';
import './NotificationCenter.css';

const { TabPane } = Tabs;
const { Text } = Typography;

const NotificationCenter = () => {
  const { 
    notifications, 
    unreadCount, 
    preferences, 
    loading, 
    markAsRead, 
    markAllAsRead, 
    updatePreferences 
  } = useNotifications();
  
  const [visible, setVisible] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) {
      form.setFieldsValue(preferences);
    }
  }, [visible, preferences, form]);

  const toggleVisible = () => {
    setVisible(!visible);
  };

  const handleTabChange = (key) => {
    setActiveTab(key);
  };

  const handleNotificationClick = (notification) => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
    
    // Handle navigation based on notification type
    if (notification.type === 'lead_created' || notification.type === 'lead_assigned') {
      // Navigate to lead details
      window.location.href = `/leads/${notification.entity_id}`;
    } else if (notification.type === 'quote_sent' || notification.type === 'quote_approved' || notification.type === 'quote_declined') {
      // Navigate to quote details
      window.location.href = `/quotes/${notification.entity_id}`;
    }
  };

  const handlePreferencesSubmit = (values) => {
    updatePreferences(values);
  };

  const getFilteredNotifications = () => {
    if (activeTab === 'all') {
      return notifications;
    } else if (activeTab === 'unread') {
      return notifications.filter(notification => !notification.read);
    } else if (activeTab === 'leads') {
      return notifications.filter(notification => 
        notification.type === 'lead_created' || 
        notification.type === 'lead_assigned' || 
        notification.type === 'lead_expired'
      );
    } else if (activeTab === 'quotes') {
      return notifications.filter(notification => 
        notification.type === 'quote_sent' || 
        notification.type === 'quote_approved' || 
        notification.type === 'quote_declined'
      );
    }
    return notifications;
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'lead_created':
        return <span className="notification-icon lead-created">LC</span>;
      case 'lead_assigned':
        return <span className="notification-icon lead-assigned">LA</span>;
      case 'lead_expired':
        return <span className="notification-icon lead-expired">LE</span>;
      case 'quote_sent':
        return <span className="notification-icon quote-sent">QS</span>;
      case 'quote_approved':
        return <span className="notification-icon quote-approved">QA</span>;
      case 'quote_declined':
        return <span className="notification-icon quote-declined">QD</span>;
      default:
        return <span className="notification-icon">N</span>;
    }
  };

  const renderNotificationItem = (notification) => (
    <List.Item 
      className={notification.read ? 'notification-item' : 'notification-item unread'}
      onClick={() => handleNotificationClick(notification)}
    >
      <List.Item.Meta
        avatar={getNotificationIcon(notification.type)}
        title={<Text strong={!notification.read}>{notification.title}</Text>}
        description={
          <>
            <Text>{notification.message}</Text>
            <div className="notification-time">
              {new Date(notification.created_at).toLocaleString()}
            </div>
          </>
        }
      />
    </List.Item>
  );

  const renderPreferencesForm = () => (
    <Form
      form={form}
      layout="vertical"
      onFinish={handlePreferencesSubmit}
      initialValues={preferences}
    >
      <Form.Item
        name="email"
        label="Email Notifications"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>
      
      <Form.Item
        name="inApp"
        label="In-App Notifications"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>
      
      <Form.Item
        name="push"
        label="Push Notifications"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>
      
      <Form.Item
        name="sms"
        label="SMS Notifications"
        valuePropName="checked"
      >
        <Switch />
      </Form.Item>
      
      <Form.Item>
        <Button type="primary" htmlType="submit">
          Save Preferences
        </Button>
      </Form.Item>
    </Form>
  );

  return (
    <div className="notification-center">
      <Badge count={unreadCount} overflowCount={99}>
        <Button 
          type="text" 
          icon={<BellOutlined />} 
          onClick={toggleVisible}
          className="notification-button"
        />
      </Badge>
      
      {visible && (
        <Card className="notification-panel">
          <Tabs 
            activeKey={activeTab} 
            onChange={handleTabChange}
            tabBarExtraContent={
              <div className="notification-actions">
                <Button 
                  type="text" 
                  icon={<CheckOutlined />} 
                  onClick={markAllAsRead}
                  disabled={unreadCount === 0}
                >
                  Mark all as read
                </Button>
                <Dropdown 
                  overlay={
                    <Card title="Notification Preferences" className="preferences-card">
                      {renderPreferencesForm()}
                    </Card>
                  } 
                  trigger={['click']}
                >
                  <Button type="text" icon={<SettingOutlined />} />
                </Dropdown>
              </div>
            }
          >
            <TabPane tab="All" key="all" />
            <TabPane tab={`Unread (${unreadCount})`} key="unread" />
            <TabPane tab="Leads" key="leads" />
            <TabPane tab="Quotes" key="quotes" />
          </Tabs>
          
          {loading ? (
            <div className="notification-loading">
              <Spin />
            </div>
          ) : (
            <List
              className="notification-list"
              dataSource={getFilteredNotifications()}
              renderItem={renderNotificationItem}
              locale={{ emptyText: <Empty description="No notifications" /> }}
            />
          )}
        </Card>
      )}
    </div>
  );
};

export default NotificationCenter;
