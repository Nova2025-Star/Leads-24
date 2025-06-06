#!/bin/bash

# T24 Arborist Lead System Startup Script
echo "Starting T24 Arborist Lead System..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker and Docker Compose before running this script."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose before running this script."
    exit 1
fi

# Start the system
echo "Building and starting containers..."
docker-compose up --build -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "T24 Arborist Lead System is now running!"
    echo "Access the system at: http://localhost"
    echo ""
    echo "Default login credentials:"
    echo "Admin: admin@t24leads.se / admin123"
    echo "Partner: partner1@t24leads.se / partner1"
    echo ""
    echo "To stop the system, run: docker-compose down"
else
    echo "Error: Failed to start T24 Arborist Lead System."
    echo "Please check the logs with: docker-compose logs"
fi
