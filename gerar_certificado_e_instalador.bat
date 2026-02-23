@echo off
cd /d "%~dp0"
title Corrigir certificado - dados.kanaflex.com.br

echo.
echo ============================================================
echo   GERAR NOVO CERTIFICADO E INSTALADOR
echo   (para o aviso "Nao seguro" sumir)
echo ============================================================
echo.
echo Este script vai:
echo   1. Gerar novo certificado para dados.kanaflex.com.br
echo   2. Criar o instalador para instalar nos PCs
echo.
pause

echo.
echo [1/2] Gerando certificado...
python gerar_certificado.py
if errorlevel 1 (
    echo [ERRO] Falha ao gerar certificado.
    pause
    exit /b 1
)

echo.
echo [2/2] Criando instalador para os PCs...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0criar_instalador_cliente.ps1"
if errorlevel 1 (
    echo [ERRO] Falha ao criar instalador.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   PRONTO!
echo ============================================================
echo.
echo PROXIMOS PASSOS:
echo.
echo 1. REINICIE o servidor (feche e abra de novo o iniciar.bat)
echo.
echo 2. Em CADA PC que acessa o site (incluindo o servidor):
echo    - Copie o arquivo: InstaladorCertificadoCliente\Instalar_Certificado_KanaData.bat
echo    - Clique com botao direito nele - Executar como administrador
echo    - Feche TODOS os navegadores e abra de novo
echo.
echo 3. Acesse: https://dados.kanaflex.com.br
echo    O aviso "Nao seguro" deve sumir apos instalar o certificado.
echo.
echo ============================================================
pause
