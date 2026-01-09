# PDF Chat with Gemini

This is a Streamlit application that allows you to upload PDF documents and chat with them using Google's Gemini Pro model.

## Features
- Upload multiple PDF files
- Extract text from PDFs automatically
- Chat interface to ask questions about the PDF content
- Powered by Google Gemini Pro

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python3 -m streamlit run app.py
   ```

3. **API Key**
   - You need a Google Gemini API Key.
   - You can enter it in the sidebar of the application.
   - Alternatively, create a `.env` file in this directory with the content:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```

## Usage
1. Open the app in your browser (usually http://localhost:8501).
2. Enter your API Key in the sidebar if not set in `.env`.
3. Upload your PDF file(s) in the sidebar.
4. Click "Process" to extract the text.
5. Ask questions in the chat input at the bottom!
