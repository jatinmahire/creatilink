# Restore creator.html with payment UI and conditional badge hiding
import shutil

# Copy the good version
shutil.copy('temp_creator.html', 'app/templates/dashboard/creator.html')

# Now read and add the conditional around delivered badge
with open('app/templates/dashboard/creator.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line with "Delivered - Awaiting approval" and add conditional
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # Check if this is the delivered status line
    if "{% elif job.status == 'delivered' %}" in line:
        new_lines.append(line)  # Add the elif line
        i += 1
        # Add transaction check
        new_lines.append("                        {% set transaction = job_transactions.get(job.id) %}\n")
        new_lines.append("                        {% if not (transaction and transaction.customer_confirmed) %}\n")
        # Add the next 3 lines (the div with badge)
        for _ in range(3):
            if i < len(lines):
                new_lines.append(lines[i])
                i += 1
        # Close the conditional
        new_lines.append("                        {% endif %}\n")
    else:
        new_lines.append(line)
        i += 1

with open('app/templates/dashboard/creator.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ FIXED! Payment UI restored + Badge hiding added")
