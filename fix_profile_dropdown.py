# Fix profile dropdown behavior
with open('app/templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add JavaScript for profile dropdown before the closing script tag
profile_dropdown_js = '''
        // Profile Dropdown with hover + click behavior
        const profileDropdown = document.getElementById('profileDropdown');
        const profileButton = document.getElementById('profileButton');
        const profileMenu = document.getElementById('profileMenu');
        
        if (profileButton && profileMenu) {
            let isOpen = false;
            
            // Open on click
            profileButton.addEventListener('click', (e) => {
                e.stopPropagation();
                isOpen = !isOpen;
                profileMenu.classList.toggle('hidden', !isOpen);
            });
            
            // Keep open when hovering over dropdown or button
            profileDropdown.addEventListener('mouseenter', () => {
                profileMenu.classList.remove('hidden');
                isOpen = true;
            });
            
            // Close when mouse leaves the entire dropdown area
            profileDropdown.addEventListener('mouseleave', () => {
                if (!isOpen) {
                    profileMenu.classList.add('hidden');
                }
            });
            
            // Close when clicking outside
            document.addEventListener('click', (e) => {
                if (!profileDropdown.contains(e.target)) {
                    profileMenu.classList.add('hidden');
                    isOpen = false;
                }
            });
        }
'''

# Find the notifications script and add profile dropdown script after it
content = content.replace('        }', '        }\n' + profile_dropdown_js, 1)

with open('app/templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed profile dropdown behavior")
