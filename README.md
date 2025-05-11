# Pythonic MUD

A Python-based Multi-User Dungeon (MUD) game built with the Evennia framework. This project serves as both a playable game and an educational resource for learning Python through game development.

## System Requirements

- **Python 3.10 or newer** (Python 3.11+ recommended)
- A virtual environment is strongly recommended

## Quick Start

Use the included convenience script to set up and run Evennia:

```bash
# Make script executable if needed
chmod +x evennia.sh

# Start the server
./evennia.sh start

# Check server status
./evennia.sh status

# Stop the server
./evennia.sh stop
```

The script will automatically activate the virtual environment and handle all the necessary setup.

## Connection Information

Once the server is running, you can connect via:
- **Web client**: http://localhost:4001
- **Telnet client**: localhost:4000
- **Admin interface**: http://localhost:4001/admin/

Default admin credentials:
- Username: admin
- Password: sudosudo

## Documentation

For more detailed information about this project:

- **[CLAUDE.md](CLAUDE.md)** - Comprehensive guide to working with this codebase
- **[TODO.md](TODO.md)** - Current project status and future plans
- **[docs/presentation](docs/presentation/index.html)** - Educational presentation about MUD development

## Game Concept

The game is structured around four main areas aligned with Bartle player types:

1. **CREATE (The Forge)** - Crafting systems and item creation
2. **EXPLAIN (The Lore Halls)** - NPC interactions and story elements
3. **CODE (The Arcane Matrix)** - Programming puzzles and logic challenges
4. **EXPLORE (The Neon Wilderness)** - World exploration and combat

## Credits

Built with [Evennia](https://www.evennia.com/), a Python MUD/MUSH/MUX development system.