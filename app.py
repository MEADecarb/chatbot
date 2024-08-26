import streamlit as st
import requests
import tempfile
from transformers import AutoTokenizer, AutoModelForQuestionAnswering
import torch
from PyPDF2 import PdfReader
import io

# Initialize session state
if 'context' not in st.session_state:
  st.session_state.context = ""
if 'messages' not in st.session_state:
  st.session_state.messages = []

@st.cache_resource
def load_qa_model():
  tokenizer = AutoTokenizer.from_pretrained("distilbert-base-cased-distilled-squad")
  model = AutoModelForQuestionAnswering.from_pretrained("distilbert-base-cased-distilled-squad")
  return tokenizer, model

tokenizer, model = load_qa_model()

def extract_text_from_pdf(file):
  pdf_reader = PdfReader(file)
  text = ""
  for page in pdf_reader.pages:
      text += page.extract_text()
  return text

def load_text_from_url(url):
  response = requests.get(url)
  if response.status_code == 200:
      return response.text
  else:
      st.error(f"Failed to load text from URL. Status code: {response.status_code}")
      return ""

def get_answer(question, context):
  inputs = tokenizer(question, context, return_tensors="pt")
  with torch.no_grad():
      outputs = model(**inputs)
  answer_start = torch.argmax(outputs.start_logits)
  answer_end = torch.argmax(outputs.end_logits) + 1
  answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(inputs["input_ids"][0][answer_start:answer_end]))
  return answer

st.title("Chat with PDF or Text Content")

# Source selection
source = st.radio("Choose your source:", ("PDF File", "URL Content"))

if source == "PDF File":
  uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
  if uploaded_file is not None:
      st.session_state.context = extract_text_from_pdf(uploaded_file)
      st.success("PDF uploaded and processed successfully!")
else:
  url = "https://energy.maryland.gov/Documents/082224_CandT.txt.txt"
  if st.button("Load content from URL"):
      st.session_state.context = load_text_from_url(url)
      st.success("Content loaded from URL successfully!")

# Chat interface
st.subheader("Chat")
for message in st.session_state.messages:
  with st.chat_message(message["role"]):
      st.markdown(message["content"])

if prompt := st.chat_input("Ask a question about the content"):
  st.session_state.messages.append({"role": "user", "content": prompt})
  with st.chat_message("user"):
      st.markdown(prompt)

  with st.chat_message("assistant"):
      if st.session_state.context:
          response = get_answer(prompt, st.session_state.context)
          st.markdown(response)
          st.session_state.messages.append({"role": "assistant", "content": response})
      else:
          st.markdown("Please upload a PDF or load content from the URL first.")

# Clear chat history
if st.button("Clear Chat History"):
  st.session_state.messages = []
  st.experimental_rerun()
