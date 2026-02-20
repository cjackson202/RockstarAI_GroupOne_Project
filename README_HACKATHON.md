# 🎯 Access Control Agent Hackathon Challenge

## 🚀 Welcome, Agent Builders!

You've been hired by RockstarAI to build an intelligent access control system for the Microsoft Reston campus! Employees and guests are arriving, and they need an AI agent to manage building access, parking, and badge permissions. Can you build it in time?

---

## 🎮 The Mission

Build a conversational AI agent that:
- ✅ Verifies employees and guests against databases
- 🎫 Manages parking validation codes for employees
- 🏢 Controls badge access to building floors
- 👥 Handles guest registration with 30-day expiration
- 💬 Provides a friendly, natural conversation experience

---

## 📚 What You'll Learn

- **Foundry Agents Basics**: Create your first AI agent
- **Function Tools**: Give your agent superpowers with custom tools
- **State Management**: Use conversation threads and CSV databases
- **Approval Workflows**: Implement confirmation patterns
- **Azure Integration**: Connect to Azure AI services

---

## 🏗️ Project Structure

```
RockstarAI_GroupOne_Project/
├── agent_starter.py          # 👈 YOUR STARTING POINT (partial framework)
├── agent.py                  # 🎓 Reference solution (peek if stuck!)
├── data/
│   ├── employees.csv         # Employee database
│   ├── guests.csv            # Guest database (30-day validity)
│   └── parking_records.csv   # Parking code logs
├── requirements.txt          # Dependencies
└── README_HACKATHON.md      # 👈 You are here!
```

---

## 🎯 Challenge Levels

### 🟢 Level 1: The Foundation (30 mins)
**Goal**: Get a basic agent running that can have a conversation

**🎯 Step-by-Step Instructions:**

1️⃣ **Complete the conversation loop** (around line 324 in `agent_starter.py`):

Replace:
```python
print("Agent: [Your message here - implement agent.run() above!]")
```

With:
```python
# Send message to agent
print("Agent: ", end="", flush=True)
result = await agent.run(user_input, thread=thread)
print(str(result), "\n")
```

2️⃣ **Add your tools to the agent** (around line 291):

Replace:
```python
tools=[],  # TODO: Add your tools here!
```

With:
```python
tools=[check_employee_exists, check_guest_exists],
```

3️⃣ **Write better agent instructions** (around line 271). Replace the TODO comment with real instructions! Here's a starter:

```python
instructions=f"""You are a friendly access control assistant for Microsoft Reston campus.

CURRENT DATE AND TIME: {current_datetime_str}

Your job is to:
1. Greet users warmly and ask: "Are you an employee or a guest?"
2. For EMPLOYEES: Ask for their alias, then use check_employee_exists tool
3. For GUESTS: Ask for their first and last name, then use check_guest_exists tool
4. Be conversational and helpful!

Always confirm the information you find before proceeding.
""",
```

**🧪 Test it**: Run `python agent_starter.py` and try: "Hi, I'm an employee, alias jsmith"

**Success Criteria**: Agent responds and calls the tools! (Don't worry if tools fail - we fix that next!)

---

### 🟡 Level 2: Database Detective (45 mins)
**Goal**: Add tools to search employee and guest databases

**🎯 Step-by-Step Instructions:**

1️⃣ **Implement `check_employee_exists()`** (around line 82):

Replace the `pass` with:
```python
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
```

**💡 What's happening?**
- `pd.read_csv()` reads the CSV file into a DataFrame
- `df[df['alias'].str.lower() == alias.lower()]` filters rows where alias matches (case-insensitive!)
- `result.empty` checks if we found anything
- `.iloc[0]` gets the first (and only) matching row

2️⃣ **Implement `check_guest_exists()`** (around line 95):

Replace the `pass` with:
```python
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
            return f"Guest found but EXPIRED: {guest['name']} (alias: {guest['alias']}, last accessed: {guest['date_accessed']}, {days_since_access} days ago). Guest access has expired and must be re-registered."
        else:
            return f"Guest found: {guest['name']} (alias: {guest['alias']}, last accessed: {guest['date_accessed']}, {days_since_access} days ago)"
    else:
        return f"Guest '{full_name}' not found in the guest database."
except Exception as e:
    return f"Error checking guest database: {str(e)}"
```

**💡 What's happening?**
- We combine first and last names to search
- `pd.to_datetime()` converts date strings to datetime objects so we can do math
- `(current_date - last_accessed).days` calculates days since last access
- We return different messages for expired vs. active guests

**🧪 Test Cases**:
- Try: "Check if jsmith exists" → Should find John Smith
- Try: "Is Alice Cooper a guest?" → Should find her (check if expired!)

**Success Criteria**: Your agent can find employees and guests in the database!

---

### 🟠 Level 3: The Gatekeeper (45 mins)
**Goal**: Add new users with approval workflow

**🎯 Step-by-Step Instructions:**

**🔐 IMPORTANT:** Starting at this level, you're implementing **write operations**! All write functions must call `request_approval_for_write_operation()` before modifying CSV files. This is already implemented for you - just follow the pattern below.

1️⃣ **Implement `add_employee()`** (around line 112):

Replace the `pass` with:
```python
try:
    df = pd.read_csv(EMPLOYEES_FILE)
    
    # Check if already exists
    if not df[df['name'].str.lower() == name.lower()].empty:
        return f"Employee '{name}' already exists in the database."
    
    # 🔐 REQUEST APPROVAL BEFORE WRITING (This is the security check!)
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
    
    return f"✅ Successfully added employee: {name} (alias: {alias}, date: {current_date})"
except Exception as e:
    return f"Error adding employee: {str(e)}"
```

**💡 What's happening?**
- `pd.read_csv()` reads the CSV file into a DataFrame
- Check if the employee already exists (avoid duplicates!)
- **🔐 Request approval** - This will prompt you to enter passkey `1234` before writing
- If denied, return early with a cancellation message
- Create a new DataFrame with one row using a dictionary
- `pd.concat()` combines the original DataFrame with the new row
- `to_csv()` saves back to the file (index=False means don't save row numbers)

2️⃣ **Implement `add_guest()`** (around line 133):

Replace the `pass` with:
```python
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
```

3️⃣ **Add these tools to your agent** (around line 291):

Update your tools list:
```python
tools=[check_employee_exists, check_guest_exists, add_employee, add_guest],
```

4️⃣ **Update agent instructions** to handle adding users. Add this to your instructions:

```python
If a user is not found in the database:
- Ask if they want to be added
- For employees: You'll need their full name and desired alias
- For guests: You'll need first name, last name, and desired alias
- Always confirm before calling add_employee or add_guest
```

**🧪 Test Case**:
```
You: I'm an employee, alias tonystark
Agent: Not found... would you like me to add you?
You: Yes, my name is Tony Stark
Agent: [Function is called]
🔐 WRITE OPERATION APPROVAL REQUIRED
Enter passkey: 1234    <-- YOU type this
✅ APPROVED
Agent: Successfully added Tony Stark!
```

**Success Criteria**: 
- New users appear in the CSV files with today's date!
- You're prompted for passkey `1234` before each write
- You can deny operations by entering wrong passkey

📖 **Learn more about the approval system:** See [PASSKEY_SYSTEM.md](PASSKEY_SYSTEM.md)

---

### 🔴 Level 4: Parking Patrol (30 mins)
**Goal**: Generate parking codes for employees

**🎯 Step-by-Step Instructions:**

1️⃣ **Implement `generate_parking_code()`** (around line 150):

Replace the `pass` with:
```python
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
```

**💡 What's happening?**
- `string.ascii_uppercase` gives us "ABCDEFG..." and `string.digits` gives us "0123456789"
- `random.choice()` picks a random character
- We do this 6 times with a list comprehension and `join()` to make a string
- **🔐 Request approval** before saving the parking code
- We handle the case where parking_records.csv doesn't exist yet

2️⃣ **Add tool to agent** (around line 291):

```python
tools=[check_employee_exists, check_guest_exists, add_employee, add_guest, generate_parking_code],
```

3️⃣ **Update agent instructions**. Add this section:

```python
PARKING RULES:
- After confirming an EMPLOYEE (existing or newly added), ask: "Will you need parking today?"
- If YES: Use generate_parking_code with their alias
- For GUESTS: Tell them "For parking, please use the ParkRTC app to pay. Park in Zone 200 in the Purple Garage."
- IMPORTANT: Only employees get parking codes, guests must pay via app!
```

**🧪 Test Case**:
```
You: I'm jsmith
Agent: Employee found! Will you need parking today?
You: Yes
🔐 Enter passkey: 1234
Agent: ✅ Parking code: A7K9M2
```

**Success Criteria**: Employees get unique codes logged in parking_records.csv!

---

### 🟣 Level 5: Badge Boss (45 mins)
**Goal**: Manage building access for floors 2-7

**🎯 Step-by-Step Instructions:**

1️⃣ **Implement `check_badge_access()`** (around line 166):

Replace the `pass` with:
```python
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
        return f"Employee {employee['name']} has badge access to: {floors_list}. Note: Floor 1 is publicly accessible."
    else:
        return f"Employee {employee['name']} currently has NO badge access to restricted floors (2-7). Floor 1 is publicly accessible."
except Exception as e:
    return f"Error checking badge access: {str(e)}"
```

**💡 What's happening?**
- `.get('badge_access', '')` safely gets the column, defaulting to empty string if missing
- `.split(',')` splits "2,3,4" into ["2", "3", "4"]
- List comprehension formats each floor number nicely

2️⃣ **Implement `update_badge_access()`** (around line 179):

Replace the `pass` with:
```python
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
            if 2 <= floor_num <= 7:
                requested_floors.add(str(floor_num))
    
    if not requested_floors:
        return "Invalid floor numbers. Please specify floors between 2 and 7."
    
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
            return f"✅ Successfully updated badge access for {employee_name}. Total access now: {floors_list}"
        else:
            return f"{employee_name} (alias: {alias}) already had access to the requested floors. Current access: {floors_list}"
    
except Exception as e:
    return f"Error updating badge access: {str(e)}"
```

**💡 What's happening?**
- We use sets (unique collections) to merge existing and new floor access
- `.union()` combines two sets without duplicates
- We validate floors are between 2-7 (Floor 1 is public!)
- **🔐 Request approval** only if there are NEW floors to add (don't require approval if they already have access)
```

4️⃣ **Update agent instructions** with:

```python
BADGE ACCESS MANAGEMENT (Employees only):
- Floor 1 is publicly accessible to EVERYONE (no badge needed)
- Floors 2-7 require badge access (employees only)
- If employee asks about floor access, use check_badge_access first
- To grant access, use update_badge_access (this ADDS floors, doesn't replace)
- Example: If employee has floors 2,3 and requests floor 5, they'll have 2,3,5
```

**🧪 Test Case**:
```
You: I'm jsmith, what floors can I access?
Agent: [Shows current badge access]
You: I need access to floor 6
Agent: [Adds floor 6 to existing access]
```

**Success Criteria**: Badge access is updated in employees.csv!

---

### ⚫ Level 6: The Expert (30 mins)
**Goal**: Handle edge cases and add polish

**🎯 Step-by-Step Instructions:**

1️⃣ **Implement `remove_expired_guest()`** (around line 200):

Replace the `pass` with:
```python
try:
    full_name = f"{first_name} {last_name}"
    
    # 🔐 REQUEST APPROVAL BEFORE REMOVING
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
        return f"✅ Expired guest '{full_name}' has been removed from the database."
    else:
        return f"Guest '{full_name}' not found in the database."
except Exception as e:
    return f"Error removing expired guest: {str(e)}"
```

2️⃣ **Implement `add_guest_with_auto_alias()`** (around line 215):

Replace the `pass` with:
```python
try:
    full_name = f"{first_name} {last_name}"
    df = pd.read_csv(GUESTS_FILE)
    
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
    
    return f"✅ Successfully re-registered guest: {full_name} with new auto-generated alias: {final_alias}"
except Exception as e:
    return f"Error adding guest with auto alias: {str(e)}"
```

**💡 What's happening?**
- `datetime.now().strftime("%m%d%H")` creates a timestamp like "021914" (Feb 19, 2pm)
- We generate alias like "tstarks021914" for Tony Stark
- We check if it's unique and add a counter if needed
- **🔐 Request approval** before re-registering the guest

3️⃣ **Add tools to agent** (around line 245):

```python
tools=[check_employee_exists, check_guest_exists, add_employee, add_guest, 
       generate_parking_code, check_badge_access, update_badge_access,
       remove_expired_guest, add_guest_with_auto_alias],
```

4️⃣ **Update agent instructions** with expiration handling:

```python
GUEST EXPIRATION (30-day policy):
- When checking a guest, if they're expired (>30 days since last access):
  * Inform them their access expired and needs renewal
  * Explain you'll generate a new unique alias automatically
  * Ask: "May I proceed with re-registering you with a new auto-generated alias?"
  * If YES: First use remove_expired_guest, then use add_guest_with_auto_alias
  * Inform them of their new alias after re-registration
```

**🧪 Test Case**: Find a guest from January in guests.csv and test expiration! You'll be prompted for passkey twice (once to remove, once to re-add).

**Success Criteria**: Expired guests can be re-registered with new aliases!

---

## 🚀 Quick Start

### Prerequisites
```powershell
# 1. Make sure you have Python 3.8+
python --version

# 2. Log in to Azure (for authentication)
az login
```

### Setup Steps
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start with the starter template
python agent_starter.py

# 3. Build out the TODOs in the file!
```

### 🔐 Important: Approval System
This project includes a **passkey-protected approval system**! Before any data is written to CSV files, you must enter the passkey:

**PASSKEY: `1234`**

When the agent tries to add an employee, generate a parking code, or modify data, you'll see:
```
======================================================================
🔐 WRITE OPERATION APPROVAL REQUIRED
======================================================================
Operation: Add Employee
Details: Add employee 'John Doe' with alias 'jdoe'
Enter passkey: 1234    <-- Type this!
======================================================================
```

**📖 Full documentation:** See [PASSKEY_SYSTEM.md](PASSKEY_SYSTEM.md) for details.

**💡 Why?** This prevents accidental data corruption and gives you full control during demos!

---

## 📊 Your Databases

### employees.csv
Contains 10 employees with:
- `name`: Full name
- `alias`: Username (e.g., "jsmith")
- `date_accessed`: Last access date
- `badge_access`: Comma-separated floors (e.g., "2,3,4")

**Sample**: John Smith, jsmith, 2026-02-15, 2,3,4

### guests.csv  
Contains 10 guests with:
- `name`: Full name
- `alias`: Username
- `date_accessed`: Last access date (30-day expiration!)

**Sample**: Alice Cooper, acooper, 2026-01-10

### parking_records.csv
Logs parking codes:
- `alias`: Who got the code
- `parking_code`: 6-char code (e.g., "A7K2M9")
- `date_issued`: When it was issued

---

## 🧪 Test Scenarios

Try these conversations to test your agent:

### Scenario 1: Existing Employee
```
You: Hi!
Agent: [Greeting] Are you an employee or guest?
You: Employee
Agent: [Asks for alias]
You: jsmith
Agent: [Confirms John Smith exists]
Agent: Will you need parking today?
You: Yes
Agent: [Generates parking code]
```

### Scenario 2: New Guest
```
You: I'm a guest
Agent: [Asks for name]
You: Tony Stark
Agent: [Not found, asks if they want to add]
You: Yes, alias tstark
Agent: [Adds guest]
Agent: [Provides parking info for Zone 200]
```

### Scenario 3: Expired Guest (30+ days)
```
You: I'm a guest
Agent: [Asks for name]
You: [Name of guest from Jan 10]
Agent: [Detects expiration]
Agent: [Offers to re-register with new alias]
You: Yes
Agent: [Re-registers with auto-generated alias]
```

### Scenario 4: Badge Access
```
You: I'm jsmith
Agent: [Confirms employee]
You: What floors can I access?
Agent: [Shows current badge access]
You: I need access to floor 5
Agent: [Updates badge access]
```

---

## 💡 Pro Tips & Cheat Sheet

### 🎓 Foundry Agent Basics
- **agent.run()**: Sends a message and gets a response
- **thread**: Maintains conversation history across messages
- **tools**: Functions you give to the agent (with @annotated parameters!)
- **instructions**: The agent's personality and rules (be specific!)

### 🛠️ Function Tool Template
```python
def my_tool(
    param: Annotated[str, Field(description="What this parameter is for")],
) -> str:
    """What this tool does - be descriptive!"""
    # Your logic here
    return "result"
```

### 📊 CSV Operations with Pandas (Your Best Friend!)
```python
import pandas as pd

# Read a CSV file
df = pd.read_csv("file.csv")

# Search (case-insensitive) - finds all matching rows
result = df[df['column'].str.lower() == value.lower()]

# Check if we found anything
if result.empty:
    print("Not found!")
else:
    row = result.iloc[0]  # Get the first matching row
    print(row['column_name'])

# Add a new row
new_row = pd.DataFrame({'col1': [val1], 'col2': [val2]})
df = pd.concat([df, new_row], ignore_index=True)

# Update a specific cell
df.loc[row_index, 'column_name'] = new_value

# Save back to CSV (index=False means don't save row numbers)
df.to_csv("file.csv", index=False)
```

### 📅 Date Handling Made Easy
```python
from datetime import datetime

# Get current date as string
current_date = datetime.now().strftime("%Y-%m-%d")  # "2026-02-19"

# Calculate days difference
import pandas as pd
date1 = pd.to_datetime("2026-01-10")
date2 = pd.to_datetime("2026-02-19")
days_diff = (date2 - date1).days  # 40 days

# Generate timestamp for unique codes
timestamp = datetime.now().strftime("%m%d%H")  # "021914"
```

### 🎲 Random Code Generation
```python
import random
import string

# Generate random 6-character alphanumeric code
characters = string.ascii_uppercase + string.digits  # "ABCD...0123456789"
code = ''.join(random.choice(characters) for _ in range(6))
# Result: "A7K9M2" (different each time!)
```

### 🔍 Common Patterns You'll Need

**Pattern 1: Search and return info**
```python
df = pd.read_csv(FILE_PATH)
result = df[df['column'].str.lower() == search_term.lower()]
if not result.empty:
    return f"Found: {result.iloc[0]['name']}"
else:
    return "Not found"
```

**Pattern 2: Check if exists before adding**
```python
df = pd.read_csv(FILE_PATH)
if not df[df['name'].str.lower() == name.lower()].empty:
    return "Already exists!"
# ... proceed with adding
```

**Pattern 3: Add new row to CSV**
```python
new_row = pd.DataFrame({
    'column1': [value1],
    'column2': [value2],
})
df = pd.concat([df, new_row], ignore_index=True)
df.to_csv(FILE_PATH, index=False)
```

**Pattern 4: Update existing row**
```python
# Find the row
idx = df[df['alias'] == alias].index[0]
# Update it
df.loc[idx, 'column_name'] = new_value
# Save
df.to_csv(FILE_PATH, index=False)
```

---

## 🎯 Scoring Guide

| Challenge | Points | Description |
|-----------|--------|-------------|
| Level 1 | 10 pts | Basic agent runs and greets |
| Level 2 | 20 pts | Database search tools work |
| Level 3 | 20 pts | Can add new users with approval |
| Level 4 | 15 pts | Parking codes for employees |
| Level 5 | 20 pts | Badge access management |
| Level 6 | 15 pts | Guest expiration + polish |
| **BONUS** | +10 pts | Creative enhancements! |

**Total**: 100 points (+10 bonus)

---

## 🎨 Bonus Challenges

Once you've completed the core challenges, try these:

1. **🎭 Personality Plus**: Give your agent a fun personality (security guard, butler, robot?)
2. **📈 Analytics Dashboard**: Show statistics (total employees, guests, parking codes today)
3. **🔔 Notifications**: Simulate sending welcome emails when adding users
4. **⏰ Time-based Rules**: Different behavior for business hours vs. after-hours
5. **🎨 Rich Formatting**: Add emojis, colors, or formatted output
6. **🔐 Security Levels**: Different access levels (visitor, contractor, employee, admin)

---

## 🐛 Troubleshooting & Debug Tips

### "Cannot find agent_framework"
```powershell
pip install agent-framework==1.0.0b260123
```

### "Azure authentication failed"
```powershell
az login
# Or set environment variables:
# AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET
```

### "CSV file not found"
Make sure you're running from the project root directory:
```powershell
cd C:\src\RockstarAI_GroupOne_Project
python agent_starter.py
```

### "Agent isn't using my tools"
- ✅ Check tool descriptions are clear and specific
- ✅ Make sure tools are in the agent's `tools=[...]` list
- ✅ Add explicit instructions about when to use each tool
- ✅ Test the tool function independently first (call it directly in Python)

### "My tool is returning an error"
Add print statements or try/except blocks:
```python
def my_tool(param: str) -> str:
    try:
        print(f"Tool called with: {param}")  # Debug output
        df = pd.read_csv(FILE_PATH)
        print(f"Found {len(df)} rows")  # Debug output
        # ... rest of code
        return result
    except Exception as e:
        print(f"ERROR: {e}")  # See the actual error
        return f"Error: {str(e)}"
```

### "Agent gives weird responses"
- Your instructions might be unclear or contradictory
- Try simplifying your instructions
- Be more specific about the exact steps
- Look at the example instructions in this README

### "Pandas says 'KeyError: column_name'"
The column doesn't exist in your CSV. Check spelling:
```python
df = pd.read_csv("file.csv")
print(df.columns)  # See all column names
```

### "The agent keeps asking the same question"
Your tool might not be returning the right information. Check:
- Is your function returning a clear string?
- Does the return message make sense?
- Try running the function directly to see what it returns

### 🔬 Quick Testing Trick
Test your functions WITHOUT the agent first:
```python
# At the bottom of agent_starter.py, add:
if __name__ == "__main__":
    # Test your functions before running the agent
    print(check_employee_exists("jsmith"))
    print(check_guest_exists("Alice", "Cooper"))
    
    # Then comment these out and run the agent
    # asyncio.run(main())
```

### 🎯 Common Newbie Mistakes
1. **Forgetting to return a string** - Tools MUST return strings!
2. **Case sensitivity** - Use `.str.lower()` for searches
3. **Empty DataFrames** - Always check `if result.empty` before using `.iloc[0]`
4. **Wrong file paths** - Use the DATA_DIR constants provided
5. **Forgetting index=False** - When saving CSV: `df.to_csv(file, index=False)`
6. **Not handling exceptions** - Wrap your code in try/except blocks!

### 💪 Getting Unstuck Checklist
- [ ] Read the error message carefully (it usually tells you what's wrong!)
- [ ] Check the reference implementation in `agent.py`
- [ ] Print debug statements in your functions
- [ ] Test functions independently before adding to agent
- [ ] Make sure CSV files exist in the `data/` folder
- [ ] Verify you're using the right column names
- [ ] Check that your instructions tell the agent when to use tools
- [ ] Ask a teammate or mentor - fresh eyes help!

---

## � Complete Agent Instructions Example

Still stuck on writing good agent instructions? Here's a complete example you can use as a starting point:

```python
agent = await provider.create_agent(
    name="UserAccessAgent",
    instructions=f"""You are a friendly and professional access control assistant for the Microsoft Reston campus.

CURRENT DATE AND TIME: {current_datetime_str}
CURRENT DATE: {current_date_str}

=== YOUR JOB ===
Manage building access, parking, and badge permissions for employees and guests.

=== WORKFLOW ===

1. INITIAL GREETING
   - Greet warmly and ask: "Are you an employee or a guest?"

2. EMPLOYEE WORKFLOW
   - Ask for their alias/username
   - Use check_employee_exists with their alias
   - If NOT FOUND: Ask for full name and desired alias, then use add_employee
   - After confirming employee (found or added):
     * Ask: "Will you need parking today?"
     * If YES: Use generate_parking_code with their alias
     * If they ask about floor access: Use check_badge_access, then update_badge_access if needed

3. GUEST WORKFLOW
   - Ask for their first name and last name
   - Use check_guest_exists with first_name and last_name
   - Check the response for expiration status:
     * If EXPIRED (>30 days): 
       - Inform them access expired
       - Ask: "May I re-register you with a new auto-generated alias?"
       - If YES: Use remove_expired_guest, then add_guest_with_auto_alias
       - Tell them their new alias
     * If NOT FOUND: Ask for desired alias, then use add_guest
   - After confirming guest: Tell them "For parking, please use the ParkRTC app. Park in Zone 200 in the Purple Garage."

=== IMPORTANT RULES ===
- Only EMPLOYEES get parking validation codes
- Guests must use ParkRTC app for parking (Zone 200, Purple Garage)
- Floor 1 is publicly accessible to everyone (no badge needed)
- Floors 2-7 require badge access (employees only)
- Guest access expires after 30 days
- Always be conversational and confirm information before taking actions
- When adding users, confirm all details first

=== BADGE ACCESS ===
- Use check_badge_access to show current floor access
- Use update_badge_access to grant new floors (this ADDS floors, doesn't replace)
- Valid floors for badges: 2, 3, 4, 5, 6, 7
- Always remind users that Floor 1 is public

Be helpful, friendly, and professional!""",
    tools=[
        check_employee_exists,
        check_guest_exists,
        add_employee,
        add_guest,
        generate_parking_code,
        check_badge_access,
        update_badge_access,
        remove_expired_guest,
        add_guest_with_auto_alias,
    ],
)
```

**💡 Tips for Great Instructions:**
1. ✅ Be specific about the SEQUENCE of actions
2. ✅ Tell the agent WHEN to use each tool
3. ✅ Include RULES and POLICY information
4. ✅ Add personality with tone guidance
5. ✅ Use formatting (=== headers ===, bullets, etc.) for clarity
6. ❌ Don't be vague ("help users" is too generic)
7. ❌ Don't forget edge cases (expired guests, duplicates, etc.)

---

## �📚 Resources

- [MSFT Agent Framework](https://github.com/microsoft/agent-framework/tree/main)

---

## 🏆 Winning Tips

1. **Start Simple**: Get Level 1 working before moving on
2. **Test Often**: Run your agent after each function you add
3. **Read Errors**: Error messages tell you what's wrong!
4. **Use the Solution**: `agent.py` is there if you get stuck (no shame!)
5. **Be Creative**: Add your own twist to make it memorable
6. **Ask Questions**: This is a learning experience!
7. **Have Fun**: You're building AI agents - how cool is that?!

---

## 🎉 Presentation Ideas

When demoing your project:
- Show a live conversation with your agent
- Demonstrate error handling (try breaking it!)
- Show the CSV files updating in real-time
- Explain one interesting technical challenge you solved
- Share your favorite part of the implementation

---

## ⏱️ Suggested Timeline

- **00:00 - 00:15**: Setup and understand the project
- **00:15 - 00:45**: Level 1 - Basic agent
- **00:45 - 01:30**: Level 2 - Database tools
- **01:30 - 02:15**: Level 3 - Add users
- **02:15 - 02:45**: Level 4 - Parking
- **02:45 - 03:30**: Level 5 - Badge access
- **03:30 - 04:00**: Level 6 - Polish & testing
- **04:00 - 04:30**: Bonus features & prep demo

**Total**: ~4-4.5 hours

---

## 🙋 Need Help?

1. Check `agent.py` for reference implementation
2. Review the instruction files:
   - `gsam_agent_instructions.txt` - GSAM agent logic
   - `Parking_agent_instructions.txt` - Parking logic
3. Ask your teammates!
4. Search error messages
5. Try the test scenarios above

---

## � Victory Checklist - Did You Complete Everything?

Use this checklist to track your progress and make sure you've built all the features!

### 🟢 Level 1: Foundation
- [ ] Agent runs without crashing
- [ ] Agent responds to messages
- [ ] Agent asks "Are you an employee or guest?"
- [ ] Conversation loop works (can type multiple messages)
- [ ] Exit commands work (quit, exit)

### 🟡 Level 2: Database Detective  
- [ ] `check_employee_exists()` works
- [ ] Can find existing employees by alias
- [ ] `check_guest_exists()` works
- [ ] Can find existing guests by name
- [ ] 30-day expiration check works for guests
- [ ] Agent reports "not found" correctly

### 🟠 Level 3: The Gatekeeper
- [ ] `add_employee()` works
- [ ] New employees appear in employees.csv
- [ ] `add_guest()` works
- [ ] New guests appear in guests.csv
- [ ] Current date is recorded automatically
- [ ] Agent asks for confirmation before adding

### 🔴 Level 4: Parking Patrol
- [ ] `generate_parking_code()` works
- [ ] Parking codes are random and unique
- [ ] Codes saved to parking_records.csv
- [ ] Employees get parking codes
- [ ] Guests are told to use ParkRTC app
- [ ] Zone 200 and Purple Garage mentioned for guests

### 🟣 Level 5: Badge Boss
- [ ] `check_badge_access()` works
- [ ] Shows current floor access for employees
- [ ] `update_badge_access()` works
- [ ] Can grant access to floors 2-7
- [ ] Floors are added (not replaced)
- [ ] Agent mentions Floor 1 is public

### ⚫ Level 6: The Expert
- [ ] `remove_expired_guest()` works
- [ ] `add_guest_with_auto_alias()` works
- [ ] Auto-generated aliases are unique
- [ ] Expired guests can be re-registered
- [ ] Agent handles expiration workflow smoothly
- [ ] Error handling is robust

### 🎨 Bonus Features
- [ ] Added custom personality to agent
- [ ] Improved error messages
- [ ] Added extra features (analytics, notifications, etc.)
- [ ] Polished the user experience
- [ ] Tested edge cases thoroughly

### 🎉 Final Checks
- [ ] All CSV files update correctly
- [ ] No crashes or unhandled errors
- [ ] Agent instructions are clear and comprehensive
- [ ] Code is commented and readable
- [ ] Ready to demo!

**Score**: ____ / 100 points (+ bonus!)

---

## �🎊 Ready to Begin?

Open `agent_starter.py` and start building! Remember:
- **Read** the TODOs carefully
- **Test** after each implementation
- **Celebrate** small wins
- **Learn** from mistakes
- **Have fun** building AI!

Good luck, and may your agents be intelligent and your parking codes random! 🚀🤖

---

*Built with ❤️ by RockstarAI Team for the Microsoft Foundry Agent Hackathon*
