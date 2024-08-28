import streamlit as st
import google.generativeai as gpt

# Access the Gemini API key from the environment variable
gemini_api_key = st.secrets["GEMINI_API_KEY"]

# Initialize the Gemini client
gpt.configure(api_key=gemini_api_key)
gemini_client = gpt.models.TextGenerationModel()

# Conversation history
memory = []

def generate_response(user_input):
  """Logic to interact with Gemini API and handle conversation chain"""
  prompt = " ".join(memory) + " User: " + user_input  # Build prompt with conversation history
  response = gemini_client.generate(prompt=prompt)
  memory.append((user_input, response.text))
  return response.text

# Streamlit interface
st.title("Website Chatbot with Gemini")
st.write("Ask me anything about this website!")

user_input = st.text_input("Your question:", key="input")

if user_input:
  response = generate_response(user_input)
  st.write(response)
