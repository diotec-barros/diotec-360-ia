#!/usr/bin/env python3
"""Fix BOM characters in Python files"""

files_to_fix = [
    'aethel/core/self_healing.py',
]

for filepath in files_to_fix:
    try:
        # Read as binary
        with open(filepath, 'rb') as f:
            content = f.read()
        
        # Remove all BOM occurrences
        content = content.replace(b'\xef\xbb\xbf', b'')
        
        # Write back as binary
        with open(filepath, 'wb') as f:
            f.write(content)
        
        print(f"Fixed: {filepath}")
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")

print("Done!")
