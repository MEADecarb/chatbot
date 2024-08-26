import time
from datetime import datetime
import tempfile
import requests
import streamlit as st
from transformers import pipeline
from streamlit_chat import message
import PyPDF2
import docx

# Initialize session state
if 'all_messages' not in st.session_state:
    st.session_state.all_messages = []
if 'tokens' not in st.session_state:
    st.session_state.tokens = []
if 'message_key' not in st.session_state:
    st.session_state.message_key = 0

# Load a pre-trained model
@st.cache_resource
def load_model():
    return pipeline("question-answering", model="distilbert/distilbert-base-cased-distilled-squad")

qa_pipeline = load_model()

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
                pdf_reader = PyPDF2.PdfReader(f)
                for page in pdf_reader.pages:
                    content += page.extract_text()
        elif file_type == 'docx':
            doc = docx.Document(file_path)
            content = "\n".join([para.text for para in doc.paragraphs])
        
        tokens = content.split()  # Simplified tokenization for QA model
        return tokens
    except Exception as e:
        st.error(f"Error loading and tokenizing file: {str(e)}")
        return []

# Function to find the most relevant section
def find_relevant_section(question, tokens):
    try:
        context = " ".join(tokens)
        max_length = 512  # Adjust based on your model's capabilities
        if len(context) > max_length:
            context = context[:max_length]
        result = qa_pipeline(question=question, context=context, clean_up_tokenization_spaces=True)
        return result['answer']
    except Exception as e:
        st.error(f"Error in question answering: {str(e)}")
        return "I'm sorry, I couldn't process that question. Could you try rephrasing it?"

# Message display and sending
def display_messages():
    for msg in st.session_state.all_messages[-50:]:  # Display last 50 messages
        if 'key' not in msg:
            msg['key'] = f"added_{time.time()}"
        message(f"{msg['user']} ({msg['time']}): {msg['text'][:500]}{'...' if len(msg['text']) > 500 else ''}",
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

@st.cache_data
def load_default_file():
    response = requests.get(default_file_url)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as tmp_file:
            tmp_file.write(response.content)
            return tmp_file.name
    else:
        st.error("Failed to load the default file. Please upload a file manually.")
        return None

if not st.session_state.tokens:
    with st.spinner("Loading and tokenizing default file..."):
        file_path = load_default_file()
        if file_path:
            st.session_state.tokens = load_and_tokenize_file(file_path)
            st.success("Default file loaded and tokenized successfully!")

# Option to upload a custom file
custom_file = st.file_uploader("Or upload your own file", type=['txt', 'pdf', 'docx'])

if custom_file is not None:
    file_size = custom_file.size
    if file_size > 10 * 1024 * 1024:  # 10 MB limit
        st.error("File size exceeds 10 MB limit. Please upload a smaller file.")
    else:
        with st.spinner("Processing uploaded file..."):
            file_type = custom_file.name.split('.')[-1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{file_type}') as tmp_file:
                tmp_file.write(custom_file.getvalue())
                file_path = tmp_file.name
            st.session_state.tokens = load_and_tokenize_file(file_path, file_type)
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
