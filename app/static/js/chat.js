// Chat room SocketIO client

const socket = io();
let currentProjectId = null;
let currentUserId = null;
let typingTimeout = null;

// Initialize chat
function initChat(projectId, userId) {
    currentProjectId = projectId;
    currentUserId = userId;

    // Join the room
    socket.emit('join_room', { project_id: projectId });

    // Load message history
    loadMessages();

    // Setup event listeners
    setupChatEvents();
}

// Load message history
async function loadMessages() {
    try {
        const response = await fetch(`/chat/api/messages/${currentProjectId}`);
        const messages = await response.json();

        const container = document.getElementById('messages-container');
        container.innerHTML = '';

        messages.forEach(msg => {
            appendMessage(msg);
        });

        scrollToBottom();
    } catch (error) {
        console.error('Failed to load messages:', error);
    }
}

// Append message to chat
function appendMessage(message) {
    const container = document.getElementById('messages-container');
    const isOwn = message.sender_id === currentUserId || message.is_own;

    const messageDiv = document.createElement('div');
    messageDiv.className = `flex ${isOwn ? 'justify-end' : 'justify-start'} mb-4`;

    messageDiv.innerHTML = `
        <div class="chat-bubble ${isOwn ? 'chat-bubble-sent' : 'chat-bubble-received'}">
            ${!isOwn ? `<div class="text-xs font-semibold mb-1">${message.sender_name}</div>` : ''}
            <div>${escapeHtml(message.content)}</div>
            <div class="text-xs mt-1 opacity-75">${formatTime(message.created_at)}</div>
        </div>
    `;

    container.appendChild(messageDiv);
}

// Send message
function sendMessage() {
    const input = document.getElementById('message-input');
    const content = input.value.trim();

    if (!content) return;

    socket.emit('send_message', {
        project_id: currentProjectId,
        content: content
    });

    input.value = '';
    stopTyping();
}

// Setup chat events
function setupChatEvents() {
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');

    // Send message on button click
    sendBtn.addEventListener('click', sendMessage);

    // Send message on Enter key
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Typing indicator
    input.addEventListener('input', () => {
        if (!typingTimeout) {
            socket.emit('typing', { project_id: currentProjectId });
        }

        clearTimeout(typingTimeout);
        typingTimeout = setTimeout(stopTyping, 2000);
    });
}

// Stop typing indicator
function stopTyping() {
    if (typingTimeout) {
        socket.emit('stop_typing', { project_id: currentProjectId });
        clearTimeout(typingTimeout);
        typingTimeout = null;
    }
}

// Socket event listeners
socket.on('new_message', (data) => {
    if (data.sender_id !== currentUserId) {
        data.is_own = false;
        appendMessage(data);
        scrollToBottom();
    }
});

socket.on('user_typing', (data) => {
    const indicator = document.getElementById('typing-indicator');
    if (indicator && data.user_id !== currentUserId) {
        indicator.textContent = `${data.user_name} is typing...`;
        indicator.classList.remove('hidden');
    }
});

socket.on('user_stop_typing', (data) => {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.classList.add('hidden');
    }
});

socket.on('status', (data) => {
    console.log(data.msg);
});

// Helper functions
function scrollToBottom() {
    const container = document.getElementById('messages-container');
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    // Less than 1 minute
    if (diff < 60000) {
        return 'Just now';
    }

    // Less than 1 hour
    if (diff < 3600000) {
        const mins = Math.floor(diff / 60000);
        return `${mins} min${mins > 1 ? 's' : ''} ago`;
    }

    // Today
    if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    }

    // This year
    if (date.getFullYear() === now.getFullYear()) {
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    }

    // Other years
    return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

// Export for global use
window.ChatClient = {
    init: initChat,
    send: sendMessage
};
