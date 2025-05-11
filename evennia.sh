#!/bin/bash
# Evennia launcher script

# Script location
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
VENV_DIR="$SCRIPT_DIR/evenv_new"
GAME_DIR="$SCRIPT_DIR/mygame"

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found at $VENV_DIR"
    echo "Would you like to create a new virtual environment? (y/n)"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo "Creating new virtual environment..."
        python3.11 -m venv "$VENV_DIR"
        source "$VENV_DIR/bin/activate"
        pip install evennia
        echo "Evennia installed successfully!"
    else
        echo "Exiting. Please set up the virtual environment before using this script."
        exit 1
    fi
else
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
fi

# Change to the game directory
cd "$GAME_DIR" || { echo "Failed to change to game directory. Exiting."; exit 1; }

# Process command
if [ $# -eq 0 ]; then
    # No arguments, show usage
    echo "Evennia launcher script"
    echo "----------------------"
    echo "Usage: ./evennia.sh [command]"
    echo ""
    echo "Available commands:"
    echo "  start      - Start the Evennia server"
    echo "  stop       - Stop the Evennia server"
    echo "  restart    - Restart the Evennia server"
    echo "  status     - Show server status"
    echo "  migrate    - Update the database schema"
    echo "  shell      - Access the Evennia shell"
    echo "  superuser  - Create a superuser using the script"
    echo "  help       - Show evennia help"
    echo ""
    echo "Or pass any other Evennia command: ./evennia.sh [command]"
else
    # Execute the appropriate command
    case "$1" in
        start|stop|restart|status|shell|migrate)
            echo "Running: evennia $1"
            evennia "$1"
            ;;
        superuser)
            echo "Creating superuser using script..."
            python create_superuser.py
            ;;
        *)
            # Pass any other command directly to evennia
            evennia "$@"
            ;;
    esac
fi