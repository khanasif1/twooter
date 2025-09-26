# Azure Container Instance (ACI) Deployment Script
param(  [string]$Action = "help", 
        [string]$ContainerName,
        [string]$ResourceGroup = "rg_legit",
        [string]$Location = "australiaeast", 
        [string]$ContainerInstanceName = "reaction-", 
        [string]$DockerHubImage = "khanasif1/victor-win-reaction:", 
        [string]$SubscriptionId = "c0346e61-0f1f-411a-8c22-32620deb01cf")

# Validate ContainerName parameter
if ([string]::IsNullOrWhiteSpace($ContainerName)) {
    Write-Host "❌ Error: ContainerName parameter is required" -ForegroundColor Red
    Write-Host "Usage: .\ACI-Deployment.ps1 [action] [containername]" -ForegroundColor Yellow
    Write-Host "Example: .\ACI-Deployment.ps1 deploy delta" -ForegroundColor Green
    exit 1
}

$DockerHubImage += $ContainerName
$ContainerInstanceName += "$(Get-Date -Format 'HHmm')-$ContainerName"

$AciDnsName = "reaction-$(Get-Date -Format 'HHmm')"

function Write-Info { param([string]$Message); Write-Host "🔍 $Message" -ForegroundColor Cyan }
function Write-Success { param([string]$Message); Write-Host "✅ $Message" -ForegroundColor Green }
function Write-Error { param([string]$Message); Write-Host "❌ $Message" -ForegroundColor Red }
function Write-Warning { param([string]$Message); Write-Host "⚠️ $Message" -ForegroundColor Yellow }

function Test-AzureCLI {
    try {
        $azVersion = az --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Azure CLI is installed"
            return $true
        }
    } catch {
        Write-Error "Azure CLI is not installed"
        Write-Warning "Install from: https://docs.microsoft.com/en-us/cli/azure/"
        return $false
    }
}

function Test-AzureLogin {
    try {
        $account = az account show --output json 2>$null | ConvertFrom-Json
        if ($account) {
            Write-Success "Logged into Azure as: $($account.user.name)"
            return $true
        }
    } catch {
        Write-Error "Not logged into Azure. Run: az login"
        return $false
    }
}

function New-ResourceGroup {
    Write-Info "Creating resource group: $ResourceGroup"
    $rgExists = az group show --name $ResourceGroup --output json 2>$null
    if ($rgExists) {
        Write-Success "Resource group already exists"
        return $true
    }
    az group create --name $ResourceGroup --location $Location --output table
    return ($LASTEXITCODE -eq 0)
}

function New-ContainerInstance {
    Write-Info "Creating Container Instance: $ContainerInstanceName"
    Write-Info "Using image: $DockerHubImage"
    
    # Clean up any existing container with the same name
    Write-Info "Checking for existing container..."
    $existing = az container show --resource-group $ResourceGroup --name $ContainerInstanceName --output json 2>$null
    if ($existing) {
        Write-Warning "Deleting existing container instance..."
        az container delete --resource-group $ResourceGroup --name $ContainerInstanceName --yes --output table
        Start-Sleep -Seconds 10
    }
    
    # Try without registry credentials first (public image)
    Write-Info "Attempting deployment with public access..."
    az container create --resource-group $ResourceGroup --name $ContainerInstanceName --image $DockerHubImage --dns-name-label $AciDnsName --cpu 1 --memory 1.5 --restart-policy Never --location $Location --os-type Linux --log-analytics-workspace legit-laws --log-analytics-workspace-key hhtcxdpUG4iUvL2IPy1lxqAj891uUiCsH9U6oI9rqlif56P6Lm7qHdO/K0e2/C0lfWl1LRjc7g44VQsAevCZ3A== --output table
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Container instance created!"
        return $true
    } else {
        Write-Warning "Public access failed. Attempting with Docker Hub authentication..."
        return New-ContainerInstanceWithAuth
    }
}

function New-ContainerInstanceWithAuth {
    Write-Info "Docker Hub authentication required for ACI deployment"
    $dockerUsername = Read-Host "Enter Docker Hub username"
    $dockerPassword = Read-Host "Enter Docker Hub password or access token" -AsSecureString
    $dockerPasswordText = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($dockerPassword))
    
    Write-Info "Creating container with Docker Hub credentials..."
    az container create --resource-group $ResourceGroup --name $ContainerInstanceName --image $DockerHubImage --dns-name-label $AciDnsName --cpu 0.5 --memory 1.5 --restart-policy Never --location $Location --os-type Linux --registry-login-server "index.docker.io" --registry-username $dockerUsername --registry-password $dockerPasswordText --output table
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Container instance created with authentication!"
        return $true
    } else {
        Write-Error "Failed to create container even with authentication"
        return $false
    }
}

function Get-ContainerStatus {
    Write-Info "Container status:"
    az container show --resource-group $ResourceGroup --name $ContainerInstanceName --output table
}

function Get-ContainerLogs {
    Write-Info "Container logs:"
    az container logs --resource-group $ResourceGroup --name $ContainerInstanceName
}

switch ($Action.ToLower()) {
    "deploy" {
        if ((Test-AzureCLI) -and (Test-AzureLogin) -and (New-ResourceGroup) -and (New-ContainerInstance)) {
            Write-Success "Deployment completed!"
        }
    }
    "status" { 
        if ((Test-AzureCLI) -and (Test-AzureLogin)) { Get-ContainerStatus }
    }
    "logs" { 
        if ((Test-AzureCLI) -and (Test-AzureLogin)) { Get-ContainerLogs }
    }
    "login" {
        Write-Info "Logging into Azure..."
        az login
    }
    default {
        Write-Host "Azure Container Instance Deployment Script" -ForegroundColor Cyan
        Write-Host "Usage: .\ACI-Deployment.ps1 [deploy|status|logs|login] [containername]" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Commands:" -ForegroundColor Green
        Write-Host "  deploy  - Deploy container to Azure"
        Write-Host "  status  - Show container status"
        Write-Host "  logs    - Show container logs" 
        Write-Host "  login   - Login to Azure"
        Write-Host ""
        Write-Host "Example:" -ForegroundColor Yellow
        Write-Host "  .\ACI-Deployment.ps1 deploy delta"
    }
}