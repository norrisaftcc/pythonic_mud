"""
Prototypes

A prototype is a simple way to create individualized instances of a
given typeclass. It is dictionary with specific key names.

For example, you might have a Sword typeclass that implements everything a
Sword would need to do. The only difference between different individual Swords
would be their key, description and some Attributes. The Prototype system
allows to create a range of such Swords with only minor variations. Prototypes
can also inherit and combine together to form entire hierarchies (such as
giving all Sabres and all Broadswords some common properties). Note that bigger
variations, such as custom commands or functionality belong in a hierarchy of
typeclasses instead.

A prototype can either be a dictionary placed into a global variable in a
python module (a 'module-prototype') or stored in the database as a dict on a
special Script (a db-prototype). The former can be created just by adding dicts
to modules Evennia looks at for prototypes, the latter is easiest created
in-game via the `olc` command/menu.

Prototypes are read and used to create new objects with the `spawn` command
or directly via `evennia.spawn` or the full path `evennia.prototypes.spawner.spawn`.

A prototype dictionary have the following keywords:

Possible keywords are:
- `prototype_key` - the name of the prototype. This is required for db-prototypes,
  for module-prototypes, the global variable name of the dict is used instead
- `prototype_parent` - string pointing to parent prototype if any. Prototype inherits
  in a similar way as classes, with children overriding values in their parents.
- `key` - string, the main object identifier.
- `typeclass` - string, if not set, will use `settings.BASE_OBJECT_TYPECLASS`.
- `location` - this should be a valid object or #dbref.
- `home` - valid object or #dbref.
- `destination` - only valid for exits (object or #dbref).
- `permissions` - string or list of permission strings.
- `locks` - a lock-string to use for the spawned object.
- `aliases` - string or list of strings.
- `attrs` - Attributes, expressed as a list of tuples on the form `(attrname, value)`,
  `(attrname, value, category)`, or `(attrname, value, category, locks)`. If using one
   of the shorter forms, defaults are used for the rest.
- `tags` - Tags, as a list of tuples `(tag,)`, `(tag, category)` or `(tag, category, data)`.
-  Any other keywords are interpreted as Attributes with no category or lock.
   These will internally be added to `attrs` (equivalent to `(attrname, value)`.

See the `spawn` command and `evennia.prototypes.spawner.spawn` for more info.

"""

# ==============================================================================
# BASIC CRAFTING MATERIALS - The Forge (CREATE area)
# ==============================================================================

CRAFTING_MATERIAL_BASE = {
    "typeclass": "typeclasses.themed_objects.CraftingObject",
    "key": "base material",
    "desc": "A basic crafting material.",
    "attrs": [
        ("material_type", "base"),
        ("durability", 100),
        ("quality", 1)
    ],
    "tags": [("material", "forge"), ("craftable", "forge")]
}

METAL_INGOT = {
    "prototype_parent": "CRAFTING_MATERIAL_BASE",
    "key": "metal ingot",
    "desc": "A solid bar of refined metal, perfect for crafting weapons and tools.",
    "attrs": [
        ("material_type", "metal"),
        ("quality", 3),
        ("required_tools", ["hammer", "tongs"])
    ]
}

CODE_FRAGMENT = {
    "prototype_parent": "CRAFTING_MATERIAL_BASE",
    "key": "code fragment",
    "desc": "A shimmering fragment of crystallized code that can be incorporated into digital constructs.",
    "attrs": [
        ("material_type", "data"),
        ("quality", 2),
        ("required_tools", ["code editor"])
    ]
}

POWER_CRYSTAL = {
    "prototype_parent": "CRAFTING_MATERIAL_BASE",
    "key": "power crystal", 
    "desc": "A glowing crystal that pulses with energy, useful for powering magical devices.",
    "attrs": [
        ("material_type", "crystal"),
        ("quality", 4),
        ("required_tools", ["crystal tuner"])
    ]
}

# ==============================================================================
# WORKBENCHES - The Forge (CREATE area)
# ==============================================================================

WORKBENCH_BASE = {
    "typeclass": "typeclasses.themed_objects.Workbench",
    "key": "workbench",
    "desc": "A sturdy workbench for crafting items.",
    "locks": "get:false();puppet:false()",
    "attrs": [
        ("workbench_type", "basic"),
        ("crafting_recipes", {"basic tool": ["metal ingot", "wood plank"]}),
    ],
    "tags": [("crafting", "forge"), ("interactive", "forge")]
}

FORGE_WORKBENCH = {
    "prototype_parent": "WORKBENCH_BASE",
    "key": "forge",
    "desc": "A blazing forge with an anvil for metalworking. The heat is intense but carefully controlled.",
    "attrs": [
        ("workbench_type", "forge"),
        ("crafting_recipes", {
            "sword": ["metal ingot", "metal ingot", "wood plank"],
            "shield": ["metal ingot", "metal ingot", "leather strap"]
        }),
    ]
}

CODE_WORKBENCH = {
    "prototype_parent": "WORKBENCH_BASE",
    "key": "code compiler",
    "desc": "A holographic terminal that allows assembly of code fragments into functional programs.",
    "attrs": [
        ("workbench_type", "compiler"),
        ("crafting_recipes", {
            "simple script": ["code fragment", "logic module"],
            "automation tool": ["code fragment", "code fragment", "power crystal"]
        }),
    ]
}

# ==============================================================================
# KNOWLEDGE ITEMS - The Lore Halls (EXPLAIN area)
# ==============================================================================

KNOWLEDGE_ITEM_BASE = {
    "typeclass": "typeclasses.themed_objects.LoreObject",
    "key": "knowledge item",
    "desc": "A source of information and lore.",
    "attrs": [
        ("readable", True),
        ("knowledge_topics", [])
    ],
    "tags": [("knowledge", "lore"), ("readable", "lore")]
}

ANCIENT_TOME = {
    "prototype_parent": "KNOWLEDGE_ITEM_BASE",
    "key": "ancient tome",
    "desc": "A weathered book bound in mysterious material, containing forgotten knowledge.",
    "attrs": [
        ("knowledge_topics", ["history", "magic", "forgotten realms"]),
        ("content", "The ancient civilizations of the digital realm were far more advanced than many realize today. Their understanding of the fundamental code structures allowed them to manipulate reality in ways we can only dream of...")
    ]
}

DIGITAL_LEXICON = {
    "prototype_parent": "KNOWLEDGE_ITEM_BASE",
    "key": "digital lexicon",
    "desc": "A hovering crystal that projects definitions and explanations when activated.",
    "attrs": [
        ("knowledge_topics", ["programming", "system architecture", "algorithms"]),
        ("content", "Basic Algorithms: 1. Sorting - Methods to arrange data in a specific order. 2. Searching - Techniques to find data within a collection. 3. Graph Traversal - Ways to visit every node in a graph structure...")
    ]
}

# ==============================================================================
# NPCs - The Lore Halls (EXPLAIN area)
# ==============================================================================

NPC_BASE = {
    "typeclass": "typeclasses.themed_objects.NPC",
    "key": "npc",
    "desc": "A non-player character you can interact with.",
    "locks": "get:false();puppet:false()",
    "attrs": [
        ("mood", "neutral"),
        ("dialogue_tree", {"greeting": "Hello there, traveler."})
    ],
    "tags": [("npc", "lore"), ("interactive", "lore")]
}

MENTOR_NPC = {
    "prototype_parent": "NPC_BASE",
    "key": "Professor Bytecode",
    "desc": "An experienced-looking figure with glowing lines of code running across their robes. They regard you with a patient, knowing expression.",
    "attrs": [
        ("mood", "helpful"),
        ("dialogue_tree", {
            "greeting": "Welcome, student. I'm Professor Bytecode. What aspect of coding would you like to learn about today?",
            "python": "Python is a versatile language that values readability and simplicity. Perfect for beginners and experts alike!",
            "algorithms": "Algorithms are the heart of efficient programming. Understanding them will greatly enhance your coding abilities.",
            "advice": "Remember: Always comment your code, use meaningful variable names, and test regularly. Future you will thank present you!"
        }),
        ("knowledge", {"programming": 10, "history": 7, "algorithms": 9}),
        ("services", ["teach", "evaluate code", "provide quests"])
    ]
}

QUEST_GIVER_NPC = {
    "prototype_parent": "NPC_BASE",
    "key": "Archivist Echo",
    "desc": "A shimmering, translucent figure that seems to be made of pure data. Multiple screens hover around them, displaying various information streams.",
    "attrs": [
        ("mood", "busy"),
        ("dialogue_tree", {
            "greeting": "Oh! A visitor. I am Archivist Echo, keeper of digital histories. Are you here to help with my research?",
            "research": "I'm studying the patterns of code evolution across the digital realms. So fascinating how algorithms adapt!",
            "help": "If you're willing to assist, I need someone to recover lost data fragments from the Matrix. The rewards would be... substantial.",
            "fragments": "The data fragments look like glowing blue crystals. They're scattered throughout the Arcane Matrix, especially in more complex puzzle areas."
        }),
        ("knowledge", {"history": 10, "research": 8, "data archaeology": 9}),
        ("services", ["provide quests", "identify items", "reward completion"])
    ]
}

# ==============================================================================
# CODING PUZZLES - The Arcane Matrix (CODE area)
# ==============================================================================

TERMINAL_BASE = {
    "typeclass": "typeclasses.themed_objects.Terminal",
    "key": "terminal",
    "desc": "An interactive terminal for solving coding challenges.",
    "locks": "get:false();puppet:false()",
    "attrs": [
        ("puzzle_type", "code"),
        ("difficulty", 1)
    ],
    "tags": [("puzzle", "matrix"), ("interactive", "matrix")]
}

BEGINNER_TERMINAL = {
    "prototype_parent": "TERMINAL_BASE",
    "key": "beginner terminal",
    "desc": "A simple terminal with a friendly interface, designed for those new to coding.",
    "attrs": [
        ("puzzle_type", "print"),
        ("current_code", "# Write a function that prints 'Hello, World!'"),
        ("expected_output", "Hello, World!"),
        ("hints", [
            "Use the print() function",
            "Don't forget to use quotes around text strings"
        ])
    ]
}

LOGIC_TERMINAL = {
    "prototype_parent": "TERMINAL_BASE",
    "key": "logic terminal",
    "desc": "A more complex terminal with circuits visible beneath its transparent casing.",
    "attrs": [
        ("puzzle_type", "logic"),
        ("difficulty", 3),
        ("current_code", "# Write a function to check if a number is prime"),
        ("expected_output", "True for prime numbers, False for non-prime numbers"),
        ("hints", [
            "A prime number is only divisible by 1 and itself",
            "Check divisibility up to the square root of the number",
            "Use modulo (%) to check for remainders"
        ])
    ]
}

# ==============================================================================
# EXPLORATION OBJECTS - The Neon Wilderness (EXPLORE area)
# ==============================================================================

TREASURE_BASE = {
    "typeclass": "typeclasses.themed_objects.ExplorationObject",
    "key": "treasure",
    "desc": "A valuable item found while exploring.",
    "attrs": [
        ("is_treasure", True),
        ("discovery_difficulty", 3)
    ],
    "tags": [("treasure", "wilderness"), ("collectible", "wilderness")]
}

DATA_CRYSTAL = {
    "prototype_parent": "TREASURE_BASE",
    "key": "data crystal",
    "desc": "A perfectly formed crystal containing compressed data and algorithms, valuable both for its information and as a crafting material.",
    "attrs": [
        ("discovery_difficulty", 5),
        ("is_hidden", True)
    ]
}

ANCIENT_ARTIFACT = {
    "prototype_parent": "TREASURE_BASE",
    "key": "ancient artifact",
    "desc": "A mysterious device from a forgotten digital civilization. Its purpose is unclear, but it radiates untapped power.",
    "attrs": [
        ("discovery_difficulty", 7),
        ("is_hidden", True)
    ]
}

# ==============================================================================
# OPPONENTS - The Neon Wilderness (EXPLORE area)
# ==============================================================================

OPPONENT_BASE = {
    "typeclass": "typeclasses.themed_objects.Opponent",
    "key": "opponent",
    "desc": "A challenging entity that will engage in combat.",
    "locks": "get:false();puppet:false()",
    "attrs": [
        ("health", 100),
        ("max_health", 100),
        ("attack_power", 10),
        ("defense", 5)
    ],
    "tags": [("opponent", "wilderness"), ("combat", "wilderness")]
}

BUG_CREATURE = {
    "prototype_parent": "OPPONENT_BASE",
    "key": "bug creature",
    "desc": "A skittering entity made of corrupt code, with too many legs and erratic movement patterns.",
    "attrs": [
        ("health", 50),
        ("max_health", 50),
        ("attack_power", 5),
        ("defense", 2),
        ("loot_table", {
            "code fragment": 0.7,
            "bug report": 0.3
        })
    ]
}

FIREWALL_GUARDIAN = {
    "prototype_parent": "OPPONENT_BASE",
    "key": "firewall guardian",
    "desc": "A towering humanoid figure composed of flickering red energy. It carries a shield emblazoned with a lock symbol.",
    "attrs": [
        ("health", 200),
        ("max_health", 200),
        ("attack_power", 15),
        ("defense", 10),
        ("loot_table", {
            "access key": 0.5,
            "power crystal": 0.4,
            "guardian core": 0.1
        })
    ]
}