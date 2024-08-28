import streamlit as st
import google.generativeai as genai

# Streamlit page configuration
st.set_page_config(page_title="Website Chatbot with Gemini", page_icon="🤖")

# Access the Gemini API key from Streamlit secrets
gemini_api_key = st.secrets["GEMINI_API_KEY"]

# Initialize the Gemini client
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-pro')

# Initialize session state for conversation history
if "messages" not in st.session_state:
  st.session_state.messages = []

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
          return response.text
      else:
          return "I apologize, but I couldn't generate a response."
  except Exception as e:
      st.error(f"An error occurred: {str(e)}")
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
  st.session_state.messages.append(user_input)
  with st.chat_message("user"):
      st.write(user_input)
  
  with st.chat_message("assistant"):
      response = generate_response(user_input)
      st.write(response)
  
  st.session_state.messages.append(response)
