import re

# Read the file
with open('ui.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Split into lines
lines = content.split('\n')
fixed_lines = []

for i, line in enumerate(lines):
    original_line = line

    # Skip comments and empty lines
    if line.strip().startswith('#') or not line.strip():
        fixed_lines.append(line)
        continue

    # Fix multiple statements separated by semicolons
    # But be careful not to break strings or complex expressions
    if ';' in line:
        # Count quotes to see if we're inside a string
        single_quotes = line.count("'")
        double_quotes = line.count('"')

        # If even number of quotes, we're not inside a string
        if single_quotes % 2 == 0 and double_quotes % 2 == 0:
            # Simple case: split by semicolon and put each statement on its own line
            parts = line.split(';')
            if len(parts) > 1:
                # Check if all parts after the first are just whitespace
                non_empty_parts = [p for p in parts if p.strip()]
                if len(non_empty_parts) > 1:
                    # Multiple statements - split them
                    indent = len(line) - len(line.lstrip())
                    indent_str = ' ' * indent

                    # First statement keeps original line
                    fixed_lines.append(parts[0].rstrip())

                    # Subsequent statements get their own lines
                    for part in parts[1:]:
                        if part.strip():
                            fixed_lines.append(indent_str + part.strip())
                else:
                    # Just remove trailing semicolon
                    fixed_lines.append(line.rstrip(';'))
            else:
                fixed_lines.append(line)
        else:
            # Inside a string, leave as is
            fixed_lines.append(line)
    else:
        fixed_lines.append(line)

# Write back
with open('ui.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(fixed_lines))

print("Fixed multiple statement issues in ui.py")