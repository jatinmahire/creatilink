# Add dispute functionality to creator and customer dashboards
import re

# Update Creator Dashboard
with open('app/templates/dashboard/creator.html', 'r', encoding='utf-8') as f:
    creator_content = f.read()

# Add "Raise Dispute" button after payment buttons
dispute_button = '''
                        <div class="mt-2">
                            <button onclick="openDisputeModal({{ transaction.id }})" 
                                    class="text-red-600 hover:text-red-800 text-xs inline-flex items-center">
                                <i class="fas fa-exclamation-triangle mr-1"></i> Raise Dispute
                            </button>
                        </div>'''

# Add after the "Received/Not Received" buttons section
pattern = r'(</div>\s*</div>\s*{% elif transaction\.creator_confirmed %})'
creator_content = re.sub(pattern, dispute_button + r'\n\1', creator_content, count=1)

with open('app/templates/dashboard/creator.html', 'w', encoding='utf-8') as f:
    f.write(creator_content)

# Update Customer Dashboard
with open('app/templates/dashboard/customer.html', 'r', encoding='utf-8') as f:
    customer_content = f.read()

# Add "Raise Dispute" button for customers too
customer_content = re.sub(pattern, dispute_button + r'\n\1', customer_content, count=1)

with open('app/templates/dashboard/customer.html', 'w', encoding='utf-8') as f:
    f.write(customer_content)

print("✅ Added dispute buttons to dashboards")
