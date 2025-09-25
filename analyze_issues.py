import subprocess
import os

files = [
    'ui.py', 'learning_sequential_mega.py', 'sequential_mega_matcher.py',
    'mega_matcher.py', 'intelligent_matcher.py', 'consensus_matcher.py',
    'enhanced_dictionary.py', 'feature_dictionary.py', 'text_normalizer.py',
    'run_dual_pipeline.py', 'run_pipeline.py', 'run_intelligent_match.py',
    'setup_api_key.py', 'build_exe.py'
]

results = []
for file in files:
    if os.path.exists(file):
        result = subprocess.run(['python', '-m', 'pylint', file, '--reports=no', '--score=no'],
                              capture_output=True, text=True)
        issue_count = len([line for line in result.stdout.split('\n') if line.strip() and not line.startswith('*')])
        results.append((file, issue_count))

results.sort(key=lambda x: x[1], reverse=True)
print("=== ISSUE COUNT BY FILE ===")
for file, count in results:
    print(f'{file}: {count} issues')

print("\n=== DETAILED ANALYSIS OF ui.py ===")
if os.path.exists('ui.py'):
    result = subprocess.run(['python', '-m', 'pylint', 'ui.py', '--reports=no', '--score=no'],
                          capture_output=True, text=True)
    lines = [line for line in result.stdout.split('\n') if line.strip() and not line.startswith('*')]

    categories = {}
    for line in lines:
        if ':' in line:
            parts = line.split(':')
            if len(parts) >= 3:
                code = parts[2].split()[0] if len(parts[2].split()) > 0 else 'unknown'
                categories[code] = categories.get(code, 0) + 1

    sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
    print("Top issue categories in ui.py:")
    for code, count in sorted_categories[:10]:
        # Extract the issue description from the first occurrence
        desc = "unknown"
        for line in lines:
            if f':{code}:' in line:
                parts = line.split(f':{code}:')
                if len(parts) > 1:
                    desc = parts[1].split('(')[0].strip()
                    break
        print(f'  {code}: {count} issues - {desc}')