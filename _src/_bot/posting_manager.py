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
    
    def get_post(self, post_id: int) -> Dict[str, Any]:
        """
        Retrieve details of a specific post.
        
        Args:
            post_id (int): The ID of the post to retrieve
            
        Returns:
            Dict[str, Any]: Post details including content, author, timestamps, etc.
            
        Raises:
            Exception: If post retrieval fails or post not found
        """
        post_url = f"{self.base_url}/twoots/{post_id}/"
        
        try:
            response = self.session.get(post_url)
            
            if response.status_code == 200:
                result = response.json()
                print(f"📖 Retrieved post {post_id}")
                return result
            elif response.status_code == 404:
                raise Exception(f"❌ Post {post_id} not found")
            else:
                error_msg = f"Failed to retrieve post {post_id}: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error retrieving post {post_id}: {e}")
    
    def get_post_replies(self, post_id: int) -> Dict[str, Any]:
        """
        Retrieve all replies to a specific post.
        
        Args:
            post_id (int): The ID of the parent post
            
        Returns:
            Dict[str, Any]: List of reply posts
            
        Raises:
            Exception: If reply retrieval fails
        """
        replies_url = f"{self.base_url}/twoots/{post_id}/replies"
        
        try:
            response = self.session.get(replies_url)
            
            if response.status_code == 200:
                result = response.json()
                reply_count = len(result.get('data', []))
                print(f"💬 Retrieved {reply_count} replies to post {post_id}")
                return result
            else:
                error_msg = f"Failed to retrieve replies for post {post_id}: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error retrieving replies for post {post_id}: {e}")
    
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
    
    def unlike_post(self, post_id: int) -> Dict[str, Any]:
        """
        Remove like from a specific post.
        
        Args:
            post_id (int): The ID of the post to unlike
            
        Returns:
            Dict[str, Any]: Response from the unlike API
            
        Raises:
            Exception: If not authenticated or if unlike operation fails
        """
        if not self.auth_manager.is_authenticated():
            raise Exception("❌ Not authenticated. Please login first.")
        
        unlike_url = f"{self.base_url}/twoots/{post_id}/like"
        
        try:
            response = self.session.delete(
                unlike_url,
                headers=self.auth_manager.get_auth_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"👎 Unliked post {post_id}")
                return result
            elif response.status_code == 409:
                print(f"ℹ️  Post {post_id} was not liked")
                return {"status": "not_liked", "post_id": post_id}
            else:
                error_msg = f"Failed to unlike post {post_id}: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error unliking post {post_id}: {e}")
    
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
    
    def unrepost(self, post_id: int) -> Dict[str, Any]:
        """
        Remove a repost of a specific post.
        
        Args:
            post_id (int): The ID of the post to unrepost
            
        Returns:
            Dict[str, Any]: Response from the unrepost API
            
        Raises:
            Exception: If not authenticated or if unrepost operation fails
        """
        if not self.auth_manager.is_authenticated():
            raise Exception("❌ Not authenticated. Please login first.")
        
        unrepost_url = f"{self.base_url}/twoots/{post_id}/repost"
        
        try:
            response = self.session.delete(
                unrepost_url,
                headers=self.auth_manager.get_auth_headers()
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"↩️  Unreposted post {post_id}")
                return result
            elif response.status_code == 409:
                print(f"ℹ️  Post {post_id} was not reposted")
                return {"status": "not_reposted", "post_id": post_id}
            else:
                error_msg = f"Failed to unrepost {post_id}: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error unreposting {post_id}: {e}")
    
    def create_thread(self, posts: List[str], delay_seconds: float = 1.0) -> List[Dict[str, Any]]:
        """
        Create a thread of connected posts.
        
        This method creates multiple posts where each post (except the first)
        is a reply to the previous one, forming a threaded conversation.
        
        Args:
            posts (List[str]): List of post contents to create as a thread
            delay_seconds (float): Delay between posts to avoid rate limiting
            
        Returns:
            List[Dict[str, Any]]: List of responses for each created post
            
        Raises:
            Exception: If thread creation fails at any point
        """
        if not posts:
            raise Exception("❌ No posts provided for thread creation")
        
        print(f"🧵 Creating thread with {len(posts)} posts")
        results = []
        parent_id = None
        
        for i, content in enumerate(posts):
            try:
                # Add thread indicator to posts after the first
                if i > 0:
                    content = f"{content} ({i+1}/{len(posts)})"
                
                result = self.create_post(content, parent_id=parent_id)
                results.append(result)
                
                # Set parent for next post
                parent_id = result.get('data', {}).get('id')
                
                # Delay between posts to avoid rate limiting
                if i < len(posts) - 1 and delay_seconds > 0:
                    import time
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                print(f"❌ Thread creation failed at post {i+1}: {e}")
                raise
        
        print(f"✅ Thread created successfully with {len(results)} posts")
        return results
    
    def bulk_like_posts(self, post_ids: List[int]) -> Dict[str, Any]:
        """
        Like multiple posts in bulk.
        
        Args:
            post_ids (List[int]): List of post IDs to like
            
        Returns:
            Dict[str, Any]: Summary of bulk like operation with success/failure counts
        """
        if not post_ids:
            return {"success": 0, "failed": 0, "results": []}
        
        print(f"👍 Bulk liking {len(post_ids)} posts")
        results = []
        success_count = 0
        failed_count = 0
        
        for post_id in post_ids:
            try:
                result = self.like_post(post_id)
                results.append({"post_id": post_id, "status": "success", "result": result})
                success_count += 1
            except Exception as e:
                results.append({"post_id": post_id, "status": "failed", "error": str(e)})
                failed_count += 1
                print(f"⚠️  Failed to like post {post_id}: {e}")
        
        summary = {
            "success": success_count,
            "failed": failed_count,
            "total": len(post_ids),
            "results": results
        }
        
        print(f"✅ Bulk like completed: {success_count} success, {failed_count} failed")
        return summary
    
    def search_posts(self, query: str, limit: int = 20) -> Dict[str, Any]:
        """
        Search for posts containing specific keywords.
        
        Note: This method assumes a search endpoint exists. Implementation
        may vary based on the actual API specification.
        
        Args:
            query (str): Search query string
            limit (int): Maximum number of results to return
            
        Returns:
            Dict[str, Any]: Search results with matching posts
        """
        search_url = f"{self.base_url}/search/twoots"
        
        params = {
            "q": query,
            "limit": limit
        }
        
        try:
            response = self.session.get(search_url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                result_count = len(result.get('data', []))
                print(f"🔍 Found {result_count} posts matching '{query}'")
                return result
            else:
                error_msg = f"Search failed: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error during search: {e}")
    
    def get_user_posts(self, username: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get posts from a specific user.
        
        Args:
            username (str): Username to get posts from
            limit (int): Maximum number of posts to return
            
        Returns:
            Dict[str, Any]: User's posts
        """
        user_posts_url = f"{self.base_url}/users/{username}/twoots"
        
        params = {"limit": limit}
        
        try:
            response = self.session.get(user_posts_url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                post_count = len(result.get('data', []))
                print(f"📊 Retrieved {post_count} posts from user {username}")
                return result
            else:
                error_msg = f"Failed to get posts for user {username}: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise Exception(error_msg)
                
        except requests.RequestException as e:
            raise Exception(f"Network error getting posts for user {username}: {e}")