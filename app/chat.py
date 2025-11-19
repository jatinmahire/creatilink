from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Project, Message
from datetime import datetime

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/<int:project_id>')
@login_required
def room(project_id):
    """Chat room for a project"""
    project = Project.query.get_or_404(project_id)
    
    # Check authorization (customer or assigned creator)
    if current_user.id not in [project.posted_by_id, project.assigned_to_id]:
        from flask import flash, redirect, url_for
        flash('You do not have access to this chat.', 'warning')
        return redirect(url_for('main.index'))
    
    # Get other participant
    if current_user.id == project.posted_by_id:
        other_user = project.creator
    else:
        other_user = project.customer
    
    return render_template('chat/room.html', project=project, other_user=other_user)


@chat_bp.route('/api/messages/<int:project_id>')
@login_required
def get_messages(project_id):
    """Get message history for a project"""
    project = Project.query.get_or_404(project_id)
    
    # Check authorization
    if current_user.id not in [project.posted_by_id, project.assigned_to_id]:
        return jsonify({'error': 'Unauthorized'}), 403
    
    messages = Message.query.filter_by(project_id=project_id).order_by(Message.created_at.asc()).all()
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'sender_id': msg.sender_id,
            'sender_name': msg.sender.full_name,
            'content': msg.content,
            'attachments': msg.attachments,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_own': msg.sender_id == current_user.id
        })
    
    return jsonify(messages_data)
