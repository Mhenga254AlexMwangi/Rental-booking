from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone,timedelta
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
import re



app = Flask(__name__)
app.secret_key = '22334455'

# MySQL Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:new_password@localhost/joys_apartments'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = '8bc574001@smtp-brevo.com'
app.config['MAIL_PASSWORD'] = '21VvJDtN5EMLCYSZ'
app.config['MAIL_DEFAULT_SENDER'] = ('Joy Apartments')
app.config['MAIL_DEBUG'] = True

s = URLSafeTimedSerializer(app.secret_key)

db = SQLAlchemy(app)
mail = Mail(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# Comment Model
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Home Page Route (Handles Commenting)
@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        comment_text = request.form.get('comment')

        if comment_text:
            new_comment = Comment(text=comment_text)
            db.session.add(new_comment)
            db.session.commit()
            flash('Comment submitted successfully!', 'success')
            return redirect(url_for('home'))

    # Delete old comments (older than 12 hours)
    expiration_time = datetime.now(timezone.utc) - timedelta(hours=12)
    Comment.query.filter(Comment.timestamp < expiration_time).delete()
    db.session.commit()

    # Fetch latest 3 comments
    comments = Comment.query.order_by(Comment.timestamp.desc()).limit(3).all()
    return render_template("index.html", comments=comments)

# About Page
@app.route('/about')
def about():
    return render_template('about.html')

# Contact Page

# Terms Page
@app.route('/terms')
def terms():
    return render_template('terms.html')

# Favorites Page


# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Try logging in.', 'danger')
            return redirect(url_for('signup'))

        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('Signup successful! You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# Forgot Password Route
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()

        if user:
            return redirect(url_for('reset_password', user_id=user.id))
        else:
            flash('Email not found. Please signup.', 'danger')
            return redirect(url_for('signup'))
    
    return render_template('forgot_password.html')

# Reset Password Route
@app.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
def reset_password(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_password = request.form['new_password']
        user.password = new_password
        db.session.commit()
        flash('Password reset successfully. You can now login.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html')
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50))
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)



@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']  # This is the email entered in the form
        phone = request.form.get('phone', '')
        subject = request.form['subject']
        message = request.form['message']

        # Save to database
        new_msg = ContactMessage(
            name=name,
            email=email,
            phone=phone,
            subject=subject,
            message=message,
            timestamp=datetime.now(timezone.utc)
        )
        db.session.add(new_msg)
        db.session.commit()

            
        try:
            msg = Message(
            subject=f"New Contact: {subject}",
            sender=('Joy Apartments', 'alexnjagi123@gmail.com'),  # Must match verified domain
            recipients=['alexnja254@gmail.com'],  # Where YOU want to receive it
            reply_to=email,  # The form submitter's email
            extra_headers={'X-Priority': '1'}  # Mark as important
        )
            
            # Email content
            msg.html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{
                        font-family: 'Poppins', sans-serif;
                        color: #495057;
                        line-height: 1.6;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background: linear-gradient(135deg, #4361ee 0%, #4cc9f0 100%);
                        color: white;
                        padding: 20px;
                        text-align: center;
                        border-radius: 8px 8px 0 0;
                    }}
                    .content {{
                        padding: 20px;
                        background: white;
                        border: 1px solid #eee;
                        border-radius: 0 0 8px 8px;
                    }}
                    .detail {{
                        margin-bottom: 15px;
                    }}
                    .label {{
                        font-weight: 600;
                        color: #4361ee;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2 style="margin:0;">New Contact Form Submission</h2>
                    </div>
                    <div class="content">
                        <div class="detail">
                            <span class="label">Name:</span> {name}
                        </div>
                        <div class="detail">
                            <span class="label">Email:</span> {email}
                        </div>
                        <div class="detail">
                            <span class="label">Phone:</span> {phone if phone else 'Not provided'}
                        </div>
                        <div class="detail">
                            <span class="label">Subject:</span> {subject}
                        </div>
                        <div class="detail">
                            <span class="label">Message:</span>
                            <p style="margin-top:10px;white-space:pre-line;">{message}</p>
                        </div>
                        <div class="detail">
                            <span class="label">Received:</span> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            app.logger.error(f"Failed to send email: {str(e)}")
            flash('Your message was saved but we encountered an error sending the notification.', 'warning')
            

        return redirect(url_for('contact'))

    return render_template('contact.html')

@app.route('/test')
def test():
    return "App is live without DB!"

    
    
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None



if __name__ == "__main__":
    app.run(debug=True)
