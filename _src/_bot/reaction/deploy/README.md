# Victor Campaign Reaction Orchestrator - Docker Deployment

A containerized solution for automating Victor Hawthorne's campaign social media mention monitoring and reply generation workflow.

## 🚀 Quick Start

### 1. Local Development
```powershell
# Build and run locally
.\deploy.ps1 run delta

# View logs
.\deploy.ps1 logs
```

### 2. Docker Hub Deployment
```powershell
# Login to Docker Hub (first time only)
.\deploy.ps1 login

# Build and push to Docker Hub
.\deploy.ps1 push delta

# Run from Docker Hub anywhere
.\deploy.ps1 run-hub delta
```

## 📦 What This Does

The container automatically executes the complete Victor Hawthorne campaign mention monitoring workflow:

1. **👂 Mention Monitoring** - Monitors posts mentioning @victor_hawthorne
2. **🤖 AI Reply Generation** - Creates supportive replies using Azure OpenAI
3. **📱 Social Engagement** - Posts replies and engages with mentions
4. **⏱️ Rate Limiting** - Handles API limits with intelligent delays

## 🐳 Docker Hub Registry

- **Repository**: https://hub.docker.com/r/khanasif1/victor-reaction-orchestrator
- **Image**: `khanasif1/victor-reaction-orchestrator`
- **Tags**: `delta`, `shaista`, `smart-citizen`, etc.

## 📋 Available Commands

### Local Development Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `build` | Build Docker image locally | `.\deploy.ps1 build delta` |
| `run` | Build and run container locally | `.\deploy.ps1 run delta` |
| `logs` | Show real-time container logs | `.\deploy.ps1 logs` |
| `stop` | Stop and remove container | `.\deploy.ps1 stop` |
| `status` | Show container and image status | `.\deploy.ps1 status` |

### Docker Hub Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `login` | Login to Docker Hub | `.\deploy.ps1 login` |
| `push` | Build and push image to Docker Hub | `.\deploy.ps1 push delta` |
| `pull` | Pull latest image from Docker Hub | `.\deploy.ps1 pull` |
| `run-hub` | Run container from Docker Hub | `.\deploy.ps1 run-hub delta` |

## 🛠️ Setup Instructions

### Prerequisites
- Docker Desktop installed and running
- PowerShell (Windows)
- Docker Hub account (for cloud deployment)

### Initial Setup

1. **Clone Repository**
   ```powershell
   git clone <repository-url>
   cd twooter\_src\_bot\reaction\deploy
   ```

2. **Configure Application**
   
   Edit `config.json` in the parent directory:
   ```json
   {
     "base_url": "https://social.legitreal.com/api",
     "bot_credentials": {
       "username": "your_bot_username",
       "password": "your_bot_password",
       "email": "bot@yourteam.com",
       "display_name": "Victor Campaign Reaction Bot"
     }
   }
   ```

3. **Azure OpenAI Configuration** (Optional)
   
   For AI reply generation, configure Azure credentials:
   - Set environment variables, or
   - Use Azure CLI: `az login`, or
   - Configure managed identity in cloud environment

### First Deployment

```powershell
# Test locally first
.\deploy.ps1 run delta
.\deploy.ps1 logs    # Verify it's working

# Push to Docker Hub
.\deploy.ps1 login   # Enter Docker Hub credentials
.\deploy.ps1 push delta    # Build and push image

# Deploy anywhere
.\deploy.ps1 run-hub delta # Pull and run from Docker Hub
```

## 🔧 Configuration

### Environment Variables (Optional)

For Azure OpenAI integration, set these environment variables:

```powershell
$env:AZURE_CLIENT_ID = "your-client-id"
$env:AZURE_CLIENT_SECRET = "your-client-secret"
$env:AZURE_TENANT_ID = "your-tenant-id"
```

Or create a `.env` file:
```env
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
ENDPOINT_URL=https://your-azure-openai-endpoint.openai.azure.com/
DEPLOYMENT_NAME=your-gpt-model-deployment
```

### Application Configuration

The application uses `config.json` for:
- Social media platform API endpoint
- Bot authentication credentials
- Campaign-specific settings

## 📊 Monitoring & Troubleshooting

### View Container Logs
```powershell
# Real-time logs
.\deploy.ps1 logs

# Or using Docker directly
docker logs -f victor-reaction-orchestrator
```

### Check Container Status
```powershell
# Container and image status
.\deploy.ps1 status

# All running containers
docker ps

# Resource usage
docker stats victor-reaction-orchestrator
```

### Common Issues

1. **Container won't start**
   ```powershell
   .\deploy.ps1 logs    # Check error messages
   .\deploy.ps1 status  # Verify image exists
   ```

2. **Azure OpenAI authentication fails**
   - Expected behavior if Azure credentials not configured
   - Container will still run mention monitoring and basic replies
   - Configure Azure credentials for AI reply generation

3. **Docker Hub push fails**
   ```powershell
   .\deploy.ps1 login   # Ensure you're logged in
   docker login         # Alternative login method
   ```

4. **Rate limiting (429 errors)**
   - Normal behavior, container handles automatically
   - Uses exponential backoff retry logic
   - Check logs for retry attempts

## 🏗️ Architecture

### Container Structure
```
victor-reaction-orchestrator/
├── Python 3.11-slim base image
├── Application dependencies (requests, beautifulsoup4, openai, etc.)
├── Campaign reaction code
├── Non-root user security
└── Automatic mention monitoring execution
```

### Workflow Process
```
1. Mention Detection → 2. AI Reply Generation → 3. Social Engagement → 4. Rate-Limited Loop
        ↓                    ↓                    ↓              ↓
   @victor_hawthorne      AI-enhanced          Reply + Like +   Intelligent
    mentions detected      replies             Repost actions   delay handling
```

## 🔒 Security Features

- **Non-root execution**: Container runs as `appuser`
- **Minimal base image**: Python 3.11-slim reduces attack surface
- **No secrets in image**: Configuration via mounted files/env vars
- **Rate limiting**: Prevents API abuse

## 📈 Production Deployment

### Azure Container Instances
```powershell
# Deploy to Azure Container Instances
.\ACI-Deployment.ps1 deploy delta

# Monitor deployment
.\ACI-Deployment.ps1 status
.\ACI-Deployment.ps1 logs
```

### Deployment Options

1. **Local Development**
   ```powershell
   .\deploy.ps1 run delta
   ```

2. **Cloud Deployment** 
   ```powershell
   # On any cloud instance with Docker
   .\deploy.ps1 run-hub delta
   ```

3. **Container Orchestration**
   ```yaml
   # docker-compose.yml example
   version: '3.8'
   services:
     victor-reaction-orchestrator:
       image: khanasif1/victor-reaction-orchestrator:latest
       container_name: victor-reaction
       restart: unless-stopped
       volumes:
         - ./config.json:/app/config.json:ro
       environment:
         - AZURE_CLIENT_ID=${AZURE_CLIENT_ID}
         - AZURE_TENANT_ID=${AZURE_TENANT_ID}
   ```

## 🔄 Development Workflow

### Making Changes
```powershell
# 1. Edit source code
# 2. Test locally
.\deploy.ps1 run delta
.\deploy.ps1 logs

# 3. Push updates
.\deploy.ps1 push delta

# 4. Deploy updated version
.\deploy.ps1 run-hub delta
```

### Version Management
```powershell
# Tag specific versions (optional)
docker tag victor-reaction-orchestrator khanasif1/victor-reaction-orchestrator:v1.0
docker push khanasif1/victor-reaction-orchestrator:v1.0
```

## 📝 Logs & Output

### Expected Log Output
```
✅ VictorPostsExtractor initialized
✅ Azure OpenAI client initialized  
✅ Loaded configuration from: /app/config.json
🤖 Twooter Reaction Bot initialized
✅ Social media bot initialized
🎭 Mention Orchestrator initialized
🚀 Starting Mention Monitoring Workflow
...
📊 Reply Summary: 4/5 replies successful
🎯 Mention Processing Complete!
```

### Success Indicators
- ✅ Mentions detected and processed
- ✅ AI replies generated successfully
- ✅ Social engagement completed
- ✅ Rate limiting handled properly

## 🤝 Contributing

1. Fork the repository
2. Make changes locally
3. Test with `.\deploy.ps1 run delta`
4. Submit pull request

## 📞 Support

### Troubleshooting Steps
1. Check container logs: `.\deploy.ps1 logs`
2. Verify configuration: `cat config.json`
3. Test connectivity: `.\deploy.ps1 status`
4. Rebuild image: `.\deploy.ps1 build delta`

### Common Solutions
- **Authentication issues**: Check credentials in `config.json`
- **Network issues**: Verify internet connectivity and API endpoints
- **Resource issues**: Ensure Docker has sufficient memory allocated
- **Rate limiting**: Normal behavior, check retry logic in logs

---

## 📋 Quick Reference

### Essential Commands
```powershell
# Local development
.\deploy-basic.ps1 run delta     # Build and run locally
.\deploy-basic.ps1 logs delta    # View logs

# Production deployment  
.\deploy-basic.ps1 push delta    # Push to Docker Hub
.\deploy-basic.ps1 deploy delta  # Build and push in one step

# Management
.\deploy-basic.ps1 stop delta    # Stop container
.\deploy-basic.ps1 status delta  # Check status
.\deploy-basic.ps1 help          # Show available commands

# Multi-bot deployment
.\pack.ps1                       # Deploy all bot configurations
```

### Key Files
- `deploy-basic.ps1` - Main deployment script with Docker Hub integration
- `Dockerfile` - Container definition with environment variable support 
- `../config.json` - Application configuration
- `../.env` - Environment variables (API keys, endpoints)
- `pack.ps1` - Multi-bot deployment script
- `ACI-Deployment.ps1` - Azure Container Instances deployment
- `README.md` - This documentation

### Docker Hub
- **Repository**: https://hub.docker.com/r/khanasif1/victor-reaction-orchestrator
- **Registry**: khanasif1/victor-reaction-orchestrator
- **Tags**: latest (auto-updated)

## 📈 Azure Container Instance Deployment

### Quick Deploy
```powershell
# Basic deployment
.\ACI-Deployment.ps1 deploy delta

# Custom deployment
.\ACI-Deployment.ps1 deploy -ResourceGroup "production-rg" -Location "eastus2"

# Monitor workflow
.\ACI-Deployment.ps1 logs

# Update to latest version
.\ACI-Deployment.ps1 update

# Clean up everything
.\ACI-Deployment.ps1 cleanup
```

📋 Available Commands:
| Command | Description | Usage |
|---------|-------------|-------|
| deploy | Create resource group and deploy container | `.\ACI-Deployment.ps1 deploy delta` |
| status | Show container status and details | `.\ACI-Deployment.ps1 status` |
| logs | View container execution logs | `.\ACI-Deployment.ps1 logs` |
| restart | Restart the container instance | `.\ACI-Deployment.ps1 restart` |
| update | Update with latest Docker Hub image | `.\ACI-Deployment.ps1 update` |
| delete | Delete container instance only | `.\ACI-Deployment.ps1 delete` |
| cleanup | Delete entire resource group | `.\ACI-Deployment.ps1 cleanup` |
| login | Login to Azure CLI | `.\ACI-Deployment.ps1 login` |

## 🔐 Authentication Requirements

**Important**: Azure Container Instances requires Docker Hub authentication even for public repositories.

During deployment, you'll be prompted for:
- **Docker Hub Username**: Your Docker Hub username (e.g., `khanasif1`)  
- **Docker Hub Password**: Your Docker Hub password or access token

### Getting Docker Hub Access Token
1. Go to [Docker Hub Security Settings](https://hub.docker.com/settings/security)
2. Click "New Access Token"
3. Give it a name (e.g., "Azure ACI Deployment")
4. Select appropriate permissions
5. Copy the generated token
6. Use this token as the password when prompted

## 📊 Monitoring Your Deployment

### Check Status
```powershell
.\ACI-Deployment.ps1 status
```

### View Logs
```powershell
.\ACI-Deployment.ps1 logs
```

### Azure Portal
1. Go to [Azure Portal](https://portal.azure.com)
2. Search for "Container Instances"
3. Find your container group
4. View metrics and logs

## 🔧 Troubleshooting

### Common Issues

1. **"InaccessibleImage" Error**
   - **Cause**: Docker Hub authentication required
   - **Solution**: Provide Docker Hub username and password/token when prompted

2. **Container Status Shows as "Running" But No Output**
   - **Cause**: Container may still be executing workflow
   - **Solution**: Check logs periodically: `az container logs --resource-group rg_legit --name [container-name]`

3. **Cannot Find Container**
   - **Cause**: Using wrong container name
   - **Solution**: List containers: `az container list --resource-group rg_legit --output table`

4. **Deployment Timeout**
   - **Cause**: Azure provisioning delays
   - **Solution**: Wait and check status, or retry deployment

---

*Victor Hawthorne Campaign - Automated Social Media Reaction System*