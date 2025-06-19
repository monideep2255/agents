#!/usr/bin/env python3
"""
Setup script to help configure environment variables for the career conversation app.
"""

import os
from pathlib import Path

def create_env_file():
    """Create a .env file with placeholder values."""
    env_path = Path(".env")
    
    if env_path.exists():
        print(".env file already exists!")
        return
    
    env_content = """# OpenAI API Key - Replace with your actual API key
# Get it from: https://platform.openai.com/account/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Pushover credentials - Replace with your actual tokens
# Get them from: https://pushover.net/
PUSHOVER_USER=your_pushover_user_token_here
PUSHOVER_TOKEN=your_pushover_application_token_here
"""
    
    with open(env_path, "w") as f:
        f.write(env_content)
    
    print("Created .env file with placeholder values!")
    print("Please edit the .env file and replace the placeholder values with your actual API keys.")

def check_current_env():
    """Check what environment variables are currently set."""
    required_vars = ['OPENAI_API_KEY', 'PUSHOVER_USER', 'PUSHOVER_TOKEN']
    
    print("Current environment variable status:")
    print("-" * 50)
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show first and last few characters for security
            masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
            print(f"✓ {var}: {masked_value}")
        else:
            print(f"✗ {var}: Not set")
    
    print("-" * 50)

if __name__ == "__main__":
    print("Career Conversation App - Environment Setup")
    print("=" * 50)
    
    check_current_env()
    print()
    
    response = input("Would you like to create a .env file with placeholder values? (y/n): ")
    if response.lower() == 'y':
        create_env_file()
        print("\nNext steps:")
        print("1. Edit the .env file and add your actual API keys")
        print("2. For HuggingFace deployment, add these as secrets in your Space settings")
        print("3. Run the app with: python app.py")
    else:
        print("No .env file created. Make sure to set your environment variables manually.") 