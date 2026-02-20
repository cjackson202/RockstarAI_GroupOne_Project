# 🔑 Quick Reference Card - Keep This Handy!

## Passkey
```
1234
```

## When Prompted
```
======================================================================
🔐 WRITE OPERATION APPROVAL REQUIRED
======================================================================
Enter passkey: 1234    <-- Type this and press Enter
```

## Operations That Require Passkey
- ✅ Add Employee
- ✅ Add Guest  
- ✅ Generate Parking Code
- ✅ Update Badge Access
- ✅ Remove Expired Guest
- ✅ Re-register Guest

## Operations That Don't Require Passkey
- ❌ Check Employee Exists (read-only)
- ❌ Check Guest Exists (read-only)
- ❌ Check Badge Access (read-only)

## Approval Function Pattern
```python
# In every write function, add this BEFORE df.to_csv():
if not request_approval_for_write_operation(
    "Operation Name",
    f"Description of what will be written"
):
    return "❌ Operation cancelled"
```

## Files
- Main Solution: `solution/agent.py`
- Starter Template: `agent_starter.py`
- Full Documentation: `PASSKEY_SYSTEM.md`
- Hackathon Guide: `README_HACKATHON.md`

---
*Pin this to your screen during the hackathon!*
