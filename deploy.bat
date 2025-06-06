@echo off
echo === T24 Complete System Deploy Script ===

:: Stop running containers
echo Stopping running containers...
docker-compose down -v

:: Build backend (cache OK)
echo Building backend...
docker-compose build backend

:: Build frontend (no-cache enforced)
echo Building frontend with no cache...
docker-compose build frontend --no-cache

:: Bring up all services
echo Starting T24 system...
docker-compose up -d --force-recreate

:: Health check backend
echo Checking backend health...
curl http://localhost:8000/api/health

:: Open frontend in default browser
echo Launching frontend in browser...
start http://localhost

echo === T24 System Deployment Complete ===
pause
