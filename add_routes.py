# Add delete and leave routes to projects.py
with open('app/projects.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the end of the file and append new routes
new_routes = '''

@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """Soft delete project (customer or creator)"""
    project = Project.query.get_or_404(project_id)
    
    # Authorization check - only customer or assigned creator can delete
    if current_user.id not in [project.posted_by_id, project.assigned_to_id]:
        return jsonify({'error': 'Unauthorized'}), 403
    
    reason = request.form.get('reason', 'No reason provided')
    
    # Soft delete
    project.deleted_by_id = current_user.id
    project.deleted_at = datetime.utcnow()
    project.deletion_reason = reason
    db.session.commit()
    
    # Notify the other party
    if current_user.id == project.posted_by_id:
        # Customer deleted - notify creator if assigned
        if project.assigned_to_id:
            create_notification(
                user_id=project.assigned_to_id,
                notification_type='project_deleted',
                title='🗑️ Project Deleted by Customer',
                message=f'Customer deleted project "{project.title}". Reason: {reason}',
                project_id=project.id
            )
    else:
        # Creator deleted - notify customer
        create_notification(
            user_id=project.posted_by_id,
            notification_type='project_deleted',
            title='🗑️ Project Deleted by Creator',
            message=f'Creator deleted project "{project.title}". Reason: {reason}',
            project_id=project.id
        )
    
    flash('Project deleted successfully', 'success')
    return jsonify({'success': True})


@projects_bp.route('/<int:project_id>/leave', methods=['POST'])
@login_required
def leave_project(project_id):
    """Creator leaves assigned project"""
    project = Project.query.get_or_404(project_id)
    
    # Only assigned creator can leave
    if current_user.id != project.assigned_to_id:
        return jsonify({'error': 'Unauthorized - you are not assigned to this project'}), 403
    
    reason = request.form.get('reason', 'No reason provided')
    
    # Mark as left
    project.creator_left = True
    project.creator_left_at = datetime.utcnow()
    project.assigned_to_id = None  # Unassign creator
    project.status = 'open'  # Back to open status
    db.session.commit()
    
    # Notify customer
    create_notification(
        user_id=project.posted_by_id,
        notification_type='creator_left_project',
        title='👋 Creator Left Your Project',
        message=f'Creator {current_user.full_name} doesn\\'t want to work on "{project.title}". Reason: {reason}. The project is now open for new applications.',
        project_id=project.id
    )
    
    flash('You have left this project. Customer has been notified.', 'info')
    return jsonify({'success': True})
'''

# Append new routes
content += new_routes

with open('app/projects.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added delete and leave routes to projects.py")
