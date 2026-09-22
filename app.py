import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import database

app = Flask(__name__)
# Secure session secret key
app.secret_key = os.environ.get('SECRET_KEY', 'canteen_flow_super_secret_session_key_2026')

# Initialize SQLite database and seed initial items if not already present
with app.app_context():
    database.init_db()

# Decorator to require login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'username' in session and 'user_id' in session:
        return redirect(url_for('menu'))
    
    # If no users have registered yet, guide to register page
    if database.get_user_count() == 0:
        flash('Welcome to CanteenFlow! Please register an account to get started.', 'info')
        return redirect(url_for('register'))
    
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('menu'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Please enter both username and password.', 'danger')
            return render_template('login.html')

        user = database.authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            if 'cart' not in session:
                session['cart'] = []
            flash(f'Welcome back, {user["username"]}! What would you like to eat today?', 'success')
            return redirect(url_for('menu'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('menu'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if confirm_password and password != confirm_password:
            flash('Passwords do not match. Please re-enter.', 'danger')
            return render_template('register.html')

        success, message = database.create_user(username, password)
        if success:
            flash(message, 'success')
            return redirect(url_for('login'))
        else:
            flash(message, 'danger')

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('cart', None)
    flash('You have been successfully logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/menu')
@login_required
def menu():
    category = request.args.get('category', 'All')
    items = database.get_menu_items(category)
    return render_template('menu.html', 
                           items=items, 
                           username=session.get('username'), 
                           selected_category=category)

@app.route('/cart')
@login_required
def cart():
    user_cart = session.get('cart', [])
    total_amount = sum(item['total_price'] for item in user_cart)
    return render_template('cart.html', cart=user_cart, total_amount=total_amount)

@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    name = request.form.get('name') or request.form.get('productName', 'Food Item')
    try:
        price = float(request.form.get('price', 0))
        quantity = int(request.form.get('quantity', 1))
    except (ValueError, TypeError):
        flash('Invalid item quantity or price.', 'danger')
        return redirect(url_for('menu'))

    if quantity <= 0:
        flash('Quantity must be at least 1.', 'warning')
        return redirect(url_for('menu'))

    customizations = request.form.get('customizations', '').strip()
    total_price = round(price * quantity, 2)

    cart = session.get('cart', [])

    # Check if item with identical customizations already exists in tray
    found = False
    for item in cart:
        if item['name'] == name and item.get('customizations', '') == customizations:
            item['quantity'] += quantity
            item['total_price'] = round(item['quantity'] * item['price'], 2)
            found = True
            break

    if not found:
        cart.append({
            'name': name,
            'price': price,
            'quantity': quantity,
            'total_price': total_price,
            'customizations': customizations
        })

    session['cart'] = cart
    session.modified = True

    flash(f'Added {quantity} &times; {name} to your tray!', 'success')
    return redirect(url_for('menu'))

# Legacy alias for /order POST
@app.route('/order', methods=['POST'])
@login_required
def order():
    return add_to_cart()

@app.route('/cart/remove/<int:item_index>', methods=['POST'])
@login_required
def remove_from_cart(item_index):
    cart = session.get('cart', [])
    if 0 <= item_index < len(cart):
        removed = cart.pop(item_index)
        session['cart'] = cart
        session.modified = True
        flash(f'Removed {removed["name"]} from your tray.', 'info')
    return redirect(url_for('cart'))

@app.route('/cart/clear', methods=['POST'])
@login_required
def clear_cart():
    session['cart'] = []
    session.modified = True
    flash('Your food tray has been cleared.', 'info')
    return redirect(url_for('cart'))

@app.route('/checkout')
@login_required
def checkout():
    user_cart = session.get('cart', [])
    if not user_cart:
        flash('Your food tray is empty! Please select dishes from the menu first.', 'warning')
        return redirect(url_for('menu'))

    total_amount = sum(item['total_price'] for item in user_cart)
    return render_template('payment.html', orders=user_cart, total_amount=total_amount)

@app.route('/process_payment', methods=['POST'])
@login_required
def process_payment():
    user_cart = session.get('cart', [])
    if not user_cart:
        flash('Cannot process payment: your tray is empty.', 'danger')
        return redirect(url_for('menu'))

    payment_method = request.form.get('payment_method', 'qr_code')
    total_amount = sum(item['total_price'] for item in user_cart)

    order_id, order_token = database.create_order(
        user_id=session['user_id'],
        username=session['username'],
        items=user_cart,
        total_amount=total_amount,
        payment_method=payment_method
    )

    # Clear active cart
    session['cart'] = []
    session.modified = True

    flash(f'Payment successful! Your order token is #{order_token}', 'success')
    return redirect(url_for('payment_confirmation', order_id=order_id))

@app.route('/payment_confirmation')
@login_required
def payment_confirmation():
    order_id = request.args.get('order_id', type=int)
    if not order_id:
        # Fallback to most recent order if not specified in URL
        user_orders = database.get_orders_for_user(session['user_id'])
        if user_orders:
            order_id = user_orders[0]['order']['id']
        else:
            flash('No order found.', 'warning')
            return redirect(url_for('menu'))

    data = database.get_order_by_id(order_id)
    if not data:
        flash('Order not found.', 'danger')
        return redirect(url_for('menu'))

    return render_template('payment_confirmation.html', 
                           order=data['order'], 
                           items=data['items'])

@app.route('/orders')
@login_required
def orders():
    orders_data = database.get_orders_for_user(session['user_id'])
    return render_template('orders.html', orders_data=orders_data)

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        try:
            rating = int(request.form.get('rating', 5))
        except ValueError:
            rating = 5

        comments = request.form.get('feedback', '').strip()
        if not comments:
            flash('Please write a short comment or suggestion.', 'warning')
            return redirect(url_for('feedback'))

        database.add_feedback(session['user_id'], session['username'], rating, comments)
        flash('Thank you! Your feedback has been received and helps us improve.', 'success')
        return redirect(url_for('feedback'))

    recent_feedback = database.get_recent_feedback(limit=8)
    return render_template('feedback.html', recent_feedback=recent_feedback)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
