"""
Email notification service using Mailgun
"""
import requests


def send_payment_confirmation_email(order_data, config):
    """Send payment confirmation email to shop owner after successful payment"""
    from bot.utils.formatting import format_receipt
    
    print(f"[v0] send_payment_confirmation_email called")
    print(f"[v0] Mailgun API key present: {bool(config.mailgun_api_key)}")
    print(f"[v0] Mailgun domain: {config.mailgun_domain}")
    
    if not config.mailgun_api_key or not config.mailgun_domain:
        print("[v0] ERROR: Mailgun not configured, skipping email")
        return False
    
    subject = f"New Order Payment Confirmed - {order_data['order_id']}"
    text_body = format_receipt(order_data, config.currency)
    
    print(f"[v0] Sending email to: {config.mailgun_to}")
    print(f"[v0] From: {config.mailgun_from}")
    print(f"[v0] Subject: {subject}")
    
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
        
        print(f"[v0] Mailgun API response: {response.status_code}")
        
        if response.status_code == 200:
            print(f"[v0] SUCCESS: Payment confirmation email sent for {order_data['order_id']}")
            return True
        else:
            print(f"[v0] ERROR: Failed to send email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"[v0] ERROR sending email: {e}")
        import traceback
        traceback.print_exc()
        return False
