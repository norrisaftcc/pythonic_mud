"""
Attributes

This module implements a flexible attribute system for characters in the MUD,
including both player characters and NPCs.

"""
from evennia import AttributeProperty
from enum import Enum
import random


class AttributeType(Enum):
    """
    Enumeration of different attribute types to categorize stats.
    """
    PHYSICAL = "physical"  # Strength, Dexterity, etc.
    MENTAL = "mental"      # Wisdom, Intelligence, etc.
    VITAL = "vital"        # Health, Mana, etc.
    PROGRESSION = "progression"  # Level, Experience, etc.


class AttributeDefinition:
    """
    Defines a specific character attribute, its properties, and behavior.
    """
    def __init__(
        self, 
        name, 
        attr_type,
        default_value=0, 
        min_value=0, 
        max_value=None,
        affects=None,
        description=""
    ):
        """
        Initialize an attribute definition.
        
        Args:
            name (str): The name of the attribute (e.g., "strength")
            attr_type (AttributeType): The category this attribute belongs to
            default_value (int/float): Starting value for this attribute
            min_value (int/float): Minimum allowed value
            max_value (int/float): Maximum allowed value (None for no maximum)
            affects (list): List of other attributes this attribute affects
            description (str): Human-readable description of this attribute
        """
        self.name = name
        self.attr_type = attr_type
        self.default_value = default_value
        self.min_value = min_value
        self.max_value = max_value
        self.affects = affects or []
        self.description = description or f"The character's {name.replace('_', ' ')}."


class CharacterAttributes:
    """
    A container class for character attributes that handles
    attribute values, modifiers, and calculations.
    """
    # Define standard attribute definitions
    ATTRIBUTE_DEFINITIONS = {
        # Physical attributes
        "strength": AttributeDefinition(
            "strength", 
            AttributeType.PHYSICAL, 
            default_value=10, 
            min_value=1,
            description="Physical power, affects damage and carrying capacity."
        ),
        "dexterity": AttributeDefinition(
            "dexterity", 
            AttributeType.PHYSICAL, 
            default_value=10, 
            min_value=1,
            description="Agility and reflexes, affects accuracy and dodge chance."
        ),
        # Mental attributes
        "wisdom": AttributeDefinition(
            "wisdom", 
            AttributeType.MENTAL, 
            default_value=10, 
            min_value=1,
            description="Intuition and perception, affects mana and awareness."
        ),
        # Vital attributes
        "health": AttributeDefinition(
            "health", 
            AttributeType.VITAL, 
            default_value=100, 
            min_value=0,
            description="Physical wellbeing, reaching 0 means defeat."
        ),
        "max_health": AttributeDefinition(
            "max_health", 
            AttributeType.VITAL, 
            default_value=100, 
            min_value=1,
            description="Maximum health capacity."
        ),
        "mana": AttributeDefinition(
            "mana", 
            AttributeType.VITAL, 
            default_value=50, 
            min_value=0,
            description="Magical energy, used for spells and abilities."
        ),
        "max_mana": AttributeDefinition(
            "max_mana", 
            AttributeType.VITAL, 
            default_value=50, 
            min_value=0,
            description="Maximum mana capacity."
        ),
        # Progression attributes
        "level": AttributeDefinition(
            "level", 
            AttributeType.PROGRESSION, 
            default_value=1, 
            min_value=1,
            description="Character level, representing overall progression."
        ),
        "experience": AttributeDefinition(
            "experience", 
            AttributeType.PROGRESSION, 
            default_value=0, 
            min_value=0,
            description="Points gained from activities, accumulate to increase level."
        ),
    }
    
    def __init__(self, owner):
        """
        Initialize attributes for a character.
        
        Args:
            owner: The Character or NPC instance these attributes belong to
        """
        self.owner = owner
        
        # Initialize all attributes with default values
        self.values = {}
        self.modifiers = {}
        
        for attr_name, attr_def in self.ATTRIBUTE_DEFINITIONS.items():
            self.values[attr_name] = attr_def.default_value
            self.modifiers[attr_name] = []
    
    def get(self, attr_name):
        """
        Get the current value of an attribute, including modifiers.
        
        Args:
            attr_name (str): The name of the attribute to get
            
        Returns:
            The current attribute value with modifiers applied
        """
        if attr_name not in self.values:
            return None
            
        base_value = self.values[attr_name]
        total_modifier = sum(mod.value for mod in self.modifiers.get(attr_name, []))
        
        attr_def = self.ATTRIBUTE_DEFINITIONS.get(attr_name)
        result = base_value + total_modifier
        
        # Apply min/max constraints
        if attr_def:
            if attr_def.min_value is not None and result < attr_def.min_value:
                result = attr_def.min_value
            if attr_def.max_value is not None and result > attr_def.max_value:
                result = attr_def.max_value
                
        return result
    
    def set(self, attr_name, value):
        """
        Set the base value of an attribute.
        
        Args:
            attr_name (str): The name of the attribute to set
            value: The new base value
            
        Returns:
            bool: True if successful, False otherwise
        """
        if attr_name not in self.ATTRIBUTE_DEFINITIONS:
            return False
            
        attr_def = self.ATTRIBUTE_DEFINITIONS[attr_name]
        
        # Apply min/max constraints
        if attr_def.min_value is not None and value < attr_def.min_value:
            value = attr_def.min_value
        if attr_def.max_value is not None and value > attr_def.max_value:
            value = attr_def.max_value
            
        self.values[attr_name] = value
        
        # If this is max_health or max_mana, we may need to adjust current values
        if attr_name == "max_health" and "health" in self.values:
            # Cap health at max_health
            if self.values["health"] > value:
                self.values["health"] = value
        elif attr_name == "max_mana" and "mana" in self.values:
            # Cap mana at max_mana
            if self.values["mana"] > value:
                self.values["mana"] = value
                
        return True
    
    def add_modifier(self, attr_name, value, source, duration=None):
        """
        Add a temporary modifier to an attribute.
        
        Args:
            attr_name (str): The attribute to modify
            value (int/float): The modifier value (can be negative)
            source (str): Description of what caused this modifier
            duration (int): Optional duration in turns (None = permanent)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if attr_name not in self.ATTRIBUTE_DEFINITIONS:
            return False
            
        mod = AttributeModifier(value, source, duration)
        self.modifiers.setdefault(attr_name, []).append(mod)
        return True
    
    def remove_modifiers_by_source(self, source):
        """
        Remove all modifiers from a particular source.
        
        Args:
            source (str): The source to remove modifiers from
            
        Returns:
            int: Number of modifiers removed
        """
        count = 0
        for attr_name in self.modifiers:
            self.modifiers[attr_name] = [
                mod for mod in self.modifiers[attr_name] 
                if mod.source != source
            ]
            count += 1
        return count
    
    def update_modifiers(self):
        """
        Update temporary modifiers, removing any that have expired.
        
        Returns:
            list: List of expired modifiers that were removed
        """
        expired = []
        for attr_name, mods in self.modifiers.items():
            remaining = []
            for mod in mods:
                if mod.update():
                    remaining.append(mod)
                else:
                    expired.append((attr_name, mod))
            self.modifiers[attr_name] = remaining
        return expired
    
    def get_all(self):
        """
        Get a dictionary of all attributes and their current values.
        
        Returns:
            dict: Attribute name -> current value (with modifiers)
        """
        return {attr: self.get(attr) for attr in self.values}
    
    def get_description(self, attr_name):
        """Get the description of an attribute."""
        if attr_name in self.ATTRIBUTE_DEFINITIONS:
            return self.ATTRIBUTE_DEFINITIONS[attr_name].description
        return None
    
    def format_attributes(self, attrs=None):
        """
        Format attributes for display.
        
        Args:
            attrs (list): Optional list of attribute names to include
                          (default: all attributes)
                          
        Returns:
            str: Formatted string displaying attributes and values
        """
        if attrs is None:
            attrs = self.values.keys()
            
        # Group attributes by type
        by_type = {}
        for attr in attrs:
            if attr in self.ATTRIBUTE_DEFINITIONS:
                attr_def = self.ATTRIBUTE_DEFINITIONS[attr]
                by_type.setdefault(attr_def.attr_type.value, []).append(attr)
        
        lines = []
        for type_name, type_attrs in by_type.items():
            lines.append(f"|y{type_name.capitalize()} Attributes:|n")
            for attr in type_attrs:
                value = self.get(attr)
                base = self.values[attr]
                if value != base:
                    # Show base value and modifiers
                    lines.append(f"  {attr.capitalize()}: {value} (Base: {base})")
                else:
                    lines.append(f"  {attr.capitalize()}: {value}")
            lines.append("")
            
        return "\n".join(lines)
    
    def handle_level_up(self):
        """
        Process a character level up, adjusting attributes accordingly.
        
        Returns:
            dict: Changes to attributes from the level up
        """
        changes = {}
        
        # Increase max health and mana based on attributes
        str_bonus = self.get("strength") // 5
        wis_bonus = self.get("wisdom") // 5
        
        old_max_health = self.get("max_health")
        old_max_mana = self.get("max_mana")
        
        new_max_health = old_max_health + 10 + str_bonus
        new_max_mana = old_max_mana + 5 + wis_bonus
        
        self.set("max_health", new_max_health)
        self.set("max_health", new_max_mana)
        
        # Restore health and mana to full
        self.set("health", new_max_health)
        self.set("mana", new_max_mana)
        
        changes["max_health"] = new_max_health - old_max_health
        changes["max_mana"] = new_max_mana - old_max_mana
        
        return changes
    
    def get_exp_for_next_level(self):
        """
        Calculate experience required for next level.
        
        Returns:
            int: Experience points needed to level up
        """
        current_level = self.get("level")
        # Simple exponential formula for required XP
        return current_level * 100
    
    def add_experience(self, amount):
        """
        Add experience points and handle level ups if appropriate.
        
        Args:
            amount (int): Amount of experience to add
            
        Returns:
            dict: Result of experience addition, including level ups
        """
        result = {
            "gained_exp": amount,
            "leveled_up": False,
            "new_level": self.get("level"),
            "attribute_changes": {}
        }
        
        if amount <= 0:
            return result
            
        current_exp = self.get("experience")
        current_level = self.get("level")
        
        self.set("experience", current_exp + amount)
        
        # Check for level up
        while True:
            next_level_exp = self.get_exp_for_next_level()
            if self.get("experience") >= next_level_exp:
                # Level up!
                new_level = current_level + 1
                self.set("level", new_level)
                self.set("experience", self.get("experience") - next_level_exp)
                
                # Update attributes for level up
                attr_changes = self.handle_level_up()
                
                result["leveled_up"] = True
                result["new_level"] = new_level
                
                # Merge attribute changes
                for attr, change in attr_changes.items():
                    if attr in result["attribute_changes"]:
                        result["attribute_changes"][attr] += change
                    else:
                        result["attribute_changes"][attr] = change
                
                current_level = new_level
            else:
                break
                
        return result


class AttributeModifier:
    """
    Represents a temporary or permanent modifier to an attribute.
    """
    def __init__(self, value, source, duration=None):
        """
        Initialize an attribute modifier.
        
        Args:
            value (int/float): Modifier value (can be negative)
            source (str): Description of what's causing this modifier
            duration (int): Duration in turns (None = permanent)
        """
        self.value = value
        self.source = source
        self.duration = duration
        self.remaining = duration
    
    def update(self):
        """
        Update the modifier, reducing its duration if temporary.
        
        Returns:
            bool: True if the modifier is still active, False if expired
        """
        if self.duration is None:
            return True  # Permanent modifier
            
        if self.remaining is None:
            return False  # Already expired
            
        self.remaining -= 1
        return self.remaining > 0
    
    def __str__(self):
        """String representation of the modifier."""
        if self.value >= 0:
            mod_str = f"+{self.value}"
        else:
            mod_str = str(self.value)
            
        if self.duration is None:
            return f"{mod_str} ({self.source}, permanent)"
        elif self.remaining is None:
            return f"{mod_str} ({self.source}, expired)"
        else:
            return f"{mod_str} ({self.source}, {self.remaining}/{self.duration} turns remaining)"


def roll_ability_check(attributes, attr_name, difficulty=10):
    """
    Roll for a character to pass an ability check.
    
    Args:
        attributes (CharacterAttributes): Character's attributes
        attr_name (str): Attribute to check against
        difficulty (int): Target number to meet or exceed
        
    Returns:
        tuple: (success, roll, bonus)
            - success (bool): True if check passed
            - roll (int): Raw dice roll (1-20)
            - bonus (int): Attribute bonus applied
    """
    if attr_name not in attributes.values:
        return (False, 0, 0)
        
    # Get the attribute value
    attr_value = attributes.get(attr_name)
    
    # Calculate bonus from attribute
    # We'll use (attr_value - 10) // 2 to match D&D-style modifiers
    bonus = (attr_value - 10) // 2
    
    # Roll d20
    roll = random.randint(1, 20)
    
    # Check result against difficulty
    total = roll + bonus
    success = total >= difficulty
    
    return (success, roll, bonus)