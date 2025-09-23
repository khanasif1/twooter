"""
Team Bot Configuration Manager

This module handles configuration file management for team bots in the Twooter platform.
It provides a centralized way to manage bot credentials, team settings, API endpoints,
and other configuration parameters. The configuration supports multiple environments
and includes validation and default value handling.

Key Features:
- JSON-based configuration with validation
- Support for environment-specific settings
- Secure credential management
- Default value handling with override capability
- Configuration file creation and template generation
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class BotCredentials:
    """Data class for bot authentication credentials."""
    username: str
    password: str
    email: str
    display_name: str


@dataclass
class TeamSettings:
    """Data class for team-related configuration."""
    team_invite_code: Optional[str] = None
    competition_bot_key: Optional[str] = None
    team_name: Optional[str] = None
    affiliation: Optional[str] = None
    member_name: Optional[str] = None
    member_email: Optional[str] = None


@dataclass
class APISettings:
    """Data class for API configuration."""
    base_url: str
    timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0


@dataclass
class DatabaseSettings:
    """Data class for database configuration."""
    tokens_db: str = "./tokens.db"
    personas_db: str = "./personas.db"
    teams_db: str = "./teams.db"


class ConfigurationManager:
    """
    Manages configuration for team bots including credentials, team settings,
    and API configuration.
    
    This class provides a unified interface for loading, validating, and
    accessing configuration parameters from JSON files. It supports both
    local configuration files and environment variable overrides.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path (Optional[str]): Path to the configuration file.
                                       If None, will search for config.json
                                       in current directory and standard locations.
        """
        self.config_path = self._resolve_config_path(config_path)
        self.config_data = {}
        
        # Configuration sections
        self.bot_credentials: Optional[BotCredentials] = None
        self.team_settings: Optional[TeamSettings] = None
        self.api_settings: Optional[APISettings] = None
        self.database_settings: Optional[DatabaseSettings] = None
        
        # Load configuration if file exists
        if self.config_path and Path(self.config_path).exists():
            self.load_config()
        else:
            self._create_default_config()
    
    def _resolve_config_path(self, explicit_path: Optional[str]) -> Optional[str]:
        """
        Resolve the configuration file path using multiple search strategies.
        
        Search order:
        1. Explicit path provided
        2. config.json in current working directory
        3. config.json in user's config directory
        4. Environment variable TWOOTER_CONFIG
        
        Args:
            explicit_path (Optional[str]): Explicitly provided config path
            
        Returns:
            Optional[str]: Resolved config file path or None if not found
        """
        # 1. Use explicit path if provided
        if explicit_path:
            return str(Path(explicit_path).expanduser().resolve())
        
        # 2. Check current working directory
        cwd_config = Path.cwd() / "config.json"
        if cwd_config.is_file():
            return str(cwd_config.resolve())
        
        # 3. Check bot directory
        bot_dir_config = Path(__file__).parent / "config.json"
        if bot_dir_config.is_file():
            return str(bot_dir_config.resolve())
        
        # 4. Check environment variable
        env_config = os.getenv('TWOOTER_CONFIG')
        if env_config:
            env_path = Path(env_config).expanduser()
            if env_path.is_file():
                return str(env_path.resolve())
        
        # 5. Default location in current directory
        return str(Path.cwd() / "config.json")
    
    def _create_default_config(self):
        """
        Create a default configuration template.
        
        This method sets up default values for all configuration sections
        when no configuration file is found.
        """
        print("⚠️  No configuration file found. Using default settings.")
        print(f"📄 You can create a config file at: {self.config_path}")
        
        # Set default values
        self.api_settings = APISettings(
            base_url="https://social.legitreal.com/api"
        )
        self.database_settings = DatabaseSettings()
        self.team_settings = TeamSettings()
        
        # Bot credentials must be provided by user
        self.bot_credentials = None
    
    def load_config(self):
        """
        Load configuration from the JSON configuration file.
        
        This method reads the configuration file, validates its contents,
        and populates the configuration objects with the loaded values.
        Environment variables can override configuration file values.
        
        Raises:
            FileNotFoundError: If configuration file is not found
            ValueError: If configuration file contains invalid JSON
            KeyError: If required configuration keys are missing
        """
        if not self.config_path or not Path(self.config_path).exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config_data = json.load(f)
            
            print(f"✅ Loaded configuration from: {self.config_path}")
            
            # Load API settings
            self._load_api_settings()
            
            # Load database settings
            self._load_database_settings()
            
            # Load bot credentials
            self._load_bot_credentials()
            
            # Load team settings
            self._load_team_settings()
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")
        except Exception as e:
            raise Exception(f"Error loading configuration: {e}")
    
    def _load_api_settings(self):
        """Load API configuration settings."""
        base_url = self.config_data.get('base_url')
        if not base_url:
            raise KeyError("Missing required 'base_url' in configuration")
        
        self.api_settings = APISettings(
            base_url=base_url.rstrip('/'),
            timeout=self.config_data.get('timeout', 30),
            retry_attempts=self.config_data.get('retry_attempts', 3),
            retry_delay=self.config_data.get('retry_delay', 1.0)
        )
    
    def _load_database_settings(self):
        """Load database configuration settings."""
        config_dir = Path(self.config_path).parent if self.config_path else Path.cwd()
        
        self.database_settings = DatabaseSettings(
            tokens_db=self._resolve_db_path(
                self.config_data.get('tokens_db', './tokens.db'), config_dir
            ),
            personas_db=self._resolve_db_path(
                self.config_data.get('personas_db', './personas.db'), config_dir
            ),
            teams_db=self._resolve_db_path(
                self.config_data.get('teams_db', './teams.db'), config_dir
            )
        )
    
    def _resolve_db_path(self, db_path: str, config_dir: Path) -> str:
        """
        Resolve database file path relative to configuration directory.
        
        Args:
            db_path (str): Database path from configuration
            config_dir (Path): Configuration file directory
            
        Returns:
            str: Resolved absolute database path
        """
        path = Path(db_path)
        if not path.is_absolute():
            path = config_dir / path
        
        # Create parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        return str(path.resolve())
    
    def _load_bot_credentials(self):
        """Load bot credential settings."""
        creds = self.config_data.get('bot_credentials', {})
        
        # Allow environment variable overrides
        username = os.getenv('TWOOTER_USERNAME') or creds.get('username')
        password = os.getenv('TWOOTER_PASSWORD') or creds.get('password')
        email = os.getenv('TWOOTER_EMAIL') or creds.get('email')
        display_name = os.getenv('TWOOTER_DISPLAY_NAME') or creds.get('display_name')
        
        if username and password and email and display_name:
            self.bot_credentials = BotCredentials(
                username=username,
                password=password,
                email=email,
                display_name=display_name
            )
        else:
            print("⚠️  Bot credentials not fully configured. Some may be missing:")
            print(f"   Username: {'✓' if username else '✗'}")
            print(f"   Password: {'✓' if password else '✗'}")
            print(f"   Email: {'✓' if email else '✗'}")
            print(f"   Display Name: {'✓' if display_name else '✗'}")
    
    def _load_team_settings(self):
        """Load team-related settings."""
        # Allow environment variable overrides
        team_invite_code = (os.getenv('TWOOTER_TEAM_INVITE_CODE') or 
                           self.config_data.get('team_invite_code'))
        competition_bot_key = (os.getenv('TWOOTER_COMPETITION_BOT_KEY') or 
                              self.config_data.get('competition_bot_key'))
        
        self.team_settings = TeamSettings(
            team_invite_code=team_invite_code,
            competition_bot_key=competition_bot_key,
            team_name=self.config_data.get('team_name'),
            affiliation=self.config_data.get('affiliation'),
            member_name=self.config_data.get('member_name'),
            member_email=self.config_data.get('member_email')
        )
    
    def save_config(self, backup: bool = True):
        """
        Save current configuration to the configuration file.
        
        Args:
            backup (bool): Whether to create a backup of existing config file
            
        Raises:
            Exception: If configuration cannot be saved
        """
        if not self.config_path:
            raise Exception("No configuration path specified")
        
        config_path = Path(self.config_path)
        
        # Create backup if requested and file exists
        if backup and config_path.exists():
            backup_path = config_path.with_suffix('.json.backup')
            config_path.rename(backup_path)
            print(f"📁 Created backup: {backup_path}")
        
        # Build configuration dictionary
        config_dict = {}
        
        if self.api_settings:
            config_dict.update(asdict(self.api_settings))
        
        if self.database_settings:
            db_dict = asdict(self.database_settings)
            config_dict.update(db_dict)
        
        if self.bot_credentials:
            config_dict['bot_credentials'] = asdict(self.bot_credentials)
        
        if self.team_settings:
            team_dict = asdict(self.team_settings)
            # Remove None values
            team_dict = {k: v for k, v in team_dict.items() if v is not None}
            config_dict.update(team_dict)
        
        try:
            # Ensure parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_dict, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Configuration saved to: {config_path}")
            
        except Exception as e:
            raise Exception(f"Failed to save configuration: {e}")
    
    def create_template_config(self, output_path: Optional[str] = None):
        """
        Create a template configuration file with example values.
        
        Args:
            output_path (Optional[str]): Path for the template file.
                                       If None, uses default config path.
        """
        template_path = output_path or self.config_path or "config.json"
        
        template_config = {
            "base_url": "https://social.legitreal.com/api",
            "timeout": 30,
            "retry_attempts": 3,
            "retry_delay": 1.0,
            "tokens_db": "./tokens.db",
            "personas_db": "./personas.db",
            "teams_db": "./teams.db",
            "bot_credentials": {
                "username": "your_bot_username",
                "password": "your_bot_password",
                "email": "your_bot@example.com",
                "display_name": "Your Team Bot"
            },
            "team_invite_code": "your_team_invite_code_here",
            "competition_bot_key": "your_competition_bot_key_here",
            "team_name": "Your Team Name",
            "affiliation": "Your University/Organization",
            "member_name": "Team Lead Name",
            "member_email": "teamlead@example.com"
        }
        
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                json.dump(template_config, f, indent=2, ensure_ascii=False)
            
            print(f"📄 Template configuration created: {template_path}")
            print("✏️  Please edit the template with your actual values before using.")
            
        except Exception as e:
            print(f"❌ Failed to create template: {e}")
    
    def validate_config(self) -> Dict[str, bool]:
        """
        Validate the current configuration.
        
        Returns:
            Dict[str, bool]: Validation results for each configuration section
        """
        validation_results = {}
        
        # Validate API settings
        validation_results['api_settings'] = (
            self.api_settings is not None and
            bool(self.api_settings.base_url)
        )
        
        # Validate database settings
        validation_results['database_settings'] = (
            self.database_settings is not None
        )
        
        # Validate bot credentials
        validation_results['bot_credentials'] = (
            self.bot_credentials is not None and
            all([
                self.bot_credentials.username,
                self.bot_credentials.password,
                self.bot_credentials.email,
                self.bot_credentials.display_name
            ])
        )
        
        # Validate team settings (at least one method should be available)
        validation_results['team_settings'] = (
            self.team_settings is not None and
            any([
                self.team_settings.team_invite_code,
                self.team_settings.competition_bot_key,
                all([
                    self.team_settings.team_name,
                    self.team_settings.affiliation,
                    self.team_settings.member_name,
                    self.team_settings.member_email
                ])
            ])
        )
        
        return validation_results
    
    def print_config_status(self):
        """Print the current configuration status."""
        print("\n📋 Configuration Status:")
        print("=" * 50)
        
        if self.config_path:
            print(f"📁 Config file: {self.config_path}")
        else:
            print("📁 Config file: Not set (using defaults)")
        
        validation = self.validate_config()
        
        print(f"\n🔧 API Settings: {'✅' if validation['api_settings'] else '❌'}")
        if self.api_settings:
            print(f"   Base URL: {self.api_settings.base_url}")
            print(f"   Timeout: {self.api_settings.timeout}s")
        
        print(f"\n💾 Database Settings: {'✅' if validation['database_settings'] else '❌'}")
        if self.database_settings:
            print(f"   Tokens DB: {self.database_settings.tokens_db}")
            print(f"   Personas DB: {self.database_settings.personas_db}")
            print(f"   Teams DB: {self.database_settings.teams_db}")
        
        print(f"\n🤖 Bot Credentials: {'✅' if validation['bot_credentials'] else '❌'}")
        if self.bot_credentials:
            print(f"   Username: {self.bot_credentials.username}")
            print(f"   Display Name: {self.bot_credentials.display_name}")
            print(f"   Email: {self.bot_credentials.email}")
            print("   Password: [CONFIGURED]")
        
        print(f"\n👥 Team Settings: {'✅' if validation['team_settings'] else '❌'}")
        if self.team_settings:
            if self.team_settings.team_invite_code:
                print("   Team Invite Code: [CONFIGURED]")
            if self.team_settings.competition_bot_key:
                print("   Competition Bot Key: [CONFIGURED]")
            if self.team_settings.team_name:
                print(f"   Team Name: {self.team_settings.team_name}")
                print(f"   Affiliation: {self.team_settings.affiliation}")
        
        all_valid = all(validation.values())
        print(f"\n🎯 Overall Status: {'✅ Ready to run' if all_valid else '⚠️  Needs configuration'}")
        
        if not all_valid:
            print("\n💡 To fix configuration issues:")
            if not validation['bot_credentials']:
                print("   - Set bot credentials in config.json or environment variables")
            if not validation['team_settings']:
                print("   - Provide team_invite_code, competition_bot_key, or team creation info")
    
    def get_team_info_for_registration(self) -> Optional[Dict[str, str]]:
        """
        Get team information formatted for new team registration.
        
        Returns:
            Optional[Dict[str, str]]: Team info dict or None if not configured
        """
        if not self.team_settings:
            return None
        
        if all([
            self.team_settings.team_name,
            self.team_settings.affiliation,
            self.team_settings.member_name,
            self.team_settings.member_email
        ]):
            return {
                'team_name': self.team_settings.team_name,
                'affiliation': self.team_settings.affiliation,
                'member_name': self.team_settings.member_name,
                'member_email': self.team_settings.member_email
            }
        
        return None