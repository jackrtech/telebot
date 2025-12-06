"""
Text and message formatting utilities
"""

def format_price(price, currency='GBP'):
    """Format price with currency symbol, removing unnecessary decimals"""
    symbols = {
        'GBP': '£',
        'USD': '$',
        'EUR': '€'
    }
    symbol = symbols.get(currency, currency)
    
    if float(price) == int(float(price)):
        return f"{symbol}{int(float(price))}"
    return f"{symbol}{price}"

def format_cart_message(cart, products_flat, currency='GBP'):
    """Format cart contents into a readable message with items listed individually"""
    if not cart:
        return "Your cart is empty."
    
    lines = ["📦 Your Cart:\n"]
    
    items_with_prices = []
    for item, quantity in cart.items():
        price = float(products_flat.get(item, 0))
        for _ in range(quantity):
            items_with_prices.append((item, price))
    
    # Sort by price ascending
    items_with_prices.sort(key=lambda x: x[1])
    
    total = 0.0
    for item, price in items_with_prices:
        lines.append(f"{item} - {format_price(price, currency)}")
        total += price
    
    lines.append(f"\nTotal: {format_price(total, currency)}")
    return "\n".join(lines)

def format_order_summary_individual(cart, products_flat, customer_info, currency='GBP'):
    """Format order summary with items listed individually and sorted by price"""
    lines = [
        "Order Summary\n",
        "Items:"
    ]
    
    items_with_prices = []
    total = 0.0
    
    for item, quantity in cart.items():
        price = float(products_flat.get(item, 0))
        for _ in range(quantity):
            items_with_prices.append((item, price))
        total += price * quantity
    
    # Sort by price ascending
    items_with_prices.sort(key=lambda x: x[1])
    
    for item, price in items_with_prices:
        lines.append(f"• {item} - {format_price(price, currency)}")
    
    lines.extend([
        f"\nTotal: {format_price(total, currency)}",
        "\nDelivery Address:",
        customer_info['name'],
        customer_info['address_line1'],
        customer_info['city'],
        customer_info['postcode']
    ])
    
    return "\n".join(lines)

def format_order_summary(order_data, currency='GBP'):
    """Format order summary for emails and messages"""
    lines = [
        f"Order ID: {order_data['order_id']}",
        f"\nCustomer Details:",
        f"Name: {order_data['name']}",
    ]
    
    
    lines.extend([
        f"\nDelivery Address:",
        f"{order_data['address_line1']}",
        order_data['city'],
        order_data['postcode'],
        f"\nItems:"
    ])
    
    items_with_prices = []
    total = 0.0
    
    for item, details in order_data['items'].items():
        quantity = details['quantity']
        price = details['price']
        subtotal = quantity * price
        total += subtotal
        for _ in range(quantity):
            items_with_prices.append((item, price))
    
    # Sort by price ascending
    items_with_prices.sort(key=lambda x: x[1])
    
    for item, price in items_with_prices:
        lines.append(f"• {item} - {format_price(price, currency)}")
    
    lines.append(f"\nTotal: {format_price(total, currency)}")
    
    return "\n".join(lines)
