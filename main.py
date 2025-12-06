"""
Telegram Marketplace Bot - Main Entry Point
"""
from dotenv import load_dotenv
load_dotenv()
import os
from bot.config import Config
from bot.handlers.commands import register_command_handlers
from bot.handlers.cart import register_cart_handlers
from bot.handlers.checkout import register_checkout_handlers
from bot.utils.session import session_cleanup_thread
from webhooks.app import create_flask_app
import telebot
import threading

def main():
    """Initialize and run the bot"""
    # Load configuration
    config = Config()
    
    # Initialize bot
    bot = telebot.TeleBot(config.telegram_token, threaded=False)
    
    # Register all handlers
    register_command_handlers(bot, config)
    register_cart_handlers(bot, config)
    register_checkout_handlers(bot, config)
    
    # Start session cleanup thread
    cleanup_thread = threading.Thread(target=session_cleanup_thread, daemon=True)
    cleanup_thread.start()
    
    # Start Flask webhook server in separate thread
    flask_app = create_flask_app(bot, config)
    flask_thread = threading.Thread(
        target=lambda: flask_app.run(
            host=config.flask_host,
            port=config.flask_port,
            debug=False
        ),
        daemon=True
    )
    flask_thread.start()
    
    print(f"Bot started successfully!")
    print(f"Flask webhook server running on {config.flask_host}:{config.flask_port}")
    
    # Start polling
    bot.infinity_polling()

if __name__ == "__main__":
    main()
