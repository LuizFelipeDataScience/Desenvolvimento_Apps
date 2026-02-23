@echo off
setlocal EnableDelayedExpansion
REM Instalador certificado KanaData - so Windows padrao (sem Python)
REM Execute como Administrador
net session >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Execute como Administrador!
    echo Clique com botao direito neste arquivo e escolha Executar como administrador
    pause
    exit /b 1
)

set "B64=%TEMP%\kanadata_cert.b64"
set "CRT=%TEMP%\kanadata_portal.crt"

echo Instalando certificado KanaData...

echo LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURRekNDQWl1Z0F3SUJBZ0lVWEV4em5TTFpK > "%B64%"
echo K2hDSmM0Q3hWWm5qTHIySDZRd0RRWUpLb1pJaHZjTkFRRUwKQlFBd1FERUxNQWtHQTFVRUJoTUNR >> "%B64%"
echo bEl4RVRBUEJnTlZCQW9NQ0V0aGJtRkVZWFJoTVI0d0hBWURWUVFEREJWawpZV1J2Y3k1cllXNWha >> "%B64%"
echo bXhsZUM1amIyMHVZbkl3SGhjTk1qWXdNakEyTVRNME1qTXlXaGNOTWpjd01qQTJNVE0wCk1qTXlX >> "%B64%"
echo akJBTVFzd0NRWURWUVFHRXdKQ1VqRVJNQThHQTFVRUNnd0lTMkZ1WVVSaGRHRXhIakFjQmdOVkJB >> "%B64%"
echo TU0KRldSaFpHOXpMbXRoYm1GbWJHVjRMbU52YlM1aWNqQ0NBU0l3RFFZSktvWklodmNOQVFFQkJR >> "%B64%"
echo QURnZ0VQQURDQwpBUW9DZ2dFQkFNakFSb1UyQzdmNDU1bHFUUE9KdlNaRjBMOVJQTzl3L1ZMYVU4 >> "%B64%"
echo SUFVUWJLRmJialZIR3kyUEFDCjFnU1Y5cnZxNmNUdFNBOVNSR0krRVZOSlV6NGRZTVdIYkRRS2tj >> "%B64%"
echo Z3haTWRKZy85K3lWR3QybzRacjMvOGw4Z3kKS21hdlNXeFRKanprVStyRTdVcDc4YjErYmlGb0Jv >> "%B64%"
echo bDlRRzhzeldtS05meFFIb28yYnQ5UnNaL3lmWS82L1Q5cQpwQWFEWGFRckZib1R6WnZkN3d3UU9X >> "%B64%"
echo a0x4VllPKzI5ZldSUGdsVVM2cWNId1FybWdKRVU2ZWhtSkFOeEFDb2JUCkg2QVBmRU1rY0xFcGVZ >> "%B64%"
echo Q3NyQVZraVF1aldOS1MwNXdJVURLTks5UDg5eFNuZWdPM2pLSnpEUDMwSUV6NWdWbDcKdHY1OVAr >> "%B64%"
echo TU8vbUhsdUZIL2twc3V3RkpsNUxpakdORUNBd0VBQWFNMU1ETXdNUVlEVlIwUkJDb3dLSUlWWkdG >> "%B64%"
echo awpiM011YTJGdVlXWnNaWGd1WTI5dExtSnlnZ2xzYjJOaGJHaHZjM1NIQkg4QUFBRXdEUVlKS29a >> "%B64%"
echo SWh2Y05BUUVMCkJRQURnZ0VCQUxvVWs3bFpab1RiK1ZaV2haM3J0R2V3N3ErRDRCaHcza0ZaT3NF >> "%B64%"
echo aENKNHRNajllM3JIdjFGQ3EKTSt0UlJHWExsV295YWVYUzY4eHNtcEpZeW1UbDBQWk5xWEQvejFG >> "%B64%"
echo NWhsWXBuU0h4UVlQUEZscFpZblV1dFg2Zgp6QnNSRlJ3SnlMMHU3MWlIOUJCUjRTZ0s2Vzhhc2cz >> "%B64%"
echo dTMvOEpzWnVpdTJEZ25rOGo4UHhodHpvVUcvbkp4alZFCkFFc0lWb3JQVE5rTlpxTWs3czNvTzRZ >> "%B64%"
echo WUM4ckdhUzRlb0xsMHM4ZGJFeFkwbi95bGVEYWpUMkpGZGVqMmJzRDcKMytqRDRBR25KQlRPcFdP >> "%B64%"
echo Z3BLdnhQVlVjMFFtR29ObVBseFlpNldWamgyTE4zR2V0ZmhUL211MDJpU2lPaW9HUgpoUm82aWgy >> "%B64%"
echo Z1NyT3lXS3ZXMzBMUXVkMFNTYk9hNlpJPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg== >> "%B64%"

certutil -decode "%B64%" "%CRT%" >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Falha ao preparar certificado.
    del "%B64%" "%CRT%" 2>nul
    pause
    exit /b 1
)

echo Instalando no Windows...
certutil -addstore -f Root "%CRT%"
if errorlevel 1 (
    echo [ERRO] Falha ao instalar.
    del "%B64%" "%CRT%" 2>nul
    pause
    exit /b 1
)
del "%B64%" "%CRT%" 2>nul

echo.
echo ========================================
echo   CERTIFICADO INSTALADO COM SUCESSO!
echo ========================================
echo.
echo Feche todos os navegadores e abra de novo.
echo Acesse: https://dados.kanaflex.com.br
echo O aviso Nao seguro nao deve mais aparecer.
echo.
pause