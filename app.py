import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Streamlit page configuration
st.set_page_config(page_title="MEA Website Chatbot with Gemini", page_icon="🤖")

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

def fetch_website_content(url, max_pages=10):
  """Fetch and parse website content from the main page and its child pages"""
  try:
      content = ""
      visited = set()
      to_visit = [url]
      
      while to_visit and len(visited) < max_pages:
          current_url = to_visit.pop(0)
          if current_url in visited:
              continue
          
          response = requests.get(current_url)
          soup = BeautifulSoup(response.content, 'html.parser')
          
          # Add the text content of the current page
          content += soup.get_text() + "\n\n"
          visited.add(current_url)
          
          # Find child links
          for link in soup.find_all('a', href=True):
              child_url = urljoin(url, link['href'])
              if child_url.startswith(url) and child_url not in visited:
                  to_visit.append(child_url)
      
      return content
  except Exception as e:
      st.error(f"Error fetching website content: {str(e)}")
      return ""

def generate_response(user_input):
  """Generate a response using the Gemini model"""
  try:
      # Prepare the conversation history for the model
      conversation = [
          {"role": "user", "parts": [f"You are a chatbot that answers questions about the following Maryland Energy Administration website content: {st.session_state.website_content[:1000]}..."]},
          {"role": "model", "parts": ["Understood. I'm ready to answer questions about the Maryland Energy Administration website content you provided."]}
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
st.title("Maryland Energy Administration Website Chatbot")

# Website URL input with pre-filled MEA homepage URL
mea_url = "https://energy.maryland.gov/Pages/default.aspx"
website_url = st.text_input("MEA Homepage URL:", value=mea_url)

if website_url:
  if website_url != st.session_state.get('last_url', ''):
      with st.spinner("Loading website content from MEA homepage and child pages..."):
          st.session_state.website_content = fetch_website_content(website_url)
      st.session_state.last_url = website_url
      st.session_state.messages = []  # Clear previous conversation
  
  st.success("Website content loaded from MEA homepage and child pages. You can now ask questions!")

  # Display chat history
  for message in st.session_state.messages:
      with st.chat_message("user" if st.session_state.messages.index(message) % 2 == 0 else "assistant"):
          st.write(message)

  # User input
  user_input = st.chat_input("Your question about the MEA website:")

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
  st.warning("Please enter the MEA website URL to start chatting about its content.")

# Add a note about the chatbot's capabilities
st.info("This chatbot can answer questions about the Maryland Energy Administration website, including information from the homepage and its child pages.")
