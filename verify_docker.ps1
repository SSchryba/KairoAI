# Check Docker installation
Write-Host "Checking Docker installation..."
try {
    $dockerVersion = docker --version
    Write-Host "Docker version: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "Docker is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check Docker Compose
Write-Host "`nChecking Docker Compose..."
try {
    $composeVersion = docker-compose --version
    Write-Host "Docker Compose version: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "Docker Compose is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check Docker daemon
Write-Host "`nChecking Docker daemon..."
try {
    $dockerInfo = docker info
    Write-Host "Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "Docker daemon is not running" -ForegroundColor Red
    Write-Host "Please start Docker Desktop" -ForegroundColor Yellow
    exit 1
}

# Check required ports
Write-Host "`nChecking required ports..."
$requiredPorts = @(5000, 8332, 8333, 18332, 18333, 9090, 3000)
$availablePorts = @()

foreach ($port in $requiredPorts) {
    $connection = Test-NetConnection -ComputerName localhost -Port $port -WarningAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        Write-Host "Port $port is in use" -ForegroundColor Yellow
    } else {
        Write-Host "Port $port is available" -ForegroundColor Green
        $availablePorts += $port
    }
}

# Check Docker images
Write-Host "`nChecking Docker images..."
$images = docker images
if ($images -match "kairoai") {
    Write-Host "KairoAI image exists" -ForegroundColor Green
} else {
    Write-Host "KairoAI image not found" -ForegroundColor Yellow
    Write-Host "Run 'docker-compose build' to build the image" -ForegroundColor Yellow
}

# Check Docker containers
Write-Host "`nChecking Docker containers..."
$containers = docker ps -a
if ($containers -match "kairoai") {
    Write-Host "KairoAI container exists" -ForegroundColor Green
} else {
    Write-Host "KairoAI container not found" -ForegroundColor Yellow
    Write-Host "Run 'docker-compose up -d' to start the containers" -ForegroundColor Yellow
}

# Summary
Write-Host "`nDocker Environment Summary:" -ForegroundColor Cyan
Write-Host "------------------------"
Write-Host "Docker: $($dockerVersion -replace '^Docker version ', '')"
Write-Host "Docker Compose: $($composeVersion -replace '^docker-compose version ', '')"
Write-Host "Docker Daemon: Running"
Write-Host "Available Ports: $($availablePorts -join ', ')"
Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. If any ports are in use, free them up"
Write-Host "2. Run 'docker-compose build' to build the images"
Write-Host "3. Run 'docker-compose up -d' to start the containers"
Write-Host "4. Check logs with 'docker-compose logs -f'" 