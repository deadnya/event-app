import React, { useState, useEffect } from 'react';
import { observer } from 'mobx-react-lite';
import { useStore } from '../../store/StoreContext';
import type { TelegramLoginRequestDTO } from '../../models/Auth';
import { TELEGRAM_CONFIG } from '../../config/telegram';
import styles from './LoginPage.module.css';

declare global {
    interface Window {
        onTelegramAuth?: (user: any) => void;
    }
}

const LoginPage: React.FC = observer(() => {
    const store = useStore();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [showFallback, setShowFallback] = useState(false);

    useEffect(() => {
        window.onTelegramAuth = handleTelegramAuth;

        loadTelegramWidget();

        return () => {
            if (window.onTelegramAuth) {
                window.onTelegramAuth = undefined as any;
            }
        };
    }, []);

    const loadTelegramWidget = () => {
        const existingScript = document.getElementById('telegram-widget-script');
        if (existingScript) {
            existingScript.remove();
        }

        const existingWidget = document.getElementById('telegram-login-widget');
        if (existingWidget) {
            existingWidget.innerHTML = '';
        }

        if (TELEGRAM_CONFIG.BOT_USERNAME === 'YourBotUsername') {
            const widgetContainer = document.getElementById('telegram-login-widget');
            if (widgetContainer) {
                widgetContainer.innerHTML = `
                <div style="color: #e74c3c; text-align: center; padding: 20px;">
                    <p><strong>Telegram Bot Not Configured</strong></p>
                    <p>Please configure your Telegram bot username in src/config/telegram.ts</p>
                </div>
                `;
            }

            return;
        }

        const script = document.createElement('script');
        script.id = 'telegram-widget-script';
        script.async = true;
        script.src = 'https://telegram.org/js/telegram-widget.js?22';
        script.setAttribute('data-telegram-login', TELEGRAM_CONFIG.BOT_USERNAME);
        script.setAttribute('data-size', TELEGRAM_CONFIG.WIDGET_SIZE);
        script.setAttribute('data-onauth', 'onTelegramAuth(user)');
        script.setAttribute('data-request-access', TELEGRAM_CONFIG.REQUEST_ACCESS);

        const timeout = setTimeout(() => {
            setShowFallback(true);
        }, 10000);

        script.onload = () => {
            clearTimeout(timeout);
            console.log('Telegram widget script loaded successfully');
            
            setTimeout(() => {
                const widgetContainer = document.getElementById('telegram-login-widget');
                const iframe = widgetContainer?.querySelector('iframe');
                if (!iframe) {
                    console.warn('Telegram widget iframe not found, showing fallback');
                    setShowFallback(true);
                }
            }, 2000);
        };

        script.onerror = () => {
            clearTimeout(timeout);
            console.error('Failed to load Telegram widget script');
            const widgetContainer = document.getElementById('telegram-login-widget');
            if (widgetContainer) {
                widgetContainer.innerHTML = `
                    <div style="color: #e74c3c; text-align: center; padding: 20px;">
                        <p><strong>Failed to load Telegram widget</strong></p>
                        <p>This might be due to Content Security Policy restrictions.</p>
                        <button id="fallback-telegram-btn" style="
                        background: #0088cc; 
                        color: white; 
                        border: none; 
                        padding: 10px 20px; 
                        border-radius: 4px; 
                        cursor: pointer; 
                        margin-top: 10px;
                        font-size: 14px;
                        ">Login with Telegram (Alternative)</button>
                    </div>
                `;
                
                const fallbackBtn = document.getElementById('fallback-telegram-btn');
                if (fallbackBtn) {
                    fallbackBtn.onclick = () => {
                        setShowFallback(true);
                        handleFallbackTelegramLogin();
                    };
                }
            }
        };

        const widgetContainer = document.getElementById('telegram-login-widget');
        if (widgetContainer) {
            widgetContainer.appendChild(script);
        }
    };

    const handleTelegramAuth = async (user: any) => {
        setError('');
        
        try {
            const telegramData: TelegramLoginRequestDTO = {
                id: user.id,
                firstName: user.first_name,
                lastName: user.last_name || undefined,
                username: user.username || undefined,
                authDate: user.auth_date,
                hash: user.hash
            };

            await store.loginWithTelegram(telegramData);
        } catch (err: any) {
            console.error('Telegram login error:', err);

            if (err.response?.status === 401) {
                setError('Telegram authentication failed. Please try again.');
            } else if (err.response?.status === 403) {
                setError('Your account is not approved yet. Please wait for admin approval.');
            } else {
                setError('Login failed. Please try again.');
            }
        }
    };

    const handleFallbackTelegramLogin = () => {
        const message = `Whoops!!! Fallback option is not yet implemented!!!`;
        
        alert(message);
    };

    const handleEmailLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        try {
            await store.login(email, password);
        } catch (err: any) {
            console.error('Login error:', err);

            if (err.response?.status === 401) {
                setError('Invalid email or password');
            } else {
                setError('Login failed. Please try again.');
            }
        }
    };

    return (
        <div className={styles.container}>
            <div className={styles.loginBox}>
                <h1 className={styles.title}>Event Management System</h1>
                
                <form onSubmit={handleEmailLogin} className={styles.form}>
                    <div className={styles.inputGroup}>
                        <label htmlFor="email" className={styles.label}>Email</label>
                        <input
                            type="email"
                            id="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className={styles.input}
                            required
                            disabled={store.isLoading}
                        />
                    </div>
                    
                    <div className={styles.inputGroup}>
                        <label htmlFor="password" className={styles.label}>Password</label>
                        <input
                            type="password"
                            id="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className={styles.input}
                            required
                            disabled={store.isLoading}
                        />
                    </div>

                    <button 
                        type="submit" 
                        className={styles.loginButton}
                        disabled={store.isLoading}
                    >
                        {store.isLoading ? 'Logging in...' : 'Log in'}
                    </button>
                </form>

                <div className={styles.separator}>
                    <span className={styles.separatorText}>or</span>
                </div>

                <div className={styles.telegramLogin}>
                    <div className={styles.telegramWidgetContainer}>
                        <div id="telegram-login-widget" className={styles.telegramWidget}></div>
                    </div>

                    {showFallback && (
                        <div className={styles.fallbackContainer}>
                            <button 
                                onClick={handleFallbackTelegramLogin}
                                className={styles.fallbackButton}
                            >
                                Alternative Telegram Login
                            </button>
                        </div>
                    )}

                    <div className={styles.telegramInfo}>
                        <p className={styles.infoText}>
                            <strong>Note:</strong> If you haven't registered yet, please use the Telegram bot to register first.
                        </p>
                    </div>
                </div>

                {error && <div className={styles.error}>{error}</div>}
            </div>
        </div>
    );
});

export default LoginPage;
