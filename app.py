import streamlit as st
import requests

# Function to load text from a URL
def load_text_from_url(url):
  response = requests.get(url)
  if response.status_code == 200:
      return response.text
  else:
      st.error("Failed to load the document.")
      return ""

# Function to process user input and generate a response
def generate_response(user_input, document_text):
  # Simple keyword matching for demonstration
  if user_input.lower() in document_text.lower():
      return f"I found something related to '{user_input}' in the document."
  else:
      return "I couldn't find anything related to your query in the document."

# Streamlit app
def main():
  st.title("Simple Streamlit Chatbot")
  
  # Predefined URL of the text document
  url = "https://energy.maryland.gov/Documents/082224_CandT.txt.txt"
  document_text = load_text_from_url(url)
  
  if document_text:
      st.write("Document loaded successfully.")
      
      # User input
      user_input = st.text_input("Ask something about the document:")
      
      if user_input:
          response = generate_response(user_input, document_text)
          st.write("Chatbot:", response)

if __name__ == "__main__":
  main()
