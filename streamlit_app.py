import streamlit as st
import os
from luma.core import Luma
import json
from datetime import datetime

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'user' not in st.session_state:
    st.session_state.user = None

# Initialize Luma with the API key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', "AIzaSyD3NIhejC7JNQ5OXBFcjACVoOGHaiUzf3o")
try:
    luma = Luma(api_key=GOOGLE_API_KEY)
    print("Luma initialized successfully with Google Gemini API")
except Exception as e:
    print(f"Error initializing Luma: {str(e)}")
    luma = None

# Set page config
st.set_page_config(
    page_title="Luma Chat",
    page_icon="💬",
    layout="wide"
)

# Main chat interface
st.title("💬 Luma Chat")
st.markdown("<style>body {background-color: #007BFF; color: white;}</style>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center; color: white;'>Welcome to Luma Chat!</h2>", unsafe_allow_html=True)

# Sidebar for settings
with st.sidebar:
    st.title("Luma Chat Settings")
    st.header("Configure Your Assistant")
    
    # Model selection
    model_options = {
        "Luma 1.5 Flash": "gemini-1.5-flash",
        "Luma 1.5 Pro": "gemini-1.5-pro"
    }
    model = st.selectbox(
        "Model",
        list(model_options.keys()),
        index=0
    )
    
    # Instruction input
    instruction = st.text_area("Instructions for AI", "You are a helpful assistant.")
    
    # Predefined settings
    predefined_settings = st.selectbox(
        "Predefined Settings",
        ["Regular", "CPA Exam", "Custom"],
        index=0
    )
    
    # Temperature, Top P, Top K sliders
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    top_p = st.slider("Top P", 0.0, 1.0, 0.95)
    top_k = st.slider("Top K", 1, 100, 40)

    # Set predefined instructions based on selection
    if predefined_settings == "CPA Exam":
        instruction = "You are a study assistant for the CPA exam. Provide concise and accurate answers."
    elif predefined_settings == "Regular":
        instruction = "You are a helpful assistant."

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        st.markdown("---")

# Chat input
if prompt := st.chat_input("What would you like to know?"):
    # Add user message to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": prompt,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get AI response
    if luma:
        try:
            # Combine instruction with user prompt
            full_prompt = f"{instruction}\n{prompt}"
            response = luma.get_response(
                full_prompt,
                model=model_options[model],
                temperature=temperature,
                top_p=top_p,
                top_k=top_k
            )
            
            # Add assistant response to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Display assistant response
            with st.chat_message("assistant"):
                st.write(response)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")
    else:
        st.error("Luma is not properly initialized. Please check your API key configuration.")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

# Function to list available models
def list_available_models(luma):
    try:
        models = luma.list_models()  # Assuming this is the correct method to list models
        return models
    except Exception as e:
        print(f"Error listing models: {str(e)}")
        return []

# Call the function and print available models
available_models = list_available_models(luma)
print("Available models:", available_models) 