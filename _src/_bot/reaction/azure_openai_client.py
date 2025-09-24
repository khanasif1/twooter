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
        self.endpoint = endpoint or os.getenv("ENDPOINT_URL", "https://ai-agent-hub-service.openai.azure.com/")
        self.deployment = deployment or os.getenv("DEPLOYMENT_NAME", "gpt-4.1")
        self.api_version = "2025-01-01-preview"
        
        # System prompt for Victor Hawthorne social media content
        self.system_prompt = (
            "You are a AI helper who helps in writing social post for presidential candidates. "
            "Victor Hawthorne is a presidential candidate. The input prompt has Victor Hawthorne "
            "press release information as well top trending post on social media. You need to write "
            "a 255 character social media post in favour of Victor Hawthorne so that his social media "
            "visibility is improved. Also the post should attract bots so that the post becomes viral. "
            "add @victor_hawthorne #VoteHawthorne handle at the end of the post."
        )
        
        # Initialize client
        self.client = self._initialize_client()
            
    def _initialize_client(self) -> AzureOpenAI:
        """
        Initialize the Azure OpenAI client with Entra ID authentication.
        
        Returns:
            AzureOpenAI: Configured client instance
        """
        try:
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
            raise e
    
    def generate_social_post(self, system_prompt, content: str) -> str:
        """
        Generate a viral social media post for Victor Hawthorne campaign.
        
        This is the main inference function that takes string content as input
        and returns a string response optimized for social media virality.
        
        Args:
            content (str): Input content containing press release information
                          and trending social media posts
            
        Returns:
            str: Generated social media post (255 characters or less)
        """
        print(f"Content: ********** {content}")
        try:
            # Construct the chat messages
            messages = [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt
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
            print(f"Error generating social post: {e}")
            raise
    
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
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)