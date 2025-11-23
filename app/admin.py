    """Decorator to require admin access"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/')
@admin_required
def dashboard():
    """Admin dashboard"""
    # User statistics
    total_users = User.query.count()
    total_customers = User.query.filter_by(role='customer').count()
    total_creators = User.query.filter_by(role='creator').count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Project statistics
    total_projects = Project.query.count()
    open_projects = Project.query.filter_by(status='open').count()
    active_projects = Project.query.filter(Project.status.in_(['assigned', 'in_progress'])).count()
    completed_projects = Project.query.filter_by(status='completed').count()
    
    # Transaction statistics
    total_transactions = Transaction.query.filter_by(status='completed').count()
    total_revenue = db.session.query(func.sum(Transaction.amount)).filter_by(status='completed').scalar() or 0
    
    # Platform fee (assume 10%)
    platform_fee = total_revenue * 0.10
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Recent projects
    recent_projects = Project.query.order_by(Project.created_at.desc()).limit(10).all()
    
    # Recent transactions
    recent_transactions = Transaction.query.filter_by(status='completed').order_by(Transaction.created_at.desc()).limit(10).all()
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_customers=total_customers,
        total_creators=total_creators,
        active_users=active_users,
        total_projects=total_projects,
        open_projects=open_projects,
        active_projects=active_projects,
        completed_projects=completed_projects,
        total_transactions=total_transactions,
        total_revenue=total_revenue,
        platform_fee=platform_fee,
        recent_users=recent_users,
        recent_projects=recent_projects,
        recent_transactions=recent_transactions
    )


@admin_bp.route('/users')
@admin_required
def users():
    """Manage users"""
    page = request.args.get('page', 1, type=int)
    role = request.args.get('role')
    search = request.args.get('search')
    
    query = User.query
    
    if role:
        query = query.filter_by(role=role)
    if search:
        query = query.filter(
            (User.full_name.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )
    
    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """Ban or unban a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-ban
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot ban yourself'}), 400
    
    # Prevent banning other admins
    if user.is_admin:
        return jsonify({'error': 'Cannot ban admin users'}), 400
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.full_name} has been {status}.', 'success')
    
    return jsonify({'success': True, 'is_active': user.is_active}), 200


@admin_bp.route('/users/<int:user_id>/details')
@admin_required
def user_details(user_id):
    """Get user details for modal"""
    user = User.query.get_or_404(user_id)
    
    # Get user's projects
    if user.role == 'customer':
        projects = Project.query.filter_by(posted_by_id=user.id).all()
        projects_data = [{
            'id': p.id,
            'title': p.title,
            'budget': p.budget,
            'status': p.status,
            'created_at': p.created_at.strftime('%Y-%m-%d')
        } for p in projects]
    else:
        projects = Project.query.filter_by(assigned_to_id=user.id).all()
        projects_data = [{
            'id': p.id,
            'title': p.title,
            'budget': p.budget,
            'status': p.status,
            'created_at': p.created_at.strftime('%Y-%m-%d')
        } for p in projects]
    
    # Get transactions
    if user.role == 'customer':
        transactions = Transaction.query.filter_by(customer_id=user.id).all()
    else:
        transactions = Transaction.query.filter_by(creator_id=user.id).all()
    
    total_spent = sum(t.amount for t in transactions if t.status == 'completed')
    
    # Get reviews
    reviews = Review.query.filter_by(creator_id=user.id).all() if user.role == 'creator' else []
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'full_name': user.full_name,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'is_admin': user.is_admin,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M'),
            'profile_image': user.profile_image or '/static/images/default-avatar.png',
            'bio': user.bio or 'No bio',
            'skills': user.skills or 'N/A',
            'portfolio_url': user.portfolio_url or 'N/A'
        },
        'stats': {
            'total_projects': len(projects),
            'total_spent': total_spent,
            'avg_rating': round(avg_rating, 1),
            'total_reviews': len(reviews),
            'total_transactions': len(transactions)
        },
        'projects': projects_data[:5],
        'recent_activity': f"Last active: {user.created_at.strftime('%Y-%m-%d')}"
    })


@admin_bp.route('/users/<int:user_id>/ban', methods=['POST'])
@admin_required
def ban_user(user_id):
    """Ban user with reason"""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-ban
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot ban yourself'}), 400
    
    # Prevent banning other admins
    if user.is_admin:
        return jsonify({'error': 'Cannot ban admin users'}), 400
    
    reason = request.form.get('reason', 'No reason provided')
    
    user.is_active = False
    db.session.commit()
    
    # TODO: Add to ban_logs table when created in Phase 6
    
    return jsonify({'success': True, 'message': f'User {user.full_name} has been banned'}), 200


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete user account"""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-delete
    if user.id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    # Prevent deleting other admins
    if user.is_admin:
        return jsonify({'error': 'Cannot delete admin users'}), 400
    
    # TODO: Handle cascading deletes properly
    # For now, just deactivate
    user.is_active = False
    db.session.commit()
    
    flash(f'User {user.full_name} has been deactivated.', 'success')
    return jsonify({'success': True}), 200


@admin_bp.route('/users/<int:user_id>/verify', methods=['POST'])
@admin_required
def verify_creator(user_id):
    """Verify a creator"""
    user = User.query.get_or_404(user_id)
    
    if user.role != 'creator':
        return jsonify({'error': 'Only creators can be verified'}), 400
    
    # Toggle verification (assuming we'll add verified field to User model)
    # For now, use a placeholder
    # user.is_verified = not getattr(user, 'is_verified', False)
    # db.session.commit()
    
    flash(f'Creator {user.full_name} verification toggled.', 'success')
    return jsonify({'success': True, 'message': 'Verification status updated'}), 200


@admin_bp.route('/users/<int:user_id>/promote', methods=['POST'])
@admin_required
def promote_to_admin(user_id):
    """Promote user to admin"""
    user = User.query.get_or_404(user_id)
    
    if user.is_admin:
        return jsonify({'error': 'User is already an admin'}), 400
    
    user.is_admin = True
    db.session.commit()
    
    flash(f'{user.full_name} has been promoted to admin.', 'success')
    return jsonify({'success': True, 'message': 'User promoted to admin'}), 200


@admin_bp.route('/users/export')
@admin_required
def export_users():
    """Export all users to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    users = User.query.all()
    
    si = StringIO()
    writer = csv.writer(si)
    
    # Header
    writer.writerow(['ID', 'Name', 'Email', 'Role', 'Status', 'Admin', 'Joined'])
    
    # Data
    for user in users:
        writer.writerow([
            user.id,
            user.full_name,
            user.email,
            user.role,
            'Active' if user.is_active else 'Banned',
            'Yes' if user.is_admin else 'No',
            user.created_at.strftime('%Y-%m-%d')
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=users_export.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output


@admin_bp.route('/projects')
@admin_required
def projects():
    """View all projects with advanced management"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    search = request.args.get('search')
    min_budget = request.args.get('min_budget', type=float)
    max_budget = request.args.get('max_budget', type=float)
    
    query = Project.query
    
    # Filters
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.filter(Project.title.ilike(f'%{search}%'))
    if min_budget:
        query = query.filter(Project.budget >= min_budget)
    if max_budget:
        query = query.filter(Project.budget <= max_budget)
    
    projects_list = query.order_by(Project.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    # Analytics
    total_projects = Project.query.count()
    open_projects = Project.query.filter_by(status='open').count()
    in_progress = Project.query.filter(Project.status.in_(['assigned', 'in_progress'])).count()
    completed = Project.query.filter_by(status='completed').count()
    deleted = Project.query.filter(Project.deleted_at.isnot(None)).count()
    
    # Budget analytics
    total_budget = db.session.query(func.sum(Project.budget)).scalar() or 0
    avg_budget = db.session.query(func.avg(Project.budget)).scalar() or 0
    
    return render_template(
        'admin/projects.html',
        projects=projects_list,
        total_projects=total_projects,
        open_projects=open_projects,
        in_progress=in_progress,
        completed=completed,
        deleted=deleted,
        total_budget=total_budget,
        avg_budget=avg_budget
    )


@admin_bp.route('/projects/<int:project_id>/details')
@admin_required
def project_details(project_id):
    """Get project details for modal"""
    project = Project.query.get_or_404(project_id)
    
    # Get applications count
    applications_count = Application.query.filter_by(project_id=project.id).count()
    
    return jsonify({
        'success': True,
        'project': {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'budget': project.budget,
            'deadline': project.deadline.strftime('%Y-%m-%d') if project.deadline else 'No deadline',
            'status': project.status,
            'category': project.category or 'N/A',
            'created_at': project.created_at.strftime('%Y-%m-%d %H:%M'),
            'is_deleted': project.deleted_at is not None
        },
        'customer': {
            'id': project.posted_by.id,
            'name': project.posted_by.full_name,
            'email': project.posted_by.email
        },
        'creator': {
            'id': project.assigned_to.id if project.assigned_to else None,
            'name': project.assigned_to.full_name if project.assigned_to else 'Not assigned',
            'email': project.assigned_to.email if project.assigned_to else 'N/A'
        } if project.assigned_to else None,
        'stats': {
            'applications': applications_count,
            'views': 0  # TODO: Add view tracking
        }
    })


@admin_bp.route('/projects/<int:project_id>/force-complete', methods=['POST'])
@admin_required
def force_complete_project(project_id):
    """Force complete a project"""
    project = Project.query.get_or_404(project_id)
    
    if project.status == 'completed':
        return jsonify({'error': 'Project already completed'}), 400
    
    # Update project
    project.status = 'completed'
    
    # Also complete transaction if exists
    transaction = Transaction.query.filter_by(project_id=project.id).first()
    if transaction and transaction.status != 'completed':
        transaction.status = 'completed'
        transaction.customer_confirmed = True
        transaction.creator_confirmed = True
        transaction.payment_confirmed_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'Project "{project.title}" marked as completed', 'success')
    return jsonify({'success': True, 'message': 'Project completed'}), 200


@admin_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@admin_required
def delete_project(project_id):
    """Soft delete a project"""
    project = Project.query.get_or_404(project_id)
    
    if project.deleted_at:
        return jsonify({'error': 'Project already deleted'}), 400
    
    reason = request.form.get('reason', 'Admin deletion')
    
    # Soft delete
    project.deleted_at = datetime.utcnow()
    project.deleted_by_id = current_user.id
    project.deletion_reason = reason
    
    db.session.commit()
    
    flash(f'Project "{project.title}" has been deleted', 'success')
    return jsonify({'success': True, 'message': 'Project deleted'}), 200


@admin_bp.route('/projects/<int:project_id>/reassign', methods=['POST'])
@admin_required
def reassign_project(project_id):
    """Reassign project to different creator"""
    project = Project.query.get_or_404(project_id)
    new_creator_id = request.form.get('creator_id', type=int)
    
    if not new_creator_id:
        return jsonify({'error': 'Creator ID required'}), 400
    
    new_creator = User.query.get_or_404(new_creator_id)
    
    if new_creator.role != 'creator':
        return jsonify({'error': 'User must be a creator'}), 400
    
    old_creator = project.assigned_to
    project.assigned_to_id = new_creator_id
    project.status = 'assigned'
    
    db.session.commit()
    
    flash(f'Project reassigned from {old_creator.full_name if old_creator else "None"} to {new_creator.full_name}', 'success')
    return jsonify({'success': True, 'message': 'Project reassigned'}), 200


@admin_bp.route('/projects/export')
@admin_required
def export_projects():
    """Export all projects to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    projects = Project.query.all()
    
    si = StringIO()
    writer = csv.writer(si)
    
    # Header
    writer.writerow(['ID', 'Title', 'Budget', 'Status', 'Customer', 'Creator', 'Created', 'Deleted'])
    
    # Data
    for p in projects:
        writer.writerow([
            p.id,
            p.title,
            p.budget,
            p.status,
            p.posted_by.full_name,
            p.assigned_to.full_name if p.assigned_to else 'Not assigned',
            p.created_at.strftime('%Y-%m-%d'),
            'Yes' if p.deleted_at else 'No'
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=projects_export.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output


@admin_bp.route('/transactions')
@admin_required
def transactions():
    """View all transactions with advanced filters"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    search = request.args.get('search')
    min_amount = request.args.get('min_amount', type=float)
    max_amount = request.args.get('max_amount', type=float)
    
    query = Transaction.query
    
    # Filters
    if status:
        query = query.filter_by(status=status)
    if search:
        # Search by project title or user names
        query = query.join(Project).filter(Project.title.ilike(f'%{search}%'))
    if min_amount:
        query = query.filter(Transaction.amount >= min_amount)
    if max_amount:
        query = query.filter(Transaction.amount <= max_amount)
    
    transactions = query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    # Analytics
    total_completed = db.session.query(func.sum(Transaction.amount)).filter_by(status='completed').scalar() or 0
    total_pending = db.session.query(func.sum(Transaction.amount)).filter_by(status='pending').scalar() or 0
    total_refunded = db.session.query(func.sum(Transaction.amount)).filter_by(status='refunded').scalar() or 0
    platform_earnings = total_completed * 0.10  # 10% platform fee
    
    return render_template(
        'admin/transactions.html',
        transactions=transactions,
        total_completed=total_completed,
        total_pending=total_pending,
        total_refunded=total_refunded,
        platform_earnings=platform_earnings
    )


@admin_bp.route('/transactions/<int:transaction_id>/details')
@admin_required
def transaction_details(transaction_id):
    """Get transaction details for modal"""
    txn = Transaction.query.get_or_404(transaction_id)
    
    return jsonify({
        'success': True,
        'transaction': {
            'id': txn.id,
            'amount': txn.amount,
            'status': txn.status,
            'created_at': txn.created_at.strftime('%Y-%m-%d %H:%M'),
            'payment_confirmed_at': txn.payment_confirmed_at.strftime('%Y-%m-%d %H:%M') if txn.payment_confirmed_at else 'N/A',
            'customer_confirmed': txn.customer_confirmed,
            'creator_confirmed': txn.creator_confirmed,
            'payment_screenshot': txn.payment_screenshot
        },
        'project': {
            'id': txn.project.id,
            'title': txn.project.title,
            'budget': txn.project.budget,
            'status': txn.project.status
        },
        'customer': {
            'id': txn.customer.id,
            'name': txn.customer.full_name,
            'email': txn.customer.email
        },
        'creator': {
            'id': txn.creator.id,
            'name': txn.creator.full_name,
            'email': txn.creator.email
        }
    })


@admin_bp.route('/transactions/<int:transaction_id>/refund', methods=['POST'])
@admin_required
def refund_transaction(transaction_id):
    """Manual refund for a transaction"""
    txn = Transaction.query.get_or_404(transaction_id)
    
    if txn.status == 'refunded':
        return jsonify({'error': 'Transaction already refunded'}), 400
    
    reason = request.form.get('reason', 'Admin refund')
    
    # Update transaction status
    txn.status = 'refunded'
    db.session.commit()
    
    # TODO: Add notification to customer and creator
    
    flash(f'Transaction #{txn.id} has been refunded. Amount: ₹{txn.amount}', 'success')
    return jsonify({'success': True, 'message': 'Transaction refunded'}), 200


@admin_bp.route('/transactions/<int:transaction_id>/release', methods=['POST'])
@admin_required  
def release_escrow(transaction_id):
    """Force release escrow payment to creator"""
    txn = Transaction.query.get_or_404(transaction_id)
    
    if txn.status == 'completed':
        return jsonify({'error': 'Transaction already completed'}), 400
    
    if txn.status == 'refunded':
        return jsonify({'error': 'Transaction was refunded'}), 400
    
    # Mark as completed
    txn.status = 'completed'
    txn.customer_confirmed = True
    txn.creator_confirmed = True
    txn.payment_confirmed_at = datetime.utcnow()
    
    # Also mark project as completed if not already
    if txn.project.status != 'completed':
        txn.project.status = 'completed'
    
    db.session.commit()
    
    # TODO: Add notification to creator about payment release
    
    flash(f'Escrow released! ₹{txn.amount} paid to {txn.creator.full_name}', 'success')
    return jsonify({'success': True, 'message': 'Escrow released'}), 200


@admin_bp.route('/transactions/export')
@admin_required
def export_transactions():
    """Export all transactions to CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    transactions = Transaction.query.all()
    
    si = StringIO()
    writer = csv.writer(si)
    
    # Header
    writer.writerow(['ID', 'Amount', 'Status', 'Project', 'Customer', 'Creator', 'Date', 'Customer Confirmed', 'Creator Confirmed'])
    
    # Data
    for txn in transactions:
        writer.writerow([
            txn.id,
            txn.amount,
            txn.status,
            txn.project.title,
            txn.customer.full_name,
            txn.creator.full_name,
            txn.created_at.strftime('%Y-%m-%d'),
            'Yes' if txn.customer_confirmed else 'No',
            'Yes' if txn.creator_confirmed else 'No'
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=transactions_export.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output


# ========== DISPUTE MANAGEMENT ==========

@admin_bp.route('/disputes')
@admin_required
def disputes():
    """View all disputes with priority sorting"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    
    query = Dispute.query
    
    if status:
        query = query.filter_by(status=status)
    
    # Priority sort: open disputes first, then by age
    disputes_list = query.order_by(
        Dispute.status.desc(),  # Open first
        Dispute.created_at.desc()  # Oldest first
    ).paginate(page=page, per_page=20, error_out=False)
    
    # Statistics
    total_open = Dispute.query.filter_by(status='open').count()
    total_resolved = Dispute.query.filter_by(status='resolved').count()
    old_disputes = Dispute.query.filter(
        Dispute.status == 'open',
        Dispute.created_at < datetime.utcnow() - timedelta(days=2)
    ).count()
    
    return render_template(
        'admin/disputes.html',
        disputes=disputes_list,
        total_open=total_open,
        total_resolved=total_resolved,
        old_disputes=old_disputes
    )


@admin_bp.route('/disputes/<int:dispute_id>/details')
@admin_required
def dispute_details(dispute_id):
    """Get dispute details for modal"""
    dispute = Dispute.query.get_or_404(dispute_id)
    txn = dispute.transaction
    
    # Calculate age in hours
    age_hours = (datetime.utcnow() - dispute.created_at).total_seconds() / 3600
    
    return jsonify({
        'success': True,
        'dispute': {
            'id': dispute.id,
            'type': dispute.dispute_type,
            'description': dispute.description,
            'status': dispute.status,
            'created_at': dispute.created_at.strftime('%Y-%m-%d %H:%M'),
            'resolved_at': dispute.resolved_at.strftime('%Y-%m-%d %H:%M') if dispute.resolved_at else None,
            'resolution_notes': dispute.resolution_notes,
            'age_hours': round(age_hours, 1)
        },
        'transaction': {
            'id': txn.id,
            'amount': txn.amount,
            'status': txn.status
        },
        'project': {
            'id': txn.project.id,
            'title': txn.project.title,
            'status': txn.project.status
        },
        'raised_by': {
            'id': dispute.raised_by.id,
            'name': dispute.raised_by.full_name,
            'email': dispute.raised_by.email,
            'role': dispute.raised_by.role
        },
        'customer': {
            'id': txn.customer.id,
            'name': txn.customer.full_name,
            'email': txn.customer.email
        },
        'creator': {
            'id': txn.creator.id,
            'name': txn.creator.full_name,
            'email': txn.creator.email
        }
    })


@admin_bp.route('/disputes/<int:dispute_id>/resolve', methods=['POST'])
@admin_required
def resolve_dispute_admin(dispute_id):
    """Admin resolves a dispute"""
    dispute = Dispute.query.get_or_404(dispute_id)
    
    if dispute.status == 'resolved':
        return jsonify({'error': 'Dispute already resolved'}), 400
    
    resolution_notes = request.form.get('notes')
    
    if not resolution_notes:
        return jsonify({'error': 'Resolution notes required'}), 400
    
    # Update dispute
    dispute.status = 'resolved'
    dispute.resolution_notes = resolution_notes
    dispute.resolved_by_id = current_user.id
    dispute.resolved_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Dispute #{dispute.id} resolved successfully', 'success')
    return jsonify({'success': True, 'message': 'Dispute resolved'}), 200


@admin_bp.route('/disputes/<int:dispute_id>/refund', methods=['POST'])
@admin_required
def refund_from_dispute(dispute_id):
    """Refund transaction and resolve dispute"""
    dispute = Dispute.query.get_or_404(dispute_id)
    txn = dispute.transaction
    
    if txn.status == 'refunded':
        return jsonify({'error': 'Transaction already refunded'}), 400
    
    resolution_notes = request.form.get('notes', 'Refunded by admin from dispute')
    
    # Refund transaction
    txn.status = 'refunded'
    
    # Resolve dispute
    dispute.status = 'resolved'
    dispute.resolution_notes = f'REFUNDED: {resolution_notes}'
    dispute.resolved_by_id = current_user.id
    dispute.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'Transaction refunded & dispute resolved. Amount: ₹{txn.amount}', 'success')
    return jsonify({'success': True, 'message': 'Refunded and resolved'}), 200


@admin_bp.route('/disputes/<int:dispute_id>/release', methods=['POST'])
@admin_required
def release_from_dispute(dispute_id):
    """Release payment to creator and resolve dispute"""
    dispute = Dispute.query.get_or_404(dispute_id)
    txn = dispute.transaction
    
    if txn.status == 'completed':
        return jsonify({'error': 'Transaction already completed'}), 400
    
    resolution_notes = request.form.get('notes', 'Payment released by admin from dispute')
    
    # Release payment
    txn.status = 'completed'
    txn.customer_confirmed = True
    txn.creator_confirmed = True
    txn.payment_confirmed_at = datetime.utcnow()
    
    # Complete project if needed
    if txn.project.status != 'completed':
        txn.project.status = 'completed'
    
    # Resolve dispute
    dispute.status = 'resolved'
    dispute.resolution_notes = f'PAYMENT RELEASED: {resolution_notes}'
    dispute.resolved_by_id = current_user.id
    dispute.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'Payment released to creator & dispute resolved. Amount: ₹{txn.amount}', 'success')
    return jsonify({'success': True, 'message': 'Payment released and resolved'}), 200


@admin_bp.route('/disputes/<int:dispute_id>/ban-user/<int:user_id>', methods=['POST'])
@admin_required
def ban_from_dispute(dispute_id, user_id):
    """Ban a user directly from dispute"""
    user = User.query.get_or_404(user_id)
    dispute = Dispute.query.get_or_404(dispute_id)
    
    # Prevent banning admins
    if user.is_admin:
        return jsonify({'error': 'Cannot ban admin users'}), 400
    
    reason = request.form.get('reason', f'Banned from dispute #{dispute_id}')
    
    # Ban user
    user.is_active = False
    
    # Optionally resolve dispute
    if dispute.status != 'resolved':
        dispute.status = 'resolved'
        dispute.resolution_notes = f'USER BANNED: {user.full_name} - {reason}'
        dispute.resolved_by_id = current_user.id
        dispute.resolved_at = datetime.utcnow()
    
    db.session.commit()
    
    flash(f'User {user.full_name} has been banned. Dispute resolved.', 'success')
    return jsonify({'success': True, 'message': 'User banned'}), 200


# ========== ANALYTICS DASHBOARD ==========

@admin_bp.route('/analytics')
@admin_required
def analytics():
    """Analytics dashboard with charts"""
    from datetime import timedelta
    
    # Summary stats
    total_users = User.query.count()
    total_projects = Project.query.count()
    active_projects = Project.query.filter(Project.status.in_(['assigned', 'in_progress'])).count()
    total_revenue = db.session.query(func.sum(Transaction.amount)).filter_by(status='completed').scalar() or 0
    avg_project_value = db.session.query(func.avg(Project.budget)).scalar() or 0
    platform_earnings = total_revenue * 0.10
    
    # Growth calculations (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    users_last_month = User.query.filter(User.created_at >= thirty_days_ago).count()
    users_previous_month = total_users - users_last_month
    user_growth = ((users_last_month / users_previous_month) * 100) if users_previous_month > 0 else 0
    
    revenue_last_month = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.status == 'completed',
        Transaction.created_at >= thirty_days_ago
    ).scalar() or 0
   revenue_previous_month = total_revenue - revenue_last_month
    revenue_growth = ((revenue_last_month / revenue_previous_month) * 100) if revenue_previous_month > 0 else 0
    
    # User growth data (last 30 days)
    user_growth_labels = []
    user_growth_data = []
    for i in range(30, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        count = User.query.filter(func.date(User.created_at) == date.date()).count()
        user_growth_labels.append(date.strftime('%b %d'))
        user_growth_data.append(count)
    
    # Revenue data (last 30 days)
    revenue_labels = []
    revenue_data = []
    for i in range(30, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        amount = db.session.query(func.sum(Transaction.amount)).filter(
            Transaction.status == 'completed',
            func.date(Transaction.created_at) == date.date()
        ).scalar() or 0
        revenue_labels.append(date.strftime('%b %d'))
        revenue_data.append(float(amount))
    
    # Project activity data
    project_labels = []
    projects_created = []
    projects_completed = []
    for i in range(30, -1, -1):
        date = datetime.utcnow() - timedelta(days=i)
        created = Project.query.filter(func.date(Project.created_at) == date.date()).count()
        completed = Project.query.filter(
            func.date(Project.created_at) == date.date(),
            Project.status == 'completed'
        ).count()
        project_labels.append(date.strftime('%b %d'))
        projects_created.append(created)
        projects_completed.append(completed)
    
    # Category breakdown
    category_data_raw = db.session.query(
        Project.category,
        func.count(Project.id)
    ).group_by(Project.category).all()
    
    category_labels = [cat if cat else 'Uncategorized' for cat, _ in category_data_raw]
    category_data = [count for _, count in category_data_raw]
    
    # Top customers
    top_customers_raw = db.session.query(
        User,
        func.count(Project.id).label('project_count'),
        func.sum(Transaction.amount).label('total_spent')
    ).join(Project, User.id == Project.posted_by_id)\
     .join(Transaction, Project.id == Transaction.project_id)\
     .filter(Transaction.status == 'completed')\
     .group_by(User.id)\
     .order_by(func.sum(Transaction.amount).desc())\
     .limit(5).all()
    
    top_customers = [{
        'full_name': user.full_name,
        'project_count': count,
        'total_spent': float(spent) if spent else 0
    } for user, count, spent in top_customers_raw]
    
    # Top creators
    top_creators_raw = db.session.query(
        User,
        func.count(Project.id).label('project_count'),
        func.sum(Transaction.amount).label('total_earned')
    ).join(Project, User.id == Project.assigned_to_id)\
     .join(Transaction, Project.id == Transaction.project_id)\
     .filter(Transaction.status == 'completed')\
     .group_by(User.id)\
     .order_by(func.sum(Transaction.amount).desc())\
     .limit(5).all()
    
    top_creators = [{
        'full_name': user.full_name,
        'project_count': count,
        'total_earned': float(earned) if earned else 0
    } for user, count, earned in top_creators_raw]
    
    # Platform stats
    completed_projects = Project.query.filter_by(status='completed').count()
    success_rate = (completed_projects / total_projects * 100) if total_projects > 0 else 0
    
    # Avg completion time
    avg_completion_days = 14  # TODO: Calculate from actual data
    
    # Dispute rate
    total_disputes = Dispute.query.count()
    total_transactions = Transaction.query.count()
    dispute_rate = (total_disputes / total_transactions * 100) if total_transactions > 0 else 0
    
    return render_template(
        'admin/analytics.html',
        total_users=total_users,
        user_growth=round(user_growth, 1),
        total_revenue=total_revenue,
        revenue_growth=round(revenue_growth, 1),
        total_projects=total_projects,
        active_projects=active_projects,
        avg_project_value=avg_project_value,
        platform_earnings=platform_earnings,
        user_growth_labels=user_growth_labels,
        user_growth_data=user_growth_data,
        revenue_labels=revenue_labels,
        revenue_data=revenue_data,
        project_labels=project_labels,
        projects_created=projects_created,
        projects_completed=projects_completed,
        category_labels=category_labels,
        category_data=category_data,
        top_customers=top_customers,
        top_creators=top_creators,
        success_rate=success_rate,
        avg_completion_days=avg_completion_days,
        dispute_rate=dispute_rate
    )


@admin_bp.route('/analytics/export')
@admin_required
def export_analytics():
    """Export analytics report"""
    import csv
    from io import StringIO
    from flask import make_response
    
    si = StringIO()
    writer = csv.writer(si)
    
    # Header
    writer.writerow(['Analytics Report - CreatiLink Admin'])
    writer.writerow([])
    writer.writerow(['Metric', 'Value'])
    
    # Data
    total_users = User.query.count()
    total_projects = Project.query.count()
    total_revenue = db.session.query(func.sum(Transaction.amount)).filter_by(status='completed').scalar() or 0
    
    writer.writerow(['Total Users', total_users])
    writer.writerow(['Total Projects', total_projects])
    writer.writerow(['Total Revenue', f'₹{total_revenue}'])
    writer.writerow(['Platform Earnings (10%)', f'₹{total_revenue * 0.10}'])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=analytics_report.csv"
    output.headers["Content-type"] = "text/csv"
    
    return output
