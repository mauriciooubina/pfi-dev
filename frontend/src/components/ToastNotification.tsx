import React from 'react';
import { CheckCircle2 } from 'lucide-react';

interface ToastNotificationProps {
  message: string | null;
}

export const ToastNotification: React.FC<ToastNotificationProps> = ({ message }) => {
  if (!message) return null;

  return (
    <div style={{
      position: 'fixed',
      bottom: '24px',
      right: '24px',
      background: 'rgba(15, 23, 42, 0.95)',
      color: '#f8fafc',
      border: '1px solid var(--primary)',
      padding: '14px 20px',
      borderRadius: '12px',
      boxShadow: '0 10px 25px -5px rgba(79, 70, 229, 0.4)',
      zIndex: 9999,
      fontFamily: 'inherit',
      fontSize: '0.9rem',
      fontWeight: 600,
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      animation: 'fadeIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
    }}>
      <CheckCircle2 size={18} style={{ color: 'var(--success)' }} />
      <span>{message}</span>
    </div>
  );
};
