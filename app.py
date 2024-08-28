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
  st.session_state.website_content = {}

def fetch_website_content(url, max_pages=20):
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
          
          # Store the content with its URL
          content_dict[current_url] = {
              'title': soup.title.string if soup.title else 'No title',
              'content': soup.get_text()
          }
          
          visited.add(current_url)
          
          # Find child links
          for link in soup.find_all('a', href=True):
              child_url = urljoin(url, link['href'])
              if child_url.startswith(url) and child_url not in visited and child_url not in to_visit:
                  to_visit.append(child_url)
      
      return content_dict
  except Exception as e:
      st.error(f"Error fetching website content: {str(e)}")
      return {}

def generate_response(user_input, content_dict):
  try:
      # Prepare the conversation history for the model
      conversation = [
          {"role": "user", "parts": ["""You are a helpful assistant for the Maryland Energy Administration (MEA). Your primary source of information is the MEA website content provided to you. Please follow these guidelines:
1. Use the information from the MEA website content to answer questions directly and specifically.
2. When discussing programs or grants, always mention the specific program name and provide the source URL.
3. If there's a relevant program or grant for the user's question, explain its key points briefly.
4. If you're not sure about specific details, say so, but provide information on how the user can find out more (e.g., contact information or relevant web pages).
5. Be concise but informative, focusing on the most relevant information for the user's query.

Here's the content from the MEA website:"""]},
          {"role": "model", "parts": ["Understood. I'll provide specific, relevant information from the MEA website, including program names, URLs, and key points. I'll be concise and direct in my responses, focusing on the user's query and providing guidance on how to get more information if needed."]},
      ]
      
      # Add content from each page
      for url, page_data in content_dict.items():
          conversation.append({"role": "user", "parts": [f"Content from {url}:\nTitle: {page_data['title']}\n\n{page_data['content'][:2000]}..."]})
      
      conversation.append({"role": "user", "parts": [user_input]})
      
      # Generate a response from the Gemini model
      response = model.generate_content(conversation)
      
      if response.text:
          return response.text
      else:
          return "I'm sorry, but I couldn't find specific information to answer your question. Please visit the MEA website at https://energy.maryland.gov/ or contact MEA directly for the most up-to-date information on their programs and grants."
  except Exception as e:
      st.error(f"An error occurred: {str(e)}")
      return "I'm sorry, but an error occurred while processing your request. Please try again or contact MEA directly for assistance."

# Streamlit interface
st.title("Maryland Energy Administration Website Chatbot")

# Information about the chatbot
st.markdown("""
### How This Chatbot Works
- This chatbot provides information based on the content of the Maryland Energy Administration website.
- It can summarize information from multiple pages and make connections between different topics.
- The chatbot will provide source URLs when possible to allow you to read more on the MEA website.
- If the chatbot is unsure about specific details, it will say so but try to provide related information.
- The goal is to be informative and helpful while maintaining accuracy about MEA programs and initiatives.
""")

# Website URL input with pre-filled MEA homepage URL
mea_url = "https://energy.maryland.gov/Pages/default.aspx"
website_url = st.text_input("MEA Homepage URL:", value=mea_url)

if website_url:
  if website_url != st.session_state.get('last_url', ''):
      with st.spinner("Loading website content from MEA homepage and related pages..."):
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
st.info("This chatbot provides information about the Maryland Energy Administration based on their website content. It can discuss various programs, initiatives, and energy-related topics relevant to Maryland.")
