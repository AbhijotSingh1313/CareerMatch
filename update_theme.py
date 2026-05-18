import os
import glob
import re

CSS_FILES = glob.glob('frontend/src/**/*.css', recursive=True) + glob.glob('frontend/src/**/*.jsx', recursive=True)

REPLACEMENTS = {
    # Indigo/Purple -> Green Palette
    '#6366f1': 'var(--palm-leaf)',
    '#4f46e5': 'var(--dusty-olive)',
    '#eef2ff': 'var(--frosted-mint)',
    '#c7d2fe': 'var(--tea-green)',
    '#818cf8': 'var(--muted-olive-2)',
    '#8b5cf6': 'var(--muted-olive)',
    '#a855f7': 'var(--muted-olive-2)',
    '#c084fc': 'var(--tea-green)',
    '#faf5ff': 'var(--frosted-mint)',
    'rgba(99, 102, 241': 'rgba(135, 152, 106',
    'rgba(99,102,241': 'rgba(135,152,106',
    'rgba(129, 140, 248': 'rgba(151, 169, 124',
    'rgba(129,140,248': 'rgba(151,169,124',
    'rgba(168, 85, 247': 'rgba(181, 201, 154',
    'rgba(168,85,247': 'rgba(181,201,154',
    'rgba(192, 132, 252': 'rgba(207, 225, 185',
    'rgba(192,132,252': 'rgba(207,225,185',
    # Dark Mode highlights
    '#1a1a2e': '#1f2924',
    '#2d2d5e': '#2c352d',
    '#2d2b50': '#2c352d',
}

for fp in CSS_FILES:
    with open(fp, 'r', encoding='utf-8') as f:
        content = f.read()
    
    orig = content
    for old, new in REPLACEMENTS.items():
        if old.startswith('#'):
            content = re.sub(old, new, content, flags=re.IGNORECASE)
        else:
            content = content.replace(old, new)
            
    if content != orig:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {fp}")

