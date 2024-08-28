import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

# Streamlit page configuration
st.set_page_config(page_title="MEA Website Chatbot with Gemini", page_icon="🤖", layout="wide")

# Access the Gemini API key from Streamlit secrets
gemini_api_key = st.secrets["GEMINI_API_KEY"]

# Initialize the Gemini client
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-pro')

# Initialize session state for conversation history and website content
if "messages" not in st.session_state:
  st.session_state.messages = []
if "website_content" not in st.session_state:
  st.session_state.website_content = {}

def fetch_website_content(url, max_pages=10):
  try:
      content_dict = {}
      visited = set()
      to_visit = [url]
      
      while to_visit and len(visited) < max_pages:
          current_url = to_visit.pop(0)
          if current_url in visited:
              continue
          
          response = requests.get(current_url)
          soup = BeautifulSoup(response.content, 'html.parser')
          
          # Store the content
          content_dict[current_url] = soup.get_text()
          
          visited.add(current_url)
          
          # Find child links
          for link in soup.find_all('a', href=True):
              child_url = urljoin(url, link['href'])
              if child_url.startswith(url) and child_url not in visited:
                  to_visit.append(child_url)
      
      return content_dict
  except Exception as e:
      st.error(f"Error fetching website content: {str(e)}")
      return {}

def generate_response(user_input, content_dict):
  try:
      # Prepare the conversation history for the model
      conversation = [
          {"role": "user", "parts": ["You are a helpful assistant that provides information about the Maryland Energy Administration (MEA). Your primary source of information is the MEA website, but you can also use your general knowledge to provide context or explanations. Please follow these guidelines:\n1. Prioritize information from the MEA website content provided.\n2. You can use your general knowledge to explain concepts or provide context, but clearly distinguish between website information and general knowledge.\n3. If you're not sure about something specific to MEA, say so.\n4. You can make reasonable inferences based on the provided information, but clearly state when you're doing so.\n5. Be helpful and informative, while maintaining accuracy.\n\nHere's the content from the MEA website:"]},
          {"role": "model", "parts": ["I understand. I'll prioritize information from the MEA website, use my general knowledge when appropriate, and be clear about the sources of my information. I'll aim to be helpful and informative while maintaining accuracy."]},
      ]
      
      # Add content from each page
      for url, content in content_dict.items():
          conversation.append({"role": "user", "parts": [f"Content from {url}:\n{content[:1000]}..."]})  # Limit content to first 1000 characters per page
      
      conversation.append({"role": "user", "parts": [user_input]})
      
      # Generate a response from the Gemini model
      response = model.generate_content(conversation)
      
      if response.text:
          return response.text
      else:
          return "I'm sorry, but I couldn't generate a response to your question."
  except Exception as e:
      st.error(f"An error occurred: {str(e)}")
      return "I'm sorry, but an error occurred while processing your request."

# Streamlit interface
st.title("Maryland Energy Administration Website Chatbot")

# Information about the chatbot
st.markdown("""
### How This Chatbot Works
- This chatbot provides information primarily based on the content of the Maryland Energy Administration website.
- It can also use general knowledge to provide context or explanations when appropriate.
- The chatbot will prioritize information from the MEA website but may make reasonable inferences or provide additional context.
- If the chatbot is unsure about MEA-specific information, it will clearly state that.
- The goal is to be informative and helpful while maintaining a high degree of accuracy.
""")

# Website URL input with pre-filled MEA homepage URL
mea_url = "https://energy.maryland.gov/Pages/default.aspx"
website_url = st.text_input("MEA Homepage URL:", value=mea_url)

if website_url:
  if website_url != st.session_state.get('last_url', ''):
      with st.spinner("Loading website content from MEA homepage and child pages..."):
          st.session_state.website_content = fetch_website_content(website_url)
      st.session_state.last_url = website_url
      st.session_state.messages = []  # Clear previous conversation
  
  st.success("Website content loaded. You can now ask questions about the Maryland Energy Administration!")

  # Display chat history
  for message in st.session_state.messages:
      with st.chat_message("user" if st.session_state.messages.index(message) % 2 == 0 else "assistant"):
          st.write(message)

  # User input
  user_input = st.chat_input("Your question about the MEA:")

  # Generate response and display
  if user_input:
      st.session_state.messages.append(user_input)
      with st.chat_message("user"):
          st.write(user_input)
      
      with st.chat_message("assistant"):
          response = generate_response(user_input, st.session_state.website_content)
          st.write(response)
          
          if st.button("Was this response helpful?"):
              st.write("Thank you for your feedback!")
      
      st.session_state.messages.append(response)
else:
  st.warning("Please enter the MEA website URL to start chatting about its content.")

# Add a note about the chatbot's capabilities
st.info("This chatbot provides information about the Maryland Energy Administration, primarily based on their website content. It can also offer general context and explanations when relevant.")
