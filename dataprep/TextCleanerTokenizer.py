import re
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# Make sure you have the necessary NLTK data files
nltk.download('punkt')

def clean_text(text):
    # Remove extra whitespace and line breaks
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)

    # Convert to lowercase
    text = text.lower()

    # Remove any unwanted characters (e.g., punctuation)
    text = re.sub(r'[^\w\s]', '', text)

    return text

def tokenize_text(text, level='word'):
    if level == 'word':
        # Tokenize text into words
        tokens = word_tokenize(text)
    elif level == 'sentence':
        # Tokenize text into sentences
        tokens = sent_tokenize(text)
    else:
        raise ValueError("Tokenization level must be either 'word' or 'sentence'")
    
    return tokens

# Load the text file
file_path = 'your_text_file.txt'
with open(file_path, 'r') as file:
    text = file.read()

# Clean the text
cleaned_text = clean_text(text)

# Tokenize the text (choose 'word' or 'sentence' depending on your needs)
tokens = tokenize_text(cleaned_text, level='word')

# Display the tokens
print(tokens)

# Save the cleaned and tokenized text to a new file (optional)
output_file_path = 'cleaned_tokenized_text.txt'
with open(output_file_path, 'w') as output_file:
    for token in tokens:
        output_file.write(token + '\n')
