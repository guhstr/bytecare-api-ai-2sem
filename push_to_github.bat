@echo off
title Deploy ByteCare AI para o GitHub
cd /d "C:\Users\labsfiap\Desktop\challenge\bytecare-api-ai-2sem"
echo ==========================================================
echo        DEPLOY BYTECARE AI (bytecare-api-ai-2sem)
echo ==========================================================
echo.
echo Repositorio local configurado para:
git remote -v
echo.
echo Tentando enviar os arquivos para a branch main...
echo Se o navegador abrir, autorize o acesso ao GitHub.
echo.
git push -u origin main
echo.
if %ERRORLEVEL% equ 0 (
    echo [SUCESSO] Repositorio enviado com sucesso para o GitHub!
) else (
    echo [ATENCAO] Se o erro for "repository not found", certifique-se de que
    echo criou o repositorio vazio "bytecare-api-ai-2sem" em https://github.com/new
)
echo.
pause
