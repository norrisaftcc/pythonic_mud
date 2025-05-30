# CLAUDE.md

Python MUD game using Evennia framework. Python 3.10+ required.

## Quick Start
```bash
python3.11 -m venv evenv_new
source evenv_new/bin/activate
pip install evennia
cd mygame
evennia migrate
evennia start
```

## Key Directories
- `/mygame/typeclasses/` - Game objects (characters, rooms, objects)
- `/mygame/commands/` - Player commands
- `/mygame/server/conf/` - Server configuration
- `/mygame/world/` - Game content (prototypes.py)

## Essential Commands
- `evennia start/stop/restart` - Server control
- `evennia migrate` - Update database
- `python create_superuser.py` - Create admin (username: admin, password: sudosudo)

## Access Points
- Web: http://localhost:4001
- Telnet: localhost:4000
- Admin: http://localhost:4001/admin/

## Development Workflow
1. Edit typeclasses for game objects
2. Add commands in commands/
3. Test via web client
4. Restart server for major changes

## Documentation
- Full commands: `docs/evennia/commands.md`
- Architecture: `docs/evennia/architecture.md`
- Game design: `docs/isekai/game_design.md`
- Deployment: `docs/evennia/deployment.md`
- [Evennia Docs](https://www.evennia.com/docs/latest/)