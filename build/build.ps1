param(
    [switch]$SkipInstall,
    [switch]$SkipSign,
    [switch]$SkipInstaller
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

function Write-Step($msg) {
    Write-Host "`n==> $msg" -ForegroundColor Cyan
}

# 1. Instalar dependencias
if (-not $SkipInstall) {
    Write-Step "Instalando dependencias Python..."
    pip install -r requirements.txt --quiet
    if ($LASTEXITCODE -ne 0) { throw "Error instalando dependencias" }
}

# 2. Build PyInstaller
Write-Step "Compilando ejecutable con PyInstaller (onefile)..."
$buildDir = Join-Path $PSScriptRoot ".."
Set-Location $buildDir

if (Test-Path "dist\EasyConverter") {
    Remove-Item -Recurse -Force "dist\EasyConverter" -ErrorAction SilentlyContinue
}
if (Test-Path "dist\EasyConverter.exe") {
    Remove-Item "dist\EasyConverter.exe" -ErrorAction SilentlyContinue
}

pyinstaller --noconfirm build/easy_converter.spec 2>&1
if ($LASTEXITCODE -ne 0) { throw "Error en PyInstaller" }

$exePath = Join-Path $buildDir "dist\EasyConverter.exe"
if (-not (Test-Path $exePath)) {
    throw "No se generó el ejecutable en $exePath"
}

Write-Host "  -> Ejecutable generado: $exePath" -ForegroundColor Green

# 3. Firmar con certificado autofirmado
if (-not $SkipSign) {
    Write-Step "Firmando ejecutable con certificado autofirmado..."

    $certPath = Join-Path $PSScriptRoot "cert.pfx"
    $certPwd = "EasyConverter2026"

    if (-not (Test-Path $certPath)) {
        Write-Host "  -> Generando certificado autofirmado..." -ForegroundColor Yellow
        $cert = New-SelfSignedCertificate -Type CodeSigning -Subject "CN=EasyConverter" `
            -CertStoreLocation Cert:\CurrentUser\My `
            -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3")
        $pwd = ConvertTo-SecureString $certPwd -Force -AsPlainText
        Export-PfxCertificate -Cert $cert -FilePath $certPath -Password $pwd | Out-Null
        Write-Host "  -> Certificado generado: $certPath" -ForegroundColor Green
    }

    & "signtool" sign /fd SHA256 /a /f $certPath /p $certPwd $exePath 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  -> Ejecutable firmado correctamente" -ForegroundColor Green
    } else {
        Write-Host "  -> Advertencia: No se pudo firmar (signtool no encontrado?)" -ForegroundColor Yellow
    }
}

# 4. Compilar instalador Inno Setup
if (-not $SkipInstaller) {
    Write-Step "Compilando instalador Inno Setup..."
    $isccPaths = @(
        "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        "C:\Program Files\Inno Setup 6\ISCC.exe",
        "C:\Program Files (x86)\Inno Setup\ISCC.exe",
        "C:\Program Files\Inno Setup\ISCC.exe"
    )
    $iscc = $null
    foreach ($p in $isccPaths) {
        if (Test-Path $p) { $iscc = $p; break }
    }

    if ($iscc) {
        $issPath = Join-Path $PSScriptRoot "setup.iss"
        & $iscc $issPath 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  -> Instalador generado en Output/" -ForegroundColor Green
        } else {
            Write-Host "  -> Error al compilar instalador" -ForegroundColor Red
        }
    } else {
        Write-Host "  -> Inno Setup no instalado. Para generar el instalador:" -ForegroundColor Yellow
        Write-Host "     Descarga Inno Setup desde https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
        Write-Host "     Luego ejecuta: ISCC.exe build/setup.iss" -ForegroundColor Yellow
    }
}

Write-Step "Build completado!"
Write-Host "Ejecutable: $exePath" -ForegroundColor Green
