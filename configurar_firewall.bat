@echo off
echo ============================================================
echo   CONFIGURANDO FIREWALL PARA PORTAL KANADATA
echo ============================================================
echo.
echo Este script vai abrir a porta 443 no firewall do Windows
echo para permitir que outras maquinas acessem o servidor.
echo.
echo IMPORTANTE: Execute como Administrador!
echo.
pause

echo.
echo Verificando se esta rodando como Administrador...
net session >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERRO] Este script precisa ser executado como Administrador!
    echo.
    echo Como fazer:
    echo 1. Clique com botao direito no arquivo
    echo 2. Selecione "Executar como administrador"
    echo.
    pause
    exit /b 1
)

echo [OK] Executando como Administrador
echo.

echo Criando regra de firewall para porta 443...
netsh advfirewall firewall add rule name="KanaData Port 443" dir=in action=allow protocol=TCP localport=443

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao criar regra de firewall
    echo Tente criar manualmente:
    echo 1. Win+R
    echo 2. firewall.cpl
    echo 3. Configuracoes Avancadas
    echo 4. Regras de Entrada - Nova Regra
    echo 5. Porta - TCP - 443 - Permitir
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] Regra de firewall criada com sucesso!
echo.
echo Porta 443 esta aberta para conexoes externas.
echo.
echo Teste agora: python teste_completo.py
echo.
pause

