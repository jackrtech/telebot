"""
Checkout and delivery address flow handlers
"""
from telebot import types
from bot.utils.session import (
    update_session_activity, get_user_state, 
    set_user_state, clear_user_state, clear_cart_message
)
from bot.services.cart_service import get_cart, clear_cart, get_cart_total
from bot.services.order_service import create_order
from bot.services.payment_service import create_payment_session
from bot.services.email_service import send_order_notification
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
            bot.answer_callback_query(call.id, "Your cart is empty!")
            return
        
        clear_cart_message(user_id)
        
        # Initialize checkout data
        checkout_data[user_id] = {}
        
        set_user_state(user_id, 'awaiting_name')
        bot.send_message(
            call.message.chat.id,
            "Let's complete your order! 📝\n\nPlease enter a name for delivery:"
        )
    
    @bot.message_handler(func=lambda m: get_user_state(m.from_user.id) == 'awaiting_name')
    def handle_name_input(message):
        user_id = message.from_user.id
        update_session_activity(user_id)
        
        name = message.text.strip()
        
        if len(name) < 2:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_restart_checkout"))
            bot.send_message(message.chat.id, "Please enter a valid name:", reply_markup=markup)
            return
        
        checkout_data[user_id]['name'] = name
        set_user_state(user_id, 'awaiting_address_line1')
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_name"))
        
        bot.send_message(
            message.chat.id,
            "Perfect! Now for delivery details.\n\nPlease enter your address (street and number):",
            reply_markup=markup
        )
    
    
    @bot.message_handler(func=lambda m: get_user_state(m.from_user.id) == 'awaiting_address_line1')
    def handle_address_line1_input(message):
        user_id = message.from_user.id
        update_session_activity(user_id)
        
        address = message.text.strip()
        
        if len(address) < 5:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_name"))
            bot.send_message(message.chat.id, "Please enter a valid address:", reply_markup=markup)
            return
        
        checkout_data[user_id]['address_line1'] = address
        set_user_state(user_id, 'awaiting_city')
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_address"))
        
        bot.send_message(message.chat.id, "Enter your city:", reply_markup=markup)
    
    
    @bot.message_handler(func=lambda m: get_user_state(m.from_user.id) == 'awaiting_city')
    def handle_city_input(message):
        user_id = message.from_user.id
        update_session_activity(user_id)
        
        city = message.text.strip()
        
        if len(city) < 2:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_address"))
            bot.send_message(message.chat.id, "Please enter a valid city:", reply_markup=markup)
            return
        
        checkout_data[user_id]['city'] = city
        set_user_state(user_id, 'awaiting_postcode')
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_city"))
        
        bot.send_message(message.chat.id, "Finally, enter your postcode:", reply_markup=markup)
    
    @bot.message_handler(func=lambda m: get_user_state(m.from_user.id) == 'awaiting_postcode')
    def handle_postcode_input(message):
        user_id = message.from_user.id
        update_session_activity(user_id)
        
        postcode = message.text.strip()
        
        if len(postcode) < 3:
            markup = types.InlineKeyboardMarkup()
            markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_city"))
            bot.send_message(message.chat.id, "Please enter a valid postcode:", reply_markup=markup)
            return
        
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
            types.InlineKeyboardButton("✅ Confirm & Pay", callback_data="confirm_order")
        )
        
        bot.send_message(
            message.chat.id,
            summary,
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == 'back_restart_checkout')
    def handle_back_restart(call):
        user_id = call.from_user.id
        clear_user_state(user_id)
        if user_id in checkout_data:
            del checkout_data[user_id]
        bot.answer_callback_query(call.id, "Checkout cancelled")
        bot.send_message(call.message.chat.id, "Checkout cancelled. Use /cart to try again.")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_name')
    def handle_back_to_name(call):
        user_id = call.from_user.id
        set_user_state(user_id, 'awaiting_name')
        bot.send_message(call.message.chat.id, "Please enter a name for delivery:")
    
    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_address')
    def handle_back_to_address(call):
        user_id = call.from_user.id
        set_user_state(user_id, 'awaiting_address_line1')
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_name"))
        bot.send_message(
            call.message.chat.id, 
            "Please enter your address (street and number):",
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == 'back_to_city')
    def handle_back_to_city(call):
        user_id = call.from_user.id
        set_user_state(user_id, 'awaiting_city')
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_address"))
        bot.send_message(call.message.chat.id, "Enter your city:", reply_markup=markup)
    
    @bot.callback_query_handler(func=lambda call: call.data == 'edit_address')
    def handle_edit_address(call):
        user_id = call.from_user.id
        # Clear address fields and restart
        if user_id in checkout_data:
            checkout_data[user_id].pop('address_line1', None)
            checkout_data[user_id].pop('city', None)
            checkout_data[user_id].pop('postcode', None)
        
        set_user_state(user_id, 'awaiting_address_line1')
        
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("⬅️ Back", callback_data="back_to_name"))
        
        bot.send_message(
            call.message.chat.id,
            "Let's update your delivery address.\n\nPlease enter your address (street and number):",
            reply_markup=markup
        )
    
    @bot.callback_query_handler(func=lambda call: call.data == 'confirm_order')
    def handle_confirm_order(call):
        user_id = call.from_user.id
        update_session_activity(user_id)
        
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
        
        # Send notification email
        send_order_notification(order_data, config)
        
        # Create Stripe payment session
        try:
            success_url = f"{config.ngrok_url}/success?session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{config.ngrok_url}/cancel"
            
            session = create_payment_session(
                order_data,
                config.stripe_secret_key,
                success_url,
                cancel_url
            )
            
            # Send payment link
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton(
                    "💳 Pay Now",
                    url=session.url
                )
            )
            
            bot.send_message(
                call.message.chat.id,
                f"✅ Order Created!\n\nOrder ID: {order_data['order_id']}\n\nClick below to complete payment:",
                reply_markup=markup
            )
            
            # Clear cart after successful order creation
            clear_cart(user_id)
            
            # Clean up checkout data
            if user_id in checkout_data:
                del checkout_data[user_id]
                
        except Exception as e:
            bot.send_message(
                call.message.chat.id,
                f"Sorry, there was an error creating your payment session. Please try again or contact support.\n\nError: {str(e)}"
            )
            print(f"Stripe error: {e}")
