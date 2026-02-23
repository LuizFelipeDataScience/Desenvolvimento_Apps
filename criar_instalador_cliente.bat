@echo off
cd /d "%~dp0"

echo.
echo Criando instalador para PC cliente (so Windows padrao, sem Python)...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_instalador_cliente.ps1"
if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao criar instalador.
    pause
    exit /b 1
)

echo.
echo Deseja abrir a pasta do instalador? (S/N)
set /p ABRIR=
if /i "%ABRIR%"=="S" (
    start "" "%~dp0InstaladorCertificadoCliente"
)

echo.
pause
