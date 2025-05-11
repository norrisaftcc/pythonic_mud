# Building MUD worlds with Python: your best framework options

College students looking to build a multi-user dungeon (MUD) game have several Python-based options, each with unique strengths. After extensive research, Evennia stands out as the most comprehensive solution for an educational MUD project, with some important caveats about hosting requirements.

## The bottom line

Evennia is the **best framework** for creating a MUD web application for college students, offering a powerful combination of a robust Python foundation, built-in web interface, and extensive documentation. While mud-pi is too limited and Streamlit requires too much custom development, Evennia provides the ideal balance of turnkey setup and extensibility. The main challenge is hosting - you'll need a VPS service instead of PythonAnywhere or Streamlit Cloud due to websocket limitations on those platforms.

## Framework comparison

| Feature | Evennia | mud-pi | Streamlit |
|---------|---------|--------|-----------|
| Real-time chat | Built-in (websockets) | Basic (telnet only) | Requires workarounds |
| Web interface | Integrated webclient | None | Customizable but limited |
| Setup complexity | Moderate (5 commands) | Simple but limited | Simple but needs custom MUD code |
| Python extensibility | Excellent (typeclass system) | Basic | Good but not MUD-specific |
| Documentation | Comprehensive | Minimal | Good (but not for MUDs) |
| Community support | Active | Minimal | Active (but not MUD-focused) |
| Hosting requirements | VPS or dedicated server | Basic Python hosting | Streamlit Cloud (limited for MUDs) |

### Evennia (recommended)

Evennia is a modern Python framework specifically designed for text-based multiplayer games. It provides a complete foundation for MUD development, including:

- **Built-in web client** with customizable interface
- **Real-time communication** via multiple protocols including websockets
- **Database persistence** allowing games to survive server restarts
- **Flexible object system** that connects Python classes with database models
- **Comprehensive documentation** including tutorials and examples

The framework uses Django and Twisted to handle web functionality and networking, making it a production-ready solution that can scale from small classroom projects to large games.

### mud-pi

While mud-pi has educational value as a minimalist introduction to MUD concepts, its limitations make it unsuitable for this project:

- **No web interface** - designed for telnet connections only
- **Limited functionality** - provides only basic movement and chat
- **No active development** - appears unmaintained
- **Would require extensive custom code** to meet project requirements

### Streamlit-based solution

Streamlit is excellent for data applications but faces challenges for real-time multiplayer games:

- **Not designed for MUDs** - would require building MUD functionality from scratch
- **Real-time limitations** - its execution model reloads the entire app on interaction
- **Multi-user challenges** - requires additional libraries for shared state
- **Better suited for dashboards** than interactive multiplayer games

## Implementation guide for Evennia

### 1. Installation and setup

```bash
# Install Evennia
pip install evennia

# Create a new game folder
evennia --init mygame
cd mygame

# Initialize the database
evennia migrate

# Start the server (creates admin account when prompted)
evennia start
```

After installation, your game will be accessible via:
- Web client: http://localhost:4001
- Telnet: localhost:4000

### 2. Core concepts and architecture

Evennia's architecture is built around these key concepts:

- **Typeclasses**: Python classes that extend database models, allowing you to create custom game objects
- **Commands**: Functions that process player input and execute game actions
- **Objects**: Everything in the game (rooms, characters, items) inherits from the same base objects
- **Attributes**: Flexible storage system for adding data to any object
- **Scripts**: Persistent processes for timed events and background tasks

The system follows a clean, modular design that encourages best practices in Python development while abstracting away the complexities of networking and database management.

### 3. Implementing basic MUD features

#### Creating rooms

```python
# in mygame/typeclasses/rooms.py
from evennia import DefaultRoom

class ClassRoom(DefaultRoom):
    """A room for teaching Python concepts."""
    
    def at_object_creation(self):
        """Set up the room with default attributes."""
        self.db.subject = "Python Basics"
        self.db.difficulty = "Beginner"
        
    def return_appearance(self, looker):
        """Customize what players see when looking at the room."""
        appearance = super().return_appearance(looker)
        subject_info = f"\nSubject: {self.db.subject} (Level: {self.db.difficulty})"
        return appearance + subject_info
```

To create this room in-game:
```
@create Computer Lab:rooms.ClassRoom
@set Computer Lab/subject = Python Data Structures
@set Computer Lab/difficulty = Intermediate
@tel Computer Lab
```

#### Creating objects

```python
# in mygame/typeclasses/objects.py
from evennia import DefaultObject

class CodeArtifact(DefaultObject):
    """A code example that students can examine."""
    
    def at_object_creation(self):
        self.db.language = "Python"
        self.db.code_snippet = "print('Hello World')"
        self.db.difficulty = "Beginner"
        
    def at_desc(self, looker):
        """Show code snippet when examined."""
        return f"{self.db.desc}\n\nCode ({self.db.language}):\n{self.db.code_snippet}"
```

#### Creating commands

```python
# in mygame/commands/command.py
from evennia import Command

class CmdExecuteCode(Command):
    """
    Execute a code snippet in a controlled environment
    
    Usage:
      execute <code>
      
    Runs Python code and shows the output.
    """
    
    key = "execute"
    locks = "cmd:all()"  # Everyone can use this command
    
    def func(self):
        """Execute the command"""
        if not self.args:
            self.caller.msg("Usage: execute <code>")
            return
            
        code = self.args.strip()
        
        # In a real implementation, you'd want to add security measures
        # This is a simplified example
        try:
            # Extremely limited execution for demonstration only
            # DO NOT use exec() without proper sandboxing in production
            result = "Code execution disabled in this example"
            self.caller.msg(f"Result: {result}")
        except Exception as e:
            self.caller.msg(f"Error: {e}")
```

### 4. Adding custom Python objects/methods

Evennia's typeclass system makes it easy to add custom Python functionality:

```python
# in mygame/typeclasses/characters.py
from evennia import DefaultCharacter

class Student(DefaultCharacter):
    """Character class for student players."""
    
    def at_object_creation(self):
        """Add student-specific attributes."""
        self.db.programming_level = 1
        self.db.assignments_completed = 0
        self.db.skills = {"python": 0, "algorithms": 0, "data_structures": 0}
        
    def complete_assignment(self, assignment_type, difficulty):
        """Method to track student progress."""
        self.db.assignments_completed += 1
        skill_gain = difficulty * 0.1
        if assignment_type in self.db.skills:
            self.db.skills[assignment_type] += skill_gain
            
        # Level up if enough assignments completed
        if self.db.assignments_completed >= self.db.programming_level * 3:
            self.db.programming_level += 1
            self.msg(f"Congratulations! Your programming level is now {self.db.programming_level}!")
        
        return f"Assignment completed. {assignment_type.capitalize()} skill increased by {skill_gain}."
```

### 5. Deployment options

Given the websocket requirements for real-time functionality, a VPS (Virtual Private Server) is the most appropriate hosting solution. PythonAnywhere has limited websocket support (currently in beta), and Streamlit Cloud isn't designed for persistent connections needed by MUDs.

Recommended VPS options:

1. **DigitalOcean**
   - Basic Droplet ($5/month) sufficient for small class
   - One-click Python app deployment
   - Detailed tutorials available for Python web apps

2. **Linode**
   - Entry-level plan ($5/month)
   - Good performance for small to medium projects
   - Python-friendly environment

3. **AWS Lightsail**
   - Simple VPS from Amazon
   - Fixed pricing starting at $3.50/month
   - Smooth upgrade path to other AWS services if needed

Basic deployment process:

```bash
# On the VPS after installing Python and required packages
git clone https://github.com/yourusername/your-mud-project.git
cd your-mud-project
pip install -r requirements.txt
evennia migrate
evennia start

# To run as a service that persists after logout
# Create a systemd service file
```

### 6. Learning resources

**Official Evennia resources:**
- [Main documentation](https://www.evennia.com/docs/latest/)
- [Beginner tutorial](https://www.evennia.com/docs/latest/Tutorials/Tutorial-Learning-Evennia-Step-by-Step)
- [GitHub repository](https://github.com/evennia/evennia)
- [Community forum](https://github.com/evennia/evennia/discussions)

**Additional resources:**
- [MUD Dev Wiki](http://mud.wikia.com/wiki/Main_Page) - General MUD design concepts
- [Python Discord server](https://discord.gg/python) - General Python help
- [Django documentation](https://docs.djangoproject.com/) - For understanding the web framework Evennia uses

## Advanced examples

### Creating an interactive teaching puzzle

```python
# in mygame/typeclasses/objects.py
from evennia import DefaultObject
import re

class PythonPuzzle(DefaultObject):
    """An interactive puzzle that tests Python knowledge."""
    
    def at_object_creation(self):
        """Set up the puzzle with default attributes."""
        self.db.question = "Write a function that returns the sum of two numbers."
        self.db.test_cases = [
            {"input": [2, 3], "expected": 5},
            {"input": [0, 0], "expected": 0},
            {"input": [-1, 1], "expected": 0}
        ]
        self.db.solution_pattern = r"def\s+\w+\s*\(.*\).*\s*return\s+.*\+"
        self.db.hints = [
            "Start by defining a function with two parameters",
            "Use the + operator to add the parameters",
            "Don't forget to return the result"
        ]
        self.db.hint_index = 0
        self.db.solved_by = []
        
    def get_hint(self, solver):
        """Provide a hint to the player."""
        if self.db.hint_index < len(self.db.hints):
            hint = self.db.hints[self.db.hint_index]
            self.db.hint_index += 1
            return f"Hint {self.db.hint_index}/{len(self.db.hints)}: {hint}"
        else:
            return "No more hints available."
            
    def check_solution(self, solver, code):
        """Verify if the submitted code solves the puzzle."""
        # Simple pattern matching for demonstration
        # A real implementation would safely execute code against test cases
        if re.search(self.db.solution_pattern, code):
            if solver not in self.db.solved_by:
                self.db.solved_by.append(solver)
            return True, "Your solution is correct! Puzzle solved."
        else:
            return False, "Your solution doesn't match the expected pattern. Try again."
```

### Creating a multi-room tutorial area

```python
# in mygame/world/tutorial.py
from evennia import create_object
from typeclasses.rooms import ClassRoom
from typeclasses.objects import CodeArtifact, PythonPuzzle

def create_tutorial_area(start_location):
    """
    Create a multi-room tutorial area.
    Returns the entrance room.
    """
    # Create rooms
    entrance = create_object(ClassRoom, key="Tutorial Entrance", 
                         location=None)
    entrance.db.desc = "Welcome to the Python Tutorial Area. Here you'll learn the basics of MUD development."
    entrance.db.subject = "Introduction"
    
    basics_room = create_object(ClassRoom, key="Python Basics Lab", 
                            location=None)
    basics_room.db.desc = "A room filled with terminals displaying Python code examples."
    basics_room.db.subject = "Python Fundamentals"
    
    oop_room = create_object(ClassRoom, key="Object-Oriented Programming Lab", 
                         location=None)
    oop_room.db.desc = "Diagrams showing class hierarchies cover the walls."
    oop_room.db.subject = "OOP Concepts"
    
    # Link rooms with exits
    entrance.db.east = basics_room.dbref
    basics_room.db.west = entrance.dbref
    basics_room.db.north = oop_room.dbref
    oop_room.db.south = basics_room.dbref
    
    # Add objects to rooms
    hello_world = create_object(CodeArtifact, key="Hello World Example", 
                             location=basics_room)
    hello_world.db.desc = "A simple introductory Python example."
    hello_world.db.code_snippet = 'print("Hello, World!")'
    
    class_example = create_object(CodeArtifact, key="Class Definition Example", 
                               location=oop_room)
    class_example.db.desc = "An example of Python class definition."
    class_example.db.code_snippet = """class Player:
    def __init__(self, name):
        self.name = name
        self.level = 1
        
    def level_up(self):
        self.level += 1
        return f"{self.name} is now level {self.level}!"
"""
    
    # Add a puzzle
    sum_puzzle = create_object(PythonPuzzle, key="Addition Puzzle", 
                            location=basics_room)
    sum_puzzle.db.desc = "A terminal with a coding challenge."
    
    return entrance
```

## Conclusion

Evennia provides the most comprehensive and appropriate solution for creating a MUD web application for college students. Its combination of built-in web functionality, flexible Python extensibility, and excellent documentation make it ideal for educational environments with students of varying skill levels. While the hosting requirements (VPS instead of PythonAnywhere or Streamlit Cloud) present a slight challenge, the benefits of using a purpose-built framework far outweigh the alternatives of extensive custom development or limited functionality.

For a classroom setting, Evennia creates an engaging environment where students can explore Python concepts through interactive game development, building real projects that demonstrate programming principles in an applied context.