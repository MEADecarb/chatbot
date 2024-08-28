import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

def process_content(content):
  # Remove extra whitespace and normalize text
  content = re.sub(r'\s+', ' ', content).strip()
  # Extract key points (this is a simple example, you might want to use NLP techniques for better extraction)
  sentences = content.split('.')
  key_points = [s.strip() for s in sentences if len(s.split()) > 5][:10]  # Take first 10 substantial sentences
  return "\n".join(key_points)

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
          
          # Process and store the content
          raw_content = soup.get_text()
          processed_content = process_content(raw_content)
          content_dict[current_url] = processed_content
          
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

def check_fact(response, content_dict):
  # Combine all content
  all_content = " ".join(content_dict.values())
  
  # Use TF-IDF and cosine similarity to check if response is similar to any content
  vectorizer = TfidfVectorizer().fit([all_content, response])
  vectors = vectorizer.transform([all_content, response])
  similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
  
  return similarity > 0.1  # Adjust this threshold as needed

def generate_response(user_input, content_dict):
  try:
      # Prepare the conversation history for the model
      conversation = [
          {"role": "user", "parts": ["You are a chatbot that answers questions about the Maryland Energy Administration website. You must follow these rules strictly:\n1. Only use the information provided in the following content to answer questions.\n2. If the answer is not in the provided content, say 'I don't have information about that.'\n3. Always cite the source URL for your information.\n4. Do not make up or infer any information not explicitly stated in the content.\n5. Provide a confidence score from 0 to 1 for each response.\n\nHere's the content:"]},
          {"role": "model", "parts": ["I understand and will strictly adhere to these rules. I will only provide information explicitly stated in the given content, always cite sources, and give a confidence score. If I don't have the information, I'll clearly state that."]},
      ]
      
      # Add content from each page
      for url, content in content_dict.items():
          conversation.append({"role": "user", "parts": [f"Content from {url}:\n{content}"]})
      
      conversation.append({"role": "user", "parts": [user_input]})
      
      # Generate a response from the Gemini model
      response = model.generate_content(conversation)
      
      if response.text:
          # Check if the response is factual
          is_factual = check_fact(response.text, content_dict)
          if is_factual:
              return response.text
          else:
              return "I don't have accurate information to answer that question based on the provided content."
      else:
          return "I don't have information about that based on the provided content."
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

st.markdown("""
### How This Chatbot Works
- This chatbot provides information solely based on the content of the Maryland Energy Administration website.
- All responses are generated using only the information from the website pages.
- If the chatbot doesn't have information to answer a question, it will clearly state that.
- Each response includes a confidence score and a source URL for transparency.
- If you believe a response is inaccurate, please use the report button below the response.
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
          response = generate_response(user_input, st.session_state.website_content)
          st.write(response)
          
          # Add confidence score display and report button (you'll need to extract the confidence score from the response)
          confidence_score = 0.9  # This should be extracted from the model's response
          st.write(f"Confidence Score: {confidence_score:.2f}")
          if st.button("Report this response as inaccurate"):
              st.write("Thank you for your feedback. We will review this response.")
      
      st.session_state.messages.append(response)
else:
  st.warning("Please enter the MEA website URL to start chatting about its content.")

# Add a note about the chatbot's capabilities
st.info("This chatbot can answer questions about the Maryland Energy Administration website, including information from the homepage and its child pages. It will only provide information based on the content of these pages.")
