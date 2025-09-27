# Victor Hawthorne Trending Content Engagement Bot

This folder contains the trending content engagement bot for Victor Hawthorne's campaign. The bot automatically discovers trending hashtags, engages with relevant posts through likes and reposts, and generates AI-powered replies to boost campaign visibility.

## 🚀 Quick Start

### Local Development
1. Copy `.env.example` to `.env` and configure your API keys
2. Install dependencies: `pip install -r requirements.txt`
3. Run the bot: `python trending_orchestrator.py`

### Docker Deployment
```powershell
# Build the Docker image
.\deploy\deploy.ps1 -Action build

# Run locally
.\deploy\deploy.ps1 -Action run

# Push to Docker Hub
.\deploy\deploy.ps1 -Action push -DockerHubUsername "your-username"

# Deploy to Azure
.\deploy\deploy.ps1 -Action deploy-azure -DockerHubUsername "your-username"
```

## 📂 File Structure

```
trend_react/
├── trending_orchestrator.py   # Main orchestrator (endless loop)
├── trending_extractor.py      # Hashtag discovery and post retrieval
├── auth_manager.py            # Authentication management
├── azure_openai_client.py     # AI content generation
├── posting_manager.py         # Social media operations
├── config.json               # Configuration settings
├── .env                      # Environment variables
├── requirements.txt          # Python dependencies
└── deploy/
    ├── Dockerfile           # Docker container configuration
    └── deploy.ps1          # PowerShell deployment script
```

## ⚙️ Core Features

### 1. Trending Hashtag Discovery
- Automatically discovers trending hashtags on Twooter
- Filters hashtags based on campaign relevance
- Configurable relevance scoring and keyword matching

### 2. Post Engagement
- **Like posts** with trending hashtags
- **Repost content** to amplify reach
- **AI-generated replies** that promote Victor's campaign themes

### 3. Intelligent Rate Limiting
- Built-in delays between operations
- Exponential backoff for rate limits
- Configurable timing intervals

### 4. Continuous Monitoring
- Runs in endless loop with configurable intervals
- Proper error handling and recovery
- Detailed logging and progress tracking

## 🔧 Configuration

### Environment Variables (.env)
```
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
TWOOTER_API_KEY=your_twooter_api_key
BOT_USERNAME=your_bot_username
BOT_PASSWORD=your_bot_password
```

### Config Settings (config.json)
- **trending_settings**: Hashtag limits, post limits, timing intervals
- **engagement_settings**: Enable/disable like, repost, reply features
- **campaign_keywords**: Keywords for relevance filtering
- **rate_limiting**: API rate limit handling configuration

## 🤖 AI Integration

The bot uses Azure OpenAI to generate contextual replies that:
- Support Victor Hawthorne's campaign themes
- Engage positively with trending content
- Maintain authentic conversation tone
- Stay under 255 character limit

## 📊 Operation Flow

1. **Discovery Phase**: Extract trending hashtags and filter for relevance
2. **Engagement Phase**: Like and repost relevant posts
3. **Reply Phase**: Generate AI responses and post replies
4. **Rate Limiting**: Apply delays to prevent API throttling
5. **Loop**: Repeat process every 10 minutes (configurable)

## 🐳 Docker Deployment

The bot is fully containerized with:
- Multi-stage build for optimized image size
- Health checks for monitoring
- Persistent data storage for tokens
- Environment variable configuration

## 📈 Monitoring

### Container Logs
```powershell
.\deploy\deploy.ps1 -Action logs
```

### Container Status
```powershell
.\deploy\deploy.ps1 -Action status
```

## 🛠️ Development

### Testing Individual Components
```python
# Test trending extraction
python -c "from trending_extractor import *; extractor = TrendingHashtagExtractor(); print(extractor.get_trending_hashtags())"

# Test AI generation
python -c "from azure_openai_client import *; ai = VictorCampaignTrendingAI(); print(ai.generate_trending_response('test', '#trending'))"
```

### Manual Operations
The bot components can be used individually for testing and development purposes.

## 🔒 Security

- Token-based authentication with secure storage
- Environment variable configuration
- No hardcoded credentials
- Rate limiting to prevent abuse

## 📋 Requirements

- Python 3.12+
- Docker (for containerized deployment)
- Azure OpenAI API access
- Twooter API credentials
- PowerShell (for deployment scripts)

## 🚨 Important Notes

- Configure proper API keys before running
- Monitor rate limits to avoid account suspension
- Review generated content for campaign alignment
- Ensure compliance with platform terms of service

---

**Campaign**: Victor Hawthorne 2024  
**Bot Type**: Trending Content Engagement  
**Status**: Production Ready