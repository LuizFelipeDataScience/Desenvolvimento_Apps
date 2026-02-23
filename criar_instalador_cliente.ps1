# Gera o instalador do certificado para PC cliente (so Windows padrao - sem Python)
# Execute no SERVIDOR. O .bat gerado pode ser copiado para qualquer cliente.

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$certFile = Join-Path $scriptDir "server.crt"
$outDir = Join-Path $scriptDir "InstaladorCertificadoCliente"
$outBat = Join-Path $outDir "Instalar_Certificado_KanaData.bat"

Write-Host "============================================================"
Write-Host "  CRIANDO INSTALADOR PARA PC CLIENTE"
Write-Host "============================================================"
Write-Host ""

if (-not (Test-Path $certFile)) {
    Write-Host "[ERRO] Arquivo server.crt nao encontrado!"
    Write-Host "       Gere o certificado antes (instalar_completo.bat ou python gerar_certificado.py)"
    exit 1
}

$certBytes = [System.IO.File]::ReadAllBytes($certFile)
$b64 = [Convert]::ToBase64String($certBytes)

# Quebrar em linhas de 76 caracteres
$b64Lines = New-Object System.Collections.ArrayList
for ($i = 0; $i -lt $b64.Length; $i += 76) {
    $len = [Math]::Min(76, $b64.Length - $i)
    [void]$b64Lines.Add($b64.Substring($i, $len))
}

$bat = @()
$bat += "@echo off"
$bat += "setlocal EnableDelayedExpansion"
$bat += "REM Instalador certificado KanaData - so Windows padrao (sem Python)"
$bat += "REM Execute como Administrador"
$bat += "net session >nul 2>&1"
$bat += "if errorlevel 1 ("
$bat += "    echo [ERRO] Execute como Administrador!"
$bat += "    echo Clique com botao direito neste arquivo e escolha Executar como administrador"
$bat += "    pause"
$bat += "    exit /b 1"
$bat += ")"
$bat += ""
$bat += 'set "B64=%TEMP%\kanadata_cert.b64"'
$bat += 'set "CRT=%TEMP%\kanadata_portal.crt"'
$bat += ""
$bat += "echo Instalando certificado KanaData..."
$bat += ""

$pct = [char]37
for ($i = 0; $i -lt $b64Lines.Count; $i++) {
    $redir = if ($i -eq 0) { ">" } else { ">>" }
    $bat += "echo $($b64Lines[$i]) $redir `"${pct}B64${pct}`""
}

$bat += ""
$bat += 'certutil -decode "%B64%" "%CRT%" >nul 2>&1'
$bat += "if errorlevel 1 ("
$bat += "    echo [ERRO] Falha ao preparar certificado."
$bat += '    del "%B64%" "%CRT%" 2>nul'
$bat += "    pause"
$bat += "    exit /b 1"
$bat += ")"
$bat += ""
$bat += "echo Instalando no Windows..."
$bat += 'certutil -addstore -f Root "%CRT%"'
$bat += "if errorlevel 1 ("
$bat += "    echo [ERRO] Falha ao instalar."
$bat += '    del "%B64%" "%CRT%" 2>nul'
$bat += "    pause"
$bat += "    exit /b 1"
$bat += ")"
$bat += 'del "%B64%" "%CRT%" 2>nul'
$bat += ""
$bat += "echo."
$bat += "echo ========================================"
$bat += "echo   CERTIFICADO INSTALADO COM SUCESSO!"
$bat += "echo ========================================"
$bat += "echo."
$bat += "echo Feche todos os navegadores e abra de novo."
$bat += "echo Acesse: https://dados.kanaflex.com.br"
$bat += "echo O aviso Nao seguro nao deve mais aparecer."
$bat += "echo."
$bat += "pause"

New-Item -ItemType Directory -Path $outDir -Force | Out-Null
$batContent = $bat -join "`r`n"
[System.IO.File]::WriteAllText($outBat, $batContent, [System.Text.Encoding]::ASCII)

Write-Host "[OK] Instalador criado (so CMD + certutil, sem Python):"
Write-Host "     $outBat"
Write-Host ""
Write-Host "No cliente: copie esse .bat, clique direito -> Executar como administrador."
Write-Host "============================================================"
exit 0
