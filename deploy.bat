@echo off
REM BasoKa PSN Bot Docker Deployment Script for Windows
REM Usage: deploy.bat [production|development]

setlocal enabledelayedexpansion

set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=development

echo 🚀 Deploying BasoKa PSN Bot in %ENVIRONMENT% mode...

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found!
    echo 📝 Please copy .env.example to .env and configure it:
    echo    copy .env.example .env
    exit /b 1
)

REM Check if Docker is running
docker version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running! Please start Docker Desktop.
    exit /b 1
)

REM Stop existing containers
echo 🛑 Stopping existing containers...
docker-compose down

REM Build and start containers
echo 🔨 Building and starting containers...
if "%ENVIRONMENT%"=="production" (
    docker-compose up -d --build
) else (
    docker-compose up --build
)

echo ✅ BasoKa PSN Bot deployed successfully!
echo 📋 Container status:
docker-compose ps

if "%ENVIRONMENT%"=="production" (
    echo.
    echo 📊 To view logs: docker-compose logs -f
    echo 🛑 To stop: docker-compose down
    echo 🔄 To restart: docker-compose restart
)

pause
