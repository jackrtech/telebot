"""
Stripe webhook event handler
"""
from flask import request
import stripe
from bot.services.email_service import send_payment_confirmation

def register_stripe_webhook(app, bot, config):
    """Register Stripe webhook endpoint"""
    
    @app.route('/webhook', methods=['POST'])
    def stripe_webhook():
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, config.stripe_webhook_secret
            )
        except ValueError:
            return 'Invalid payload', 400
        except stripe.error.SignatureVerificationError:
            return 'Invalid signature', 400
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            handle_successful_payment(session, bot, config)
        
        return 'Success', 200

def handle_successful_payment(session, bot, config):
    """Handle successful payment event"""
    metadata = session.get('metadata', {})
    order_id = metadata.get('order_id')
    user_id = metadata.get('user_id')
    customer_email = metadata.get('customer_email')
    
    if not order_id or not user_id:
        print("Missing order_id or user_id in webhook metadata")
        return
    
    try:
        user_id = int(user_id)
        
        # Send confirmation message to user
        bot.send_message(
            user_id,
            f"Payment confirmed\n\nYour order {order_id} has been received and will be processed shortly"
        )
        
        # Note: We would update the order status in the CSV here
        # For now, just log it
        print(f"Payment confirmed for order {order_id}")
        
    except Exception as e:
        print(f"Error handling payment confirmation: {e}")
