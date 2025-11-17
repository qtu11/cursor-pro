# Kiem tra xem co phai duoc khoi dong bang quyen nang cao khong
param(
    [switch]$Elevated
)

# Thiet lap chu de mau sac
$Theme = @{
    Primary   = 'Cyan'
    Success   = 'Green'
    Warning   = 'Yellow'
    Error     = 'Red'
    Info      = 'White'
}

# ASCII Logo
$Logo = @"
██████╗ ███████╗███████╗███████╗████████╗    ████████╗ ██████╗  ██████╗ ██╗     
██╔══██╗██╔════╝██╔════╝██╔════╝╚══██╔══╝    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     
██████╔╝█████╗  ███████╗█████╗     ██║          ██║   ██║   ██║██║   ██║██║     
██╔══██╗██╔══╝  ╚════██║██╔══╝     ██║          ██║   ██║   ██║██║   ██║██║     
██║  ██║███████╗███████║███████╗   ██║          ██║   ╚██████╔╝╚██████╔╝███████╗
╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝   ╚═╝          ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
"@

# Ham xuat dep
function Write-Styled {
    param (
        [string]$Message,
        [string]$Color = $Theme.Info,
        [string]$Prefix = "",
        [switch]$NoNewline
    )
    $emoji = switch ($Color) {
        $Theme.Success { "✅" }
        $Theme.Error   { "❌" }
        $Theme.Warning { "⚠️" }
        default        { "ℹ️" }
    }
    
    $output = if ($Prefix) { "$emoji $Prefix :: $Message" } else { "$emoji $Message" }
    if ($NoNewline) {
        Write-Host $output -ForegroundColor $Color -NoNewline
    } else {
        Write-Host $output -ForegroundColor $Color
    }
}

# Kiem tra quyen quan tri vien
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-NOT $isAdmin) {
    Write-Styled "Can quyen quan tri vien de chay cong cu reset" -Color $Theme.Warning -Prefix "Quyen"
    Write-Styled "Dang yeu cau quyen quan tri vien..." -Color $Theme.Primary -Prefix "Nang cao"
    
    # Hien thi cac tuy chon thao tac
    Write-Host "`nChon thao tac:" -ForegroundColor $Theme.Primary
    Write-Host "1. Yeu cau quyen quan tri vien" -ForegroundColor $Theme.Info
    Write-Host "2. Thoat chuong trinh" -ForegroundColor $Theme.Info
    
    $choice = Read-Host "`nVui long nhap tuy chon (1-2)"
    
    if ($choice -ne "1") {
        Write-Styled "Thao tac da bi huy" -Color $Theme.Warning -Prefix "Huy"
        Write-Host "`nNhan phim bat ky de thoat..." -ForegroundColor $Theme.Info
        $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
        exit
    }
    
    try {
        Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -Elevated"
        exit
    }
    catch {
        Write-Styled "Khong the lay quyen quan tri vien" -Color $Theme.Error -Prefix "Loi"
        Write-Styled "Vui long chay PowerShell voi quyen quan tri vien roi thu lai" -Color $Theme.Warning -Prefix "Gợi y"
        Write-Host "`nNhan phim bat ky de thoat..." -ForegroundColor $Theme.Info
        $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
        exit 1
    }
}

# Neu la cua so sau khi nang cao quyen, cho mot chut de dam bao cua so hien thi
if ($Elevated) {
    Start-Sleep -Seconds 1
}

# Hien thi Logo
Write-Host $Logo -ForegroundColor $Theme.Primary
Write-Host "Created by qtusdev`n" -ForegroundColor $Theme.Info

# Thiet lap TLS 1.2
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# Tao thu muc tam thoi
$TmpDir = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
New-Item -ItemType Directory -Path $TmpDir -Force | Out-Null

# Ham don dep
function Cleanup {
    if (Test-Path $TmpDir) {
        Remove-Item -Recurse -Force $TmpDir -ErrorAction SilentlyContinue
    }
}

try {
    # Dia chi tai xuong
    $url = "https://github.com/qtu11/cursor-pro/releases/download/ManualReset/reset_machine_manual.exe"
    $output = Join-Path $TmpDir "reset_machine_manual.exe"

    # Tai xuong file
    Write-Styled "Dang tai xuong cong cu reset..." -Color $Theme.Primary -Prefix "Tai xuong"
    Invoke-WebRequest -Uri $url -OutFile $output
    Write-Styled "Tai xuong hoan tat!" -Color $Theme.Success -Prefix "Hoan tat"

    # Thuc thi cong cu reset
    Write-Styled "Dang khoi dong cong cu reset..." -Color $Theme.Primary -Prefix "Thuc thi"
    Start-Process -FilePath $output -Wait
    Write-Styled "Reset hoan tat!" -Color $Theme.Success -Prefix "Hoan tat"
}
catch {
    Write-Styled "Thao tac that bai" -Color $Theme.Error -Prefix "Loi"
    Write-Styled $_.Exception.Message -Color $Theme.Error
}
finally {
    Cleanup
    Write-Host "`nNhan phim bat ky de thoat..." -ForegroundColor $Theme.Info
    $null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
} 