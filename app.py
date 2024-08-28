import streamlit as st
import google.generativeai as genai
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page configuration
st.set_page_config(page_title="Website Chatbot with Gemini", page_icon="🤖")

try:
  # Access the Gemini API key from Streamlit secrets
  gemini_api_key = st.secrets["GEMINI_API_KEY"]
  logger.info("API key successfully loaded from secrets")
except Exception as e:
  st.error(f"Failed to load API key: {str(e)}")
  logger.error(f"Failed to load API key: {str(e)}")
  st.stop()

try:
  # Initialize the Gemini client
  genai.configure(api_key=gemini_api_key)
  model = genai.GenerativeModel('gemini-pro')
  logger.info("Gemini model initialized successfully")
except Exception as e:
  st.error(f"Failed to initialize Gemini model: {str(e)}")
  logger.error(f"Failed to initialize Gemini model: {str(e)}")
  st.stop()

# Initialize session state for conversation history
if "messages" not in st.session_state:
  st.session_state.messages = []
  logger.info("Session state initialized")

def generate_response(user_input):
  """Generate a response using the Gemini model"""
  try:
      # Prepare the conversation history for the model
      conversation = [
          {"role": "user" if i % 2 == 0 else "model", "parts": [msg]}
          for i, msg in enumerate(st.session_state.messages + [user_input])
      ]
      
      # Generate a response from the Gemini model
      response = model.generate_content(conversation)
      
      if response.text:
          logger.info("Response generated successfully")
          return response.text
      else:
          logger.warning("Empty response received from model")
          return "I apologize, but I couldn't generate a response."
  except Exception as e:
      logger.error(f"Error generating response: {str(e)}")
      st.error(f"An error occurred while generating the response: {str(e)}")
      return "I'm sorry, but an error occurred while processing your request."

# Streamlit interface
st.title("Website Chatbot with Gemini")
st.write("Ask me anything about this website!")

# Display chat history
for message in st.session_state.messages:
  with st.chat_message("user" if st.session_state.messages.index(message) % 2 == 0 else "assistant"):
      st.write(message)

# User input
user_input = st.chat_input("Your question:")

# Generate response and display
if user_input:
  logger.info(f"Received user input: {user_input}")
  st.session_state.messages.append(user_input)
  with st.chat_message("user"):
      st.write(user_input)
  
  with st.chat_message("assistant"):
      response = generate_response(user_input)
      st.write(response)
  
  st.session_state.messages.append(response)
  logger.info("Response added to chat history")

# Add a footer with version information
st.markdown("---")
st.markdown("Chatbot Version 1.0 | Powered by Gemini AI")
