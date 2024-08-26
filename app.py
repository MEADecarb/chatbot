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
        message(msg['text'], is_user=msg['is_user'], key=msg['key'])

# Input text box for user questions
def user_input():
    return st.text_input("Ask your question here...", key="input", placeholder="Type a question and hit Enter")

# Main App Logic
def main():
    st.markdown("<h2 style='text-align: center;'>Chat with Your Document</h2>", unsafe_allow_html=True)

    # Upload file
    uploaded_file = st.file_uploader("Upload your cleaned and tokenized .txt file", type=["txt", "pdf", "docx"])

    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1]
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.getvalue())
            temp_file_path = temp_file.name

        # Load and tokenize the uploaded file
        st.session_state.tokens = load_and_tokenize_file(temp_file_path, file_type)

        # Display chat interface once the file is loaded
        if st.session_state.tokens:
            user_question = user_input()

            if user_question:
                # Display the user's question
                st.session_state.all_messages.append({"text": user_question, "is_user": True, "key": f"user_{st.session_state.message_key}"})
                st.session_state.message_key += 1

                # Find and display the answer
                answer = find_relevant_section(user_question, st.session_state.tokens)
                st.session_state.all_messages.append({"text": answer, "is_user": False, "key": f"bot_{st.session_state.message_key}"})
                st.session_state.message_key += 1

            # Display conversation history
            display_messages()

# Run the app
if __name__ == "__main__":
    main()
