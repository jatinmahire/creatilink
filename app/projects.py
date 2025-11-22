from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from app import db
from app.models import Project, Application, User, Upload, Package, Review, Transaction
from app.notification_helpers import create_notification

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

@projects_bp.route('/')
def list_projects():
    """List and search projects"""
    # Get filter parameters
    category = request.args.get('category')
    min_budget = request.args.get('min_budget', type=float)
    max_budget = request.args.get('max_budget', type=float)
    search = request.args.get('search')
    status = request.args.get('status', 'open')
    sort_by = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    
    # Build query
    query = Project.query
    
    if category:
        query = query.filter_by(category=category)
    if min_budget:
        query = query.filter(Project.budget >= min_budget)
    if max_budget:
        query = query.filter(Project.budget <= max_budget)
    if search:
        query = query.filter(
            (Project.title.ilike(f'%{search}%')) |
            (Project.description.ilike(f'%{search}%'))
        )
    if status:
        query = query.filter_by(status=status)
    
    # Apply sorting
    if sort_by == 'oldest':
        query = query.order_by(Project.created_at.asc())
    elif sort_by == 'price_low':
        query = query.order_by(Project.budget.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Project.budget.desc())
    else:  # newest (default)
        query = query.order_by(Project.created_at.desc())
    
    # Paginate
    from flask import current_app
    per_page = current_app.config.get('PROJECTS_PER_PAGE', 12)
    projects = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('projects/list.html', projects=projects)


@projects_bp.route('/<int:project_id>')
def detail(project_id):
    """Project detail page"""
    project = Project.query.get_or_404(project_id)
    
    # Get applications for this project
    applications = Application.query.filter_by(project_id=project_id).order_by(Application.created_at.desc()).all()
    
    # Check if current user has applied
    user_application = None
    if current_user.is_authenticated and current_user.role == 'creator':
        user_application = Application.query.filter_by(
            project_id=project_id,
            creator_id=current_user.id
        ).first()
    
    return render_template(
        'projects/detail.html',
        project=project,
        applications=applications,
        user_application=user_application
    )


@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new project (customer only)"""
    if current_user.role != 'customer':
        flash('Only customers can post projects.', 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        from flask import current_app
        
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        budget = request.form.get('budget', type=float)
        deadline_str = request.form.get('deadline')
        
        # Validation
        if not all([title, description, category, budget]):
            flash('All fields are required.', 'danger')
            return render_template('projects/create.html')
        
        # Parse deadline
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid deadline format.', 'danger')
                return render_template('projects/create.html')
        
        # Create project
        project = Project(
            title=title,
            description=description,
            category=category,
            budget=budget,
            deadline=deadline,
            posted_by_id=current_user.id
        )
        db.session.add(project)
        db.session.commit()
        
        # Handle file attachments
        if 'attachments' in request.files:
            files = request.files.getlist('attachments')
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    filename = f"project_{project.id}_{timestamp}_{filename}"
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    
                    # Determine file type
                    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
                    if ext in ['jpg', 'jpeg', 'png', 'gif']:
                        file_type = 'image'
                    elif ext in ['mp4', 'mov', 'avi']:
                        file_type = 'video'
                    else:
                        file_type = 'document'
                    
                    upload = Upload(
                        owner_id=current_user.id,
                        file_path=f'/static/uploads/{filename}',
                        file_type=file_type,
                        file_size=os.path.getsize(filepath),
                        original_filename=file.filename,
                        upload_type='project'
                    )
                    db.session.add(upload)
        
        db.session.commit()
        flash('Project posted successfully!', 'success')
        return redirect(url_for('projects.detail', project_id=project.id))
    
    return render_template('projects/create.html')


@projects_bp.route('/<int:project_id>/apply', methods=['POST'])
@login_required
def apply(project_id):
    """Apply to a project (creator only)"""
    if current_user.role != 'creator':
        return jsonify({'error': 'Only creators can apply'}), 403
    
    project = Project.query.get_or_404(project_id)
    
    # Check if already applied
    existing = Application.query.filter_by(
        project_id=project_id,
        creator_id=current_user.id
    ).first()
    
    if existing:
        return jsonify({'error': 'You already applied to this project'}), 400
    
    # Check if project is still open
    if project.status != 'open':
        return jsonify({'error': 'This project is no longer accepting applications'}), 400
    
    quote = request.form.get('quote', type=float)
    message = request.form.get('message')
    delivery_days = request.form.get('delivery_days', type=int)
    
    if not quote:
        return jsonify({'error': 'Quote is required'}), 400
    
    application = Application(
        project_id=project_id,
        creator_id=current_user.id,
        quote=quote,
        message=message,
        delivery_days=delivery_days
    )
    db.session.add(application)
    db.session.commit()
    
    flash('Application submitted successfully!', 'success')
    return jsonify({'success': True}), 200


@projects_bp.route('/<int:project_id>/assign', methods=['POST'])
@login_required
def assign(project_id):
    """Assign a creator to project (customer only)"""
    project = Project.query.get_or_404(project_id)
    
    # Check ownership
    if project.posted_by_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    application_id = request.form.get('application_id', type=int)
    application = Application.query.get_or_404(application_id)
    
    # Assign creator
    project.assigned_to_id = application.creator_id
    project.status = 'assigned'
    application.status = 'accepted'
    
    # Reject other applications
    other_apps = Application.query.filter_by(project_id=project_id).filter(Application.id != application_id).all()
    for app in other_apps:
        app.status = 'rejected'
    
    db.session.commit()
    
    flash(f'Creator assigned successfully!', 'success')
    return jsonify({'success': True}), 200


@projects_bp.route('/<int:project_id>/submit_delivery', methods=['POST'])
@login_required
def submit_delivery(project_id):
    """Creator submits delivery via Drive link"""
    project = Project.query.get_or_404(project_id)
    
    # Only assigned creator can submit delivery
    if current_user.id != project.assigned_to_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Check if project is assigned
    if project.status != 'assigned':
        return jsonify({'error': 'Project is not in assigned status'}), 400
    
    delivery_link = request.form.get('delivery_link', '').strip()
    delivery_note = request.form.get('delivery_note', '').strip()
    
    # Validate link
    if not delivery_link:
        return jsonify({'error': 'Delivery link is required'}), 400
    
    # Validate link is from allowed domains
    allowed_domains = ['drive.google.com', 'dropbox.com', 'onedrive.live.com', '1drv.ms']
    if not any(domain in delivery_link.lower() for domain in allowed_domains):
        return jsonify({'error': 'Please use Google Drive, Dropbox, or OneDrive links only'}), 400
    
    # Update project
    project.delivery_link = delivery_link
    project.delivery_note = delivery_note
    project.delivered_at = datetime.utcnow()
    project.status = 'delivered'
    
    # Create pending transaction for payment
    # Get the application to find the quoted amount
    application = Application.query.filter_by(
        project_id=project_id,
        creator_id=current_user.id,
        status='accepted'
    ).first()
    
    if application:
        # Check if transaction already exists
        existing = Transaction.query.filter_by(project_id=project_id).first()
        if not existing:
            transaction = Transaction(
                project_id=project_id,
                customer_id=project.posted_by_id,
                creator_id=current_user.id,
                amount=application.quote,
                status='pending',
                type='full'
            )
            db.session.add(transaction)
            
            # Notify customer about delivery
            create_notification(
                user_id=project.posted_by_id,
                notification_type='delivery_submitted',
                title='🎉 Delivery Received!',
                message=f'{current_user.full_name} has submitted the delivery for "{project.title}". Please review and make payment.',
                project_id=project_id
            )
    
    db.session.commit()
    
    flash('Delivery submitted successfully!', 'success')
    return jsonify({'success': True}), 200


@projects_bp.route('/<int:project_id>/complete', methods=['POST'])
@login_required
def complete(project_id):
    """Mark project as complete"""
    project = Project.query.get_or_404(project_id)
    
    # Only customer or assigned creator can complete
    if current_user.id not in [project.posted_by_id, project.assigned_to_id]:
        return jsonify({'error': 'Unauthorized'}), 403
    
    project.status = 'completed'
    project.completed_at = datetime.utcnow()
    db.session.commit()
    
    flash('Project marked as complete!', 'success')
    return jsonify({'success': True}), 200


@projects_bp.route('/<int:project_id>/review', methods=['GET', 'POST'])
@login_required
def review(project_id):
    """Submit review for completed project (customer only)"""
    project = Project.query.get_or_404(project_id)
    
    # Only customer can review
    if current_user.id != project.posted_by_id:
        flash('Only the customer can review this project.', 'warning')
        return redirect(url_for('projects.detail', project_id=project_id))
    
    # Project must be completed
    if project.status != 'completed':
        flash('Project must be completed before reviewing.', 'warning')
        return redirect(url_for('projects.detail', project_id=project_id))
    
    # Check if already reviewed
    existing_review = Review.query.filter_by(
        project_id=project_id,
        reviewer_id=current_user.id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this project.', 'info')
        return redirect(url_for('projects.detail', project_id=project_id))
    
    if request.method == 'POST':
        rating = request.form.get('rating', type=int)
        comment = request.form.get('comment')
        
        if not rating or rating < 1 or rating > 5:
            flash('Please provide a rating between 1 and 5.', 'danger')
            return render_template('projects/review.html', project=project)
        
        # Create review
        review_obj = Review(
            project_id=project_id,
            reviewer_id=current_user.id,
            creator_id=project.assigned_to_id,
            rating=rating,
            comment=comment
        )
        db.session.add(review_obj)
        
        # Update creator rating
        creator = project.creator
        reviews = Review.query.filter_by(creator_id=creator.id).all()
        total_rating = sum([r.rating for r in reviews]) + rating
        total_reviews = len(reviews) + 1
        creator.rating = round(total_rating / total_reviews, 2)
        creator.total_reviews = total_reviews
        
        db.session.commit()
        
        flash('Review submitted successfully!', 'success')
        return redirect(url_for('projects.creator_profile', creator_id=creator.id))
    
    return render_template('projects/review.html', project=project)



@projects_bp.route('/creator/<int:creator_id>')
def creator_profile(creator_id):
    """View creator profile"""
    creator = User.query.get_or_404(creator_id)
    
    if creator.role != 'creator':
        flash('User is not a creator.', 'warning')
        return redirect(url_for('main.index'))
    
    # Get portfolio
    portfolio = Upload.query.filter_by(
        owner_id=creator_id,
        upload_type='portfolio'
    ).all()
    
    # Get packages
    packages = Package.query.filter_by(
        creator_id=creator_id,
        is_active=True
    ).all()
    
    # Get reviews
    reviews = Review.query.filter_by(creator_id=creator_id).order_by(Review.created_at.desc()).limit(10).all()
    
    # Get completed projects count
    completed_count = Project.query.filter_by(
        assigned_to_id=creator_id,
        status='completed'
    ).count()
    
    return render_template(
        'projects/creator_profile.html',
        creator=creator,
        portfolio=portfolio,
        packages=packages,
        reviews=reviews,
        completed_count=completed_count
    )


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
        message=f'Creator {current_user.full_name} doesn\'t want to work on "{project.title}". Reason: {reason}. The project is now open for new applications.',
        project_id=project.id
    )
    
    flash('You have left this project. Customer has been notified.', 'info')
    return jsonify({'success': True})
