"""
Lore (EXPLAIN) Commands

This module contains commands for the EXPLAIN/Lore Halls area of the Pythonic MUD.
These commands enable players to interact with NPCs, acquire knowledge,
and engage in dialogue systems.

"""
from evennia.commands.command import Command
from evennia.utils.evtable import EvTable
from evennia import CmdSet


class CmdTalk(Command):
    """
    Start or continue a conversation with an NPC.

    Usage:
      talk <npc>
      talk <npc> about <topic>

    This command allows you to engage in dialogue with non-player
    characters. With no topic specified, the NPC will greet you
    or continue your existing conversation.

    Specifying a topic directs the conversation to that subject,
    if the NPC has knowledge about it.

    Examples:
      talk professor
      talk archivist about history
      talk mentor about python
    """

    key = "talk"
    aliases = ["speak", "converse"]
    help_category = "Lore"

    def func(self):
        """Implement the command"""
        caller = self.caller

        if not self.args:
            caller.msg("Who do you want to talk to?")
            return

        # Check for 'about' to separate npc and topic
        if " about " in self.args:
            npc_name, topic = self.args.split(" about ", 1)
            npc_name = npc_name.strip()
            topic = topic.strip().lower()
        else:
            npc_name = self.args.strip()
            topic = "greeting"  # Default topic is greeting

        # Look for the NPC in the room
        npc = caller.search(npc_name)
        if not npc:
            return

        # Check if this is actually an NPC
        if not hasattr(npc, 'db') or not npc.db.dialogue_tree:
            caller.msg(f"{npc.key} doesn't seem interested in talking.")
            return

        # Track conversation with this NPC
        if not hasattr(caller.db, "conversations"):
            caller.db.conversations = {}
        
        if npc.id not in caller.db.conversations:
            caller.db.conversations[npc.id] = {
                "npc": npc,
                "current_topic": None,
                "topics_discussed": set(),
                "last_topic": None
            }
        
        conv = caller.db.conversations[npc.id]
        
        # Get the dialogue from the NPC for this topic
        dialogue_tree = npc.db.dialogue_tree
        if topic in dialogue_tree:
            response = dialogue_tree[topic]
            conv["current_topic"] = topic
            conv["topics_discussed"].add(topic)
            conv["last_topic"] = topic
            
            # Format the response with available topics
            related_topics = self._get_related_topics(npc, topic, conv["topics_discussed"])
            
            # Send the NPC's response
            caller.msg(f"|g{npc.key} says:|n \"{response}\"")
            
            # If there are related topics, suggest them
            if related_topics:
                topic_list = ", ".join(related_topics)
                caller.msg(f"\nYou could ask about: {topic_list}")
        else:
            # Topic not found
            caller.msg(f"{npc.key} doesn't seem to know about '{topic}'.")
            
            # Suggest some topics they do know about
            known_topics = [t for t in dialogue_tree.keys() if t != "greeting"]
            if known_topics:
                sample_topics = known_topics[:3] if len(known_topics) > 3 else known_topics
                topic_list = ", ".join(sample_topics)
                caller.msg(f"You could try asking about: {topic_list}")

    def _get_related_topics(self, npc, topic, discussed_topics):
        """
        Get a list of related topics that the player can ask about next.
        This helps guide the conversation.
        """
        related = []
        
        # Simple implementation - just suggest other topics in the dialogue tree
        # that haven't been discussed yet
        if hasattr(npc, 'db') and npc.db.dialogue_tree:
            # Get topics that aren't 'greeting' and haven't been discussed
            available_topics = [t for t in npc.db.dialogue_tree.keys() 
                               if t != "greeting" and t != topic]
            
            # Prioritize topics that haven't been discussed
            for t in available_topics:
                if t not in discussed_topics:
                    related.append(t)
                    
            # If we have less than 3 related topics, add some that were discussed
            if len(related) < 3:
                for t in available_topics:
                    if t in discussed_topics and len(related) < 3:
                        related.append(t)
        
        return related


class CmdLearn(Command):
    """
    Learn specific knowledge from an NPC or object.

    Usage:
      learn <topic> from <npc/object>
      learn from <npc/object>

    This command allows you to acquire in-depth knowledge on a
    specific topic from NPCs or knowledge items like books.

    With no topic specified, it will show what topics you can
    learn from the source.

    Examples:
      learn python from professor
      learn history from ancient tome
      learn from archivist
    """

    key = "learn"
    aliases = ["study"]
    help_category = "Lore"

    def func(self):
        """Implement the command"""
        caller = self.caller

        if not self.args:
            caller.msg("Learn what? Specify a topic and a source.")
            return

        # Check for 'from' to separate topic and source
        if " from " in self.args:
            topic, source_name = self.args.split(" from ", 1)
            topic = topic.strip().lower()
            source_name = source_name.strip()
            
            # Empty topic means list available topics
            if not topic:
                topic = None
        else:
            # No 'from' means just a source was specified
            source_name = self.args.strip()
            topic = None

        # Look for the source in the room or inventory
        source = caller.search(source_name, location=[caller.location, caller])
        if not source:
            return

        # Check if this is a valid knowledge source
        is_npc = hasattr(source, 'db') and source.db.dialogue_tree
        is_knowledge_item = hasattr(source, 'db') and source.db.knowledge_topics
        
        if not (is_npc or is_knowledge_item):
            caller.msg(f"You can't learn anything from {source.key}.")
            return

        # Track knowledge acquisition
        if not hasattr(caller.db, "knowledge"):
            caller.db.knowledge = {}
        
        # If no topic specified, list available topics
        if topic is None:
            available_topics = []
            
            if is_npc and source.db.knowledge:
                available_topics = list(source.db.knowledge.keys())
            elif is_knowledge_item and source.db.knowledge_topics:
                available_topics = source.db.knowledge_topics
            
            if available_topics:
                topic_list = ", ".join(available_topics)
                caller.msg(f"Topics you can learn from {source.key}: {topic_list}")
            else:
                caller.msg(f"{source.key} doesn't seem to have any specific knowledge to share.")
            return
        
        # Learn the requested topic
        knowledge_gained = False
        
        if is_npc and source.db.knowledge and topic in source.db.knowledge:
            knowledge_level = source.db.knowledge[topic]
            
            # Add or update knowledge
            current_level = caller.db.knowledge.get(topic, 0)
            if knowledge_level > current_level:
                caller.db.knowledge[topic] = knowledge_level
                knowledge_gained = True
                
                # Find something from dialogue tree related to this topic
                related_dialogue = None
                for dialogue_topic, text in source.db.dialogue_tree.items():
                    if topic in dialogue_topic:
                        related_dialogue = text
                        break
                
                if related_dialogue:
                    caller.msg(f"|g{source.key} teaches you about {topic}:|n \"{related_dialogue}\"")
                else:
                    caller.msg(f"|g{source.key} teaches you about {topic}.|n Your knowledge level is now {knowledge_level}.")
            else:
                caller.msg(f"You already know as much about {topic} as {source.key} can teach you.")
                
        elif is_knowledge_item and source.db.knowledge_topics and topic in source.db.knowledge_topics:
            # Knowledge items always grant level 1 knowledge
            current_level = caller.db.knowledge.get(topic, 0)
            if current_level < 1:
                caller.db.knowledge[topic] = 1
                knowledge_gained = True
                
                # Get content if available
                if source.db.content:
                    caller.msg(f"|gYou learn about {topic} from {source.key}:|n\n{source.db.content}")
                else:
                    caller.msg(f"|gYou learn about {topic} from {source.key}.|n")
                
                # Mark as read
                if not source.db.read_by:
                    source.db.read_by = set()
                source.db.read_by.add(caller)
            else:
                caller.msg(f"You've already learned about {topic} from {source.key}.")
        else:
            caller.msg(f"{source.key} doesn't seem to know about '{topic}'.")
            
        # If knowledge was gained, update the location
        if knowledge_gained and hasattr(caller.location, 'db') and caller.location.db.area_type == "lore":
            if not caller in caller.location.db.visitors_learned:
                caller.location.db.visitors_learned = set()
            caller.location.db.visitors_learned.add(caller)


class CmdQuest(Command):
    """
    Get or check quests from NPCs.

    Usage:
      quest <npc>
      quest/list
      quest/complete <quest name> with <npc>

    This command allows you to get quests from NPCs, check your
    current quests, or complete quests by turning in items or
    reporting back to the quest giver.

    Switches:
      list - Show all your current quests and their status
      complete - Complete a quest with a specific NPC

    Examples:
      quest professor
      quest/list
      quest/complete data recovery with archivist
    """

    key = "quest"
    aliases = ["mission", "task"]
    help_category = "Lore"

    def func(self):
        """Implement the command"""
        caller = self.caller

        # Initialize quest tracker if needed
        if not hasattr(caller.db, "quests"):
            caller.db.quests = {
                "active": {},
                "completed": set()
            }
        
        # Handle quest list
        if 'list' in self.switches:
            self._list_quests(caller)
            return
            
        # Handle quest completion
        if 'complete' in self.switches:
            if not self.args or " with " not in self.args:
                caller.msg("Usage: quest/complete <quest name> with <npc>")
                return
                
            quest_name, npc_name = self.args.split(" with ", 1)
            quest_name = quest_name.strip().lower()
            npc_name = npc_name.strip()
            
            self._complete_quest(caller, quest_name, npc_name)
            return
        
        # Handle quest request from NPC
        if not self.args:
            caller.msg("Who do you want to get a quest from?")
            return
            
        npc_name = self.args.strip()
        npc = caller.search(npc_name)
        if not npc:
            return
            
        # Check if this is an NPC with quests
        if not hasattr(npc, 'db') or "provide quests" not in npc.db.services:
            caller.msg(f"{npc.key} doesn't seem to have any quests for you.")
            return
            
        # Get available quests from this NPC
        self._get_quests(caller, npc)

    def _list_quests(self, caller):
        """List all of the caller's current quests"""
        quests = caller.db.quests
        
        if not quests["active"] and not quests["completed"]:
            caller.msg("You don't have any quests at the moment.")
            return
            
        # Show active quests
        if quests["active"]:
            table = EvTable("Quest", "Description", "From", border="cells")
            for quest_name, quest_data in quests["active"].items():
                table.add_row(
                    quest_name,
                    quest_data.get("description", "No description"),
                    quest_data.get("giver_name", "Unknown")
                )
                
            caller.msg("|gActive Quests:|n")
            caller.msg(table)
        else:
            caller.msg("You don't have any active quests.")
            
        # Show completed quests if any
        if quests["completed"]:
            caller.msg(f"\n|gCompleted Quests:|n {', '.join(quests['completed'])}")

    def _get_quests(self, caller, npc):
        """Get available quests from an NPC"""
        # For this simple implementation, NPCs only offer one quest
        # In a more complex system, we would have multiple quests with requirements
        
        # Check if the NPC has a quest attribute
        if not hasattr(npc.db, "quest"):
            caller.msg(f"{npc.key} doesn't have any quests for you right now.")
            return
            
        quest_data = npc.db.quest
        quest_name = quest_data.get("name", "Unnamed Quest")
        
        # Check if player already has this quest
        if quest_name.lower() in caller.db.quests["active"]:
            caller.msg(f"You're already working on '{quest_name}' for {npc.key}.")
            
            # Repeat the quest details
            description = quest_data.get("description", "No description available.")
            caller.msg(f"\n{description}")
            return
            
        # Check if player already completed this quest
        if quest_name.lower() in caller.db.quests["completed"]:
            caller.msg(f"You've already completed '{quest_name}' for {npc.key}.")
            return
            
        # Offer the quest
        description = quest_data.get("description", "No description available.")
        
        caller.msg(f"|g{npc.key} offers you a quest:|n '{quest_name}'")
        caller.msg(f"\n{description}")
        
        # Automatically accept the quest for simplicity
        # In a more complex system, we would have a quest acceptance mechanism
        caller.db.quests["active"][quest_name.lower()] = {
            "name": quest_name,
            "description": description,
            "giver": npc,
            "giver_name": npc.key,
            "requirements": quest_data.get("requirements", {}),
            "reward": quest_data.get("reward", {})
        }
        
        caller.msg("\nYou've accepted this quest. Use 'quest/list' to review your quests.")

    def _complete_quest(self, caller, quest_name, npc_name):
        """Attempt to complete a quest with an NPC"""
        # Look for the NPC
        npc = caller.search(npc_name)
        if not npc:
            return
            
        # Check if this quest exists and is active
        quests = caller.db.quests
        if quest_name not in quests["active"]:
            caller.msg(f"You don't have an active quest called '{quest_name}'.")
            return
            
        quest_data = quests["active"][quest_name]
        
        # Check if this is the right NPC to complete with
        if quest_data["giver_name"].lower() != npc.key.lower():
            caller.msg(f"You need to complete this quest with {quest_data['giver_name']}, not {npc.key}.")
            return
            
        # Check requirements (simplified)
        # In a real system, we would check inventory for items, etc.
        requirements_met = True
        required_items = quest_data.get("requirements", {}).get("items", [])
        
        if required_items:
            # Check inventory for required items
            inventory_items = [obj.key.lower() for obj in caller.contents]
            
            for item_name in required_items:
                if item_name.lower() not in inventory_items:
                    requirements_met = False
                    caller.msg(f"You need to have '{item_name}' to complete this quest.")
                    break
                    
        if not requirements_met:
            return
            
        # Complete the quest
        caller.msg(f"|gYou've completed the quest '{quest_data['name']}'!|n")
        
        # Move from active to completed
        del quests["active"][quest_name]
        quests["completed"].add(quest_name)
        
        # Grant rewards (simplified)
        # In a real system, we would spawn items, grant experience, etc.
        reward_text = quest_data.get("reward", {}).get("description", "")
        if reward_text:
            caller.msg(f"\nReward: {reward_text}")
            
        # Try to give a physical reward if specified
        reward_item = quest_data.get("reward", {}).get("item")
        if reward_item:
            from evennia.utils.spawner import spawn
            try:
                # Try to spawn the reward item
                proto_key = reward_item.upper().replace(" ", "_")
                result = spawn(proto_key, prototype_modules=["world.prototypes"])
                if result:
                    item = result[0]
                    item.location = caller
                    caller.msg(f"You received {item.key}!")
                else:
                    # Fallback to a basic object
                    from typeclasses.objects import Object
                    item = Object.create(
                        key=reward_item,
                        location=caller,
                        attributes={
                            "desc": f"A reward for completing the '{quest_data['name']}' quest."
                        }
                    )
                    caller.msg(f"You received {item.key}!")
            except Exception:
                caller.msg("There was a problem with your reward. Please report this to an admin.")


class CmdNPCs(Command):
    """
    List all NPCs in the current area.

    Usage:
      npcs

    This command shows all NPCs in your current location,
    along with their current mood and available services.

    Examples:
      npcs
    """

    key = "npcs"
    aliases = ["list npcs"]
    help_category = "Lore"

    def func(self):
        """Implement the command"""
        caller = self.caller
        location = caller.location

        # Find all NPCs in the current location
        npcs = []
        for obj in location.contents:
            if hasattr(obj, 'db') and obj.db.dialogue_tree:
                npcs.append(obj)

        if not npcs:
            caller.msg("There are no NPCs in this area.")
            return

        # Display the NPCs in a table
        table = EvTable("NPC", "Mood", "Services", border="cells")
        
        for npc in npcs:
            # Get mood
            mood = npc.db.mood if hasattr(npc.db, "mood") else "neutral"
            
            # Get services
            services = npc.db.services if hasattr(npc.db, "services") else []
            services_str = ", ".join(services) if services else "none"
            
            table.add_row(npc.key, mood, services_str)

        caller.msg("|gNPCs in this area:|n")
        caller.msg(table)


class LoreCmdSet(CmdSet):
    """
    Cmdset for lore-related commands.
    """
    
    key = "lore_commands"
    
    def at_cmdset_creation(self):
        """
        Add the lore commands to the command set
        """
        self.add(CmdTalk())
        self.add(CmdLearn())
        self.add(CmdQuest())
        self.add(CmdNPCs())