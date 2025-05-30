# Evennia Commands Reference

## Installation and Setup

```bash
# Set up Python 3.10+ virtual environment
python3.11 -m venv evenv_new
source evenv_new/bin/activate

# Install Evennia
pip install evennia

# Create new game folder (if starting new)
evennia --init mygame
cd mygame

# Initialize database
evennia migrate

# Create superuser (or use the script)
evennia createsuperuser

# Start server
evennia start
```

## Server Management

```bash
evennia start      # Start the Evennia server
evennia stop       # Stop the Evennia server
evennia restart    # Restart the Evennia server
evennia status     # Check server status
```

## Database Management

```bash
evennia migrate    # Initialize/update the database
evennia reset      # Reset database (CAUTION - destroys all data)
```

## Development Commands

```bash
evennia createsuperuser    # Create a new superuser
evennia run <scriptname>   # Run a specific script
evennia shell              # Shell access to game's Python environment
evennia -h                 # Get help with Evennia commands
```

## In-Game Building Commands

Use these when connected as a superuser:

```
# Room creation
@create <room_name>:<typeclass>
@desc <room_name> = <description>

# Exit creation
@dig <exit_name> = <destination>

# Object creation
@create <object_name>:<typeclass>
@desc <object_name> = <description>

# Navigation
@tel <room_name>

# Attributes
@set <object>/attribute = <value>
```

## Superuser Creation Script

For non-interactive environments:

```bash
python create_superuser.py
```

Creates admin user with:
- Username: admin
- Password: sudosudo