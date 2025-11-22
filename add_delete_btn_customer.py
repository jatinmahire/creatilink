# Simple script to add delete button to customer dashboard
with open('app/templates/dashboard/customer.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line 74 and insert delete button after it
output = []
for i, line in enumerate(lines):
    output.append(line)
    # After the budget line, add delete button
    if i == 73 and '&#8377;{{ project.budget }}' in line:  # Line 74 (0-indexed 73)
        output.append('                        <button onclick="deleteProject({{ project.id }}, \'{{ project.title }}\')" \n')
        output.append('                                class="mt-2 text-red-600 hover:text-red-800 text-sm" \n')
        output.append('                                title="Delete Project">\n')
        output.append('                            <i class="fas fa-trash-alt"></i>\n')
        output.append('                        </button>\n')

# Write back
with open('app/templates/dashboard/customer.html', 'w', encoding='utf-8') as f:
    f.writelines(output)

print("✅ Added delete button to customer dashboard")
