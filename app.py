import os
import time
from datetime import datetime
import tempfile

import streamlit as st
from streamlit_chat import message
import requests

# Initialize session state
if 'all_messages' not in st.session_state:
  st.session_state.all_messages = []
if 'tokens' not in st.session_state:
  st.session_state.tokens = []

# UI Setup
st.set_page_config(page_title="Doc-Bot", page_icon="👋")
st.markdown("<h1 style='text-align: center; color: red;'>Doc-Bot👋</h1>", unsafe_allow_html=True)

# File handling functions
def save_uploaded_file(uploadedfile):
  with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
      tmp_file.write(uploadedfile.getbuffer())
      return tmp_file.name

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
  message_container = st.container()
  with message_container:
      for msg in st.session_state.all_messages:
          message(f"{msg['user']} ({msg['time']}): {msg['text']}", 
                  is_user=msg['user']=='You', 
                  key=msg['time'])

def send_message(user_query):
  if user_query:
      st.session_state.all_messages.append({
          'user': 'You', 
          'time': datetime.now().strftime("%H:%M"), 
          'text': user_query
      })
      bot_response = query_grok_api(user_query, st.session_state.tokens)
      st.session_state.all_messages.append({
          'user': 'Bot', 
          'time': datetime.now().strftime("%H:%M"), 
          'text': bot_response
      })

# Main app logic
datafile = st.file_uploader("Upload your text file", type=['txt'])

if datafile is not None:
  with st.spinner("Processing file..."):
      file_path = save_uploaded_file(datafile)
      st.session_state.tokens = tokenize_text_file(file_path)
  st.success("File processed successfully!")

  # Chat interface
  st.subheader("Chat with Doc-Bot")
  user_query = st.text_input("You: ", key="input")
  
  if st.button("Send"):
      send_message(user_query)
  
  display_messages()

else:
  st.info("Please upload a text file to start chatting.")
