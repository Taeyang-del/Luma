# Luma AI Assistant

Luma is an intelligent AI assistant powered by Google's Gemini-Pro model. It's designed to be helpful, friendly, and capable of handling a wide range of tasks through natural conversation.

## Features

- Natural language conversation using Google's state-of-the-art Gemini-Pro model
- Context-aware responses
- Customizable personality
- Command-line interface
- Easy to extend and customize
- Free to use with Google AI API

## Prerequisites

1. Get a free Google AI API key from: https://aistudio.google.com/app/apikey
2. Save your API key - you'll need it to run Luma

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run Luma with your API key:
   ```bash
   python -m luma --api-key "your_api_key_here"
   ```
   
   Alternatively, you can set the API key as an environment variable:
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   python -m luma
   ```

## Usage

Simply start a conversation with Luma by running the application. You can:
- Ask questions
- Request assistance with tasks
- Have natural conversations
- Use specific commands (type /help to see available commands)

## Configuration

Luma can be customized through the `config.py` file, where you can adjust:
- Model parameters
- Personality traits
- Command prefixes
- Response formatting

## License

MIT License - Feel free to use and modify as needed.

# Luma Deployment Configuration

This repository contains the deployment configuration for the Luma application using Render's infrastructure as code.

## render.yaml Configuration

The `render.yaml` file defines the deployment settings for the Luma web application. Here's a breakdown of the configuration:

### Service Configuration
- **Type**: Web service
- **Name**: luma
- **Runtime**: Python 3.9.0
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python3 -m luma web`

### Environment Variables
1. **Python Version**: Set to 3.9.0 for compatibility
2. **Google Authentication**:
   - `GOOGLE_CLIENT_ID`: For Google Sign-In integration
   - `GOOGLE_API_KEY`: For Google API access
3. **Flask Configuration**:
   - `FLASK_ENV`: Set to production
4. **Security Settings**:
   - `SESSION_COOKIE_SECURE`: Enabled for HTTPS-only cookies
   - `SESSION_COOKIE_HTTPONLY`: Prevents JavaScript access to cookies
   - `SESSION_COOKIE_SAMESITE`: Set to Lax for security
5. **Session Management**:
   - `PERMANENT_SESSION_LIFETIME`: 7 days (604800 seconds)
   - `SESSION_TYPE`: Filesystem-based session storage
   - `SESSION_FILE_THRESHOLD`: 500 sessions

### Security Notes
- Google credentials (`GOOGLE_CLIENT_ID` and `GOOGLE_API_KEY`) are marked with `sync: false` to ensure they are securely managed through Render's dashboard
- Session cookies are configured with security best practices
- The application runs in production mode with appropriate security headers

## Deployment
1. Push this configuration to your GitHub repository
2. Connect your repository to Render
3. Set up the required environment variables in Render's dashboard
4. Deploy your application

## Requirements
- Python 3.9.0 or higher
- All dependencies listed in requirements.txt
- Valid Google OAuth credentials 