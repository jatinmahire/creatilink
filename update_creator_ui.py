# Script to add delete and leave buttons to creator dashboard
import re

# Read the file
with open('app/templates/dashboard/creator.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the job card header section and add action buttons
# Look for the div with job title and customer name
pattern = r'(<div class="flex justify-between items-start mb-2">[\s\S]*?<p class="text-gray-600 text-sm">{{ job\.customer\.full_name }}</p>\s*</div>)'

replacement = r'''<div class="flex justify-between items-start mb-2">
                    <div>
                        <h3 class="font-bold">{{ job.title }}</h3>
                        <p class="text-gray-600 text-sm">{{ job.customer.full_name }}</p>
                    </div>
                    <div class="flex gap-2">
                        <button onclick="leaveProject({{ job.id }}, '{{ job.title }}')" 
                                class="text-orange-600 hover:text-orange-800 p-1" 
                                title="Leave Project">
                            <i class="fas fa-sign-out-alt text-sm"></i>
                        </button>
                        <button onclick="deleteProject({{ job.id }}, '{{ job.title }}')" 
                                class="text-red-600 hover:text-red-800 p-1" 
                                title="Delete Project">
                            <i class="fas fa-trash-alt text-sm"></i>
                        </button>
                    </div>
                </div>'''

content = re.sub(pattern, replacement, content, count=1)

# Add modals before the closing </div> tag (before {% endblock %})
modals_html = '''
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

<!-- Leave Project Modal -->
<div id="leaveModal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
        <h3 class="text-xl font-bold mb-4">👋 Leave Project?</h3>
        <p class="text-gray-600 mb-4">Customer will be notified. Project: <strong id="leaveProjectName"></strong></p>
        <input type="text" id="leaveReason" placeholder="Reason for leaving (optional)" 
               class="w-full px-4 py-2 border rounded mb-4">
        <div class="flex gap-3">
            <button onclick="closeLeaveModal()" class="flex-1 px-4 py-2 border rounded hover:bg-gray-50">Cancel</button>
            <button onclick="confirmLeave()" class="flex-1 px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700">Leave</button>
        </div>
    </div>
</div>
'''

# Add JavaScript for modals (before closing </script>)
js_code = '''
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

function leaveProject(id, title) {
    currentProjectId = id;
    document.getElementById('leaveProjectName').textContent = title;
    document.getElementById('leaveModal').classList.remove('hidden');
}

function closeLeaveModal() {
    document.getElementById('leaveModal').classList.add('hidden');
    document.getElementById('leaveReason').value = '';
    currentProjectId = null;
}

function confirmLeave() {
    const reason = document.getElementById('leaveReason').value;
    fetch(`/projects/${currentProjectId}/leave`, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({reason: reason})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('👋 You have left this project');
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'Failed to leave'));
        }
    })
    .catch(err => {
        alert('Error leaving project');
        console.error(err);
    });
}
'''

# Insert modals before {% endblock %}
content = content.replace('{% endblock %}', modals_html + '\n{% endblock %}')

# Insert JavaScript before the closing </script> tag
content = content.replace('</script>', js_code + '\n</script>')

# Write back
with open('app/templates/dashboard/creator.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added delete and leave UI to creator dashboard")
