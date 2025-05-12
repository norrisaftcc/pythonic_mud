"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from .attributes import CharacterAttributes, roll_ability_check


class Character(DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    def at_object_creation(self):
        """
        Called when object is first created.
        """
        super().at_object_creation()

        # Initialize character attributes
        self.db.attributes = CharacterAttributes(self)

        # Combat and interaction stats will be derived from attributes
        self.db.combat = {
            "target": None,
            "weapon": None,
            "last_attack": None,
        }

    def get_attribute(self, attr_name):
        """
        Get the value of a character attribute.

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
        Set a character attribute.

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
        Get a formatted display of character attributes.

        Returns:
            str: Formatted attributes for display
        """
        if hasattr(self.db, "attributes"):
            return self.db.attributes.format_attributes()
        return "No attributes available."

    def ability_check(self, attr_name, difficulty=10):
        """
        Perform an ability check using one of the character's attributes.

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

        return roll_ability_check(self.db.attributes, attr_name, difficulty)

    def add_experience(self, amount):
        """
        Add experience points to the character and handle level ups.

        Args:
            amount (int): Amount of experience to add

        Returns:
            dict: Result of experience addition, including level ups
        """
        if not hasattr(self.db, "attributes"):
            return {
                "gained_exp": 0,
                "leveled_up": False,
                "new_level": 1,
                "attribute_changes": {}
            }

        result = self.db.attributes.add_experience(amount)

        # Announce level up if it occurred
        if result["leveled_up"]:
            self.msg(f"|gCongratulations! You have reached level {result['new_level']}!|n")

            # Show attribute changes
            if result["attribute_changes"]:
                changes = []
                for attr, change in result["attribute_changes"].items():
                    if change > 0:
                        changes.append(f"{attr.capitalize()} +{change}")
                    else:
                        changes.append(f"{attr.capitalize()} {change}")

                if changes:
                    self.msg(f"Your attributes have improved: {', '.join(changes)}")

            # Restore health and mana to full
            self.msg("Your health and mana have been fully restored.")

        return result
