# Add screenshot display to creator dashboard
import re

with open('app/templates/dashboard/creator.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the payment status section where customer has paid
# Add screenshot link after the "Customer Paid" message

screenshot_display = '''
                        {% if transaction.payment_screenshot %}
                        <div class="mt-2">
                            <a href="/static/{{ transaction.payment_screenshot }}" 
                               target="_blank" 
                               class="text-blue-600 hover:text-blue-800 text-xs inline-flex items-center">
                                <i class="fas fa-image mr-1"></i> View Payment Screenshot
                            </a>
                        </div>
                        {% endif %}'''

# Find the section after "Check your UPI app and confirm"
pattern = r'(<p class="text-xs text-yellow-600 mb-2">Check your UPI app and confirm</p>)'

def add_screenshot(match):
    return match.group(0) + screenshot_display

content = re.sub(pattern, add_screenshot, content)

# Also add to the "Received" section
screenshot_display_received = '''
                        {% if transaction.payment_screenshot %}
                        <a href="/static/{{ transaction.payment_screenshot }}" 
                           target="_blank" 
                           class="text-blue-600 hover:text-blue-800 text-xs inline-flex items-center mt-1 block">
                            <i class="fas fa-file-image mr-1"></i> View Screenshot
                        </a>
                        {% endif %}'''

# Add after the "Received" amount display
pattern2 = r'(<div class="text-green-700 text-sm font-semibold">✅ Received: &#8377;{{ transaction\.amount }}</div>)'

def add_screenshot_received(match):
    return match.group(0) + screenshot_display_received

content = re.sub(pattern2, add_screenshot_received, content)

with open('app/templates/dashboard/creator.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added screenshot display to creator dashboard")
