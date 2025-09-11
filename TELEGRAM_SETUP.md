# Telegram Login Widget Setup

## Important: Domain Configuration

The Telegram Login Widget has strict requirements for local development:

1. **Use `http://127.0.0.1:80` - NEVER `http://localhost`**
2. **Must use port 80**

This is the only way to test the Telegram Login Widget locally.

## Setup Steps

1. **Configure your Telegram bot domain:**
   ```
   /setdomain http://127.0.0.1:80
   ```
   Send this command to @BotFather for your bot.

2. **Start the application:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://127.0.0.1
   - Backend API: http://127.0.0.1:8080/api

## Configuration

Make sure your `.env` file has:
```
VITE_API_URL=http://127.0.0.1:8080/api
```

And your `src/config/telegram.ts` has your bot username:
```typescript
export const TELEGRAM_CONFIG = {
  BOT_USERNAME: 'your_bot_username',
  // ... other config
};
```

## Troubleshooting

- If you get "Bot domain invalid", make sure you've set the domain with @BotFather
- If the widget doesn't load, check browser console for CSP errors
- Make sure Docker containers are running on the correct ports (80 and 8080)
