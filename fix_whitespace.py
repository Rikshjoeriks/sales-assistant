import re

# Read the file
with open('ui.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix trailing whitespace
fixed_lines = []
for line in lines:
    fixed_lines.append(line.rstrip() + '\n')

# Write back
with open('ui.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print("Fixed trailing whitespace in ui.py")