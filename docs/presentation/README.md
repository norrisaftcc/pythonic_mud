# Pythonic MUD Presentation

This folder contains an HTML presentation introducing the Pythonic MUD project. The presentation covers:

1. Introduction to MUDs and why they're valuable learning projects
2. Overview of the Evennia framework
3. Getting started with Evennia
4. Understanding Evennia's architecture
5. Game areas and player types
6. Essential commands
7. Next steps for development

## System Requirements

To work with Evennia, you'll need:
- **Python 3.10 or newer** (Python 3.11+ recommended)
- A virtual environment is strongly recommended for isolation

## Getting Started

To view the presentation:

1. Open `index.html` in a web browser
2. Use the navigation menu on the left to move between sections

To run the actual Evennia server:
1. Set up a Python 3.10+ virtual environment
2. Install Evennia (`pip install evennia`)
3. Follow the setup instructions in the presentation

## Standalone SVG Diagrams

This folder also includes several standalone SVG diagrams that can be viewed directly:

- `evennia_architecture.svg` - A detailed view of Evennia's framework structure
- `player_types.svg` - Relationship between Bartle player types and game areas
- `evennia_workflow.svg` - The development workflow for Evennia MUD projects

## Audience

This presentation is designed for college freshmen with basic programming knowledge who are interested in learning more about Python development through game creation.

## Project Directory Structure

The Pythonic MUD project follows Evennia's standard directory structure:

- `/mygame/typeclasses/` - Core game object definitions
- `/mygame/commands/` - Custom commands
- `/mygame/server/conf/` - Configuration settings
- `/mygame/web/` - Web client and website files
- `/mygame/world/` - Game-specific content

## Connection Information

When the Evennia server is running, you can connect via:
- Web client: http://localhost:4001
- Telnet client: localhost:4000
- Admin interface: http://localhost:4001/admin/