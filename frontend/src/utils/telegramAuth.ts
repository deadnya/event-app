import type { TelegramLoginRequestDTO } from '../models/Auth';

export const createTelegramLoginButton = (
    botUsername: string,
    onAuth: (user: TelegramLoginRequestDTO) => void,
    size: 'small' | 'medium' | 'large' = 'large'
) => {
    const sizes = {
        small: { width: 186, height: 28, fontSize: 12 },
        medium: { width: 230, height: 38, fontSize: 14 },
        large: { width: 244, height: 40, fontSize: 16 }
    };

    const buttonSize = sizes[size];

    const createButton = () => {
        const button = document.createElement('iframe');
        button.src = `https://oauth.telegram.org/auth?bot_id=${botUsername}&origin=${encodeURIComponent(window.location.origin)}&size=${size}&request_access=write`;
        button.width = buttonSize.width.toString();
        button.height = buttonSize.height.toString();
        button.frameBorder = '0';
        button.scrolling = 'no';
        button.style.border = 'none';
        button.style.borderRadius = '6px';
        button.style.overflow = 'hidden';

        const handleMessage = (event: MessageEvent) => {
        if (event.origin !== 'https://oauth.telegram.org') return;
        
        if (event.data && event.data.event === 'auth_result') {
            const userData = event.data.result;
            if (userData) {
                const telegramData: TelegramLoginRequestDTO = {
                    id: userData.id,
                    firstName: userData.first_name,
                    lastName: userData.last_name,
                    username: userData.username,
                    authDate: userData.auth_date,
                    hash: userData.hash
                };
                onAuth(telegramData);
            }
        }
        };

        window.addEventListener('message', handleMessage);

        return {
            element: button,
            cleanup: () => window.removeEventListener('message', handleMessage)
        };
    };

    return createButton;
};

export const getTelegramOAuthUrl = (botUsername: string, redirectUrl?: string) => {
    const baseUrl = 'https://oauth.telegram.org/auth';
    const params = new URLSearchParams({
        bot_id: botUsername,
        origin: window.location.origin,
        request_access: 'write',
        return_to: redirectUrl || window.location.href
    });

    return `${baseUrl}?${params.toString()}`;
};
