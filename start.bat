@echo off
echo Starting T24 Arborist Lead System...

REM Check if Docker is installed
docker --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker is not installed. Please install Docker and Docker Compose before running this script.
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker Compose is not installed. Please install Docker Compose before running this script.
    exit /b 1
)

REM Start the system
echo Building and starting containers...
docker-compose up --build -d

REM Wait for services to be ready
echo Waiting for services to start...
timeout /t 10 /nobreak > nul

REM Check if services are running
docker-compose ps | findstr Up > nul
if %ERRORLEVEL% EQU 0 (
    echo T24 Arborist Lead System is now running!
    echo Access the system at: http://localhost
    echo.
    echo Default login credentials:
    echo Admin: admin@t24leads.se / admin123
    echo Partner: partner1@t24leads.se / partner1
    echo.
    echo To stop the system, run: docker-compose down
) else (
    echo Error: Failed to start T24 Arborist Lead System.
    echo Please check the logs with: docker-compose logs
)

