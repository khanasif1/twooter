#!/usr/bin/env python3
"""
Azure OpenAI Client for Victor Campaign Trending Content Generation

This module provides an Azure OpenAI client with API key and Entra ID authentication
specifically designed for generating social media responses for trending hashtags
in Victor Hawthorne's presidential campaign.

Features:
- API key and Entra ID authentication fallback
- Optimized prompts for trending hashtag engagement
- 255-character limit enforcement for social media posts
- Error handling and retry logic
"""

import os
from typing import Optional, Dict, Any
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

# Load environment variables from .env file
# Use override=True to ensure .env file takes precedence over system environment variables
load_dotenv(override=True)


class VictorCampaignTrendingAI:
    """
    Azure OpenAI client for Victor Hawthorne campaign trending hashtag engagement.
    """
    
    def __init__(self, endpoint: Optional[str] = None, deployment: Optional[str] = None):
        """
        Initialize the Azure OpenAI client with authentication.
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            deployment: Model deployment name
        """
        # Configuration
        self.endpoint = endpoint or os.getenv("ENDPOINT_URL", "https://ai-agent-hub-service.openai.azure.com/")
        self.deployment = deployment or os.getenv("DEPLOYMENT_NAME", "gpt-4.1")
        self.api_version = "2025-01-01-preview"
        
        # System prompt for Victor Hawthorne trending hashtag responses
        self.system_prompt = (
            "You are an AI helper for Victor Hawthorne's presidential campaign. "
            "Generate engaging social media responses to trending posts that align with Victor's campaign themes. "
            "Victor advocates for fairness, climate action, education reform, worker rights, and progressive policies. "
            "Your responses should be supportive, engaging, and help Victor's visibility in trending conversations. "
            "Keep responses under 255 characters and always include @victor_hawthorne and relevant campaign hashtags "
            "like #VoteHawthorne #Hawthorne2025 #Kingston #KingstonDaily."
        )
        
        # Initialize client
        self.client = self._initialize_client()
            
    def _initialize_client(self) -> AzureOpenAI:
        """
        Initialize the Azure OpenAI client with API key if available, otherwise use Entra ID authentication.
        
        Returns:
            AzureOpenAI: Configured client instance
        """
        try:
            # Check for API key first
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            
            if api_key:
                print("🔑 Using API key authentication")
                print(f"🌐 Endpoint: {self.endpoint}")
                print(f"🚀 Deployment: {self.deployment}")
                print(f"📅 API Version: {self.api_version}")
                
                client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=api_key,
                    api_version=self.api_version,
                )
            else:
                print("🛡️ Using Entra ID authentication")
                print(f"🌐 Endpoint: {self.endpoint}")
                print(f"🚀 Deployment: {self.deployment}")
                print(f"📅 API Version: {self.api_version}")
                
                # Initialize Azure OpenAI client with Entra ID authentication
                token_provider = get_bearer_token_provider(
                    DefaultAzureCredential(),
                    "https://cognitiveservices.azure.com/.default"
                )

                client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    azure_ad_token_provider=token_provider,                
                    api_version=self.api_version,
                )            
        
            return client
            
        except Exception as e:
            print(f"❌ Error initializing Azure OpenAI client: {e}")
            print(f"🔍 Endpoint: {self.endpoint}")
            print(f"🔍 Deployment: {self.deployment}")
            print(f"🔍 API Version: {self.api_version}")
            print(f"🔍 Using API Key: {'Yes' if os.getenv('AZURE_OPENAI_API_KEY') else 'No'}")
            raise e
    
    def generate_trending_response(self, trending_post: str, hashtag: str = "") -> str:
        """
        Generate an engaging response to a trending post for Victor Hawthorne campaign.
        
        Args:
            trending_post (str): The trending post content to respond to
            hashtag (str): The trending hashtag associated with the post
            
        Returns:
            str: Generated response (255 characters or less)
        """
        try:
            content = f"Trending Post: {trending_post}"
            if hashtag:
                content += f"\nTrending Hashtag: {hashtag}"
            content += "\n\nGenerate a supportive response that promotes Victor Hawthorne's campaign."
            
            # Construct the chat messages
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": self.system_prompt
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": content
                        }
                    ]
                }
            ]
            
            # Generate completion
            completion = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=150,  # Limit tokens since we need 255 characters max
                temperature=0.7,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                stream=False
            )
            
            # Extract the generated text
            generated_text = completion.choices[0].message.content
            
            if not generated_text:
                raise ValueError("No content generated from Azure OpenAI")
            
            # Ensure 255 character limit
            if len(generated_text) > 255:
                generated_text = generated_text[:252] + "..."
                print(f"Generated text truncated to 255 characters")
            
            print(f"Successfully generated trending response: {len(generated_text)} characters")
            return generated_text.strip()
            
        except Exception as e:
            print(f"Error generating trending response: {e}")
            raise
    
    def test_connection(self) -> bool:
        """
        Test the Azure OpenAI connection and authentication.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            test_content = "Test connection to Azure OpenAI for Victor Hawthorne trending campaign."
            
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": "You are a helpful assistant. Respond with 'Connection successful' if you receive this message."
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": test_content
                        }
                    ]
                }
            ]
            
            completion = self.client.chat.completions.create(
                model=self.deployment,
                messages=messages,
                max_tokens=10,
                temperature=0,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                stream=False
            )
            
            response = completion.choices[0].message.content
            print("✅ Azure OpenAI connection test successful")
            return "successful" in response.lower()
            
        except Exception as e:
            print(f"❌ Azure OpenAI connection test failed: {e}")
            return False