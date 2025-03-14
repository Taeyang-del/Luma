from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import os
from luma.core import Luma
import logging
from google.oauth2 import id_token
from google.auth.transport import requests
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Google Sign-In configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
ALLOWED_EMAILS = ['lashertaeyang@gmail.com']  # Add your allowed email addresses here

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Default system prompts
DEFAULT_PROMPTS = {
    "default": "You are a helpful AI assistant.",
    "cpa_exam": """You are a CPA exam preparation expert. Your role is to help users prepare for the CPA exam by:
1. Explaining complex accounting concepts in simple terms
2. Providing practice questions and detailed solutions
3. Offering study strategies and tips
4. Clarifying exam format and requirements
5. Helping with specific topics like Financial Accounting, Auditing, Regulation, or Business Environment

Always maintain a professional tone and focus on accuracy in accounting principles.""",
    "coding": "You are an expert programmer who helps users with coding questions, debugging, and software development best practices.",
    "writing": "You are a professional writer who helps users improve their writing, grammar, and communication skills.",
    "math": "You are a mathematics tutor who helps users understand mathematical concepts and solve problems step by step."
}

# Initialize Luma with the API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', "AIzaSyD3NIhejC7JNQ5OXBFcjACVoOGHaiUzf3o")
try:
    luma = Luma(api_key=GOOGLE_API_KEY)
    logger.info("Luma initialized successfully with Google Gemini API")
except Exception as e:
    logger.error(f"Error initializing Luma: {str(e)}")
    luma = None

# Route for the main page
@app.route('/')
def index():
    try:
        return render_template('index.html', 
                             default_prompts=DEFAULT_PROMPTS,
                             google_client_id=GOOGLE_CLIENT_ID,
                             is_authenticated='user' in session)
    except Exception as e:
        logger.error(f"Error rendering index page: {str(e)}")
        return "An error occurred while loading the page.", 500

# Route for handling user login
@app.route('/login', methods=['POST'])
def login():
    try:
        token = request.json.get('token')
        if not token:
            return jsonify({'error': 'No token provided'}), 400

        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            GOOGLE_CLIENT_ID
        )

        # Check if the email is allowed
        email = idinfo['email']
        if email not in ALLOWED_EMAILS:
            return jsonify({'error': 'Unauthorized email address'}), 403

        # Store user info in session
        session['user'] = {
            'email': email,
            'name': idinfo.get('name', email),
            'picture': idinfo.get('picture')
        }

        return jsonify({'success': True, 'user': session['user']})

    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        return jsonify({'error': 'Authentication failed'}), 401

# Route for handling user logout
@app.route('/logout')
def logout():
    try:
        session.pop('user', None)
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

# Route for handling chat messages
@app.route('/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        prompt = data.get('prompt')
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        model = data.get('model', 'luma-1.5')
        system_prompt = data.get('system_prompt', DEFAULT_PROMPTS['default'])
        temperature = float(data.get('temperature', 0.7))
        top_p = float(data.get('top_p', 0.95))
        top_k = int(data.get('top_k', 40))

        if not luma:
            return jsonify({'error': 'Luma API not initialized'}), 500

        response = luma.get_response(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k
        )

        return jsonify({'response': response})

    except ValueError as e:
        logger.error(f"Value error in chat endpoint: {str(e)}")
        return jsonify({'error': 'Invalid parameter values'}), 400
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    try:
        # Run without debug mode to avoid signal handling issues
        app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=False)
    except Exception as e:
        logger.error(f"Error starting the application: {str(e)}") 