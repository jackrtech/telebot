"""
Checkout and delivery address flow handlers
"""
from telebot import types
from bot.utils.session import (
    update_session_activity, get_user_state, 
    set_user_state, clear_user_state, clear_cart_message,
    get_checkout_message, set_checkout_message, get_order_message
)
from bot.services.cart_service import get_cart, clear_cart, get_cart_total
from bot.services.order_service import create_order
from bot.services.payment_service import create_payment_session
from bot.utils.formatting import format_cart_message, format_order_summary_individual

# Temporary storage for customer info during checkout
checkout_data = {}

def register_checkout_handlers(bot, config):
    """Register all checkout-related handlers"""
    
    @bot.callback_query_handler(func=lambda call: call.data == 'checkout')
    def handle_checkout_start(call):
        user_id = call.from_user.id
        update_session_activity(user_id)
        
        cart = get_cart(user_id)
        if not cart:
            bot.answer_callback_query(call.id, "Your cart is empty")
            return
        
        clear_cart_message(user_id)
        
        # Initialize checkout data
        checkout_data[user_id] = {}
        
        set_user_state(user_id, 'awaiting_name')
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("📦 Continue Shopping", callback_data="continue_shopping"))
        
        sent_msg = bot.send_message(
            call.message.chat.id,
            "Enter a name for delivery:",
            reply_markup=markup
        )
        
        set_checkout_message(user_id, sent_msg.message_id)
    
    @bot.callback_query_handler(func=lambda call: call.data == 'continue_shopping')
    def handle_continue_shopping(call):
        user_id = call.from_user.id
        clear_user_state(user_id)
        if user_id in checkout_data:
            del checkout_data[user_id]
        
        bot.answer_callback_query(call.id, "Returning to products...")
        
        # Delete old order message if exists
        old_message_id = get_order_message(user_id)
        if old_message_id:
            try:
                bot.delete_message(call.message.chat.id, old_message_id)
            except:
                pass
        
        # Show categories in new message
        from bot.handlers.commands import show_categories
        show_categories(call.message, bot, config, user_id)
    
    @bot.message_handler(func=lambda m: get_user_state(m.from_user.id) == 'awaiting_name')
    def handle_name_input(message):
        user_id = message.from_user.id
        update_session_activity(user_id)
        
        # Delete the user's message to keep chat tidy
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        
        name = message.text.strip()
        checkout_data[user_id]['name'] = name
        set_user_state(user_id, 'awaiting_address_line1')
        
        checkout_msg_id = get_checkout_message(user_id)
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_name"))
        
        try:
            bot.edit_message_text(
                "Enter house number + street name:",
                message.chat.id,
                checkout_msg_id,
                reply_markup=markup
            )
        except:
            sent_msg = bot.send_message(
                message.chat.id,
                "Enter house number + street name:",
                reply_markup=markup
            )
            set_checkout_message(user_id, sent_msg.message_id)
    
    @bot.message_handler(func=lambda m: get_user_state(m.from_user.id) == 'awaiting_address_line1')
    def handle_address_line1_input(message):
        user_id = message.from_user.id
        update_session_activity(user_id)
        
        # Delete the user's message to keep chat tidy
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        
        address = message.text.strip()
        checkout_data[user_id]['address_line1'] = address
        set_user_state(user_id, 'awaiting_city')
        
        checkout_msg_id = get_checkout_message(user_id)
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_address"))
        
        try:
            bot.edit_message_text(
                "Enter your city:",
                message.chat.id,
                checkout_msg_id,
                reply_markup=markup
            )
        except:
            sent_msg = bot.send_message(message.chat.id, "Enter your city:", reply_markup=markup)
            set_checkout_message(user_id, sent_msg.message_id)
    
    @bot.message_handler(func=lambda m: get_user_state(m.from_user.id) == 'awaiting_city')
    def handle_city_input(message):
        user_id = message.from_user.id
        update_session_activity(user_id)
        
        # Delete the user's message to keep chat tidy
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        
        city = message.text.strip()
        checkout_data[user_id]['city'] = city
        set_user_state(user_id, 'awaiting_postcode')
        
        checkout_msg_id = get_checkout_message(user_id)
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_city"))
        
        try:
            bot.edit_message_text(
                "Postcode:",
                message.chat.id,
                checkout_msg_id,
                reply_markup=markup
            )
        except:
            bot.send_message(message.chat.id, "Postcode:", reply_markup=markup)
    
    @bot.message_handler(func=lambda m: get_user_state(m.from_user.id) == 'awaiting_postcode')
    def handle_postcode_input(message):
        user_id = message.from_user.id
        update_session_activity(user_id)
        
        # Delete the user's message to keep chat tidy
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        
        postcode = message.text.strip()
        checkout_data[user_id]['postcode'] = postcode.upper()
        
        # Clear state
        clear_user_state(user_id)
        
        cart = get_cart(user_id)
        products_flat = config.get_all_products_flat()
        
        summary = format_order_summary_individual(
            cart, 
            products_flat, 
            checkout_data[user_id], 
            config.currency
        )
        
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton("✏️ Edit Address", callback_data="edit_address")
        )
        markup.row(
            types.InlineKeyboardButton("🏁 Confirm & Pay", callback_data="confirm_order")
        )
        
        checkout_msg_id = get_checkout_message(user_id)
        try:
            bot.edit_message_text(
                summary,
                message.chat.id,
                checkout_msg_id,
                reply_markup=markup
            )
        except:
            bot.send_message(
                message.chat.id,
                summary,
                reply_markup=markup
            )
    
    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_name')
    def handle_back_to_name(call):
        user_id = call.from_user.id
        set_user_state(user_id, 'awaiting_name')
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("📦 Continue Shopping", callback_data="continue_shopping"))
        
        bot.edit_message_text(
            "Enter a name for delivery:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_address')
    def handle_back_to_address(call):
        user_id = call.from_user.id
        set_user_state(user_id, 'awaiting_address_line1')
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_name"))
        
        bot.edit_message_text(
            "Enter house number + street name:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_city')
    def handle_back_to_city(call):
        user_id = call.from_user.id
        set_user_state(user_id, 'awaiting_city')
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_address"))
        
        bot.edit_message_text(
            "Enter your city:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == 'edit_address')
    def handle_edit_address(call):
        user_id = call.from_user.id
        
        set_user_state(user_id, 'awaiting_name')
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("📦 Continue Shopping", callback_data="continue_shopping"))
        
        bot.edit_message_text(
            "Enter a name for delivery:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == 'confirm_order')
    def handle_confirm_order(call):
        user_id = call.from_user.id
        update_session_activity(user_id)
        
        username = call.from_user.username or "Unknown"
        checkout_data[user_id]['username'] = username
        
        # Create order
        cart = get_cart(user_id)
        products_flat = config.get_all_products_flat()
        
        order_data = create_order(
            user_id,
            checkout_data[user_id],
            cart,
            products_flat,
            config.currency
        )
        
        # Create Stripe payment session
        try:
            success_url = f"{config.public_url}/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{config.public_url}/cancel"
            
            session = create_payment_session(
                order_data,
                config.stripe_secret_key,
                success_url,
                cancel_url
            )
            
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton(
                    "💳 Pay Now",
                    url=session.url
                )
            )
            
            bot.send_message(
                call.message.chat.id,
                f"🏁 Order Created\n\nOrder ID: {order_data['order_id']}\n\nClick below to complete payment:",
                reply_markup=markup
            )
            
            # Clear cart after successful order creation
            clear_cart(user_id)
            
                
        except Exception as e:
            bot.send_message(
                call.message.chat.id,
                f"There was an error creating your payment session. Try again or contact us directly."
            )
            print(f"Stripe error: {e}")
