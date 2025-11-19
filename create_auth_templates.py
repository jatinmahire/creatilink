"""
Script to generate all remaining HTML templates for CreatiLink
Run this to create all necessary template files
"""

import os

# Base directory for templates
TEMPLATES_DIR = "app/templates"

# Template content dictionary
TEMPLATES = {
    # Authentication templates
    "auth/signup.html": '''{% extends "base.html" %}

{% block title %}Sign Up - CreatiLink{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 py-12 px-4">
    <div class="max-w-md w-full bg-white rounded-xl shadow-2xl p-8">
        <h2 class="text-3xl font-bold text-center mb-8">Create Account</h2>
        <form method="POST">
            <div class="mb-4">
                <label class="block text-gray-700 font-semibold mb-2">Full Name</label>
                <input type="text" name="full_name" required 
                       class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                       placeholder="John Doe">
            </div>
            
            <div class="mb-4">
                <label class="block text-gray-700 font-semibold mb-2">Email</label>
                <input type="email" name="email" required 
                       class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                       placeholder="john@example.com">
            </div>
            
            <div class="mb-4">
                <label class="block text-gray-700 font-semibold mb-2">Password</label>
                <input type="password" name="password" required 
                       class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                       placeholder="••••••••">
            </div>
            
            <div class="mb-6">
                <label class="block text-gray-700 font-semibold mb-2">I am a:</label>
                <div class="grid grid-cols-2 gap-4">
                    <label class="flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer hover:border-indigo-500 transition">
                        <input type="radio" name="role" value="customer" required class="mr-2">
                        <span>Customer</span>
                    </label>
                    <label class="flex items-center justify-center p-4 border-2 rounded-lg cursor-pointer hover:border-indigo-500 transition">
                        <input type="radio" name="role" value="creator" required class="mr-2">
                        <span>Creator</span>
                    </label>
                </div>
            </div>
            
            <button type="submit" 
                    class="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition">
                Sign Up
            </button>
            
            <p class="text-center mt-4 text-gray-600">
                Already have an account? 
                <a href="{{ url_for('auth.login') }}" class="text-indigo-600 hover:text-indigo-800 font-semibold">Login</a>
            </p>
        </form>
    </div>
</div>
{% endblock %}
''',

    "auth/login.html": '''{% extends "base.html" %}

{% block title %}Login - CreatiLink{% endblock %}

{% block content %}
<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 py-12 px-4">
    <div class="max-w-md w-full bg-white rounded-xl shadow-2xl p-8">
        <h2 class="text-3xl font-bold text-center mb-8">Welcome Back</h2>
        <form method="POST">
            <div class="mb-4">
                <label class="block text-gray-700 font-semibold mb-2">Email</label>
                <input type="email" name="email" required 
                       class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                       placeholder="your@email.com">
            </div>
            
            <div class="mb-4">
                <label class="block text-gray-700 font-semibold mb-2">Password</label>
                <input type="password" name="password" required 
                       class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                       placeholder="••••••••">
            </div>
            
            <div class="mb-6 flex items-center">
                <input type="checkbox" name="remember" id="remember" class="mr-2">
                <label for="remember" class="text-gray-700">Remember me</label>
            </div>
            
            <button type="submit" 
                    class="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition">
                Login
            </button>
            
            <p class="text-center mt-4 text-gray-600">
                Don't have an account? 
                <a href="{{ url_for('auth.signup') }}" class=" text-indigo-600 hover:text-indigo-800 font-semibold">Sign up</a>
            </p>
        </form>
    </div>
</div>
{% endblock %}
''',

    "auth/profile_setup.html": '''{% extends "base.html" %}

{% block title %}Complete Your Profile - CreatiLink{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto px-4 py-12">
    <div class="bg-white rounded-xl shadow-lg p-8">
        <h2 class="text-3xl font-bold mb-2">Complete Your Creator Profile</h2>
        <p class="text-gray-600 mb-8">Let's set up your portfolio to start getting projects</p>
        
        <form method="POST" enctype="multipart/form-data">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Domain</label>
                    <select name="domain" required class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <option value="">Select your specialty</option>
                        <option value="graphic_design">Graphic Design</option>
                        <option value="video_editing">Video Editing</option>
                        <option value="photography">Photography</option>
                        <option value="videography">Videography</option>
                    </select>
                </div>
                
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Location</label>
                    <input type="text" name="location" 
                           class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                           placeholder="City, Country">
                </div>
            </div>
            
            <div class="mt-6">
                <label class="block text-gray-700 font-semibold mb-2">Bio</label>
                <textarea name="bio" rows="4" required
                          class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                          placeholder="Tell us about yourself and your experience..."></textarea>
            </div>
            
            <div class="mt-6">
                <label class="block text-gray-700 font-semibold mb-2">Skills</label>
                <input type="text" name="skills" required
                       class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                       placeholder="e.g., Adobe Photoshop, Illustrator, Brand Design">
                <p class="text-sm text-gray-500 mt-1">Separate skills with commas</p>
            </div>
            
            <div class="mt-6">
                <label class="block text-gray-700 font-semibold mb-2">Portfolio Files</label>
                <input type="file" name="portfolio_files" id="portfolio_files" multiple accept="image/*,video/*"
                       class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
                <p class="text-sm text-gray-500 mt-1">Upload images or videos of your best work</p>
                <div id="portfolio_preview" class="mt-4 flex flex-wrap gap-2"></div>
            </div>
            
            <div class="mt-8">
                <button type="submit" 
                        class="w-full bg-indigo-600 text-white py-3 rounded-lg font-semibold hover:bg-indigo-700 transition">
                    Complete Setup
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
''',

    "auth/profile.html": '''{% extends "base.html" %}

{% block title %}My Profile - CreatiLink{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto px-4 py-12">
    <div class="bg-white rounded-xl shadow-lg p-8">
        <h2 class="text-3xl font-bold mb-8">My Profile</h2>
        
        <form method="POST" enctype="multipart/form-data">
            <div class="mb-6">
                <label class="block text-gray-700 font-semibold mb-2">Profile Picture</label>
                <div class="flex items-center space-x-4">
                    <img src="{{ current_user.profile_image or '/static/images/default-avatar.png' }}" 
                         class="w-20 h-20 rounded-full object-cover border-2">
                    <input type="file" name="profile_image" accept="image/*"
                           class="px-4 py-2 border rounded-lg">
                </div>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Full Name</label>
                    <input type="text" name="full_name" value="{{ current_user.full_name }}"
                           class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
                </div>
                
                <div>
                    <label class="block text-gray-700 font-semibold mb-2">Email</label>
                    <input type="email" value="{{ current_user.email }}" disabled
                           class="w-full px-4 py-2 border rounded-lg bg-gray-100">
                </div>
            </div>
            
            {% if current_user.role == 'creator' %}
            <div class="mt-6">
                <label class="block text-gray-700 font-semibold mb-2">Bio</label>
                <textarea name="bio" rows="4"
                          class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">{{ current_user.bio }}</textarea>
            </div>
            
            <div class="mt-6">
                <label class="block text-gray-700 font-semibold mb-2">Skills</label>
                <input type="text" name="skills" value="{{ current_user.skills }}"
                       class="w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
            </div>
            {% endif %}
            
            <div class="mt-8">
                <button type="submit" 
                        class="bg-indigo-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition">
                    Update Profile
                </button>
            </div>
        </form>
    </div>
</div>
{% endblock %}
'''
}

def create_templates():
    """Create all template files"""
    for path, content in TEMPLATES.items():
        full_path = os.path.join(TEMPLATES_DIR, path)
        directory = os.path.dirname(full_path)
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Write template file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Created: {full_path}")
    
    print(f"\nSuccessfully created {len(TEMPLATES)} templates!")

if __name__ == '__main__':
    create_templates()
