"""
Character Commands

This module contains commands related to character attributes, ability checks,
and statistics. These commands provide ways for players to view and interact
with their character's capabilities.

"""
from evennia.commands.command import Command
from evennia.utils.evtable import EvTable
from evennia import CmdSet


class CmdAttributes(Command):
    """
    View your character's attributes.

    Usage:
      attributes
      attr
      stats

    This command shows all your character's current attributes, including
    physical and mental stats, vital statistics, and progression information.

    Attributes like strength and wisdom affect what your character can do,
    while health and mana represent your current condition.
    """

    key = "attributes"
    aliases = ["attr", "stats"]
    lock = "cmd:all()"
    help_category = "Character"

    def func(self):
        """Execute the command"""
        caller = self.caller
        
        # Check if character has attributes system
        if not hasattr(caller.db, "attributes"):
            caller.msg("You don't have any attributes defined.")
            return
            
        # Display formatted attributes
        attrs_display = caller.get_attributes_display()
        caller.msg(f"|cYour Attributes:|n\n{attrs_display}")
        
        # Show experience info if available
        if hasattr(caller.db, "attributes"):
            attrs = caller.db.attributes
            current_level = attrs.get("level")
            current_exp = attrs.get("experience")
            next_level_exp = attrs.get_exp_for_next_level()
            
            if all(x is not None for x in [current_level, current_exp, next_level_exp]):
                exp_needed = next_level_exp - current_exp
                caller.msg(f"|wLevel: {current_level}  XP: {current_exp}/{next_level_exp} (Need {exp_needed} more for next level)|n")


class CmdRoll(Command):
    """
    Roll ability checks using your character's attributes.

    Usage:
      roll <attribute> [difficulty]
      check <attribute> [difficulty]

    This command rolls a d20 and adds your attribute modifier to check
    against a difficulty class (DC). If no difficulty is specified,
    a standard check (DC 10) is performed.

    Available attributes to roll:
      strength, dexterity, wisdom

    Examples:
      roll strength
      roll wisdom 15
      check dexterity 12
    """

    key = "roll"
    aliases = ["check"]
    lock = "cmd:all()"
    help_category = "Character"

    def func(self):
        """Execute the command"""
        caller = self.caller
        
        if not self.args:
            caller.msg("What attribute do you want to roll? (strength, dexterity, wisdom)")
            return
            
        # Parse arguments
        args = self.args.strip().split()
        attr_name = args[0].lower()
        
        # Check for valid attribute
        valid_attrs = ["strength", "dexterity", "wisdom"]
        if attr_name not in valid_attrs:
            caller.msg(f"Invalid attribute. Choose from: {', '.join(valid_attrs)}")
            return
            
        # Parse difficulty (default to 10)
        difficulty = 10
        if len(args) > 1:
            try:
                difficulty = int(args[1])
                if difficulty < 1:
                    difficulty = 1
            except ValueError:
                caller.msg(f"Invalid difficulty number: {args[1]}. Using default (10).")
                difficulty = 10
                
        # Perform ability check
        success, roll, bonus = caller.ability_check(attr_name, difficulty)
        
        # Format results
        total = roll + bonus
        result_color = "|g" if success else "|r"
        
        # Create detailed output
        roll_text = f"Rolling {attr_name} check (DC {difficulty}):"
        roll_detail = f"d20 roll: {roll}"
        
        if bonus >= 0:
            bonus_text = f"+ {bonus} ({attr_name} bonus)"
        else:
            bonus_text = f"- {abs(bonus)} ({attr_name} penalty)"
            
        result_text = f"{result_color}Result: {total} ({'SUCCESS' if success else 'FAILURE'})|n"
        
        # Send the message
        caller.msg(f"{roll_text}\n{roll_detail} {bonus_text}\n{result_text}")
        
        # If in a room with others, show a public message
        if hasattr(caller, "location") and caller.location:
            others_msg = f"{caller.name} rolls a {attr_name} check."
            caller.location.msg_contents(others_msg, exclude=caller)


class CmdLevelUp(Command):
    """
    Check your progress toward the next level or distribute level-up points.

    Usage:
      levelup
      level

    This command shows your current level and progress toward the next level,
    or lets you distribute attribute points when you level up.
    """

    key = "levelup"
    aliases = ["level"]
    lock = "cmd:all()"
    help_category = "Character"

    def func(self):
        """Execute the command"""
        caller = self.caller
        
        # Check if character has attributes system
        if not hasattr(caller.db, "attributes"):
            caller.msg("You don't have any attributes defined.")
            return
            
        # Get level information
        attrs = caller.db.attributes
        current_level = attrs.get("level")
        current_exp = attrs.get("experience")
        next_level_exp = attrs.get_exp_for_next_level()
        
        # Simple progress bar
        if next_level_exp > 0:
            progress_percent = (current_exp / next_level_exp) * 100
            bar_length = 20
            filled_length = int(bar_length * (current_exp / next_level_exp))
            bar = "|g" + "=" * filled_length + "|w" + "-" * (bar_length - filled_length) + "|n"
        else:
            progress_percent = 0
            bar = "|w" + "-" * 20 + "|n"
            
        # Display level information
        caller.msg(f"|cLevel Information:|n")
        caller.msg(f"Current Level: {current_level}")
        caller.msg(f"Experience: {current_exp}/{next_level_exp}")
        caller.msg(f"Progress: {bar} ({progress_percent:.1f}%)")
        caller.msg(f"XP Needed: {next_level_exp - current_exp}")
        
        # Show physical attributes
        caller.msg("\n|cPrimary Attributes:|n")
        for attr in ["strength", "dexterity", "wisdom"]:
            value = attrs.get(attr)
            modifier = (value - 10) // 2
            mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
            caller.msg(f"{attr.capitalize()}: {value} ({mod_str} modifier)")


class CmdGiveXP(Command):
    """
    Award experience points to a character.

    Usage:
      givexp <character> <amount>
      awardxp <character> <amount>

    This admin command grants experience points to a character,
    possibly triggering a level up if enough XP is awarded.

    Examples:
      givexp Anna 100
      awardxp #123 50
    """

    key = "givexp"
    aliases = ["awardxp"]
    lock = "cmd:perm(Admin)"
    help_category = "Admin"

    def func(self):
        """Execute the command"""
        caller = self.caller
        
        if not self.args or len(self.args.split()) < 2:
            caller.msg("Usage: givexp <character> <amount>")
            return
            
        # Parse arguments
        args = self.args.split()
        target_name = args[0]
        
        try:
            xp_amount = int(args[1])
        except ValueError:
            caller.msg(f"Invalid XP amount: {args[1]}")
            return
            
        if xp_amount <= 0:
            caller.msg("XP amount must be positive.")
            return
            
        # Find the target character
        target = caller.search(target_name)
        if not target:
            return
            
        # Award experience
        if hasattr(target, "add_experience"):
            result = target.add_experience(xp_amount)
            
            # Report the results
            caller.msg(f"Awarded {xp_amount} XP to {target.name}.")
            
            if result["leveled_up"]:
                caller.msg(f"{target.name} leveled up to level {result['new_level']}!")
        else:
            caller.msg(f"{target.name} cannot receive experience points.")


class CharacterCmdSet(CmdSet):
    """
    Cmdset for character attributes and related commands.
    """
    
    key = "character_commands"
    
    def at_cmdset_creation(self):
        """
        Add character commands to the command set
        """
        self.add(CmdAttributes())
        self.add(CmdRoll())
        self.add(CmdLevelUp())
        self.add(CmdGiveXP())