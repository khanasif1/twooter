# Twooter Team Bot

A comprehensive Python bot for team participation in CTF competitions on the Twooter platform. This bot provides automated posting, engagement, and team coordination capabilities for Capture The Flag (CTF) events.

## 🚀 Features

### Core Functionality
- **Team Authentication**: Multiple authentication methods including team invite codes, competition bot keys, and new team creation
- **Automated Posting**: Create posts, replies, and threaded conversations
- **Social Engagement**: Like, repost, and interact with other users' content
- **Auto-Engagement Mode**: Automatically monitor and engage with posts containing specific keywords
- **Token Management**: Secure local storage of authentication tokens with SQLite
- **Rate Limiting**: Built-in rate limiting to prevent API abuse

### Team Integration
- **Team Registration**: Join existing teams using invite codes
- **Bot Key Support**: Official competition bot registration with special permissions
- **New Team Creation**: Create new teams for independent participation
- **Multi-Environment Support**: Separate configurations for different competitions

### User Interfaces
- **Command Line Interface**: Complete CLI for manual operations
- **Interactive Mode**: Real-time command interface for live operations
- **Programmatic API**: Python API for custom automation scripts
- **Configuration Management**: JSON-based configuration with validation

## 📦 Installation

### Prerequisites
- Python 3.7 or higher
- `requests` library for HTTP operations
- **SQLite database support** (built into Python - no additional installation needed)

### Quick Setup
1. Clone or download the bot files to your `_bot` directory
2. Install required dependencies:
   ```bash
   pip install requests
   ```
3. Create your configuration file (see Configuration section below)
4. **Databases are auto-created** - no database setup required!

### File Structure
```
_bot/
├── team_bot.py          # Main bot application
├── auth_manager.py      # Authentication handling
├── posting_manager.py   # Posting and social features
├── config_manager.py    # Configuration management
├── config.json          # Your bot configuration (create this)
├── tokens.db           # Token storage (auto-created)
├── personas.db         # User data (auto-created)
├── teams.db            # Team info (auto-created)
├── DATABASE.md         # Database documentation
└── README.md           # This documentation
```

## 🗄️ Database Management

### **Zero Setup Required!** ✅

The bot uses **SQLite databases** for local storage. SQLite is built into Python, so:
- **No database software to install**
- **No database configuration needed** 
- **No schema creation required**
- **Databases auto-created when needed**

### Database Files (Auto-Created)
- `tokens.db` - Authentication tokens and session data
- `personas.db` - User credentials and profile information
- `teams.db` - Team configurations and member data

### Database Operations
```bash
# Check database health
python team_bot.py --db-health

# View database statistics  
python team_bot.py --db-stats

# All databases created automatically on first run
python team_bot.py --login
```

For detailed database information, see [`DATABASE.md`](DATABASE.md).

## ⚙️ Configuration

### Creating Configuration File

Create a `config.json` file in the `_bot_post` directory:

```json
{
  "base_url": "https://social.legitreal.com/api",
  "timeout": 30,
  "retry_attempts": 3,
  "retry_delay": 1.0,
  "tokens_db": "./tokens.db",
  "personas_db": "./personas.db",
  "teams_db": "./teams.db",
  "bot_credentials": {
    "username": "your_team_bot",
    "password": "secure_bot_password",
    "email": "teambot@yourteam.com",
    "display_name": "Team Alpha Bot"
  },
  "team_invite_code": "your_team_invite_code_here",
  "competition_bot_key": "competition_bot_key_if_available",
  "team_name": "Team Alpha",
  "affiliation": "Your University",
  "member_name": "Team Lead Name",
  "member_email": "teamlead@yourteam.com"
}
```

### Configuration Options

#### Required Settings
- `base_url`: Twooter API endpoint
- `bot_credentials`: Bot authentication information
  - `username`: Unique bot username
  - `password`: Secure password for the bot
  - `email`: Bot email address
  - `display_name`: Public display name for the bot

#### Team Settings (at least one required)
- `team_invite_code`: Join existing team (recommended for most users)
- `competition_bot_key`: Official competition bot key
- Team creation info: `team_name`, `affiliation`, `member_name`, `member_email`

#### Optional Settings
- `timeout`: API request timeout (default: 30 seconds)
- `retry_attempts`: Number of retry attempts for failed requests
- Database paths for token and data storage

### Environment Variable Overrides

You can override configuration using environment variables:
```bash
export TWOOTER_USERNAME="your_bot"
export TWOOTER_PASSWORD="your_password"
export TWOOTER_EMAIL="bot@team.com"
export TWOOTER_DISPLAY_NAME="Team Bot"
export TWOOTER_TEAM_INVITE_CODE="invite_code"
export TWOOTER_COMPETITION_BOT_KEY="bot_key"
```

## 🎮 Usage

### Command Line Interface

#### Basic Operations
```bash
# Create template configuration file
python team_bot.py --create-config

# Check configuration status
python team_bot.py --config-status

# Test login
python team_bot.py --login

# Create a post
python team_bot.py --post "Hello from Team Alpha! 🚀"

# Reply to a post
python team_bot.py --reply 123 "Great point about that flag!"

# Like a post
python team_bot.py --like 456

# Repost content
python team_bot.py --repost 789

# Create a thread
python team_bot.py --thread "First post" "Second post" "Third post"
```

#### Interactive Mode
```bash
# Start interactive mode
python team_bot.py --interactive

# Interactive commands:
Bot> post Hello from our team!
Bot> reply 123 Nice work on that challenge
Bot> like 456
Bot> repost 789
Bot> status
Bot> help
Bot> quit
```

#### Auto-Engagement Mode
```bash
# Monitor for keywords and auto-engage
python team_bot.py --auto-engage "ctf,flag,solution,challenge"

# Custom settings
python team_bot.py --auto-engage "ctf,flag" --check-interval 30 --rate-limit 5
```

### Programmatic Usage

#### Basic Bot Operations
```python
from team_bot import TwooterTeamBot

# Initialize and start bot
bot = TwooterTeamBot("./config.json")
bot.start()

# Create posts
result = bot.post("Our team is ready for the CTF! 💪")
post_id = result["data"]["id"]

# Reply to discussions
bot.post("We found an interesting vulnerability in challenge 3", parent_id=123)

# Engage with community
bot.like_post(456)
bot.repost(789)

# Create announcement thread
announcements = [
    "🚨 Team Alpha CTF Update Thread 🚨",
    "We've solved challenges 1, 3, and 5 so far",
    "Currently working on the crypto challenge",
    "DM us if you want to collaborate! 🤝"
]
bot.create_thread(announcements)

# Cleanup
bot.stop()
```

#### Advanced Automation
```python
import time
from team_bot import TwooterTeamBot

bot = TwooterTeamBot()
bot.start()

# Automated competition participation
def ctf_automation():
    # Morning announcement
    bot.post("🌅 Good morning! Team Alpha is starting day 2 of the CTF")
    
    # Monitor for team mentions and respond
    keywords = ["team alpha", "collaboration", "hint"]
    bot.auto_engage(
        keywords=keywords,
        actions=['like', 'reply'],
        check_interval=30,
        max_actions_per_hour=15
    )

# Run automation
ctf_automation()
```

## 🔧 Bot Functions Explained

### AuthenticationManager (`auth_manager.py`)

**Purpose**: Handles all authentication operations with automatic fallback between different registration methods.

**Key Functions**:
- `login(username, password)`: Standard login with existing credentials
- `register_with_team_invite()`: Join existing team using invite code
- `register_with_bot_key()`: Register as official competition bot
- `register_new_team()`: Create new team and become admin
- `authenticate_with_fallback()`: Try all methods automatically
- `get_auth_headers()`: Get headers for authenticated requests
- `logout()`: Clean logout and token cleanup

**Authentication Flow**:
1. Try standard login first
2. If failed, try bot registration (if bot key available)
3. If failed, try team registration (if invite code available)
4. If failed, create new team (if team info available)
5. Store token in local SQLite database for reuse

### PostingManager (`posting_manager.py`)

**Purpose**: Manages all social interactions and content creation on the platform.

**Key Functions**:
- `create_post(content, parent_id, embed, media)`: Create posts with various content types
- `get_post(post_id)`: Retrieve post details
- `get_post_replies(post_id)`: Get all replies to a post
- `like_post(post_id)` / `unlike_post(post_id)`: Like/unlike posts
- `repost(post_id)` / `unrepost(post_id)`: Share/unshare content
- `create_thread(posts, delay)`: Create connected post threads
- `bulk_like_posts(post_ids)`: Like multiple posts efficiently
- `search_posts(query)`: Search for posts by keywords
- `get_user_posts(username)`: Get posts from specific users

**Error Handling**:
- Comprehensive error messages with HTTP status codes
- Conflict detection (already liked/reposted)
- Network error recovery with retry logic
- Rate limiting compliance

### ConfigurationManager (`config_manager.py`)

**Purpose**: Manages all configuration settings with validation and environment support.

**Key Functions**:
- `load_config()`: Load and validate configuration from JSON file
- `save_config()`: Save current configuration with backup
- `create_template_config()`: Generate template configuration file
- `validate_config()`: Validate all configuration sections
- `print_config_status()`: Display current configuration status
- `get_team_info_for_registration()`: Format team info for registration

**Configuration Sections**:
- **BotCredentials**: Username, password, email, display name
- **TeamSettings**: Invite codes, bot keys, team creation info
- **APISettings**: Base URL, timeout, retry settings
- **DatabaseSettings**: Database file paths

### TwooterTeamBot (`team_bot.py`)

**Purpose**: Main bot application that combines all components into a unified interface.

**Key Functions**:
- `start()`: Initialize and authenticate the bot
- `stop()`: Graceful shutdown with cleanup
- `post()`: Simplified posting interface
- `like_post()` / `repost()`: Social engagement shortcuts
- `create_thread()`: Thread creation helper
- `auto_engage()`: Automated engagement with keyword monitoring
- `run_interactive_mode()`: Command-line interactive interface

**Automation Features**:
- Keyword monitoring with configurable check intervals
- Rate limiting to prevent API abuse
- Multiple action types (like, repost, reply)
- Graceful error handling and recovery

## 🔒 Security Features

### Token Security
- Tokens stored in local SQLite database
- Database files created with restricted permissions
- Automatic token cleanup on logout
- Session-based and Bearer token support

### Rate Limiting
- Built-in rate limiting for auto-engagement
- Configurable actions per hour limits
- Delays between automated actions
- Respect for API rate limits

### Error Handling
- Comprehensive error logging
- Graceful degradation on failures
- Network error recovery
- Configuration validation

## 🏆 Competition Best Practices

### Team Coordination
1. **Use team invite codes** for official team participation
2. **Configure display names** to identify team affiliation
3. **Set up automation** for routine tasks
4. **Monitor keywords** related to your team or challenges

### Engagement Strategy
1. **Be helpful**: Share insights and collaborate with other teams
2. **Stay active**: Regular posting shows team engagement
3. **Use threads**: Organize complex discussions with threaded posts
4. **Respect limits**: Follow rate limiting to maintain good standing

### Competition Workflow
```python
# Example competition day workflow
bot = TwooterTeamBot()
bot.start()

# Morning check-in
bot.post("🌅 Team Alpha checking in for day 2! Let's solve some challenges 💪")

# Monitor for collaboration opportunities
keywords = ["collaboration", "team up", "hints", "crypto", "web", "pwn"]
bot.auto_engage(keywords, actions=['like', 'reply'], check_interval=60)

# Regular updates
bot.post("📊 Status update: 5/10 challenges solved, working on reversing challenge")

# Evening wrap-up
bot.post("🌙 Wrapping up day 2. Great progress today! See you tomorrow 🚀")
```

## 🐛 Troubleshooting

### Common Issues

#### Authentication Failures
```bash
# Check configuration
python team_bot.py --config-status

# Test login
python team_bot.py --login

# Verify credentials in config.json
```

#### Missing Dependencies
```bash
pip install requests
```

#### Configuration Errors
```bash
# Create new template
python team_bot.py --create-config

# Validate current config
python team_bot.py --config-status
```

#### API Connection Issues
- Verify `base_url` in configuration
- Check network connectivity
- Confirm API endpoint is accessible

### Debug Mode
```bash
# Enable verbose logging
python team_bot.py --verbose --post "Debug test"
```

### Log Analysis
- Check console output for error messages
- Verify HTTP status codes in error messages
- Check token database permissions

## 📚 API Reference

### Configuration File Schema
```json
{
  "base_url": "string (required)",
  "timeout": "integer (optional, default: 30)",
  "retry_attempts": "integer (optional, default: 3)",
  "retry_delay": "float (optional, default: 1.0)",
  "tokens_db": "string (optional, default: ./tokens.db)",
  "personas_db": "string (optional, default: ./personas.db)",
  "teams_db": "string (optional, default: ./teams.db)",
  "bot_credentials": {
    "username": "string (required)",
    "password": "string (required)",
    "email": "string (required)",
    "display_name": "string (required)"
  },
  "team_invite_code": "string (optional)",
  "competition_bot_key": "string (optional)",
  "team_name": "string (optional)",
  "affiliation": "string (optional)",
  "member_name": "string (optional)",
  "member_email": "string (optional)"
}
```

### Command Line Arguments
```
--config PATH              Path to configuration file
--config-status           Show configuration status
--create-config           Create template configuration
--login                   Test login and exit
--post TEXT               Create post with specified content
--reply ID TEXT           Reply to post with specified ID
--like ID                 Like post with specified ID
--repost ID               Repost post with specified ID
--thread TEXT [TEXT ...]  Create thread with multiple posts
--auto-engage KEYWORDS    Auto-engage with comma-separated keywords
--check-interval SECONDS  Seconds between checks in auto mode
--rate-limit NUMBER       Max actions per hour in auto mode
--interactive             Start interactive mode
--verbose                 Enable verbose logging
```

## 🤝 Contributing

This bot is designed to be modular and extensible. Key areas for enhancement:

1. **Additional Social Features**: Follow/unfollow, direct messages
2. **Advanced Automation**: ML-based content analysis, smart reply generation
3. **Team Coordination**: Team-specific channels, role management
4. **Competition Analytics**: Performance tracking, statistics

## 📄 License

This bot is part of the Twooter project and follows the same licensing terms as the main project.

## 🆘 Support

For issues specific to this bot:
1. Check the troubleshooting section above
2. Verify your configuration with `--config-status`
3. Test authentication with `--login`
4. Use `--verbose` mode for detailed error information

For Twooter platform issues, refer to the main project documentation.

## Run Commands

1. # Setup and configuration

```
python team_bot.py --create-config
python team_bot.py --config-status
python team_bot.py --login

```
2. # Basic operations
```
python team_bot.py --post "Team Alpha checking in! 🚀"
python team_bot.py --reply 123 "Great work on that challenge!"
python team_bot.py --like 456
python team_bot.py --repost 229320
```

3. # Interactive mode
```
python team_bot.py --interactive

```
4. # Automated engagement
```
python team_bot.py --auto-engage "ctf,flag,challenge"
```
5. Database
```
python team_bot.py --db-health    # Check database health
python team_bot.py --db-stats     # Show database statistics  
python team_bot.py --db-cleanup   # Clean up old entries
```

# Normal usage (will login each time)
python team_bot.py --post "Hello world!"

# Check what's in database  
python team_bot.py --db-stats

# Manually clear any stored tokens
python team_bot.py --logout

# Check database health
python team_bot.py --db-health