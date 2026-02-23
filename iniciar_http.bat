@echo off
echo ============================================================
echo   INICIANDO PORTAL KANADATA EM MODO HTTP
echo ============================================================
echo.
echo Este modo permite acesso via HTTP (sem HTTPS)
echo Pessoas devem acessar: http://dados.kanaflex.com.br:443
echo NOTA: Porta 443 e padrao para HTTPS. Para HTTP use outra porta.
echo.
echo Para usar HTTPS (recomendado para Power BI):
echo   - Execute: iniciar.bat
echo   - Ou: python app.py (apos gerar certificados)
echo.
echo ============================================================
echo.

set FORCE_HTTP=1
python app.py

