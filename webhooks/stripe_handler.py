"""
Stripe webhook event handler
"""
from flask import request
import stripe
import json
from bot.services.email_service import send_payment_confirmation_email
from bot.utils.formatting import format_receipt

def register_stripe_webhook(app, bot, config):
    """Register Stripe webhook endpoint"""
    
    @app.route('/webhook', methods=['POST'])
    def stripe_webhook():
        print(f"[v0] Webhook received at /webhook endpoint")
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        print(f"[v0] Signature header present: {sig_header is not None}")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, config.stripe_webhook_secret
            )
            print(f"[v0] Webhook event verified: {event['type']}")
        except ValueError as e:
            print(f"[v0] Invalid payload: {e}")
            return 'Invalid payload', 400
        except stripe.error.SignatureVerificationError as e:
            print(f"[v0] Invalid signature: {e}")
            return 'Invalid signature', 400
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            print(f"[v0] Processing checkout.session.completed event")
            session = event['data']['object']
            handle_successful_payment(session, bot, config)
        else:
            print(f"[v0] Unhandled event type: {event['type']}")
        
        return 'Success', 200

def handle_successful_payment(session, bot, config):
    """Handle successful payment event"""
    print(f"[v0] handle_successful_payment called")
    metadata = session.get('metadata', {})
    order_id = metadata.get('order_id')
    user_id = metadata.get('user_id')
    username = metadata.get('username', 'Unknown')
    customer_name = metadata.get('customer_name')
    address_line1 = metadata.get('address_line1')
    city = metadata.get('city')
    postcode = metadata.get('postcode')
    items_json = metadata.get('items')
    total = metadata.get('total')
    
    print(f"[v0] Metadata: order_id={order_id}, user_id={user_id}, username={username}")
    
    if not order_id or not user_id:
        print("[v0] ERROR: Missing order_id or user_id in webhook metadata")
        return
    
    try:
        user_id = int(user_id)
        
        items_dict = json.loads(items_json) if items_json else {}
        
        order_data = {
            'order_id': order_id,
            'username': username,
            'name': customer_name,
            'address_line1': address_line1,
            'city': city,
            'postcode': postcode,
            'items': items_dict,
            'total': float(total),
            'currency': config.currency
        }
        
        print(f"[v0] Sending receipt to Telegram user {user_id}")
        receipt_text = format_receipt(order_data, config.currency)
        bot.send_message(user_id, receipt_text)
        print(f"[v0] Receipt sent to Telegram")
        
        print(f"[v0] Sending email notification")
        send_payment_confirmation_email(order_data, config)
        
        print(f"[v0] Payment confirmed for order {order_id}")
        
    except Exception as e:
        print(f"[v0] ERROR handling payment confirmation: {e}")
        import traceback
        traceback.print_exc()
