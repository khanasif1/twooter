#!/usr/bin/env python3
"""
Azure OpenAI Client for Victor Campaign Social Media Content Generation

This module provides an Azure OpenAI client with Entra ID authentication
specifically designed for generating social media posts for Victor Hawthorne's
presidential campaign.

Features:
- Entra ID authentication using DefaultAzureCredential
- Optimized prompt for viral social media content generation
- 255-character limit enforcement for social media posts
- Error handling and retry logic
"""

import os
import time
from typing import Optional, Dict, Any
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider


class VictorCampaignAzureOpenAI:
    """
    Azure OpenAI client for Victor Hawthorne campaign content generation.
    """
    
    def __init__(self, endpoint: Optional[str] = None, deployment: Optional[str] = None):
        """
        Initialize the Azure OpenAI client with Entra ID authentication.
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            deployment: Model deployment name
        """
        # Configuration
        self.endpoint = endpoint or os.getenv("ENDPOINT_URL", "https://aoai-legi.services.ai.azure.com/")
        self.deployment = deployment or os.getenv("DEPLOYMENT_NAME", "gpt-4.1")
        self.api_version = "2025-01-01-preview"
        
        # System prompt for Victor Hawthorne social media content
        self.system_prompt = (
            "You are a AI helper who helps in writing social post for presidential candidates. "
            "Victor Hawthorne is a presidential candidate. The input prompt may have Victor Hawthorne "
            "press release information,top trending post, post refering Victor Hawthorne. You need to write "
            "a 255 character social media post in favour of Victor Hawthorne so that his social media "
            "visibility is improved. Also the post should attract bots so that the post becomes viral. "
            "add @victor_hawthorne #Kingston #KingstonDaily #Kingston4Hawthorne #VoteHawthorne handle at the end of the post."
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
            api_key = #os.getenv("AZURE_OPENAI_API_KEY")
            # Remove hardcoded key - use environment variable or Entra ID
            
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
    
    def generate_social_post(self, content: str) -> str:
        """
        Generate a viral social media post for Victor Hawthorne campaign.
        
        This is the main inference function that takes string content as input
        and returns a string response optimized for social media virality.
        Includes retry logic for rate limiting.
        
        Args:
            content (str): Input content containing press release information
                          and trending social media posts
            
        Returns:
            str: Generated social media post (255 characters or less)
        """
        print(f"Content: ********** {content}")
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
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
                
                print(f"Successfully generated social post: {len(generated_text)} characters")
                return generated_text.strip()
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limiting error
                if "429" in error_str or "Too Many Requests" in error_str or "RateLimitReached" in error_str:
                    retry_count += 1
                    if retry_count < max_retries:
                        wait_time = 5 * (2 ** (retry_count - 1))  # Exponential backoff: 5s, 10s, 20s
                        print(f"⏳ Azure OpenAI rate limit hit. Waiting {wait_time}s before retry {retry_count}/{max_retries}...")
                        time.sleep(wait_time)
                    else:
                        print(f"❌ Azure OpenAI max retries reached for rate limiting")
                        raise Exception(f"Azure OpenAI rate limit exceeded after {max_retries} retries")
                else:
                    # Non-rate-limit error, don't retry
                    print(f"❌ Azure OpenAI error (non-rate-limit): {e}")
                    raise
        
        # This shouldn't be reached, but just in case
        raise Exception("Failed to generate social post after maximum retries")
    
    def diagnose_authentication_error(self) -> Dict[str, Any]:
        """
        Diagnose common authentication issues and provide troubleshooting information.
        
        Returns:
            Dict containing diagnostic information
        """
        diagnostics = {
            "endpoint": self.endpoint,
            "deployment": self.deployment,
            "api_version": self.api_version,
            "has_api_key": bool(os.getenv("AZURE_OPENAI_API_KEY")),
            "endpoint_format_valid": False,
            "common_issues": [],
            "recommendations": []
        }
        
        # Check endpoint format
        if self.endpoint.startswith("https://") and ".openai.azure.com" in self.endpoint:
            diagnostics["endpoint_format_valid"] = True
        else:
            diagnostics["common_issues"].append("Endpoint format invalid - should be https://[resource-name].openai.azure.com/")
            diagnostics["recommendations"].append("Check your Azure OpenAI resource endpoint URL")
        
        # Check API key if using key authentication
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        if api_key:
            if len(api_key) < 32:
                diagnostics["common_issues"].append("API key appears too short")
                diagnostics["recommendations"].append("Verify the API key is complete and valid")
            
            if not api_key.replace("-", "").replace("_", "").isalnum():
                diagnostics["common_issues"].append("API key contains unexpected characters")
                diagnostics["recommendations"].append("Ensure API key is copied correctly without extra spaces")
        
        # Common 401 error causes
        diagnostics["common_401_causes"] = [
            "Invalid or expired API key",
            "Wrong Azure OpenAI endpoint URL",
            "Incorrect region for your resource", 
            "Resource subscription inactive or suspended",
            "Model deployment name mismatch"
        ]
        
        return diagnostics
    
    def test_connection(self) -> bool:
        """
        Test the Azure OpenAI connection and authentication.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            test_content = "Test connection to Azure OpenAI for Victor Hawthorne campaign."
            
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
            print("Azure OpenAI connection test successful")
            return "successful" in response.lower()
            
        except Exception as e:
            print(f"Azure OpenAI connection test failed: {e}")
            return False


def main():
    """
    Example usage and testing of the Azure OpenAI client.
    """
    print("🤖 Victor Campaign Azure OpenAI Client Test")
    print("=" * 50)
    
    try:
        # Initialize client
        client = VictorCampaignAzureOpenAI()
        
        # Test connection
        print("\n🔍 Testing connection...")
        if client.test_connection():
            print("✅ Connection test passed")
        else:
            print("❌ Connection test failed")
            return 1
        
        # Test content generation
        print("\n📝 Testing content generation...")
        sample_content = """
        Victor Hawthorne Press Release: "A Kingston For All - Building a Future Rooted in Fairness and Opportunity"
        
        Victor's campaign focuses on:
        - Free tertiary education and expanded vocational grants
        - Progressive taxation for fairness
        - Aggressive action on climate change
        - Ending offshore drilling
        - Strengthening worker protections
        - Supporting renters' rights
        
        Trending Social Media Posts:
        - #FairnessForAll is trending
        - People are talking about climate action
        - Education reform is a hot topic
        - Worker rights discussions are viral
        """
        
        generated_post = client.generate_social_post(sample_content)
        
        print(f"✅ Generated post ({len(generated_post)} characters):")
        print(f"📱 \"{generated_post}\"")
        
        if len(generated_post) <= 255:
            print("✅ Post length within 255 character limit")
        else:
            print("❌ Post length exceeds 255 character limit")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # If it's a 401 error or similar authentication issue, provide diagnostics
        if "401" in str(e) or "Access denied" in str(e) or "invalid subscription" in str(e):
            print("\n🔍 Running diagnostics for authentication error...")
            try:
                client = VictorCampaignAzureOpenAI()
                diagnostics = client.diagnose_authentication_error()
                
                print(f"\n📊 Diagnostic Information:")
                print(f"🌐 Endpoint: {diagnostics['endpoint']}")
                print(f"🚀 Deployment: {diagnostics['deployment']}")
                print(f"📅 API Version: {diagnostics['api_version']}")
                print(f"🔑 Has API Key: {diagnostics['has_api_key']}")
                print(f"✅ Endpoint Format Valid: {diagnostics['endpoint_format_valid']}")
                
                if diagnostics['common_issues']:
                    print(f"\n⚠️ Issues Found:")
                    for issue in diagnostics['common_issues']:
                        print(f"   • {issue}")
                
                if diagnostics['recommendations']:
                    print(f"\n💡 Recommendations:")
                    for rec in diagnostics['recommendations']:
                        print(f"   • {rec}")
                
                print(f"\n🔍 Common 401 Error Causes:")
                for cause in diagnostics['common_401_causes']:
                    print(f"   • {cause}")
                    
            except Exception as diag_error:
                print(f"Could not run diagnostics: {diag_error}")
        
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)