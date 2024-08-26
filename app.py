import time
from datetime import datetime
import tempfile
import requests
import streamlit as st
from transformers import pipeline
from streamlit_chat import message
import os
from PyPDF2 import PdfReader
import docx2txt
import tiktoken

# Initialize session state
if 'all_messages' not in st.session_state:
  st.session_state.all_messages = []
if 'tokens' not in st.session_state:
  st.session_state.tokens = []
if 'message_key' not in st.session_state:
  st.session_state.message_key = 0

# Load a pre-trained model
@st.cache_resource
def load_qa_pipeline():
  return pipeline("question-answering", model="distilbert-base-cased-distilled-squad")

qa_pipeline = load_qa_pipeline()

# UI Setup
st.set_page_config(page_title="Doc-Bot", page_icon="👋")
st.markdown("<h1 style='text-align: center; color: red;'>Doc-Bot👋</h1>", unsafe_allow_html=True)

# File handling functions
@st.cache_data
def load_and_tokenize_file(file_path, file_type='txt'):
  try:
      content = ""
      if file_type == 'txt':
          with open(file_path, 'r', encoding='utf-8') as f:
              content = f.read()
      elif file_type == 'pdf':
          with open(file_path, 'rb') as f:
              pdf_reader = PdfReader(f)
              for page in pdf_reader.pages:
                  content += page.extract_text()
      elif file_type == 'docx':
          content = docx2txt.process(file_path)
      
      # Tokenize using tiktoken
      enc = tiktoken.get_encoding("cl100k_base")
      tokens = enc.encode(content)
      
      progress_bar = st.progress(0)
      for i in range(len(tokens)):
          progress_bar.progress((i + 1) / len(tokens))
      return tokens
  except Exception as e:
      st.error(f"Error loading and tokenizing file: {str(e)}")
      return []

# Function to find the most relevant section
def find_relevant_section(question, tokens):
  try:
      # Decode tokens to text
      enc = tiktoken.get_encoding("cl100k_base")
      context = enc.decode(tokens)
      
      # Implement sliding window for long contexts
      max_context_length = 512  # Adjust based on model's capacity
      stride = 256
      
      best_answer = ""
      best_score = 0
      
      for i in range(0, len(context), stride):
          window = context[i:i+max_context_length]
          result = qa_pipeline(question=question, context=window, clean_up_tokenization_spaces=True)
          if result['score'] > best_score:
              best_score = result['score']
              best_answer = result['answer']
      
      return best_answer
  except Exception as e:
      st.error(f"Error in finding relevant section: {str(e)}")
      return "I'm sorry, I couldn't process that question. Could you try rephrasing it?"

# Message display and sending
def display_messages():
  for msg in st.session_state.all_messages[-50:]:  # Display last 50 messages
      if 'key' not in msg:
          msg['key'] = f"added_{time.time()}"
      message(f"{msg['user']} ({msg['time']}): {msg['text'][:500]}...",  # Limit displayed message length
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
      bot_response = find_relevant_section(user_query, st.session_state.tokens)
      st.session_state.message_key += 1
      st.session_state.all_messages.append({
          'user': 'Bot',
          'time': datetime.now().strftime("%H:%M"),
          'text': bot_response,
          'key': f"bot_{st.session_state.message_key}"
      })

# Main app logic
@st.cache_data
def load_default_file(url):
  response = requests.get(url)
  if response.status_code == 200:
      with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
          tmp_file.write(response.content)
          return tmp_file.name
  else:
      st.error("Failed to load the default file. Please upload a file manually.")
      return None

default_file_url = "https://energy.maryland.gov/Documents/082224_CandT.txt.txt"

if not st.session_state.tokens:
  with st.spinner("Loading and tokenizing default file..."):
      file_path = load_default_file(default_file_url)
      if file_path:
          st.session_state.tokens = load_and_tokenize_file(file_path)
          st.success("Default file loaded and tokenized successfully!")

# Option to upload a custom file
custom_file = st.file_uploader("Or upload your own file", type=['txt', 'pdf', 'docx'])

if custom_file is not None:
  file_size = custom_file.size
  max_size = 10 * 1024 * 1024  # 10 MB limit
  if file_size > max_size:
      st.error(f"File size ({file_size/1024/1024:.2f} MB) exceeds the limit of 10 MB.")
  else:
      with st.spinner("Processing uploaded file..."):
          with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{custom_file.type.split("/")[-1]}') as tmp_file:
              tmp_file.write(custom_file.getvalue())
              file_path = tmp_file.name
          st.session_state.tokens = load_and_tokenize_file(file_path, custom_file.type.split("/")[-1])
      st.success("Custom file processed successfully!")

# Chat interface
chat_container = st.container()
with chat_container:
  st.subheader("Chat with Doc-Bot")
  display_messages()

user_query = st.text_input("You: ", key="input", max_chars=500)

if st.button("Send"):
  with st.spinner("Processing your message..."):
      send_message(user_query)
  st.experimental_rerun()

# Clear chat history button
if st.button("Clear Chat History"):
  st.session_state.all_messages = []
  st.session_state.message_key = 0
  st.experimental_rerun()

# Export chat history
if st.button("Export Chat History"):
  chat_history = "\n".join([f"{msg['user']} ({msg['time']}): {msg['text']}" for msg in st.session_state.all_messages])
  st.download_button(
      label="Download Chat History",
      data=chat_history,
      file_name="chat_history.txt",
      mime="text/plain"
  )
