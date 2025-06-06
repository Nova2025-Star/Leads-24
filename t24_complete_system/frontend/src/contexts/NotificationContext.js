import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';
import { useAuth } from './AuthContext';

const NotificationContext = createContext();

export const useNotifications = () => useContext(NotificationContext);

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [preferences, setPreferences] = useState({
    email: true,
    inApp: true,
    push: false,
    sms: false
  });
  const [loading, setLoading] = useState(false);
  const { currentUser, token } = useAuth();

  // Fetch notifications for the current user
  const fetchNotifications = async () => {
    if (!currentUser || !token) return;
    
    setLoading(true);
    try {
      const response = await axios.get(`/api/v1/notifications/user/${currentUser.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setNotifications(response.data);
      setUnreadCount(response.data.filter(notif => !notif.read).length);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mark a notification as read
  const markAsRead = async (notificationId) => {
    if (!token) return;
    
    try {
      await axios.post(`/api/v1/notifications/read/${notificationId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setNotifications(notifications.map(notif => 
        notif.id === notificationId ? { ...notif, read: true } : notif
      ));
      
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  // Mark all notifications as read
  const markAllAsRead = async () => {
    if (!token || !currentUser) return;
    
    try {
      const unreadIds = notifications.filter(notif => !notif.read).map(notif => notif.id);
      
      for (const id of unreadIds) {
        await axios.post(`/api/v1/notifications/read/${id}`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      
      setNotifications(notifications.map(notif => ({ ...notif, read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  // Fetch notification preferences
  const fetchPreferences = async () => {
    if (!currentUser || !token) return;
    
    try {
      const response = await axios.get(`/api/v1/notifications/preferences/${currentUser.id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setPreferences(response.data);
    } catch (error) {
      console.error('Error fetching notification preferences:', error);
    }
  };

  // Update notification preferences
  const updatePreferences = async (newPreferences) => {
    if (!currentUser || !token) return;
    
    try {
      await axios.post('/api/v1/notifications/preferences', {
        user_id: currentUser.id,
        ...newPreferences
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setPreferences(newPreferences);
    } catch (error) {
      console.error('Error updating notification preferences:', error);
    }
  };

  // Poll for new notifications every 30 seconds
  useEffect(() => {
    if (!currentUser) return;
    
    fetchNotifications();
    fetchPreferences();
    
    const interval = setInterval(fetchNotifications, 30000);
    
    return () => clearInterval(interval);
  }, [currentUser, token, fetchNotifications, fetchPreferences]);

  const value = {
    notifications,
    unreadCount,
    preferences,
    loading,
    fetchNotifications,
    markAsRead,
    markAllAsRead,
    updatePreferences
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
};

export default NotificationContext;
