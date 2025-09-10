# Telegram Bot Structure

This refactored Telegram bot follows a modular architecture for better maintainability and extensibility.

## Project Structure

```
telegram/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── bot/                       # Main bot package
│   ├── __init__.py
│   ├── config.py             # Configuration and constants
│   ├── telegram_bot.py       # Main bot class
│   ├── handlers/             # Command handlers
│   │   ├── __init__.py
│   │   ├── base_handler.py   # Base class for all handlers
│   │   ├── general_handler.py # General commands (start, help, status)
│   │   ├── registration_handler.py # User registration flow
│   │   ├── student_handler.py # Student-specific commands
│   │   └── manager_handler.py # Manager-specific commands
│   ├── services/             # External service integrations
│   │   ├── __init__.py
│   │   └── api_service.py    # Backend API service
│   ├── models/               # Data models
│   │   ├── __init__.py
│   │   └── registration.py   # Registration data model
│   └── utils/                # Utility modules
│       ├── __init__.py
│       └── logger.py         # Logging configuration
└── logs/
    └── bot.log               # Log files
```

## Key Features

### Modular Architecture
- **Handlers**: Separate handlers for different user roles and functionalities
- **Services**: External API integrations (backend communication)
- **Models**: Data models for type safety and validation
- **Utils**: Common utilities like logging

### Role-Based Commands
- **General**: Available to all users (start, help, status, register)
- **Student**: Commands specific to students (view events, register for events)
- **Manager**: Commands specific to managers (create events, manage participants)

### Extensible Design
- Easy to add new commands for each role
- Base handler provides common functionality
- Service layer abstracts API calls

## Available Commands

### General Commands (All Users)
- `/start` - Welcome message with automatic authentication attempt
- `/help` - Show available commands (dynamic based on authentication status)
- `/status` - Check registration and approval status
- `/register` - Start registration process
- `/backend_health` - Check backend system health

### Student Commands (Auto-authenticated when needed)
- `/student_help` - Show student-specific help
- `/my_events` - View your registered events
- `/available_events` - View available events for registration
- `/register_event <event_id>` - Register for an event using its ID
- `/unregister_event <event_id>` - Unregister from an event using its ID

### Manager Commands (Auto-authenticated when needed)
- `/manager_help` - Show manager-specific help
- `/my_company_events` - View events managed by your company
- `/create_event` - Create a new event (placeholder for conversation flow)
- `/edit_event` - Edit an existing event (placeholder for conversation flow)
- `/delete_event <event_id>` - Delete an event by ID
- `/event_participants <event_id>` - View participants of an event by ID

## Seamless Authentication System

The bot now features **automatic authentication** - no manual login/logout commands needed!

### How It Works:
1. **Smart Detection**: When a user tries to use any role-specific command, the bot automatically checks if they need authentication
2. **Auto-Login**: If the user is registered and approved, the bot automatically authenticates them using Telegram's secure authentication
3. **Transparent Experience**: Users don't need to think about logging in - it happens seamlessly in the background
4. **Clear Feedback**: If authentication fails, users get clear messages about what they need to do (register, wait for approval, etc.)

### Authentication Flow:
1. **User Registration**: `/register` command creates account (no authentication yet)
2. **Admin Approval**: Admin approves the user in backend system
3. **Automatic Authentication**: When user tries any authenticated command:
   - Bot checks if user has valid tokens
   - If not, automatically attempts Telegram authentication
   - Creates HMAC signature using bot token
   - Calls backend `/auth/telegram-login` endpoint
   - Stores tokens locally for future use
4. **Seamless Access**: User gets immediate access to their role-specific features

### User Experience Benefits:
- **No Extra Steps**: Users don't need to remember to login
- **Immediate Access**: Approved users get instant access to features
- **Clear Guidance**: Unapproved users get helpful next-step messages
- **Persistent Sessions**: Tokens are managed automatically in background

### Technical Benefits:
- **Automatic Token Refresh**: Access tokens refresh automatically when expired
- **Secure Token Storage**: JWT tokens stored securely with proper cleanup
- **Role-Based Access**: Commands automatically check authentication and roles
- **Error Handling**: Comprehensive error handling with user-friendly messages

## Adding New Commands

### For Students
1. Add the command method to `student_handler.py`
2. Register the command in `telegram_bot.py` setup_handlers method
3. Add appropriate role and approval checks

### For Managers
1. Add the command method to `manager_handler.py`
2. Register the command in `telegram_bot.py` setup_handlers method
3. Add appropriate role and approval checks

### Example: Adding a new student command
```python
# In student_handler.py
async def new_student_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    await self.log_command_usage(update, "new_student_command")
    
    user_id = update.effective_user.id
    if await self.check_user_role(user_id) != STUDENT_ROLE:
        await update.message.reply_text("❌ This command is only available for students.")
        return
    
    if not await self.is_user_approved(user_id):
        await update.message.reply_text("❌ Your account is not approved yet.")
        return
    
    # Your command logic here
    await update.message.reply_text("Command executed!")

# In telegram_bot.py setup_handlers method
self.application.add_handler(CommandHandler("new_student_command", self.student_handler.new_student_command))
```

## Configuration

Environment variables are loaded in `config.py`:
- `TELEGRAM_BOT_TOKEN`: Bot token from BotFather
- `API_BASE_URL`: Backend API base URL (default: http://backend:8080/api)

## Error Handling

- Comprehensive error handling in API service
- Logging for debugging and monitoring
- User-friendly error messages
- Graceful fallbacks for network issues

## Future Enhancements

- Add conversation handlers for complex workflows (event creation, editing)
- Implement inline keyboards for better user experience
- Add caching for frequently accessed data
- Implement user session management
- Add metrics and monitoring
