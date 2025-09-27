# Victor Hawthorne Trending Engagement Bot - Deployment Script
# This script builds and deploys the trending engagement bot to Docker Hub and Azure Container Instances

param(
    [string]$Action = "build",  # build, deploy, run, stop, logs, clean
    [string]$ImageName = "victor-trending-react",
    [string]$ImageTag = "latest",
    [string]$DockerHubUsername = "khanasif1",
    [string]$ContainerName = "victor-trending-react",
    [string]$ResourceGroup = "rg_legit",
    [string]$ContainerGroupName = "trending",
    [string]$Location = "australiaeast"
)

# Handle positional parameters if provided (for backwards compatibility)
if ($args.Count -gt 0) {
    $Action = $args[0]
}
if ($args.Count -gt 1) {
    $ImageTag = $args[1]
}
if ($args.Count -gt 2) {
    $DockerHubUsername = $args[2]
}

# Color functions for better output
function Write-Success { param($Message) Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Info { param($Message) Write-Host "ℹ️ $Message" -ForegroundColor Blue }
function Write-Warning { param($Message) Write-Host "⚠️ $Message" -ForegroundColor Yellow }

# Header
Write-Host "🚀 Victor Hawthorne Trending Engagement Bot Deployment" -ForegroundColor Cyan
Write-Host "Action: $Action" -ForegroundColor Yellow
Write-Host "Image: $ImageName`:$ImageTag" -ForegroundColor Yellow
Write-Host "Container: $ContainerName" -ForegroundColor Yellow
Write-Host "="*60

# Verify Docker is running
try {
    docker version | Out-Null
    Write-Success "Docker is running and accessible"
} catch {
    Write-Error "Docker is not running or not accessible. Please start Docker Desktop."
    exit 1
}

switch ($Action.ToLower()) {
    "build" {
        Write-Info "Building Docker image for trending engagement bot..."
        
        # Navigate to the deploy directory
        $deployPath = Split-Path -Parent $PSCommandPath
        Push-Location $deployPath
        
        try {
            # Build the image
            Write-Info "Building image: $ImageName`:$ImageTag"
            docker build -t "$ImageName`:$ImageTag" -f Dockerfile ..
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Successfully built image: $ImageName`:$ImageTag"
                
                # Show image info
                Write-Info "Image information:"
                docker images | Where-Object { $_ -match $ImageName }
            } else {
                Write-Error "Failed to build Docker image"
                exit 1
            }
        } finally {
            Pop-Location
        }
    }
    
    "push" {
        if (-not $DockerHubUsername) {
            Write-Error "DockerHubUsername parameter is required for push action"
            exit 1
        }
        
        Write-Info "Pushing image to Docker Hub..."
        
        # Tag image for Docker Hub
        $dockerHubImage = "$DockerHubUsername/$ImageName`:$ImageTag"
        docker tag "$ImageName`:$ImageTag" $dockerHubImage
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Successfully tagged image as: $dockerHubImage"
            
            # Push to Docker Hub
            Write-Info "Pushing to Docker Hub..."
            docker push $dockerHubImage
            
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Successfully pushed image to Docker Hub: $dockerHubImage"
            } else {
                Write-Error "Failed to push image to Docker Hub"
                exit 1
            }
        } else {
            Write-Error "Failed to tag image for Docker Hub"
            exit 1
        }
    }
    
    "run" {
        Write-Info "Running trending engagement bot container locally..."
        
        # Stop existing container if running
        $existingContainer = docker ps -a --filter "name=$ContainerName" --format "table {{.Names}}" | Where-Object { $_ -eq $ContainerName }
        if ($existingContainer) {
            Write-Warning "Stopping existing container: $ContainerName"
            docker stop $ContainerName
            docker rm $ContainerName
        }
        
        # Check if .env file exists
        $envFile = Join-Path (Split-Path -Parent $PSCommandPath) "..\\.env"
        if (Test-Path $envFile) {
            Write-Info "Using environment file: $envFile"
            $envParam = "--env-file `"$envFile`""
        } else {
            Write-Warning "No .env file found. Container will use default environment variables."
            $envParam = ""
        }
        
        # Run the container
        $runCommand = "docker run -d --name $ContainerName $envParam $ImageName`:$ImageTag"
        Write-Info "Executing: $runCommand"
        
        Invoke-Expression $runCommand
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Successfully started container: $ContainerName"
            
            # Wait a moment and check container status
            Start-Sleep -Seconds 3
            $containerStatus = docker ps --filter "name=$ContainerName" --format "table {{.Names}}\t{{.Status}}"
            Write-Info "Container status:"
            $containerStatus
        } else {
            Write-Error "Failed to start container"
            exit 1
        }
    }
    
    "stop" {
        Write-Info "Stopping trending engagement bot container..."
        
        docker stop $ContainerName
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Successfully stopped container: $ContainerName"
        } else {
            Write-Warning "Container may not be running or may not exist"
        }
    }
    
    "logs" {
        Write-Info "Showing logs for trending engagement bot container..."
        Write-Info "Press Ctrl+C to stop following logs"
        Write-Info "="*50
        
        docker logs -f $ContainerName
    }
    
    "status" {
        Write-Info "Checking trending engagement bot container status..."
        
        # Check if container exists and its status
        $containerInfo = docker ps -a --filter "name=$ContainerName" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        if ($containerInfo -and $containerInfo.Count -gt 1) {
            Write-Success "Container found:"
            $containerInfo
        } else {
            Write-Warning "Container '$ContainerName' not found"
        }
        
        # Show recent logs
        Write-Info "`nRecent logs (last 20 lines):"
        Write-Info "="*30
        try {
            docker logs --tail 20 $ContainerName
        } catch {
            Write-Warning "Could not retrieve logs (container may not be running)"
        }
    }
    
    "clean" {
        Write-Info "Cleaning up trending engagement bot resources..."
        
        # Stop and remove container
        Write-Info "Removing container..."
        docker stop $ContainerName 2>$null
        docker rm $ContainerName 2>$null
        
        # Remove image
        Write-Info "Removing image..."
        docker rmi "$ImageName`:$ImageTag" 2>$null
        
        # Clean up dangling images
        Write-Info "Cleaning up dangling images..."
        docker image prune -f
        
        Write-Success "Cleanup completed"
    }
    
    "deploy-azure" {
        Write-Info "Deploying to Azure Container Instances..."
        
        if (-not $DockerHubUsername) {
            Write-Error "DockerHubUsername parameter is required for Azure deployment"
            exit 1
        }
        
        $dockerHubImage = "$DockerHubUsername/$ImageName`:$ImageTag"
        
        # Check if logged into Azure
        try {
            az account show | Out-Null
            Write-Success "Azure CLI is authenticated"
        } catch {
            Write-Error "Please log in to Azure CLI using 'az login'"
            exit 1
        }
        
        # Create or update container group
        Write-Info "Creating/updating Azure Container Instance..."
        $ContainerGroupName += "$(Get-Date -Format 'HHmm')-$ImageTag"

        $azCommand = @"
                        az container create ``
                        --resource-group $ResourceGroup ``
                        --name $ContainerGroupName ``
                        --image $dockerHubImage ``
                        --restart-policy Always ``
                        --location $Location ``
                        --cpu 1 ``
                        --memory 1.5 ``
                        --os-type Linux ``
                        --log-analytics-workspace legit-laws ``
                        --log-analytics-workspace-key hhtcxdpUG4iUvL2IPy1lxqAj891uUiCsH9U6oI9rqlif56P6Lm7qHdO/K0e2/C0lfWl1LRjc7g44VQsAevCZ3A== ``
                        --environment-variables PYTHONUNBUFFERED=1
"@
        
        Write-Info "Executing Azure deployment command..."
        Invoke-Expression $azCommand
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Successfully deployed to Azure Container Instances"
            Write-Info "Container Group: $ContainerGroupName"
            Write-Info "Resource Group: $ResourceGroup"
            Write-Info "Location: $Location"
        } else {
            Write-Error "Failed to deploy to Azure Container Instances"
            exit 1
        }
    }
    
    default {
        Write-Info "Available actions:"
        Write-Host "  build           - Build Docker image"
        Write-Host "  push            - Push image to Docker Hub (requires -DockerHubUsername)"
        Write-Host "  run             - Run container locally"
        Write-Host "  stop            - Stop running container"
        Write-Host "  logs            - Show container logs"
        Write-Host "  status          - Show container status and recent logs"
        Write-Host "  clean           - Clean up containers and images"
        Write-Host "  deploy-azure    - Deploy to Azure Container Instances"
        Write-Host ""
        Write-Info "Usage examples:"
        Write-Host "  .\deploy.ps1 -Action build"
        Write-Host "  .\deploy.ps1 -Action push -DockerHubUsername 'yourusername'"
        Write-Host "  .\deploy.ps1 -Action run"
        Write-Host "  .\deploy.ps1 -Action deploy-azure -DockerHubUsername 'yourusername'"
    }
}

Write-Host "`n🏁 Deployment script completed!" -ForegroundColor Cyan