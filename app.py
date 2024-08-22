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
from concurrent.futures import ThreadPoolExecutor, as_completed

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

# Function to scrape all links
@st.cache_data
def scrape_all_links(links):
  all_content = []
  with ThreadPoolExecutor(max_workers=5) as executor:
      future_to_url = {executor.submit(scrape_website_with_selenium, url): url for url in links[:10]}  # Limit to first 10 links for demo
      for future in as_completed(future_to_url):
          url = future_to_url[future]
          try:
              content = future.result()
              all_content.append(f"Content from {url}:\n{content}\n\n")
          except Exception as exc:
              print(f'{url} generated an exception: {exc}')
  return "\n".join(all_content)

# Streamlit app
st.title("Energy Maryland Website Chatbot")

# Fetch sitemap and scrape content (only if not already in session state)
if 'all_content' not in st.session_state:
  sitemap_url = "https://www.xml-sitemaps.com/download/energy.maryland.gov-49798b7b7/sitemap.xml?view=1"
  with st.spinner("Fetching website content... This may take a few minutes."):
      links = fetch_sitemap(sitemap_url)
      st.session_state.all_content = scrape_all_links(links)

# Chat interface
st.subheader("Ask a question about Energy Maryland:")
user_question = st.text_input("Your question:")

if user_question:
  with st.spinner("Generating response..."):
      chat_prompt = f"Based on the following content from the Energy Maryland website:\n\n{st.session_state.all_content[:50000]}\n\nUser question: {user_question}"
      response = model.generate_content(chat_prompt)

  st.subheader("Response:")
  st.write(response.text)
