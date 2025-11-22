# Quick script to add conditional around delivered badge
import re

with open('app/templates/dashboard/creator.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the delivered badge section
old_pattern = r"(\s+{% elif job\.status == 'delivered' %}\r?\n)(\s+<div class=\"bg-yellow-50 text-yellow-800 px-3 py-1 rounded text-sm\">\r?\n\s+<i class=\"fas fa-check-circle mr-1\"></i> Delivered - Awaiting approval\r?\n\s+</div>)"

new_content = r"\1                        {% set transaction = job_transactions.get(job.id) %}\r\n                        {% if not (transaction and transaction.customer_confirmed) %}\r\n\2\r\n                        {% endif %}"

content = re.sub(old_pattern, new_content, content)

with open('app/templates/dashboard/creator.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed! Delivered badge will now hide when customer confirms payment.")
