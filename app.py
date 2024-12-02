from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Secret key for sessions
app.secret_key = 'your_secret_key'

# Set up PostgreSQL database URI (Heroku will automatically provide DATABASE_URL in the environment)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///expense_manager.db')  # Use Heroku's database if available, else fallback to SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

from sqlalchemy import inspect

@app.route('/tables')
def view_tables():
    if 'username' not in session or session['username'] != 'admin':  # Restrict access to 'admin'
        return redirect(url_for('login'))
    
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    return render_template('tables.html', tables=tables)

@app.route('/columns/<table_name>')
def view_columns(table_name):
    if 'username' not in session:
        return redirect(url_for('login'))

    inspector = inspect(db.engine)
    columns = inspector.get_columns(table_name)
    return render_template('columns.html', table_name=table_name, columns=columns)

@app.route('/users')
def view_users():
    if 'username' not in session or session['username'] != 'admin':  # Restrict access to 'admin'
        return redirect(url_for('login'))
    
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/expensest')
def view_expenses():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    expenses = Expense.query.all()
    return render_template('expenses.html', expenses=expenses)

@app.route('/earningst')
def view_earnings():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    earnings = Earning.query.all()
    return render_template('earnings.html', earnings=earnings)


# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Define Expense Model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(10), nullable=False)

# Define Earning Model
class Earning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(10), nullable=False)

# Create database tables (run this once when setting up the app)
with app.app_context():
    db.create_all()

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
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            session['user_id'] = user.id  # Store user ID in session
            return redirect(url_for('home'))
        else:
            error = "Invalid credentials. Please try again."
            return render_template('login.html', error=error)

    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('home'))  # If already logged in, redirect to home

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if the username already exists
        if User.query.filter_by(username=username).first():
            error = "Username already exists. Please choose another one."
            return render_template('register.html', error=error)  # Display error if username exists
        
        # Create a new user and add to the database
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()  # Commit the changes
        return redirect(url_for('login'))  # Redirect to login page after successful registration

    return render_template('register.html')


# Expenses route - Add, Edit, View, and Delete Expenses
@app.route('/expenses', methods=['GET', 'POST'])
def expenses_page():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    user_id = session['user_id']

    if request.method == 'POST':
        category = request.form['category']
        if category == "Other":
            category = request.form['category_other']
        amount = float(request.form['amount'])
        date = request.form['date']
        new_expense = Expense(user_id=user_id, category=category, amount=amount, date=date)
        db.session.add(new_expense)  # Add expense to the database
        db.session.commit()  # Commit the changes
        return redirect(url_for('expenses_page'))

    expenses = Expense.query.filter_by(user_id=user_id).all()  # Retrieve expenses from the database
    return render_template('expenses.html', expenses=expenses)

# Delete Expense
@app.route('/delete_expense/<int:id>')
def delete_expense(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    expense = Expense.query.get(id)  # Find the expense by ID
    if expense:
        db.session.delete(expense)  # Delete the expense
        db.session.commit()  # Commit the changes
    return redirect(url_for('expenses_page'))

# Edit Expense
@app.route('/edit_expense/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        category = request.form['category']
        if category == "Other":
            category = request.form['category_other']
        amount = float(request.form['amount'])
        date = request.form['date']

        expense = Expense.query.get(id)
        if expense:
            expense.category = category
            expense.amount = amount
            expense.date = date
            db.session.commit()  # Commit the changes
        return redirect(url_for('expenses_page'))

    expense = Expense.query.get(id)
    return render_template('edit_expense.html', expense=expense)

# Earnings route - Add, Edit, View, and Delete Earnings
@app.route('/earnings', methods=['GET', 'POST'])
def earnings_page():
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    user_id = session['user_id']

    if request.method == 'POST':
        category = request.form['category']
        if category == "Other":
            category = request.form['category_other']
        amount = float(request.form['amount'])
        date = request.form['date']
        new_earning = Earning(user_id=user_id, category=category, amount=amount, date=date)
        db.session.add(new_earning)  # Add earning to the database
        db.session.commit()  # Commit the changes
        return redirect(url_for('earnings_page'))

    earnings = Earning.query.filter_by(user_id=user_id).all()  # Retrieve earnings from the database
    return render_template('earnings.html', earnings=earnings)

# Delete Earning
@app.route('/delete_earning/<int:id>')
def delete_earning(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    earning = Earning.query.get(id)  # Find the earning by ID
    if earning:
        db.session.delete(earning)  # Delete the earning
        db.session.commit()  # Commit the changes
    return redirect(url_for('earnings_page'))

# Edit Earning
@app.route('/edit_earning/<int:id>', methods=['GET', 'POST'])
def edit_earning(id):
    if 'username' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        category = request.form['category']
        if category == "Other":
            category = request.form['category_other']
        amount = float(request.form['amount'])
        date = request.form['date']

        earning = Earning.query.get(id)
        if earning:
            earning.category = category
            earning.amount = amount
            earning.date = date
            db.session.commit()  # Commit the changes
        return redirect(url_for('earnings_page'))

    earning = Earning.query.get(id)
    return render_template('edit_earning.html', earning=earning)

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove user from session
    return redirect(url_for('login'))  # Redirect to login page

# Report route
@app.route('/report')
def report():
    if 'username' not in session:
        return redirect(url_for('login'))  # Ensure the user is logged in

    user_id = session['user_id']  # Get the logged-in user's ID

    # Calculate totals for the logged-in user
    total_expenses = sum(expense.amount for expense in Expense.query.filter_by(user_id=user_id))
    total_earnings = sum(earning.amount for earning in Earning.query.filter_by(user_id=user_id))

    # Aggregate expenses by category for the logged-in user
    expense_categories = {}
    for expense in Expense.query.filter_by(user_id=user_id):
        category = expense.category
        if category not in expense_categories:
            expense_categories[category] = 0
        expense_categories[category] += expense.amount

    # Aggregate earnings by category for the logged-in user
    earning_categories = {}
    for earning in Earning.query.filter_by(user_id=user_id):
        category = earning.category
        if category not in earning_categories:
            earning_categories[category] = 0
        earning_categories[category] += earning.amount

    # Render the report page with the user's specific data
    return render_template('report.html', total_expenses=total_expenses, total_earnings=total_earnings,
                           expense_categories=expense_categories, earning_categories=earning_categories)


if __name__ == "__main__":
    app.run(debug=True)
