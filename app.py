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

# Function to get a response, either from the content or Gemini API
def get_response(user_input):
    # First try to find the answer in the loaded content
    response = find_answer_in_content(user_input, web_pages_content)
    if response:
        return response
    
    # Fallback to Gemini API if no match is found
    return get_gemini_response(user_input)

# Function to interact with the Gemini API
def get_gemini_response(user_input):
    gemini_api_url = "https://api.gemini.com/your_endpoint"  # Replace with the actual Gemini API endpoint
    gemini_api_key = st.secrets["gemini"]["api_key"]  # Ensure you've added this to Streamlit secrets
    headers = {
        "Authorization": f"Bearer {gemini_api_key}",
        "Content-Type": "application/json"  # Adjust if Gemini API requires different headers
    }
    data = {"query": user_input}  # Adjust the payload format based on Gemini API requirements
    
    # Make the request to the Gemini API
    response = requests.post(gemini_api_url, json=data, headers=headers, verify=True)  # Use SSL verification
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
