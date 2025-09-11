import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { googleCalendarApi } from '../../../api/apiRequests';
import LoadingSpinner from '../../../components/LoadingSpinner/LoadingSpinner';
import styles from './GoogleCalendarCallback.module.css';

const GoogleCalendarCallback: React.FC = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
    const [errorMessage, setErrorMessage] = useState<string>('');

    useEffect(() => {
        const handleCallback = async () => {
            const code = searchParams.get('code');
            const error = searchParams.get('error');

            if (error) {
                setErrorMessage(`Authorization failed: ${error}`);
                setStatus('error');
                return;
            }

            if (!code) {
                setErrorMessage('No authorization code received');
                setStatus('error');
                return;
            }

            try {
                await googleCalendarApi.handleCallback(code);
                setStatus('success');
                
                setTimeout(() => {
                    navigate('/student/google-calendar');
                }, 2000);
            } catch (error) {
                console.error('Failed to complete Google Calendar authorization:', error);
                setErrorMessage('Failed to complete authorization. Please try again.');
                setStatus('error');
            }
        };

        handleCallback();
    }, [searchParams, navigate]);

    const handleRetry = () => {
        navigate('/student/google-calendar');
    };

    return (
        <div className={styles.container}>
            <div className={styles.content}>
                {status === 'loading' && (
                    <div className={styles.loadingSection}>
                        <LoadingSpinner />
                        <h2>Connecting to Google Calendar...</h2>
                        <p>Please wait while we complete the authorization process.</p>
                    </div>
                )}

                {status === 'success' && (
                    <div className={styles.successSection}>
                        <div className={styles.successIcon}>✅</div>
                        <h2>Successfully Connected!</h2>
                        <p>Your Google Calendar has been connected successfully.</p>
                        <p>You will be redirected to the Google Calendar settings page in a moment...</p>
                    </div>
                )}

                {status === 'error' && (
                    <div className={styles.errorSection}>
                        <div className={styles.errorIcon}>❌</div>
                        <h2>Connection Failed</h2>
                        <p className={styles.errorMessage}>{errorMessage}</p>
                        <button 
                            className={styles.retryButton}
                            onClick={handleRetry}
                        >
                            Back to Google Calendar Settings
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default GoogleCalendarCallback;
