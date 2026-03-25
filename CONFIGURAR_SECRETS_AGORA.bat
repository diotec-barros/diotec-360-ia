@echo off
REM ============================================================================
REM DIOTEC 360 IA - Configuração Rápida de Segredos do Relay
REM ============================================================================
REM 
REM Este script guia você na configuração do GUNDB_RELAY_URL
REM no Hugging Face e Vercel.
REM 
REM Desenvolvido por: Kiro para Dionísio Sebastião Barros
REM Data: 25 de Março de 2026
REM ============================================================================

echo.
echo ========================================
echo   DIOTEC 360 IA - Configurar Segredos
echo ========================================
echo.

REM Verificar se estamos no diretório correto
if not exist "diotec360" (
    echo [ERRO] Execute este script na raiz do projeto!
    echo.
    pause
    exit /b 1
)

echo [INFO] Este script vai ajudar voce a configurar o relay GunDB
echo        no Hugging Face e Vercel.
echo.

REM Ler relay URL do .env
set RELAY_URL=https://gun-manhattan.herokuapp.com/gun

for /f "tokens=1,2 delims==" %%a in ('findstr /C:"GUNDB_RELAY_URL=" diotec360\.env 2^>nul') do (
    set RELAY_URL=%%b
)

echo [INFO] Relay URL detectado: %RELAY_URL%
echo.

echo ========================================
echo   PASSO 1: HUGGING FACE
echo ========================================
echo.
echo Configure o segredo no Hugging Face:
echo.
echo 1. Acesse: https://huggingface.co/spaces/diotec-360/diotec-360-ia-judge/settings
echo 2. Role ate "Repository secrets"
echo 3. Clique em "New secret"
echo 4. Adicione:
echo    Name:  GUNDB_RELAY_URL
echo    Value: %RELAY_URL%
echo 5. Clique em "Factory reboot" para reiniciar o Space
echo.

pause

echo.
echo ========================================
echo   PASSO 2: VERCEL
echo ========================================
echo.
echo Configure a variavel de ambiente no Vercel:
echo.
echo 1. Acesse: https://vercel.com/dashboard
echo 2. Selecione o projeto "diotec360-frontend"
echo 3. Va para Settings ^> Environment Variables
echo 4. Clique em "Add New"
echo 5. Adicione:
echo    Name:  NEXT_PUBLIC_GUNDB_RELAY
echo    Value: %RELAY_URL%
echo    Environments: Marque TODOS (Production, Preview, Development)
echo 6. Va para Deployments e faca "Redeploy" do ultimo deploy
echo.

pause

echo.
echo ========================================
echo   PASSO 3: VALIDACAO
echo ========================================
echo.
echo Apos configurar, valide a sincronizacao:
echo.
echo 1. Aguarde o Space reiniciar (2-3 minutos)
echo 2. Aguarde o Vercel fazer redeploy (2-5 minutos)
echo 3. Teste o backend:
echo    curl https://diotec-360-diotec-360-ia-judge.hf.space/api/lattice/peers
echo 4. Teste o frontend:
echo    Abra o site e verifique o Console (F12)
echo    Digite: console.log(process.env.NEXT_PUBLIC_GUNDB_RELAY)
echo.

pause

echo.
echo ========================================
echo   CONFIGURACAO CONCLUIDA
echo ========================================
echo.
echo Se voce seguiu todos os passos:
echo   [OK] Hugging Face configurado
echo   [OK] Vercel configurado
echo   [OK] Lattice pronta para produção
echo.
echo Proximos passos:
echo   1. Aguarde os deploys completarem
echo   2. Teste a sincronizacao P2P
echo   3. Demonstre para investidores
echo.
echo ========================================
echo   A LATTICE RESPIRA EM PRODUCAO
echo ========================================
echo.

pause
