# Script to add delete button to customer dashboard
import re

# Read the file
with open('app/templates/dashboard/customer.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the project card header and add delete button
# Look for the section with project title and status
pattern = r'(<div class="flex justify-between items-start">[\s\S]*?<div class="font-bold mt-2">&#8377;{{ project\.budget }}</div>\s*</div>)'

replacement = r'''<div class="flex justify-between items-start">
                    <div>
                        <h3 class="font-bold text-lg">{{ project.title }}</h3>
                        <p class="text-gray-600">{{ project.category|replace('_', ' ')|title }}</p>
                    </div>
                    <div class="flex items-start gap-2">
                        <div class="text-right">
                            <span class="inline-block bg-{{ 'green' if project.status == 'completed' else 'blue' }}-100 text-{{ 'green' if project.status == 'completed' else 'blue' }}-800 px-3 py-1 rounded-full text-sm">
                                {{ project.status|title }}
                            </span>
                            <div class="font-bold mt-2">&#8377;{{ project.budget }}</div>
                        </div>
                        <button onclick="deleteProject({{ project.id }}, '{{ project.title }}')" 
                                class="text-red-600 hover:text-red-800 p-2 mt-1" 
                                title="Delete Project">
                            <i class="fas fa-trash-alt text-sm"></i>
                        </button>
                    </div>
                </div>'''

content = re.sub(pattern, replacement, content, count=1)

# Add modal before {% endblock %}
modal_html = '''
<!-- Delete Project Modal -->
<div id="deleteModal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
        <h3 class="text-xl font-bold mb-4">🗑️ Delete Project?</h3>
        <p class="text-gray-600 mb-4">Are you sure you want to delete <strong id="deleteProjectName"></strong>?</p>
        <input type="text" id="deleteReason" placeholder="Reason for deletion (optional)" 
               class="w-full px-4 py-2 border rounded mb-4">
        <div class="flex gap-3">
            <button onclick="closeDeleteModal()" class="flex-1 px-4 py-2 border rounded hover:bg-gray-50">Cancel</button>
            <button onclick="confirmDelete()" class="flex-1 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700">Delete</button>
        </div>
    </div>
</div>
'''

# Add JavaScript before closing </script> or before {% endblock %} if no script
js_code = '''
<script>
// Project Management Functions
let currentProjectId = null;

function deleteProject(id, title) {
    currentProjectId = id;
    document.getElementById('deleteProjectName').textContent = title;
    document.getElementById('deleteModal').classList.remove('hidden');
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.add('hidden');
    document.getElementById('deleteReason').value = '';
    currentProjectId = null;
}

function confirmDelete() {
    const reason = document.getElementById('deleteReason').value;
    fetch(`/projects/${currentProjectId}/delete`, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({reason: reason})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('✅ Project deleted successfully');
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'Failed to delete'));
        }
    })
    .catch(err => {
        alert('Error deleting project');
        console.error(err);
    });
}
</script>
'''

# Insert modal and script before {% endblock %}
content = content.replace('{% endblock %}', modal_html + '\n' + js_code + '\n{% endblock %}')

# Write back
with open('app/templates/dashboard/customer.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added delete UI to customer dashboard")
