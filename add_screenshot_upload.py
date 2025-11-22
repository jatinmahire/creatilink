# Add screenshot upload to customer payment modal
import re

with open('app/templates/dashboard/customer.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the payment button section and add file upload
# Look for the "Make Payment" button section

# Add file input before the confirmation button
payment_ui_addition = '''
                                        <!-- Screenshot Upload (Optional) -->
                                        <div class="mt-3">
                                            <label class="block text-sm font-semibold text-gray-700 mb-2">
                                                📸 Payment Screenshot (Optional but Recommended)
                                            </label>
                                            <input type="file" 
                                                   id="paymentScreenshot" 
                                                   name="screenshot" 
                                                   accept="image/*,.pdf"
                                                   class="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500">
                                            <p class="text-xs text-gray-500 mt-1">
                                                <i class="fas fa-info-circle"></i> Upload proof of payment (JPG, PNG, PDF)
                                            </p>
                                        </div>'''

# Find and replace the section before "I Successfully Made Payment" button
# Look for the button that confirms payment
pattern = r'(<button[^>]*onclick="confirmPayment\([^)]+\)"[^>]*>.*?I Successfully Made Payment.*?</button>)'

def replacement_func(match):
    return payment_ui_addition + '\n' + match.group(0)

content = re.sub(pattern, replacement_func, content, flags=re.DOTALL)

# Update the confirmPayment JavaScript function to handle file upload
old_js = '''function confirmPayment(transactionId) {
    if (!confirm('Have you completed the UPI payment?')) return;
    
    fetch(`/payment/confirm/${transactionId}`, {
        method: 'POST'
    })'''

new_js = '''function confirmPayment(transactionId) {
    if (!confirm('Have you completed the UPI payment?')) return;
    
    // Create FormData to include file
    const formData = new FormData();
    const screenshot = document.getElementById('paymentScreenshot');
    if (screenshot && screenshot.files[0]) {
        formData.append('screenshot', screenshot.files[0]);
    }
    
    fetch(`/payment/confirm/${transactionId}`, {
        method: 'POST',
        body: formData
    })'''

content = content.replace(old_js, new_js)

with open('app/templates/dashboard/customer.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added screenshot upload to customer payment modal")
