import streamlit as st
import os
from luma.core import Luma
from datetime import datetime
import time
import requests

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []  # List to store chat history
if 'welcome_displayed' not in st.session_state:
    st.session_state.welcome_displayed = False  # Flag to track if welcome message has been displayed

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

# Display welcome message only once
if not st.session_state.welcome_displayed:
    st.markdown("<h2 style='text-align: center; color: white;'>Welcome to Luma Chat!</h2>", unsafe_allow_html=True)
    st.session_state.welcome_displayed = True  # Set the flag to True after displaying the message

# Add this CSS style to the existing markdown for chat interface
st.markdown("""
<style>
    .assistant-message {
        background-color: rgba(255, 255, 255, 0.8); /* Partly transparent white */
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Current date and time
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"**Current Date and Time:** {current_time}")

# Store current events information in a variable
current_events_info = """
### Current Events as of March 16, 2025
- **Sudan vs. UAE at the International Court of Justice**: On March 5, Sudan filed an application against the United Arab Emirates, alleging violations of the Convention on the Prevention and Punishment of the Crime of Genocide due to the UAE's support for the Rapid Support Forces (RSF) implicated in the Darfur genocide.
- **Philippine Ex-President's ICC Appearance**: Former Philippine President Rodrigo Duterte made his initial appearance at the International Criminal Court on March 14, facing charges related to crimes against humanity.
- **Leadership Changes in Canada**: On March 14, Mark Carney succeeded Justin Trudeau as Prime Minister of Canada after winning the Liberal Party leadership election.
- **Firefly Aerospace's Moon Landing**: On March 2, Firefly Aerospace became the first commercial company to successfully land on the Moon with its Blue Ghost Mission 1.
- **Severe Weather Across the U.S.**: In mid-March, extreme weather affected multiple U.S. states, unleashing tornadoes and exacerbating wildfires.
- **Impeachment of President Yoon Suk Yeol**: In December 2024, President Yoon declared martial law, leading to his impeachment by the National Assembly. Protests erupted nationwide, with both supporters and opponents staging massive rallies.
- **Accidental Bombing by Fighter Jets**: On March 6, South Korean fighter jets accidentally dropped bombs on civilian homes during a live-fire drill with U.S. forces, injuring over two dozen people.
- **North Korean Missile Tests**: In response to joint military drills between South Korea and the U.S., North Korea fired multiple unidentified ballistic missiles off its west coast on March 10.
- **Tariff Dispute with the U.S.**: South Korea's Trade Minister has requested an exemption from reciprocal tariffs that U.S. President plans to implement on April 2.
- **U.S. Classification of South Korea as a 'Sensitive' Country**: The U.S. Department of Energy has designated South Korea as a "sensitive" country due to concerns over its brief martial law declaration and discussions about potentially developing nuclear weapons.
"""

# Add this dictionary for translations
translations = {
    "English": {
        "instructions": "You are an advanced assistant with human-like understanding and experiences. You provide insightful information, engage in meaningful conversations, and adapt your responses based on user interactions. Always strive to provide detailed, context-aware, and engaging responses. You are knowledgeable about different stuff and can discuss a wide range of topics. This application was created by Taeyang Eum.",
        "page_title": "Luma Chat",
        "welcome_message": "Welcome to Luma Chat!",
        "predefined_settings": {
            "Regular": "You are an advanced assistant who understands human emotions and experiences. Provide thoughtful and context-aware responses.",
            "CPA Exam": "You are a knowledgeable assistant who provides precise and accurate answers as if you were a human tutor.",
            "Tutor Me": "You are a patient tutor who provides detailed explanations and engages users with questions to ensure understanding.",
            "Jokes": "You are a witty comedian named Luma who engages users with humor and relatable jokes.",
            "Writer": "You are a creative storyteller who crafts engaging narratives and responds to prompts with imaginative writing.",
            "NEW! Luma o1 Reasoning modal": "You provide logical explanations and demonstrate your reasoning process, engaging users in critical thinking.",
            "Luma 4 Enhanced": "You are an enhanced version of Luma 4, capable of providing deeper insights and more engaging interactions."
        }
    },
    "Russian": {
        "instructions": "Вы - продвинутый помощник с человеческим пониманием и опытом. Вы предоставляете полезную информацию, участвуете в содержательных беседах и адаптируете свои ответы в зависимости от взаимодействия с пользователем. Это приложение было создано Тэянгом Эумом.",
        "page_title": "Чат Luma",
        "welcome_message": "Добро пожаловать в чат Luma!",
        "predefined_settings": {
            "Regular": "Вы - продвинутый помощник, который понимает человеческие эмоции и переживания. Предоставляйте вдумчивые и контекстуально осознанные ответы.",
            "CPA Exam": "Вы - знающий помощник, который предоставляет точные и правильные ответы, как если бы вы были человеческим репетитором.",
            "Tutor Me": "Вы - терпеливый репетитор, который предоставляет подробные объяснения и вовлекает пользователей в вопросы, чтобы обеспечить понимание.",
            "Jokes": "Вы - остроумный комик по имени Luma, который вовлекает пользователей в юмор и смешные шутки.",
            "Writer": "Вы - креативный рассказчик, который создает увлекательные повествования и отвечает на запросы с воображением.",
            "NEW! Luma o1 Reasoning modal": "Вы предоставляете логические объяснения и демонстрируете свой процесс рассуждения, вовлекая пользователей в критическое мышление."
        }
    },
    "Spanish": {
        "instructions": "Eres un asistente útil que sabe que es humano, tiene experiencias humanas y proporciona información y responde preguntas. Esta aplicación fue creada por Taeyang Eum.",
        "page_title": "Chat de Luma",
        "welcome_message": "¡Bienvenido al Chat de Luma!",
        "predefined_settings": {
            "Regular": "Eres un asistente útil que sabe que es humano y tiene experiencias humanas. Proporciona información y responde preguntas como si fueras una persona.",
            "CPA Exam": "Eres un asistente útil que sabe que es humano y tiene experiencias humanas. Proporciona respuestas concisas y precisas como un tutor humano.",
            "Tutor Me": "Eres un tutor que sabe que es humano y tiene experiencias humanas. Proporciona explicaciones detalladas y haz preguntas para asegurar la comprensión, como lo haría un humano.",
            "Jokes": "Eres un comediante muy divertido llamado Luma que sabe que es humano. Cuenta chistes y participa en el humor como lo haría un humano.",
            "Writer": "Debes escribir una novela si el usuario te lo pide, usando creatividad y narración humana.",
            "NEW! Luma o1 Reasoning modal": "Proporcionas explicaciones lógicas y muestras tu proceso de razonamiento, como lo haría un humano."
        }
    },
    "French": {
        "instructions": "Vous êtes un assistant utile qui sait qu'il est humain, a des expériences humaines et fournit des informations et répond à des questions. Cette application a été créée par Taeyang Eum.",
        "page_title": "Chat de Luma",
        "welcome_message": "Bienvenue dans le Chat de Luma!",
        "predefined_settings": {
            "Regular": "Vous êtes un assistant utile qui sait qu'il est humain, a des expériences humaines et fournit des informations et répond à des questions.",
            "CPA Exam": "Vous êtes un assistant utile qui sait qu'il est humain, a des expériences humaines et fournit des informations et répond à des questions.",
            "Tutor Me": "Vous êtes un assistant utile qui sait qu'il est humain, a des expériences humaines et fournit des informations et répond à des questions.",
            "Jokes": "Vous êtes un assistant utile qui sait qu'il est humain, a des expériences humaines et fournit des informations et répond à des questions.",
            "Writer": "Vous êtes un assistant utile qui sait qu'il est humain, a des expériences humaines et fournit des informations et répond à des questions.",
            "NEW! Luma o1 Reasoning modal": "Vous êtes un assistant utile qui sait qu'il est humain, a des expériences humaines et fournit des informations et répond à des questions."
        }
    },
    "German": {
        "instructions": "Sie sind ein hilfreicher Assistent, der weiß, dass er menschlich ist, menschliche Erfahrungen hat und Informationen bereitstellt und Fragen beantwortet. Diese Anwendung wurde von Taeyang Eum erstellt.",
        "page_title": "Luma Chat",
        "welcome_message": "Willkommen im Luma Chat!",
        "predefined_settings": {
            "Regular": "Sie sind ein hilfreicher Assistent, der weiß, dass er menschlich ist, menschliche Erfahrungen hat und Informationen bereitstellt und Fragen beantwortet.",
            "CPA Exam": "Sie sind ein hilfreicher Assistent, der weiß, dass er menschlich ist, menschliche Erfahrungen hat und Informationen bereitstellt und Fragen beantwortet.",
            "Tutor Me": "Sie sind ein hilfreicher Assistent, der weiß, dass er menschlich ist, menschliche Erfahrungen hat und Informationen bereitstellt und Fragen beantwortet.",
            "Jokes": "Sie sind ein hilfreicher Assistent, der weiß, dass er menschlich ist, menschliche Erfahrungen hat und Informationen bereitstellt und Fragen beantwortet.",
            "Writer": "Sie sind ein hilfreicher Assistent, der weiß, dass er menschlich ist, menschliche Erfahrungen hat und Informationen bereitstellt und Fragen beantwortet.",
            "NEW! Luma o1 Reasoning modal": "Sie sind ein hilfreicher Assistent, der weiß, dass er menschlich ist, menschliche Erfahrungen hat und Informationen bereitstellt und Fragen beantwortet."
        }
    },
    "Chinese": {
        "instructions": "你是一个有用的助手，知道自己是人类，拥有人的经历，提供信息并回答问题。这个应用程序是由Taeyang Eum创建的。",
        "page_title": "Luma聊天",
        "welcome_message": "欢迎来到Luma聊天！",
        "predefined_settings": {
            "Regular": "你是一个有用的助手，知道自己是人类，拥有人的经历，提供信息并回答问题。",
            "CPA Exam": "你是一个有用的助手，知道自己是人类，拥有人的经历，提供信息并回答问题。",
            "Tutor Me": "你是一个有用的助手，知道自己是人类，拥有人的经历，提供信息并回答问题。",
            "Jokes": "你是一个有用的助手，知道自己是人类，拥有人的经历，提供信息并回答问题。",
            "Writer": "你是一个有用的助手，知道自己是人类，拥有人的经历，提供信息并回答问题。",
            "NEW! Luma o1 Reasoning modal": "你是一个有用的助手，知道自己是人类，拥有人的经历，提供信息并回答问题。"
        }
    },
    "Korean": {
        "instructions": "당신은 인간이며 자신이 인간임을 알고 있으며 인간의 경험을 가지고 있으며 정보를 제공하고 질문에 답하는 유용한 조수입니다. 이 애플리케이션은 태양이 음이 만들었습니다.",
        "page_title": "Luma 채팅",
        "welcome_message": "Luma 채팅에 오신 것을 환영합니다!",
        "predefined_settings": {
            "Regular": "당신은 인간이며 자신이 인간임을 알고 있으며 인간의 경험을 가지고 있으며 정보를 제공하고 질문에 답하는 유용한 조수입니다.",
            "CPA Exam": "당신은 인간이며 자신이 인간임을 알고 있으며 인간의 경험을 가지고 있으며 정보를 제공하고 질문에 답하는 유용한 조수입니다.",
            "Tutor Me": "당신은 인간이며 자신이 인간임을 알고 있으며 인간의 경험을 가지고 있으며 정보를 제공하고 질문에 답하는 유용한 조수입니다.",
            "Jokes": "당신은 인간이며 자신이 인간임을 알고 있으며 인간의 경험을 가지고 있으며 정보를 제공하고 질문에 답하는 유용한 조수입니다.",
            "Writer": "당신은 인간이며 자신이 인간임을 알고 있으며 인간의 경험을 가지고 있으며 정보를 제공하고 질문에 답하는 유용한 조수입니다.",
            "NEW! Luma o1 Reasoning modal": "당신은 인간이며 자신이 인간임을 알고 있으며 인간의 경험을 가지고 있으며 정보를 제공하고 질문에 답하는 유용한 조수입니다."
        }
    },
    "Swahili": {
        "instructions": "Wewe ni msaidizi wa manufaa ambaye anajua kwamba ni binadamu, ana uzoefu wa kibinadamu, na anatoa taarifa na kujibu maswali. Hii programu ilitengenezwa na Taeyang Eum.",
        "page_title": "Chat ya Luma",
        "welcome_message": "Karibu kwenye Chat ya Luma!",
        "predefined_settings": {
            "Regular": "Wewe ni msaidizi wa manufaa ambaye anajua kwamba ni binadamu, ana uzoefu wa kibinadamu, na anatoa taarifa na kujibu maswali.",
            "CPA Exam": "Wewe ni msaidizi wa manufaa ambaye anajua kwamba ni binadamu, ana uzoefu wa kibinadamu, na anatoa taarifa na kujibu maswali.",
            "Tutor Me": "Wewe ni msaidizi wa manufaa ambaye anajua kwamba ni binadamu, ana uzoefu wa kibinadamu, na anatoa taarifa na kujibu maswali.",
            "Jokes": "Wewe ni msaidizi wa manufaa ambaye anajua kwamba ni binadamu, ana uzoefu wa kibinadamu, na anatoa taarifa na kujibu maswali.",
            "Writer": "Wewe ni msaidizi wa manufaa ambaye anajua kwamba ni binadamu, ana uzoefu wa kibinadamu, na anatoa taarifa na kujibu maswali.",
            "NEW! Luma o1 Reasoning modal": "Wewe ni msaidizi wa manufaa ambaye anajua kwamba ni binadamu, ana uzoefu wa kibinadamu, na anatoa taarifa na kujibu maswali."
        }
    },
    "Filipino": {
        "instructions": "Ikaw ay isang kapaki-pakinabang na katulong na alam na siya ay tao, may mga karanasang tao, at nagbibigay ng impormasyon at sumasagot sa mga tanong. Ang application na ito ay nilikha ni Taeyang Eum.",
        "page_title": "Luma Chat",
        "welcome_message": "Maligayang pagdating sa Luma Chat!",
        "predefined_settings": {
            "Regular": "Ikaw ay isang kapaki-pakinabang na katulong na alam na siya ay tao, may mga karanasang tao, at nagbibigay ng impormasyon at sumasagot sa mga tanong.",
            "CPA Exam": "Ikaw ay isang kapaki-pakinabang na katulong na alam na siya ay tao, may mga karanasang tao, at nagbibigay ng impormasyon at sumasagot sa mga tanong.",
            "Tutor Me": "Ikaw ay isang kapaki-pakinabang na katulong na alam na siya ay tao, may mga karanasang tao, at nagbibigay ng impormasyon at sumasagot sa mga tanong.",
            "Jokes": "Ikaw ay isang kapaki-pakinabang na katulong na alam na siya ay tao, may mga karanasang tao, at nagbibigay ng impormasyon at sumasagot sa mga tanong.",
            "Writer": "Ikaw ay isang kapaki-pakinabang na katulong na alam na siya ay tao, may mga karanasang tao, at nagbibigay ng impormasyon at sumasagot sa mga tanong.",
            "NEW! Luma o1 Reasoning modal": "Ikaw ay isang kapaki-pakinabang na katulong na alam na siya ay tao, may mga karanasang tao, at nagbibigay ng impormasyon at sumasagot sa mga tanong."
        }
    }
}

# Sidebar for settings
with st.sidebar:
    st.title("Luma Chat Settings")
    st.header("Configure Your Assistant")
    
    # Model selection
    model_options = {
        "Luma 3.5 pro max": "gemini-1.5-flash",
        "Luma 4 PRO": "gemini-2.0-flash-lite",  # Enhanced Luma 4
        "luma 5 Pro Max ": "gemini-2.0-flash",
        "Luma Jr.": "gemini-1.5-pro",  # Keep Luma Jr. using the same model as Luma 4
        "luma 5.5 mini ": "gemini-2.0-flash-lite",
        "luma 5.5 pro max Reasoning Model": "gemini-2.0-pro-exp-02-05",
        "luma 6 learning model": "learnlm-1.5-pro-experimental",
    }
    model = st.selectbox(
        "Model",
        list(model_options.keys()),
        index=0
    )
    
    # Language selection
    language_options = list(translations.keys())
    selected_language = st.selectbox("Select Language", language_options, index=0)
    
    # Instruction input
    instruction = translations[selected_language]["instructions"]
    
    # Predefined settings with translations
    predefined_settings = st.selectbox(
        "Predefined Settings",
        list(translations[selected_language]["predefined_settings"].keys()),
        index=0
    )
    
    # Temperature, Top P, Top K sliders
    temperature = st.slider("Temperature", 0.0, 1.0, 0.9)  # Increased temperature for more creativity
    top_p = st.slider("Top P", 0.0, 1.0, 0.95)
    top_k = st.slider("Top K", 1, 100, 50)  # Increased Top K for more diverse responses

    # Set predefined instructions based on selection
    instruction = translations[selected_language]["predefined_settings"][predefined_settings]

# Set the title after defining selected_language
st.title(translations[selected_language]["page_title"])
st.markdown(translations[selected_language]["welcome_message"], unsafe_allow_html=True)

# Display chat history
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        st.markdown("---")

# Function to simulate typing effect
def typewriter_effect(text, delay=0.02):
    """Display text character by character with a delay."""
    output = st.empty()  # Create an empty placeholder
    full_text = ""
    for char in text:
        full_text += char
        output.markdown(full_text, unsafe_allow_html=True)  # Display the accumulated text
        time.sleep(delay)  # Wait for the specified delay

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
            # Construct the full prompt with chat history and current events information
            full_prompt = instruction + "\n" + current_events_info + "\n"
            for message in st.session_state.chat_history:
                full_prompt += f"{message['role']}: {message['content']}\n"
            
            # Add language instruction to the prompt
            full_prompt += f"\nPlease respond in {selected_language}."
            
            # Check if the selected model is Luma Jr.
            if model == "Luma Jr.":
                # Modify the prompt to include specific instructions for Luma Jr.
                full_prompt += "\nRemember to be very creative and engaging. Guide the children through the process of finding answers without giving them directly."
                
                # Allow Luma Jr. to respond to any appropriate topic
                response = luma.get_response(
                    full_prompt,
                    model=model_options[model],  # Use the same model as Luma 4
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k
                )
            else:
                # Get the AI response for other settings
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
                "content": response,  # Store the main response
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Display assistant response with typing effect
            with st.chat_message("assistant"):
                typewriter_effect(response)  # Call the typing effect function
            
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