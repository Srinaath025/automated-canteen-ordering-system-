from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# In-memory data storage (you can replace this with a database)
users = {}
orders = {}

@app.route('/')
def index():
    if not users:
        flash('No accounts available. Please register.', 'danger')
        return redirect(url_for('register'))
    elif 'username' in session:
        return redirect(url_for('menu'))
    else:
        return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)

        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('menu'))
        else:
            flash('Invalid credentials, please try again.', 'danger')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            flash('Username already exists.', 'danger')
        else:
            users[username] = {'password': generate_password_hash(password)}
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    if 'username' in session:
        return render_template('menu_item.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/order', methods=['POST'])
def order():
    if 'username' in session:
        product_name = request.form['productName']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        customizations = request.form.get('customizations', '')

        total_price = quantity * price

        if session['username'] not in orders:
            orders[session['username']] = []

        order = {
            'product_name': product_name,
            'quantity': quantity,
            'price': price,
            'total_price': total_price,
            'customizations': customizations
        }
        orders[session['username']].append(order)
        flash(f'Order placed for {product_name} (Quantity: {quantity}, Total: ${total_price})', 'success')

    return redirect(url_for('menu'))

@app.route('/checkout')
def checkout():
    if 'username' in session:
        user_orders = orders.get(session['username'], [])
        total_amount = sum(order['total_price'] for order in user_orders)
        return render_template('payment.html', orders=user_orders, total_amount=total_amount)
    return redirect(url_for('login'))

@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'username' in session:
        # Dummy payment processing logic
        user_orders = orders.get(session['username'], [])
        total_amount = sum(order['total_price'] for order in user_orders)

        # Assuming payment is always successful for this dummy logic
        flash('Payment successful!', 'success')
        return redirect(url_for('payment_confirmation'))
    return redirect(url_for('login'))

@app.route('/payment_confirmation')
def payment_confirmation():
    if 'username' in session:
        user_orders = orders.get(session['username'], [])
        total_amount = sum(order['total_price'] for order in user_orders)
        return render_template('payment_confirmation.html', orders=user_orders, total_amount=total_amount)
    return redirect(url_for('login'))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if 'username' in session:
        if request.method == 'POST':
            feedback_text = request.form['feedback']
            # Save the feedback (e.g., store in a database or log file)
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('menu'))

        return render_template('feedback.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
