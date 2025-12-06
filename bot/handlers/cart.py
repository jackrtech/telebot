"""
Cart management callback handlers
"""
from telebot import types
from bot.utils.session import (
    update_session_activity, get_user_state, set_user_state, 
    clear_user_state, get_cart_message, set_cart_message, clear_cart_message
)
from bot.services.cart_service import (
    get_cart, add_to_cart, clear_cart, get_cart_items_count
)
from bot.utils.formatting import format_cart_message, format_price

def register_cart_handlers(bot, config):
    """Register all cart-related callback handlers"""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
    def handle_category_selection(call):
        user_id = call.from_user.id
        update_session_activity(user_id)
        
        category = call.data[4:]  # Remove 'cat_' prefix
        products = config.get_products_in_category(category)
        
        markup = types.InlineKeyboardMarkup()
        for product_name, price in products.items():
            markup.row(
                types.InlineKeyboardButton(
                    f"{product_name} - {format_price(price, config.currency)}",
                    callback_data=f"prod_{product_name}"
                )
            )
        markup.row(
            types.InlineKeyboardButton("⬅️ Back to Categories", callback_data="back_to_categories")
        )
        
        bot.edit_message_text(
            f"Select a product from {category}:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith('prod_'))
    def handle_product_selection(call):
        user_id = call.from_user.id
        update_session_activity(user_id)
        
        product_name = call.data[5:]  # Remove 'prod_' prefix
        
        # Add 1 to cart
        add_to_cart(user_id, product_name, 1)
        
        cart_count = get_cart_items_count(user_id)
        
        bot.answer_callback_query(
            call.id,
            f"Added {product_name} to cart! ({cart_count} items total)"
        )
        
        # Check if live cart message exists
        cart_message_id = get_cart_message(user_id)
        cart = get_cart(user_id)
        products_flat = config.get_all_products_flat()
        cart_text = format_cart_message(cart, products_flat, config.currency)
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("🗑️ Clear Cart", callback_data="clear_cart")
        )
        markup.row(
            types.InlineKeyboardButton("✅ Checkout", callback_data="checkout")
        )
        
        if cart_message_id:
            # Update existing cart message
            try:
                bot.edit_message_text(
                    cart_text,
                    call.message.chat.id,
                    cart_message_id,
                    reply_markup=markup
                )
            except:
                # If message doesn't exist anymore, create new one
                sent_msg = bot.send_message(call.message.chat.id, cart_text, reply_markup=markup)
                set_cart_message(user_id, sent_msg.message_id)
        else:
            # Create new live cart message
            sent_msg = bot.send_message(call.message.chat.id, cart_text, reply_markup=markup)
            set_cart_message(user_id, sent_msg.message_id)
    
    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_categories')
    def handle_back_to_categories(call):
        user_id = call.from_user.id
        update_session_activity(user_id)
        
        categories = config.get_categories()
        
        markup = types.InlineKeyboardMarkup()
        for category in categories:
            markup.row(
                types.InlineKeyboardButton(
                    f"📦 {category}",
                    callback_data=f"cat_{category}"
                )
            )
        
        bot.edit_message_text(
            "Select a category:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == 'clear_cart')
    def handle_clear_cart(call):
        user_id = call.from_user.id
        update_session_activity(user_id)
        
        clear_cart(user_id)
        
        bot.answer_callback_query(call.id, "Cart cleared!")
        
        # Update the cart message to show empty cart
        bot.edit_message_text(
            "Your cart is empty.",
            call.message.chat.id,
            call.message.message_id
        )
