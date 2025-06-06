# Installation Guide

This document provides detailed instructions for installing and setting up the T24 Arborist Lead System.

## Prerequisites

Before installing the system, ensure you have the following prerequisites:

- **Docker**: Version 20.10.0 or higher
- **Docker Compose**: Version 2.0.0 or higher
- **Internet connection**: Required for pulling Docker images
- **Minimum system requirements**:
  - 2 CPU cores
  - 4GB RAM
  - 10GB free disk space

## Installation Steps

### 1. Extract the Package

Extract the zip file to your preferred location:

```bash
unzip t24_arborist_lead_system.zip -d /path/to/destination
cd /path/to/destination
```

### 2. Configure Environment Variables

The system comes with a default `.env` file with basic configuration. Review and modify this file as needed:

```bash
# Open the .env file in your preferred editor
nano .env
```

Key environment variables to consider:

- `DB_PASSWORD`: Change this to a secure password
- `JWT_SECRET`: Change this to a secure random string
- `ADMIN_EMAIL`: Default admin email address
- `ADMIN_PASSWORD`: Default admin password

### 3. Start the System

#### On Linux/Mac:

```bash
# Make the start script executable if needed
chmod +x start.sh

# Start the system
./start.sh
```

#### On Windows:

```bash
# Start the system
start.bat
```

The startup script will:
1. Build and start all Docker containers
2. Initialize the database
3. Create default users if they don't exist
4. Start the backend API server
5. Start the frontend web server

### 4. Verify Installation

Once the system is running, verify the installation by:

1. Opening a web browser
2. Navigating to `http://localhost` (or the configured host/port)
3. Logging in with the default admin credentials:
   - Email: admin@t24leads.se
   - Password: admin123

## Troubleshooting

### Common Issues

#### Docker Containers Not Starting

If containers fail to start:

```bash
# Check container status
docker-compose ps

# View container logs
docker-compose logs
```

#### Database Connection Issues

If the application cannot connect to the database:

1. Ensure the PostgreSQL container is running
2. Check the database credentials in the `.env` file
3. Verify network connectivity between containers

#### Port Conflicts

If there are port conflicts:

1. Edit the `docker-compose.yml` file
2. Change the exposed ports to available ones
3. Restart the system

## Updating the System

To update the system to a newer version:

1. Stop the running system:
   ```bash
   docker-compose down
   ```

2. Back up your data:
   ```bash
   docker-compose exec postgres pg_dump -U postgres t24db > backup.sql
   ```

3. Replace the files with the new version
4. Start the system again:
   ```bash
   ./start.sh
   ```

## Security Recommendations

For production deployments, consider these security enhancements:

1. Change all default passwords
2. Use a reverse proxy with HTTPS
3. Implement regular database backups
4. Set up monitoring and logging
5. Restrict network access to the system
