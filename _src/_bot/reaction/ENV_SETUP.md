# Victor Campaign Reaction Bot - Environment Configuration

## Quick Setup

1. **Copy the environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file with your actual Azure OpenAI credentials:**
   ```bash
   # Open .env file in your editor and replace placeholder values
   AZURE_OPENAI_API_KEY=your-actual-api-key-here
   ENDPOINT_URL=https://your-resource-name.openai.azure.com/
   DEPLOYMENT_NAME=your-deployment-name
   ```

3. **Install dependencies:**
   ```bash
   pip install -r deploy/requirements.txt
   ```

4. **Test the configuration:**
   ```bash
   python azure_openai_client.py
   ```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AZURE_OPENAI_API_KEY` | Your Azure OpenAI API key from Azure Portal | `abc123def456...` |
| `ENDPOINT_URL` | Your Azure OpenAI service endpoint | `https://myservice.openai.azure.com/` |
| `DEPLOYMENT_NAME` | Your model deployment name | `gpt-4` or `gpt-35-turbo` |

## Authentication Methods

The system supports two authentication methods:

### 1. **API Key Authentication** (Recommended for Development)
- Set `AZURE_OPENAI_API_KEY` in your `.env` file
- Quick to set up and test locally
- Best for development and testing

### 2. **Entra ID Authentication** (Recommended for Production)
- Leave `AZURE_OPENAI_API_KEY` empty or unset
- Uses Azure managed identity when deployed to cloud
- More secure for production deployments
- Requires Azure CLI login for local testing: `az login`

## Getting Your Azure OpenAI Credentials

1. **Go to Azure Portal** (https://portal.azure.com)
2. **Navigate to your Azure OpenAI resource**
3. **Go to "Keys and Endpoint" section**
4. **Copy:**
   - API Key (Key 1 or Key 2)
   - Endpoint URL
5. **Go to "Model deployments" to find your deployment name**

## Security Notes

⚠️ **Important**: The `.env` file is excluded from version control (via `.gitignore`) to protect your API keys.

- Never commit your actual `.env` file to git
- Use `.env.example` as a template for team members
- For production deployments, use Azure managed identity instead of API keys

## Docker Deployment

When deploying with Docker, you can:

1. **Mount the .env file:**
   ```bash
   docker run -v $(pwd)/.env:/app/.env your-image
   ```

2. **Pass environment variables directly:**
   ```bash
   docker run -e AZURE_OPENAI_API_KEY=your-key your-image
   ```

3. **Use Azure Container Instances with managed identity** (recommended for production)

## Troubleshooting

### Common Issues:

1. **401 Authentication Error:**
   - Check your API key is correct
   - Verify the endpoint URL matches your Azure resource
   - Ensure your Azure subscription is active

2. **Module Import Errors:**
   - Install dependencies: `pip install -r deploy/requirements.txt`
   - Activate virtual environment if using one

3. **Environment Variables Not Loading:**
   - Ensure `.env` file is in the same directory as the script
   - Check file permissions are readable
   - Verify no syntax errors in `.env` file format

For more help, run the diagnostic tools built into the client:
```bash
python azure_openai_client.py
```