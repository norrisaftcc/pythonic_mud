# Script to create an Evennia superuser programmatically
import os
import sys
import django

# Add the parent directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")
django.setup()

# Import the Account model
from evennia.accounts.models import AccountDB

# Create a superuser if it doesn't exist
if not AccountDB.objects.filter(is_superuser=True).exists():
    print("Creating superuser...")
    account = AccountDB.objects.create_superuser(
        username="admin",
        email="admin@example.com",
        password="sudosudo",  # Using the password from setup.txt
    )
    print(f"Superuser '{account.username}' created successfully!")
else:
    print("Superuser already exists.")