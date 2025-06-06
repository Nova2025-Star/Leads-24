import React from 'react';
import { useNotifications } from '../../contexts/NotificationContext';
import { Card, Table, Tag, Button, Typography, Spin, Empty } from 'antd';
import { BellOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import './NotificationSettings.css';

const { Title, Text } = Typography;

const NotificationSettings = () => {
  const { 
    notifications, 
    preferences, 
    loading, 
    updatePreferences 
  } = useNotifications();

  // Group notifications by type for statistics
  const getNotificationStats = () => {
    const stats = {
      lead_created: 0,
      lead_assigned: 0,
      lead_expired: 0,
      quote_sent: 0,
      quote_approved: 0,
      quote_declined: 0,
      system: 0
    };

    notifications.forEach(notification => {
      if (stats.hasOwnProperty(notification.type)) {
        stats[notification.type]++;
      } else {
        stats.system++;
      }
    });

    return stats;
  };

  const stats = getNotificationStats();

  // Table columns for notification types
  const columns = [
    {
      title: 'Notification Type',
      dataIndex: 'type',
      key: 'type',
      render: (text) => {
        const displayNames = {
          lead_created: 'Lead Created',
          lead_assigned: 'Lead Assigned',
          lead_expired: 'Lead Expired',
          quote_sent: 'Quote Sent',
          quote_approved: 'Quote Approved',
          quote_declined: 'Quote Declined',
          system: 'System Notifications'
        };
        return displayNames[text] || text;
      }
    },
    {
      title: 'Count',
      dataIndex: 'count',
      key: 'count',
      render: (count) => <Tag color="blue">{count}</Tag>
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
      render: (enabled, record) => (
        <Button 
          type={enabled ? "primary" : "default"}
          shape="circle"
          icon={enabled ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          onClick={() => toggleChannel(record.type, 'email', !enabled)}
        />
      )
    },
    {
      title: 'In-App',
      dataIndex: 'inApp',
      key: 'inApp',
      render: (enabled, record) => (
        <Button 
          type={enabled ? "primary" : "default"}
          shape="circle"
          icon={enabled ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          onClick={() => toggleChannel(record.type, 'inApp', !enabled)}
        />
      )
    },
    {
      title: 'Push',
      dataIndex: 'push',
      key: 'push',
      render: (enabled, record) => (
        <Button 
          type={enabled ? "primary" : "default"}
          shape="circle"
          icon={enabled ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          onClick={() => toggleChannel(record.type, 'push', !enabled)}
        />
      )
    },
    {
      title: 'SMS',
      dataIndex: 'sms',
      key: 'sms',
      render: (enabled, record) => (
        <Button 
          type={enabled ? "primary" : "default"}
          shape="circle"
          icon={enabled ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          onClick={() => toggleChannel(record.type, 'sms', !enabled)}
        />
      )
    }
  ];

  // Prepare data for the table
  const getTableData = () => {
    // In a real implementation, we would get detailed preferences per notification type
    // For this example, we'll use the same preferences for all types
    return Object.keys(stats).map(type => ({
      key: type,
      type,
      count: stats[type],
      email: preferences.email,
      inApp: preferences.inApp,
      push: preferences.push,
      sms: preferences.sms
    }));
  };

  // Toggle notification channel for a specific type
  const toggleChannel = (type, channel, value) => {
    // In a real implementation, we would update preferences per notification type
    // For this example, we'll update the global preferences
    const newPreferences = { ...preferences, [channel]: value };
    updatePreferences(newPreferences);
  };

  // Toggle all channels for all types
  const toggleAllChannels = (channel, value) => {
    const newPreferences = { ...preferences, [channel]: value };
    updatePreferences(newPreferences);
  };

  return (
    <div className="notification-settings">
      <Card className="notification-settings-card">
        <Title level={3}>
          <BellOutlined /> Notification Settings
        </Title>
        
        <Text className="notification-settings-description">
          Configure how you want to receive notifications from the system.
          You can enable or disable different notification channels for each type of notification.
        </Text>
        
        {loading ? (
          <div className="notification-settings-loading">
            <Spin size="large" />
          </div>
        ) : notifications.length === 0 ? (
          <Empty description="No notification history found" />
        ) : (
          <>
            <div className="notification-settings-actions">
              <div className="notification-settings-action">
                <Text strong>Email All:</Text>
                <Button 
                  type={preferences.email ? "primary" : "default"}
                  shape="circle"
                  icon={preferences.email ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                  onClick={() => toggleAllChannels('email', !preferences.email)}
                />
              </div>
              
              <div className="notification-settings-action">
                <Text strong>In-App All:</Text>
                <Button 
                  type={preferences.inApp ? "primary" : "default"}
                  shape="circle"
                  icon={preferences.inApp ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                  onClick={() => toggleAllChannels('inApp', !preferences.inApp)}
                />
              </div>
              
              <div className="notification-settings-action">
                <Text strong>Push All:</Text>
                <Button 
                  type={preferences.push ? "primary" : "default"}
                  shape="circle"
                  icon={preferences.push ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                  onClick={() => toggleAllChannels('push', !preferences.push)}
                />
              </div>
              
              <div className="notification-settings-action">
                <Text strong>SMS All:</Text>
                <Button 
                  type={preferences.sms ? "primary" : "default"}
                  shape="circle"
                  icon={preferences.sms ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
                  onClick={() => toggleAllChannels('sms', !preferences.sms)}
                />
              </div>
            </div>
            
            <Table 
              columns={columns} 
              dataSource={getTableData()} 
              pagination={false}
              className="notification-settings-table"
            />
          </>
        )}
      </Card>
    </div>
  );
};

export default NotificationSettings;
