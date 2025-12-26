@echo off
REM Docker startup script for Windows

echo Starting Crop Monitoring System with Docker Compose...

REM Check if .env.docker exists
if not exist .env.docker (
    echo WARNING: .env.docker not found. Please create it from .env.docker.example
)

REM Build and start containers
docker-compose up --build -d

echo Waiting for database to be ready...
timeout /t 5 /nobreak >nul

REM Run migrations
echo Running database migrations...
docker-compose exec web python manage.py migrate

echo.
echo Backend is starting up!
echo Django API: http://localhost:8000
echo Admin Panel: http://localhost:8000/admin
echo.

REM Optionally start React dev server in a new window
echo Starting React frontend (npm start) in a new window...
cd frontend
start "React Frontend" cmd /k npm start
cd ..

echo.
echo To view backend logs: docker-compose logs -f
echo To stop backend: docker-compose down
echo (Close the React window or press Ctrl+C there to stop the frontend)

pause


