@echo off
echo ============================================================
echo   INICIANDO PORTAL KANADATA
echo ============================================================
echo.

if not exist "app.py" (
    echo [ERRO] Arquivo app.py nao encontrado!
    echo Execute este script na pasta do projeto.
    pause
    exit /b 1
)

echo Verificando processos Python travados...
netstat -an | findstr :443 >nul 2>&1
if not errorlevel 1 (
    echo [AVISO] Porta 443 esta em uso!
    echo         Pode haver servidor travado.
    echo         Parando processos Python...
    taskkill /F /IM python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
    echo [OK] Processos parados
)

echo Verificando se ja foi instalado...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Execute primeiro: instalar_completo.bat
    pause
    exit /b 1
)

python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [AVISO] Dependencias nao instaladas!
    echo Execute primeiro: instalar_completo.bat
    pause
    exit /b 1
)

if not exist "server.crt" (
    echo [AVISO] Certificados SSL nao encontrados!
    echo Execute primeiro: instalar_completo.bat
    pause
    exit /b 1
)

echo [OK] Tudo pronto! Iniciando servidor...
echo.
echo ============================================================
echo   SERVIDOR INICIANDO
echo ============================================================
echo.
echo ============================================================
echo   ATENCAO: USE HTTPS (NAO HTTP)!
echo ============================================================
echo.
echo URLs CORRETAS:
echo   Local: https://localhost
echo   Rede:  https://dados.kanaflex.com.br
echo   Admin: https://dados.kanaflex.com.br/admin
echo.
echo URLs ERRADAS (NAO FUNCIONAM):
echo   http://localhost  <- ERRADO!
echo   http://dados.kanaflex.com.br  <- ERRADO!
echo.
echo IMPORTANTE:
echo - Use https:// (com 's' no final!)
echo - Para TIRAR o aviso "Nao seguro": execute criar_instalador_cliente.bat, depois o .bat gerado como Admin
echo   (depois feche o navegador e abra de novo)
echo.
echo Pressione Ctrl+C para parar o servidor
echo ============================================================
echo.

python app.py
