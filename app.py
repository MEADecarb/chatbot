import streamlit as st
import google.generativeai as gpt

# Access the Gemini API key from the environment variable
gemini_api_key = st.secrets["GEMINI_API_KEY"]

# Initialize the Gemini client
gpt.configure(api_key=gemini_api_key)
gemini_client = gpt.models.TextGenerationModel()

# Conversation history
memory = []

def generate_response(user_input):
    """Logic to interact with Gemini API and handle conversation chain"""
    # Build prompt with conversation history
    prompt = " ".join([f"User: {item[0]}\nBot: {item[1]}" for item in memory]) + f"\nUser: {user_input}"
    
    # Generate a response from the Gemini client
    response = gemini_client.generate(prompt=prompt)
    
    # Ensure that the response object has the expected structure
    if response and hasattr(response, 'text'):
        response_text = response.text
    else:
        response_text = "Sorry, I couldn't understand that."
    
    # Append the user input and bot response to memory
    memory.append((user_input, response_text))
    
    return response_text

# Streamlit interface
st.title("Website Chatbot with Gemini")
st.write("Ask me anything about this website!")

# User input
user_input = st.text_input("Your question:", key="input")

# Generate response and display
if user_input:
    response = generate_response(user_input)
    st.write(response)
