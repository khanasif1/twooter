"""
Team Bot Authentication Manager

This module handles authentication for team bots in the Twooter CTF platform.
It supports multiple authentication methods:
1. Standard login with existing credentials
2. Team registration using invite codes
3. Bot registration using competition bot keys
4. New team creation for independent teams

The authentication manager handles token storage, session management,
and automatic fallback between different registration methods.
"""

import requests
import json
import sqlite3
import os
from typing import Optional, Dict, Any
from pathlib import Path


class AuthenticationManager:
    """
    Manages authentication for Twooter team bots.
    
    This class handles the complete authentication flow including:
    - Token storage and retrieval from local SQLite database
    - Multiple registration methods for different competition scenarios
    - Session management with automatic token refresh
    - Error handling and fallback authentication methods
    """
    
    def __init__(self, base_url: str, tokens_db_path: str = "./tokens.db"):
        """
        Initialize the authentication manager.
        
        Args:
            base_url (str): The base URL of the Twooter API (e.g., "https://social.legitreal.com/api")
            tokens_db_path (str): Path to the SQLite database for storing authentication tokens
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.tokens_db_path = tokens_db_path
        self.current_token = None
        self.current_username = None
        
        # Initialize token database
        self._init_token_db()
    
    def _init_token_db(self):
        """
        Initialize the SQLite database for storing authentication tokens.
        
        Creates a tokens table if it doesn't exist. The table stores:
        - username: The bot's username
        - token: The authentication token
        - user_info: JSON string containing user profile information
        """
        # Ensure the database directory exists
        db_path = Path(self.tokens_db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.tokens_db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    username TEXT PRIMARY KEY,
                    token TEXT NOT NULL,
                    user_info TEXT
                )
            """)
            conn.commit()
    
    def _store_token(self, username: str, token: str, user_info: Dict[str, Any]):
        """
        Store authentication token and user info in the local database.
        
        Args:
            username (str): The username associated with the token
            token (str): The authentication token
            user_info (dict): User profile information returned from the API
        """
        print(f"💾 Storing token for {username}, {token}...")
        with sqlite3.connect(self.tokens_db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO tokens (username, token, user_info)
                VALUES (?, ?, ?)
            """, (username, token, json.dumps(user_info)))
            conn.commit()
    
    def _get_stored_token(self, username: str) -> Optional[str]:
        """
        Retrieve stored authentication token for a username.
        
        Args:
            username (str): The username to lookup
            
        Returns:
            Optional[str]: The stored token if found, None otherwise
        """
        with sqlite3.connect(self.tokens_db_path) as conn:
            cursor = conn.execute("SELECT token FROM tokens WHERE username = ?", (username,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def _validate_stored_token(self, username: str) -> bool:
        """
        Validate a stored token by making a test API call.
        
        Args:
            username (str): The username to validate
            
        Returns:
            bool: True if token is valid, False otherwise
        """
        stored_token = self._get_stored_token(username)
        if not stored_token:
            return False
        
        # Session-based authentication doesn't persist across app restarts
        # due to cookie session expiration, so skip validation for these
        if stored_token == "session_based":
            print(f"🔄 Session-based token found for {username}, but sessions don't persist. Removing...")
            self._remove_stored_token(username)
            return False
        
        # Set token temporarily for validation
        old_token = self.current_token
        old_username = self.current_username
        self.current_token = stored_token
        self.current_username = username
        
        try:
            # Test the token with a simple API call
            test_url = f"{self.base_url}/auth/me"
            response = self.session.get(test_url, headers=self.get_auth_headers())
            
            if response.status_code == 200:
                print(f"✅ Using stored token for {username}")
                return True
            else:
                print(f"🔄 Stored token for {username} expired, removing...")
                self._remove_stored_token(username)
                return False
        except Exception:
            print(f"🔄 Stored token for {username} invalid, removing...")
            self._remove_stored_token(username)
            return False
        finally:
            # Restore original state if validation failed
            if not (response.status_code == 200 if 'response' in locals() else False):
                self.current_token = old_token
                self.current_username = old_username
    
    def _remove_stored_token(self, username: str):
        """
        Remove stored authentication token for a username.
        
        Args:
            username (str): The username to remove
        """
        with sqlite3.connect(self.tokens_db_path) as conn:
            conn.execute("DELETE FROM tokens WHERE username = ?", (username,))
            conn.commit()
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Authenticate with existing credentials using standard login.
        
        This method attempts to log in with the provided username and password.
        If successful, it stores the authentication token for future use.
        
        Args:
            username (str): The bot's username
            password (str): The bot's password
            
        Returns:
            Dict[str, Any]: Response from the login API containing user info and token
            
        Raises:
            Exception: If login fails with detailed error message
        """
        login_url = f"{self.base_url}/auth/login"
        
        payload = {
            "username": username,
            "password": password
        }
        
        response = self.session.post(
            login_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract token from response (could be in different places)
            token = None
            if 'token' in result:
                token = result['token']
            elif 'access_token' in result:
                token = result['access_token']
            
            # Store token and user info
            if token:
                self.current_token = token
                self.current_username = username
                self._store_token(username, token, result)
            else:
                # For session-based authentication, use cookies
                self.current_token = "session_based"
                self.current_username = username
                self._store_token(username, "session_based", result)
            
            print(f"✅ Login successful for {username}")
            return result
        else:
            error_msg = f"Login failed: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            raise Exception(error_msg)
    
    def register_with_team_invite(self, username: str, password: str, email: str, 
                                display_name: str, team_invite_code: str) -> Dict[str, Any]:
        """
        Register the bot as part of an existing team using an invite code.
        
        This method is used when you want your bot to join an existing team
        in a CTF competition. The team admin provides an invite code that
        allows the bot to register and become part of the team.
        
        Args:
            username (str): Desired username for the bot
            password (str): Password for the bot account
            email (str): Email address for the bot
            display_name (str): Display name for the bot (shown to other users)
            team_invite_code (str): Invite code provided by the team admin
            
        Returns:
            Dict[str, Any]: Response from the registration API
            
        Raises:
            Exception: If registration fails with detailed error message
        """
        register_url = f"{self.base_url}/auth/register"
        
        payload = {
            "username": username,
            "password": password,
            "email": email,
            "display_name": display_name,
            "invite_code": team_invite_code
        }
        
        response = self.session.post(
            register_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            
            # Extract and store token
            token = result.get('token', 'session_based')
            self.current_token = token
            self.current_username = username
            self._store_token(username, token, result)
            
            print(f"✅ Team registration successful for {username}")
            return result
        else:
            error_msg = f"Team registration failed: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            raise Exception(error_msg)
    
    def register_with_bot_key(self, username: str, password: str, email: str,
                            display_name: str, competition_bot_key: str) -> Dict[str, Any]:
        """
        Register the bot using a competition bot key.
        
        This method is used for official competition bots that have been
        provided with a special bot key by the competition organizers.
        Bot keys typically provide elevated permissions for competition management.
        
        Args:
            username (str): Desired username for the bot
            password (str): Password for the bot account
            email (str): Email address for the bot
            display_name (str): Display name for the bot
            competition_bot_key (str): Special bot key provided by organizers
            
        Returns:
            Dict[str, Any]: Response from the bot registration API
            
        Raises:
            Exception: If bot registration fails with detailed error message
        """
        register_url = f"{self.base_url}/auth/register-bot"
        
        payload = {
            "key": competition_bot_key,
            "username": username,
            "password": password,
            "email": email,
            "display_name": display_name,
            "member_email": email  # Required for bot registration
        }
        
        response = self.session.post(
            register_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            
            # Extract and store token
            token = result.get('token', 'session_based')
            self.current_token = token
            self.current_username = username
            self._store_token(username, token, result)
            
            print(f"✅ Bot registration successful for {username}")
            return result
        else:
            error_msg = f"Bot registration failed: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            raise Exception(error_msg)
    
    def register_new_team(self, username: str, password: str, email: str,
                         display_name: str, team_name: str, affiliation: str,
                         member_name: str, member_email: str) -> Dict[str, Any]:
        """
        Register a new team and make the bot the team admin.
        
        This method creates a completely new team for independent competition
        participation. The bot becomes the team admin and can later invite
        other members to join the team.
        
        Args:
            username (str): Desired username for the bot/team admin
            password (str): Password for the bot account
            email (str): Email address for the bot
            display_name (str): Display name for the bot
            team_name (str): Name of the new team
            affiliation (str): University/organization affiliation
            member_name (str): Name of the first team member
            member_email (str): Email of the first team member
            
        Returns:
            Dict[str, Any]: Response from the team registration API
            
        Raises:
            Exception: If team registration fails with detailed error message
        """
        register_url = f"{self.base_url}/auth/register-team"
        
        payload = {
            "username": username,
            "password": password,
            "email": email,
            "display_name": display_name,
            "team_name": team_name,
            "affiliation": affiliation,
            "member_name": member_name,
            "member_email": member_email
        }
        
        response = self.session.post(
            register_url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            
            # Extract and store token
            token = result.get('token', 'session_based')
            self.current_token = token
            self.current_username = username
            self._store_token(username, token, result)
            
            print(f"✅ Team creation successful for {username} (Team: {team_name})")
            return result
        else:
            error_msg = f"Team creation failed: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
            raise Exception(error_msg)
    
    def authenticate_with_fallback(self, username: str, password: str, email: str,
                                 display_name: str, team_invite_code: Optional[str] = None,
                                 competition_bot_key: Optional[str] = None,
                                 team_info: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Attempt authentication with automatic fallback between methods.
        
        This method implements the complete authentication flow used by the
        Twooter system. It tries multiple methods in order of preference:
        1. Standard login (if credentials already exist)
        2. Bot registration (if bot key provided)
        3. Team registration (if invite code provided)
        4. New team creation (if team info provided)
        
        Args:
            username (str): Bot username
            password (str): Bot password
            email (str): Bot email
            display_name (str): Bot display name
            team_invite_code (Optional[str]): Team invite code (if joining existing team)
            competition_bot_key (Optional[str]): Bot key (if official competition bot)
            team_info (Optional[Dict[str, str]]): Team creation info with keys:
                - team_name: Name of new team
                - affiliation: Organization affiliation
                - member_name: First member name
                - member_email: First member email
                
        Returns:
            Dict[str, Any]: Response from successful authentication method
            
        Raises:
            Exception: If all authentication methods fail
        """
        # Try 0: Check for stored valid token first
        print(f"🔍 Checking for stored token for {username}...")
        if self._validate_stored_token(username):
            # Token is valid, we're already authenticated
            print(f"✅ Using stored authentication for {username}")
            return {"message": "Using stored authentication", "user": {"username": username}}
        
        # Try 1: Standard login first
        try:
            print(f"🔐 Attempting login for {username}...")
            return self.login(username, password)
        except Exception as e:
            print(f"⚠️  Login failed: {e}")
        
        # Try 2: Bot registration if bot key available
        if competition_bot_key and competition_bot_key.strip():
            try:
                print(f"🤖 Attempting bot registration for {username}...")
                return self.register_with_bot_key(username, password, email, display_name, competition_bot_key)
            except Exception as e:
                print(f"⚠️  Bot registration failed: {e}")
        
        # Try 3: Team registration if invite code available
        if team_invite_code and team_invite_code.strip():
            try:
                print(f"👥 Attempting team registration for {username}...")
                return self.register_with_team_invite(username, password, email, display_name, team_invite_code)
            except Exception as e:
                print(f"⚠️  Team registration failed: {e}")
        
        # Try 4: Create new team if team info provided
        if team_info:
            try:
                print(f"🆕 Creating new team for {username}...")
                return self.register_new_team(
                    username, password, email, display_name,
                    team_info['team_name'], team_info['affiliation'],
                    team_info['member_name'], team_info['member_email']
                )
            except Exception as e:
                print(f"⚠️  Team creation failed: {e}")
        
        # All methods failed
        raise Exception("❌ All authentication methods failed. Please check your credentials and configuration.")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns:
            Dict[str, str]: Headers to include in authenticated requests
            
        Raises:
            Exception: If not authenticated
        """
        if not self.current_token:
            raise Exception("Not authenticated. Please login first.")
        
        headers = {"Content-Type": "application/json"}
        
        # Add authorization header for token-based auth
        if self.current_token != "session_based":
            headers["Authorization"] = f"Bearer {self.current_token}"
        
        return headers
    
    def logout(self):
        """
        Logout and clear stored authentication token.
        
        This method attempts to logout from the server and removes
        the locally stored authentication token.
        """
        if self.current_token and self.current_username:
            try:
                # Attempt server logout
                logout_url = f"{self.base_url}/auth/logout"
                self.session.post(logout_url, json={}, headers=self.get_auth_headers())
            except:
                pass  # Ignore logout errors
            
            # Remove stored token
            self._remove_stored_token(self.current_username)
            print(f"✅ Logged out {self.current_username}")
        
        # Clear current session
        self.current_token = None
        self.current_username = None
    
    def is_authenticated(self) -> bool:
        """
        Check if currently authenticated.
        
        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.current_token is not None
    
    def get_current_user(self) -> Optional[str]:
        """
        Get the currently authenticated username.
        
        Returns:
            Optional[str]: Current username if authenticated, None otherwise
        """
        return self.current_username