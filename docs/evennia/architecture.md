# Evennia Architecture

Evennia uses a modular architecture based on Django and Twisted.

## Core Components

### 1. Typeclasses
Python classes that extend database models for custom game objects.
- **Location**: `/mygame/typeclasses/`
- **Key files**: `characters.py`, `objects.py`, `rooms.py`, `exits.py`
- **Purpose**: Connect Python classes with database models
- **Usage**: Create rooms, characters, items, and other game objects

### 2. Commands
Functions that process player input and execute game actions.
- **Location**: `/mygame/commands/`
- **Command sets**: Defined in `default_cmdsets.py`
- **Structure**: Each command is a Python class with a `func` method

### 3. Server Configuration
Django settings and server configuration.
- **Location**: `/mygame/server/conf/`
- **Main settings**: `settings.py`
- **Connection screens**: `connection_screens.py`

### 4. Web Interface
Browser-based client and website built on Django.
- **Location**: `/mygame/web/`
- **Static files**: `static/`
- **Templates**: `templates/`

### 5. World Content
Game-specific content definitions.
- **Location**: `/mygame/world/`
- **Prototypes**: `prototypes.py`
- **Batch scripts**: `batch_cmds.ev`

### 6. Scripts
Persistent processes for timed events and background tasks.
- **Location**: `/mygame/typeclasses/scripts.py`
- **Usage**: Timed events, AI, background processes

## Development Workflow

1. Modify typeclasses to create custom game objects
2. Create commands to enable new player actions
3. Design rooms and areas with appropriate descriptions
4. Use attributes (db fields) to store data on any object
5. Create scripts for timed events and ongoing processes
6. Test changes by connecting to the game via web client or telnet
7. Restart the server to apply significant changes

## Documentation Resources

- [Evennia Documentation](https://www.evennia.com/docs/latest/)
- [Evennia Tutorial](https://www.evennia.com/docs/latest/Tutorials/Tutorial-Learning-Evennia-Step-by-Step)
- [Evennia GitHub](https://github.com/evennia/evennia)
- [Evennia Forum](https://github.com/evennia/evennia/discussions)
- [MUD Dev Wiki](http://mud.wikia.com/wiki/Main_Page)
- [Django Documentation](https://docs.djangoproject.com/)