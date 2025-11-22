from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Transaction, db
from sqlalchemy import or_

payment_history_bp = Blueprint('payment_history', __name__, url_prefix='/payment')

@payment_history_bp.route('/history')
@login_required
def payment_history():
    """View all payment transactions for current user"""
    
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Build base query based on user role
    if current_user.role == 'creator':
        query = Transaction.query.filter_by(creator_id=current_user.id)
    else:  # customer
        query = Transaction.query.filter_by(customer_id=current_user.id)
    
    # Apply status filter
    if status_filter == 'completed':
        query = query.filter(
            Transaction.customer_confirmed == True,
            Transaction.creator_confirmed == True
        )
    elif status_filter == 'pending':
        query = query.filter(
            or_(
                Transaction.customer_confirmed == False,
                Transaction.creator_confirmed == False
            )
        )
    elif status_filter == 'awaiting':
        query = query.filter(Transaction.customer_confirmed == False)
    
    # Apply search filter (search by project title)
    if search:
        query = query.join(Transaction.project).filter(
            Transaction.project.has(
                or_(
                    Transaction.project.title.ilike(f'%{search}%'),
                    Transaction.project.description.ilike(f'%{search}%')
                )
            )
        )
    
    # Order by most recent first
    query = query.order_by(Transaction.created_at.desc())
    
    # Paginate results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    transactions = pagination.items
    
    # Calculate statistics
    total_amount = db.session.query(db.func.sum(Transaction.amount))\
        .filter_by(creator_id=current_user.id if current_user.role == 'creator' else None,
                   customer_id=current_user.id if current_user.role == 'customer' else None)\
        .scalar() or 0
    
    completed_count = Transaction.query\
        .filter_by(creator_id=current_user.id if current_user.role == 'creator' else None,
                   customer_id=current_user.id if current_user.role == 'customer' else None)\
        .filter(Transaction.customer_confirmed == True, Transaction.creator_confirmed == True)\
        .count()
    
    pending_count = Transaction.query\
        .filter_by(creator_id=current_user.id if current_user.role == 'creator' else None,
                   customer_id=current_user.id if current_user.role == 'customer' else None)\
        .filter(or_(Transaction.customer_confirmed == False, Transaction.creator_confirmed == False))\
        .count()
    
    return render_template(
        'payment/history.html',
        transactions=transactions,
        pagination=pagination,
        status_filter=status_filter,
        search=search,
        total_amount=total_amount,
        completed_count=completed_count,
        pending_count=pending_count
    )
