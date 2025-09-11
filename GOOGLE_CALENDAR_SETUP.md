# Google Calendar Integration Setup

## Overview
The application includes Google Calendar integration that allows students to automatically sync their event registrations to their personal Google Calendar.

## Prerequisites
1. A Google Cloud Project
2. Google Calendar API enabled
3. OAuth 2.0 credentials configured

## Setup Instructions

### 1. Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Note your project ID

### 2. Enable the Google Calendar API
1. In the Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

### 3. Create OAuth 2.0 Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client IDs"
3. If prompted, configure the OAuth consent screen first:
   - Choose "External" user type (for testing) or "Internal" (for organization use)
   - Fill in the required fields (App name, User support email, Developer contact information)
   - Add your domain to authorized domains if needed
   - Add the following scopes: `../auth/calendar`
   - **Important**: If using "External" type, add test users in the "Test users" section
4. For the OAuth 2.0 Client ID:
   - Application type: "Web application"
   - Name: "Event Management System" (or your preferred name)
   - Authorized JavaScript origins: 
     - `http://localhost:3000` (for development)
     - Your production domain (e.g., `https://yourdomain.com`)
   - Authorized redirect URIs:
     - `http://localhost:3000/google-calendar/callback` (for development)
     - `https://yourdomain.com/google-calendar/callback` (for production)

### 4. Configure Environment Variables
1. Copy `.env.example` to `.env` in the project root
2. Update the following variables with your Google OAuth credentials:
   ```bash
   GOOGLE_CLIENT_ID=your_client_id_from_google_cloud_console
   GOOGLE_CLIENT_SECRET=your_client_secret_from_google_cloud_console
   GOOGLE_REDIRECT_URI=http://localhost:3000/google-calendar/callback
   ```

### 5. Testing Setup
1. Make sure your `.env` file has the correct Google Calendar credentials
2. Start the application: `docker-compose up`
3. Log in as a student
4. Navigate to "Google Calendar" in the student dashboard
5. Click "Connect to Google Calendar"
6. You should be redirected to Google's OAuth consent screen

## Features

### For Students
- **Connect Google Calendar**: Link their Google account to automatically sync events
- **Automatic Event Creation**: When registering for an event, it's automatically added to their Google Calendar
- **Automatic Event Removal**: When unregistering from an event, it's automatically removed from their Google Calendar
- **Connection Management**: View connection status and disconnect if needed

### Technical Details
- **OAuth 2.0 Flow**: Secure authentication using Google's OAuth 2.0
- **Token Management**: Access and refresh tokens are securely stored
- **Event Synchronization**: Events are created with proper titles, descriptions, and timing
- **Error Handling**: Graceful handling of API errors and token expiration

## API Endpoints

### Google Calendar Integration
- `GET /api/google-calendar/auth-url` - Get OAuth authorization URL
- `POST /api/google-calendar/callback` - Handle OAuth callback
- `DELETE /api/google-calendar/disconnect` - Disconnect Google Calendar
- `GET /api/google-calendar/status` - Check connection status

## Troubleshooting

### Common Issues

#### "Missing required parameter: client_id"
- Ensure `GOOGLE_CLIENT_ID` is set in your `.env` file
- Verify the client ID is correct (no extra spaces or characters)

#### "Access blocked: EventManager has not completed the Google verification process"
- Your app is in testing mode and the user is not in the test users list
- Go to Google Cloud Console > APIs & Services > OAuth consent screen
- Add the user's email to the "Test users" section
- Alternatively, change User Type to "Internal" if using Google Workspace

#### "Error 403: access_denied"
- Same as above - add the user as a test user
- Verify that the redirect URI in Google Cloud Console matches exactly: `http://localhost:3000/google-calendar/callback`

#### "Invalid client_secret"
- Double-check the `GOOGLE_CLIENT_SECRET` in your `.env` file
- Regenerate the client secret in Google Cloud Console if needed

#### Events not syncing
- Check that the user has properly connected their Google Calendar
- Verify that the Calendar API quota hasn't been exceeded
- Check application logs for any API errors

### Security Considerations
- Never commit the `.env` file to version control
- Use HTTPS in production
- Regularly rotate OAuth client secrets
- Monitor API usage and quotas
- Implement proper error handling for token expiration

## Development Notes
- The integration uses Google's Calendar API v3
- Tokens are automatically refreshed when possible
- Events are created in the user's primary calendar
- Event titles follow the format: "Event: [Event Name]"
- Event descriptions include location and company information
