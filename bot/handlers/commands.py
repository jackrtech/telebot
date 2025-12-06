"""
Bot command handlers (/start, /order, /cart, /restart)
"""
from telebot import types
from bot.utils.session import (
    get_or_create_session, clear_user_session, is_session_expired,
    get_user_state, set_user_state, get_order_message, set_order_message
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
{config.shop_name} 🏴

First Class Shipping Included ✉️

Commands:
/order
/cart 
/restart
"""
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row(types.KeyboardButton("🛍️ Browse Products"))
        markup.row(types.KeyboardButton("📦 View Cart"))
        
        bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
    
    @bot.message_handler(commands=['order'])
    @bot.message_handler(func=lambda m: m.text == "🛍️ Browse Products")
    def handle_order(message):
        user_id = message.from_user.id
        
        if is_session_expired(user_id):
            bot.send_message(
                message.chat.id,
                "Your session has expired. /start again."
            )
            return
        
        get_or_create_session(user_id)
        
        old_message_id = get_order_message(user_id)
        if old_message_id:
            try:
                bot.delete_message(message.chat.id, old_message_id)
            except:
                pass
        
        show_categories(message, bot, config, user_id)
    
    @bot.message_handler(commands=['cart'])
    @bot.message_handler(func=lambda m: m.text == "📦 View Cart")
    def handle_cart(message):
        user_id = message.from_user.id
        
        if is_session_expired(user_id):
            bot.send_message(
                message.chat.id,
                "Your session has expired. /start again."
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
            types.InlineKeyboardButton("🪓 Clear Cart", callback_data="clear_cart")
        )
        markup.row(
            types.InlineKeyboardButton("🏁 Checkout", callback_data="checkout")
        )
        
        bot.send_message(message.chat.id, cart_message, reply_markup=markup)
    
    
    @bot.message_handler(commands=['restart'])
    def handle_restart(message):
        user_id = message.from_user.id
        clear_user_session(user_id)
        bot.send_message(
            message.chat.id,
            "Your session has been cleared. Use /start to begin again."
        )

def show_categories(message, bot, config, user_id):
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
    
    sent_msg = bot.send_message(
        message.chat.id,
        "Select a category:",
        reply_markup=markup
    )
    
    set_order_message(user_id, sent_msg.message_id)
