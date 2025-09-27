"""
Team Bot Posting Manager

This module handles all posting-related functionality for team bots in the Twooter platform.
It provides methods for creating posts (twoots), replies, likes, reposts, and other social
interactions. The module includes comprehensive error handling and response validation.

Key Features:
- Create text posts with optional media and embeds
- Reply to existing posts with threaded conversations
- Like and unlike posts with conflict detection
- Repost and unrepost content with duplicate prevention
- Retrieve post details and reply threads
- Comprehensive error handling and logging
"""

import requests
import json
from typing import Optional, List, Dict, Any, Union
from pathlib import Path


class PostingManager:
    """
    Manages all posting and social interaction functionality for Twooter bots.
    
    This class provides a comprehensive interface for creating content, engaging
    with other users' posts, and retrieving post information. It handles all
    the HTTP communication with the Twooter API and provides meaningful error
    messages for debugging.
    """
    
    def __init__(self, auth_manager):
        """
        Initialize the posting manager with an authentication manager.
        
        Args:
            auth_manager: An instance of AuthenticationManager that handles
                         authentication tokens and headers
        """
        self.auth_manager = auth_manager
        self.base_url = auth_manager.base_url
        self.session = auth_manager.session
    
    def create_post(self, content: str, parent_id: Optional[int] = None,
                   embed: Optional[str] = None, media: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new post (twoot) on the platform.
        
        This method creates a new post with the specified content. Posts can be
        standalone content or replies to existing posts. They can include text,
        embeds (like URLs), and media attachments.
        
        Args:
            content (str): The text content of the post (required)
            parent_id (Optional[int]): ID of the parent post (for replies)
            embed (Optional[str]): URL or content to embed in the post
            media (Optional[List[str]]): List of media file paths to attach
            
        Returns:
            Dict[str, Any]: Response from the API containing post details including:
                - data.id: The ID of the created post
                - data.content: The post content
                - data.author: Author information
                - data.created_at: Timestamp of creation
                
        Raises:
            Exception: If not authenticated or if post creation fails
            
        Example:
            # Simple text post
            result = bot.create_post("Hello from team bot! 🤖")
            
            # Reply to another post
            result = bot.create_post("Great point!", parent_id=123)
            
            # Post with embed
            result = bot.create_post("Check this out:", embed="https://example.com")
        """
        if not self.auth_manager.is_authenticated():
            raise Exception("❌ Not authenticated. Please login first.")
        
        post_url = f"{self.base_url}/twoots/"
        
        # Build the post payload - parent_id is always required by the API
        payload = {
            "content": content,
            "parent_id": parent_id  # API requires this field even if None
        }
        
        if parent_id:
            print(f"📝 Creating reply to post {parent_id}")
        else:
            print(f"📝 Creating new post")
        
        if embed:
            payload["embed"] = embed
            print(f"🔗 Including embed: {embed}")
        
        if media:
            payload["media"] = media
            print(f"📎 Including {len(media)} media files")
        
        try:
            response = self.session.post(
                post_url,
                json=payload,
                headers=self.auth_manager.get_auth_headers()
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                post_id = result.get('data', {}).get('id', 'Unknown')
                print(f"✅ Post created successfully with ID: {post_id}")
                return result
            else:
                error_msg = f"Post creation failed: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error during post creation: {e}")
    
    def like_post(self, post_id: int) -> Dict[str, Any]:
        """
        Like a specific post.
        
        This method adds a like to the specified post. If the post is already
        liked by this user, the API will return an appropriate response.
        
        Args:
            post_id (int): The ID of the post to like
            
        Returns:
            Dict[str, Any]: Response from the like API
            
        Raises:
            Exception: If not authenticated or if like operation fails
        """
        if not self.auth_manager.is_authenticated():
            raise Exception("❌ Not authenticated. Please login first.")
        
        like_url = f"{self.base_url}/twoots/{post_id}/like"
        
        try:
            response = self.session.post(
                like_url,
                json={},
                headers=self.auth_manager.get_auth_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"👍 Liked post {post_id}")
                return result
            elif response.status_code == 409:
                print(f"ℹ️  Post {post_id} already liked")
                return {"status": "already_liked", "post_id": post_id}
            else:
                error_msg = f"Failed to like post {post_id}: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error liking post {post_id}: {e}")
    
    def repost(self, post_id: int) -> Dict[str, Any]:
        """
        Repost (share) a specific post.
        
        This method creates a repost of the specified content, sharing it
        with the bot's followers. Reposts help amplify important content.
        
        Args:
            post_id (int): The ID of the post to repost
            
        Returns:
            Dict[str, Any]: Response from the repost API
            
        Raises:
            Exception: If not authenticated or if repost operation fails
        """
        if not self.auth_manager.is_authenticated():
            raise Exception("❌ Not authenticated. Please login first.")
        
        repost_url = f"{self.base_url}/twoots/{post_id}/repost"
        
        try:
            response = self.session.post(
                repost_url,
                json={},
                headers=self.auth_manager.get_auth_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"🔄 Reposted post {post_id}")
                return result
            elif response.status_code == 409:
                print(f"ℹ️  Post {post_id} already reposted")
                return {"status": "already_reposted", "post_id": post_id}
            else:
                error_msg = f"Failed to repost {post_id}: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error reposting {post_id}: {e}")
    
    def get_trending_posts(self, limit: int = 20) -> Dict[str, Any]:
        """
        Get trending posts from the platform.
        
        This method retrieves the most popular/trending posts currently on the platform.
        These are typically posts with high engagement (likes, reposts, replies).
        
        Args:
            limit (int): Maximum number of trending posts to return (default: 20)
            
        Returns:
            Dict[str, Any]: Response containing trending posts data with:
                - data: List of trending post objects
                - count: Number of posts returned
                - feed_type: "trending"
                
        Raises:
            Exception: If API call fails or authentication is required
            
        Example:
            trending = bot.get_trending_posts(limit=10)
            for post in trending.get('data', []):
                print(f"📈 {post['content'][:100]}...")
        """
        trending_url = f"{self.base_url}/feeds/trending"
        
        params = {"limit": limit}
        
        try:
            response = self.session.get(trending_url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                post_count = len(result.get('data', []))
                print(f"📈 Retrieved {post_count} trending posts")
                
                # Add metadata about the feed type
                result['feed_type'] = 'trending'
                return result
            else:
                error_msg = f"Failed to get trending posts: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error getting trending posts: {e}")
    
    def get_latest_posts(self, limit: int = 20, at_iso: Optional[str] = None) -> Dict[str, Any]:
        """
        Get latest posts from the platform.
        
        This method retrieves the most recent posts chronologically.
        You can optionally specify a timestamp to get posts from a specific time.
        
        Args:
            limit (int): Maximum number of latest posts to return (default: 20)
            at_iso (Optional[str]): ISO timestamp to get posts from specific time
            
        Returns:
            Dict[str, Any]: Response containing latest posts data with:
                - data: List of latest post objects  
                - count: Number of posts returned
                - feed_type: "latest"
                
        Raises:
            Exception: If API call fails or authentication is required
            
        Example:
            # Get latest posts
            latest = bot.get_latest_posts(limit=10)
            
            # Get posts from specific time
            latest = bot.get_latest_posts(at_iso="2024-08-10T12:34:56")
        """
        latest_url = f"{self.base_url}/feeds/latest"
        
        params = {"limit": limit}
        if at_iso:
            params["at"] = at_iso
        
        try:
            response = self.session.get(latest_url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                post_count = len(result.get('data', []))
                if at_iso:
                    print(f"🕐 Retrieved {post_count} posts from {at_iso}")
                else:
                    print(f"🕐 Retrieved {post_count} latest posts")
                
                # Add metadata about the feed type
                result['feed_type'] = 'latest'
                return result
            else:
                error_msg = f"Failed to get latest posts: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error getting latest posts: {e}")
    
    def get_posts_by_hashtag(self, hashtag: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get posts containing a specific hashtag.
        
        Args:
            hashtag (str): Hashtag to search for (with or without # symbol)
            limit (int): Maximum number of posts to return (default: 20)
            
        Returns:
            Dict[str, Any]: Response containing posts with the hashtag
            
        Raises:
            Exception: If API call fails
        """
        # Ensure hashtag starts with #
        if not hashtag.startswith('#'):
            hashtag = f"#{hashtag}"
        
        search_url = f"{self.base_url}/search"
        params = {
            "query": hashtag,
            "limit": limit
        }
        
        try:
            response = self.session.get(search_url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                post_count = len(result.get('data', []))
                print(f"🏷️ Retrieved {post_count} posts with hashtag {hashtag}")
                return result
            else:
                error_msg = f"Failed to get posts for hashtag {hashtag}: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error getting posts for hashtag {hashtag}: {e}")