import React, { useState, useEffect } from 'react';
import { observer } from 'mobx-react-lite';
import ApiRequests from '../../../api/apiRequests';
import type { UserDTO } from '../../../models/User';
import type { DeclineReasonDTO } from '../../../models/DeclineReason';
import styles from './UserManagement.module.css';

const UserManagement: React.FC = observer(() => {
  const [pendingUsers, setPendingUsers] = useState<UserDTO[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [processingUsers, setProcessingUsers] = useState<Set<string>>(new Set());
  const [declineModal, setDeclineModal] = useState<{
    isOpen: boolean;
    userId: string;
    userName: string;
  }>({ isOpen: false, userId: '', userName: '' });
  const [declineReason, setDeclineReason] = useState('');

  const loadPendingUsers = async () => {
    try {
      setLoading(true);
      setError('');
      const response = await ApiRequests.getPendingUsers();
      setPendingUsers(response.data);
    } catch (err: any) {
      console.error('Failed to load pending users:', err);
      setError('Failed to load pending users. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPendingUsers();
  }, []);

  const handleApproveUser = async (userId: string) => {
    if (processingUsers.has(userId)) return;

    try {
      setProcessingUsers(prev => new Set(prev).add(userId));
      await ApiRequests.approveUser(userId);
      
      // Remove user from pending list
      setPendingUsers(prev => prev.filter(user => user.id !== userId));
      
      // Show success message (you could use a toast library here)
      console.log('User approved successfully');
    } catch (err: any) {
      console.error('Failed to approve user:', err);
      setError('Failed to approve user. Please try again.');
    } finally {
      setProcessingUsers(prev => {
        const newSet = new Set(prev);
        newSet.delete(userId);
        return newSet;
      });
    }
  };

  const handleDeclineUser = (userId: string, userName: string) => {
    setDeclineModal({
      isOpen: true,
      userId,
      userName
    });
  };

  const confirmDeclineUser = async () => {
    const { userId } = declineModal;
    if (!userId || processingUsers.has(userId)) return;

    try {
      setProcessingUsers(prev => new Set(prev).add(userId));
      
      const declineReasonDTO: DeclineReasonDTO = {
        reason: declineReason.trim() || undefined
      };
      
      await ApiRequests.declineUser(userId, declineReasonDTO);
      
      // Remove user from pending list
      setPendingUsers(prev => prev.filter(user => user.id !== userId));
      
      // Close modal and reset
      setDeclineModal({ isOpen: false, userId: '', userName: '' });
      setDeclineReason('');
      
      // Show success message
      console.log('User declined successfully');
    } catch (err: any) {
      console.error('Failed to decline user:', err);
      setError('Failed to decline user. Please try again.');
    } finally {
      setProcessingUsers(prev => {
        const newSet = new Set(prev);
        newSet.delete(userId);
        return newSet;
      });
    }
  };

  const cancelDeclineUser = () => {
    setDeclineModal({ isOpen: false, userId: '', userName: '' });
    setDeclineReason('');
  };

  const getFullName = (user: UserDTO) => {
    const { name, surname, patronymic } = user.name;
    return `${surname} ${name}${patronymic ? ` ${patronymic}` : ''}`.trim();
  };

  const getUserContact = (user: UserDTO) => {
    if (user.email) return user.email;
    if (user.telegramChatId) return `Telegram ID: ${user.telegramChatId}`;
    return 'No contact info';
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.header}>
          <h2 className={styles.title}>User Management</h2>
        </div>
        <div className={styles.loading}>Loading pending users...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>User Management</h2>
        <button 
          className={styles.refreshButton}
          onClick={loadPendingUsers}
          disabled={loading}
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className={styles.error}>
          {error}
        </div>
      )}
      
      {pendingUsers.length === 0 ? (
        <div className={styles.emptyState}>
          <h3>No Pending Users</h3>
          <p>All users have been processed. New registrations will appear here for approval.</p>
        </div>
      ) : (
        <div className={styles.usersList}>
          <h3>Pending User Approvals ({pendingUsers.length})</h3>
          
          <div className={styles.usersGrid}>
            {pendingUsers.map(user => (
              <div key={user.id} className={styles.userCard}>
                <div className={styles.userInfo}>
                  <h4 className={styles.userName}>{getFullName(user)}</h4>
                  <p className={styles.userContact}>{getUserContact(user)}</p>
                  <p className={styles.userRole}>Role: {user.role}</p>
                  {user.group && (
                    <p className={styles.userGroup}>Group: {user.group}</p>
                  )}
                </div>
                
                <div className={styles.userActions}>
                  <button
                    className={`${styles.approveButton} ${processingUsers.has(user.id) ? styles.processing : ''}`}
                    onClick={() => handleApproveUser(user.id)}
                    disabled={processingUsers.has(user.id)}
                  >
                    {processingUsers.has(user.id) ? 'Approving...' : 'Approve'}
                  </button>
                  
                  <button
                    className={`${styles.declineButton} ${processingUsers.has(user.id) ? styles.processing : ''}`}
                    onClick={() => handleDeclineUser(user.id, getFullName(user))}
                    disabled={processingUsers.has(user.id)}
                  >
                    {processingUsers.has(user.id) ? 'Declining...' : 'Decline'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Decline Reason Modal */}
      {declineModal.isOpen && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h3 className={styles.modalTitle}>
              Decline User: {declineModal.userName}
            </h3>
            
            <p className={styles.modalDescription}>
              You are about to decline this user's application. This action will permanently delete their account.
            </p>
            
            <div className={styles.formGroup}>
              <label htmlFor="declineReason" className={styles.label}>
                Reason for decline (optional):
              </label>
              <textarea
                id="declineReason"
                className={styles.textarea}
                value={declineReason}
                onChange={(e) => setDeclineReason(e.target.value)}
                placeholder="Enter reason for declining this user's application..."
                rows={4}
                maxLength={255}
              />
              <div className={styles.charCount}>
                {declineReason.length}/255 characters
              </div>
            </div>
            
            <div className={styles.modalActions}>
              <button
                className={styles.cancelButton}
                onClick={cancelDeclineUser}
                disabled={processingUsers.has(declineModal.userId)}
              >
                Cancel
              </button>
              <button
                className={styles.confirmDeclineButton}
                onClick={confirmDeclineUser}
                disabled={processingUsers.has(declineModal.userId)}
              >
                {processingUsers.has(declineModal.userId) ? 'Declining...' : 'Confirm Decline'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

export default UserManagement;
