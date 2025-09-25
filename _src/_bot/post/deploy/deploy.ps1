param([string]$Action = "run", [string]$BuildName)

# Validate BuildName parameter
if ([string]::IsNullOrWhiteSpace($BuildName)) {
    Write-Host "❌ Error: BuildName parameter is required" -ForegroundColor Red
    Write-Host "Usage: .\deploy.ps1 [action] [buildname]" -ForegroundColor Yellow
    Write-Host "Example: .\deploy.ps1 run delta" -ForegroundColor Green
    exit 1
}

$ImageName = "victor-win-post-$BuildName"
$ContainerName = "victor-win-post--$BuildName"
$DockerHubRegistry = "khanasif1"
$DockerHubImageName = "$DockerHubRegistry/victor-win-post:$BuildName"




switch ($Action.ToLower()) {
    "build" {
        Write-Host "Building Docker image..." -ForegroundColor Cyan
        Set-Location ".."
        docker build -f deploy/Dockerfile -t $ImageName -t $DockerHubImageName .
        Set-Location "deploy"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Build successful!" -ForegroundColor Green
            Write-Host "Local image: $ImageName" -ForegroundColor Yellow
            Write-Host "Docker Hub image: $DockerHubImageName" -ForegroundColor Yellow
        }
    }
    "push" {
        Write-Host "Building and pushing to Docker Hub..." -ForegroundColor Cyan
        Write-Host "Registry: $DockerHubRegistry" -ForegroundColor Yellow
        
        # Build with both tags
        Set-Location ".."
        docker build -f deploy/Dockerfile -t $ImageName -t $DockerHubImageName .
        Set-Location "deploy"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Build successful!" -ForegroundColor Green
            Write-Host "Pushing to Docker Hub..." -ForegroundColor Cyan
            docker push $DockerHubImageName
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Successfully pushed to Docker Hub!" -ForegroundColor Green
                Write-Host "Image available at: $DockerHubImageName" -ForegroundColor Yellow
            } else {
                Write-Host "❌ Failed to push to Docker Hub" -ForegroundColor Red
                Write-Host "Make sure you're logged in: docker login" -ForegroundColor Yellow
            }
        }
    }
    "login" {
        Write-Host "Logging into Docker Hub..." -ForegroundColor Cyan
        docker login
    }
    "run" {
        Write-Host "Building and running container..." -ForegroundColor Cyan
        Set-Location ".."
        docker build -f deploy/Dockerfile -t $ImageName -t $DockerHubImageName .
        if ($LASTEXITCODE -eq 0) {
            $existing = docker ps -q -f name=$ContainerName
            if ($existing) {
                docker stop $ContainerName
                docker rm $ContainerName
            }
            docker run -d --name $ContainerName $ImageName
            Write-Host "✅ Container started!" -ForegroundColor Green
            Write-Host "View logs: docker logs -f $ContainerName" -ForegroundColor Yellow
        }
        Set-Location "deploy"
    }
    "logs" {
        docker logs -f $ContainerName
    }
    "stop" {
        docker stop $ContainerName
        docker rm $ContainerName
        Write-Host " Container stopped!" -ForegroundColor Green
    }
    "status" {
        Write-Host "Container Status:" -ForegroundColor Cyan
        docker ps -f name=$ContainerName
        Write-Host "`nLocal Images:" -ForegroundColor Cyan
        docker images $ImageName
        Write-Host "`nDocker Hub Images:" -ForegroundColor Cyan
        docker images $DockerHubImageName
    }
    "pull" {
        Write-Host "Pulling latest image from Docker Hub..." -ForegroundColor Cyan
        docker pull $DockerHubImageName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Successfully pulled from Docker Hub!" -ForegroundColor Green
            Write-Host "Image: $DockerHubImageName" -ForegroundColor Yellow
        }
    }
    "run-hub" {
        Write-Host "Running container from Docker Hub image..." -ForegroundColor Cyan
        
        # Pull latest image first
        docker pull $DockerHubImageName
        
        if ($LASTEXITCODE -eq 0) {
            $existing = docker ps -q -f name=$ContainerName
            if ($existing) {
                docker stop $ContainerName
                docker rm $ContainerName
            }
            docker run -d --name $ContainerName $DockerHubImageName
            Write-Host "✅ Container started from Docker Hub image!" -ForegroundColor Green
            Write-Host "View logs: docker logs -f $ContainerName" -ForegroundColor Yellow
        }
    }
    default {
        Write-Host "Victor Campaign Post Orchestrator - Docker Deploy Script" -ForegroundColor Green
        Write-Host ""
        Write-Host "Usage: .\deploy.ps1 [action] [buildname]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Parameters:" -ForegroundColor Cyan
        Write-Host "  action     - The action to perform (see below)"
        Write-Host "  buildname  - Required. Build identifier (e.g., 'delta', 'prod', 'v1.0')"
        Write-Host ""
        Write-Host "Local Actions:" -ForegroundColor Cyan
        Write-Host "  build      - Build the Docker image only"
        Write-Host "  run        - Build and run container locally"
        Write-Host "  logs       - Show container logs"
        Write-Host "  stop       - Stop and remove container"
        Write-Host "  status     - Show container and image status"
        Write-Host ""
        Write-Host "Docker Hub Actions:" -ForegroundColor Cyan
        Write-Host "  login      - Login to Docker Hub"
        Write-Host "  push       - Build and push image to Docker Hub"
        Write-Host "  pull       - Pull latest image from Docker Hub"
        Write-Host "  run-hub    - Run container from Docker Hub image"
        Write-Host ""
        Write-Host "Registry: $DockerHubRegistry/victor-post-orchestrator:[buildname]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Examples:" -ForegroundColor Green
        Write-Host "  .\deploy.ps1 build delta       # Build local image with 'delta' tag"
        Write-Host "  .\deploy.ps1 push prod         # Build and push 'prod' version to Docker Hub"
        Write-Host "  .\deploy.ps1 run-hub v1.0      # Run 'v1.0' version from Docker Hub"
        Write-Host "  .\deploy.ps1 run latest        # Run 'latest' version locally"
    }
}
