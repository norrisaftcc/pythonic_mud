"""
Themed Rooms

This module contains custom room typeclasses for the four themed areas
of the Pythonic MUD, each designed to support specific gameplay mechanics.

"""
from evennia import DefaultObject
from typeclasses.rooms import Room


class ThemedRoom(Room):
    """
    Base class for all themed rooms with common functionality.
    
    Attributes:
        area_type (str): One of "forge", "lore", "matrix", "wilderness"
        difficulty (int): A value from 1-10 indicating challenge level
    """
    
    def at_object_creation(self):
        """Set up basic attributes for all themed rooms."""
        super().at_object_creation()
        self.db.area_type = "base"
        self.db.difficulty = 1
        self.db.visited_by = set()  # track players who've visited
    
    def at_object_receive(self, obj, source_location):
        """Called when a character enters the room."""
        super().at_object_receive(obj, source_location)
        
        # Only track character arrivals
        if hasattr(obj, 'is_superuser'):
            # Add character to the visited_by list if not there already
            if obj not in self.db.visited_by:
                self.db.visited_by.add(obj)
    

class ForgeRoom(ThemedRoom):
    """
    Rooms in the CREATE/Forge area focus on crafting and building.

    These rooms support the crafting system, resource gathering, and
    storage of crafting materials. They contain workbenches and other
    facilities for item creation.
    """

    def at_object_creation(self):
        """Set up forge-specific attributes."""
        super().at_object_creation()
        self.db.area_type = "forge"

        # Crafting-related attributes
        self.db.available_resources = {
            "metal ore": {
                "quantity": 5,
                "respawn_time": 600,  # in seconds (10 minutes)
                "last_respawn": None
            },
            "wood": {
                "quantity": 8,
                "respawn_time": 300,  # in seconds (5 minutes)
                "last_respawn": None
            },
            "crystal shard": {
                "quantity": 3,
                "respawn_time": 1200,  # in seconds (20 minutes)
                "last_respawn": None
            }
        }
        self.db.workbenches = {}  # Dict of workbench types available in this room

    def return_appearance(self, looker):
        """
        Customize appearance to show available resources.
        """
        appearance = super().return_appearance(looker)

        # Add info about available resources
        if self.db.available_resources:
            resource_list = []
            for resource, data in self.db.available_resources.items():
                if data.get("quantity", 0) > 0:
                    resource_list.append(resource)

            if resource_list:
                resources_text = "\n\nAvailable resources: " + ", ".join(resource_list)
                appearance += resources_text

        return appearance


class LoreRoom(ThemedRoom):
    """
    Rooms in the EXPLAIN/Lore Halls area focus on storytelling and dialogue.

    These rooms support NPC interactions, knowledge acquisition, and
    quest management. They are designed for social gameplay and lore discovery.
    """

    def at_object_creation(self):
        """Set up lore-specific attributes."""
        super().at_object_creation()
        self.db.area_type = "lore"

        # NPC and knowledge-related attributes
        self.db.knowledge_topics = [
            "python", "programming", "history", "algorithms"
        ]  # Topics that can be learned here
        self.db.npc_keys = []  # Keys of NPCs associated with this room
        self.db.visitors_learned = set()  # Track characters who have gained knowledge here

    def return_appearance(self, looker):
        """
        Customize appearance to show available NPCs and knowledge sources.
        """
        appearance = super().return_appearance(looker)

        # Find NPCs in the room
        npcs = []
        knowledge_items = []

        for obj in self.contents:
            if hasattr(obj, 'db'):
                if obj.db.dialogue_tree:
                    npcs.append(obj.key)
                elif obj.db.knowledge_topics:
                    knowledge_items.append(obj.key)

        # Add NPCs to room description
        if npcs:
            npcs_text = "\n\nPresent characters: " + ", ".join(npcs)
            appearance += npcs_text

        # Add knowledge items to room description
        if knowledge_items:
            items_text = "\n\nKnowledge sources: " + ", ".join(knowledge_items)
            appearance += items_text

        return appearance


class MatrixRoom(ThemedRoom):
    """
    Rooms in the CODE/Arcane Matrix area focus on programming puzzles and logic.

    These rooms contain coding challenges, logical puzzles, and hackable objects.
    They support the programming gameplay mechanics.
    """

    def at_object_creation(self):
        """Set up matrix-specific attributes."""
        super().at_object_creation()
        self.db.area_type = "matrix"

        # Programming puzzle related attributes
        self.db.puzzles = {
            "beginner": {
                "description": "A simple challenge to test basic Python skills.",
                "difficulty": 1,
                "current_code": "# Write a function that prints 'Hello, World!'",
                "expected_output": "Hello, World!",
                "hints": [
                    "Use the print() function",
                    "The message should be exactly 'Hello, World!' including the comma and exclamation mark",
                    "Try this: print('Hello, World!')"
                ]
            },
            "loop": {
                "description": "A challenge about using loops in Python.",
                "difficulty": 2,
                "current_code": "# Write a loop that prints the numbers 1 to 5, each on a new line",
                "expected_output": "1\n2\n3\n4\n5",
                "hints": [
                    "Use a for loop with the range() function",
                    "Remember that range(1, 6) gives numbers from 1 to 5",
                    "Try this: for i in range(1, 6):\n    print(i)"
                ]
            },
            "function": {
                "description": "A challenge about creating functions.",
                "difficulty": 3,
                "current_code": "# Write a function that returns the sum of two numbers",
                "expected_output": "3",
                "hints": [
                    "Define a function that takes two parameters",
                    "Use the + operator to add them together",
                    "Don't forget to call your function, like: print(add(1, 2))"
                ]
            }
        }
        self.db.completed_by = set()  # Characters who solved this room's challenges

    def return_appearance(self, looker):
        """
        Customize appearance to show available terminals.
        """
        appearance = super().return_appearance(looker)

        # Find terminals in the room
        terminals = []
        for obj in self.contents:
            if hasattr(obj, 'db') and obj.db.puzzle_type and "code" in obj.db.puzzle_type:
                terminals.append(obj.key)

        if terminals:
            terminals_text = "\n\nAvailable terminals: " + ", ".join(terminals)
            appearance += terminals_text

        return appearance


class WildernessRoom(ThemedRoom):
    """
    Rooms in the EXPLORE/Neon Wilderness area focus on exploration and combat.

    These rooms support navigation challenges, combat encounters, and
    resource discovery. They have dynamic encounters and environmental hazards.
    """

    def at_object_creation(self):
        """Set up wilderness-specific attributes."""
        super().at_object_creation()
        self.db.area_type = "wilderness"

        # Exploration and combat related attributes
        self.db.danger_level = 1  # Combat difficulty (1-10)
        self.db.hidden_exits = {
            "north": {
                "destination": "The Neon Wilderness Entrance",  # Default to starting point
                "difficulty": 5,  # 1-10, higher is harder to find
                "desc": "A partially obscured path leading deeper into the wilderness."
            }
        }
        self.db.encounter_chance = 0.2  # Probability of random encounter (0-1)
        self.db.treasures = {
            "data crystal": {
                "prototype": "DATA_CRYSTAL",
                "difficulty": 5,
                "desc": "A perfectly formed crystal containing compressed data and algorithms."
            },
            "ancient artifact": {
                "prototype": "ANCIENT_ARTIFACT",
                "difficulty": 7,
                "desc": "A mysterious device from a forgotten digital civilization."
            }
        }
        self.db.last_encounter_check = None  # When we last checked for random encounters
        self.db.explorers = set()  # Track who has explored this room

    def at_object_receive(self, obj, source_location):
        """Called when an object enters the room."""
        super().at_object_receive(obj, source_location)

        # Only process for characters
        if not hasattr(obj, 'is_superuser'):
            return

        # Add to explorers set
        self.db.explorers.add(obj)

        # Check for random encounters
        # Import time for encounter timing
        import time
        current_time = time.time()

        # Only check once every 5 minutes
        if (self.db.last_encounter_check is None or
                current_time - self.db.last_encounter_check > 300):

            self.db.last_encounter_check = current_time

            # Roll for encounter
            import random
            if random.random() < self.db.encounter_chance:
                # Spawn an encounter after a short delay
                from evennia.utils import delay
                delay(2, self._spawn_encounter, obj)

    def return_appearance(self, looker):
        """
        Customize appearance for wilderness rooms.
        """
        appearance = super().return_appearance(looker)

        # Show any active opponents
        opponents = []
        for obj in self.contents:
            if hasattr(obj, 'db') and hasattr(obj.db, "health") and "opponent" in str(obj.typeclass):
                opponents.append(obj.key)

        if opponents:
            appearance += "\n\n|rActive threats:|n " + ", ".join(opponents)

        # If this area has been explored extensively, provide hints
        if hasattr(looker.db, "explored_rooms") and self.id in looker.db.explored_rooms:
            exploration_count = looker.db.explored_rooms[self.id]
            if exploration_count > 2:
                # Give hints about what might be found here
                hints = []

                if self.db.hidden_exits:
                    hints.append("You sense there may be hidden paths in this area.")

                if self.db.treasures:
                    hints.append("This area looks like it might contain valuable items.")

                if hints:
                    appearance += "\n\n|y" + " ".join(hints) + "|n"

        return appearance

    def _spawn_encounter(self, character):
        """Create a random encounter in the room"""
        # Check if character is still in the room
        if character.location != self:
            return

        # Determine encounter type and difficulty based on danger level
        difficulty = self.db.danger_level

        # For simplicity, we'll use two types: bug creatures and firewall guardians
        encounter_type = "bug creature" if difficulty <= 5 else "firewall guardian"

        # Try to spawn from prototype
        from evennia.utils.spawner import spawn
        proto_key = encounter_type.upper().replace(" ", "_")

        try:
            result = spawn(proto_key, prototype_modules=["world.prototypes"])
            if result:
                opponent = result[0]
                opponent.location = self

                # Announce the encounter
                self.msg_contents(f"|rA {opponent.key} suddenly appears!|n")
            else:
                # Fall back to basic creation
                self._create_basic_opponent(encounter_type, difficulty)
        except Exception:
            # Fall back to basic creation
            self._create_basic_opponent(encounter_type, difficulty)

    def _create_basic_opponent(self, encounter_type, difficulty):
        """Create a basic opponent if prototype fails"""
        from typeclasses.themed_objects import Opponent

        # Scale attributes based on difficulty
        health = 50 + (difficulty * 20)
        attack = 5 + (difficulty * 2)
        defense = 2 + difficulty

        # Create loot table
        loot_table = {
            "code fragment": 0.7,
            "data crystal": 0.3
        }

        # Create the opponent
        opponent = Opponent.create(
            key=encounter_type,
            location=self,
            attributes={
                "desc": f"A dangerous {encounter_type} prowling the wilderness.",
                "health": health,
                "max_health": health,
                "attack_power": attack,
                "defense": defense,
                "loot_table": loot_table
            }
        )

        # Announce the encounter
        self.msg_contents(f"|rA {opponent.key} suddenly appears!|n")


# Central hub room - connects the four themed areas
class NexusRoom(Room):
    """
    The Nexus serves as the central connection point between the four themed areas.
    
    This room type has special capabilities for directing players to appropriate
    areas and tracking overall progress across the game's zones.
    """
    
    def at_object_creation(self):
        """Set up nexus-specific attributes."""
        super().at_object_creation()
        self.db.area_type = "nexus"
        
        # Nexus-specific attributes
        self.db.area_status = {
            "forge": {"unlocked": True, "completion": 0.0},
            "lore": {"unlocked": True, "completion": 0.0},
            "matrix": {"unlocked": True, "completion": 0.0},
            "wilderness": {"unlocked": True, "completion": 0.0}
        }