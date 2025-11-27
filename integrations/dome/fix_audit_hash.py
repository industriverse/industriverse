# Fix the audit trail hash calculation
with open('src/industrial/compliance_export.py', 'r') as f:
    content = f.read()

# Replace the problematic line
old_line = 'entry_string = json.dumps(audit_entry, sort_keys=True, default=str)'
new_lines = '''entry_copy = {k: v for k, v in audit_entry.items() if k != "hash"}
        entry_string = json.dumps(entry_copy, sort_keys=True, default=str)'''

content = content.replace(old_line, new_lines)

with open('src/industrial/compliance_export.py', 'w') as f:
    f.write(content)

print("✅ Fixed audit trail hash calculation")
