# Add delete modal and JavaScript to customer dashboard
with open('app/templates/dashboard/customer.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the endblock and add modal + JS before it
modal_and_js = '''
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

<script>
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

content = content.replace('{% endblock %}', modal_and_js + '{% endblock %}')

with open('app/templates/dashboard/customer.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added delete modal and JavaScript")
