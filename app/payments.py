from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
import stripe
from app import db
from app.models import Project, Transaction, User

payments_bp = Blueprint('payments', __name__, url_prefix='/payment')

def init_stripe():
    """Initialize Stripe with secret key"""
    from flask import current_app
    stripe.api_key = current_app.config.get('STRIPE_SECRET_KEY')


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
