@echo off
echo ============================================================
echo   INSTALACAO COMPLETA - PORTAL KANADATA
echo ============================================================
echo.
echo Este script instala tudo necessario para primeira vez:
echo 1. Verifica Python
echo 2. Instala dependencias
echo 3. Gera certificados SSL
echo 4. Configura firewall (opcional)
echo.
echo Execute apenas UMA VEZ em maquina nova!
echo.
pause

echo.
echo [1/4] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo.
    echo Instale Python 3.8 ou superior de:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
python --version
echo [OK] Python encontrado

echo.
echo [2/4] Instalando dependencias Python...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)
echo [OK] Dependencias instaladas

echo.
echo [3/4] Gerando certificados SSL...
if exist "server.crt" (
    echo Certificados ja existem. Regenerando...
    del server.crt server.key 2>nul
)
python gerar_certificado.py
if not exist "server.crt" (
    echo [ERRO] Falha ao gerar certificados!
    pause
    exit /b 1
)
echo [OK] Certificados gerados

echo.
echo [4/4] Configuracao do Firewall...
echo.
echo Deseja configurar o firewall agora? (S/N)
echo Isso permite que outras maquinas acessem o servidor.
set /p CONFIGURAR_FIREWALL=
if /i "%CONFIGURAR_FIREWALL%"=="S" (
    echo.
    echo [AVISO] Esta operacao requer privilegios de Administrador
    echo         Se nao funcionar, execute manualmente:
    echo         configurar_firewall.bat (como Administrador)
    echo.
    netsh advfirewall firewall add rule name="KanaData Port 443" dir=in action=allow protocol=TCP localport=443 >nul 2>&1
    if errorlevel 1 (
        echo [AVISO] Nao foi possivel configurar firewall automaticamente
        echo         Execute: configurar_firewall.bat (como Administrador)
    ) else (
        echo [OK] Firewall configurado
    )
) else (
    echo [INFO] Firewall nao configurado
    echo        Execute: configurar_firewall.bat (como Administrador) se necessario
)

echo.
echo ============================================================
echo   INSTALACAO CONCLUIDA!
echo ============================================================
echo.
echo Proximos passos:
echo 1. Execute: iniciar.bat
echo 2. Acesse: https://dados.kanaflex.com.br/admin
echo 3. Adicione seus dashboards Power BI
echo.
echo IMPORTANTE:
echo - Para tirar aviso "Nao seguro" no navegador (servidor e clientes):
echo   Execute: criar_instalador_cliente.bat depois rode o .bat gerado como Admin em cada PC
echo.
pause

