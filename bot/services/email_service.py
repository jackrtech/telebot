"""
Email notification service using Mailgun
"""
import requests


def send_payment_confirmation_email(order_data, config):
    """Send payment confirmation email to shop owner after successful payment"""
    from bot.utils.formatting import format_receipt
    
    if not config.mailgun_api_key or not config.mailgun_domain:
        print("Mailgun not configured, skipping email")
        return False
    
    subject = f"New Order Payment Confirmed - {order_data['order_id']}"
    text_body = format_receipt(order_data, config.currency)
    
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
            print(f"Payment confirmation email sent for {order_data['order_id']}")
            return True
        else:
            print(f"Failed to send email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
