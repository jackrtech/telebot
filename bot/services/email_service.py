"""
Email notification service using Mailgun
"""
import requests

def send_order_notification(order_data, config):
    """Send order notification email via Mailgun"""
    from bot.utils.formatting import format_order_summary
    
    if not config.mailgun_api_key or not config.mailgun_domain:
        print("Mailgun not configured, skipping email")
        return False
    
    subject = f"New Order: {order_data['order_id']}"
    text_body = format_order_summary(order_data, config.currency)
    
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{config.mailgun_domain}/messages",
            auth=("api", config.mailgun_api_key),
            data={
                "from": config.mailgun_from,
                "to": config.mailgun_to,
                "subject": subject,
                "text": text_body
            }
        )
        
        if response.status_code == 200:
            print(f"Order notification email sent for {order_data['order_id']}")
            return True
        else:
            print(f"Failed to send email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_payment_confirmation(order_data, config):
    """Send payment confirmation email to customer"""
    from bot.utils.formatting import format_order_summary
    
    if not config.mailgun_api_key or not config.mailgun_domain:
        return False
    
    subject = f"Payment Confirmed - Order {order_data['order_id']}"
    text_body = f"Welcome to the Postmen 📨\n\n{format_order_summary(order_data, config.currency)}\n\nWe'll process your order shortly."
    
    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{config.mailgun_domain}/messages",
            auth=("api", config.mailgun_api_key),
            data={
                "from": config.mailgun_from,
                "to": order_data['email'],
                "subject": subject,
                "text": text_body
            }
        )
        
        return response.status_code == 200
            
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False
