import warnings
warnings.filterwarnings("ignore")
import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import os
from dotenv import load_dotenv
from blog_agents import run_blog_pipeline

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
    /* Main Background */
    .stApp {
        background-color: #ffffff;
        color: #1a1a1a;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1a1a1a;
        font-weight: 700;
    }
    
    /* Chat Messages */
    .stChatMessage {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 12px;
        color: #1a1a1a;
    }
    
    /* User Message Specific (Optional - if we want distinction) */
    div[data-testid="stChatMessage"]:nth-of-type(odd) {
       background-color: #e8f0fe;
       border-color: #d2e3fc;
    }

    /* Inputs */
    .stTextInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        color: #1a1a1a !important;
        border: 1px solid #ced4da !important;
        border-radius: 8px !important;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #4285F4 !important;
        box-shadow: 0 0 0 1px #4285F4 !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #4285F4;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: #3367d6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        background-color: #f8f9fa;
        border: 1px dashed #ced4da;
        border-radius: 10px;
        padding: 20px;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #4285F4;
        background-color: #e8f0fe;
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
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
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
        
        if st.button("Process Docs"):
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
                    st.success(f"Processed and saved {len(saved_files)} PDF(s) successfully!")
            else:
                st.error("Please upload a PDF first.")

        st.markdown("---")
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    if "pdf_text" not in st.session_state:
        st.session_state.pdf_text = ""

    # Create tabs for different functionalities
    tab1, tab2 = st.tabs(["💬 Chat with PDF", "📝 Generate Blog Post"])

    with tab1:
        # Welcome Message if history is empty
        if not st.session_state.messages:
            st.markdown("""
            <div style='text-align: center; padding: 50px;'>
                <h3>👋 Welcome to Gemini PDF Chat!</h3>
                <p>Get started by following these steps:</p>
                <ol style='display: inline-block; text-align: left;'>
                    <li>Enter your <b>Gemini API Key</b> in the sidebar.</li>
                    <li>Upload your <b>PDF documents</b>.</li>
                    <li>Click <b>Process Docs</b> to analyze them.</li>
                    <li>Start asking questions below!</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)

        # Display chat messages from history on app rerun
        for message in st.session_state.messages:
            avatar = "👤" if message["role"] == "user" else "🤖"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # React to user input
        if prompt := st.chat_input("Ask a question about your PDF..."):
            # Check if API key and PDF text are present
            if not api_key:
                st.info("Please provide a Gemini API Key in the sidebar to start chatting.")
            elif not st.session_state.pdf_text:
                st.info("Please upload and process a PDF document first so I can answer your questions.")
            else:
                # Display user message in chat message container
                st.chat_message("user", avatar="👤").markdown(prompt)
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})

                # Generate response
                try:
                    # Create a simple history string for context
                    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-5:]]) # Last 5 messages
                    
                    with st.spinner("Gemini is thinking..."):
                        response = get_gemini_response(prompt, st.session_state.pdf_text, history_str)
                    
                    # Display assistant response in chat message container
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(response)
                        
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    with tab2:
        st.header("Agentic Blog Generator")
        st.markdown("Use our multi-agent system to turn your PDF into a blog post.")
        
        if not st.session_state.pdf_text:
            st.warning("Please upload and process a PDF document in the sidebar first.")
        else:
            if st.button("🚀 Create Blog Post"):
                if not api_key:
                     st.error("Please configure your API Key in the sidebar.")
                else:
                    with st.status("🚀 Running Agentic Pipeline...", expanded=True) as status:
                        st.write("Initializing Agents...")
                        
                        # Execute the pipeline
                        st.write("Agent 1: Researching and creating brief...")
                        results = run_blog_pipeline(st.session_state.pdf_text)
                        
                        if "error" in results:
                            status.update(label="Pipeline Failed", state="error")
                            st.error(results["error"])
                        else:
                            st.write("Agent 1 Complete. Handoff to Agent 2...")
                            st.write("Agent 2: Writing blog post...")
                            
                            status.update(label="Pipeline Completed Successfully!", state="complete")
                            
                            # Display Results
                            st.divider()
                            st.subheader("📝 Final Blog Post")
                            st.markdown(results["blog_post"])
                            
                            with st.expander("ℹ️ View Research Brief (Backend Artifact)"):
                                st.info("This is the intermediate brief created by Agent 1 and passed to Agent 2.")
                                st.markdown(results["brief"])

if __name__ == "__main__":
    main()
