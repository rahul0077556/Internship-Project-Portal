import React, { useState, useEffect } from 'react';
import { messageService } from '@/services/messageService';
import { Message } from '@/types';

const Messages: React.FC = () => {
  const [conversations, setConversations] = useState<any[]>([]);
  const [selectedConversation, setSelectedConversation] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (selectedConversation) {
      loadMessages(selectedConversation);
    }
  }, [selectedConversation]);

  const loadConversations = async () => {
    try {
      const data = await messageService.getConversations();
      setConversations(data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadMessages = async (userId: number) => {
    try {
      const data = await messageService.getAll(userId);
      setMessages(data);
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const handleSend = async () => {
    if (!selectedConversation || !newMessage.trim()) return;

    try {
      await messageService.send(selectedConversation, newMessage);
      setNewMessage('');
      loadMessages(selectedConversation);
    } catch (error: any) {
      alert(error.response?.data?.error || 'Failed to send message');
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div style={styles.container}>
      <h1>Messages</h1>
      <div style={styles.layout}>
        <div style={styles.sidebar}>
          {conversations.map((conv) => (
            <div
              key={conv.user.id}
              style={{
                ...styles.conversation,
                ...(selectedConversation === conv.user.id ? styles.selected : {}),
              }}
              onClick={() => setSelectedConversation(conv.user.id)}
            >
              <h3>{conv.user.email}</h3>
              {conv.last_message && (
                <p style={styles.preview}>{conv.last_message.content.substring(0, 50)}...</p>
              )}
              {conv.unread_count > 0 && (
                <span className="badge badge-danger">{conv.unread_count}</span>
              )}
            </div>
          ))}
        </div>
        <div style={styles.main}>
          {selectedConversation ? (
            <>
              <div style={styles.messages}>
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    style={{
                      ...styles.message,
                      ...(msg.sender_id === selectedConversation ? styles.received : styles.sent),
                    }}
                  >
                    <p>{msg.content}</p>
                    <small>{new Date(msg.created_at!).toLocaleString()}</small>
                  </div>
                ))}
              </div>
              <div style={styles.inputArea}>
                <textarea
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Type a message..."
                  rows={3}
                  style={styles.textarea}
                />
                <button className="btn btn-primary" onClick={handleSend}>
                  Send
                </button>
              </div>
            </>
          ) : (
            <div style={styles.placeholder}>Select a conversation to start messaging</div>
          )}
        </div>
      </div>
    </div>
  );
};

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    height: 'calc(100vh - 200px)',
  },
  layout: {
    display: 'flex',
    height: '100%',
    gap: '1rem',
  },
  sidebar: {
    width: '300px',
    border: '1px solid #e2e8f0',
    borderRadius: '0.5rem',
    overflowY: 'auto',
    padding: '1rem',
  },
  conversation: {
    padding: '1rem',
    cursor: 'pointer',
    borderRadius: '0.5rem',
    marginBottom: '0.5rem',
    border: '1px solid #e2e8f0',
  },
  selected: {
    background: '#f0f9ff',
    borderColor: '#2563eb',
  },
  preview: {
    color: '#64748b',
    fontSize: '0.875rem',
    marginTop: '0.5rem',
  },
  main: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    border: '1px solid #e2e8f0',
    borderRadius: '0.5rem',
    padding: '1rem',
  },
  messages: {
    flex: 1,
    overflowY: 'auto',
    marginBottom: '1rem',
  },
  message: {
    padding: '1rem',
    borderRadius: '0.5rem',
    marginBottom: '1rem',
    maxWidth: '70%',
  },
  sent: {
    background: '#2563eb',
    color: 'white',
    marginLeft: 'auto',
  },
  received: {
    background: '#f1f5f9',
    color: '#1e293b',
  },
  inputArea: {
    display: 'flex',
    gap: '1rem',
  },
  textarea: {
    flex: 1,
    padding: '0.75rem',
    border: '1px solid #cbd5e1',
    borderRadius: '0.5rem',
  },
  placeholder: {
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    height: '100%',
    color: '#64748b',
  },
};

export default Messages;

