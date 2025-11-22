# Add dispute modal to both dashboards
modal_html = '''
<!-- Dispute Modal -->
<div id="disputeModal" class="hidden fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-xl shadow-2xl max-w-md w-full p-6">
        <h3 class="text-xl font-bold mb-4">⚠️ Raise Dispute</h3>
        <form id="disputeForm">
            <div class="mb-4">
                <label class="block text-sm font-semibold mb-2">Dispute Type</label>
                <select id="disputeType" class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500" required>
                    <option value="">Select type...</option>
                    <option value="payment_not_received">Payment Not Received</option>
                    <option value="wrong_amount">Wrong Amount</option>
                    <option value="quality_issue">Quality Issue</option>
                </select>
            </div>
            <div class="mb-4">
                <label class="block text-sm font-semibold mb-2">Description</label>
                <textarea id="disputeDescription" 
                          rows="4" 
                          placeholder="Describe the issue in detail..." 
                          class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-red-500" 
                          required></textarea>
            </div>
            <div class="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
                <p class="text-xs text-yellow-800">
                    <i class="fas fa-info-circle mr-1"></i>
                    Admin will review this dispute and contact both parties. Please provide accurate details.
                </p>
            </div>
            <div class="flex gap-3">
                <button type="button" onclick="closeDisputeModal()" 
                        class="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50">Cancel</button>
                <button type="submit" 
                        class="flex-1 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700">Submit Dispute</button>
            </div>
        </form>
    </div>
</div>

<script>
let currentDisputeTransactionId = null;

function openDisputeModal(transactionId) {
    currentDisputeTransactionId = transactionId;
    document.getElementById('disputeModal').classList.remove('hidden');
}

function closeDisputeModal() {
    document.getElementById('disputeModal').classList.add('hidden');
    document.getElementById('disputeForm').reset();
    currentDisputeTransactionId = null;
}

document.getElementById('disputeForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const type = document.getElementById('disputeType').value;
    const description = document.getElementById('disputeDescription').value;
    
    if (!type || !description) {
        alert('Please fill all fields');
        return;
    }
    
    fetch(`/dispute/create/${currentDisputeTransactionId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams({type: type, description: description})
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert('⚠️ Dispute raised successfully. Admin will review.');
            closeDisputeModal();
            location.reload();
        } else {
            alert('Error: ' + (data.error || 'Failed to raise dispute'));
        }
    })
    .catch(err => {
        alert('Error raising dispute');
        console.error(err);
    });
});
</script>
'''

# Add to creator dashboard
with open('app/templates/dashboard/creator.html', 'r', encoding='utf-8') as f:
    creator_content = f.read()

if 'disputeModal' not in creator_content:
    creator_content = creator_content.replace('{% endblock %}', modal_html + '\n{% endblock %}')
    with open('app/templates/dashboard/creator.html', 'w', encoding='utf-8') as f:
        f.write(creator_content)

# Add to customer dashboard
with open('app/templates/dashboard/customer.html', 'r', encoding='utf-8') as f:
    customer_content = f.read()

if 'disputeModal' not in customer_content:
    customer_content = customer_content.replace('{% endblock %}', modal_html + '\n{% endblock %}')
    with open('app/templates/dashboard/customer.html', 'w', encoding='utf-8') as f:
        f.write(customer_content)

print("✅ Added dispute modal and JavaScript")
