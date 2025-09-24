#!/usr/bin/env python3
"""
Victor Hawthorne Posts Extractor

This script extracts posts related to @victor_hawthorne from the Twooter platform:
1. Posts made by @victor_hawthorne 
2. Posts mentioning @victor_hawthorne

Usage:
    python victor_posts_extractor.py
"""

import json
from typing import Dict, List, Any
from auth_manager import AuthenticationManager
from config_manager import ConfigurationManager


class VictorPostsExtractor:
    """
    Extracts posts by and about @victor_hawthorne.
    """
    
    def __init__(self, config_path: str = "./config.json"):
        """
        Initialize the extractor with local config.
        
        Args:
            config_path (str): Path to configuration file
        """
        self.config = ConfigurationManager(config_path)
        self.auth_manager = None
        self.session = None
        
        print("🎯 Victor Hawthorne Posts Extractor initialized")
    
    def login(self) -> bool:
        """
        Login to the Twooter platform.
        
        Returns:
            bool: True if login successful
        """
        try:
            print("🔐 Logging into Twooter platform...")
            
            self.auth_manager = AuthenticationManager(
                base_url=self.config.api_settings.base_url,
                tokens_db_path=self.config.database_settings.tokens_db
            )
            
            # Attempt authentication
            auth_result = self.auth_manager.authenticate_with_fallback(
                username=self.config.bot_credentials.username,
                password=self.config.bot_credentials.password,
                email=self.config.bot_credentials.email,
                display_name=self.config.bot_credentials.display_name,
                team_invite_code=getattr(self.config.team_settings, 'team_invite_code', None) if hasattr(self.config, 'team_settings') else None,
                competition_bot_key=getattr(self.config.team_settings, 'competition_bot_key', None) if hasattr(self.config, 'team_settings') else None,
                team_info=None
            )
            
            if auth_result:
                self.session = self.auth_manager.session
                print("✅ Authentication successful!")
                print(f"👤 Logged in as: {self.auth_manager.get_current_user()}")
                return True
            else:
                print("❌ Authentication failed")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_posts_by_victor_hawthorne(self) -> List[Dict[str, Any]]:
        """
        Get all posts made BY @victor_hawthorne.
        
        Returns:
            List[Dict[str, Any]]: List of posts by Victor Hawthorne
        """
        if not self.session:
            print("❌ Not authenticated. Please login first.")
            return []
        
        try:
            print("📝 Getting posts BY @victor_hawthorne...")
            
            base_url = self.config.api_settings.base_url.rstrip('/')
            activity_url = f"{base_url}/users/@victor_hawthorne/activity"
            
            response = self.session.get(activity_url)
            
            if response.status_code == 200:
                result = response.json()
                posts = result.get('data', [])
                
                # Filter to only posts BY victor_hawthorne (not replies to him)
                victor_posts = []
                for post in posts:
                    author = post.get('author', {})
                    if author.get('username') == 'victor_hawthorne':
                        victor_posts.append(post)
                
                print(f"✅ Found {len(victor_posts)} posts BY @victor_hawthorne")
                return victor_posts
            else:
                print(f"❌ Failed to get posts BY @victor_hawthorne: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting posts BY @victor_hawthorne: {e}")
            return []
    
    def get_posts_mentioning_victor_hawthorne(self) -> List[Dict[str, Any]]:
        """
        Get all posts that mention @victor_hawthorne.
        
        Returns:
            List[Dict[str, Any]]: List of posts mentioning Victor Hawthorne
        """
        if not self.session:
            print("❌ Not authenticated. Please login first.")
            return []
        
        try:
            print("💬 Getting posts MENTIONING @victor_hawthorne...")
            
            base_url = self.config.api_settings.base_url.rstrip('/')
            search_url = f"{base_url}/search"
            
            # Search for posts mentioning @victor_hawthorne
            params = {
                'query': '@victor_hawthorne',
                'limit': 100
            }
            
            response = self.session.get(search_url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                posts = result.get('data', [])
                
                print(f"✅ Found {len(posts)} posts MENTIONING @victor_hawthorne")
                return posts
            else:
                print(f"❌ Failed to search for posts mentioning @victor_hawthorne: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error searching for posts mentioning @victor_hawthorne: {e}")
            return []


def main():
    """
    Main function to extract Victor Hawthorne posts.
    """
    extractor = VictorPostsExtractor()
    
    # Login
    if not extractor.login():
        print("❌ Cannot proceed without authentication")
        return
    
    # Get posts BY Victor Hawthorne
    posts_by_victor = extractor.get_posts_by_victor_hawthorne()
    
    # Get posts MENTIONING Victor Hawthorne  
    posts_mentioning_victor = extractor.get_posts_mentioning_victor_hawthorne()
    
    # Print posts BY Victor Hawthorne
    print("\n📝 Posts BY @victor_hawthorne:")
    for idx, post in enumerate(posts_by_victor, 1):
        print(f"--- Post #{idx} ---")
        print(json.dumps(post, indent=2, ensure_ascii=False))
        print("-------------------\n")

    # Print posts MENTIONING Victor Hawthorne
    print("\n💬 Posts MENTIONING @victor_hawthorne:")
    for idx, post in enumerate(posts_mentioning_victor, 1):
        print(f"--- Mention #{idx} ---")
        print(json.dumps(post, indent=2, ensure_ascii=False))
        print("----------------------\n")
    # Display results
    print(f"\n📊 Results Summary:")
    print(f"   📝 Posts BY @victor_hawthorne: {len(posts_by_victor)}")
    print(f"   💬 Posts MENTIONING @victor_hawthorne: {len(posts_mentioning_victor)}")
    
    print(f"\n🎉 Extraction complete!")


if __name__ == "__main__":
    main()