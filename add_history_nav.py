# Add Payment History link to navbar
import re

with open('app/templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the profile dropdown menu and add Payment History link
# Look for the Dashboard link and add after it

payment_history_link = '''
                                <a href="/payment/history" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
                                    <i class="fas fa-history mr-2"></i> Payment History
                                </a>'''

# Find the Dashboard link in dropdown
pattern = r'(<a href="[^"]*dashboard[^"]*" class="block px-4 py-2[^>]*>[\s\S]*?</a>)'

def add_history_link(match):
    return match.group(0) + payment_history_link

content = re.sub(pattern, add_history_link, content, count=1)

with open('app/templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added Payment History link to navbar")
