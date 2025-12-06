"""
Configuration management for the bot
"""
import os
import json

class Config:
    """Bot configuration loader"""
    
    def __init__(self):
        # Load config.json
        with open('config.json', 'r', encoding='utf-8') as f:
            self.config_data = json.load(f)
        
        # Bot configuration
        self.shop_name = self.config_data.get('shop_name', 'Shop')
        self.currency = self.config_data.get('currency', 'GBP')
        self.products = self.config_data.get('products', {})
        
        # Environment variables
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
        self.stripe_secret_key = os.getenv('STRIPE_SECRET_KEY', '')
        self.stripe_webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')
        
        # Mailgun
        self.mailgun_api_key = os.getenv('MAILGUN_API_KEY', '')
        self.mailgun_domain = os.getenv('MAILGUN_DOMAIN', '')
        self.mailgun_from = os.getenv('MAILGUN_FROM_EMAIL', '')
        self.mailgun_to = os.getenv('MAILGUN_TO_EMAIL', '')
        
        # Flask
        self.flask_host = os.getenv('FLASK_HOST', '0.0.0.0')
        self.flask_port = int(os.getenv('FLASK_PORT', 5000))
        
        # Ngrok URL for local testing
        self.ngrok_url = os.getenv('NGROK_URL', '')
    
    def get_categories(self):
        """Get list of product categories"""
        return list(self.products.keys())
    
    def get_products_in_category(self, category):
        """Get products in a specific category"""
        return self.products.get(category, {})
    
    def get_all_products_flat(self):
        """Get all products as a flat dictionary"""
        all_products = {}
        for category, items in self.products.items():
            all_products.update(items)
        return all_products
