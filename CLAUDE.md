# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python MUD (Multi-User Dungeon) game built using the Evennia framework. Evennia is a modern Python framework specifically designed for text-based multiplayer games, providing a complete foundation for MUD development.

## System Requirements

- **Python**: 3.10 or newer (Python 3.11+ recommended)
- **Virtual Environment**: Recommended for isolation

## Core Commands

### Installation and Setup

```bash
# Set up a Python 3.10+ virtual environment
python3.11 -m venv evenv_new
source evenv_new/bin/activate

# Install Evennia (if needed)
pip install evennia

# Create a new game folder (if starting new)
evennia --init mygame
cd mygame

# Initialize the database
evennia migrate

# Create a superuser (or use the script provided)
evennia createsuperuser

# Start the server
evennia start
```

### Server Management

```bash
# Start the Evennia server
evennia start

# Stop the Evennia server
evennia stop

# Restart the Evennia server
evennia restart

# Check server status
evennia status
```

### Database Management

```bash
# Initialize/update the database
evennia migrate

# Reset the database (USE WITH CAUTION - destroys all data)
evennia reset
```

### Development Commands

```bash
# Create a new superuser
evennia createsuperuser

# Run a specific script
evennia run <scriptname>

# Shell access to the game's Python environment
evennia shell

# Get help with Evennia commands
evennia -h
```

## Project Architecture

Evennia uses a modular architecture based on Django and Twisted:

1. **Typeclasses**: Python classes that extend database models, allowing custom game objects
   - Located in `/mygame/typeclasses/`
   - Key files: `characters.py`, `objects.py`, `rooms.py`, `exits.py`
   - Typeclasses connect Python classes with database models
   - Used to create rooms, characters, items, and other game objects

2. **Commands**: Functions that process player input and execute game actions
   - Located in `/mygame/commands/`
   - Command sets defined in `default_cmdsets.py`
   - Each command is a Python class with a `func` method that executes the command logic

3. **Server Configuration**: Django settings and server configuration
   - Located in `/mygame/server/conf/`
   - Main settings file: `settings.py`
   - Connection screens in `connection_screens.py`

4. **Web Interface**: Browser-based client and website
   - Located in `/mygame/web/`
   - Static files in `static/` (formerly static_overrides)
   - Templates in `templates/` (formerly template_overrides)
   - Built on Django's web framework

5. **World Content**: Game-specific content definitions
   - Located in `/mygame/world/`
   - Object prototypes in `prototypes.py`
   - Batch scripts in `batch_cmds.ev`

6. **Scripts**: Persistent processes for timed events and background tasks
   - Located in `/mygame/typeclasses/scripts.py`
   - Used for timed events, AI, and other background processes

## Game Concepts

The game is structured around four main areas aligned with Bartle player types:

1. **CREATE (The Forge)**
   - Appeals to Achievers and Explorers
   - Crafting systems, creating items, and seeing tangible results
   - Similar to Minecraft crafting and RPG gear progression

2. **EXPLAIN (The Lore Halls)**
   - Appeals to Socializers and Explorers
   - NPC interactions, dialogue systems, and uncovering lore
   - Similar to visual novels and dialogue-rich RPGs

3. **CODE (The Arcane Matrix)**
   - Appeals to Achievers and Explorers
   - Mastering logical systems and discovering how things work
   - Programming puzzles, logic games, and optimization challenges

4. **EXPLORE (The Neon Wilderness)**
   - Appeals to Explorers, Killers, and Achievers
   - Mapping territories, tactical combat, and finding rewards
   - Similar to dungeon crawlers and roguelike games

## Development Workflow

1. Modify typeclasses to create custom game objects
2. Create commands to enable new player actions
3. Design rooms and areas with appropriate descriptions
4. Use attributes (db fields) to store data on any object
5. Create scripts for timed events and ongoing processes
6. Test changes by connecting to the game via the web client or telnet
7. Restart the server to apply significant changes

## In-Game Building Commands

These commands can be used when connected as a superuser:

```
# Create a new room
@create <room_name>:<typeclass>
@desc <room_name> = <description>

# Create an exit between rooms
@dig <exit_name> = <destination>

# Create an object
@create <object_name>:<typeclass>
@desc <object_name> = <description>

# Teleport to a room
@tel <room_name>

# Set attributes on objects
@set <object>/attribute = <value>
```

## Connection Information

- **Web client**: http://localhost:4001
- **Telnet client**: localhost:4000
- **Admin interface**: http://localhost:4001/admin/

## Project-Specific Utilities

### Superuser Creation Script

If you encounter issues creating a superuser in non-interactive environments, use the provided script:

```bash
# Run the script to create a superuser programmatically
python create_superuser.py
```

The script creates an admin user with the following credentials:
- Username: admin
- Password: sudosudo

## Deployment Considerations

For deployment, a VPS (Virtual Private Server) is recommended due to the websocket requirements:
- DigitalOcean ($5/month basic droplet)
- Linode ($5/month entry-level plan)
- AWS Lightsail (starting at $3.50/month)

Basic deployment process:
1. Set up a VPS with Python 3.10+
2. Clone the repository
3. Install requirements
4. Configure the server for production use
5. Run as a service using systemd

## Documentation Resources

- [Evennia Documentation](https://www.evennia.com/docs/latest/)
- [Evennia Tutorial](https://www.evennia.com/docs/latest/Tutorials/Tutorial-Learning-Evennia-Step-by-Step)
- [Evennia GitHub Repository](https://github.com/evennia/evennia)
- [Evennia Community Forum](https://github.com/evennia/evennia/discussions)
- [MUD Dev Wiki](http://mud.wikia.com/wiki/Main_Page) - General MUD design concepts
- [Django Documentation](https://docs.djangoproject.com/) - For understanding the web framework Evennia uses