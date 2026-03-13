@echo off
REM Test Hugging Face Docker configuration locally
REM This ensures the Dockerfile works before deploying

echo ========================================
echo Testing Hugging Face Docker Setup
echo ========================================
echo.

echo Building Docker image...
docker build -f Dockerfile.huggingface -t diotec360-judge-test .

if errorlevel 1 (
    echo.
    echo ❌ Docker build failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ✅ Docker build successful!
echo.
echo Starting container on port 7860...
docker run -d -p 7860:7860 --name diotec360-judge-test diotec360-judge-test

if errorlevel 1 (
    echo.
    echo ❌ Failed to start container!
    pause
    exit /b 1
)

echo.
echo ✅ Container started!
echo.
echo Waiting for API to be ready...
timeout /t 5 /nobreak > nul

echo.
echo Testing health endpoint...
curl http://localhost:7860/health

echo.
echo.
echo ========================================
echo Test Complete!
echo ========================================
echo.
echo Your API is running at: http://localhost:7860
echo.
echo Test it with:
echo   curl http://localhost:7860/health
echo   curl http://localhost:7860/api/examples
echo.
echo Or run the full test suite:
echo   python test_huggingface_deployment.py http://localhost:7860
echo.
echo To stop the container:
echo   docker stop diotec360-judge-test
echo   docker rm diotec360-judge-test
echo.
pause
