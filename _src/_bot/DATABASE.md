# Database Management Guide

## 🗄️ Database Overview

The Twooter Team Bot uses **SQLite databases** for local data storage. SQLite is built into Python, so **no additional database software installation is required**.

## 📂 Database Files

The bot creates and manages three SQLite database files:

### 1. `tokens.db` - Authentication Storage
**Purpose**: Stores authentication tokens and session data
**Auto-created**: ✅ Yes, when first needed
**Location**: Same directory as your config.json

**Schema**:
```sql
CREATE TABLE tokens (
    username TEXT PRIMARY KEY,
    token TEXT NOT NULL,
    token_type TEXT DEFAULT 'bearer',
    created_at TEXT NOT NULL,
    expires_at TEXT,
    last_used TEXT
);
```

**What it stores**:
- Your bot's authentication tokens
- Token expiration times
- Session information

### 2. `personas.db` - User Profile Storage  
**Purpose**: Stores user credentials and profile information
**Auto-created**: ✅ Yes, when first needed
**Location**: Same directory as your config.json

**Schema**:
```sql
CREATE TABLE users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    display_name TEXT,
    team_invite_code TEXT,
    member_email TEXT,
    created_at TEXT NOT NULL,
    last_login TEXT
);
```

**What it stores**:
- Bot user profiles
- Credential information
- Team association data

### 3. `teams.db` - Team Information Storage
**Purpose**: Stores team configurations and membership data
**Auto-created**: ✅ Yes, when first needed  
**Location**: Same directory as your config.json

**Schema**:
```sql
CREATE TABLE teams (
    team_id INTEGER PRIMARY KEY AUTOINCREMENT,
    team_name TEXT NOT NULL,
    invite_code TEXT UNIQUE,
    affiliation TEXT,
    created_at TEXT NOT NULL,
    members TEXT
);
```

**What it stores**:
- Team information
- Invite codes
- Member lists (as JSON)

## 🔧 How Database Creation Works

### Automatic Initialization
When you run the bot for the first time:

1. **Check for existing databases** in your config directory
2. **Create missing databases** automatically with proper schema
3. **Set appropriate file permissions** for security
4. **Log database creation** for transparency

### Code Example
```python
# This happens automatically when you start the bot
from auth_manager import AuthenticationManager

# The AuthenticationManager creates databases automatically
auth_manager = AuthenticationManager(
    base_url="https://social.legitreal.com/api",
    tokens_db_path="./tokens.db"  # Created if doesn't exist
)
```

## 🚀 What You Need to Do: **NOTHING!**

### Zero Setup Required ✅
- **No database software to install**
- **No schema creation scripts to run**  
- **No database configuration needed**
- **No database user accounts to create**

### First Time Running the Bot:
```bash
# Just run the bot - databases created automatically
python team_bot.py --config-status

# You'll see output like:
# ✅ Tokens database initialized: ./tokens.db
# ✅ Personas database initialized: ./personas.db  
# ✅ Teams database initialized: ./teams.db
```

## 📊 Database Management Features

### Built-in Database Operations
The bot includes several database management features:

#### Health Checks
```bash
python team_bot.py --db-health
```
Checks if all databases are accessible and properly structured.

#### Database Statistics  
```bash
python team_bot.py --db-stats
```
Shows record counts and database status.

#### Token Cleanup
```python
# Automatic cleanup of expired tokens
auth_manager.cleanup_expired_tokens()
```

#### Backup Creation
```python
# Create backups of all databases
db_manager.backup_databases("./backups/")
```

## 🔍 Verifying Database Creation

After running the bot for the first time, you should see these files:

```
your_bot_directory/
├── config.json          # Your configuration
├── team_bot.py         # Main bot file
├── tokens.db           # ✅ Auto-created
├── personas.db         # ✅ Auto-created  
├── teams.db           # ✅ Auto-created
└── ...
```

### Check Database Contents
You can inspect the databases using any SQLite viewer, or with Python:

```python
import sqlite3

# Check tokens database
conn = sqlite3.connect('tokens.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables in tokens.db:", tables)
conn.close()
```

## 🔒 Security Considerations

### File Permissions
- Database files are created with restricted permissions
- Only the user running the bot can read/write the files
- Tokens are stored securely in the local database

### Data Privacy
- All data stored locally on your machine
- No data sent to external databases
- Tokens automatically cleaned up on logout

### Backup Recommendations
```bash
# Create periodic backups (optional)
cp tokens.db tokens_backup_$(date +%Y%m%d).db
cp personas.db personas_backup_$(date +%Y%m%d).db
cp teams.db teams_backup_$(date +%Y%m%d).db
```

## 🐛 Troubleshooting Database Issues

### Permission Errors
```bash
# Fix file permissions if needed (Linux/Mac)
chmod 600 *.db

# Windows - check folder permissions in Properties
```

### Corrupted Database
```bash
# Remove and recreate (will require re-authentication)
rm tokens.db personas.db teams.db
python team_bot.py --login
```

### Database Locked Errors
```bash
# Stop any running bot instances
# Restart the bot - SQLite handles most lock issues automatically
```

## 📝 Summary

### What the Code Handles Automatically:
✅ Database file creation  
✅ Schema creation and validation  
✅ Data insertion and retrieval  
✅ Token storage and management  
✅ Error handling and recovery  
✅ File permission setup  
✅ Automatic cleanup of expired data  

### What You Need to Do:
❌ Nothing! Just run the bot and everything is handled automatically.

### Requirements:
✅ Python 3.7+ (includes SQLite)  
✅ File system write permissions in bot directory  

The databases are designed to be maintenance-free and work seamlessly with your bot operations. Just focus on configuring your team settings and let the bot handle all the database operations!