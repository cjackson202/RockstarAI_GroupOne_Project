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
User Access Check Agent

This agent checks if users exist in employee or guest datasets and can add new users with approval.
"""

# Define data file paths
# Since agent.py is in solution/, go up one level to find data/
DATA_DIR = Path(__file__).parent.parent / "data"
EMPLOYEES_FILE = DATA_DIR / "employees.csv"
GUESTS_FILE = DATA_DIR / "guests.csv"
PARKING_RECORDS_FILE = DATA_DIR / "parking_records.csv"

# ============================================================================
# 🔐 HUMAN-IN-THE-LOOP APPROVAL SYSTEM
# ============================================================================
# PASSKEY: 1234
# This approval system protects all write operations (CSV modifications).
# Before any data is written, the system admin must enter the passkey.
# ============================================================================

APPROVAL_PASSKEY = "1234"  # Secret passkey for write operations

def request_approval_for_write_operation(operation_name: str, details: str) -> bool:
    """Request human approval before executing a write operation.
    
    Args:
        operation_name: Name of the operation (e.g., "Add Employee", "Generate Parking Code")
        details: Description of what will be written (e.g., "Add John Doe with alias jdoe")
    
    Returns:
        True if approved, False if denied
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


def check_employee_exists(
    alias: Annotated[str, Field(description="The alias/username of the employee to check.")],
) -> str:
    """Check if an employee exists in the employee dataset by their alias."""
    try:
        df = pd.read_csv(EMPLOYEES_FILE)
        # Case-insensitive search by alias
        result = df[df['alias'].str.lower() == alias.lower()]
        
        if not result.empty:
            employee = result.iloc[0]
            return f"Employee found: {employee['name']} (alias: {employee['alias']}, last accessed: {employee['date_accessed']})"
        else:
            return f"Employee with alias '{alias}' not found in the employee database."
    except Exception as e:
        return f"Error checking employee database: {str(e)}"


def check_guest_exists(
    first_name: Annotated[str, Field(description="The first name of the guest to check.")],
    last_name: Annotated[str, Field(description="The last name of the guest to check.")],
) -> str:
    """Check if a guest exists in the guest dataset by their first and last name. Validates 30-day expiration."""
    try:
        from datetime import timedelta
        
        df = pd.read_csv(GUESTS_FILE)
        # Construct full name and search case-insensitively
        full_name = f"{first_name} {last_name}"
        result = df[df['name'].str.lower() == full_name.lower()]
        
        if not result.empty:
            guest = result.iloc[0]
            
            # Check if guest has expired (more than 30 days since last access)
            last_accessed = pd.to_datetime(guest['date_accessed'])
            current_date = pd.to_datetime(datetime.now().strftime("%Y-%m-%d"))
            days_since_access = (current_date - last_accessed).days
            
            if days_since_access > 30:
                return f"Guest found but EXPIRED: {guest['name']} (alias: {guest['alias']}, last accessed: {guest['date_accessed']}, {days_since_access} days ago). Guest access has expired after 30 days and must be re-registered with a new alias."
            else:
                return f"Guest found: {guest['name']} (alias: {guest['alias']}, last accessed: {guest['date_accessed']}, {days_since_access} days ago)"
        else:
            return f"Guest '{full_name}' not found in the guest database."
    except Exception as e:
        return f"Error checking guest database: {str(e)}"


def remove_expired_guest(
    first_name: Annotated[str, Field(description="The first name of the expired guest to remove.")],
    last_name: Annotated[str, Field(description="The last name of the expired guest to remove.")],
) -> str:
    """Remove an expired guest from the guest database. Requires passkey approval."""
    try:
        full_name = f"{first_name} {last_name}"
        
        # 🔐 REQUEST APPROVAL BEFORE WRITING
        if not request_approval_for_write_operation(
            "Remove Expired Guest",
            f"Remove guest '{full_name}' from the guest database"
        ):
            return f"❌ Operation cancelled: Removal of guest '{full_name}' was not approved."
        
        df = pd.read_csv(GUESTS_FILE)
        
        # Find and remove the guest
        initial_count = len(df)
        df = df[df['name'].str.lower() != full_name.lower()]
        final_count = len(df)
        
        if initial_count > final_count:
            df.to_csv(GUESTS_FILE, index=False)
            return f"✅ Expired guest '{full_name}' has been removed from the database. They can now be re-registered with a new alias."
        else:
            return f"Guest '{full_name}' not found in the database."
    except Exception as e:
        return f"Error removing expired guest: {str(e)}"


def add_employee(
    name: Annotated[str, Field(description="The full name of the employee to add.")],
    alias: Annotated[str, Field(description="The alias/username for the employee.")],
) -> str:
    """Add a new employee to the employee dataset. Requires passkey approval."""
    try:
        df = pd.read_csv(EMPLOYEES_FILE)
        
        # Check if already exists
        if not df[df['name'].str.lower() == name.lower()].empty:
            return f"Employee '{name}' already exists in the database."
        
        # 🔐 REQUEST APPROVAL BEFORE WRITING
        if not request_approval_for_write_operation(
            "Add Employee",
            f"Add employee '{name}' with alias '{alias}' to the database"
        ):
            return f"❌ Operation cancelled: Adding employee '{name}' was not approved."
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Add new row
        new_row = pd.DataFrame({
            'name': [name],
            'alias': [alias],
            'date_accessed': [current_date],
            'badge_access': ['']  # New employees start with no badge access
        })
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(EMPLOYEES_FILE, index=False)
        
        return f"✅ Successfully added employee: {name} (alias: {alias}, date: {current_date}). No badge access granted yet."
    except Exception as e:
        return f"Error adding employee: {str(e)}"

def add_guest(
    first_name: Annotated[str, Field(description="The first name of the guest to add.")],
    last_name: Annotated[str, Field(description="The last name of the guest to add.")],
    alias: Annotated[str, Field(description="The alias/username for the guest.")],
) -> str:
    """Add a new guest to the guest dataset. Requires passkey approval."""
    try:
        full_name = f"{first_name} {last_name}"
        df = pd.read_csv(GUESTS_FILE)
        
        # Check if already exists
        if not df[df['name'].str.lower() == full_name.lower()].empty:
            return f"Guest '{full_name}' already exists in the database."
        
        # 🔐 REQUEST APPROVAL BEFORE WRITING
        if not request_approval_for_write_operation(
            "Add Guest",
            f"Add guest '{full_name}' with alias '{alias}' to the database"
        ):
            return f"❌ Operation cancelled: Adding guest '{full_name}' was not approved."
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Add new row
        new_row = pd.DataFrame({
            'name': [full_name],
            'alias': [alias],
            'date_accessed': [current_date]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(GUESTS_FILE, index=False)
        
        return f"✅ Successfully added guest: {full_name} (alias: {alias}, date: {current_date})"
    except Exception as e:
        return f"Error adding guest: {str(e)}"


def add_guest_with_auto_alias(
    first_name: Annotated[str, Field(description="The first name of the guest to add.")],
    last_name: Annotated[str, Field(description="The last name of the guest to add.")],
) -> str:
    """Add a new guest with an automatically generated alias. Use this for re-registering expired guests. Requires passkey approval."""
    try:
        full_name = f"{first_name} {last_name}"
        df = pd.read_csv(GUESTS_FILE)
        
        # Check if already exists
        if not df[df['name'].str.lower() == full_name.lower()].empty:
            return f"Guest '{full_name}' already exists in the database."
        
        # Auto-generate alias: first initial + last name + timestamp suffix
        timestamp_suffix = datetime.now().strftime("%m%d%H")
        base_alias = f"{first_name[0].lower()}{last_name.lower()}"
        auto_alias = f"{base_alias}{timestamp_suffix}"
        
        # Ensure alias is unique
        counter = 1
        final_alias = auto_alias
        while not df[df['alias'].str.lower() == final_alias.lower()].empty:
            final_alias = f"{auto_alias}{counter}"
            counter += 1
        
        # 🔐 REQUEST APPROVAL BEFORE WRITING
        if not request_approval_for_write_operation(
            "Re-register Expired Guest",
            f"Re-register guest '{full_name}' with auto-generated alias '{final_alias}'"
        ):
            return f"❌ Operation cancelled: Re-registering guest '{full_name}' was not approved."
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Add new row
        new_row = pd.DataFrame({
            'name': [full_name],
            'alias': [final_alias],
            'date_accessed': [current_date]
        })
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(GUESTS_FILE, index=False)
        
        return f"✅ Successfully re-registered guest: {full_name} with new auto-generated alias: {final_alias} (date: {current_date})"
    except Exception as e:
        return f"Error adding guest with auto alias: {str(e)}"


def generate_parking_code(
    alias: Annotated[str, Field(description="The alias/username of the employee requesting parking.")],
) -> str:
    """Generate a 6-digit parking validation code for an employee and save it to parking records. Requires passkey approval."""
    try:
        import random
        import string
        
        # Generate a random 6-character code (letters and numbers)
        characters = string.ascii_uppercase + string.digits
        parking_code = ''.join(random.choice(characters) for _ in range(6))
        
        # 🔐 REQUEST APPROVAL BEFORE WRITING
        if not request_approval_for_write_operation(
            "Generate Parking Code",
            f"Generate parking code '{parking_code}' for employee '{alias}'"
        ):
            return f"❌ Operation cancelled: Parking code generation for '{alias}' was not approved."
        
        # Get current date
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Load existing parking records
        try:
            df = pd.read_csv(PARKING_RECORDS_FILE)
        except FileNotFoundError:
            # Create new dataframe if file doesn't exist
            df = pd.DataFrame(columns=['alias', 'parking_code', 'date_issued'])
        
        # Add new parking record
        new_record = pd.DataFrame({
            'alias': [alias],
            'parking_code': [parking_code],
            'date_issued': [current_date]
        })
        df = pd.concat([df, new_record], ignore_index=True)
        df.to_csv(PARKING_RECORDS_FILE, index=False)
        
        return f"✅ Parking validation code generated: {parking_code}. Valid for {current_date}. Please enter this code in the ParkRTC app to access parking."
    except Exception as e:
        return f"Error generating parking code: {str(e)}"


def check_badge_access(
    alias: Annotated[str, Field(description="The alias/username of the employee to check badge access for.")],
) -> str:
    """Check which floors an employee has badge access to (floors 2-7). Note: Floor 1 is publicly accessible to everyone."""
    try:
        df = pd.read_csv(EMPLOYEES_FILE)
        result = df[df['alias'].str.lower() == alias.lower()]
        
        if result.empty:
            return f"Employee with alias '{alias}' not found in the database."
        
        employee = result.iloc[0]
        badge_access = str(employee.get('badge_access', ''))
        
        if badge_access and badge_access.strip():
            floors = badge_access.split(',')
            floors_list = ', '.join([f"Floor {f.strip()}" for f in floors if f.strip()])
            return f"Employee {employee['name']} (alias: {alias}) has badge access to: {floors_list}. Note: Floor 1 is publicly accessible to everyone."
        else:
            return f"Employee {employee['name']} (alias: {alias}) currently has NO badge access to restricted floors (2-7). Note: Floor 1 is publicly accessible to everyone."
    except Exception as e:
        return f"Error checking badge access: {str(e)}"


def update_badge_access(
    alias: Annotated[str, Field(description="The alias/username of the employee to update badge access for.")],
    floors: Annotated[str, Field(description="Comma-separated list of floor numbers (2-7) to grant access to. Example: '2,3,4' or '5,6,7'. Note: Floor 1 is publicly accessible and doesn't need badge access.")],
) -> str:
    """Update or add badge access floors for an employee (floors 2-7). This will ADD to existing access, not replace it. Floor 1 is publicly accessible."""
    try:
        df = pd.read_csv(EMPLOYEES_FILE)
        
        # Find the employee
        employee_idx = df[df['alias'].str.lower() == alias.lower()].index
        
        if employee_idx.empty:
            return f"Employee with alias '{alias}' not found in the database."
        
        idx = employee_idx[0]
        employee_name = df.loc[idx, 'name']
        
        # Parse requested floors
        requested_floors = set()
        for floor in floors.split(','):
            floor = floor.strip()
            if floor and floor.isdigit():
                floor_num = int(floor)
                if 1 <= floor_num <= 7:
                    requested_floors.add(str(floor_num))
        
        if not requested_floors:
            return "Invalid floor numbers. Please specify floors between 2 and 7. Note: Floor 1 is publicly accessible and doesn't require badge access."
        
        # Get existing access
        existing_access = str(df.loc[idx, 'badge_access'])
        existing_floors = set()
        if existing_access and existing_access.strip() and existing_access != 'nan':
            existing_floors = set(f.strip() for f in existing_access.split(',') if f.strip())
        
        # Combine existing and new floors
        all_floors = existing_floors.union(requested_floors)
        
        # Sort and format
        sorted_floors = sorted(list(all_floors), key=int)
        new_access_string = ','.join(sorted_floors)
        
        floors_list = ', '.join([f"Floor {f}" for f in sorted_floors])
        newly_added = requested_floors - existing_floors
        
        # 🔐 REQUEST APPROVAL BEFORE WRITING (only if there are new floors to add)
        if newly_added:
            added_list = ', '.join([f"Floor {f}" for f in sorted(newly_added, key=int)])
            if not request_approval_for_write_operation(
                "Update Badge Access",
                f"Grant {employee_name} ({alias}) access to: {added_list}. Total access will be: {floors_list}"
            ):
                return f"❌ Operation cancelled: Badge access update for '{employee_name}' was not approved."
        
        # Update the dataframe
        df.loc[idx, 'badge_access'] = new_access_string
        df.to_csv(EMPLOYEES_FILE, index=False)
        
        if newly_added:
            added_list = ', '.join([f"Floor {f}" for f in sorted(newly_added, key=int)])
            return f"✅ Successfully updated badge access for {employee_name} (alias: {alias}). Added: {added_list}. Total access now: {floors_list}"
        else:
            return f"{employee_name} (alias: {alias}) already had access to the requested floors. Current access: {floors_list}"
        
    except Exception as e:
        return f"Error updating badge access: {str(e)}"


def display_tool_execution_log(thought_process) -> None:
    """Display detailed tool execution information from the captured thought process."""
    if not thought_process or not thought_process.get("tool_calls"):
        print("\n⚠️  No tool calls were made in the last interaction.\n")
        return
    
    print("\n" + "="*70)
    print("🔍 AGENT REASONING & TOOL EXECUTION LOG")
    print("="*70)
    
    for i, tool_call in enumerate(thought_process["tool_calls"], 1):
        print(f"\n🔧 Step {i}: Called Tool '{tool_call['name']}'")
        
        if tool_call.get('server'):
            print(f"   📍 Server: {tool_call['server']}")
        
        # Display input arguments
        if tool_call.get('arguments'):
            try:
                args = json.loads(tool_call['arguments']) if isinstance(tool_call['arguments'], str) else tool_call['arguments']
                print(f"   📥 Input Parameters:")
                for key, value in args.items():
                    if value:  # Only show non-empty
                        print(f"      • {key}: {value}")
            except:
                print(f"   📥 Arguments: {tool_call['arguments']}")
        
        # Display output
        if tool_call.get('output'):
            output_str = str(tool_call['output'])
            if len(output_str) > 200:
                print(f"   📤 Output: {output_str[:200]}...")
            else:
                print(f"   📤 Output: {output_str}")
        
        # Display status
        if tool_call.get('status'):
            print(f"   ✅ Status: {tool_call['status']}")
    
    print("\n" + "="*70 + "\n")


async def run_user_check_agent() -> None:
    """Run the user access check agent with interactive conversation."""
    print("=== User Access Check Agent ===\n")
    print("💡 Tip: Type 'show' after any response to see tool execution details")
    print("💡 Tip: Type 'exit' or 'quit' to end the session\n")

    # Use DefaultAzureCredential which tries multiple authentication methods:
    # 1. Environment variables (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET)
    # 2. Managed Identity
    # 3. Azure CLI (az login)
    # 4. Visual Studio Code
    # 5. Azure PowerShell
    async with (
        DefaultAzureCredential() as credential,
        AzureAIAgentsProvider(credential=credential) as provider,
    ):
        # Get current date and time for context
        current_datetime = datetime.now()
        current_date_str = current_datetime.strftime("%Y-%m-%d")
        current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        
        agent = await provider.create_agent(
            name="UserAccessAgent",
            instructions=f"""You are a friendly access control assistant. 

CURRENT DATE AND TIME: {current_datetime_str}
CURRENT DATE: {current_date_str}

Your job is to:

1. Greet users warmly

2. Ask if they are an employee or a guest

3. EMPLOYEE WORKFLOW:
   - Ask for their ALIAS/USERNAME to check the employee database
   - Check if they exist in the employee database
   - If they exist, confirm their information
   - If they don't exist, ask for their full name and alias, then request approval to add them
   
4. GUEST WORKFLOW (30-DAY EXPIRATION POLICY):
   - Ask for their FIRST NAME and LAST NAME to check the guest database
   - Check if they exist in the guest database
   - Guest access expires after 30 days from their last access date
   - If the guest is found and NOT expired (less than 30 days since last access), confirm their information
   - If the guest is found but EXPIRED (more than 30 days since last access):
     * Inform them their access has expired and needs to be renewed
     * Explain that you will generate a new unique alias for them automatically
     * ASK FOR PERMISSION: "May I proceed with re-registering you in our system with a new auto-generated alias?"
     * Wait for user confirmation (yes/no)
     * If YES: Remove the expired guest using remove_expired_guest, then add them with a new auto-generated alias using add_guest_with_auto_alias
     * If NO: Thank them and let them know they'll need approval to proceed
     * After successful re-registration, inform them of their new auto-generated alias
   - If they don't exist at all, ask for their desired alias and request approval to add them using add_guest tool

5. PARKING VALIDATION (EMPLOYEES ONLY):
   - After confirming an employee is in the database (whether existing or newly added), ask: "Will you need parking today?"
   - If YES: Generate a parking validation code for them using their alias, and tell them to use it in the ParkRTC app
   - If NO: Respond with a friendly message and let them know they can proceed
   - IMPORTANT: NEVER offer parking validation to guests
   - If a guest asks about parking, apologetically inform them that parking validation is only available for employees

6. GUEST PARKING INFORMATION:
   - After confirming a guest is in the database (whether newly added or expired/re-registered), inform them: "For parking, please use the ParkRTC app to pay. Park in Zone 200 in the Purple Garage."
   - Guests must pay for their own parking via the ParkRTC app
   - Always mention Zone 200 and Purple Garage for guests

7. BADGE ACCESS MANAGEMENT (EMPLOYEES ONLY):
   - Microsoft Reston office has floors 1-7
   - FLOOR 1 is publicly accessible to EVERYONE (employees and guests) - NO badge access needed
   - Badge access is only required for floors 2-7
   - If an employee mentions needing badge access or asks about floor access:
     * Remind them that Floor 1 is always accessible to everyone
     * First check their current badge access using check_badge_access with their alias
     * If they need additional floor access (floors 2-7), ask which floors they need (if not already specified)
     * Valid floors for badge access are 2-7
     * Update their badge access using update_badge_access with their alias and the requested floors
     * Confirm the updated access with them
   - The update_badge_access tool ADDS to existing access, it does not replace it
   - IMPORTANT: Badge access is only for employees, never for guests
   - If a guest asks about floor access, inform them that Floor 1 is always accessible, but floors 2-7 are restricted to employees only

Be conversational and helpful. Always confirm before adding someone to the database.""",
            tools=[check_employee_exists, check_guest_exists, add_employee, add_guest, add_guest_with_auto_alias, generate_parking_code, remove_expired_guest, check_badge_access, update_badge_access],
        )

        print("Agent is ready! You can start chatting.\n")
        
        # Create a thread to maintain conversation history
        thread = agent.get_new_thread()
        last_thought_process = None  # Store last thought process for 'show' command
        
        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()
                
                # Check for exit commands
                if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                    print("\nAgent: Goodbye! Have a great day!")
                    break
                
                # Check for show command to display previous interaction details
                if user_input.lower() == 'show':
                    if last_thought_process:
                        display_tool_execution_log(last_thought_process)
                    else:
                        print("\n⚠️  No previous interaction to show.\n")
                    continue
                
                # Skip empty inputs
                if not user_input:
                    continue
                
                # Initialize thought process for this interaction
                thought_process = {
                    "tool_calls": [],
                    "reasoning": None
                }
                
                # Send message with thread to maintain conversation history
                print("Agent: ", end="", flush=True)
                result = await agent.run(user_input, thread=thread)
                
                # Extract tool calls from message contents
                if hasattr(result, 'messages'):
                    for message in result.messages:
                        if hasattr(message, 'contents'):
                            for content in message.contents:
                                # Capture function calls
                                if hasattr(content, 'type') and content.type == 'function_call':
                                    tool_call = {
                                        "name": getattr(content, 'name', 'Unknown'),
                                        "server": 'local',
                                        "arguments": getattr(content, 'arguments', None),
                                        "call_id": getattr(content, 'call_id', None),
                                        "status": 'completed',
                                        "output": None
                                    }
                                    thought_process["tool_calls"].append(tool_call)
                                
                                # Capture function results and match with calls
                                elif hasattr(content, 'type') and content.type == 'function_result':
                                    call_id = getattr(content, 'call_id', None)
                                    result_output = getattr(content, 'result', None)
                                    
                                    # Find matching tool call and update its output
                                    if call_id and result_output:
                                        for tool_call in thought_process["tool_calls"]:
                                            if tool_call.get("call_id") == call_id:
                                                tool_call["output"] = result_output
                                                break
                
                # Store thought process for 'show' command
                last_thought_process = thought_process if thought_process["tool_calls"] else None
                
                # AgentResponse object has a text property or can be converted to string
                response_text = str(result) if not hasattr(result, 'text') else result.text
                print(response_text)
                
                # Show hint about the 'show' command if tools were used
                if thought_process["tool_calls"]:
                    print("   💬 (Type 'show' to see tool execution details)\n")
                else:
                    print()
                
            except EOFError:
                # Handle Ctrl+D
                print("\n\nAgent: Goodbye! Have a great day!")
                break


async def main() -> None:
    """Main entry point for the user access check agent."""
    await run_user_check_agent()


if __name__ == "__main__":
    asyncio.run(main())
