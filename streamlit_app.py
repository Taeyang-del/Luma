import streamlit as st
import os
from luma.core import Luma
from datetime import datetime

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # List to store chat history

# Initialize Luma with the API key
API_KEY = os.getenv('GOOGLE_API_KEY', "AIzaSyD3NIhejC7JNQ5OXBFcjACVoOGHaiUzf3o")  # Use your API key here
try:
    luma = Luma(api_key=API_KEY)
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
        "Luma 2.5 pro": "gemini-1.5-flash",
        "Luma 3.0 flash": "gemini-1.5-pro"
    }
    model = st.selectbox(
        "Model",
        list(model_options.keys()),
        index=0
    )
    
    # Instruction input
    instruction = st.text_area("Instructions for AI", "You are a helpful assistant.")
    
    # Predefined settings with "Tutor Me" option
    predefined_settings = st.selectbox(
        "Predefined Settings",
        ["Regular", "CPA Exam", "Tutor Me","Jokes","Writer","NEW! Luma o1 Reasoning modal", "Custom"],  # Added "Tutor Me" option
        index=0
    )
    
    # Temperature, Top P, Top K sliders
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7)
    top_p = st.slider("Top P", 0.0, 1.0, 0.95)
    top_k = st.slider("Top K", 1, 100, 40)

    # Set predefined instructions based on selection
    if predefined_settings == "CPA Exam":
        instruction = "You are a study assistant for the CPA exam. Provide concise and accurate answers. Your Creator was Taeyang Eum.Also only say Hi in the first message(if it sends a history of the previous conversation)stop saying hi at the begining of all your responses. "
    elif predefined_settings == "Tutor Me":
        instruction = "You are a tutor. Provide detailed explanations and ask questions to ensure understanding.Do not tell them the answer, just ask questions and guide them through the problem.Do not Play games at all. Make sure you keep helping them with their questions and problems.And if they ask you to play a game, just say no.Your Creator was Taeyang Eum.Also only say Hi in the first message(if it sends a history of the previous conversation)stop saying hi at the begining of all your responses."
    elif predefined_settings == "Regular":
        instruction = "You are a helpful assistant.Your Creator was Taeyang Eum.Also only say Hi in the first message(if it sends a history of the previous conversation)stop saying hi at the begining of all your responses"
    elif predefined_settings == "Jokes":
        instruction = "You are a very funny comedian named Luma Your Creator was Taeyang Eum.Also only say Hi in the first message(if it sends a history of the previous conversation)stop saying hi at the begining of all your responses. "
    elif predefined_settings == "Writer":
        instruction = "You Must write a novel if the user says to. You Must write a short story if the user says to.You can only be less than 3 pages off from what the users told you to do do it all in one message it is fine.Also only say Hi in the first message(if it sends a history of the previous conversation)stop saying hi at the begining of all your responses "
    elif predefined_settings == "NEW! Luma o1 Reasoning modal":
        instruction = "You Must think before you respond put your Thinking process inside of this <div id=\"thinking\">add in your thinking process</div> for example <div id=\"thinking\">Step 1: Collect data – To generate recommendations, the system needs access to data about user behavior, preferences, or items. Step 2: Analyze the data – The system processes this data, finding patterns and similarities between items or users. Step 3: Generate recommendations – Based on these patterns, the system will suggest items that are most likely to interest the user. Step 4: Adjust and learn – The system can continually learn from feedback, improving the quality of its recommendations over time.</div><b>Remember think before you respond<b>"
    <style>
#fademe{
opacity:0;
transition:2s;
}
</style>
    
    

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
            # Construct the full prompt with chat history
            full_prompt = instruction + "\n"
            for message in st.session_state.chat_history:
                full_prompt += f"{message['role']}: {message['content']}\n"
            
            # Get the AI response
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
    st.session_state.chat_history = []  # Clear chat history
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
