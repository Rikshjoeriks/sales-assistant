import subprocess

# Get the specific lines with multiple statement issues
result = subprocess.run(['python', '-m', 'pylint', 'ui.py', '--reports=no', '--score=no'],
                      capture_output=True, text=True)
lines = [line for line in result.stdout.split('\n') if 'More than one statement' in line]

print(f"Found {len(lines)} multiple statement issues:")
for line in lines[:10]:  # Show first 10
    print(line)

# Read the file to fix the issues
with open('ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Common patterns to fix:
# 1. Lines ending with semicolons
# 2. Multiple statements separated by semicolons

lines = content.split('\n')
fixed_lines = []

for line in lines:
    # Remove trailing semicolons (but keep them if they're in strings or comments)
    if line.strip().endswith(';') and not line.strip().startswith('#'):
        # Check if it's inside a string by counting quotes
        single_quotes = line.count("'")
        double_quotes = line.count('"')
        if (single_quotes % 2 == 0) and (double_quotes % 2 == 0):  # Not inside a string
            line = line.rstrip(';')

    # Handle multiple statements (basic case - split by semicolon)
    if ';' in line and not line.strip().startswith('#'):
        # Simple case: split by semicolon if not in strings
        parts = line.split(';')
        if len(parts) == 2 and parts[1].strip() == '':
            # Just remove the semicolon
            line = parts[0]
        # More complex cases would need manual review

    fixed_lines.append(line)

# Write back
with open('ui.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("Attempted to fix multiple statement issues")