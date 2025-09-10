# HITS Task Project - Docker Setup

This project consists of three main components:
1. **Backend**: Java Spring Boot application
2. **Frontend**: React TypeScript application with Vite
3. **Telegram Bot**: Python-based Telegram bot

## Prerequisites

- Docker
- Docker Compose
- Git

## Quick Start

1. **Clone the repository and navigate to project directory**
   ```bash
   cd hits_task
   ```

2. **Copy environment file and configure**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your actual values:
   - Set a strong database password
   - Add your Telegram bot token (get from @BotFather on Telegram)
   - Adjust other settings as needed

3. **Build and start all services**
   ```bash
   docker-compose up --build
   ```

4. **Access the applications**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8080
   - Database: localhost:5432

## Individual Service Management

### Start specific services
```bash
# Start only database and backend
docker-compose up db backend

# Start frontend in development mode
docker-compose up frontend
```

### View logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs telegram-bot
```

### Stop services
```bash
docker-compose down
```

### Rebuild after changes
```bash
# Rebuild all
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

## Development

### Backend Development
- Logs are mounted to `./backend/logs/`
- The application uses PostgreSQL database
- Health check available at: http://localhost:8080/actuator/health

### Frontend Development
- Built with Vite and served with Nginx
- API calls are proxied through Nginx to backend
- Environment variables can be set via `VITE_` prefix

### Telegram Bot Development
- Logs are mounted to `./telegram/logs/`
- Bot connects to backend API for data operations
- Uses python-telegram-bot library

## Environment Variables

### Main .env file
- `DB_NAME`: Database name
- `DB_USER`: Database username  
- `DB_PASSWORD`: Database password
- `VITE_API_URL`: Frontend API URL
- `TELEGRAM_BOT_TOKEN`: Bot token from @BotFather
- `API_BASE_URL`: Backend API URL for telegram bot

### Getting Telegram Bot Token
1. Message @BotFather on Telegram
2. Use `/newbot` command
3. Follow instructions to create your bot
4. Copy the provided token to your `.env` file

## Database

The project uses PostgreSQL database with persistent storage.

### Database Connection
- Host: localhost (from host machine) or `db` (from containers)
- Port: 5432
- Database: Value from `DB_NAME` env var
- Username: Value from `DB_USER` env var
- Password: Value from `DB_PASSWORD` env var

### Access Database
```bash
# Connect to database container
docker-compose exec db psql -U hits_user -d hits_task_db
```

## Troubleshooting

### Common Issues

1. **Port already in use**
   - Check if ports 3000, 8080, or 5432 are already in use
   - Stop other services or modify ports in docker-compose.yml

2. **Database connection failed**
   - Ensure database service is running: `docker-compose ps`
   - Check database credentials in .env file

3. **Telegram bot not responding**
   - Verify TELEGRAM_BOT_TOKEN is correct
   - Check bot logs: `docker-compose logs telegram-bot`
   - Ensure backend is running and accessible

4. **Frontend can't reach backend**
   - Check VITE_API_URL in .env file
   - Verify backend is running on correct port

### Reset Everything
```bash
# Stop all containers and remove data
docker-compose down -v

# Remove all images
docker-compose down --rmi all

# Start fresh
docker-compose up --build
```

## Production Deployment

For production deployment:

1. Use production environment variables
2. Set up proper SSL certificates
3. Configure proper logging and monitoring
4. Use Docker secrets for sensitive data
5. Set up backup strategy for database
6. Configure proper firewall rules

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React+Vite)  │────│  (Spring Boot)  │────│  (PostgreSQL)   │
│   Port: 3000    │    │   Port: 8080    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                │
                       ┌─────────────────┐
                       │  Telegram Bot   │
                       │   (Python)      │
                       └─────────────────┘
```

All services communicate through Docker network `hits-network`.
