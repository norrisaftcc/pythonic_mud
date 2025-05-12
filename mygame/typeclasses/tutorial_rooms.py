"""
Tutorial Rooms

This module contains custom room typeclasses for the tutorial area
of the Pythonic MUD, designed to teach new players the basic game mechanics.

"""
from typeclasses.rooms import Room
from evennia import CmdSet
from evennia.commands.command import Command


class TutorialCommand(Command):
    """
    A command that's only available in the tutorial area.
    """
    key = "tutorial"
    aliases = ["tut", "help"]
    lock = "cmd:all()"
    help_category = "Tutorial"
    
    def func(self):
        """Execute the tutorial command"""
        if not self.args:
            # No arguments, show tutorial overview
            self.caller.msg(self.obj.db.tutorial_help)
        elif self.args.strip().lower() == "next":
            # Show next step
            if hasattr(self.obj.db, "tutorial_next") and self.obj.db.tutorial_next:
                self.caller.msg(self.obj.db.tutorial_next)
            else:
                self.caller.msg("There are no further specific instructions for this area.")
        else:
            # Try to match a specific topic
            topic = self.args.strip().lower()
            if hasattr(self.obj.db, "tutorial_topics") and topic in self.obj.db.tutorial_topics:
                self.caller.msg(self.obj.db.tutorial_topics[topic])
            else:
                self.caller.msg(f"No tutorial help available for '{topic}'. Try 'tutorial' without arguments for general help.")


class TutorialCmdSet(CmdSet):
    """
    Command set for tutorial commands.
    """
    key = "tutorial_cmdset"
    
    def at_cmdset_creation(self):
        """
        Add tutorial commands to the command set
        """
        self.add(TutorialCommand())


class TutorialRoom(Room):
    """
    Base class for all tutorial rooms.
    
    These rooms provide guidance and help for new players
    learning the game mechanics.
    """
    
    def at_object_creation(self):
        """Set up tutorial room attributes and commands."""
        super().at_object_creation()
        
        # Tutorial messages
        self.db.tutorial_help = "Welcome to the tutorial! Type 'tutorial next' for step-by-step guidance, or 'tutorial <topic>' for help on a specific topic."
        self.db.tutorial_next = "Try exploring this room with 'look' command. When you're ready to move on, look for an exit."
        self.db.tutorial_topics = {
            "movement": "You can move between rooms using the cardinal directions: north, south, east, west, up, down. Type the direction or its first letter (e.g. 'n' for north).",
            "look": "The 'look' command lets you examine your surroundings. Use 'look <object>' to examine specific things.",
            "commands": "Type 'help' to see all available commands. Different areas of the game have specialized commands for crafting, coding, dialogue, and exploration."
        }
        
        # Add the tutorial command set
        cmdset = TutorialCmdSet()
        cmdset.key = "tutorial_cmdset"
        self.cmdset.add(cmdset, permanent=True)
        
        # Track players who have visited this tutorial room
        self.db.visitors = set()
    
    def at_object_receive(self, moved_obj, source_location):
        """Called when an object enters the room."""
        super().at_object_receive(moved_obj, source_location)
        
        # Only process for player characters
        if not hasattr(moved_obj, 'is_superuser'):
            return
            
        # Add to visitors
        self.db.visitors.add(moved_obj)
        
        # If this is the first time the player is here, show the welcome message
        if hasattr(moved_obj.db, "visited_tutorials") and self.id not in moved_obj.db.visited_tutorials:
            if not hasattr(moved_obj.db, "visited_tutorials"):
                moved_obj.db.visited_tutorials = set()
                
            # Show the welcome message after a short delay
            from evennia.utils import delay
            delay(1, self._show_welcome, moved_obj)
            
            # Mark as visited
            moved_obj.db.visited_tutorials.add(self.id)
    
    def _show_welcome(self, character):
        """Show the welcome message to a character."""
        # Check that character is still here
        if character.location != self:
            return
            
        # Send the tutorial welcome message
        if hasattr(self.db, "tutorial_welcome") and self.db.tutorial_welcome:
            character.msg(self.db.tutorial_welcome)
        else:
            character.msg("Welcome to the tutorial area! Type 'tutorial' for help.")


class CreateTutorialRoom(TutorialRoom):
    """
    Tutorial room for teaching the crafting system (CREATE area).
    """
    
    def at_object_creation(self):
        """Set up CREATE tutorial specifics."""
        super().at_object_creation()
        
        # Override basic tutorial texts
        self.db.tutorial_welcome = "|gWelcome to the Crafting Tutorial!|n\nHere you'll learn how to gather materials and craft items. Type 'tutorial' for an overview or 'tutorial next' for step-by-step guidance."
        self.db.tutorial_help = "The CREATE area focuses on crafting and building. You can gather materials with the 'gather' command and craft items at workbenches with the 'craft' command."
        self.db.tutorial_next = "Try using 'gather' to collect some materials, then use 'craft' at the workbench to make something."
        
        # Add specific tutorial topics
        self.db.tutorial_topics.update({
            "gather": "The 'gather' command lets you collect crafting materials. Just type 'gather' to see what's available, or 'gather <material>' to collect a specific material.",
            "craft": "The 'craft' command is used at workbenches to create items. Use 'craft/list' to see what you can make with your current materials, 'craft/recipes' to see all recipes, and 'craft <item>' to create something.",
            "inspect": "Use 'inspect <object>' to examine crafting materials, workbenches, and crafted items in detail."
        })
        
        # Crafting materials available in this room
        self.db.available_resources = {
            "training metal": {
                "quantity": 10,
                "respawn_time": 60,  # 1 minute
                "last_respawn": None
            },
            "practice wood": {
                "quantity": 10,
                "respawn_time": 60,
                "last_respawn": None
            }
        }


class CodeTutorialRoom(TutorialRoom):
    """
    Tutorial room for teaching the programming system (CODE area).
    """
    
    def at_object_creation(self):
        """Set up CODE tutorial specifics."""
        super().at_object_creation()
        
        # Override basic tutorial texts
        self.db.tutorial_welcome = "|gWelcome to the Coding Tutorial!|n\nHere you'll learn how to solve programming puzzles. Type 'tutorial' for an overview or 'tutorial next' for step-by-step guidance."
        self.db.tutorial_help = "The CODE area focuses on programming puzzles and logic challenges. You can write and execute Python code at terminals with the 'code' command."
        self.db.tutorial_next = "Try using the 'terminals' command to see available puzzle terminals, then use 'puzzle <terminal>' to examine a terminal and 'code' to write and execute code."
        
        # Add specific tutorial topics
        self.db.tutorial_topics.update({
            "code": "The 'code' command lets you write and execute Python code. Use 'code <python code>' to add code to a terminal, 'code/run' to execute it, and 'code/hint' for hints.",
            "puzzle": "The 'puzzle <terminal>' command provides information about a coding puzzle terminal, including its description, difficulty, and any hints.",
            "terminals": "The 'terminals' command shows all available coding terminals in the current room."
        })
        
        # Pre-defined puzzles for this tutorial room
        self.db.puzzles = {
            "tutorial": {
                "description": "A simple introduction to Python coding puzzles.",
                "difficulty": 1,
                "current_code": "# Print the message 'Hello, Python!'",
                "expected_output": "Hello, Python!",
                "hints": [
                    "Use the print() function to display text",
                    "Make sure to use quotes around the text string",
                    "Try writing: print('Hello, Python!')"
                ]
            }
        }


class LoreTutorialRoom(TutorialRoom):
    """
    Tutorial room for teaching the dialogue system (EXPLAIN area).
    """
    
    def at_object_creation(self):
        """Set up EXPLAIN tutorial specifics."""
        super().at_object_creation()
        
        # Override basic tutorial texts
        self.db.tutorial_welcome = "|gWelcome to the Dialogue Tutorial!|n\nHere you'll learn how to interact with NPCs and acquire knowledge. Type 'tutorial' for an overview or 'tutorial next' for step-by-step guidance."
        self.db.tutorial_help = "The EXPLAIN area focuses on dialogue, lore, and knowledge acquisition. You can talk to NPCs with the 'talk' command and learn from them with the 'learn' command."
        self.db.tutorial_next = "Try using the 'npcs' command to see who's available to talk to, then use 'talk <npc>' to start a conversation."
        
        # Add specific tutorial topics
        self.db.tutorial_topics.update({
            "talk": "The 'talk <npc>' command starts a conversation with an NPC. You can also use 'talk <npc> about <topic>' to discuss specific subjects.",
            "learn": "The 'learn <topic> from <npc/object>' command allows you to acquire knowledge on specific topics. Use 'learn from <npc/object>' to see available topics.",
            "quest": "The 'quest <npc>' command lets you get quests from NPCs. Use 'quest/list' to see your active quests and 'quest/complete <quest> with <npc>' to complete them.",
            "npcs": "The 'npcs' command shows all available NPCs in the current room, along with their mood and services."
        })
        
        # Knowledge topics available in this room
        self.db.knowledge_topics = [
            "python basics", "game commands", "tutorial"
        ]


class ExploreTutorialRoom(TutorialRoom):
    """
    Tutorial room for teaching the exploration system (EXPLORE area).
    """
    
    def at_object_creation(self):
        """Set up EXPLORE tutorial specifics."""
        super().at_object_creation()
        
        # Override basic tutorial texts
        self.db.tutorial_welcome = "|gWelcome to the Exploration Tutorial!|n\nHere you'll learn how to explore the wilderness, find hidden features, and engage in combat. Type 'tutorial' for an overview or 'tutorial next' for step-by-step guidance."
        self.db.tutorial_help = "The EXPLORE area focuses on exploration, discovery, and combat. You can search areas with the 'explore' command, check your status with 'status', and engage in combat with 'attack'."
        self.db.tutorial_next = "Try using the 'explore' command to search this area for hidden features, then check your health and combat status with 'status'."
        
        # Add specific tutorial topics
        self.db.tutorial_topics.update({
            "explore": "The 'explore' command lets you search the area for hidden features like exits, objects, and resources. You can also use 'explore <direction>' to focus on a specific area.",
            "attack": "The 'attack <target>' command initiates combat with an opponent. You can also use 'attack <target> with <weapon>' to use a specific weapon.",
            "status": "The 'status' command shows your current health, equipped items, and other combat information.",
            "map": "The 'map' command displays a simple map of explored areas, helping you track your exploration progress."
        })
        
        # Exploration features for this room
        self.db.danger_level = 1
        self.db.hidden_exits = {
            "secret": {
                "destination": "Tutorial Hub",
                "difficulty": 2,
                "desc": "A hidden exit back to the Tutorial Hub, easily found by beginners."
            }
        }
        self.db.treasures = {
            "practice treasure": {
                "difficulty": 2,
                "desc": "A simple treasure to practice discovery mechanics."
            }
        }
        self.db.encounter_chance = 0.0  # No random encounters in tutorial