from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'https://poe.com/s/HfOC50pQLUzHf7w6rtnJ'  # Set a strong secret key for session management

def get_db_connection():
    conn = sqlite3.connect('bank.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']  # Store user ID in session
            return redirect(url_for('user_page', user_id=user['id']))
        else:
            return "Invalid credentials", 401  # Optional: Show an error message

    return render_template('index.html')

@app.route('/user/<int:user_id>', methods=['GET'])
def user_page(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('index'))  # Redirect if not logged in or accessing another user's account

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    transactions = conn.execute('SELECT * FROM transactions WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    
    return render_template('user.html', user=user, transactions=transactions)

@app.route('/withdraw/<int:user_id>', methods=['POST'])
def withdraw(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('index'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if user:
        amount = float(request.form['amount'])
        if amount > 0 and amount <= user['balance']:
            new_balance = user['balance'] - amount
            conn.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
        else:
            return "Invalid withdrawal amount", 400

    conn.close()
    return redirect(url_for('user_page', user_id=user_id))

@app.route('/send_money/<int:user_id>', methods=['POST'])
def send_money(user_id):
    if 'user_id' not in session or session['user_id'] != user_id:
        return redirect(url_for('index'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

    if user:
        recipient_username = request.form['recipient_username']
        amount = float(request.form['amount'])

        recipient = conn.execute('SELECT * FROM users WHERE username = ?', (recipient_username,)).fetchone()

        if recipient and amount > 0 and amount <= user['balance']:
            new_sender_balance = user['balance'] - amount
            new_recipient_balance = recipient['balance'] + amount

            conn.execute('UPDATE users SET balance = ? WHERE id = ?', (new_sender_balance, user_id))
            conn.execute('UPDATE users SET balance = ? WHERE id = ?', (new_recipient_balance, recipient['id']))

            # Log the transaction
            conn.execute('INSERT INTO transactions (user_id, type, amount, date) VALUES (?, ?, ?, datetime("now"))',
                         (user_id, 'send', amount))

            conn.commit()
        else:
            return "Invalid transaction", 400

    conn.close()
    return redirect(url_for('user_page', user_id=user_id))

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    return redirect(url_for('index'))

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if 'user_id' not in session:
        return redirect(url_for('index'))

    conn = get_db_connection()
    current_user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    
    if current_user['role'] != 'admin':
        return "Access denied", 403

    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_user':
            username = request.form['username']
            password = request.form['password']
            balance = float(request.form['balance'])
            conn.execute('INSERT INTO users (username, password, balance) VALUES (?, ?, ?)',
                         (username, password, balance))
            conn.commit()
        
        elif action == 'edit_user':
            user_id = request.form['user_id']
            new_balance = float(request.form['new_balance'])
            conn.execute('UPDATE users SET balance = ? WHERE id = ?', (new_balance, user_id))
            conn.commit()
        
        elif action == 'delete_user':
            user_id = request.form['user_id']
            conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.commit()

    users = conn.execute('SELECT * FROM users').fetchall()
    transactions = conn.execute('SELECT * FROM transactions').fetchall()
    conn.close()
    
    return render_template('admin.html', users=users, transactions=transactions)

if __name__ == '__main__':
    app.run(debug=True)