import React from 'react';
import { useStore } from '../../store/StoreContext';
import styles from './ErrorPage.module.css';

interface ErrorPageProps {
    message?: string;
}

const ErrorPage: React.FC<ErrorPageProps> = ({ message = 'An error occurred' }) => {
    const store = useStore();

    const handleLogout = async () => {
        await store.logout();
    };

    return (
        <div className={styles.container}>
            <div className={styles.errorBox}>
                <h1 className={styles.title}>Oops!</h1>
                <p className={styles.message}>{message}</p>
                <button 
                    onClick={handleLogout}
                    className={styles.logoutButton}
                >
                    Back to Login
                </button>
            </div>
        </div>
    );
};

export default ErrorPage;
