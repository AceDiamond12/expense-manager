from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)

# Secret key for sessions (you should replace this with a random string in production)
app.secret_key = 'your_secret_key'

# Sample in-memory user database (replace with a real database later)
users = {
    "admin": "password123"
}

# Sample in-memory expenses and earnings
expenses = []
earnings = []

# Home route
@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html')
    return redirect(url_for('login'))  # Redirect to login if not logged in

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))  # If already logged in, redirect to home

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username  # Save username in session
            return redirect(url_for('home'))  # Redirect to home after successful login
        else:
            return 'Invalid credentials'
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('home'))  # If already logged in, redirect to home

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users[username] = password  # Save the user in the sample "database"
        session['username'] = username  # Automatically log in the user after registration
        return redirect(url_for('home'))  # Redirect to home after successful registration
    return render_template('register.html')

# Expenses route - Add, Edit, View, and Delete Expenses
@app.route('/expenses', methods=['GET', 'POST'])
def expenses_page():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        category = request.form['category']
        if category == "Other":
            category = request.form['category_other']  # Use custom category if 'Other' is selected
        amount = float(request.form['amount'])
        date = request.form['date']
        expenses.append({"category": category, "amount": amount, "date": date})
        return redirect(url_for('expenses_page'))  # Reload the page after adding

    return render_template('expenses.html', expenses=expenses)

# Delete Expense
@app.route('/delete_expense/<int:index>')
def delete_expense(index):
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if 0 <= index < len(expenses):
        expenses.pop(index)  # Remove the expense from the list
    return redirect(url_for('expenses_page'))  # Reload the expenses page

# Edit Expense
@app.route('/edit_expense/<int:index>', methods=['GET', 'POST'])
def edit_expense(index):
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        category = request.form['category']
        if category == "Other":
            category = request.form['category_other']  # Use custom category if 'Other' is selected
        amount = float(request.form['amount'])
        date = request.form['date']
        
        if 0 <= index < len(expenses):
            expenses[index] = {"category": category, "amount": amount, "date": date}
        return redirect(url_for('expenses_page'))  # Reload the expenses page

    if 0 <= index < len(expenses):
        expense = expenses[index]
        return render_template('edit_expense.html', expense=expense, index=index)
    return redirect(url_for('expenses_page'))  # If the index is invalid, go back to the expenses page


# Earnings route - Add, Edit, View, and Delete Earnings
@app.route('/earnings', methods=['GET', 'POST'])
def earnings_page():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        category = request.form['category']
        if category == "Other":
            category = request.form['category_other']  # Use custom category if 'Other' is selected
        amount = float(request.form['amount'])
        date = request.form['date']
        earnings.append({"category": category, "amount": amount, "date": date})
        return redirect(url_for('earnings_page'))  # Reload the page after adding

    return render_template('earnings.html', earnings=earnings)

# Delete Earning
@app.route('/delete_earning/<int:index>')
def delete_earning(index):
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if 0 <= index < len(earnings):
        earnings.pop(index)  # Remove the earning from the list
    return redirect(url_for('earnings_page'))  # Reload the earnings page

# Edit Earning
@app.route('/edit_earning/<int:index>', methods=['GET', 'POST'])
def edit_earning(index):
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        category = request.form['category']
        if category == "Other":
            category = request.form['category_other']  # Use custom category if 'Other' is selected
        amount = float(request.form['amount'])
        date = request.form['date']
        
        if 0 <= index < len(earnings):
            earnings[index] = {"category": category, "amount": amount, "date": date}
        return redirect(url_for('earnings_page'))  # Reload the earnings page

    if 0 <= index < len(earnings):
        earning = earnings[index]
        return render_template('edit_earning.html', earning=earning, index=index)
    return redirect(url_for('earnings_page'))  # If the index is invalid, go back to the earnings page


# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove user from session
    return redirect(url_for('login'))  # Redirect to login page

# Report route
@app.route('/report')
def report():
    total_expenses = sum(expense['amount'] for expense in expenses)
    total_earnings = sum(earning['amount'] for earning in earnings)

    expense_categories = {}
    for expense in expenses:
        category = expense['category']
        if category not in expense_categories:
            expense_categories[category] = 0
        expense_categories[category] += expense['amount']

    earning_categories = {}
    for earning in earnings:
        category = earning['category']
        if category not in earning_categories:
            earning_categories[category] = 0
        earning_categories[category] += earning['amount']

    return render_template('report.html', total_expenses=total_expenses, total_earnings=total_earnings,
                           expense_categories=expense_categories, earning_categories=earning_categories)

if __name__ == "__main__":
    app.run(debug=True)
