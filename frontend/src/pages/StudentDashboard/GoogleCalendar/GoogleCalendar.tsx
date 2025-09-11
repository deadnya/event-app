import React, { useState, useEffect } from 'react';
import { observer } from 'mobx-react-lite';
import { googleCalendarApi } from '../../../api/apiRequests';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';
import styles from './GoogleCalendar.module.css';

const GoogleCalendar: React.FC = observer(() => {
    const [connected, setConnected] = useState(false);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        checkConnectionStatus();
    }, []);

    const checkConnectionStatus = async () => {
        try {
            setLoading(true);
            const response = await googleCalendarApi.getStatus();
            setConnected(response.data.connected);
        } catch (err: any) {
            console.error('Failed to check Google Calendar status:', err);
            setError('Failed to check Google Calendar status');
        } finally {
            setLoading(false);
        }
    };

    const handleConnect = async () => {
        try {
            setActionLoading(true);
            setError('');
            
            const response = await googleCalendarApi.getAuthUrl();
            
            if (response.data.error) {
                setError(response.data.error);
                setActionLoading(false);
                return;
            }

            if (!response.data.authUrl) {
                setError('Failed to get authorization URL');
                setActionLoading(false);
                return;
            }
            
            const authWindow = window.open(
                response.data.authUrl,
                'googleAuth',
                'width=500,height=600,scrollbars=yes,resizable=yes'
            );

            const checkClosed = setInterval(() => {
                if (authWindow?.closed) {
                    clearInterval(checkClosed);
                    setActionLoading(false);
                    setTimeout(() => {
                        checkConnectionStatus();
                    }, 1000);
                }
            }, 1000);

        } catch (err: any) {
            console.error('Failed to connect Google Calendar:', err);
            if (err.response?.data?.error) {
                setError(err.response.data.error);
            } else {
                setError('Failed to connect Google Calendar. Please check if the service is properly configured.');
            }
            setActionLoading(false);
        }
    };

    const handleDisconnect = async () => {
        if (!confirm('Are you sure you want to disconnect Google Calendar? This will remove all synced events.')) {
            return;
        }

        try {
            setActionLoading(true);
            setError('');
            
            await googleCalendarApi.disconnect();
            setConnected(false);
            
        } catch (err: any) {
            console.error('Failed to disconnect Google Calendar:', err);
            setError('Failed to disconnect Google Calendar');
        } finally {
            setActionLoading(false);
        }
    };

    if (loading) {
        return <LoadingSpinner />;
    }

    return (
        <div className={styles.container}>
            <div className={styles.header}>
                <h2 className={styles.title}>Google Calendar Integration</h2>
                <div className={styles.status}>
                    {connected ? (
                        <span className={styles.connectedBadge}>✅ Connected</span>
                    ) : (
                        <span className={styles.disconnectedBadge}>❌ Not Connected</span>
                    )}
                </div>
            </div>

            {error && (
                <div className={styles.error}>
                    {error}
                    {error.includes('not configured') && (
                        <div style={{ marginTop: '10px', fontSize: '0.9rem' }}>
                            <strong>For administrators:</strong> Please check the GOOGLE_CALENDAR_SETUP.md file 
                            for instructions on how to configure Google Calendar integration.
                        </div>
                    )}
                </div>
            )}

            <div className={styles.content}>
                {connected ? (
                    <div className={styles.connectedContent}>
                        <p className={styles.description}>
                            🎉 Your Google Calendar is connected! Events you register for will automatically 
                            appear in your Google Calendar, and will be removed when you unregister.
                        </p>
                        
                        <div className={styles.features}>
                            <h3>What's synced:</h3>
                            <ul>
                                <li>✅ Event name and description</li>
                                <li>✅ Event date and location</li>
                                <li>✅ Registration deadline information</li>
                                <li>✅ Automatic removal when unregistering</li>
                            </ul>
                        </div>

                        <button 
                            onClick={handleDisconnect}
                            className={styles.disconnectButton}
                            disabled={actionLoading}
                        >
                            {actionLoading ? 'Disconnecting...' : 'Disconnect Google Calendar'}
                        </button>
                    </div>
                ) : (
                    <div className={styles.disconnectedContent}>
                        <p className={styles.description}>
                            📅 Connect your Google Calendar to automatically sync event registrations! 
                            When you register for events, they'll appear in your Google Calendar.
                        </p>
                        
                        <div className={styles.benefits}>
                            <h3>Benefits:</h3>
                            <ul>
                                <li>🔄 Automatic event synchronization</li>
                                <li>📱 Access events on all your devices</li>
                                <li>⏰ Get Google Calendar notifications</li>
                                <li>🗓️ See events alongside your other appointments</li>
                            </ul>
                        </div>

                        <button 
                            onClick={handleConnect}
                            className={styles.connectButton}
                            disabled={actionLoading}
                        >
                            {actionLoading ? 'Connecting...' : 'Connect Google Calendar'}
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
});

export default GoogleCalendar;
