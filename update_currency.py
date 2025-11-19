"""
Script to update all currency symbols from $ to  ₹ in templates
"""

import os
import re

TEMPLATES_DIR = "app/templates"

def update_currency_in_file(filepath):
    """Update currency symbols in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace ${{ with ₹{{
    updated = content.replace('${{', '₹{{')
    
    # Replace "Budget (USD)" with "Budget (INR)"
    updated = updated.replace('Budget (USD)', 'Budget (INR)')
    
    # Update placeholder from 500 to 5000
    updated = updated.replace('placeholder="500"', 'placeholder="5000"')
    
    if content != updated:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(updated)
        return True
    return False

def main():
    """Update all template files"""
    count = 0
    for root, dirs, files in os.walk(TEMPLATES_DIR):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                if update_currency_in_file(filepath):
                    print(f"✓ Updated: {filepath}")
                    count += 1
    
    print(f"\n{'='*60}")
    print(f"Updated currency in {count} files!")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
