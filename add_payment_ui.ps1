# PowerShell script to insert payment UI
$file = "app/templates/dashboard/creator.html"
$content = Get-Content $file -Raw -Encoding UTF8

# Find the location after the delivered badge and before closing </div>
# Insert payment section after line with {% endif %} that closes the delivered status

$paymentSection = @"

                <!-- Payment Status for Delivered Jobs -->
                {% if job.status == 'delivered' %}
                {% set transaction = job_transactions.get(job.id) %}
                {% if transaction %}
                <div class="mt-3 border-t pt-3">
                    <div class="text-xs font-semibold text-gray-600 mb-2">💰 Payment Status</div>
                    
                    {% if transaction.customer_confirmed and not transaction.creator_confirmed %}
                    <div class="bg-yellow-50 border border-yellow-200 rounded p-2">
                        <div class="text-yellow-700 text-sm font-semibold mb-1">🟡 Customer Paid ₹{{ transaction.amount }}</div>
                        <p class="text-xs text-yellow-600 mb-2">Check your UPI app and confirm</p>
                        <div class="flex gap-2">
                            <button onclick="confirmReceipt({{ transaction.id }})" class="flex-1 bg-green-600 text-white px-2 py-1 rounded hover:bg-green-700 text-xs">✓ Received</button>
                            <button onclick="rejectPayment({{ transaction.id }})" class="flex-1 bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700 text-xs">✗ Not Received</button>
                        </div>
                    </div>
                    {% elif transaction.creator_confirmed %}
                    <div class="bg-green-50 border border-green-200 rounded p-2">
                        <div class="text-green-700 text-sm font-semibold">✅ Received: ₹{{ transaction.amount }}</div>
                    </div>
                    {% else %}
                    <div class="bg-gray-50 border border-gray-200 rounded p-2">
                        <div class="text-gray-700 text-sm">⚪ Awaiting Payment (₹{{ transaction.amount }})</div>
                    </div>
                    {% endif %}
                </div>
                {% endif %}
                {% endif %}
"@

# Find the pattern to insert after
# Look for: {% endif %}\r\n                </div>\r\n            </div>
# This is after the delivered badge section

$pattern = '({% endif %}\r\n                </div>)\r\n(            </div>\r\n            {% else %})'

$replacement = '$1' + $paymentSection + '$2'

$content = $content -replace $pattern, $replacement

Set-Content -Path $file -Value $content -Encoding UTF8 -NoNewline
Write-Host "✅ Payment UI added successfully!"
