from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from sqlalchemy import func
from app import db
from app.models import User, Project, Transaction, Application, Review

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
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
    """View all projects"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    
    query = Project.query
    
    if status:
        query = query.filter_by(status=status)
    
    projects = query.order_by(Project.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/projects.html', projects=projects)


@admin_bp.route('/transactions')
@admin_required
def transactions():
    """View all transactions"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status')
    
    query = Transaction.query
    
    if status:
        query = query.filter_by(status=status)
    
    transactions = query.order_by(Transaction.created_at.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('admin/transactions.html', transactions=transactions)
