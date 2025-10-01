"""Extract first N profiles for testing."""
import json

# Read the fixed file
with open('profile_fixed.json', 'r', encoding='utf-8') as f:
    all_profiles = json.load(f)

# Extract first 10 profiles for testing
test_profiles = all_profiles[:10]

# Save to a test file
with open('profile_test_10.json', 'w', encoding='utf-8') as f:
    json.dump(test_profiles, f, indent=2)

print(f"✅ Created test file with {len(test_profiles)} profiles")
print(f"Test file: profile_test_10.json")
print(f"Full file has {len(all_profiles)} profiles remaining")

