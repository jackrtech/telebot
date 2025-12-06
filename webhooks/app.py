"""
Flask app for webhook endpoints
"""
from flask import Flask

def create_flask_app(bot, config):
    """Create and configure Flask app"""
    app = Flask(__name__)
    
    # Import and register webhook handlers
    from webhooks.stripe_handler import register_stripe_webhook
    register_stripe_webhook(app, bot, config)
    
    # Health check endpoint
    @app.route('/')
    def health_check():
        return "Bot is running", 200
    
    @app.route('/success')
    def payment_success():
        return """
        <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>Payment Successful</h1>
                <p>You will receive a confirmation email shortly.</p>
                <p>You can close this window and return to Telegram.</p>
            </body>
        </html>
        """
    
    @app.route('/cancel')
    def payment_cancel():
        return """
        <html>
            <body style="font-family: Arial; text-align: center; padding: 50px;">
                <h1>❌ Payment Cancelled</h1>
                <p>Your order has been cancelled. No charges were made.</p>
                <p>You can close this window and return to Telegram to try again.</p>
            </body>
        </html>
        """
    
    return app
