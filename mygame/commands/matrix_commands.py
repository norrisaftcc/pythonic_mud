"""
Matrix (CODE) Commands

This module contains commands for the CODE/Matrix area of the Pythonic MUD.
These commands enable players to interact with coding terminals, solve
programming puzzles, and execute Python code in a controlled environment.

"""
from evennia.commands.command import Command
from evennia.utils.evtable import EvTable
from evennia.utils.utils import class_from_module
from evennia import CmdSet
import re
import io
import sys
import traceback
from contextlib import redirect_stdout, redirect_stderr
from typing import Any, Dict, List, Optional, Tuple


class CmdCode(Command):
    """
    Write and execute Python code in a terminal.

    Usage:
      code
      code <python code>
      code/clear
      code/run
      code/hint
      code/reset

    This command allows you to write and execute Python code in a terminal
    object. The code is executed in a sandboxed environment.

    With no arguments, it shows your current code in the terminal.

    Switches:
      clear - Clear the current code in the terminal
      run - Execute the current code in the terminal
      hint - Get a hint about the current puzzle
      reset - Reset the current puzzle to its initial state

    Examples:
      code print("Hello, World!")
      code/run
      code/hint
    """

    key = "code"
    aliases = ["program"]
    help_category = "Matrix"

    def func(self):
        """Implement the command"""
        caller = self.caller

        # First check if the caller is at a terminal
        terminal = None
        for obj in caller.location.contents:
            if hasattr(obj, 'db') and obj.db.puzzle_type and "code" in obj.db.puzzle_type:
                terminal = obj
                break

        if not terminal:
            caller.msg("You need to be at a code terminal to use this command.")
            return

        # Mark this user as the current terminal user
        if terminal.db.current_user and terminal.db.current_user != caller:
            caller.msg(f"{terminal.db.current_user.name} is currently using this terminal.")
            return
        else:
            terminal.db.current_user = caller

        # Handle the different switches
        if 'clear' in self.switches:
            terminal.db.current_code = ""
            caller.msg("You clear the code in the terminal.")
            return
        elif 'run' in self.switches:
            self._run_code(caller, terminal)
            return
        elif 'hint' in self.switches:
            self._get_hint(caller, terminal)
            return
        elif 'reset' in self.switches:
            self._reset_puzzle(caller, terminal)
            return

        # If no switches and no args, display the current code
        if not self.args:
            if not terminal.db.current_code or terminal.db.current_code.strip() == "":
                caller.msg("The terminal is empty. Use 'code <python code>' to add code.")
            else:
                caller.msg(f"Current code in the terminal:\n{terminal.db.current_code}")
            return

        # If we have args, add the code to the terminal
        code = self.args.strip()
        
        # If this is the first code entry, replace the current_code
        # Otherwise append to it with a newline
        if not terminal.db.current_code or terminal.db.current_code.strip() == "":
            terminal.db.current_code = code
        else:
            terminal.db.current_code += f"\n{code}"
        
        caller.msg("Code added to the terminal.")

    def _run_code(self, caller, terminal):
        """Execute the Python code in the terminal"""
        code = terminal.db.current_code
        
        if not code or code.strip() == "":
            caller.msg("There is no code to run. Use 'code <python code>' to add code.")
            return

        # Execute the code in a safe environment
        result, output, error = self._safe_eval(code)
        
        # Display the results
        if error:
            caller.msg(f"|rError:|n\n{error}")
        else:
            caller.msg(f"|gCode executed successfully:|n\n{output}")
            
            # Check if this solves the puzzle
            if terminal.db.expected_output and output.strip() == terminal.db.expected_output.strip():
                # Mark the puzzle as solved by this player
                if not terminal.db.solved_by:
                    terminal.db.solved_by = set()
                terminal.db.solved_by.add(caller)
                
                caller.msg("|gCongratulations! You solved the puzzle!|n")
                
                # Give a reward (this could be expanded later)
                from evennia.utils.spawner import spawn
                try:
                    # Try to spawn a code fragment as reward
                    result = spawn("CODE_FRAGMENT", prototype_modules=["world.prototypes"])
                    if result:
                        reward = result[0]
                        reward.location = caller
                        caller.msg(f"You received a {reward.key} as a reward!")
                except Exception:
                    # Fallback to a basic reward
                    from typeclasses.themed_objects import CodeObject
                    reward = CodeObject.create(
                        key="code fragment",
                        location=caller,
                        attributes={
                            "desc": "A shimmering fragment of code, useful for crafting digital items.",
                            "material_type": "data"
                        }
                    )
                    caller.msg("You received a code fragment as a reward!")

    def _get_hint(self, caller, terminal):
        """Get a hint about the current puzzle"""
        if not terminal.db.hints:
            caller.msg("There are no hints available for this puzzle.")
            return
        
        # Choose an appropriate hint based on how many times the player has asked
        hint_count = getattr(caller.db, "hints_used", {}).get(terminal.id, 0)
        if not hasattr(caller.db, "hints_used"):
            caller.db.hints_used = {}
        if terminal.id not in caller.db.hints_used:
            caller.db.hints_used[terminal.id] = 0
        
        # Increment hint count
        caller.db.hints_used[terminal.id] += 1
        hint_index = min(hint_count, len(terminal.db.hints) - 1)
        
        # Display the hint
        hint = terminal.db.hints[hint_index]
        caller.msg(f"|yHint:|n {hint}")

    def _reset_puzzle(self, caller, terminal):
        """Reset the terminal to its initial state"""
        # Reset the code in the terminal
        terminal.db.current_code = ""
        
        # Reset the current user
        terminal.db.current_user = None
        
        caller.msg("You reset the terminal to its initial state.")

    def _safe_eval(self, code_string):
        """
        Safely evaluate Python code with restricted abilities.
        Returns a tuple of (result, output, error)
        """
        restricted_globals = {
            "__builtins__": {
                # Allow basic operations
                "abs": abs, "all": all, "any": any, "bool": bool,
                "chr": chr, "dict": dict, "dir": dir, "divmod": divmod,
                "enumerate": enumerate, "filter": filter, "float": float,
                "format": format, "frozenset": frozenset, "getattr": getattr,
                "hasattr": hasattr, "hash": hash, "hex": hex, "id": id,
                "int": int, "isinstance": isinstance, "issubclass": issubclass,
                "iter": iter, "len": len, "list": list, "map": map,
                "max": max, "min": min, "next": next, "oct": oct,
                "ord": ord, "pow": pow, "print": print, "range": range,
                "repr": repr, "reversed": reversed, "round": round,
                "set": set, "slice": slice, "sorted": sorted, "str": str,
                "sum": sum, "tuple": tuple, "type": type, "zip": zip,
            }
        }
        
        # Capture stdout and stderr
        stdout = io.StringIO()
        stderr = io.StringIO()
        
        result = None
        error = None
        
        try:
            # First compile the code to catch syntax errors
            compiled_code = compile(code_string, "<string>", "exec")
            
            # Execute the code, capturing output
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exec(compiled_code, restricted_globals)
            
        except Exception as e:
            error = f"{type(e).__name__}: {str(e)}\n"
            error += "".join(traceback.format_exception(type(e), e, e.__traceback__))
        
        return result, stdout.getvalue(), error


class CmdInspectPuzzle(Command):
    """
    Examine a programming puzzle to understand its requirements.

    Usage:
      puzzle <terminal>

    This command provides detailed information about a programming
    puzzle, including its description, expected output, and current
    status.

    Examples:
      puzzle terminal
      puzzle beginner terminal
    """

    key = "puzzle"
    aliases = ["inspect puzzle"]
    help_category = "Matrix"

    def func(self):
        """Implement the command"""
        caller = self.caller

        if not self.args:
            caller.msg("What terminal or puzzle do you want to inspect?")
            return

        # Try to find the terminal
        terminal = caller.search(self.args)
        if not terminal:
            return

        # Check if this is actually a terminal
        if not hasattr(terminal, 'db') or not terminal.db.puzzle_type or "code" not in terminal.db.puzzle_type:
            caller.msg(f"{terminal.key} is not a code terminal.")
            return

        # Display information about the puzzle
        message = [f"|gPuzzle Information for {terminal.key}:|n"]
        
        # Description
        desc = terminal.db.desc if terminal.db.desc else "No description available."
        message.append(f"Description: {desc}")
        
        # Puzzle type
        if terminal.db.puzzle_type:
            message.append(f"Puzzle Type: {terminal.db.puzzle_type}")
        
        # Current assignment/challenge
        if terminal.db.current_code and terminal.db.current_code.strip():
            message.append(f"Current Code:\n{terminal.db.current_code}")
        else:
            message.append("Current Code: None")
        
        # Expected output (if player has seen hints)
        hint_count = getattr(caller.db, "hints_used", {}).get(terminal.id, 0)
        if hint_count > 0 and terminal.db.expected_output:
            message.append(f"Expected Output: {terminal.db.expected_output}")
        
        # Difficulty
        if terminal.db.difficulty:
            difficulty_levels = {
                1: "Beginner",
                2: "Easy",
                3: "Intermediate",
                4: "Advanced",
                5: "Expert"
            }
            difficulty = difficulty_levels.get(terminal.db.difficulty, str(terminal.db.difficulty))
            message.append(f"Difficulty: {difficulty}")
        
        # Solved status
        if terminal.db.solved_by and caller in terminal.db.solved_by:
            message.append("|gStatus: You have solved this puzzle!|n")
        else:
            message.append("|yStatus: Not yet solved|n")
        
        # Send the full inspection results
        caller.msg("\n".join(message))


class CmdShowTerminals(Command):
    """
    List all available code terminals in the current area.

    Usage:
      terminals

    This command shows all terminals that contain programming puzzles
    in your current location, along with their puzzle type and difficulty.

    Examples:
      terminals
    """

    key = "terminals"
    aliases = ["list terminals"]
    help_category = "Matrix"

    def func(self):
        """Implement the command"""
        caller = self.caller
        location = caller.location

        # Find all terminals in the current location
        terminals = []
        for obj in location.contents:
            if hasattr(obj, 'db') and obj.db.puzzle_type and "code" in obj.db.puzzle_type:
                terminals.append(obj)

        if not terminals:
            caller.msg("There are no code terminals in this area.")
            return

        # Display the terminals in a table
        table = EvTable("Terminal", "Type", "Difficulty", "Status", border="cells")
        
        for term in terminals:
            # Get difficulty level
            difficulty_levels = {
                1: "Beginner",
                2: "Easy",
                3: "Intermediate",
                4: "Advanced",
                5: "Expert"
            }
            difficulty = difficulty_levels.get(term.db.difficulty, str(term.db.difficulty))
            
            # Check solved status
            if term.db.solved_by and caller in term.db.solved_by:
                status = "|gSolved|n"
            else:
                status = "|yUnsolved|n"
            
            table.add_row(term.key, term.db.puzzle_type, difficulty, status)

        caller.msg("|gAvailable code terminals:|n")
        caller.msg(table)


class MatrixCmdSet(CmdSet):
    """
    Cmdset for matrix-related commands.
    """
    
    key = "matrix_commands"
    
    def at_cmdset_creation(self):
        """
        Add the matrix commands to the command set
        """
        self.add(CmdCode())
        self.add(CmdInspectPuzzle())
        self.add(CmdShowTerminals())