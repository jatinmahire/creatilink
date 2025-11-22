# Add delete button to creator dashboard active jobs
with open('app/templates/dashboard/creator.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line 190 (leave button) and add delete button after it
output = []
for i, line in enumerate(lines):
    output.append(line)
    # After the leave button closing tag, add delete button
    if i == 189 and '</button>' in line:  # Line 190 (0-indexed 189)
        output.append('                        <button onclick="deleteProject({{ job.id }}, \'{{ job.title }}\')" \n')
        output.append('                                class="text-red-600 hover:text-red-800 p-1" \n')
        output.append('                                title="Delete Project">\n')
        output.append('                            <i class="fas fa-trash-alt text-sm"></i>\n')
        output.append('                        </button>\n')

# Write back
with open('app/templates/dashboard/creator.html', 'w', encoding='utf-8') as f:
    f.writelines(output)

print("✅ Added delete button to creator dashboard active jobs")
