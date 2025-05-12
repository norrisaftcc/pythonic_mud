"""
Wilderness (EXPLORE) Commands

This module contains commands for the EXPLORE/Neon Wilderness area of the Pythonic MUD.
These commands enable exploration, discovery, and combat mechanics for the
adventure-focused wilderness area.

"""
from evennia.commands.command import Command
from evennia.utils.evtable import EvTable
from evennia import CmdSet
import random


class CmdExplore(Command):
    """
    Search the current area for hidden features and resources.

    Usage:
      explore
      explore <direction>

    This command allows you to thoroughly search the area for
    hidden objects, secret exits, and valuable resources that
    aren't immediately visible.

    With a direction specified, you focus your exploration in
    that particular area of the room.

    Examples:
      explore
      explore north
      explore under rocks
    """

    key = "explore"
    aliases = ["search"]
    help_category = "Wilderness"

    def func(self):
        """Implement the command"""
        caller = self.caller
        location = caller.location

        # Check if this is a wilderness room that supports exploration
        if not hasattr(location, 'db') or location.db.area_type != "wilderness":
            caller.msg("There's nothing special to explore here.")
            return

        # Track exploration attempts
        if not hasattr(caller.db, "explored_rooms"):
            caller.db.explored_rooms = {}
        
        if location.id not in caller.db.explored_rooms:
            caller.db.explored_rooms[location.id] = 0
        
        # Increment exploration counter for this room
        caller.db.explored_rooms[location.id] += 1
        exploration_count = caller.db.explored_rooms[location.id]
        
        # Get a focused direction if specified
        if self.args:
            direction = self.args.strip().lower()
            focused = True
        else:
            direction = None
            focused = False
        
        # Check for hidden exits first
        found_exit = self._check_for_hidden_exits(caller, location, direction, exploration_count)
        
        # Check for hidden objects next
        if not found_exit:
            found_object = self._check_for_hidden_objects(caller, location, direction, exploration_count)
            
            if not found_object:
                # If nothing was found, give an appropriate message
                if focused:
                    caller.msg(f"You search carefully {direction}, but find nothing of interest.")
                else:
                    if exploration_count > 3:
                        caller.msg("You've thoroughly explored this area and doubt there's anything else to find.")
                    else:
                        caller.msg("You explore the area but don't find anything noteworthy.")

    def _check_for_hidden_exits(self, caller, location, direction, exploration_count):
        """Check for hidden exits in the room"""
        # Check if the room has hidden exits
        if not hasattr(location.db, "hidden_exits") or not location.db.hidden_exits:
            return False
            
        # Filter exits by direction if specified
        available_exits = {}
        if direction:
            for exit_name, exit_data in location.db.hidden_exits.items():
                if direction in exit_name.lower():
                    available_exits[exit_name] = exit_data
        else:
            available_exits = location.db.hidden_exits
            
        if not available_exits:
            return False
            
        # Determine chance to find an exit based on exploration count
        base_chance = 0.2  # 20% base chance
        bonus = min(0.5, exploration_count * 0.1)  # +10% per exploration, max +50%
        
        # Roll for each exit
        for exit_name, exit_data in available_exits.items():
            difficulty = exit_data.get("difficulty", 5)
            # Scale from 1-10 difficulty to 0.1-1.0 modifier (lower is harder)
            difficulty_mod = (11 - difficulty) / 10.0
            
            find_chance = base_chance + bonus
            find_chance *= difficulty_mod
            
            if random.random() < find_chance:
                # Found a hidden exit!
                self._reveal_exit(caller, location, exit_name, exit_data)
                return True
                
        return False
        
    def _reveal_exit(self, caller, location, exit_name, exit_data):
        """Reveal a hidden exit by creating it"""
        destination_name = exit_data.get("destination")
        
        # Check if the destination exists
        destination = None
        if destination_name:
            from evennia.utils.search import search_object
            matches = search_object(destination_name)
            if matches:
                destination = matches[0]
        
        if not destination:
            caller.msg(f"You discover what looks like a hidden path {exit_name}, but it seems impassable.")
            return
            
        # Create the exit
        from evennia.utils.create import create_object
        from typeclasses.exits import Exit
        
        new_exit = create_object(
            Exit,
            key=exit_name,
            location=location,
            attributes=[
                ("desc", exit_data.get("desc", f"A hidden path leading {exit_name}.")),
            ],
        )
        
        # Set the destination
        new_exit.destination = destination
        
        # Remove from hidden exits
        del location.db.hidden_exits[exit_name]
        
        # Announce the discovery
        caller.msg(f"|gYou've discovered a hidden path leading {exit_name}!|n")
        location.msg_contents(f"{caller.key} has discovered a hidden path leading {exit_name}!", exclude=caller)

    def _check_for_hidden_objects(self, caller, location, direction, exploration_count):
        """Check for hidden objects in the room"""
        # Look for objects in this room that are hidden
        hidden_objects = []
        
        # First check if there are existing objects in the room that are hidden
        for obj in location.contents:
            if hasattr(obj, 'db') and obj.db.is_hidden and obj != caller:
                hidden_objects.append(obj)
                
        # If there are no objects and the room has no treasure, return False
        if not hidden_objects and (not hasattr(location.db, "treasures") or not location.db.treasures):
            return False
            
        # Determine chance to find an object based on exploration count
        base_chance = 0.25  # 25% base chance
        bonus = min(0.5, exploration_count * 0.1)  # +10% per exploration, max +50%
        
        # Roll for existing hidden objects first
        for obj in hidden_objects:
            difficulty = obj.db.discovery_difficulty if hasattr(obj.db, "discovery_difficulty") else 5
            # Scale from 1-10 difficulty to 0.1-1.0 modifier (lower is harder)
            difficulty_mod = (11 - difficulty) / 10.0
            
            find_chance = base_chance + bonus
            find_chance *= difficulty_mod
            
            # Direction focus increases chance for applicable objects
            if direction and obj.key.lower() in direction:
                find_chance += 0.2
                
            if random.random() < find_chance:
                # Found a hidden object!
                obj.db.is_hidden = False
                caller.msg(f"|gYou've discovered {obj.key}!|n")
                location.msg_contents(f"{caller.key} has discovered {obj.key}!", exclude=caller)
                return True
                
        # If we didn't find an existing object, check for potential treasures to spawn
        if hasattr(location.db, "treasures") and location.db.treasures:
            # Filter treasures by direction if specified
            available_treasures = {}
            if direction:
                for treasure_name, treasure_data in location.db.treasures.items():
                    if direction in treasure_name.lower():
                        available_treasures[treasure_name] = treasure_data
            else:
                available_treasures = location.db.treasures
                
            if not available_treasures:
                return False
                
            # Roll for each treasure
            for treasure_name, treasure_data in available_treasures.items():
                difficulty = treasure_data.get("difficulty", 5)
                # Scale from 1-10 difficulty to 0.1-1.0 modifier (lower is harder)
                difficulty_mod = (11 - difficulty) / 10.0
                
                find_chance = base_chance + bonus
                find_chance *= difficulty_mod
                
                if random.random() < find_chance:
                    # Create the treasure!
                    self._create_treasure(caller, location, treasure_name, treasure_data)
                    
                    # Remove from potential treasures
                    del location.db.treasures[treasure_name]
                    return True
                    
        return False
        
    def _create_treasure(self, caller, location, treasure_name, treasure_data):
        """Create a treasure object from the treasure data"""
        # Try to spawn the treasure using prototype if available
        proto_key = treasure_data.get("prototype")
        
        if proto_key:
            from evennia.utils.spawner import spawn
            try:
                # Convert to upper case and replace spaces with underscores for prototype key format
                proto_key = proto_key.upper().replace(" ", "_")
                result = spawn(proto_key, prototype_modules=["world.prototypes"])
                if result:
                    treasure = result[0]
                    treasure.location = location
                    
                    # Announce the discovery
                    caller.msg(f"|gYou've discovered {treasure.key}!|n")
                    location.msg_contents(f"{caller.key} has discovered {treasure.key}!", exclude=caller)
                    return
            except Exception:
                # Fall through to manual creation if prototype fails
                pass
                
        # Manual creation if prototype didn't work or wasn't specified
        from typeclasses.themed_objects import ExplorationObject
        
        # Get attributes for the treasure
        attrs = {
            "desc": treasure_data.get("desc", f"A valuable item found in the wilderness."),
            "is_treasure": True,
            "discovery_difficulty": treasure_data.get("difficulty", 5)
        }
        
        # Add any other attributes from treasure_data
        for key, value in treasure_data.items():
            if key not in ["prototype", "desc", "difficulty"]:
                attrs[key] = value
                
        # Create the treasure
        treasure = ExplorationObject.create(
            key=treasure_name,
            location=location,
            attributes=attrs
        )
        
        # Announce the discovery
        caller.msg(f"|gYou've discovered {treasure.key}!|n")
        location.msg_contents(f"{caller.key} has discovered {treasure.key}!", exclude=caller)


class CmdAttack(Command):
    """
    Attack an opponent or target.

    Usage:
      attack <target>
      attack <target> with <weapon>

    This command initiates combat with the specified target.
    If a weapon is specified, you will attack with that item.
    Otherwise, you'll use your default/equipped weapon or unarmed combat.

    Examples:
      attack bug creature
      attack guardian with sword
    """

    key = "attack"
    aliases = ["fight", "hit"]
    help_category = "Wilderness"

    def func(self):
        """Implement the command"""
        caller = self.caller
        
        if not self.args:
            caller.msg("Attack what?")
            return
            
        # Check if a weapon is specified
        if " with " in self.args:
            target_name, weapon_name = self.args.split(" with ", 1)
            target_name = target_name.strip()
            weapon_name = weapon_name.strip()
            
            # Look for the weapon
            weapon = caller.search(weapon_name, location=caller)
            if not weapon:
                return
        else:
            target_name = self.args.strip()
            weapon = None
            
            # Try to find an equipped weapon
            if hasattr(caller.db, "equipped") and caller.db.equipped:
                weapon = caller.db.equipped.get("weapon")
        
        # Look for the target
        target = caller.search(target_name)
        if not target:
            return
            
        # Check if the target is actually an opponent
        if not hasattr(target, 'db') or not hasattr(target.db, "health"):
            caller.msg(f"{target.key} doesn't look like a valid combat target.")
            return
            
        # Initialize combat attributes if needed
        if not hasattr(caller.db, "combat"):
            caller.db.combat = {
                "target": None,
                "weapon": None,
                "health": 100,
                "max_health": 100,
                "attack_power": 10,
                "defense": 5,
                "last_attack": None
            }
            
        # Set the target and weapon
        caller.db.combat["target"] = target
        caller.db.combat["weapon"] = weapon
        
        # Perform the attack
        self._do_attack(caller, target, weapon)
        
    def _do_attack(self, attacker, defender, weapon):
        """Execute the attack and calculate damage"""
        # More sophisticated attack logic using attributes

        # Roll attack using strength or dexterity (depending on weapon type)
        attr_name = "strength"  # Default for melee
        if weapon and hasattr(weapon.db, "weapon_type") and weapon.db.weapon_type == "ranged":
            attr_name = "dexterity"  # Use dexterity for ranged weapons

        # Get the attacker's attribute bonus
        if hasattr(attacker, "get_attribute"):
            attr_value = attacker.get_attribute(attr_name)
            attr_bonus = (attr_value - 10) // 2 if attr_value is not None else 0
        else:
            # Fallback if attacker doesn't have the attribute system
            attr_bonus = 0

        # Roll to hit (d20 + attribute bonus)
        import random
        hit_roll = random.randint(1, 20)
        hit_total = hit_roll + attr_bonus

        # Get defender's defense from attributes if available
        if hasattr(defender, "get_attribute"):
            defense = defender.get_attribute("defense")
            if defense is None:
                # If no specific defense stat, derive from dexterity
                dex = defender.get_attribute("dexterity")
                defense = (dex - 10) // 2 if dex is not None else 0
        else:
            # Fallback if defender doesn't have attributes
            defense = getattr(defender.db, "defense", 0)

        # Minimum defense value
        defense = max(0, defense)

        # Check if attack hits (need to overcome defense + 10)
        defense_class = 10 + defense
        hit_success = hit_total >= defense_class

        if not hit_success:
            # Attack missed
            attacker.msg(f"Your attack against {defender.key} misses!")
            defender.msg(f"{attacker.key}'s attack misses you!")
            attacker.location.msg_contents(
                f"{attacker.key} attacks {defender.key} but misses.",
                exclude=[attacker, defender]
            )
            return

        # Calculate base damage
        if hasattr(attacker, "get_attribute"):
            strength = attacker.get_attribute("strength")
            base_damage = random.randint(1, 4) + ((strength - 10) // 2 if strength is not None else 0)
            base_damage = max(1, base_damage)  # Minimum 1 damage
        else:
            # Fallback for non-attribute entities
            base_damage = getattr(attacker.db.combat, "attack_power", 5)

        # Add weapon bonus if applicable
        weapon_damage = 0
        weapon_name = "unarmed"

        if weapon:
            weapon_damage = weapon.db.damage if hasattr(weapon.db, "damage") else 5
            weapon_name = weapon.key

        # Calculate total damage
        raw_damage = base_damage + weapon_damage

        # Get defender's damage reduction from attributes or defense stat
        damage_reduction = 0
        if hasattr(defender, "get_attribute"):
            defense_attr = defender.get_attribute("defense")
            if defense_attr is not None:
                damage_reduction = defense_attr

        # Apply damage reduction
        damage = max(1, raw_damage - damage_reduction)  # Minimum 1 damage

        # Apply damage to defender
        if hasattr(defender, "at_damage"):
            actual_damage = defender.at_damage(damage)
        else:
            # Fallback for entities without at_damage method
            if hasattr(defender.db, "health"):
                defender.db.health -= damage
            elif hasattr(defender.db, "attributes") and defender.db.attributes.get("health") is not None:
                current_health = defender.db.attributes.get("health")
                defender.db.attributes.set("health", max(0, current_health - damage))
            actual_damage = damage

        # Check if defender is defeated
        defeated = False
        if hasattr(defender, "is_defeated") and defender.is_defeated():
            defeated = True
        elif hasattr(defender.db, "health") and defender.db.health <= 0:
            defeated = True
        elif hasattr(defender.db, "attributes") and defender.db.attributes.get("health") == 0:
            defeated = True

        # Attack messages
        attack_msg = f"You attack {defender.key} with {weapon_name} for {actual_damage} damage!"
        if defeated:
            attack_msg += f" {defender.key} has been defeated!"

        defender_msg = f"{attacker.key} attacks you with {weapon_name} for {actual_damage} damage!"
        if defeated:
            defender_msg += " You have been defeated!"

        room_msg = f"{attacker.key} attacks {defender.key} with {weapon_name}."

        # Send messages
        attacker.msg(attack_msg)
        defender.msg(defender_msg)
        attacker.location.msg_contents(room_msg, exclude=[attacker, defender])

        # Handle defeated opponent
        if defeated:
            self._handle_defeat(attacker, defender)

        # If the target is an NPC opponent, they counter-attack
        elif ("opponent" in str(defender.typeclass) or
              (hasattr(defender.db, "combat_style") and
               not (hasattr(defender, "is_defeated") and defender.is_defeated()))):
            # Wait a moment and then counter
            from evennia.utils import delay
            delay(1, self._counter_attack, defender, attacker)
            
    def _counter_attack(self, attacker, defender):
        """NPC counter-attack"""
        # Only attack if both are still in the same location and defender is alive
        is_defender_alive = True

        if hasattr(defender, "is_defeated"):
            is_defender_alive = not defender.is_defeated()
        elif hasattr(defender.db, "health") and defender.db.health <= 0:
            is_defender_alive = False
        elif hasattr(defender.db, "attributes") and defender.db.attributes.get("health") == 0:
            is_defender_alive = False

        if attacker.location != defender.location or not is_defender_alive:
            return

        # Roll attack using strength (for NPCs)
        import random
        hit_roll = random.randint(1, 20)

        # Get attacker's strength bonus if available
        if hasattr(attacker, "get_attribute"):
            strength = attacker.get_attribute("strength")
            attr_bonus = (strength - 10) // 2 if strength is not None else 0
        else:
            attr_bonus = 0

        hit_total = hit_roll + attr_bonus

        # Get defender's defense from attributes if available
        if hasattr(defender, "get_attribute"):
            defense = defender.get_attribute("defense")
            if defense is None:
                # If no specific defense stat, derive from dexterity
                dex = defender.get_attribute("dexterity")
                defense = (dex - 10) // 2 if dex is not None else 0
        else:
            # Fallback for defender without attributes
            defense = getattr(defender.db.combat, "defense", 0)

        # Minimum defense value
        defense = max(0, defense)

        # Check if attack hits (need to overcome defense + 10)
        defense_class = 10 + defense
        hit_success = hit_total >= defense_class

        if not hit_success:
            # Attack missed
            defender.msg(f"{attacker.key}'s counter-attack misses you!")
            attacker.msg(f"Your counter-attack misses {defender.key}!")
            attacker.location.msg_contents(
                f"{attacker.key} counter-attacks {defender.key} but misses.",
                exclude=[attacker, defender]
            )
            return

        # Calculate base damage
        if hasattr(attacker, "get_attribute"):
            strength = attacker.get_attribute("strength")
            base_damage = random.randint(1, 4) + ((strength - 10) // 2 if strength is not None else 0)
            base_damage = max(1, base_damage)  # Minimum 1 damage
        else:
            # Fallback for entities without attributes
            base_damage = getattr(attacker.db, "attack_power", 5)

        # Calculate damage reduction
        damage_reduction = 0
        if hasattr(defender, "get_attribute"):
            defense_attr = defender.get_attribute("defense")
            if defense_attr is not None:
                damage_reduction = defense_attr
        elif hasattr(defender.db.combat, "defense"):
            damage_reduction = defender.db.combat["defense"]

        # Calculate final damage
        damage = max(1, base_damage - damage_reduction)  # Minimum 1 damage

        # Apply damage to defender
        defender_defeated = False

        if hasattr(defender.db, "combat") and "health" in defender.db.combat:
            defender.db.combat["health"] -= damage
            if defender.db.combat["health"] <= 0:
                defender_defeated = True
        elif hasattr(defender, "at_damage"):
            defender.at_damage(damage)
            defender_defeated = defender.is_defeated() if hasattr(defender, "is_defeated") else False
        elif hasattr(defender.db, "attributes") and defender.db.attributes.get("health") is not None:
            current_health = defender.db.attributes.get("health")
            new_health = max(0, current_health - damage)
            defender.db.attributes.set("health", new_health)
            if new_health <= 0:
                defender_defeated = True
        else:
            # Fallback for entities without health tracking
            defender_defeated = damage >= 20  # Arbitrary threshold for entities without health

        # Attack messages
        attack_msg = f"{attacker.key} strikes back at you for {damage} damage!"
        if defender_defeated:
            attack_msg += " You have been defeated!"

        defender_msg = f"You strike back at {defender.key} for {damage} damage!"
        if defender_defeated:
            defender_msg += f" {defender.key} has been defeated!"

        room_msg = f"{attacker.key} counter-attacks {defender.key}."

        # Send messages
        defender.msg(attack_msg)
        attacker.msg(defender_msg)
        attacker.location.msg_contents(room_msg, exclude=[attacker, defender])

        # Handle player defeat if needed
        if defender_defeated:
            self._handle_player_defeat(defender, attacker)
            
    def _handle_defeat(self, victor, defeated):
        """Handle opponent defeat and rewards"""
        # Check for loot table
        if hasattr(defeated.db, "loot_table") and defeated.db.loot_table:
            loot_dropped = []
            
            # Roll for each possible loot item
            for item_name, drop_chance in defeated.db.loot_table.items():
                if random.random() < drop_chance:
                    # Spawn the item
                    from evennia.utils.spawner import spawn
                    try:
                        # Convert to upper case and replace spaces for prototype format
                        proto_key = item_name.upper().replace(" ", "_")
                        result = spawn(proto_key, prototype_modules=["world.prototypes"])
                        if result:
                            item = result[0]
                            item.location = victor.location
                            loot_dropped.append(item.key)
                    except Exception:
                        # Create a basic object if prototype fails
                        from typeclasses.objects import Object
                        item = Object.create(
                            key=item_name,
                            location=victor.location,
                            attributes={"desc": f"Loot dropped by {defeated.key}."}
                        )
                        loot_dropped.append(item_name)
            
            # Announce dropped loot
            if loot_dropped:
                loot_list = ", ".join(loot_dropped)
                victor.msg(f"{defeated.key} dropped: {loot_list}")
                victor.location.msg_contents(f"{defeated.key} dropped: {loot_list}", exclude=victor)
        
        # Remove the defeated opponent
        defeated.location = None
        
        # Track combat victory
        if not hasattr(victor.db, "combat_victories"):
            victor.db.combat_victories = {}
            
        opponent_type = defeated.key
        victor.db.combat_victories[opponent_type] = victor.db.combat_victories.get(opponent_type, 0) + 1
        
    def _handle_player_defeat(self, player, opponent):
        """Handle player defeat"""
        # Respawn at their home location
        home = player.home
        if not home:
            # Default to the Nexus if no home is set
            from evennia.utils.search import search_object
            matches = search_object("The Nexus Point")
            if matches:
                home = matches[0]
            
        if home:
            # Teleport player to home
            player.msg("You have been defeated! You are teleported back to safety.")
            player.location.msg_contents(f"{player.key} has been defeated and disappears!", exclude=player)
            player.move_to(home, quiet=True)
            player.location.msg_contents(f"{player.key} appears, looking wounded.", exclude=player)
            
            # Restore some health
            player.db.combat["health"] = max(20, player.db.combat["max_health"] // 2)
            player.msg("You've recovered some of your health, but not all of it.")
        else:
            # Just restore health if no home location
            player.db.combat["health"] = player.db.combat["max_health"]
            player.msg("You've been defeated, but somehow recover.")


class CmdStatus(Command):
    """
    Check your current health and combat status.

    Usage:
      status

    This command displays information about your current health,
    equipped weapons, active effects, and exploration statistics.

    Examples:
      status
    """

    key = "status"
    aliases = ["hp", "health"]
    help_category = "Wilderness"

    def func(self):
        """Implement the command"""
        caller = self.caller
        
        # Initialize combat attributes if needed
        if not hasattr(caller.db, "combat"):
            caller.db.combat = {
                "target": None,
                "weapon": None,
                "health": 100,
                "max_health": 100,
                "attack_power": 10,
                "defense": 5,
                "last_attack": None
            }
            
        combat = caller.db.combat
        
        # Initialize exploration stats if needed
        if not hasattr(caller.db, "explored_rooms"):
            caller.db.explored_rooms = {}
            
        explored_count = len(caller.db.explored_rooms)
        
        # Initialize victories if needed
        if not hasattr(caller.db, "combat_victories"):
            caller.db.combat_victories = {}
            
        victory_count = sum(caller.db.combat_victories.values())
        
        # Format the health bar
        health_percent = combat["health"] / combat["max_health"]
        bar_length = 20
        filled_length = int(bar_length * health_percent)
        health_bar = "|g" + "=" * filled_length + "|r" + "-" * (bar_length - filled_length) + "|n"
        
        # Create the status message
        status = [
            f"|wStatus for {caller.key}:|n",
            f"Health: {combat['health']}/{combat['max_health']} {health_bar}",
            f"Attack Power: {combat['attack_power']}",
            f"Defense: {combat['defense']}",
            ""
        ]
        
        # Add equipped weapon info
        weapon = combat["weapon"]
        if weapon:
            status.append(f"Equipped Weapon: {weapon.key}")
            if hasattr(weapon.db, "damage"):
                status.append(f"Weapon Damage: +{weapon.db.damage}")
        else:
            status.append("Equipped Weapon: None (Unarmed)")
            
        status.append("")
        
        # Add exploration stats
        status.append(f"Areas Explored: {explored_count}")
        status.append(f"Combat Victories: {victory_count}")
        
        # Add current target if any
        target = combat["target"]
        if target and target.location == caller.location:
            status.append("")
            status.append(f"Current Target: {target.key}")
            if hasattr(target.db, "health") and hasattr(target.db, "max_health"):
                target_percent = target.db.health / target.db.max_health
                target_filled = int(bar_length * target_percent)
                target_bar = "|g" + "=" * target_filled + "|r" + "-" * (bar_length - target_filled) + "|n"
                status.append(f"Target Health: {target_bar}")
            
        # Display the status
        caller.msg("\n".join(status))


class CmdMap(Command):
    """
    Display a map of explored areas.

    Usage:
      map

    This command shows a visual representation of the areas you've
    explored, with your current location highlighted. It helps with
    navigation and exploration tracking.

    Examples:
      map
    """

    key = "map"
    help_category = "Wilderness"

    def func(self):
        """Implement the command"""
        caller = self.caller
        
        # This is a simplified implementation that just lists explored areas
        # A true map system would require more data about room coordinates
        
        # Initialize exploration stats if needed
        if not hasattr(caller.db, "explored_rooms"):
            caller.db.explored_rooms = {}
            
        if not caller.db.explored_rooms:
            caller.msg("You haven't explored any areas yet.")
            return
            
        # Collect room data
        explored_rooms = []
        for room_id, exploration_count in caller.db.explored_rooms.items():
            # Try to get the room
            from evennia.utils.search import search_object_by_id
            matches = search_object_by_id(room_id)
            if matches:
                room = matches[0]
                explored_rooms.append({
                    "name": room.key,
                    "id": room.id,
                    "exploration_count": exploration_count,
                    "is_current": room == caller.location
                })
                
        # Sort by exploration count (most explored first)
        explored_rooms.sort(key=lambda r: r["exploration_count"], reverse=True)
        
        # Create the table
        table = EvTable("Area", "Explored", "Current", border="cells")
        
        for room in explored_rooms:
            current = "Yes" if room["is_current"] else ""
            table.add_row(
                room["name"],
                f"{room['exploration_count']} times",
                current
            )
            
        # Show the map
        caller.msg("|wExplored Areas:|n")
        caller.msg(table)


class WildernessCmdSet(CmdSet):
    """
    Cmdset for wilderness-related commands.
    """
    
    key = "wilderness_commands"
    
    def at_cmdset_creation(self):
        """
        Add the wilderness commands to the command set
        """
        self.add(CmdExplore())
        self.add(CmdAttack())
        self.add(CmdStatus())
        self.add(CmdMap())