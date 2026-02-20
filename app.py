from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 'secret_key'

db = SQLAlchemy(app)

# ================== DATABASE MODEL ==================
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password.encode('utf-8')
        )

with app.app_context():
    db.create_all()


# ================== ROUTES ==================

@app.route("/")
def index():
    return render_template("index.html")


# ================== REGISTER ==================
@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name'].strip()
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        # 1. Name validation
        if not name:
            flash("Name is required!", "danger")
            return redirect('/register')

        # 2. Email validation
        if not email:
            flash("Email is required!", "danger")
            return redirect('/register')

        # 3. Password validation
        if not password:
            flash("Password is required!", "danger")
            return redirect('/register')

        # 4. Password length validation
        if len(password) < 6:
            flash("Password must be at least 6 characters!", "danger")
            return redirect('/register')

        # 5. Email uniqueness check
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered!", "danger")
            return redirect('/register')

        # If all validation passed
        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! Please login.", "success")
        return redirect('/login')

    return render_template("register.html")


# ================== LOGIN ==================
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()

        if not email or not password:
            flash("All fields are required!", "danger")
            return redirect('/login')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            flash("Login successful!", "success")
            return redirect('/dashboard')
        else:
            flash("Invalid email or password", "danger")
            return redirect('/login')

    return render_template("login.html")


# ================== DASHBOARD ==================
@app.route("/dashboard")
def dashboard():
    if 'email' in session:
        user = User.query.filter_by(email=session['email']).first()
        return render_template("dashboard.html", user=user)

    flash("Please login first", "warning")
    return redirect('/login')


# ================== LOGOUT ==================
@app.route('/logout')
def logout():
    session.pop('email', None)
    flash("Logged out successfully", "info")
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)