import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
from dotenv import load_dotenv

# Load environment variables if .env exists
load_dotenv()

# Configure page settings
st.set_page_config(
    page_title="Gemini PDF Chat",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a premium feel
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stChatMessage {
        background-color: #1e2329;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .stTextInput input {
        color: #ffffff;
    }
    /* Add a subtle gradient to the sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(#1e2329, #0e1117);
    }
    h1 {
        background: -webkit-linear-gradient(45deg, #4285F4, #9B72CB, #D96570);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
</style>
""", unsafe_allow_html=True)

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_gemini_response(input_text, pdf_content, prompt_chain):
    model = genai.GenerativeModel('gemini-pro')
    # Construct a prompt that includes context. 
    # For a simple chat, we can just prepend the context or use a robust prompt strategy.
    
    combined_prompt = f"""
    You are a helpful assistant capable of analyzing PDF documents.
    
    Context from the PDF Document:
    {pdf_content}
    
    Chat History:
    {prompt_chain}
    
    User Question: {input_text}
    
    Answer the user's question based strictly on the context provided above. If the answer is not in the context, say so.
    """
    
    response = model.generate_content(combined_prompt)
    return response.text

def main():
    st.title("Chat with PDF using Gemini 🤖")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # API Key input
        api_key = st.text_input("Enter your Google Gemini API Key:", type="password")
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
            
        if api_key:
            genai.configure(api_key=api_key)
            st.success("API Key configured!")
        else:
            st.warning("Please enter your API Key to proceed.")
            
        st.markdown("---")
        st.subheader("Your Documents")
        pdf_docs = st.file_uploader(
            "Upload your PDFs here and click on 'Process'", 
            accept_multiple_files=True,
            type=['pdf']
        )
        
        if st.button("Process"):
            if pdf_docs:
                with st.spinner("Processing PDF..."):
                    # Create data directory if it doesn't exist
                    data_dir = "data"
                    os.makedirs(data_dir, exist_ok=True)
                    
                    saved_files = []
                    for pdf in pdf_docs:
                        # Save the file to disk
                        file_path = os.path.join(data_dir, pdf.name)
                        with open(file_path, "wb") as f:
                            f.write(pdf.getbuffer())
                        saved_files.append(file_path)
                    
                    # Process the text
                    raw_text = get_pdf_text(pdf_docs)
                    st.session_state['pdf_text'] = raw_text
                    st.success(f"Processed and saved {len(saved_files)} PDF(s) to '{data_dir}' folder!")
            else:
                st.error("Please upload a PDF first.")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    if "pdf_text" not in st.session_state:
        st.session_state.pdf_text = ""

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # React to user input
    if prompt := st.chat_input("Ask a question about your PDF..."):
        # Check if API key and PDF text are present
        if not api_key:
            st.error("Please provide a Gemini API Key in the sidebar.")
            return
        if not st.session_state.pdf_text:
            st.error("Please upload and process a PDF document first.")
            return

        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Generate response
        try:
            # Create a simple history string for context (could be improved with robust history handling)
            history_str = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]]) # Last 5 messages
            
            with st.spinner("Gemini is thinking..."):
                response = get_gemini_response(prompt, st.session_state.pdf_text, history_str)
            
            # Display assistant response in chat message container
            with st.chat_message("assistant"):
                st.markdown(response)
                
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
