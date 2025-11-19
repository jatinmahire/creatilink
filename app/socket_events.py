from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from app import socketio, db
from app.models import Message, Project
from datetime import datetime

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f'Client connected: {current_user.id if current_user.is_authenticated else "anonymous"}')


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f'Client disconnected: {current_user.id if current_user.is_authenticated else "anonymous"}')


@socketio.on('join_room')
def handle_join_room(data):
    """Join a project chat room"""
    if not current_user.is_authenticated:
        return
    
    project_id = data.get('project_id')
    project = Project.query.get(project_id)
    
    if not project:
        return
    
    # Check authorization
    if current_user.id not in [project.posted_by_id, project.assigned_to_id]:
        return
    
    room = f'project_{project_id}'
    join_room(room)
    emit('status', {'msg': f'{current_user.full_name} has joined the chat.'}, room=room)


@socketio.on('leave_room')
def handle_leave_room(data):
    """Leave a project chat room"""
    if not current_user.is_authenticated:
        return
    
    project_id = data.get('project_id')
    room = f'project_{project_id}'
    leave_room(room)
    emit('status', {'msg': f'{current_user.full_name} has left the chat.'}, room=room)


@socketio.on('send_message')
def handle_send_message(data):
    """Send a message in project chat"""
    if not current_user.is_authenticated:
        return
    
    project_id = data.get('project_id')
    content = data.get('content')
    attachments = data.get('attachments')  # Optional file paths
    
    project = Project.query.get(project_id)
    
    if not project or not content:
        return
    
    # Check authorization
    if current_user.id not in [project.posted_by_id, project.assigned_to_id]:
        return
    
    # Create message
    message = Message(
        project_id=project_id,
        sender_id=current_user.id,
        content=content,
        attachments=attachments
    )
    db.session.add(message)
    db.session.commit()
    
    # Broadcast to room
    room = f'project_{project_id}'
    emit('new_message', {
        'id': message.id,
        'sender_id': current_user.id,
        'sender_name': current_user.full_name,
        'sender_image': current_user.profile_image or '/static/images/default-avatar.png',
        'content': content,
        'attachments': attachments,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'is_own': False  # Receivers will check this
    }, room=room)


@socketio.on('typing')
def handle_typing(data):
    """Handle typing indicator"""
    if not current_user.is_authenticated:
        return
    
    project_id = data.get('project_id')
    room = f'project_{project_id}'
    
    emit('user_typing', {
        'user_id': current_user.id,
        'user_name': current_user.full_name
    }, room=room, include_self=False)


@socketio.on('stop_typing')
def handle_stop_typing(data):
    """Handle stop typing indicator"""
    if not current_user.is_authenticated:
        return
    
    project_id = data.get('project_id')
    room = f'project_{project_id}'
    
    emit('user_stop_typing', {
        'user_id': current_user.id
    }, room=room, include_self=False)
