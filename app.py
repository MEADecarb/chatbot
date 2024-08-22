import streamlit as st
import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests
import xml.etree.ElementTree as ET

# Configure the Gemini API
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

# Initialize the model
model = genai.GenerativeModel('gemini-pro')

# Function to fetch and parse sitemap
def fetch_sitemap(url):
  response = requests.get(url)
  root = ET.fromstring(response.content)
  links = [elem.text for elem in root.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
  return links

# Function to scrape website content using Selenium
def scrape_website_with_selenium(url):
  chrome_options = Options()
  chrome_options.add_argument("--headless")
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--disable-dev-shm-usage")

  driver = webdriver.Chrome(options=chrome_options)
  
  try:
      driver.get(url)
      time.sleep(5)

      WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.TAG_NAME, "body"))
      )

      text_content = driver.find_element(By.TAG_NAME, "body").text
      return text_content

  finally:
      driver.quit()

# Streamlit app
st.title("Energy Maryland Sitemap Explorer")

# Fetch sitemap
sitemap_url = "https://www.xml-sitemaps.com/download/energy.maryland.gov-49798b7b7/sitemap.xml?view=1"
links = fetch_sitemap(sitemap_url)

# Display links and allow selection
selected_link = st.selectbox("Select a link to explore:", links)

if st.button("Explore Selected Link"):
  with st.spinner("Fetching content..."):
      content = scrape_website_with_selenium(selected_link)

  st.subheader("Page Content:")
  st.text_area("Raw Content", content, height=200)

  # Generate summary with Gemini
  with st.spinner("Generating summary..."):
      summary_prompt = f"Summarize the following content from {selected_link}:\n\n{content[:4000]}"  # Limit content to 4000 chars
      summary = model.generate_content(summary_prompt)

  st.subheader("Summary:")
  st.write(summary.text)

# Chat interface
st.subheader("Ask about the page:")
user_question = st.text_input("Your question:")

if user_question:
  with st.spinner("Generating response..."):
      chat_prompt = f"Based on the content from {selected_link}:\n\n{content[:4000]}\n\nUser question: {user_question}"
      response = model.generate_content(chat_prompt)

  st.subheader("Response:")
  st.write(response.text)
