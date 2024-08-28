import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

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
          content += f"Content from {current_url}:\n"
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
          {"role": "user", "parts": [f"You are a chatbot that answers questions about the Maryland Energy Administration website. Here's the content you should base your answers on: {st.session_state.website_content[:1000]}..."]},
          {"role": "model", "parts": ["Understood. I will only provide information based on the Maryland Energy Administration website content you provided. If a question is outside this scope, I will state that I don't have that information."]},
          {"role": "user", "parts": ["Always stick to the facts provided in the website content. If you're not sure about something, say you don't know or don't have that information. Never make up information."]},
          {"role": "model", "parts": ["I understand. I will only provide information that is explicitly stated in the website content. If I'm unsure or if the information isn't available, I'll clearly state that I don't have that information."]}
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
          return "I apologize, but I couldn't generate a response based on the available information."
  except Exception as e:
      st.error(f"An error occurred: {str(e)}")
      return "I'm sorry, but an error occurred while processing your request."

# Streamlit interface
st.title("Maryland Energy Administration Website Chatbot")

# Information about session history clearing
st.markdown("""
### Important Information
This application is designed with your privacy and data security in mind. Here's how it works:

1. **Session State Reset:** At the start of each session, the application resets its internal session state. This means that any data from previous sessions is cleared, ensuring that no information carries over from one use to the next.

2. **Temporary Data Storage:** When you use this chatbot, the website content and your conversation history are only stored temporarily within the current session. As soon as you close the app or start a new session, this data is automatically deleted.

3. **No Permanent Storage:** The app does not store any of the fetched website content or your conversations permanently. Once you end your session, all data is removed from the app's memory.

4. **Security:** This process helps ensure that your interaction remains private and is not accessible after you finish using the app.

In summary, every time you use the app, it starts with a clean slate, clearing all previous session data to protect your privacy and maintain data security.
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
st.info("This chatbot can answer questions about the Maryland Energy Administration website, including information from the homepage and its child pages. It will only provide information based on the content of these pages.")
