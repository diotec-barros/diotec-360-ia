@echo off
echo ========================================
echo Aethel Judge - Push para Hugging Face
echo ========================================
echo.
echo IMPORTANTE: Voce vai precisar de um Access Token
echo.
echo 1. Va para: https://huggingface.co/settings/tokens
echo 2. Clique em "New token"
echo 3. De um nome (ex: aethel-deploy)
echo 4. Selecione permissao "write"
echo 5. Copie o token gerado
echo.
echo Pressione qualquer tecla quando tiver o token pronto...
pause > nul
echo.
echo ========================================
echo Fazendo Push...
echo ========================================
echo.
echo Quando pedir credenciais:
echo   Username: diotec
echo   Password: Cole o token (nao a senha!)
echo.
cd diotec360-judge
git push
echo.
if errorlevel 1 (
    echo.
    echo ========================================
    echo ERRO no Push!
    echo ========================================
    echo.
    echo Se deu erro de autenticacao:
    echo 1. Certifique-se de usar o TOKEN como senha
    echo 2. Nao use sua senha normal do HF
    echo 3. O token deve ter permissao "write"
    echo.
    echo Tente novamente:
    echo   cd diotec360-judge
    echo   git push
    echo.
) else (
    echo.
    echo ========================================
    echo SUCESSO! Deploy Completo!
    echo ========================================
    echo.
    echo Seu Space esta sendo construido em:
    echo https://huggingface.co/spaces/diotec/diotec360-judge
    echo.
    echo Aguarde 5-10 minutos para o build completar.
    echo Acompanhe os logs na aba "Logs" do Space.
    echo.
)
cd ..
pause
