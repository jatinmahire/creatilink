from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import stripe
import qrcode
from io import BytesIO
import base64
from app import db
from app.models import Project, Transaction, User, Notification
from app.notification_helpers import create_notification, get_unread_count, mark_as_read, get_user_notifications

payments_bp = Blueprint('payments', __name__, url_prefix='/payment')

def init_stripe():
    """Initialize Stripe with secret key"""
    from flask import current_app
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')


# ====================
# UPI PAYMENT ROUTES
# ====================

@payments_bp.route('/confirm/<int:transaction_id>', methods=['POST'])
@login_required
def customer_confirm_payment(transaction_id):
    """Customer confirms they made the UPI payment"""
    transaction = Transaction.query.get_or_404(transaction_id)
    project = Project.query.get(transaction.project_id)
    
    # Only customer can confirm
    if current_user.id != transaction.customer_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Mark customer as confirmed
    transaction.customer_confirmed = True
    db.session.commit()
    
    # Notify creator to check payment
    create_notification(
        user_id=transaction.creator_id,
        notification_type='payment_pending',
        title='💰 Payment Confirmation Pending',
        message=f'Customer has paid ₹{transaction.amount} for "{project.title}". Please check your UPI app and confirm receipt.',
        project_id=project.id,
        transaction_id=transaction_id
    )
    
    flash('Payment confirmation sent! Waiting for creator to verify receipt.', 'success')
    return jsonify({'success': True}), 200


@payments_bp.route('/creator_confirm/<int:transaction_id>', methods=['POST'])
@login_required
def creator_confirm_payment(transaction_id):
    """Creator confirms they received the payment"""
    transaction = Transaction.query.get_or_404(transaction_id)
    project = Project.query.get(transaction.project_id)
    
    # Only creator can confirm
    if current_user.id != transaction.creator_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Mark creator as confirmed and complete transaction
    transaction.creator_confirmed = True
    transaction.payment_confirmed_at = datetime.utcnow()
    transaction.status = 'completed'
    transaction.completed_at = datetime.utcnow()
    
    # Update project status
    project.status = 'completed'
    project.completed_at = datetime.utcnow()
    
    db.session.commit()
    
    # Notify customer that payment is confirmed and link is unlocked
    create_notification(
        user_id=transaction.customer_id,
        notification_type='payment_received',
        title='✅ Payment Confirmed!',
        message=f'Creator confirmed receiving ₹{transaction.amount} for "{project.title}". Delivery files are now accessible!',
        project_id=project.id,
        transaction_id=transaction_id
    )
    
    flash('Payment confirmed! Customer can now access delivery files.', 'success')
    return jsonify({'success': True}), 200


@payments_bp.route('/creator_reject/<int:transaction_id>', methods=['POST'])
@login_required
def creator_reject_payment(transaction_id):
    """Creator indicates payment not received"""
    transaction = Transaction.query.get_or_404(transaction_id)
    project = Project.query.get(transaction.project_id)
    
    # Only creator can reject
    if current_user.id != transaction.creator_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Reset customer confirmation
    transaction.customer_confirmed = False
    db.session.commit()
    
    # Notify customer that payment not received
    create_notification(
        user_id=transaction.customer_id,
        notification_type='payment_rejected',
        title='❌ Payment Not Received',
        message=f'Creator has not received payment for "{project.title}". Please check your UPI transaction and try again.',
        project_id=project.id,
        transaction_id=transaction_id
    )
    
    flash('Customer has been notified that payment was not received.', 'info')
    return jsonify({'success': True}), 200


@payments_bp.route('/qr/<int:transaction_id>')
@login_required
def generate_qr(transaction_id):
    """Generate UPI QR code for payment"""
    transaction = Transaction.query.get_or_404(transaction_id)
    creator = User.query.get(transaction.creator_id)
    project = Project.query.get(transaction.project_id)
    
    # Only customer can view QR
    if current_user.id != transaction.customer_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if not creator.upi_id:
        return jsonify({'error': 'Creator has not set up UPI ID'}), 400
    
    # Create UPI payment link
    upi_url = f"upi://pay?pa={creator.upi_id}&pn={creator.full_name}&am={transaction.amount}&cu=INR&tn=Payment for {project.title}"
    
    # Generate QR code
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(upi_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({
        'qr_code': f"data:image/png;base64,{img_str}",
        'upi_id': creator.upi_id,
        'amount': transaction.amount,
        'creator_name': creator.full_name
    }), 200


# ====================
# NOTIFICATION ROUTES
# ====================

@payments_bp.route('/notifications/list')
@login_required
def list_notifications():
    """Get user notifications"""
    notifications = get_user_notifications(current_user.id, limit=20)
    return jsonify([
        {
            'id': n.id,
            'type': n.type,
            'title': n.title,
            'message': n.message,
            'project_id': n.project_id,
            'is_read': n.is_read,
            'created_at': n.created_at.isoformat()
        }
        for n in notifications
    ]), 200


@payments_bp.route('/notifications/unread_count')
@login_required
def unread_count():
    """Get unread notification count"""
    count = get_unread_count(current_user.id)
    return jsonify({'count': count}), 200


@payments_bp.route('/notifications/mark_read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification = mark_as_read(notification_id)
    if notification and notification.user_id == current_user.id:
        return jsonify({'success': True}), 200
    return jsonify({'error': 'Not found'}), 404


# ====================
# STRIPE ROUTES (existing)
# ====================

@payments_bp.route('/create', methods=['POST'])
@login_required
def create_payment():
    """Create Stripe checkout session"""
    from flask import current_app
    init_stripe()
    
    project_id = request.form.get('project_id', type=int)
    amount = request.form.get('amount', type=float)
    payment_type = request.form.get('type', 'full')  # 'full' or 'milestone'
    
    project = Project.query.get_or_404(project_id)
    
    # Verify customer is paying
    if current_user.id != project.posted_by_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Verify creator is assigned
    if not project.assigned_to_id:
        return jsonify({'error': 'No creator assigned to this project'}), 400
    
    creator = User.query.get(project.assigned_to_id)
    
    try:
        # Create Stripe checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr',
                    'unit_amount': int(amount * 100),  # Convert to paise
                    'product_data': {
                        'name': f'Payment for: {project.title}',
                        'description': f'Project payment to {creator.full_name}',
                    },
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payments.success', project_id=project_id, _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('payments.cancel', project_id=project_id, _external=True),
            metadata={
                'project_id': project_id,
                'customer_id': current_user.id,
                'creator_id': creator.id,
                'payment_type': payment_type
            }
        )
        
        # Create pending transaction
        transaction = Transaction(
            project_id=project_id,
            customer_id=current_user.id,
            creator_id=creator.id,
            amount=amount,
            type=payment_type,
            status='pending',
            stripe_session_id=session.id
        )
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({'checkout_url': session.url}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/success/<int:project_id>')
@login_required
def success(project_id):
    """Payment success callback"""
    init_stripe()
    
    session_id = request.args.get('session_id')
    
    if session_id:
        try:
            # Retrieve session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            # Update transaction
            transaction = Transaction.query.filter_by(stripe_session_id=session_id).first()
            if transaction:
                transaction.status = 'completed'
                transaction.stripe_payment_intent = session.payment_intent
                transaction.completed_at = datetime.utcnow()
                
                # Update project status
                project = Project.query.get(project_id)
                if project:
                    project.status = 'in_progress'
                
                db.session.commit()
            
        except Exception as e:
            print(f"Error processing payment: {e}")
    
    flash('Payment successful! The creator can now start working.', 'success')
    return render_template('payments/success.html', project_id=project_id)


@payments_bp.route('/cancel/<int:project_id>')
@login_required
def cancel(project_id):
    """Payment cancellation"""
    flash('Payment was cancelled.', 'warning')
    return redirect(url_for('projects.detail', project_id=project_id))


@payments_bp.route('/transactions')
@login_required
def transactions():
    """View user transaction history"""
    if current_user.role == 'customer':
        user_transactions = Transaction.query.filter_by(customer_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    else:
        user_transactions = Transaction.query.filter_by(creator_id=current_user.id).order_by(Transaction.created_at.desc()).all()
    
    return render_template('payments/transactions.html', transactions=user_transactions)


@payments_bp.route('/webhook', methods=['POST'])
def webhook():
    """Stripe webhook handler"""
    from flask import current_app
    init_stripe()
    
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get('STRIPE_WEBHOOK_SECRET')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        # Update transaction
        transaction = Transaction.query.filter_by(stripe_session_id=session['id']).first()
        if transaction:
            transaction.status = 'completed'
            transaction.stripe_payment_intent = session.get('payment_intent')
            transaction.completed_at = datetime.utcnow()
            db.session.commit()
    
    return jsonify({'status': 'success'}), 200
