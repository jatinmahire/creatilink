from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app import db
from app.models import Dispute, Transaction, Project, User
from app.notification_helpers import create_notification

disputes_bp = Blueprint('disputes', __name__, url_prefix='/dispute')

@disputes_bp.route('/create/<int:transaction_id>', methods=['POST'])
@login_required
def create_dispute(transaction_id):
    """Raise a new dispute for a transaction"""
    transaction = Transaction.query.get_or_404(transaction_id)
    
    # Check authorization - only customer or creator can raise dispute
    if current_user.id not in [transaction.customer_id, transaction.creator_id]:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get form data
    dispute_type = request.form.get('type')
    description = request.form.get('description')
    
    if not dispute_type or not description:
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Create dispute
    dispute = Dispute(
        transaction_id=transaction_id,
        raised_by_id=current_user.id,
        dispute_type=dispute_type,
        description=description,
        status='open'
    )
    db.session.add(dispute)
    db.session.commit()
    
    # Notify the other party
    other_user_id = transaction.creator_id if current_user.id == transaction.customer_id else transaction.customer_id
    create_notification(
        user_id=other_user_id,
        notification_type='dispute_raised',
        title='⚠️ Dispute Raised',
        message=f'A dispute has been raised for project "{transaction.project.title}". Type: {dispute_type}',
        transaction_id=transaction_id
    )
    
    # Notify admin (user_id=1, assuming first user is admin)
    admin_user = User.query.filter_by(role='admin').first()
    if admin_user:
        create_notification(
            user_id=admin_user.id,
            notification_type='dispute_raised',
            title='⚠️ New Dispute Reported',
            message=f'Dispute raised for project "{transaction.project.title}" by {current_user.full_name}',
            transaction_id=transaction_id
        )
    
    flash('Dispute raised successfully. Admin will review and contact you.', 'info')
    return jsonify({'success': True})


@disputes_bp.route('/list')
@login_required
def list_disputes():
    """View all disputes for current user"""
    
    # Get disputes where user is involved
    disputes = Dispute.query.join(Transaction).filter(
        db.or_(
            Transaction.customer_id == current_user.id,
            Transaction.creator_id == current_user.id
        )
    ).order_by(Dispute.created_at.desc()).all()
    
    return render_template('dispute/list.html', disputes=disputes)


@disputes_bp.route('/<int:dispute_id>')
@login_required
def view_dispute(dispute_id):
    """View dispute details"""
    dispute = Dispute.query.get_or_404(dispute_id)
    transaction = dispute.transaction
    
    # Check authorization
    if current_user.id not in [transaction.customer_id, transaction.creator_id] and current_user.role != 'admin':
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template('dispute/detail.html', dispute=dispute)


@disputes_bp.route('/<int:dispute_id>/resolve', methods=['POST'])
@login_required
def resolve_dispute(dispute_id):
    """Admin resolves a dispute"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Unauthorized - Admin only'}), 403
    
    dispute = Dispute.query.get_or_404(dispute_id)
    resolution_notes = request.form.get('resolution_notes')
    
    if not resolution_notes:
        return jsonify({'error': 'Resolution notes required'}), 400
    
    # Update dispute
    dispute.status = 'resolved'
    dispute.resolution_notes = resolution_notes
    dispute.resolved_by_id = current_user.id
    dispute.resolved_at = datetime.utcnow()
    db.session.commit()
    
    # Notify both parties
    transaction = dispute.transaction
    for user_id in [transaction.customer_id, transaction.creator_id]:
        create_notification(
            user_id=user_id,
            notification_type='dispute_resolved',
            title='✅ Dispute Resolved',
            message=f'Your dispute for "{transaction.project.title}" has been resolved by admin.',
            transaction_id=transaction.id
        )
    
    flash('Dispute resolved successfully', 'success')
    return jsonify({'success': True})
