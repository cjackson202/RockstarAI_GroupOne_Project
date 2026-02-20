# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Annotated

import pandas as pd
from agent_framework.azure import AzureAIAgentsProvider
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
from pydantic import Field

# Load environment variables from .env file
load_dotenv()

"""
🎯 HACKATHON CHALLENGE: User Access Control Agent
Your mission: Complete the TODOs to build a working access control system!
"""

# Define data file paths
DATA_DIR = Path(__file__).parent / "data"
EMPLOYEES_FILE = DATA_DIR / "employees.csv"
GUESTS_FILE = DATA_DIR / "guests.csv"
PARKING_RECORDS_FILE = DATA_DIR / "parking_records.csv"

# ============================================================================
# 🔐 HUMAN-IN-THE-LOOP APPROVAL SYSTEM
# ============================================================================
# PASSKEY: 1234
# This approval system protects all write operations (CSV modifications).
# Before any data is written, the system admin must enter the passkey.
# This prevents unauthorized changes to the database!
# ============================================================================

APPROVAL_PASSKEY = "1234"  # Secret passkey for write operations - DO NOT SHARE!

def request_approval_for_write_operation(operation_name: str, details: str) -> bool:
    """Request human approval before executing a write operation.
    
    Args:
        operation_name: Name of the operation (e.g., "Add Employee", "Generate Parking Code")
        details: Description of what will be written (e.g., "Add John Doe with alias jdoe")
    
    Returns:
        True if approved (correct passkey entered), False if denied
    
    Example usage in your write functions:
        if not request_approval_for_write_operation("Add Employee", f"Add {name} with alias {alias}"):
            return "Operation cancelled - not approved"
    """
    print("\n" + "="*70)
    print("🔐 WRITE OPERATION APPROVAL REQUIRED")
    print("="*70)
    print(f"Operation: {operation_name}")
    print(f"Details: {details}")
    print(f"\nThis operation will modify data files.")
    print("\nTo approve, enter the passkey (or press Enter to deny):")
    print("="*70)
    
    try:
        user_input = input("Enter passkey: ").strip()
        
        if user_input == APPROVAL_PASSKEY:
            print("✅ APPROVED - Operation will proceed\n")
            return True
        else:
            print("❌ DENIED - Invalid passkey or operation cancelled\n")
            return False
    except (EOFError, KeyboardInterrupt):
        print("\n❌ DENIED - Operation cancelled by user\n")
        return False


# ============================================================================
# 🟢 LEVEL 2: DATABASE DETECTIVE - Implement these search functions!
# ============================================================================

def check_employee_exists(
    alias: Annotated[str, Field(description="The alias/username of the employee to check.")],
) -> str:
    """Check if an employee exists in the employee dataset by their alias."""
    # TODO: Implement this function!
    # HINT: Use pandas to read EMPLOYEES_FILE
    # HINT: Search for the alias (case-insensitive)
    # HINT: If found, return employee info. If not found, return "not found" message
    
    pass  # Replace this with your code!


def check_guest_exists(
    first_name: Annotated[str, Field(description="The first name of the guest to check.")],
    last_name: Annotated[str, Field(description="The last name of the guest to check.")],
) -> str:
    """Check if a guest exists in the guest dataset by their first and last name. Validates 30-day expiration."""
    # TODO: Implement this function!
    # HINT: Combine first_name and last_name into full_name
    # HINT: Read GUESTS_FILE with pandas
    # HINT: Search for the full name (case-insensitive)
    # HINT: BONUS - Check if more than 30 days have passed since date_accessed
    
    pass  # Replace this with your code!


# ============================================================================
# 🟠 LEVEL 3: THE GATEKEEPER - Implement these add functions!
# ============================================================================

def add_employee(
    name: Annotated[str, Field(description="The full name of the employee to add.")],
    alias: Annotated[str, Field(description="The alias/username for the employee.")],
) -> str:
    """Add a new employee to the employee dataset. Requires PASSKEY approval before writing!"""
    # TODO: Implement this function!
    # HINT: Read EMPLOYEES_FILE
    # HINT: Check if employee already exists
    # HINT: 🔐 IMPORTANT: Call request_approval_for_write_operation() BEFORE writing to CSV!
    #       Example: if not request_approval_for_write_operation("Add Employee", f"Add {name} with alias {alias}"):
    #                    return "Operation cancelled"
    # HINT: If not exists, create a new row with name, alias, current date, and empty badge_access
    # HINT: Use pd.concat() to add the new row
    # HINT: Save back to CSV with df.to_csv()
    
    pass  # Replace this with your code!


def add_guest(
    first_name: Annotated[str, Field(description="The first name of the guest to add.")],
    last_name: Annotated[str, Field(description="The last name of the guest to add.")],
    alias: Annotated[str, Field(description="The alias/username for the guest.")],
) -> str:
    """Add a new guest to the guest dataset. Requires PASSKEY approval before writing!"""
    # TODO: Implement this function!
    # HINT: Combine first_name and last_name into full_name
    # HINT: Read GUESTS_FILE and check if guest already exists
    # HINT: 🔐 IMPORTANT: Call request_approval_for_write_operation() BEFORE writing to CSV!
    # HINT: Guests only have name, alias, and date_accessed columns
    # HINT: Use pd.concat() and save with df.to_csv()
    
    pass  # Replace this with your code!


# ============================================================================
# 🔴 LEVEL 4: PARKING PATROL - Implement parking code generation!
# ============================================================================

def generate_parking_code(
    alias: Annotated[str, Field(description="The alias/username of the employee requesting parking.")],
) -> str:
    """Generate a 6-digit parking validation code for an employee and save it to parking records. Requires PASSKEY approval before writing!"""
    # TODO: Implement this function!
    # HINT: Use random.choice() to generate a 6-character code
    # HINT: Use string.ascii_uppercase + string.digits for characters
    # HINT: 🔐 IMPORTANT: Call request_approval_for_write_operation() BEFORE writing to CSV!
    # HINT: Save the code to PARKING_RECORDS_FILE with alias and current date
    # HINT: Handle case where PARKING_RECORDS_FILE might not exist yet
    
    pass  # Replace this with your code!


# ============================================================================
# 🟣 LEVEL 5: BADGE BOSS - Implement badge access management!
# ============================================================================

def check_badge_access(
    alias: Annotated[str, Field(description="The alias/username of the employee to check badge access for.")],
) -> str:
    """Check which floors an employee has badge access to (floors 2-7). Note: Floor 1 is publicly accessible to everyone."""
    # TODO: Implement this function!
    # HINT: Read EMPLOYEES_FILE and find the employee by alias
    # HINT: Get the 'badge_access' column (it's comma-separated floor numbers)
    # HINT: Return a friendly message showing which floors they can access
    
    pass  # Replace this with your code!


def update_badge_access(
    alias: Annotated[str, Field(description="The alias/username of the employee to update badge access for.")],
    floors: Annotated[str, Field(description="Comma-separated list of floor numbers (2-7) to grant access to. Example: '2,3,4' or '5,6,7'. Note: Floor 1 is publicly accessible and doesn't need badge access.")],
) -> str:
    """Update or add badge access floors for an employee (floors 2-7). This will ADD to existing access, not replace it. Requires PASSKEY approval before writing!"""
    # TODO: Implement this function!
    # HINT: Read EMPLOYEES_FILE and find the employee
    # HINT: Parse the 'floors' parameter (split by comma)
    # HINT: Combine with existing floors from badge_access column (use sets to avoid duplicates)
    # HINT: 🔐 IMPORTANT: Call request_approval_for_write_operation() BEFORE writing to CSV!
    #       (But only if there are NEW floors to add - don't require approval if they already have access)
    # HINT: Save the updated access back to the CSV
    
    pass  # Replace this with your code!


# ============================================================================
# ⚫ LEVEL 6: THE EXPERT - Handle expired guests (advanced!)
# ============================================================================

def remove_expired_guest(
    first_name: Annotated[str, Field(description="The first name of the expired guest to remove.")],
    last_name: Annotated[str, Field(description="The last name of the expired guest to remove.")],
) -> str:
    """Remove an expired guest from the guest database. Requires PASSKEY approval before writing!"""
    # TODO: Implement this function!
    # HINT: Combine first_name and last_name into full_name
    # HINT: 🔐 IMPORTANT: Call request_approval_for_write_operation() BEFORE removing from CSV!
    # HINT: Read GUESTS_FILE, find the guest, and remove their row
    # HINT: Use df = df[df['name'].str.lower() != full_name.lower()]
    # HINT: Save back to CSV
    
    pass  # Replace this with your code!


def add_guest_with_auto_alias(
    first_name: Annotated[str, Field(description="The first name of the guest to add.")],
    last_name: Annotated[str, Field(description="The last name of the guest to add.")],
) -> str:
    """Add a new guest with an automatically generated alias. Use this for re-registering expired guests. Requires PASSKEY approval before writing!"""
    # TODO: Implement this function!
    # HINT: Auto-generate alias like: first_initial + last_name + timestamp
    # HINT: Example: "Tony Stark" -> "tstark0219" (with month+day+hour)
    # HINT: Make sure the alias is unique by checking existing guests
    # HINT: 🔐 IMPORTANT: Call request_approval_for_write_operation() BEFORE writing to CSV!
    # HINT: Add the guest with the auto-generated alias and current date
    
    pass  # Replace this with your code!


# ============================================================================
# 🎨 BONUS FEATURE: Tool execution logger (copy from agent.py if you want!)
# ============================================================================

def display_tool_execution_log(thought_process) -> None:
    """Display detailed tool execution information from the captured thought process."""
    # This is optional - add this later if you want the 'show' command feature!
    pass


# ============================================================================
# 🟢 LEVEL 1: THE FOUNDATION - Complete the agent setup!
# ============================================================================

async def run_user_check_agent() -> None:
    """Run the user access check agent with interactive conversation."""
    print("=== User Access Check Agent ===\n")
    print("💡 Tip: Type 'exit' or 'quit' to end the session\n")

    # Azure authentication setup
    async with (
        DefaultAzureCredential() as credential,
        AzureAIAgentsProvider(credential=credential) as provider,
    ):
        # Get current date for agent context
        current_datetime = datetime.now()
        current_date_str = current_datetime.strftime("%Y-%m-%d")
        current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        # TODO: Create your agent here!
        # HINT: Use await provider.create_agent()
        # HINT: Give it a name like "UserAccessAgent"
        # HINT: Write clear instructions - this is the agent's brain!
        # HINT: Add your tools to the tools=[] parameter
        
        agent = await provider.create_agent(
            name="UserAccessAgent",
            instructions=f"""You are a friendly access control assistant. 

CURRENT DATE AND TIME: {current_datetime_str}

TODO: Write your agent instructions here!

TIPS FOR WRITING GOOD INSTRUCTIONS:
- Tell the agent what its job is
- Explain the workflow step-by-step
- Be specific about when to use each tool
- Add personality to make it friendly!

SUGGESTED WORKFLOW:
1. Greet users warmly
2. Ask if they are an employee or guest
3. For employees: Ask for alias, check database, offer parking
4. For guests: Ask for name, check database, explain parking app
5. Handle badge access requests for employees

Remember:
- Only employees get parking codes (guests use ParkRTC app)
- Floor 1 is public, floors 2-7 need badge access
- Guests expire after 30 days
""",
            tools=[],  # TODO: Add your tools here! Example: [check_employee_exists, add_employee, ...]
        )

        print("Agent is ready! You can start chatting.\n")
        
        # Create a thread to maintain conversation history
        thread = agent.get_new_thread()
        
        # TODO: Implement the conversation loop!
        # HINT: Use a while True loop
        # HINT: Get user input with input("You: ")
        # HINT: Check for exit commands like 'quit' or 'exit'
        # HINT: Send message to agent with: result = await agent.run(user_input, thread=thread)
        # HINT: Print the agent's response
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                # TODO: Handle exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    print("\nAgent: Goodbye! Have a great day!")
                    break
                
                # Skip empty inputs
                if not user_input:
                    continue
                
                # TODO: Send message to agent and print response
                # HINT: result = await agent.run(user_input, thread=thread)
                # HINT: print("Agent:", str(result))
                
                print("Agent: [Your message here - implement agent.run() above!]")
                
            except EOFError:
                print("\n\nAgent: Goodbye! Have a great day!")
                break


async def main() -> None:
    """Main entry point for the user access check agent."""
    await run_user_check_agent()


if __name__ == "__main__":
    # Start the agent!
    asyncio.run(main())
