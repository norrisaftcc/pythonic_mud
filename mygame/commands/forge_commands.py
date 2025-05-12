"""
Forge (CREATE) Commands

This module contains commands for the CREATE/Forge area of the Pythonic MUD.
These commands enable the crafting system, allowing players to gather materials,
inspect workbenches, and craft items.

"""
from evennia.commands.command import Command
from evennia.utils.utils import list_to_string
from evennia.utils.evtable import EvTable
from evennia.utils.search import search_tag
from evennia import CmdSet


class CmdCraft(Command):
    """
    Create an item by combining materials at a workbench.

    Usage:
      craft <item name>
      craft/list
      craft/recipes
      craft/info <recipe name>

    Crafting requires:
    1. Being in the same location as a workbench
    2. Having the necessary materials in your inventory
    3. The recipe being available at that workbench

    Switches:
      list - Show all items you can currently craft
      recipes - Show all recipes available at this workbench
      info - Show detailed info about a specific recipe

    Examples:
      craft sword
      craft/list
      craft/recipes
      craft/info shield
    """

    key = "craft"
    aliases = ["make"]
    help_category = "Forge"

    def func(self):
        """Implement the command"""
        caller = self.caller

        # First check if the caller is at a workbench
        workbench = None
        for obj in caller.location.contents:
            if hasattr(obj, 'db') and obj.db.workbench_type:
                workbench = obj
                break

        if not workbench:
            caller.msg("You need to be at a workbench to craft items.")
            return

        # Handle the different switches
        if 'list' in self.switches:
            # List what the player can craft with current inventory
            self._list_craftable_items(caller, workbench)
            return
        elif 'recipes' in self.switches:
            # List all recipes available at this workbench
            self._list_all_recipes(caller, workbench)
            return
        elif 'info' in self.switches:
            # Show detailed info about a specific recipe
            if not self.args:
                caller.msg("You must specify a recipe to get information about.")
                return
            self._show_recipe_info(caller, workbench, self.args)
            return

        # If no switches, attempt to craft the specified item
        if not self.args:
            caller.msg("What do you want to craft? (Use craft/recipes to see available recipes)")
            return

        recipe_name = self.args.strip().lower()
        self._craft_item(caller, workbench, recipe_name)

    def _list_all_recipes(self, caller, workbench):
        """List all recipes available at this workbench"""
        recipes = workbench.db.crafting_recipes
        if not recipes:
            caller.msg(f"There are no recipes available at this {workbench.key}.")
            return

        table = EvTable("Recipe", "Materials Required", border="cells")
        for recipe, materials in recipes.items():
            table.add_row(recipe, list_to_string(materials))

        caller.msg(f"|gRecipes available at the {workbench.key}:|n")
        caller.msg(table)

    def _list_craftable_items(self, caller, workbench):
        """List what the player can craft with current inventory"""
        recipes = workbench.db.crafting_recipes
        if not recipes:
            caller.msg(f"There are no recipes available at this {workbench.key}.")
            return

        inventory = [obj.key.lower() for obj in caller.contents]
        craftable = []

        for recipe, materials in recipes.items():
            can_craft = True
            material_count = {}

            # Count required materials
            for material in materials:
                if material in material_count:
                    material_count[material] += 1
                else:
                    material_count[material] = 1

            # Count inventory materials
            inventory_count = {}
            for item in inventory:
                if item in inventory_count:
                    inventory_count[item] += 1
                else:
                    inventory_count[item] = 1

            # Check if player has enough materials
            for material, count in material_count.items():
                if material not in inventory_count or inventory_count[material] < count:
                    can_craft = False
                    break

            if can_craft:
                craftable.append(recipe)

        if not craftable:
            caller.msg("You don't have the materials to craft anything at the moment.")
            return

        table = EvTable("Craftable Items", border="cells")
        for item in craftable:
            table.add_row(item)

        caller.msg("|gItems you can craft with your current materials:|n")
        caller.msg(table)

    def _show_recipe_info(self, caller, workbench, recipe_name):
        """Show detailed info about a specific recipe"""
        recipes = workbench.db.crafting_recipes
        recipe_name = recipe_name.lower().strip()

        if recipe_name not in recipes:
            caller.msg(f"There is no recipe for '{recipe_name}' at this {workbench.key}.")
            return

        materials = recipes[recipe_name]
        material_count = {}

        # Count required materials
        for material in materials:
            if material in material_count:
                material_count[material] += 1
            else:
                material_count[material] = 1

        table = EvTable("Material", "Quantity", border="cells")
        for material, count in material_count.items():
            table.add_row(material, count)

        caller.msg(f"|gRecipe details for '{recipe_name}':|n")
        caller.msg(table)

    def _craft_item(self, caller, workbench, recipe_name):
        """Attempt to craft the specified item"""
        recipes = workbench.db.crafting_recipes
        if recipe_name not in recipes:
            caller.msg(f"There is no recipe for '{recipe_name}' at this {workbench.key}.")
            return

        materials_needed = recipes[recipe_name]
        materials_count = {}

        # Count required materials
        for material in materials_needed:
            if material in materials_count:
                materials_count[material] += 1
            else:
                materials_count[material] = 1

        # Check if player has all required materials
        materials_found = {}
        material_objects = {}

        for obj in caller.contents:
            obj_key = obj.key.lower()
            if obj_key in materials_count:
                if obj_key not in materials_found:
                    materials_found[obj_key] = 1
                    material_objects[obj_key] = [obj]
                else:
                    materials_found[obj_key] += 1
                    material_objects[obj_key].append(obj)

        missing = []
        for material, count in materials_count.items():
            if material not in materials_found:
                missing.append(f"{material} (need {count})")
            elif materials_found[material] < count:
                missing.append(f"{material} (have {materials_found[material]}, need {count})")

        if missing:
            caller.msg(f"You're missing: {', '.join(missing)}.")
            return

        # Consume materials
        for material, count in materials_count.items():
            for i in range(count):
                obj = material_objects[material][i]
                obj.delete()

        # Create the crafted item
        from evennia.utils.spawner import spawn
        from random import randint
        
        # Try to find an appropriate prototype for the crafted item
        # First, build the prototype key from the recipe name
        proto_key = recipe_name.upper().replace(" ", "_")
        
        # Default attributes for a crafted item
        crafted_attrs = {
            "key": recipe_name,
            "desc": f"A {recipe_name} crafted at a {workbench.db.workbench_type}.",
            "quality": randint(1, 5),  # Random quality based on skill (future enhancement)
            "creator": caller.name
        }
        
        # Now try to spawn the item, either from prototype or from scratch
        try:
            # Look for a matching prototype in the prototypes module
            result = spawn(proto_key, prototype_modules=["world.prototypes"])
            if result:
                crafted_item = result[0]
                # Update with creator info
                crafted_item.db.creator = caller.name
            else:
                # No prototype found, create a basic object
                from typeclasses.themed_objects import CraftingObject
                crafted_item = CraftingObject.create(
                    key=recipe_name,
                    location=caller,
                    attributes=crafted_attrs
                )
        except Exception as e:
            # If error with prototype, create basic object
            from typeclasses.themed_objects import CraftingObject
            crafted_item = CraftingObject.create(
                key=recipe_name,
                location=caller,
                attributes=crafted_attrs
            )
        
        # Success message
        caller.msg(f"You successfully craft a {recipe_name}!")
        caller.location.msg_contents(f"{caller.name} crafts a {recipe_name} at the {workbench.key}.", exclude=caller)


class CmdGather(Command):
    """
    Gather crafting materials from your surroundings.

    Usage:
      gather
      gather <material name>

    This command allows you to gather available crafting materials
    from your current location, if any are present.

    With no arguments, it will show all materials available to gather.
    With a specific material name, it will attempt to gather that material.

    Examples:
      gather
      gather metal ore
    """

    key = "gather"
    aliases = ["collect", "harvest"]
    help_category = "Forge"

    def func(self):
        """Implement the command"""
        caller = self.caller
        location = caller.location

        # Check if this room has resources to gather
        if not hasattr(location, 'db') or not location.db.available_resources:
            caller.msg("There are no materials to gather in this area.")
            return

        resources = location.db.available_resources

        # If no arguments, list available resources
        if not self.args:
            if not resources:
                caller.msg("There are no materials to gather in this area.")
                return

            table = EvTable("Available Materials", border="cells")
            for resource in resources:
                table.add_row(resource)

            caller.msg("|gMaterials available to gather:|n")
            caller.msg(table)
            return

        # Try to gather the specified resource
        resource_name = self.args.strip().lower()
        if resource_name not in resources:
            caller.msg(f"There is no '{resource_name}' to gather here.")
            return

        # Get resource details
        resource_data = resources[resource_name]
        quantity = resource_data.get("quantity", 1)
        
        if quantity <= 0:
            caller.msg(f"There is no more {resource_name} left to gather here.")
            return

        # Create the gathered material
        from evennia.utils.spawner import spawn
        
        # Try to find an appropriate prototype for the material
        proto_key = resource_name.upper().replace(" ", "_")
        
        try:
            # Look for a matching prototype
            result = spawn(proto_key, prototype_modules=["world.prototypes"])
            if result:
                material = result[0]
                material.location = caller
            else:
                # No prototype found, create a basic object
                from typeclasses.themed_objects import CraftingObject
                material = CraftingObject.create(
                    key=resource_name,
                    location=caller,
                    attributes={
                        "desc": f"A gathered {resource_name}, useful for crafting.",
                        "material_type": resource_name
                    }
                )
        except Exception as e:
            # If error with prototype, create basic object
            from typeclasses.themed_objects import CraftingObject
            material = CraftingObject.create(
                key=resource_name,
                location=caller,
                attributes={
                    "desc": f"A gathered {resource_name}, useful for crafting.",
                    "material_type": resource_name
                }
            )
        
        # Decrease the available quantity
        resources[resource_name]["quantity"] -= 1
        if resources[resource_name]["quantity"] <= 0:
            del resources[resource_name]
        
        # Success message
        caller.msg(f"You gather some {resource_name}.")
        caller.location.msg_contents(f"{caller.name} gathers some {resource_name}.", exclude=caller)


class CmdInspect(Command):
    """
    Examine an object in detail to learn about its properties.

    Usage:
      inspect <object>

    This command allows you to carefully examine an object to
    discover its properties, quality, and other attributes.
    It's especially useful for crafting materials and items.

    Examples:
      inspect sword
      inspect metal ingot
    """

    key = "inspect"
    aliases = ["examine"]
    help_category = "Forge"

    def func(self):
        """Implement the command"""
        caller = self.caller

        if not self.args:
            caller.msg("What do you want to inspect?")
            return

        target = caller.search(self.args)
        if not target:
            return

        # Basic properties all objects should have
        name = target.key
        desc = target.db.desc if target.db.desc else "No description."

        # Start building the inspection message
        message = [f"|gInspection of {name}:|n"]
        message.append(f"Description: {desc}")

        # Check for crafting-related attributes
        if hasattr(target, 'db'):
            # Material type
            if target.db.material_type:
                message.append(f"Material: {target.db.material_type}")
            
            # Quality
            if target.db.quality:
                quality_levels = {
                    1: "Poor",
                    2: "Common",
                    3: "Good",
                    4: "Excellent",
                    5: "Masterwork"
                }
                quality = quality_levels.get(target.db.quality, str(target.db.quality))
                message.append(f"Quality: {quality}")
            
            # Durability
            if target.db.durability:
                message.append(f"Durability: {target.db.durability}%")
            
            # Creator
            if target.db.creator:
                message.append(f"Created by: {target.db.creator}")
            
            # For workbenches, show what they can craft
            if target.db.workbench_type:
                message.append(f"Workbench Type: {target.db.workbench_type}")
                if target.db.crafting_recipes:
                    recipes = list(target.db.crafting_recipes.keys())
                    message.append(f"Available Recipes: {', '.join(recipes)}")
                else:
                    message.append("This workbench has no recipes available.")

        # Send the full inspection results
        caller.msg("\n".join(message))


class ForgeCmdSet(CmdSet):
    """
    Cmdset for forge-related commands.
    """
    
    key = "forge_commands"
    
    def at_cmdset_creation(self):
        """
        Add the forge commands to the command set
        """
        self.add(CmdCraft())
        self.add(CmdGather())
        self.add(CmdInspect())