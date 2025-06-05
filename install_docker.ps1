# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Please run this script as Administrator"
    exit 1
}

# Enable required Windows features
Write-Host "Enabling required Windows features..."
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
Enable-WindowsOptionalFeature -Online -FeatureName Containers -All

# Download Docker Desktop Installer
$dockerUrl = "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe"
$installerPath = "$env:TEMP\DockerDesktopInstaller.exe"
Write-Host "Downloading Docker Desktop..."
Invoke-WebRequest -Uri $dockerUrl -OutFile $installerPath

# Install Docker Desktop
Write-Host "Installing Docker Desktop..."
Start-Process -FilePath $installerPath -ArgumentList "install --quiet" -Wait

# Clean up installer
Remove-Item $installerPath

# Add Docker to PATH
$dockerPath = "$env:ProgramFiles\Docker\Docker\resources\bin"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if (-not $currentPath.Contains($dockerPath)) {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$dockerPath", "Machine")
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
}

Write-Host "Docker Desktop installation completed. Please restart your computer."
Write-Host "After restart, run 'docker --version' to verify the installation."
Write-Host "Then you can run 'docker-compose up -d' to start KairoAI."

# Prompt for restart
$restart = Read-Host "Would you like to restart your computer now? (Y/N)"
if ($restart -eq 'Y' -or $restart -eq 'y') {
    Restart-Computer -Force
} 