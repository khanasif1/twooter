#!/usr/bin/env python3
"""
Trending Hashtag Extractor for Victor Campaign

This module extracts trending hashtags from the Twooter platform and retrieves
all posts associated with each trending hashtag. It provides functionality to
discover popular hashtags and engage with trending content for Victor Hawthorne's
presidential campaign visibility.
"""

import requests
import json
from typing import List, Dict, Any, Optional
from auth_manager import AuthenticationManager
from posting_manager import PostingManager


class TrendingHashtagExtractor:
    """
    Extracts trending hashtags and associated posts from the Twooter platform.
    
    This class provides functionality to:
    - Retrieve trending hashtags
    - Get all posts for specific hashtags
    - Filter hashtags based on relevance to campaign themes
    - Extract post details for engagement
    """
    
    def __init__(self):
        """Initialize the trending hashtag extractor with authentication."""
        self.config = self._load_config()
        self.auth_manager = AuthenticationManager(
            base_url=self.config['base_url'],
            tokens_db_path="./tokens.db"
        )
        self.posting_manager = None
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from config.json file.
        
        Returns:
            Dict containing configuration data
        """
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            print("✅ Loaded configuration from: config.json")
            return config
        except FileNotFoundError:
            print("❌ Config file not found: config.json")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            raise
    
    def login(self) -> bool:
        """
        Authenticate with the platform using credentials from config.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            bot_creds = self.config['bot_credentials']
            
            # Attempt authentication with fallback methods
            auth_result = self.auth_manager.authenticate_with_fallback(
                username=bot_creds['username'],
                password=bot_creds['password'],
                email=bot_creds['email'],
                display_name=bot_creds['display_name'],
                team_invite_code=self.config.get('team_invite_code'),
                competition_bot_key=self.config.get('competition_bot_key'),
                team_info={
                    'team_name': self.config.get('team_name'),
                    'affiliation': self.config.get('affiliation'),
                    'member_name': self.config.get('member_name'),
                    'member_email': self.config.get('member_email')
                }
            )
            
            if self.auth_manager.is_authenticated():
                self.posting_manager = PostingManager(self.auth_manager)
                print(f"✅ Successfully authenticated as: {self.auth_manager.get_current_user()}")
                return True
            else:
                print("❌ Authentication failed")
                return False
                
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def get_trending_hashtags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve trending hashtags from the platform.
        
        This method fetches the most popular hashtags currently trending on the platform.
        
        Args:
            limit (int): Maximum number of trending hashtags to return
            
        Returns:
            List[Dict[str, Any]]: List of trending hashtag objects containing:
                - name: The hashtag name (with # symbol)
                - count: Number of posts using this hashtag
                - trend_score: Popularity score for the hashtag
                
        Raises:
            Exception: If API call fails or not authenticated
        """
        if not self.auth_manager.is_authenticated():
            raise Exception("❌ Authentication required to get trending hashtags")
        
        trending_url = f"{self.auth_manager.base_url}/tags/trending"
        params = {"limit": limit}
        
        try:
            response = self.auth_manager.session.get(
                trending_url, 
                params=params,
                headers=self.auth_manager.get_auth_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                hashtags = result.get('data', [])
                print(f"📈 Retrieved {len(hashtags)} trending hashtags")
                
                # Log trending hashtags
                for hashtag in hashtags[:10]:  # Show top 10
                    name = hashtag.get('name', 'Unknown')
                    count = hashtag.get('count', 0)
                    print(f"   🏷️ {name} ({count} posts)")
                
                return hashtags
            else:
                error_msg = f"Failed to get trending hashtags: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error getting trending hashtags: {e}")
    
    def get_posts_by_hashtag(self, hashtag: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get all posts associated with a specific hashtag.
        
        Args:
            hashtag (str): The hashtag to search for (with or without # symbol)
            limit (int): Maximum number of posts to return
            
        Returns:
            List[Dict[str, Any]]: List of post objects containing hashtag
            
        Raises:
            Exception: If API call fails
        """
        if not self.posting_manager:
            raise Exception("❌ Not authenticated. Please login first.")
        
        # Ensure hashtag starts with #
        if not hashtag.startswith('#'):
            hashtag = f"#{hashtag}"
        
        try:
            result = self.posting_manager.get_posts_by_hashtag(hashtag, limit=limit)
            posts = result.get('data', [])
            print(f"🏷️ Found {len(posts)} posts for hashtag {hashtag}")
            return posts
            
        except Exception as e:
            print(f"❌ Error getting posts for hashtag {hashtag}: {e}")
            return []
    
    def get_trending_posts_with_hashtags(self, hashtag_limit: int = 5, posts_per_hashtag: int = 10) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get trending hashtags and their associated posts.
        
        Args:
            hashtag_limit (int): Number of trending hashtags to process
            posts_per_hashtag (int): Number of posts to get per hashtag
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary mapping hashtag names to lists of posts
        """
        trending_data = {}
        
        try:
            # Get trending hashtags
            trending_hashtags = self.get_trending_hashtags(limit=hashtag_limit)
            
            if not trending_hashtags:
                print("ℹ️ No trending hashtags found")
                return trending_data
            
            # Get posts for each trending hashtag
            for hashtag_obj in trending_hashtags:
                hashtag_name = hashtag_obj.get('name', '')
                if not hashtag_name:
                    continue
                
                print(f"\n🔍 Processing hashtag: {hashtag_name}")
                posts = self.get_posts_by_hashtag(hashtag_name, limit=posts_per_hashtag)
                
                if posts:
                    trending_data[hashtag_name] = posts
                    print(f"   ✅ Retrieved {len(posts)} posts for {hashtag_name}")
                else:
                    print(f"   ⚠️ No posts found for {hashtag_name}")
            
            return trending_data
            
        except Exception as e:
            print(f"❌ Error getting trending posts with hashtags: {e}")
            return trending_data
    
    def filter_campaign_relevant_hashtags(self, hashtags: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter hashtags based on relevance to Victor Hawthorne's campaign themes.
        
        Args:
            hashtags (List[Dict[str, Any]]): List of hashtag objects
            
        Returns:
            List[Dict[str, Any]]: Filtered list of campaign-relevant hashtags
        """
        # Campaign-relevant keywords
        campaign_keywords = [
            'politics', 'election', 'vote', 'democracy', 'government', 'policy',
            'education', 'climate', 'fairness', 'justice', 'equality', 'rights',
            'worker', 'union', 'healthcare', 'housing', 'economy', 'tax',
            'kingston', 'hawthorne', 'campaign', 'president', 'candidate',
            'progressive', 'reform', 'change', 'future', 'community'
        ]
        
        relevant_hashtags = []
        
        for hashtag in hashtags:
            hashtag_name = hashtag.get('name', '').lower()
            
            # Check if hashtag contains campaign-relevant keywords
            is_relevant = any(keyword in hashtag_name for keyword in campaign_keywords)
            
            if is_relevant:
                relevant_hashtags.append(hashtag)
                print(f"✅ Relevant hashtag: {hashtag.get('name', '')}")
            
        print(f"🎯 Found {len(relevant_hashtags)} campaign-relevant hashtags out of {len(hashtags)} total")
        return relevant_hashtags
    
    def get_campaign_trending_content(self, hashtag_limit: int = 10, posts_per_hashtag: int = 15) -> Dict[str, Any]:
        """
        Get trending content relevant to Victor Hawthorne's campaign.
        
        This method retrieves trending hashtags, filters them for campaign relevance,
        and gets associated posts for engagement.
        
        Args:
            hashtag_limit (int): Number of trending hashtags to analyze
            posts_per_hashtag (int): Number of posts to get per relevant hashtag
            
        Returns:
            Dict[str, Any]: Campaign-relevant trending content with:
                - relevant_hashtags: List of campaign-relevant trending hashtags
                - hashtag_posts: Dictionary mapping hashtags to posts
                - total_posts: Total number of posts for engagement
        """
        try:
            print("🎯 Analyzing trending content for campaign relevance...")
            
            # Get all trending hashtags
            all_trending = self.get_trending_hashtags(limit=hashtag_limit)
            
            # Filter for campaign-relevant hashtags
            relevant_hashtags = self.filter_campaign_relevant_hashtags(all_trending)
            
            if not relevant_hashtags:
                print("ℹ️ No campaign-relevant trending hashtags found")
                return {
                    'relevant_hashtags': [],
                    'hashtag_posts': {},
                    'total_posts': 0
                }
            
            # Get posts for relevant hashtags
            hashtag_posts = {}
            total_posts = 0
            
            for hashtag_obj in relevant_hashtags:
                hashtag_name = hashtag_obj.get('name', '')
                posts = self.get_posts_by_hashtag(hashtag_name, limit=posts_per_hashtag)
                
                if posts:
                    hashtag_posts[hashtag_name] = posts
                    total_posts += len(posts)
            
            result = {
                'relevant_hashtags': relevant_hashtags,
                'hashtag_posts': hashtag_posts,
                'total_posts': total_posts
            }
            
            print(f"📊 Campaign Trending Content Summary:")
            print(f"   🏷️ Relevant hashtags: {len(relevant_hashtags)}")
            print(f"   📱 Total posts for engagement: {total_posts}")
            
            return result
            
        except Exception as e:
            print(f"❌ Error getting campaign trending content: {e}")
            return {
                'relevant_hashtags': [],
                'hashtag_posts': {},
                'total_posts': 0
            }