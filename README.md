
# MEA Website Chatbot with Gemini 🤖

This Streamlit application serves as a chatbot for the Maryland Energy Administration (MEA) website. The chatbot uses Google's Gemini (Bard) API to provide answers to user queries based on content extracted from the MEA homepage and its child pages.

## Features

- **Website Content Fetching:** Automatically fetches and parses content from the MEA homepage and its linked child pages.
- **Conversation History:** Maintains a session-based conversation history to ensure context-aware interactions.
- **Gemini Integration:** Leverages Google's Gemini (Bard) API for natural language understanding and response generation.
- **Interactive Chat Interface:** Provides a user-friendly chat interface where users can ask questions about the MEA website.

## Installation

To run this application, you need to have Python installed along with the required libraries.

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/mea-website-chatbot.git
   cd mea-website-chatbot
   ```

2. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Gemini API Key:**
   - Create a `.streamlit` directory in the root of your project.
   - Inside this directory, create a `secrets.toml` file with the following content:
     ```toml
     [default]
     GEMINI_API_KEY = "your_actual_gemini_api_key_here"
     ```

4. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

## How It Works

1. **Fetching Website Content:**
   - The application fetches the content from the MEA homepage and its child pages by following internal links, up to a specified depth.
   - The fetched content is stored in the session state for use in generating responses.

2. **Generating Responses:**
   - The chatbot uses Google's Gemini model to generate responses based on the user's input and the content fetched from the MEA website.
   - The conversation history is maintained in session state to provide context for ongoing interactions.

3. **Interactive Interface:**
   - Users can enter the URL of the MEA homepage (default is pre-filled).
   - The chatbot interacts with the user, answering questions based on the content from the specified MEA pages.

## Usage

1. **Start the application:**
   - Run the Streamlit app using the command mentioned above.

2. **Enter the MEA Website URL:**
   - The app is pre-filled with the MEA homepage URL. You can change it to another MEA page if needed.

3. **Ask Questions:**
   - After the content is loaded, type your questions into the chat input, and the chatbot will generate responses based on the MEA website's content.

## Limitations

- The chatbot can only provide information based on the content it has fetched from the MEA website.
- The chatbot may not fully understand or respond accurately to all queries, depending on the content and context available.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an issue for any feature requests or bug reports.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This README provides an overview of your application, installation instructions, usage details, and other relevant information for users and contributors. Make sure to adjust the URLs and any placeholders as necessary for your specific project setup.
