from typing import List, Optional
import os
from dotenv import load_dotenv
from pydantic import BaseModel
from rich.console import Console
from rich.markdown import Markdown
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable or use default
DEFAULT_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBmoqSBO3vZLUnqIGZr_qYSDmm26kFOAIw")

class Message(BaseModel):
    role: str
    content: str

class Luma:
    def __init__(self, api_key: str = DEFAULT_API_KEY):
        """Initialize Luma with Google Gemini API."""
        self.console = Console()
        try:
            # Configure the Google Generative AI with the API key
            genai.configure(api_key=api_key)
            
            # Initialize the model
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            self.initialize_personality()
            
        except Exception as e:
            self.console.print(f"[bold red]Error initializing Luma:[/] {str(e)}")
            raise
    
    def initialize_personality(self):
        """Initialize Luma's personality and context."""
        self.system_prompt = """You are Luma, a friendly and capable AI assistant. You are:
        - Helpful and supportive
        - Clear and concise in your communication
        - Knowledgeable but humble
        - Proactive in offering relevant suggestions
        
        When sharing code, always format it using markdown code blocks with the appropriate language specified:
        ```python
        # Python code example
        def hello_world():
            print("Hello, world!")
        ```
        
        For inline code, use backticks like `this`.
        
        When explaining concepts, use clear headers and organized structure:
        # Main Topic
        ## Subtopic
        
        You should always strive to provide accurate, helpful responses while maintaining
        a warm and engaging conversation style."""
        
        try:
            # Initialize the chat with the system prompt
            self.messages = [{"role": "system", "content": self.system_prompt}]
        except Exception as e:
            self.console.print(f"[bold red]Error initializing personality:[/] {str(e)}")
            raise
    
    def get_response(self, message: str, model: str = None, system_prompt: str = None, 
                    temperature: float = 0.7, top_p: float = 0.95, top_k: int = 40) -> str:
        """Process a user message and return a response with customizable settings."""
        try:
            # Add user message to conversation
            self.messages.append({"role": "user", "content": message})
            
            # Use provided system prompt or default
            current_system_prompt = system_prompt if system_prompt is not None else self.system_prompt
            
            # Create generation config with provided parameters
            generation_config = {
                "temperature": temperature,
                "top_p": top_p,
                "top_k": top_k,
            }
            
            # Use specified model or default
            if model and model != self.model.model_name:
                current_model = genai.GenerativeModel(model)
            else:
                current_model = self.model
            
            # Include the system prompt in the generation
            prompt = f"{current_system_prompt}\n\nUser: {message}"
            response = current_model.generate_content(prompt, generation_config=generation_config)
            
            # Extract the response text
            response_text = response.text
            
            # Add assistant's response to conversation history
            self.messages.append({"role": "assistant", "content": response_text})
            
            return response_text
            
        except Exception as e:
            error_msg = str(e)
            if "Unauthorized" in error_msg:
                error_msg = """Authentication Error: Your API key is invalid or not properly configured.
                Please check your API key and try again."""
            elif "429" in error_msg or "quota" in error_msg.lower():
                error_msg = """I apologize, but I've hit the API quota limit. This means:
                1. The current API key has reached its usage limit
                2. You may need to:
                   - Wait a while before trying again
                   - Use a different API key
                   - Check your Google AI API dashboard for quota limits
                Please try again later or contact the administrator for a new API key."""
            else:
                error_msg = f"I apologize, but I encountered an error: {str(e)}"
            
            self.console.print(f"[bold red]Error in get_response:[/] {str(e)}")
            return error_msg
    
    def display_message(self, message: str, is_user: bool = False):
        """Display a message in the console with appropriate formatting."""
        if is_user:
            self.console.print(f"[bold blue]You:[/] ", end="")
        else:
            self.console.print(f"[bold green]Luma:[/] ", end="")
        
        # Render markdown for assistant messages
        if not is_user:
            self.console.print(Markdown(message))
        else:
            self.console.print(message)
    
    def run(self):
        """Run the interactive chat loop."""
        self.console.print("[bold purple]Welcome to Luma AI Assistant![/]")
        self.console.print("[bold purple]Using Google's Gemini model[/]")
        self.console.print("Type 'exit' or 'quit' to end the conversation.\n")
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['exit', 'quit']:
                    self.console.print("\n[bold purple]Goodbye! Have a great day![/]")
                    break
                
                response = self.get_response(user_input)
                print("\nLuma:", end=" ")
                self.console.print(Markdown(response))
                print()
                
            except KeyboardInterrupt:
                self.console.print("\n\n[bold purple]Goodbye! Have a great day![/]")
                break
            except Exception as e:
                self.console.print(f"[bold red]Error:[/] {str(e)}") 