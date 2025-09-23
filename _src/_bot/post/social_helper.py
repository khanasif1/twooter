"""
Twooter Team Bot - Main Application

This is the main application file for the Twooter team bot. It provides a complete
command-line interface and programmatic API for team bots to participate in CTF
competitions on the Twooter platform.

The bot supports:
- Team-based authentication with multiple registration methods
- Automated posting, replying, and social interaction
- Command-line interface for manual operations
- Programmatic API for automated workflows
- Comprehensive error handling and logging

Usage Examples:
    # Command line interface
    python team_bot.py --login
    python team_bot.py --post "Hello from our team bot!"
    python team_bot.py --reply 123 "Great point!"
    
    # Programmatic usage
    from team_bot import TwooterTeamBot
    bot = TwooterTeamBot()
    bot.start()
    bot.post("Automated message from team bot")
"""

import argparse
import sys
import time
import signal
import threading
from typing import Optional, List, Dict, Any
from pathlib import Path

# Import our custom modules
from auth_manager import AuthenticationManager
from posting_manager import PostingManager
from config_manager import ConfigurationManager


class TwooterTeamBot:
    """
    Main Twooter team bot class that combines authentication, posting,
    and configuration management into a unified interface.
    
    This class provides both programmatic and command-line interfaces
    for team bots to interact with the Twooter platform during CTF
    competitions.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the team bot with configuration.
        
        Args:
            config_path (Optional[str]): Path to configuration file
        """
        self.config = ConfigurationManager(config_path)
        self.auth_manager: Optional[AuthenticationManager] = None
        self.posting_manager: Optional[PostingManager] = None
        self.running = False
        self.auto_mode = False
        
        print("🤖 Twooter Team Bot initialized")
        
        # Validate configuration
        if not self._validate_setup():
            print("\n⚠️  Configuration issues detected. Please fix before proceeding.")
    
    def _validate_setup(self) -> bool:
        """
        Validate that the bot is properly configured.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        validation = self.config.validate_config()
        
        if not validation['api_settings']:
            print("❌ API settings not configured properly")
            return False
        
        if not validation['bot_credentials']:
            print("❌ Bot credentials not configured")
            print("   Please set username, password, email, and display_name")
            return False
        
        if not validation['team_settings']:
            print("❌ Team settings not configured")
            print("   Please provide team_invite_code, competition_bot_key, or team creation info")
            return False
        
        return True
    
    def start(self) -> bool:
        """
        Start the bot by authenticating and initializing all components.
        
        Returns:
            bool: True if startup successful, False otherwise
        """
        try:
            print("\n🚀 Starting team bot...")
            
            # Initialize authentication manager
            self.auth_manager = AuthenticationManager(
                base_url=self.config.api_settings.base_url,
                tokens_db_path=self.config.database_settings.tokens_db
            )
            
            # Attempt authentication with fallback methods
            auth_result = self.auth_manager.authenticate_with_fallback(
                username=self.config.bot_credentials.username,
                password=self.config.bot_credentials.password,
                email=self.config.bot_credentials.email,
                display_name=self.config.bot_credentials.display_name,
                team_invite_code=self.config.team_settings.team_invite_code,
                competition_bot_key=self.config.team_settings.competition_bot_key,
                team_info=self.config.get_team_info_for_registration()
            )
            
            # Initialize posting manager
            self.posting_manager = PostingManager(self.auth_manager)
            
            self.running = True
            print("✅ Bot started successfully!")
            print(f"👤 Logged in as: {self.auth_manager.get_current_user()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")
            return False
    
    def stop(self):
        """Stop the bot and cleanup resources."""
        print("\n🛑 Stopping team bot...")
        
        self.running = False
        self.auto_mode = False
        
        # Note: We don't logout here to preserve the token for next run
        # Use --logout flag or logout command to explicitly clear tokens
        
        print("✅ Bot stopped successfully")
    
    def post(self, content: str, parent_id: Optional[int] = None,
             embed: Optional[str] = None, media: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new post.
        
        Args:
            content (str): Post content
            parent_id (Optional[int]): ID of parent post for replies
            embed (Optional[str]): URL to embed
            media (Optional[List[str]]): List of media file paths
            
        Returns:
            Optional[Dict[str, Any]]: Post creation result or None if failed
        """
        if not self.posting_manager:
            print("❌ Bot not started. Please call start() first.")
            return None
        
        try:
            return self.posting_manager.create_post(content, parent_id, embed, media)
        except Exception as e:
            print(f"❌ Failed to create post: {e}")
            return None
    
    def like_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """
        Like a post.
        
        Args:
            post_id (int): ID of post to like
            
        Returns:
            Optional[Dict[str, Any]]: Like result or None if failed
        """
        if not self.posting_manager:
            print("❌ Bot not started. Please call start() first.")
            return None
        
        try:
            return self.posting_manager.like_post(post_id)
        except Exception as e:
            print(f"❌ Failed to like post {post_id}: {e}")
            return None
    
    def repost(self, post_id: int) -> Optional[Dict[str, Any]]:
        """
        Repost a post.
        
        Args:
            post_id (int): ID of post to repost
            
        Returns:
            Optional[Dict[str, Any]]: Repost result or None if failed
        """
        if not self.posting_manager:
            print("❌ Bot not started. Please call start() first.")
            return None
        
        try:
            return self.posting_manager.repost(post_id)
        except Exception as e:
            print(f"❌ Failed to repost {post_id}: {e}")
            return None
    
    def create_thread(self, posts: List[str], delay_seconds: float = 1.0) -> Optional[List[Dict[str, Any]]]:
        """
        Create a thread of connected posts.
        
        Args:
            posts (List[str]): List of post contents
            delay_seconds (float): Delay between posts
            
        Returns:
            Optional[List[Dict[str, Any]]]: Thread creation results or None if failed
        """
        if not self.posting_manager:
            print("❌ Bot not started. Please call start() first.")
            return None
        
        try:
            return self.posting_manager.create_thread(posts, delay_seconds)
        except Exception as e:
            print(f"❌ Failed to create thread: {e}")
            return None
    
    def get_trending_posts(self, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get trending posts from the platform.
        
        Args:
            limit (int): Number of trending posts to retrieve (default: 10)
            
        Returns:
            Optional[Dict[str, Any]]: Trending posts data or None if failed
        """
        if not self.posting_manager:
            print("❌ Bot not started. Call start() first.")
            return None
        
        try:
            trending = self.posting_manager.get_trending_posts(limit=limit)
            posts = trending.get('data', [])
            print(f"📈 Retrieved {len(posts)} trending posts")
            return trending
        except Exception as e:
            print(f"❌ Failed to get trending posts: {e}")
            return None
    
    def get_latest_posts(self, limit: int = 10, at_iso: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get latest posts from the platform.
        
        Args:
            limit (int): Number of latest posts to retrieve (default: 10)
            at_iso (Optional[str]): ISO timestamp to get posts from specific time
            
        Returns:
            Optional[Dict[str, Any]]: Latest posts data or None if failed
        """
        if not self.posting_manager:
            print("❌ Bot not started. Call start() first.")
            return None
        
        try:
            latest = self.posting_manager.get_latest_posts(limit=limit, at_iso=at_iso)
            posts = latest.get('data', [])
            if at_iso:
                print(f"🕐 Retrieved {len(posts)} posts from {at_iso}")
            else:
                print(f"🕐 Retrieved {len(posts)} latest posts")
            return latest
        except Exception as e:
            print(f"❌ Failed to get latest posts: {e}")
            return None
    
    def get_home_feed(self, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get personalized home feed (requires authentication).
        
        Args:
            limit (int): Number of posts to retrieve (default: 10)
            
        Returns:
            Optional[Dict[str, Any]]: Home feed data or None if failed
        """
        if not self.posting_manager:
            print("❌ Bot not started. Call start() first.")
            return None
        
        try:
            home = self.posting_manager.get_home_feed(limit=limit)
            posts = home.get('data', [])
            print(f"🏠 Retrieved {len(posts)} posts from home feed")
            return home
        except Exception as e:
            print(f"❌ Failed to get home feed: {e}")
            return None
    
    def get_explore_feed(self, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get explore/discovery feed.
        
        Args:
            limit (int): Number of posts to retrieve (default: 10)
            
        Returns:
            Optional[Dict[str, Any]]: Explore feed data or None if failed
        """
        if not self.posting_manager:
            print("❌ Bot not started. Call start() first.")
            return None
        
        try:
            explore = self.posting_manager.get_explore_feed(limit=limit)
            posts = explore.get('data', [])
            print(f"🔍 Retrieved {len(posts)} posts from explore feed")
            return explore
        except Exception as e:
            print(f"❌ Failed to get explore feed: {e}")
            return None
    
    def create_post(self, content: str, parent_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Create a new post on the platform.
        
        Args:
            content (str): Post content
            parent_id (Optional[int]): Parent post ID for replies
            
        Returns:
            Optional[Dict[str, Any]]: Created post data or None if failed
        """
        if not self.posting_manager:
            print("❌ Bot not started. Call start() first.")
            return None
        
        try:
            result = self.posting_manager.create_post(content, parent_id)
            
            # Check if we have a successful response with post data
            if result and result.get('data') and result.get('data', {}).get('id'):
                print(f"✅ Post created successfully")
                post_id = result['data'].get('id', 'Unknown')
                print(f"📝 Post ID: {post_id}")
                # Wrap in expected format for consistency
                return {"success": True, "data": result.get('data')}
            else:
                print(f"❌ Failed to create post: {result}")
                return None
        except Exception as e:
            print(f"❌ Failed to create post: {e}")
            return None
    
    def monitor_feeds(self, feed_types: List[str] = None, limit: int = 5, 
                     interval: int = 300, display_content: bool = True):
        """
        Monitor multiple feeds and display new content.
        
        This method continuously monitors specified feeds and displays
        new posts as they appear. Useful for staying updated on platform activity.
        
        Args:
            feed_types (List[str]): Feed types to monitor ['trending', 'latest', 'home', 'explore']
            limit (int): Number of posts to check per feed (default: 5)
            interval (int): Seconds between checks (default: 300 = 5 minutes)
            display_content (bool): Whether to display post content (default: True)
        """
        if not self.posting_manager:
            print("❌ Bot not started. Call start() first.")
            return
        
        if feed_types is None:
            feed_types = ['trending', 'latest']
        
        print(f"📡 Starting feed monitoring...")
        print(f"🔍 Monitoring: {feed_types}")
        print(f"⏱️  Check interval: {interval}s")
        print(f"📊 Posts per feed: {limit}")
        print(f"Press Ctrl+C to stop monitoring\n")
        
        seen_posts = set()  # Track posts we've already seen
        
        try:
            while self.running:
                for feed_type in feed_types:
                    try:
                        print(f"\n📡 Checking {feed_type} feed...")
                        
                        # Get feed data
                        if feed_type == 'trending':
                            feed_data = self.get_trending_posts(limit=limit)
                        elif feed_type == 'latest':
                            feed_data = self.get_latest_posts(limit=limit)
                        elif feed_type == 'home':
                            feed_data = self.get_home_feed(limit=limit)
                        elif feed_type == 'explore':
                            feed_data = self.get_explore_feed(limit=limit)
                        else:
                            print(f"⚠️  Unknown feed type: {feed_type}")
                            continue
                        
                        if not feed_data:
                            continue
                        
                        # Check for new posts
                        posts = feed_data.get('data', [])
                        new_posts = []
                        
                        for post in posts:
                            post_id = post.get('id')
                            if post_id and post_id not in seen_posts:
                                new_posts.append(post)
                                seen_posts.add(post_id)
                        
                        # Display new posts
                        if new_posts:
                            print(f"🆕 {len(new_posts)} new posts in {feed_type} feed:")
                            for post in new_posts:
                                author = post.get('author', {}).get('username', 'Unknown')
                                content = post.get('content', '')
                                post_id = post.get('id', 'N/A')
                                
                                if display_content:
                                    preview = content[:100] + "..." if len(content) > 100 else content
                                    print(f"   📝 @{author} (#{post_id}): {preview}")
                                else:
                                    print(f"   📝 @{author} (#{post_id})")
                        else:
                            print(f"   ℹ️  No new posts in {feed_type} feed")
                        
                    except Exception as e:
                        print(f"⚠️  Error checking {feed_type} feed: {e}")
                
                # Wait before next check
                print(f"\n💤 Waiting {interval}s before next check...")
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Feed monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Feed monitoring error: {e}")
        finally:
            print("📡 Feed monitoring stopped")
    
    def auto_engage(self, keywords: List[str], actions: List[str] = None,
                   check_interval: int = 60, max_actions_per_hour: int = 10):
        """
        Start automated engagement mode.
        
        This method starts an automated process that monitors for posts
        containing specified keywords and performs automated actions.
        
        Args:
            keywords (List[str]): Keywords to monitor for
            actions (List[str]): Actions to perform ('like', 'repost', 'reply')
            check_interval (int): Seconds between checks
            max_actions_per_hour (int): Rate limiting for actions
        """
        if not self.posting_manager:
            print("❌ Bot not started. Please call start() first.")
            return
        
        if actions is None:
            actions = ['like']
        
        self.auto_mode = True
        action_count = 0
        last_reset = time.time()
        
        print(f"🔄 Starting auto-engagement mode")
        print(f"🔍 Monitoring keywords: {keywords}")
        print(f"⚡ Actions: {actions}")
        print(f"⏱️  Check interval: {check_interval}s")
        print(f"🚦 Rate limit: {max_actions_per_hour} actions/hour")
        
        try:
            while self.auto_mode and self.running:
                current_time = time.time()
                
                # Reset action count every hour
                if current_time - last_reset >= 3600:
                    action_count = 0
                    last_reset = current_time
                    print("🔄 Hourly rate limit reset")
                
                # Check if we've hit rate limit
                if action_count >= max_actions_per_hour:
                    print(f"⏸️  Rate limit reached ({max_actions_per_hour}/hour). Waiting...")
                    time.sleep(check_interval)
                    continue
                
                # Search for posts with keywords
                for keyword in keywords:
                    try:
                        results = self.posting_manager.search_posts(keyword, limit=5)
                        posts = results.get('data', [])
                        
                        for post in posts[:2]:  # Limit to 2 posts per keyword per check
                            post_id = post.get('id')
                            if not post_id:
                                continue
                            
                            # Perform actions
                            for action in actions:
                                if action_count >= max_actions_per_hour:
                                    break
                                
                                if action == 'like':
                                    self.like_post(post_id)
                                    action_count += 1
                                elif action == 'repost':
                                    self.repost(post_id)
                                    action_count += 1
                                elif action == 'reply':
                                    reply_text = f"Thanks for sharing about {keyword}! 🤖"
                                    self.post(reply_text, parent_id=post_id)
                                    action_count += 1
                                
                                # Small delay between actions
                                time.sleep(2)
                        
                    except Exception as e:
                        print(f"⚠️  Error processing keyword '{keyword}': {e}")
                
                # Wait before next check
                print(f"💤 Waiting {check_interval}s before next check... (Actions: {action_count}/{max_actions_per_hour})")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n⏹️  Auto-engagement stopped by user")
        finally:
            self.auto_mode = False
    
    def run_interactive_mode(self):
        """
        Run the bot in interactive command-line mode.
        
        This provides a simple command-line interface for manual bot operations.
        """
        if not self.running:
            if not self.start():
                return
        
        print("\n🎮 Entering interactive mode. Type 'help' for commands or 'quit' to exit.")
        
        while self.running:
            try:
                command = input("\nBot> ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    break
                elif command == 'help':
                    self._print_help()
                elif command == 'status':
                    self._print_status()
                elif command.startswith('post '):
                    content = command[5:]
                    self.post(content)
                elif command.startswith('like '):
                    try:
                        post_id = int(command[5:])
                        self.like_post(post_id)
                    except ValueError:
                        print("❌ Invalid post ID. Please provide a number.")
                elif command.startswith('repost '):
                    try:
                        post_id = int(command[7:])
                        self.repost(post_id)
                    except ValueError:
                        print("❌ Invalid post ID. Please provide a number.")
                elif command.startswith('reply '):
                    parts = command[6:].split(' ', 1)
                    if len(parts) >= 2:
                        try:
                            post_id = int(parts[0])
                            content = parts[1]
                            self.post(content, parent_id=post_id)
                        except ValueError:
                            print("❌ Invalid post ID. Please provide a number.")
                    else:
                        print("❌ Usage: reply <post_id> <content>")
                elif command.startswith('trending'):
                    parts = command.split()
                    limit = 10
                    if len(parts) > 1:
                        try:
                            limit = int(parts[1])
                        except ValueError:
                            print("❌ Invalid limit. Using default of 10.")
                    trending = self.get_trending_posts(limit=limit)
                    if trending:
                        posts = trending.get('data', [])
                        print(f"\n📈 TRENDING POSTS ({len(posts)} posts):")
                        for i, post in enumerate(posts, 1):
                            author = post.get('author', {}).get('username', 'Unknown')
                            content = post.get('content', '')[:100] + "..." if len(post.get('content', '')) > 100 else post.get('content', '')
                            post_id = post.get('id', 'N/A')
                            print(f"  {i}. @{author} (#{post_id}): {content}")
                elif command.startswith('latest'):
                    parts = command.split()
                    limit = 10
                    if len(parts) > 1:
                        try:
                            limit = int(parts[1])
                        except ValueError:
                            print("❌ Invalid limit. Using default of 10.")
                    latest = self.get_latest_posts(limit=limit)
                    if latest:
                        posts = latest.get('data', [])
                        print(f"\n🕐 LATEST POSTS ({len(posts)} posts):")
                        for i, post in enumerate(posts, 1):
                            author = post.get('author', {}).get('username', 'Unknown')
                            content = post.get('content', '')[:100] + "..." if len(post.get('content', '')) > 100 else post.get('content', '')
                            post_id = post.get('id', 'N/A')
                            print(f"  {i}. @{author} (#{post_id}): {content}")
                elif command.startswith('home'):
                    parts = command.split()
                    limit = 10
                    if len(parts) > 1:
                        try:
                            limit = int(parts[1])
                        except ValueError:
                            print("❌ Invalid limit. Using default of 10.")
                    home = self.get_home_feed(limit=limit)
                    if home:
                        posts = home.get('data', [])
                        print(f"\n🏠 HOME FEED ({len(posts)} posts):")
                        for i, post in enumerate(posts, 1):
                            author = post.get('author', {}).get('username', 'Unknown')
                            content = post.get('content', '')[:100] + "..." if len(post.get('content', '')) > 100 else post.get('content', '')
                            post_id = post.get('id', 'N/A')
                            print(f"  {i}. @{author} (#{post_id}): {content}")
                elif command.startswith('explore'):
                    parts = command.split()
                    limit = 10
                    if len(parts) > 1:
                        try:
                            limit = int(parts[1])
                        except ValueError:
                            print("❌ Invalid limit. Using default of 10.")
                    explore = self.get_explore_feed(limit=limit)
                    if explore:
                        posts = explore.get('data', [])
                        print(f"\n🔍 EXPLORE FEED ({len(posts)} posts):")
                        for i, post in enumerate(posts, 1):
                            author = post.get('author', {}).get('username', 'Unknown')
                            content = post.get('content', '')[:100] + "..." if len(post.get('content', '')) > 100 else post.get('content', '')
                            post_id = post.get('id', 'N/A')
                            print(f"  {i}. @{author} (#{post_id}): {content}")
                elif command.startswith('monitor '):
                    feed_types_str = command[8:].strip()
                    if feed_types_str:
                        feed_types = [f.strip() for f in feed_types_str.split(',')]
                        print(f"🔄 Starting feed monitoring for: {feed_types}")
                        print("Press Ctrl+C to stop monitoring...")
                        try:
                            self.monitor_feeds(feed_types=feed_types, limit=5, interval=60, display_content=True)
                        except KeyboardInterrupt:
                            print("\n⏹️  Feed monitoring stopped")
                    else:
                        print("❌ Usage: monitor <feed_types> (e.g., monitor trending,latest)")
                elif command == 'config':
                    self.config.print_config_status()
                else:
                    print("❌ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def _print_help(self):
        """Print available commands for interactive mode."""
        print("""
📚 Available Commands:
  help                    - Show this help message
  status                  - Show bot status
  config                  - Show configuration status
  post <content>          - Create a new post
  reply <post_id> <text>  - Reply to a post
  like <post_id>          - Like a post
  repost <post_id>        - Repost a post
  trending [limit]        - Get trending posts (default: 10)
  latest [limit]          - Get latest posts (default: 10)
  home [limit]            - Get home feed posts (default: 10)
  explore [limit]         - Get explore feed posts (default: 10)
  monitor <feeds>         - Monitor feeds (trending,latest,home,explore)
  quit                    - Exit the bot
        """)
    
    def _print_status(self):
        """Print current bot status."""
        print(f"""
🤖 Bot Status:
  Running: {self.running}
  Auto Mode: {self.auto_mode}
  User: {self.auth_manager.get_current_user() if self.auth_manager else 'Not logged in'}
  API: {self.config.api_settings.base_url if self.config.api_settings else 'Not configured'}
        """)
    
    def check_database_health(self):
        """
        Check the health of all database files.
        
        Returns:
            bool: True if all databases are healthy, False otherwise
        """
        import sqlite3
        import os
        
        databases = {
            'tokens.db': self.config.database_settings.tokens_db,
            'personas.db': self.config.database_settings.personas_db,
            'teams.db': self.config.database_settings.teams_db
        }
        
        print("\n🗄️  Database Health Check")
        print("=" * 40)
        
        all_healthy = True
        
        for db_name, db_path in databases.items():
            try:
                # Check if file exists
                if not os.path.exists(db_path):
                    print(f"📁 {db_name}: ⚠️  File not found (will be auto-created)")
                    continue
                
                # Check if database is readable
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    
                    if tables:
                        print(f"📁 {db_name}: ✅ Healthy ({len(tables)} tables)")
                    else:
                        print(f"📁 {db_name}: ⚠️  Empty (will be initialized)")
                        
            except Exception as e:
                print(f"📁 {db_name}: ❌ Error - {e}")
                all_healthy = False
        
        if all_healthy:
            print("\n✅ All databases are healthy!")
        else:
            print("\n⚠️  Some database issues detected")
        
        return all_healthy
    
    def show_database_stats(self):
        """Show statistics about database contents."""
        import sqlite3
        import os
        
        databases = {
            'tokens.db': (self.config.database_settings.tokens_db, 'tokens'),
            'personas.db': (self.config.database_settings.personas_db, 'users'),
            'teams.db': (self.config.database_settings.teams_db, 'teams')
        }
        
        print("\n📊 Database Statistics")
        print("=" * 40)
        
        for db_name, (db_path, table_name) in databases.items():
            try:
                if not os.path.exists(db_path):
                    print(f"📁 {db_name}: File not found")
                    continue
                
                with sqlite3.connect(db_path) as conn:
                    cursor = conn.cursor()
                    
                    # Get record count
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        print(f"📁 {db_name}: {count} records")
                    except sqlite3.OperationalError:
                        print(f"📁 {db_name}: Table '{table_name}' not found (uninitialized)")
                    
                    # Get file size
                    file_size = os.path.getsize(db_path)
                    size_kb = file_size / 1024
                    print(f"   Size: {size_kb:.1f} KB")
                    
            except Exception as e:
                print(f"📁 {db_name}: Error - {e}")
        
        print("\n💡 Note: Databases are auto-created when needed")
    
    def cleanup_databases(self):
        """Clean up expired tokens and optimize databases."""
        print("\n🧹 Database Cleanup")
        print("=" * 30)
        
        if not self.auth_manager:
            print("⚠️  Authentication manager not initialized")
            return
        
        try:
            # Cleanup expired tokens
            import sqlite3
            import os
            from datetime import datetime, timedelta
            
            tokens_db = self.config.database_settings.tokens_db
            
            if os.path.exists(tokens_db):
                with sqlite3.connect(tokens_db) as conn:
                    cursor = conn.cursor()
                    
                    # Count total tokens before cleanup
                    cursor.execute("SELECT COUNT(*) FROM tokens")
                    total_before = cursor.fetchone()[0]
                    
                    # Remove tokens older than 30 days
                    cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
                    cursor.execute("DELETE FROM tokens WHERE created_at < ?", (cutoff_date,))
                    deleted_count = cursor.rowcount
                    
                    # Vacuum to reclaim space
                    cursor.execute("VACUUM")
                    conn.commit()
                    
                    print(f"🗑️  Removed {deleted_count} old tokens")
                    print(f"📊 Tokens: {total_before - deleted_count} remaining")
                    print("✅ Database optimized")
            else:
                print("ℹ️  No tokens database found")
                
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")


def setup_signal_handlers(bot):
    """Setup signal handlers for graceful shutdown."""
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}. Shutting down gracefully...")
        bot.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """
    Main entry point for the command-line interface.
    
    This function parses command-line arguments and executes the appropriate
    bot operations based on the provided parameters.
    """
    parser = argparse.ArgumentParser(
        description="Twooter Team Bot - Automated CTF team participation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --interactive                    # Start interactive mode
  %(prog)s --post "Hello from team bot!"    # Create a post
  %(prog)s --reply 123 "Great point!"       # Reply to post 123
  %(prog)s --like 456                       # Like post 456
  %(prog)s --trending 5                     # Get 5 trending posts
  %(prog)s --latest 10                      # Get 10 latest posts
  %(prog)s --home 15                        # Get 15 home feed posts
  %(prog)s --explore                        # Get explore feed posts (default 10)
  %(prog)s --latest --at-time "2024-08-10T12:34:56"  # Get posts from specific time
  %(prog)s --monitor-feeds trending,latest  # Monitor trending and latest feeds
  %(prog)s --auto-engage ctf,flag,solution  # Auto-engage with keywords
  %(prog)s --config-status                  # Show configuration status
  %(prog)s --create-config                  # Create template config file
  %(prog)s --login                          # Test login
  %(prog)s --logout                         # Logout and clear tokens
  %(prog)s --db-health                      # Check database health
  %(prog)s --db-stats                       # Show database statistics
  %(prog)s --db-cleanup                     # Clean up old database entries
        """
    )
    
    # Configuration options
    parser.add_argument('--config', '-c', help='Path to configuration file')
    parser.add_argument('--config-status', action='store_true', help='Show configuration status and exit')
    parser.add_argument('--create-config', action='store_true', help='Create template configuration file')
    
    # Database options
    parser.add_argument('--db-health', action='store_true', help='Check database health and exit')
    parser.add_argument('--db-stats', action='store_true', help='Show database statistics and exit')
    parser.add_argument('--db-cleanup', action='store_true', help='Clean up expired tokens and exit')
    
    # Authentication options
    parser.add_argument('--login', action='store_true', help='Test login and exit')
    parser.add_argument('--logout', action='store_true', help='Logout and clear stored tokens')
    
    # Posting options
    parser.add_argument('--post', help='Create a post with the specified content')
    parser.add_argument('--reply', nargs=2, metavar=('POST_ID', 'CONTENT'), 
                       help='Reply to a post with specified ID')
    parser.add_argument('--like', type=int, metavar='POST_ID', help='Like a post with specified ID')
    parser.add_argument('--repost', type=int, metavar='POST_ID', help='Repost a post with specified ID')
    parser.add_argument('--thread', nargs='+', help='Create a thread with multiple posts')
    
    # Feed options
    parser.add_argument('--trending', type=int, nargs='?', const=10, metavar='LIMIT',
                       help='Get trending posts (default: 10 posts)')
    parser.add_argument('--latest', type=int, nargs='?', const=10, metavar='LIMIT',
                       help='Get latest posts (default: 10 posts)')
    parser.add_argument('--home', type=int, nargs='?', const=10, metavar='LIMIT',
                       help='Get home feed posts (requires auth, default: 10 posts)')
    parser.add_argument('--explore', type=int, nargs='?', const=10, metavar='LIMIT',
                       help='Get explore feed posts (default: 10 posts)')
    parser.add_argument('--monitor-feeds', help='Monitor feeds continuously (comma-separated: trending,latest,home,explore)')
    parser.add_argument('--monitor-interval', type=int, default=300,
                       help='Seconds between feed checks in monitor mode (default: 300)')
    parser.add_argument('--show-content', action='store_true', default=True,
                       help='Show post content in feed monitoring (default: true)')
    parser.add_argument('--at-time', metavar='ISO_TIMESTAMP',
                       help='Get posts from specific time (ISO format: 2024-08-10T12:34:56)')
    
    # Automation options
    parser.add_argument('--auto-engage', help='Start auto-engagement with comma-separated keywords')
    parser.add_argument('--check-interval', type=int, default=60, 
                       help='Seconds between checks in auto mode (default: 60)')
    parser.add_argument('--rate-limit', type=int, default=10,
                       help='Max actions per hour in auto mode (default: 10)')
    
    # Interface options
    parser.add_argument('--interactive', '-i', action='store_true', help='Start interactive mode')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Handle configuration commands first
    if args.create_config:
        config = ConfigurationManager()
        config.create_template_config()
        return
    
    if args.config_status:
        config = ConfigurationManager(args.config)
        config.print_config_status()
        return
    
    # Handle database commands
    if args.db_health:
        bot = TwooterTeamBot(args.config)
        bot.check_database_health()
        return
    
    if args.db_stats:
        bot = TwooterTeamBot(args.config)
        bot.show_database_stats()
        return
    
    if args.db_cleanup:
        bot = TwooterTeamBot(args.config)
        bot.cleanup_databases()
        return
    
    # Handle authentication commands
    if args.logout:
        # Simple logout that clears token database
        import sqlite3
        import os
        
        try:
            tokens_db = './tokens.db'
            if os.path.exists(tokens_db):
                with sqlite3.connect(tokens_db) as conn:
                    conn.execute("DELETE FROM tokens")
                    conn.commit()
                print("✅ Logged out and cleared stored tokens")
            else:
                print("✅ No stored tokens found")
        except Exception as e:
            print(f"⚠️  Error during logout: {e}")
        return
    
    # Initialize bot
    bot = TwooterTeamBot(args.config)
    setup_signal_handlers(bot)
    
    try:
        # Handle login test
        if args.login:
            if bot.start():
                print("✅ Login test successful!")
                bot.stop()
            else:
                print("❌ Login test failed!")
                sys.exit(1)
            return
        
        # Handle posting commands
        if any([args.post, args.reply, args.like, args.repost, args.thread]):
            if not bot.start():
                sys.exit(1)
            
            if args.post:
                bot.post(args.post)
            
            if args.reply:
                post_id, content = args.reply
                bot.post(content, parent_id=int(post_id))
            
            if args.like:
                bot.like_post(args.like)
            
            if args.repost:
                bot.repost(args.repost)
            
            if args.thread:
                bot.create_thread(args.thread)
            
            bot.stop()
            return
        
        # Handle feed commands
        if any([args.trending, args.latest, args.home, args.explore]):
            if not bot.start():
                sys.exit(1)
            
            if args.trending:
                trending = bot.get_trending_posts(limit=args.trending)
                if trending:
                    posts = trending.get('data', [])
                    print(f"\n📈 TRENDING POSTS ({len(posts)} posts):")
                    for i, post in enumerate(posts, 1):
                        author = post.get('author', {}).get('username', 'Unknown')
                        content = post.get('content', '')[:150] + "..." if len(post.get('content', '')) > 150 else post.get('content', '')
                        post_id = post.get('id', 'N/A')
                        print(f"  {i}. @{author} (#{post_id}): {content}")
            
            if args.latest:
                latest = bot.get_latest_posts(limit=args.latest, at_iso=args.at_time)
                if latest:
                    posts = latest.get('data', [])
                    print(f"\n🕐 LATEST POSTS ({len(posts)} posts):")
                    for i, post in enumerate(posts, 1):
                        author = post.get('author', {}).get('username', 'Unknown')
                        content = post.get('content', '')[:150] + "..." if len(post.get('content', '')) > 150 else post.get('content', '')
                        post_id = post.get('id', 'N/A')
                        created_at = post.get('created_at', 'Unknown time')
                        print(f"  {i}. @{author} (#{post_id}) at {created_at}: {content}")
            
            if args.home:
                home = bot.get_home_feed(limit=args.home)
                if home:
                    posts = home.get('data', [])
                    print(f"\n🏠 HOME FEED ({len(posts)} posts):")
                    for i, post in enumerate(posts, 1):
                        author = post.get('author', {}).get('username', 'Unknown')
                        content = post.get('content', '')[:150] + "..." if len(post.get('content', '')) > 150 else post.get('content', '')
                        post_id = post.get('id', 'N/A')
                        print(f"  {i}. @{author} (#{post_id}): {content}")
            
            if args.explore:
                explore = bot.get_explore_feed(limit=args.explore)
                if explore:
                    posts = explore.get('data', [])
                    print(f"\n🔍 EXPLORE FEED ({len(posts)} posts):")
                    for i, post in enumerate(posts, 1):
                        author = post.get('author', {}).get('username', 'Unknown')
                        content = post.get('content', '')[:150] + "..." if len(post.get('content', '')) > 150 else post.get('content', '')
                        post_id = post.get('id', 'N/A')
                        print(f"  {i}. @{author} (#{post_id}): {content}")
            
            bot.stop()
            return
        
        # Handle feed monitoring
        if args.monitor_feeds:
            if not bot.start():
                sys.exit(1)
            
            feed_types = [f.strip() for f in args.monitor_feeds.split(',')]
            bot.monitor_feeds(
                feed_types=feed_types,
                limit=5,
                interval=args.monitor_interval,
                display_content=args.show_content
            )
            bot.stop()
            return
        
        # Handle auto-engagement mode
        if args.auto_engage:
            if not bot.start():
                sys.exit(1)
            
            keywords = [k.strip() for k in args.auto_engage.split(',')]
            bot.auto_engage(
                keywords=keywords,
                actions=['like', 'repost'],
                check_interval=args.check_interval,
                max_actions_per_hour=args.rate_limit
            )
            bot.stop()
            return
        
        # Default to interactive mode
        if args.interactive or len(sys.argv) == 1:
            bot.run_interactive_mode()
            bot.stop()
            return
        
        # If no specific command, show help
        parser.print_help()
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        bot.stop()
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()