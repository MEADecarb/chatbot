import time
from datetime import datetime
import tempfile
import requests
import streamlit as st
from transformers import pipeline
from streamlit_chat import message

# Initialize session state
if 'all_messages' not in st.session_state:
    st.session_state.all_messages = []
if 'tokens' not in st.session_state:
    st.session_state.tokens = []
if 'message_key' not in st.session_state:
    st.session_state.message_key = 0

# Load a pre-trained model
qa_pipeline = pipeline("question-answering")

# UI Setup
st.set_page_config(page_title="Doc-Bot", page_icon="👋")
st.markdown("<h1 style='text-align: center; color: red;'>Doc-Bot👋</h1>", unsafe_allow_html=True)

# File handling functions
@st.cache_data
def load_and_tokenize_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        tokens = []
        progress_bar = st.progress(0)
        word_list = content.split()
        for i, token in enumerate(word_list):
            tokens.append(token)
            progress_bar.progress((i + 1) / len(word_list))
        return tokens
    except Exception as e:
        st.error(f"Error loading and tokenizing file: {str(e)}")
        return []

# Function to find the most relevant section
def find_relevant_section(question, tokens):
    context = " ".join(tokens)
    return qa_pipeline(question=question, context=context)['answer']

# Message display and sending
def display_messages():
    for msg in st.session_state.all_messages[-50:]:  # Display last 50 messages
        if 'key' not in msg:
            msg['key'] = f"added_{time.time()}"
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
        bot_response = find_relevant_section(user_query, st.session_state.tokens)
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
    with st.spinner("Loading and tokenizing default file..."):
        response = requests.get(default_file_url)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
                tmp_file.write(response.content)
                file_path = tmp_file.name
            st.session_state.tokens = load_and_tokenize_file(file_path)
            st.success("Default file loaded and tokenized successfully!")
        else:
            st.error("Failed to load the default file. Please upload a file manually.")

# Option to upload a custom file
custom_file = st.file_uploader("Or upload your own text file", type=['txt'])

if custom_file is not None:
    with st.spinner("Processing uploaded file..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
            tmp_file.write(custom_file.getbuffer())
            file_path = tmp_file.name
        st.session_state.tokens = load_and_tokenize_file(file_path)
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
