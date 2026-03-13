@echo off
REM ========================================
REM Diotec360 v3.0.5 - Node 1 Deployment
REM Target: Hugging Face Space
REM ========================================

echo.
echo ========================================
echo   Diotec360 v3.0.5 - NODE 1 DEPLOYMENT
echo   Target: Hugging Face Space
echo ========================================
echo.

REM Check if HF Space directory exists
if not exist "aethel-hf-space" (
    echo [1/7] Cloning Hugging Face Space repository...
    git clone https://huggingface.co/spaces/diotec/aethel aethel-hf-space
    if errorlevel 1 (
        echo ERROR: Failed to clone repository
        echo Please make sure you have access to the Space
        pause
        exit /b 1
    )
) else (
    echo [1/7] Space directory exists, pulling latest...
    cd aethel-hf-space
    git pull
    cd ..
)

echo.
echo [2/7] Copying core application files...
xcopy /E /I /Y aethel aethel-hf-space\aethel
xcopy /E /I /Y api aethel-hf-space\api

echo.
echo [3/7] Copying configuration files...
copy /Y requirements.txt aethel-hf-space\requirements.txt
copy /Y Dockerfile.huggingface aethel-hf-space\Dockerfile
copy /Y README_HF.md aethel-hf-space\README.md
copy /Y .dockerignore aethel-hf-space\.dockerignore
copy /Y .env.node1.huggingface aethel-hf-space\.env

echo.
echo [4/7] Creating vault directories...
if not exist "aethel-hf-space\.DIOTEC360_vault\bundles" mkdir aethel-hf-space\.DIOTEC360_vault\bundles
if not exist "aethel-hf-space\.DIOTEC360_vault\certificates" mkdir aethel-hf-space\.DIOTEC360_vault\certificates
if not exist "aethel-hf-space\.DIOTEC360_state" mkdir aethel-hf-space\.DIOTEC360_state
if not exist "aethel-hf-space\.DIOTEC360_sentinel" mkdir aethel-hf-space\.DIOTEC360_sentinel

echo.
echo [5/7] Copying genesis state...
xcopy /E /I /Y .DIOTEC360_vault aethel-hf-space\.DIOTEC360_vault
xcopy /E /I /Y .DIOTEC360_state aethel-hf-space\.DIOTEC360_state

echo.
echo [6/7] Updating Dockerfile for HF Spaces (port 7860)...
cd aethel-hf-space
(
echo # Diotec360 v3.0.5 - Hugging Face Space Dockerfile
echo FROM python:3.11-slim
echo.
echo WORKDIR /app
echo.
echo # Install dependencies
echo COPY requirements.txt .
echo RUN pip install --no-cache-dir -r requirements.txt
echo.
echo # Copy application
echo COPY aethel ./aethel
echo COPY api ./api
echo COPY .env .env
echo.
echo # Copy genesis state
echo COPY .DIOTEC360_vault ./.DIOTEC360_vault
echo COPY .DIOTEC360_state ./.DIOTEC360_state
echo.
echo # Create directories
echo RUN mkdir -p .DIOTEC360_sentinel
echo.
echo # Expose HF Spaces port
echo EXPOSE 7860
echo.
echo # Start application
echo CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]
) > Dockerfile

echo.
echo [7/7] Committing and pushing to Hugging Face...
git add .
git commit -m "Deploy Diotec360 v3.0.5 - Triangle of Truth Node 1"
git push

if errorlevel 1 (
    echo.
    echo ERROR: Push failed. You may need to authenticate.
    echo.
    echo Run these commands manually:
    echo   cd aethel-hf-space
    echo   git config credential.helper store
    echo   git push
    echo.
    cd ..
    pause
    exit /b 1
)

cd ..

echo.
echo ========================================
echo   DEPLOYMENT SUCCESSFUL! 🎉
echo ========================================
echo.
echo Your Space is building at:
echo https://huggingface.co/spaces/diotec/aethel
echo.
echo Wait 5-10 minutes for the build to complete.
echo.
echo Then verify deployment:
echo   curl https://diotec-aethel.hf.space/health
echo   curl https://diotec-aethel.hf.space/api/lattice/state
echo.
echo Expected Merkle Root:
echo   5df3daee3a0ca23c388a16c3db2c2388aea63f1c4ed5fa12377fe0fef6bf3ce5
echo.
pause
