"""
Shopping cart management service
"""
from bot.utils.session import user_carts, update_session_activity

def get_cart(user_id):
    """Get user's cart"""
    if user_id not in user_carts:
        user_carts[user_id] = {}
    return user_carts[user_id]

def add_to_cart(user_id, item, quantity=1):
    """Add item to user's cart"""
    cart = get_cart(user_id)
    if item in cart:
        cart[item] += quantity
    else:
        cart[item] = quantity
    update_session_activity(user_id)
    return cart

def remove_from_cart(user_id, item):
    """Remove item from user's cart"""
    cart = get_cart(user_id)
    if item in cart:
        del cart[item]
    update_session_activity(user_id)
    return cart

def update_cart_quantity(user_id, item, quantity):
    """Update quantity of item in cart"""
    cart = get_cart(user_id)
    if quantity <= 0:
        return remove_from_cart(user_id, item)
    cart[item] = quantity
    update_session_activity(user_id)
    return cart

def clear_cart(user_id):
    """Clear user's cart"""
    if user_id in user_carts:
        user_carts[user_id] = {}
    update_session_activity(user_id)

def get_cart_total(user_id, products_flat):
    """Calculate total price of items in cart"""
    cart = get_cart(user_id)
    total = 0.0
    for item, quantity in cart.items():
        price = float(products_flat.get(item, 0))
        total += price * quantity
    return total

def get_cart_items_count(user_id):
    """Get total number of items in cart"""
    cart = get_cart(user_id)
    return sum(cart.values())
