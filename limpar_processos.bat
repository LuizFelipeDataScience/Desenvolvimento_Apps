@echo off
echo ============================================================
echo   LIMPANDO PROCESSOS PYTHON TRAVADOS
echo ============================================================
echo.

echo Parando todos os processos Python...
taskkill /F /IM python.exe >nul 2>&1
if errorlevel 1 (
    echo [INFO] Nenhum processo Python encontrado
) else (
    echo [OK] Processos Python parados
)

echo.
echo Aguardando 2 segundos...
timeout /t 2 /nobreak >nul

echo.
echo Verificando porta 443...
netstat -an | findstr :443
if errorlevel 1 (
    echo [OK] Porta 443 esta livre
) else (
    echo [AVISO] Porta 443 ainda esta em uso
    echo         Pode ser necessario reiniciar o computador
)

echo.
echo ============================================================
echo   LIMPEZA CONCLUIDA
echo ============================================================
echo.
echo Agora execute: iniciar.bat
echo.
pause

