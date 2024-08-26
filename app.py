import time
from datetime import datetime
import tempfile
import requests

import streamlit as st
from streamlit_chat import message

# Initialize session state
if 'all_messages' not in st.session_state:
  st.session_state.all_messages = []
if 'tokens' not in st.session_state:
  st.session_state.tokens = []
if 'message_key' not in st.session_state:
  st.session_state.message_key = 0

# UI Setup
st.set_page_config(page_title="Doc-Bot", page_icon="👋")
st.markdown("<h1 style='text-align: center; color: red;'>Doc-Bot👋</h1>", unsafe_allow_html=True)

# File handling functions
@st.cache_data
def tokenize_text_file(file_path):
  try:
      with open(file_path, 'r', encoding='utf-8') as f:
          content = f.read()
      # Implement more sophisticated tokenization here if needed
      tokens = content.split()
      return tokens
  except Exception as e:
      st.error(f"Error tokenizing file: {str(e)}")
      return []

# API interaction
def query_grok_api(query, tokens):
  url = "https://api.grok.com/v1/query"  # Replace with actual Grok API endpoint
  headers = {
      "Authorization": f"Bearer {st.secrets['GROK_API_KEY']}",
      "Content-Type": "application/json"
  }
  data = {
      "query": query,
      "documents": tokens
  }
  try:
      response = requests.post(url, json=data, headers=headers)
      response.raise_for_status()
      return response.json().get("response", "No response from Grok API")
  except requests.RequestException as e:
      return f"Error: {str(e)}"

# Message display and sending
def display_messages():
  for msg in st.session_state.all_messages:
      message(f"{msg['user']} ({msg['time']}): {msg['text']}", 
              is_user=msg['user']=='You', 
              key=msg['key'])

def send_message(user_query):
  if user_query:
      st.session_state.message_key += 1
      st.session_state.all_messages.append({
          'user': 'You', 
          'time': datetime.now().strftime("%H:%M"), 
          'text': user_query,
          'key': f"user_{st.session_state.message_key}"
      })
      bot_response = query_grok_api(user_query, st.session_state.tokens)
      st.session_state.message_key += 1
      st.session_state.all_messages.append({
          'user': 'Bot', 
          'time': datetime.now().strftime("%H:%M"), 
          'text': bot_response,
          'key': f"bot_{st.session_state.message_key}"
      })

# Main app logic
default_file_url = "https://energy.maryland.gov/Documents/082224_CandT.txt.txt"

if not st.session_state.tokens:
  with st.spinner("Loading default file..."):
      response = requests.get(default_file_url)
      if response.status_code == 200:
          with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
              tmp_file.write(response.content)
              file_path = tmp_file.name
          st.session_state.tokens = tokenize_text_file(file_path)
          st.success("Default file loaded successfully!")
      else:
          st.error("Failed to load default file. Please upload a file manually.")

# Option to upload a custom file
custom_file = st.file_uploader("Or upload your own text file", type=['txt'])

if custom_file is not None:
  with st.spinner("Processing uploaded file..."):
      with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
          tmp_file.write(custom_file.getbuffer())
          file_path = tmp_file.name
      st.session_state.tokens = tokenize_text_file(file_path)
  st.success("Custom file processed successfully!")

# Chat interface
st.subheader("Chat with Doc-Bot")
user_query = st.text_input("You: ", key="input")

if st.button("Send"):
  send_message(user_query)

display_messages()

# Clear chat history button
if st.button("Clear Chat History"):
  st.session_state.all_messages = []
  st.session_state.message_key = 0
  st.experimental_rerun()
