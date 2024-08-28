import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup

# Streamlit page configuration
st.set_page_config(page_title="Website Chatbot with Gemini", page_icon="🤖")

# Access the Gemini API key from Streamlit secrets
gemini_api_key = st.secrets["GEMINI_API_KEY"]

# Initialize the Gemini client
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-pro')

# Initialize session state for conversation history and website content
if "messages" not in st.session_state:
  st.session_state.messages = []
if "website_content" not in st.session_state:
  st.session_state.website_content = ""

def fetch_website_content(url):
  """Fetch and parse website content"""
  try:
      response = requests.get(url)
      soup = BeautifulSoup(response.content, 'html.parser')
      return soup.get_text()
  except Exception as e:
      st.error(f"Error fetching website content: {str(e)}")
      return ""

def generate_response(user_input):
  """Generate a response using the Gemini model"""
  try:
      # Prepare the conversation history for the model
      conversation = [
          {"role": "user", "parts": [f"You are a chatbot that answers questions about the following website content: {st.session_state.website_content[:1000]}..."]},
          {"role": "model", "parts": ["Understood. I'm ready to answer questions about the website content you provided."]}
      ]
      
      for i, msg in enumerate(st.session_state.messages):
          role = "user" if i % 2 == 0 else "model"
          conversation.append({"role": role, "parts": [msg]})
      
      conversation.append({"role": "user", "parts": [user_input]})
      
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

# Website URL input
website_url = st.text_input("Enter the website URL you want to chat about:")

if website_url:
  if website_url != st.session_state.get('last_url', ''):
      st.session_state.website_content = fetch_website_content(website_url)
      st.session_state.last_url = website_url
      st.session_state.messages = []  # Clear previous conversation
  
  st.write("Website content loaded. You can now ask questions about it!")

  # Display chat history
  for message in st.session_state.messages:
      with st.chat_message("user" if st.session_state.messages.index(message) % 2 == 0 else "assistant"):
          st.write(message)

  # User input
  user_input = st.chat_input("Your question about the website:")

  # Generate response and display
  if user_input:
      st.session_state.messages.append(user_input)
      with st.chat_message("user"):
          st.write(user_input)
      
      with st.chat_message("assistant"):
          response = generate_response(user_input)
          st.write(response)
      
      st.session_state.messages.append(response)
else:
  st.write("Please enter a website URL to start chatting about its content.")
