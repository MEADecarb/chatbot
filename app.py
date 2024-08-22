import streamlit as st
import requests

# Function to load content from the provided URL
def load_content_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        content = response.text
        return content.splitlines()
    else:
        st.error(f"Failed to load content from {url}. Status code: {response.status_code}")
        return []

# Function to search for the user's query in the loaded content
def find_answer_in_content(query, content_list):
    for idx, content in enumerate(content_list):
        if query.lower() in content.lower():
            return f"Match found in section {idx+1}: {content[:300]}..."  # Return a snippet of the content
    return None

# Function to get a response, either from the content or Grok API
def get_response(user_input):
    # First try to find the answer in the loaded content
    response = find_answer_in_content(user_input, web_pages_content)
    if response:
        return response
    
    # Fallback to Grok API if no match is found
    return get_grok_response(user_input)

# Function to interact with the Grok API
def get_grok_response(user_input):
    grok_api_url = "https://api.grok.ai/your_endpoint"
    # Retrieve the API key from Streamlit secrets
    grok_api_key = st.secrets["grok"]["api_key"]
    headers = {"Authorization": f"Bearer {grok_api_key}"}
    data = {"message": user_input}
    response = requests.post(grok_api_url, json=data, headers=headers)
    return response.json().get('response')

# Load the content from the URL
url = 'https://energy.maryland.gov/Documents/MEA_22AUG_2024.txt'
web_pages_content = load_content_from_url(url)

# Streamlit app setup
st.title("MEA Document Chatbot")
st.write("Ask questions based on the content of the MEA document!")

user_input = st.text_input("You: ", "")
if st.button("Send"):
    if user_input:
        response = get_response(user_input)
        st.write(f"Chatbot: {response}")
    else:
        st.write("Please enter a message.")
