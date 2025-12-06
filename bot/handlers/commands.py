"""
Bot command handlers (/start, /order, /cart, /help, /restart)
"""
from telebot import types
from bot.utils.session import (
    get_or_create_session, clear_user_session, is_session_expired,
    get_user_state, set_user_state
)
from bot.services.cart_service import get_cart, get_cart_items_count
from bot.utils.formatting import format_cart_message

def register_command_handlers(bot, config):
    """Register all command handlers"""
    
    @bot.message_handler(commands=['start'])
    def handle_start(message):
        user_id = message.from_user.id
        get_or_create_session(user_id)
        
        welcome_text = f"""
Welcome to {config.shop_name}! 🛍️

Use the buttons below to browse our products, view your cart, or get help.

Commands:
/order - Browse products
/cart - View your cart
/help - Get help
/restart - Clear your session and start over
"""
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("🛍️ Browse Products"))
        markup.row(types.KeyboardButton("🛒 View Cart"), types.KeyboardButton("❓ Help"))
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
    
    @bot.message_handler(commands=['order'])
    @bot.message_handler(func=lambda m: m.text == "🛍️ Browse Products")
    def handle_order(message):
        user_id = message.from_user.id
        
        if is_session_expired(user_id):
            bot.send_message(
                message.chat.id,
                "Your session has expired. Please /start again."
            )
            return
        
        get_or_create_session(user_id)
        show_categories(message, bot, config)
    
    @bot.message_handler(commands=['cart'])
    @bot.message_handler(func=lambda m: m.text == "🛒 View Cart")
    def handle_cart(message):
        user_id = message.from_user.id
        
        if is_session_expired(user_id):
            bot.send_message(
                message.chat.id,
                "Your session has expired. Please /start again."
            )
            return
        
        cart = get_cart(user_id)
        products_flat = config.get_all_products_flat()
        cart_message = format_cart_message(cart, products_flat, config.currency)
        
        if not cart:
            bot.send_message(message.chat.id, cart_message)
            return
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart")
        )
        markup.row(
            types.InlineKeyboardButton("✅ Checkout", callback_data="checkout")
        )
        
        bot.send_message(message.chat.id, cart_message, reply_markup=markup)
    
    @bot.message_handler(commands=['help'])
    @bot.message_handler(func=lambda m: m.text == "❓ Help")
    def handle_help(message):
        help_text = f"""
{config.shop_name} Bot Help 📚

Commands:
/start - Start the bot
/order - Browse and order products
/cart - View your shopping cart
/help - Show this help message
/restart - Clear your session and start fresh

How to order:
1. Use /order to browse products
2. Click items to add them to cart
3. Use /cart to review your order
4. Click Checkout to proceed with payment

Need assistance? Contact us at {config.mailgun_to if config.mailgun_to else 'our support email'}.
"""
        bot.send_message(message.chat.id, help_text)
    
    @bot.message_handler(commands=['restart'])
    def handle_restart(message):
        user_id = message.from_user.id
        clear_user_session(user_id)
        bot.send_message(
            message.chat.id,
            "Your session has been cleared. Use /start to begin again."
        )

def show_categories(message, bot, config):
    """Display product categories"""
    categories = config.get_categories()
    
    markup = types.InlineKeyboardMarkup()
    for category in categories:
        markup.row(
            types.InlineKeyboardButton(
                f"📦 {category}",
                callback_data=f"cat_{category}"
            )
        )
    
    bot.send_message(
        message.chat.id,
        "Select a category:",
        reply_markup=markup
    )
