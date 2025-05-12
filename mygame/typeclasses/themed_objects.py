"""
Themed Objects

This module contains custom object typeclasses for the four themed areas
of the Pythonic MUD, each designed to support specific gameplay mechanics.

"""
from typeclasses.objects import Object


class ThemedObject(Object):
    """
    Base class for all themed objects with common functionality.
    
    Attributes:
        area_type (str): One of "forge", "lore", "matrix", "wilderness"
        difficulty (int): A value from 1-10 indicating challenge level
    """
    
    def at_object_creation(self):
        """Set up basic attributes for all themed objects."""
        super().at_object_creation()
        self.db.area_type = "base"
        self.db.difficulty = 1
        self.db.creator = None  # Who created this object (if applicable)


class CraftingObject(ThemedObject):
    """
    Objects in the CREATE/Forge area related to crafting.
    
    These objects include crafting materials, tools, workbenches, and
    crafted items. They support the crafting system mechanics.
    """
    
    def at_object_creation(self):
        """Set up crafting-specific attributes."""
        super().at_object_creation()
        self.db.area_type = "forge"
        
        # Crafting-related attributes
        self.db.material_type = None  # Type of crafting material
        self.db.durability = 100  # How long the object lasts (percentage)
        self.db.quality = 1  # Quality level (1-10)
        self.db.required_tools = []  # Tools needed to work with this material
        self.db.crafting_recipes = {}  # For workbenches: available recipes


class LoreObject(ThemedObject):
    """
    Objects in the EXPLAIN/Lore Halls area related to knowledge and dialogue.
    
    These objects include books, scrolls, knowledge crystals, and other
    information-bearing items. They support the knowledge system.
    """
    
    def at_object_creation(self):
        """Set up lore-specific attributes."""
        super().at_object_creation()
        self.db.area_type = "lore"
        
        # Knowledge-related attributes
        self.db.knowledge_topics = []  # Topics contained in this object
        self.db.readable = True  # Can be read to gain knowledge
        self.db.read_by = set()  # Characters who have read this object


class CodeObject(ThemedObject):
    """
    Objects in the CODE/Arcane Matrix area related to programming puzzles.
    
    These objects include terminals, code fragments, logic puzzles, and
    hackable devices. They support the programming challenge system.
    """
    
    def at_object_creation(self):
        """Set up code-specific attributes."""
        super().at_object_creation()
        self.db.area_type = "matrix"
        
        # Programming-related attributes
        self.db.puzzle_type = None  # Type of programming puzzle
        self.db.current_state = None  # Current state of the puzzle
        self.db.goal_state = None  # Target state to solve puzzle
        self.db.hints = []  # Available hints
        self.db.solved_by = set()  # Characters who have solved this puzzle


class ExplorationObject(ThemedObject):
    """
    Objects in the EXPLORE/Neon Wilderness area related to exploration.
    
    These objects include treasures, environmental elements, combat gear,
    and navigational tools. They support exploration and combat systems.
    """
    
    def at_object_creation(self):
        """Set up exploration-specific attributes."""
        super().at_object_creation()
        self.db.area_type = "wilderness"
        
        # Exploration-related attributes
        self.db.is_treasure = False  # Whether this is a valuable find
        self.db.combat_modifiers = {}  # Modifiers for combat if applicable
        self.db.is_hidden = False  # Whether object starts hidden
        self.db.discovery_difficulty = 1  # How hard to find (1-10)


# Workbench for crafting
class Workbench(CraftingObject):
    """
    A specialized crafting station that enables the creation of items.
    
    Workbenches are interactive objects that allow players to combine
    materials to create new items according to recipes.
    """
    
    def at_object_creation(self):
        """Set up workbench-specific attributes."""
        super().at_object_creation()
        
        # Workbench attributes
        self.db.workbench_type = "basic"  # Type of workbench
        self.db.crafting_recipes = {}  # Available recipes at this workbench
        self.db.required_materials = {}  # Materials needed for each recipe
        self.db.active_crafter = None  # Who is currently using this workbench
        
        # Lock the workbench so it can't be picked up
        self.locks.add("get:false()")


# NPC for dialogues
class NPC(LoreObject):
    """
    A non-player character that can engage in dialogue with players.

    NPCs are interactive objects that can respond to conversation
    and provide knowledge, quests, or services to players.
    """

    def at_object_creation(self):
        """Set up NPC-specific attributes."""
        super().at_object_creation()

        # NPC dialogue and interaction attributes
        self.db.dialogue_tree = {}  # Available conversation options
        self.db.mood = "neutral"  # Current disposition
        self.db.knowledge = {}  # What this NPC knows and can share
        self.db.services = []  # Services this NPC can provide

        # Initialize character attributes
        from .attributes import CharacterAttributes
        self.db.attributes = CharacterAttributes(self)

        # Set default NPC level to 1
        self.db.level = 1

        # Lock the NPC so it can't be picked up
        self.locks.add("get:false()")

    def get_attribute(self, attr_name):
        """
        Get the value of an NPC attribute.

        Args:
            attr_name (str): The name of the attribute to get

        Returns:
            The current attribute value or None if not found
        """
        if hasattr(self.db, "attributes"):
            return self.db.attributes.get(attr_name)
        return None

    def set_attribute(self, attr_name, value):
        """
        Set an NPC attribute.

        Args:
            attr_name (str): The name of the attribute to set
            value: The new value for the attribute

        Returns:
            bool: True if successful, False otherwise
        """
        if hasattr(self.db, "attributes"):
            return self.db.attributes.set(attr_name, value)
        return False

    def get_attributes_display(self):
        """
        Get a formatted display of NPC attributes.

        Returns:
            str: Formatted attributes for display
        """
        if hasattr(self.db, "attributes"):
            return self.db.attributes.format_attributes()
        return "No attributes available."

    def ability_check(self, attr_name, difficulty=10):
        """
        Perform an ability check using one of the NPC's attributes.

        Args:
            attr_name (str): The attribute to check against
            difficulty (int): Target number to meet or exceed

        Returns:
            tuple: (success, roll, bonus)
                - success (bool): True if check passed
                - roll (int): Raw dice roll (1-20)
                - bonus (int): Attribute bonus applied
        """
        if not hasattr(self.db, "attributes"):
            return (False, 0, 0)

        from .attributes import roll_ability_check
        return roll_ability_check(self.db.attributes, attr_name, difficulty)

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.
        """
        appearance = super().return_appearance(looker)

        # Add level to appearance
        if hasattr(self.db, "attributes") and self.db.attributes.get("level"):
            level = self.db.attributes.get("level")
            level_text = f"\n|yLevel {level} NPC|n"
            appearance += level_text

        return appearance


# Terminal for coding puzzles
class Terminal(CodeObject):
    """
    An interactive terminal for solving programming challenges.
    
    Terminals present players with coding puzzles that must be
    solved using Python syntax and programming concepts.
    """
    
    def at_object_creation(self):
        """Set up terminal-specific attributes."""
        super().at_object_creation()
        
        # Terminal attributes
        self.db.puzzle_type = "code"  # Type of programming puzzle
        self.db.current_code = ""  # Current code in the editor
        self.db.expected_output = ""  # Output that indicates success
        self.db.current_user = None  # Who is currently using this terminal
        
        # Lock the terminal so it can't be picked up
        self.locks.add("get:false()")


# Combat opponent for the wilderness
class Opponent(ExplorationObject):
    """
    A creature or entity that engages in combat with players.

    Opponents present combat challenges in the wilderness area,
    with varying levels of difficulty and different combat styles.
    """

    def at_object_creation(self):
        """Set up opponent-specific attributes."""
        super().at_object_creation()

        # Initialize character attributes
        from .attributes import CharacterAttributes
        self.db.attributes = CharacterAttributes(self)

        # Set default level to 1 (can be adjusted later)
        self.db.attributes.set("level", 1)

        # Additional combat attributes
        self.db.combat_style = "melee"  # melee, ranged, magic
        self.db.attack_patterns = ["basic"]  # List of available attack types
        self.db.loot_table = {}  # Potential drops when defeated

        # Lock the opponent so it can't be picked up
        self.locks.add("get:false()")

    def get_attribute(self, attr_name):
        """
        Get the value of an opponent attribute.

        Args:
            attr_name (str): The name of the attribute to get

        Returns:
            The current attribute value or None if not found
        """
        if hasattr(self.db, "attributes"):
            return self.db.attributes.get(attr_name)
        return None

    def set_attribute(self, attr_name, value):
        """
        Set an opponent attribute.

        Args:
            attr_name (str): The name of the attribute to set
            value: The new value for the attribute

        Returns:
            bool: True if successful, False otherwise
        """
        if hasattr(self.db, "attributes"):
            return self.db.attributes.set(attr_name, value)
        return False

    def ability_check(self, attr_name, difficulty=10):
        """
        Perform an ability check using one of the opponent's attributes.

        Args:
            attr_name (str): The attribute to check against
            difficulty (int): Target number to meet or exceed

        Returns:
            tuple: (success, roll, bonus)
                - success (bool): True if check passed
                - roll (int): Raw dice roll (1-20)
                - bonus (int): Attribute bonus applied
        """
        if not hasattr(self.db, "attributes"):
            return (False, 0, 0)

        from .attributes import roll_ability_check
        return roll_ability_check(self.db.attributes, attr_name, difficulty)

    def at_damage(self, damage):
        """
        Handle this opponent taking damage.

        Args:
            damage (int): Amount of damage to take

        Returns:
            int: Actual damage taken after defenses
        """
        if not hasattr(self.db, "attributes"):
            return 0

        # Get current health and defense
        current_health = self.db.attributes.get("health")
        defense = self.db.attributes.get("defense")

        # Reduce damage by defense, minimum 1
        actual_damage = max(1, damage - defense)

        # Apply damage
        new_health = max(0, current_health - actual_damage)
        self.db.attributes.set("health", new_health)

        return actual_damage

    def is_defeated(self):
        """
        Check if this opponent has been defeated.

        Returns:
            bool: True if the opponent's health is 0, False otherwise
        """
        if not hasattr(self.db, "attributes"):
            return False

        return self.db.attributes.get("health") <= 0

    def return_appearance(self, looker):
        """
        This formats a description. It is the hook a 'look' command
        should call.
        """
        appearance = super().return_appearance(looker)

        # Add health bar and level if attributes exist
        if hasattr(self.db, "attributes"):
            health = self.db.attributes.get("health")
            max_health = self.db.attributes.get("max_health")
            level = self.db.attributes.get("level")

            if health is not None and max_health is not None:
                # Create a health bar
                bar_length = 20
                health_percent = health / max_health
                filled_length = int(bar_length * health_percent)
                health_bar = "|g" + "=" * filled_length + "|r" + "-" * (bar_length - filled_length) + "|n"

                status_text = f"\n|rHealth:|n {health}/{max_health} {health_bar}"

                # Add level if available
                if level:
                    status_text += f"\n|yLevel {level} Opponent|n"

                appearance += status_text

        return appearance

    def scale_to_level(self, level):
        """
        Scale this opponent's attributes to match a specific level.

        Args:
            level (int): The target level

        Returns:
            dict: The scaled attributes
        """
        if not hasattr(self.db, "attributes"):
            return {}

        if level < 1:
            level = 1

        # Set basic attributes
        self.db.attributes.set("level", level)

        # Scale health based on level
        base_health = 50
        health_per_level = 10
        max_health = base_health + (level * health_per_level)
        self.db.attributes.set("max_health", max_health)
        self.db.attributes.set("health", max_health)

        # Scale mana based on level
        base_mana = 20
        mana_per_level = 5
        max_mana = base_mana + (level * mana_per_level)
        self.db.attributes.set("max_mana", max_mana)
        self.db.attributes.set("mana", max_mana)

        # Scale combat stats based on level
        base_attr = 8
        attr_per_level = 0.5

        strength = base_attr + int(level * attr_per_level)
        dexterity = base_attr + int(level * attr_per_level)
        wisdom = base_attr + int(level * attr_per_level)

        self.db.attributes.set("strength", strength)
        self.db.attributes.set("dexterity", dexterity)
        self.db.attributes.set("wisdom", wisdom)

        # Return the set attributes
        return {
            "level": level,
            "max_health": max_health,
            "health": max_health,
            "max_mana": max_mana,
            "mana": max_mana,
            "strength": strength,
            "dexterity": dexterity,
            "wisdom": wisdom
        }