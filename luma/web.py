from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from google.oauth2 import id_token
from google.auth.transport import requests
from flask_cors import CORS
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import os
from .core import Luma
from .database import db, User, Chat, Message
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Get the absolute path to the luma directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "luma.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Generate a fixed secret key if it doesn't exist
secret_key_path = os.path.join(BASE_DIR, 'secret_key')
if not os.path.exists(secret_key_path):
    with open(secret_key_path, 'wb') as f:
        f.write(os.urandom(24))
with open(secret_key_path, 'rb') as f:
    secret_key = f.read()

# Session configuration
app.config.update(
    SECRET_KEY=secret_key,
    SESSION_COOKIE_SECURE=True,  # Always True in production
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    SESSION_TYPE='filesystem',
    SESSION_FILE_DIR=os.path.join(BASE_DIR, 'flask_session'),
    SESSION_FILE_THRESHOLD=500
)

# Initialize extensions
db.init_app(app)
Session(app)

# Enable CORS with credentials
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:5002", "http://127.0.0.1:5002", "https://*.replit.dev"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Create necessary directories
os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)

# Create database tables
with app.app_context():
    db.create_all()

# Google Sign-In configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', "351677565370-2tied2b684ha53e6gu6jle4qqkhe2ljh.apps.googleusercontent.com")
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', "AIzaSyBmoqSBO3vZLUnqIGZr_qYSDmm26kFOAIw")

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Initialize Luma with the API key from environment variable
try:
    luma = Luma(api_key=GOOGLE_API_KEY)
    print("Luma initialized successfully with Google Gemini API")
except Exception as e:
    print(f"Error initializing Luma: {str(e)}")
    luma = None

@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.query.get(int(user_id))
        print(f"Loading user: {user.email if user else 'None'}")
        return user
    except Exception as e:
        print(f"Error loading user: {str(e)}")
        return None

@app.route('/')
def home():
    print(f"Home route - User authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        print(f"User: {current_user.email}")
    return render_template('index.html', user=current_user)

@app.route('/callback', methods=['POST'])
def callback():
    print("Callback route accessed")
    print(f"Request method: {request.method}")
    print(f"Request headers: {dict(request.headers)}")
    
    try:
        data = request.get_json()
        if not data or 'credential' not in data:
            print("No credential provided")
            return jsonify({'success': False, 'error': 'No credential provided'}), 400
            
        # Verify the token
        try:
            idinfo = id_token.verify_oauth2_token(
                data['credential'], 
                requests.Request(), 
                GOOGLE_CLIENT_ID,
                clock_skew_in_seconds=300
            )
            print(f"Token verified for user: {idinfo.get('email')}")
            
            if not idinfo.get('email_verified'):
                print("Email not verified")
                return jsonify({'success': False, 'error': 'Email not verified'}), 400
            
            userinfo = {
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', '')
            }
        except ValueError as e:
            print(f"Token verification failed: {str(e)}")
            return jsonify({'success': False, 'error': 'Invalid token'}), 400

        # Check if user exists
        user = User.query.filter_by(email=userinfo['email']).first()
        if not user:
            print("Creating new user...")
            try:
                user = User(
                    email=userinfo['email'],
                    name=userinfo.get('name', ''),
                    picture=userinfo.get('picture', '')
                )
                db.session.add(user)
                db.session.commit()
                print(f"Created new user: {user.email}")
            except Exception as e:
                db.session.rollback()
                print(f"Error creating user: {str(e)}")
                return jsonify({'success': False, 'error': 'Failed to create user'}), 500
        else:
            print(f"Found existing user: {user.email}")
            # Update user information if changed
            if (user.name != userinfo['name'] or 
                user.picture != userinfo['picture']):
                user.name = userinfo['name']
                user.picture = userinfo['picture']
                try:
                    db.session.commit()
                    print("Updated user information")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error updating user: {str(e)}")

        # Log in the user
        login_user(user, remember=True)
        print(f"User logged in successfully: {user.email}")

        # Set session data
        session.permanent = True
        session['user_id'] = user.id
        session['email'] = user.email
        session['name'] = user.name
        session['picture'] = user.picture
        session.modified = True
        
        print(f"Session data set: {dict(session)}")

        response = jsonify({
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture
            }
        })
        
        # Set additional headers for CORS
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        return response

    except Exception as e:
        print(f"Error in callback: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home'))

@app.route('/chat', methods=['POST'])
def chat():
    if not luma:
        return jsonify({
            "error": "Luma is not properly initialized. Please check your API key configuration."
        }), 500
        
    try:
        data = request.json
        message = data.get('message', '')
        settings = data.get('settings', {})
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Apply settings if provided
        model = settings.get('model', 'gemini-1.5-flash')
        system_prompt = settings.get('systemPrompt', luma.system_prompt)
        temperature = settings.get('temperature', 0.7)
        top_p = settings.get('topP', 0.95)
        top_k = settings.get('topK', 40)
        
        # Get response with the specified settings
        response = luma.get_response(
            message, 
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k
        )
        
        # Get existing chat history from cookies
        chat_history = request.cookies.get('chat_history', '[]')
        try:
            chat_history = json.loads(chat_history)
        except json.JSONDecodeError:
            chat_history = []
        
        # Add new messages to chat history
        chat_history.append({
            'role': 'user',
            'content': message,
            'timestamp': datetime.utcnow().isoformat()
        })
        chat_history.append({
            'role': 'assistant',
            'content': response,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Create response with updated chat history
        response_data = {
            "response": response,
            "chat_history": chat_history
        }
        
        # Create response object
        response_obj = jsonify(response_data)
        
        # Set cookie with updated chat history
        response_obj.set_cookie(
            'chat_history',
            json.dumps(chat_history),
            max_age=7*24*60*60,  # 7 days
            httponly=True,
            samesite='Lax'
        )
        
        return response_obj
        
    except Exception as e:
        error_message = str(e)
        if "Unauthorized" in error_message:
            return jsonify({
                "error": "Authentication Error: Your API key is invalid or not properly configured."
            }), 401
        return jsonify({"error": error_message}), 500

def run_web():
    """Run the web interface."""
    app.run(host='0.0.0.0', port=5002, debug=True) 