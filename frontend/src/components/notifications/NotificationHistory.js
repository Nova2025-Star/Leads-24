import React from 'react';
import { useNotifications } from '../../contexts/NotificationContext';
import { List, Card, Typography, Tag, Timeline, Empty, Spin } from 'antd';
import { 
  BellOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined, 
  ClockCircleOutlined,
  UserOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import './NotificationHistory.css';

const { Title, Text } = Typography;

const NotificationHistory = () => {
  const { notifications, loading } = useNotifications();

  // Get icon based on notification type
  const getNotificationIcon = (type) => {
    switch (type) {
      case 'lead_created':
      case 'lead_assigned':
      case 'lead_expired':
        return <UserOutlined />;
      case 'quote_sent':
      case 'quote_approved':
      case 'quote_declined':
        return <FileTextOutlined />;
      default:
        return <BellOutlined />;
    }
  };

  // Get color based on notification type
  const getNotificationColor = (type) => {
    switch (type) {
      case 'lead_created':
        return 'green';
      case 'lead_assigned':
        return 'blue';
      case 'lead_expired':
        return 'red';
      case 'quote_sent':
        return 'purple';
      case 'quote_approved':
        return 'cyan';
      case 'quote_declined':
        return 'orange';
      default:
        return 'gray';
    }
  };

  // Get display name for notification type
  const getNotificationTypeName = (type) => {
    const displayNames = {
      lead_created: 'Lead Created',
      lead_assigned: 'Lead Assigned',
      lead_expired: 'Lead Expired',
      quote_sent: 'Quote Sent',
      quote_approved: 'Quote Approved',
      quote_declined: 'Quote Declined'
    };
    return displayNames[type] || 'System Notification';
  };

  // Group notifications by date
  const groupNotificationsByDate = () => {
    const grouped = {};
    
    notifications.forEach(notification => {
      const date = new Date(notification.created_at).toLocaleDateString();
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(notification);
    });
    
    return Object.entries(grouped).map(([date, items]) => ({
      date,
      items
    }));
  };

  const groupedNotifications = groupNotificationsByDate();

  return (
    <div className="notification-history">
      <Card className="notification-history-card">
        <Title level={3}>
          <BellOutlined /> Notification History
        </Title>
        
        {loading ? (
          <div className="notification-history-loading">
            <Spin size="large" />
          </div>
        ) : notifications.length === 0 ? (
          <Empty description="No notification history found" />
        ) : (
          <List
            dataSource={groupedNotifications}
            renderItem={group => (
              <List.Item className="notification-history-group">
                <div className="notification-history-date">
                  <Text strong>{group.date}</Text>
                </div>
                
                <Timeline className="notification-history-timeline">
                  {group.items.map(notification => (
                    <Timeline.Item 
                      key={notification.id}
                      color={getNotificationColor(notification.type)}
                      dot={getNotificationIcon(notification.type)}
                    >
                      <div className="notification-history-item">
                        <div className="notification-history-header">
                          <Tag color={getNotificationColor(notification.type)}>
                            {getNotificationTypeName(notification.type)}
                          </Tag>
                          <Text type="secondary" className="notification-history-time">
                            {new Date(notification.created_at).toLocaleTimeString()}
                          </Text>
                        </div>
                        
                        <div className="notification-history-content">
                          <Text strong>{notification.title}</Text>
                          <Text>{notification.message}</Text>
                        </div>
                        
                        <div className="notification-history-status">
                          {notification.read ? (
                            <Tag icon={<CheckCircleOutlined />} color="success">
                              Read
                            </Tag>
                          ) : (
                            <Tag icon={<ClockCircleOutlined />} color="warning">
                              Unread
                            </Tag>
                          )}
                        </div>
                      </div>
                    </Timeline.Item>
                  ))}
                </Timeline>
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
};

export default NotificationHistory;
