param([string]$Action = "run", [string]$BuildName)

Write-Host "Victor Reaction Bot Deployment Script" -ForegroundColor Cyan
Write-Host "Action: $Action" -ForegroundColor Gray
Write-Host "BuildName: $BuildName" -ForegroundColor Gray

$ImageName = "victor-win-reaction:$BuildName"
$ContainerName = "victor-win-reaction:$BuildName"
$DockerHubRegistry = "khanasif1"
$DockerHubImageName = "$DockerHubRegistry/victor-win-reaction:$BuildName"

if ($Action -eq "run") {
    Write-Host "Starting new deployment..." -ForegroundColor Green
    
    # Stop and remove existing container if it exists
    Write-Host "Cleaning up existing container..." -ForegroundColor Yellow
    docker stop $ContainerName 2>$null
    docker rm $ContainerName 2>$null
    
    # Load environment variables from .env file
    $EnvFile = "../.env"
    $ApiKey = ""
    $Endpoint = ""
    $Deployment = ""
    
    if (Test-Path $EnvFile) {
        Write-Host "Loading environment variables from .env file..." -ForegroundColor Cyan
        $content = Get-Content $EnvFile
        foreach ($line in $content) {
            if ($line -match "AZURE_OPENAI_API_KEY=(.+)") {
                $ApiKey = $matches[1]
                Write-Host "AZURE_OPENAI_API_KEY=***" -ForegroundColor Gray
            }
            if ($line -match "ENDPOINT_URL=(.+)") {
                $Endpoint = $matches[1]
                Write-Host "ENDPOINT_URL=$Endpoint" -ForegroundColor Gray
            }
            if ($line -match "DEPLOYMENT_NAME=(.+)") {
                $Deployment = $matches[1]
                Write-Host "DEPLOYMENT_NAME=$Deployment" -ForegroundColor Gray
            }
        }
    }
    
    # Start container
    if ($ApiKey -ne "" -and $Endpoint -ne "" -and $Deployment -ne "") {
        Write-Host "Starting container with API key authentication..." -ForegroundColor Green
        $containerId = docker run --name $ContainerName -d -e "AZURE_OPENAI_API_KEY=$ApiKey" -e "ENDPOINT_URL=$Endpoint" -e "DEPLOYMENT_NAME=$Deployment" $ImageName
        Write-Host "Container started with API key authentication!" -ForegroundColor Green
    } else {
        Write-Host "Starting container with Entra ID authentication..." -ForegroundColor Green
        $containerId = docker run --name $ContainerName -d $ImageName
        Write-Host "Container started!" -ForegroundColor Green
    }
    
    # Wait a moment for container to initialize
    Start-Sleep -Seconds 3
    
    # Check if container is actually running
    $containerStatus = docker ps -f name=$ContainerName --format "{{.Status}}"
    if ($containerStatus) {
        Write-Host "Container is running: $containerStatus" -ForegroundColor Green
        
        # Show initial logs
        Write-Host "`nContainer logs (first 50 lines):" -ForegroundColor Cyan
        docker logs $ContainerName --tail 50
        
        Write-Host "`nFor real-time logs, run:" -ForegroundColor Yellow
        Write-Host "   .\deploy-basic.ps1 logs $BuildName" -ForegroundColor White
        
    } else {
        Write-Host "Container is not running! Checking what happened..." -ForegroundColor Red
        
        # Check if container exited
        $exitedStatus = docker ps -a -f name=$ContainerName --format "{{.Status}}"
        Write-Host "Container status: $exitedStatus" -ForegroundColor Yellow
        
        # Show logs to see what went wrong
        Write-Host "`nContainer logs (to see errors):" -ForegroundColor Red
        docker logs $ContainerName
        
        # Get exit code
        $exitCode = docker inspect $ContainerName --format="{{.State.ExitCode}}" 2>$null
        if ($exitCode) {
            Write-Host "`nContainer exited with code: $exitCode" -ForegroundColor Red
        }
    }
}

if ($Action -eq "logs") {
    Write-Host "Showing logs for container: $ContainerName" -ForegroundColor Cyan
    
    # Check if container exists
    $containerExists = docker ps -a -f name=$ContainerName --format "{{.Names}}"
    if (-not $containerExists) {
        Write-Host "Container $ContainerName not found!" -ForegroundColor Red
        Write-Host "Available containers:" -ForegroundColor Yellow
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
        return
    }
    
    # Check if container is running
    $isRunning = docker ps -f name=$ContainerName --format "{{.Names}}"
    if ($isRunning) {
        Write-Host "Following real-time logs (Press Ctrl+C to stop)..." -ForegroundColor Green
        docker logs -f $ContainerName
    } else {
        Write-Host "Container is not running. Showing all available logs:" -ForegroundColor Yellow
        docker logs $ContainerName
        
        # Show container status
        $status = docker ps -a -f name=$ContainerName --format "{{.Status}}"
        Write-Host "`nContainer Status: $status" -ForegroundColor Gray
    }
}

if ($Action -eq "stop") {
    docker stop $ContainerName
    docker rm $ContainerName
    Write-Host "Container stopped!" -ForegroundColor Green
}

if ($Action -eq "status") {
    Write-Host "Container Status for: $ContainerName" -ForegroundColor Cyan
    
    # Check if container exists
    $containerExists = docker ps -a -f name=$ContainerName --format "{{.Names}}"
    if (-not $containerExists) {
        Write-Host "Container $ContainerName not found!" -ForegroundColor Red
        Write-Host "`nAvailable containers:" -ForegroundColor Yellow
        docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Image}}\t{{.CreatedAt}}"
        return
    }
    
    # Detailed status
    Write-Host "`nContainer Details:" -ForegroundColor Green
    docker ps -a -f name=$ContainerName --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.CreatedAt}}"
    
    # Additional info
    $state = docker inspect $ContainerName --format="{{.State.Status}}" 2>$null
    $exitCode = docker inspect $ContainerName --format="{{.State.ExitCode}}" 2>$null
    $startedAt = docker inspect $ContainerName --format="{{.State.StartedAt}}" 2>$null
    
    Write-Host "`nAdditional Info:" -ForegroundColor Cyan
    Write-Host "   State: $state" -ForegroundColor Gray
    if ($exitCode -ne "0") {
        Write-Host "   Exit Code: $exitCode" -ForegroundColor Red
    } else {
        Write-Host "   Exit Code: $exitCode" -ForegroundColor Green
    }
    Write-Host "   Started At: $startedAt" -ForegroundColor Gray
    
    # Show last few log lines
    Write-Host "`nLast 10 log lines:" -ForegroundColor Cyan
    docker logs --tail 10 $ContainerName 2>$null
}

if ($Action -eq "build") {
    Write-Host "Building Docker image..." -ForegroundColor Green
    Set-Location ".."
    docker build -t $ImageName -f deploy/Dockerfile .
    Write-Host "Build complete!" -ForegroundColor Green
    Set-Location "deploy"
}

if ($Action -eq "push") {
    Write-Host "Pushing image to Docker Hub..." -ForegroundColor Green
    docker tag $ImageName $DockerHubImageName
    docker push $DockerHubImageName
    Write-Host "Image pushed to Docker Hub: $DockerHubImageName" -ForegroundColor Green
}

if ($Action -eq "deploy") {
    Write-Host "Building and deploying to Docker Hub..." -ForegroundColor Green
    
    # Build the image
    Write-Host "Step 1: Building Docker image..." -ForegroundColor Cyan
    Set-Location ".."
    docker build -t $ImageName -f deploy/Dockerfile .
    Set-Location "deploy"
    
    # Tag and push to Docker Hub
    Write-Host "Step 2: Tagging and pushing to Docker Hub..." -ForegroundColor Cyan
    docker tag $ImageName $DockerHubImageName
    docker push $DockerHubImageName
    
    Write-Host "Deployment complete! Image available at: $DockerHubImageName" -ForegroundColor Green
}

if ($Action -eq "help") {
    Write-Host "Available actions:" -ForegroundColor Cyan
    Write-Host "  run    - Start container with environment variables" -ForegroundColor Yellow
    Write-Host "  stop   - Stop and remove container" -ForegroundColor Yellow
    Write-Host "  status - Show container status" -ForegroundColor Yellow
    Write-Host "  logs   - Show container logs" -ForegroundColor Yellow
    Write-Host "  build  - Build Docker image" -ForegroundColor Yellow
    Write-Host "  push   - Push image to Docker Hub" -ForegroundColor Yellow
    Write-Host "  deploy - Build and push to Docker Hub" -ForegroundColor Yellow
    Write-Host "  help   - Show this help" -ForegroundColor Yellow
}

Write-Host "Script completed!" -ForegroundColor Green