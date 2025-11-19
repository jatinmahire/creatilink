"""
Comprehensive template generator for CreatiLink
Creates all remaining HTML templates
"""

import os

TEMPLATES_DIR = "app/templates"

# All templates organized by category
ALL_TEMPLATES = {
    # Projects templates
    "projects/list.html": '''{% extends "base.html" %}
{% block title %}Browse Projects - CreatiLink{% endblock %}
{% block content %}
<div class="max-w-7xl mx-auto px-4 py-12">
    <h1 class="text-3xl font-bold mb-8">Browse Projects</h1>
    <div class="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div class="lg:col-span-1">
            <div class="bg-white p-6 rounded-lg shadow">
                <h3 class="font-bold mb-4">Filters</h3>
                <form method="GET">
                    <div class="mb-4">
                        <label class="block text-sm font-semibold mb-2">Category</label>
                        <select name="category" class="w-full px-3 py-2 border rounded">
                            <option value="">All Categories</option>
                            <option value="graphic_design">Graphic Design</option>
                            <option value="video_editing">Video Editing</option>
                            <option value="photography">Photography</option>
                            <option value="videography">Videography</option>
                        </select>
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-semibold mb-2">Budget Range</label>
                        <input type="number" name="min_budget" placeholder="Min" class="w-full px-3 py-2 border rounded mb-2">
                        <input type="number" name="max_budget" placeholder="Max" class="w-full px-3 py-2 border rounded">
                    </div>
                    <button type="submit" class="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700">
                        Apply Filters
                    </button>
                </form>
            </div>
        </div>
        <div class="lg:col-span-3">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                {% for project in projects.items %}
                <div class="bg-white rounded-lg shadow hover:shadow-lg transition p-6">
                    <h3 class="font-bold text-xl mb-2">{{ project.title }}</h3>
                    <p class="text-gray-600 mb-4">{{ project.description[:150] }}...</p>
                    <div class="flex justify-between items-center text-sm text-gray-500 mb-4">
                        <span><i class="fas fa-tag"></i> {{ project.category|replace('_', ' ')|title }}</span>
                        <span class="font-bold text-indigo-600">${{ project.budget }}</span>
                    </div>
                    <a href="{{ url_for('projects.detail', project_id=project.id) }}" 
                       class="block text-center bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700">
                        View Details
                    </a>
                </div>
                {% endfor %}
            </div>
            {% if projects.has_prev or projects.has_next %}
            <div class="flex justify-center mt-8 space-x-2">
                {% if projects.has_prev %}
                <a href="?page={{ projects.prev_num }}" class="px-4 py-2 bg-gray-200 rounded">Previous</a>
                {% endif %}
                <span class="px-4 py-2">Page {{ projects.page }} of {{ projects.pages }}</span>
                {% if projects.has_next %}
                <a href="?page={{ projects.next_num }}" class="px-4 py-2 bg-gray-200 rounded">Next</a>
                {% endif %}
            </div>
            {% endif %}
        </div>
    </div>
</div>
{% endblock %}''',

    "projects/create.html": '''{% extends "base.html" %}
{% block title %}Post a Project - CreatiLink{% endblock %}
{% block content %}
<div class="max-w-3xl mx-auto px-4 py-12">
    <div class="bg-white rounded-xl shadow-lg p-8">
        <h2 class="text-3xl font-bold mb-8">Post a New Project</h2>
        <form method="POST" enctype="multipart/form-data">
            <div class="mb-6">
                <label class="block text-gray-700 font-semibold mb-2">Project Title *</label>
                <input type="text" name="title" required
                       class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                       placeholder="e.g., Logo Design for Tech Startup">
            </div>
            <div class="mb-6">
                <label class="block text-gray-700 font-semibold mb-2">Description *</label>
                <textarea name="description" rows="6" required
                          class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                          placeholder="Describe your project requirements in detail..."></textarea>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Category *</label>
                    <select name="category" required class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500">
                        <option value="">Select category</option>
                        <option value="graphic_design">Graphic Design</option>
                        <option value="video_editing">Video Editing</option>
                        <option value="photography">Photography</option>
                        <option value="videography">Videography</option>
                    </select>
                </div>
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Budget (USD) *</label>
                    <input type="number" name="budget" step="0.01" required
                           class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500"
                           placeholder="500">
                </div>
            </div>
            <div class="mb-6">
                <label class="block text-gray-700 font-semibold mb-2">Deadline</label>
                <input type="date" name="deadline"
                       class="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500">
            </div>
            <div class="mb-6">
                <label class="block text-gray-700 font-semibold mb-2">Attachments</label>
                <input type="file" name="attachments" id="attachments" multiple
                       class="w-full px-4 py-2 border rounded-lg">
                <div id="attachments_preview" class="mt-4"></div>
            </div>
            <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700">
                Post Project
            </button>
        </form>
    </div>
</div>
{% endblock %}''',

    "projects/detail.html": '''{% extends "base.html" %}
{% block title %}{{ project.title }} - CreatiLink{% endblock %}
{% block content %}
<div class="max-w-7xl mx-auto px-4 py-12">
    <div class="bg-white rounded-xl shadow-lg p-8 mb-8">
        <div class="flex justify-between items-start mb-6">
            <div>
                <h1 class="text-3xl font-bold mb-2">{{ project.title }}</h1>
                <p class="text-gray-600">Posted by {{ project.customer.full_name }}</p>
            </div>
            <div class="text-right">
                <div class="text-3xl font-bold text-indigo-600">${{ project.budget }}</div>
                <div class="text-sm text-gray-500">Budget</div>
            </div>
        </div>
        <div class="mb-6">
            <span class="inline-block bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm mr-2">
                {{ project.category|replace('_', ' ')|title }}
            </span>
            <span class="inline-block bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm">
                {{ project.status|title }}
            </span>
        </div>
        <div class="prose max-w-none mb-6">
            <h3 class="font-bold mb-2">Description</h3>
            <p class="text-gray-700">{{ project.description }}</p>
        </div>
        {% if project.deadline %}
        <p class="text-gray-600"><strong>Deadline:</strong> {{ project.deadline.strftime('%B %d, %Y') }}</p>
        {% endif %}
        
        {% if current_user.is_authenticated %}
            {% if current_user.role == 'creator' and project.status == 'open' and not user_application %}
            <button onclick="openModal('apply-modal')" class="mt-4 bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700">
                Apply to This Project
            </button>
            {% elif current_user.id == project.posted_by_id and project.assigned_to_id %}
            <a href="{{ url_for('chat.room', project_id=project.id) }}" 
               class="mt-4 inline-block bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700">
                <i class="fas fa-comments"></i> Open Chat
            </a>
            {% endif %}
        {% endif %}
    </div>
    
    {% if current_user.is_authenticated and current_user.id == project.posted_by_id %}
    <div class="bg-white rounded-xl shadow-lg p-8">
        <h2 class="text-2xl font-bold mb-6">Applications ({{ applications|length }})</h2>
        {% for app in applications %}
        <div class="border-b py-4">
            <div class="flex justify-between items-start">
                <div>
                    <h3 class="font-bold">{{ app.creator.full_name }}</h3>
                    <p class="text-gray-600">{{ app.message }}</p>
                </div>
                <div class="text-right">
                    <div class="font-bold text-indigo-600">${{ app.quote }}</div>
                    <div class="text-sm text-gray-500">{{ app.delivery_days }} days</div>
                    {% if project.status == 'open' %}
                    <button onclick="assignCreator({{ app.id }})" 
                            class="mt-2 bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 text-sm">
                        Assign
                    </button>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}
</div>

<!-- Apply Modal -->
<div id="apply-modal" class="modal-backdrop hidden fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="bg-white rounded-xl p-8 max-w-md w-full mx-4">
        <h3 class="text-2xl font-bold mb-4">Apply to Project</h3>
        <form id="apply-form">
            <div class="mb-4">
                <label class="block font-semibold mb-2">Your Quote (USD)</label>
                <input type="number" name="quote" step="0.01" required class="w-full px-4 py-2 border rounded">
            </div>
            <div class="mb-4">
                <label class="block font-semibold mb-2">Delivery Time (days)</label>
                <input type="number" name="delivery_days" required class="w-full px-4 py-2 border rounded">
            </div>
            <div class="mb-4">
                <label class="block font-semibold mb-2">Cover Letter</label>
                <textarea name="message" rows="4" class="w-full px-4 py-2 border rounded"></textarea>
            </div>
            <div class="flex space-x-4">
                <button type="submit" class="flex-1 bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700">
                    Submit Application
                </button>
                <button type="button" onclick="closeModal('apply-modal')" class="flex-1 bg-gray-200 py-2 rounded hover:bg-gray-300">
                    Cancel
                </button>
            </div>
        </form>
    </div>
</div>

<script>
document.getElementById('apply-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    try {
        const response = await fetch('{{ url_for("projects.apply", project_id=project.id) }}', {
            method: 'POST',
            body: formData
        });
        if (response.ok) {
            window.location.reload();
        }
    } catch (error) {
        alert('Failed to submit application');
    }
});

function assignCreator(appId) {
    if (confirm('Assign this creator to the project?')) {
        const formData = new FormData();
        formData.append('application_id', appId);
        fetch('{{ url_for("projects.assign", project_id=project.id) }}', {
            method: 'POST',
            body: formData
        }).then(() => window.location.reload());
    }
}
</script>
{% endblock %}''',

    "projects/creator_profile.html": '''{% extends "base.html" %}
{% block title %}{{ creator.full_name }} - CreatiLink{% endblock %}
{% block content %}
<div class="max-w-7xl mx-auto px-4 py-12">
    <div class="bg-white rounded-xl shadow-lg p-8 mb-8">
        <div class="flex items-start space-x-8">
            <img src="{{ creator.profile_image or '/static/images/default-avatar.png' }}" 
                 class="w-32 h-32 rounded-full object-cover">
            <div class="flex-1">
                <h1 class="text-3xl font-bold mb-2">{{ creator.full_name }}</h1>
                <p class="text-gray-600 mb-2">{{ creator.domain|replace('_', ' ')|title }}</p>
                <div class="flex items-center mb-4">
                    <span class="text-yellow-500">
                        {% for i in range(5) %}
                            {% if i < creator.rating|int %}<i class="fas fa-star"></i>
                            {% else %}<i class="far fa-star"></i>{% endif %}
                        {% endfor %}
                    </span>
                    <span class="ml-2 text-gray-600">{{ creator.rating }} ({{ creator.total_reviews }} reviews)</span>
                </div>
                <p class="text-gray-700 mb-4">{{ creator.bio }}</p>
                <div class="mb-4">
                    <strong>Skills:</strong> {{ creator.skills }}
                </div>
                <div>
                    <strong>Completed Projects:</strong> {{ completed_count }}
                </div>
            </div>
        </div>
    </div>
    
    {% if portfolio %}
    <div class="bg-white rounded-xl shadow-lg p-8 mb-8">
        <h2 class="text-2xl font-bold mb-6">Portfolio</h2>
        <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {% for item in portfolio %}
            <div class="rounded-lg overflow-hidden shadow hover:shadow-lg transition">
                {% if item.file_type == 'image' %}
                <img src="{{ item.file_path }}" class="w-full h-48 object-cover">
                {% elif item.file_type == 'video' %}
                <video src="{{ item.file_path }}" class="w-full h-48 object-cover" controls></video>
                {% endif %}
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}
    
    {% if reviews %}
    <div class="bg-white rounded-xl shadow-lg p-8">
        <h2 class="text-2xl font-bold mb-6">Reviews</h2>
        {% for review in reviews %}
        <div class="border-b py-4">
            <div class="flex justify-between mb-2">
                <strong>{{ review.reviewer.full_name }}</strong>
                <span class="text-yellow-500">
                    {% for i in range(review.rating) %}<i class="fas fa-star"></i>{% endfor %}
                </span>
            </div>
            <p class="text-gray-700">{{ review.comment }}</p>
            <p class="text-sm text-gray-500 mt-2">{{ review.created_at.strftime('%B %d, %Y') }}</p>
        </div>
        {% endfor %}
    </div>
    {% endif %}
</div>
{% endblock %}''',

    "projects/review.html": '''{% extends "base.html" %}
{% block title %}Review Project - CreatiLink{% endblock %}
{% block content %}
<div class="max-w-2xl mx-auto px-4 py-12">
    <div class="bg-white rounded-xl shadow-lg p-8">
        <h2 class="text-3xl font-bold mb-8">Review Project</h2>
        <div class="mb-6 p-4 bg-gray-50 rounded">
            <h3 class="font-bold mb-2">{{ project.title }}</h3>
            <p class="text-gray-600">Creator: {{ project.creator.full_name }}</p>
        </div>
        <form method="POST">
            <div class="mb-6">
                <label class="block font-semibold mb-2">Rating</label>
                <div id="rating-stars" class="star-rating text-3xl">
                    {% for i in range(1, 6) %}
                    <i class="far fa-star" data-rating="{{ i }}"></i>
                    {% endfor %}
                    <input type="hidden" name="rating" required>
                </div>
            </div>
            <div class="mb-6">
                <label class="block font-semibold mb-2">Your Review</label>
                <textarea name="comment" rows="4" class="w-full px-4 py-2 border rounded-lg"
                          placeholder="Share your experience with this creator..."></textarea>
            </div>
            <button type="submit" class="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700">
                Submit Review
            </button>
        </form>
    </div>
</div>
{% endblock %}''',

    "dashboard/customer.html": '''{% extends "base.html" %}
{% block title %}Customer Dashboard - CreatiLink{% endblock %}
{% block content %}
<div class="max-w-7xl mx-auto px-4 py-12">
    <h1 class="text-3xl font-bold mb-8">Customer Dashboard</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-indigo-600">{{ total_projects }}</div>
            <div class="text-gray-600">Total Projects</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-green-600">{{ active_projects }}</div>
            <div class="text-gray-600">Active Projects</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-blue-600">{{ completed_projects }}</div>
            <div class="text-gray-600">Completed</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-purple-600">${{ "%.2f"|format(total_spent) }}</div>
            <div class="text-gray-600">Total Spent</div>
        </div>
    </div>
    
    <div class="bg-white rounded-xl shadow-lg p-8">
        <h2 class="text-2xl font-bold mb-6">My Projects</h2>
        <div class="space-y-4">
            {% for project in projects %}
            <div class="border rounded-lg p-4 hover:shadow-md transition">
                <div class="flex justify-between items-start">
                    <div>
                        <h3 class="font-bold text-lg">{{ project.title }}</h3>
                        <p class="text-gray-600">{{ project.category|replace('_', ' ')|title }}</p>
                    </div>
                    <div class="text-right">
                        <span class="inline-block bg-{{ 'green' if project.status == 'completed' else 'blue' }}-100 text-{{ 'green' if project.status == 'completed' else 'blue' }}-800 px-3 py-1 rounded-full text-sm">
                            {{ project.status|title }}
                        </span>
                        <div class="font-bold mt-2">${{ project.budget }}</div>
                    </div>
                </div>
                <div class="mt-4 flex space-x-2">
                    <a href="{{ url_for('projects.detail', project_id=project.id) }}" 
                       class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700 text-sm">
                        View Details
                    </a>
                    {% if project.assigned_to_id %}
                    <a href="{{ url_for('chat.room', project_id=project.id) }}" 
                       class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm">
                        Chat
                    </a>
                    {% endif %}
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}''',

    "dashboard/creator.html": '''{% extends "base.html" %}
{% block title %}Creator Dashboard - CreatiLink{% endblock %}
{% block content %}
<div class="max-w-7xl mx-auto px-4 py-12">
    <h1 class="text-3xl font-bold mb-8">Creator Dashboard</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-indigo-600">{{ active_jobs|length }}</div>
            <div class="text-gray-600">Active Jobs</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-green-600">{{ completed_jobs }}</div>
            <div class="text-gray-600">Completed</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-blue-600">{{ pending_applications }}</div>
            <div class="text-gray-600">Pending Applications</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-purple-600">${{ "%.2f"|format(total_earnings) }}</div>
            <div class="text-gray-600">Total Earnings</div>
        </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="bg-white rounded-xl shadow-lg p-8">
            <h2 class="text-2xl font-bold mb-6">Active Jobs</h2>
            {% for job in active_jobs %}
            <div class="border-b py-4">
                <h3 class="font-bold">{{ job.title }}</h3>
                <p class="text-gray-600 text-sm">{{ job.customer.full_name }}</p>
                <div class="mt-2 flex space-x-2">
                    <a href="{{ url_for('projects.detail', project_id=job.id) }}" 
                       class="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700">
                        View
                    </a>
                    <a href="{{ url_for('chat.room', project_id=job.id) }}" 
                       class="bg-green-600 text-white px-3 py-1 rounded text-sm hover:bg-green-700">
                        Chat
                    </a>
                </div>
            </div>
            {% endfor %}
        </div>
        
        <div class="bg-white rounded-xl shadow-lg p-8">
            <h2 class="text-2xl font-bold mb-6">Recent Applications</h2>
            {% for app in applications %}
            <div class="border-b py-4">
                <h3 class="font-bold">{{ app.project.title }}</h3>
                <div class="flex justify-between text-sm mt-2">
                    <span class="text-gray-600">Quote: ${{ app.quote }}</span>
                    <span class="bg-{{ 'green' if app.status == 'accepted' else 'yellow' if app.status == 'pending' else 'red' }}-100 text-{{ 'green' if app.status == 'accepted' else 'yellow' if app.status == 'pending' else 'red' }}-800 px-2 py-1 rounded text-xs">
                        {{ app.status|title }}
                    </span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}''',

    "chat/room.html": '''{% extends "base.html" %}
{% block title %}Chat - {{ project.title }}{% endblock %}
{% block extra_head %}
<script src="{{ url_for('static', filename='js/chat.js') }}"></script>
{% endblock %}
{% block content %}
<div class="max-w-5xl mx-auto px-4 py-12">
    <div class="bg-white rounded-xl shadow-lg overflow-hidden" style="height: 600px; display: flex; flex-direction: column;">
        <div class="bg-indigo-600 text-white p-4">
            <h2 class="font-bold text-xl">{{ project.title }}</h2>
            <p class="text-indigo-100 text-sm">Chat with {{ other_user.full_name if other_user else 'Participant' }}</p>
        </div>
        
        <div id="messages-container" class="flex-1 overflow-y-auto p-4 bg-gray-50">
            <!-- Messages will be loaded here -->
        </div>
        
        <div id="typing-indicator" class="hidden px-4 py-2 text-sm text-gray-500 italic"></div>
        
        <div class="border-t p-4 bg-white">
            <div class="flex space-x-2">
                <input type="text" id="message-input" placeholder="Type your message..."
                       class="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500">
                <button id="send-btn" class="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700">
                    <i class="fas fa-paper-plane"></i> Send
                </button>
            </div>
        </div>
    </div>
</div>
<script>
// Initialize chat when page loads
document.addEventListener('DOMContentLoaded', function() {
    ChatClient.init({{ project.id }}, {{ current_user.id }});
});
</script>
{% endblock %}''',

    "payments/success.html": '''{% extends "base.html" %}
{% block title %}Payment Successful - CreatiLink{% endblock %}
{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="max-w-md w-full bg-white rounded-xl shadow-2xl p-8 text-center">
        <div class="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <i class="fas fa-check text-4xl text-green-600"></i>
        </div>
        <h2 class="text-3xl font-bold mb-4">Payment Successful!</h2>
        <p class="text-gray-600 mb-8">Your payment has been processed successfully. The creator can now start working on your project.</p>
        <a href="{{ url_for('projects.detail', project_id=project_id) }}" 
           class="inline-block bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700">
            View Project
        </a>
    </div>
</div>
{% endblock %}''',

    "payments/transactions.html": '''{% extends "base.html" %}
{% block title %}Transaction History - CreatiLink{% endblock %}
{% block content %}
<div class="max-w-6xl mx-auto px-4 py-12">
    <h1 class="text-3xl font-bold mb-8">Transaction History</h1>
    
    <div class="bg-white rounded-xl shadow-lg overflow-hidden">
        <table class="w-full">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Project</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Amount</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                </tr>
            </thead>
            <tbody class="divide-y">
                {% for transaction in transactions %}
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap">{{ transaction.created_at.strftime('%Y-%m-%d') }}</td>
                    <td class="px-6 py-4">{{ transaction.project.title }}</td>
                    <td class="px-6 py-4 font-bold text-indigo-600">${{ transaction.amount }}</td>
                    <td class="px-6 py-4">
                        <span class="px-3 py-1 rounded-full text-xs bg-{{ 'green' if transaction.status == 'completed' else 'yellow' }}-100 text-{{ 'green' if transaction.status == 'completed' else 'yellow' }}-800">
                            {{ transaction.status|title }}
                        </span>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}''',

    "admin/dashboard.html": '''{% extends "base.html" %}
{% block title %}Admin Dashboard - CreatiLink{% endblock %}
{% block content %}
<div class="max-w-7xl mx-auto px-4 py-12">
    <h1 class="text-3xl font-bold mb-8 text-orange-600"><i class="fas fa-shield-alt"></i> Admin Dashboard</h1>
    
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-blue-600">{{ total_users }}</div>
            <div class="text-gray-600">Total Users</div>
            <div class="text-sm text-gray-500 mt-2">{{ total_customers }} customers, {{ total_creators }} creators</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-green-600">{{ total_projects }}</div>
            <div class="text-gray-600">Total Projects</div>
            <div class="text-sm text-gray-500 mt-2">{{ active_projects }} active</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-purple-600">{{ total_transactions }}</div>
            <div class="text-gray-600">Transactions</div>
        </div>
        <div class="bg-white rounded-lg shadow p-6">
            <div class="text-3xl font-bold text-indigo-600">${{ "%.2f"|format(platform_fee) }}</div>
            <div class="text-gray-600">Platform Revenue</div>
            <div class="text-sm text-gray-500 mt-2">10% of ${{ "%.2f"|format(total_revenue) }}</div>
        </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div class="bg-white rounded-xl shadow-lg p-6">
            <h2 class="text-xl font-bold mb-4">Recent Users</h2>
            <div class="space-y-3">
                {% for user in recent_users %}
                <div class="flex justify-between items-center border-b pb-2">
                    <div>
                        <div class="font-semibold">{{ user.full_name }}</div>
                        <div class="text-sm text-gray-500">{{ user.email }} - {{ user.role|title }}</div>
                    </div>
                    <a href="{{ url_for('admin.users') }}" class="text-indigo-600 hover:text-indigo-800 text-sm">
                        Manage
                    </a>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="bg-white rounded-xl shadow-lg p-6">
            <h2 class="text-xl font-bold mb-4">Recent Projects</h2>
            <div class="space-y-3">
                {% for project in recent_projects %}
                <div class="border-b pb-2">
                    <div class="font-semibold">{{ project.title }}</div>
                    <div class="text-sm text-gray-500">${{ project.budget }} - {{ project.status|title }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
</div>
{% endblock %}''',

    "admin/users.html": '''{% extends "base.html" %}
{% block title %}User Management - Admin{% endblock %}
{% block content %}
<div class="max-w-7xl mx-auto px-4 py-12">
    <h1 class="text-3xl font-bold mb-8">User Management</h1>
    
    <div class="bg-white rounded-xl shadow-lg overflow-hidden">
        <table class="w-full">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Email</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Role</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
            </thead>
            <tbody class="divide-y">
                {% for user in users.items %}
                <tr>
                    <td class="px-6 py-4">{{ user.full_name }}</td>
                    <td class="px-6 py-4">{{ user.email }}</td>
                    <td class="px-6 py-4">{{ user.role|title }}</td>
                    <td class="px-6 py-4">
                        <span class="px-3 py-1 rounded-full text-xs bg-{{ 'green' if user.is_active else 'red' }}-100 text-{{ 'green' if user.is_active else 'red' }}-800">
                            {{ 'Active' if user.is_active else 'Inactive' }}
                        </span>
                    </td>
                    <td class="px-6 py-4">
                        {% if not user.is_admin %}
                        <button onclick="toggleUserStatus({{ user.id }})" 
                                class="text-orange-600 hover:text-orange-800 text-sm">
                            {{ 'Deactivate' if user.is_active else 'Activate' }}
                        </button>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
<script>
function toggleUserStatus(userId) {
    if (confirm('Are you sure?')) {
        fetch(`/admin/users/${userId}/toggle-status`, { method: 'POST' })
            .then(() => window.location.reload());
    }
}
</script>
{% endblock %}'''
}

def create_all_templates():
    """Create all template files"""
    created = 0
    for path, content in ALL_TEMPLATES.items():
        full_path = os.path.join(TEMPLATES_DIR, path)
        directory = os.path.dirname(full_path)
        
        os.makedirs(directory, exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Created: {path}")
        created += 1
    
    print(f"\n{'='*60}")
    print(f"Successfully created {created} templates!")
    print(f"{'='*60}")
    print("\nAll templates are now ready. Next steps:")
    print("1. Run: python seed.py (to populate database)")
    print("2. Run: python manage.py (to start server)")
    print("3. Visit: http://localhost:5000")

if __name__ == '__main__':
    create_all_templates()
