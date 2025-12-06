"""
Session management and timeout handling
"""
import time
import threading

# Global session storage
user_sessions = {}
user_carts = {}
user_states = {}
user_cart_messages = {}

SESSION_TIMEOUT = 900  # 15 minutes in seconds

def get_or_create_session(user_id):
    """Get or create a session for a user"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'last_activity': time.time(),
            'active': True
        }
    else:
        user_sessions[user_id]['last_activity'] = time.time()
    return user_sessions[user_id]

def update_session_activity(user_id):
    """Update the last activity time for a user"""
    if user_id in user_sessions:
        user_sessions[user_id]['last_activity'] = time.time()

def clear_user_session(user_id):
    """Clear all session data for a user"""
    if user_id in user_sessions:
        del user_sessions[user_id]
    if user_id in user_carts:
        del user_carts[user_id]
    if user_id in user_states:
        del user_states[user_id]
    # Clear the stored cart message ID
    if user_id in user_cart_messages:
        del user_cart_messages[user_id]

def is_session_expired(user_id):
    """Check if a user's session has expired"""
    if user_id not in user_sessions:
        return True
    
    last_activity = user_sessions[user_id]['last_activity']
    return (time.time() - last_activity) > SESSION_TIMEOUT

def session_cleanup_thread():
    """Background thread to clean up expired sessions"""
    while True:
        time.sleep(60)  # Check every minute
        
        expired_users = []
        for user_id, session in list(user_sessions.items()):
            if is_session_expired(user_id):
                expired_users.append(user_id)
        
        for user_id in expired_users:
            clear_user_session(user_id)

def get_user_state(user_id):
    """Get the current state of a user"""
    return user_states.get(user_id, None)

def set_user_state(user_id, state):
    """Set the state for a user"""
    user_states[user_id] = state
    update_session_activity(user_id)

def clear_user_state(user_id):
    """Clear the state for a user"""
    if user_id in user_states:
        del user_states[user_id]

def set_cart_message(user_id, message_id):
    """Store the message ID of the user's live cart"""
    user_cart_messages[user_id] = message_id

def get_cart_message(user_id):
    """Get the message ID of the user's live cart"""
    return user_cart_messages.get(user_id, None)

def clear_cart_message(user_id):
    """Clear the stored cart message ID"""
    if user_id in user_cart_messages:
        del user_cart_messages[user_id]
