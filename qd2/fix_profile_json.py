"""Fix doubled quotes in profile JSON file."""

# Read the file
with open('profileerr.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace doubled quotes with single quotes
fixed_content = content.replace('""', '"')

# Write to a new file
with open('profile_fixed.json', 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("✅ Fixed! Output saved to: profile_fixed.json")
print(f"Original size: {len(content)} chars")
print(f"Fixed size: {len(fixed_content)} chars")

# Validate it's valid JSON
import json
try:
    data = json.loads(fixed_content)
    print(f"✅ Valid JSON! Found {len(data)} profile records")
except json.JSONDecodeError as e:
    print(f"❌ Still has JSON errors: {e}")

