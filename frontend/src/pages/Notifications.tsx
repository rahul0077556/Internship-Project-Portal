import React, { useState, useEffect } from 'react';
import { notificationService } from '@/services/notificationService';
import { Notification } from '@/types';

const Notifications: React.FC = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const data = await notificationService.getAll();
      setNotifications(data);
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleMarkAsRead = async (id: number) => {
    try {
      await notificationService.markAsRead(id);
      loadNotifications();
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      loadNotifications();
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div>
      <div style={styles.header}>
        <h1>Notifications</h1>
        {notifications.some(n => !n.is_read) && (
          <button className="btn btn-secondary" onClick={handleMarkAllAsRead}>
            Mark All as Read
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div className="card">
          <p>No notifications</p>
        </div>
      ) : (
        <div>
          {notifications.map((notif) => (
            <div
              key={notif.id}
              className="card"
              style={{
                ...styles.card,
                ...(notif.is_read ? {} : styles.unread),
              }}
              onClick={() => !notif.is_read && handleMarkAsRead(notif.id)}
            >
              <div style={styles.cardHeader}>
                <h3>{notif.title}</h3>
                {!notif.is_read && <span className="badge badge-info">New</span>}
              </div>
              <p>{notif.message}</p>
              <small>{new Date(notif.created_at!).toLocaleString()}</small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2rem',
  },
  card: {
    marginBottom: '1rem',
    cursor: 'pointer',
  },
  unread: {
    background: '#f0f9ff',
    borderLeft: '4px solid #2563eb',
  },
  cardHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '0.5rem',
  },
};

export default Notifications;

