import os
import streamlit as st
import base64
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    UnstructuredURLLoader,
    CSVLoader,
    TextLoader,
    PyPDFLoader,
    UnstructuredFileLoader
)
from langchain_community.vectorstores import FAISS

# Page config
st.set_page_config(page_title="Research Tool", page_icon="📰", layout="centered")

# Load custom CSS
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css()
except:
    pass

os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'show_upload' not in st.session_state:
    st.session_state.show_upload = False

# Add logo and title in top left
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

logo_base64 = get_base64_image("dc_witness_logo.png")
if logo_base64:
    st.markdown(
        f'<img src="data:image/png;base64,{logo_base64}" class="top-left-logo">',
        unsafe_allow_html=True
    )
else:
    # Fallback: text logo if image not found
    st.markdown(
        '<div style="position: fixed; top: 15px; left: 20px; font-size: 1.2rem; '
        'font-weight: 700; color: #e0e0e0; z-index: 1000;">DC WITNESS</div>',
        unsafe_allow_html=True
    )

st.markdown('<div class="top-left-title">Research Tool</div>', unsafe_allow_html=True)

# Function to process documents
def process_documents(urls_input, uploaded_files):
    all_documents = []
    
    # Handle URLs
    if urls_input:
        urls = [url.strip() for url in urls_input.split("\n") if url.strip()]
        if urls:
            loader = UnstructuredURLLoader(urls=urls)
            all_documents.extend(loader.load())
    
    # Handle uploaded files
    if uploaded_files:
        for uploaded_file in uploaded_files:
            temp_path = f"temp_{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            try:
                if uploaded_file.name.endswith('.pdf'):
                    loader = PyPDFLoader(temp_path)
                elif uploaded_file.name.endswith('.csv'):
                    loader = CSVLoader(temp_path)
                elif uploaded_file.name.endswith('.txt'):
                    loader = TextLoader(temp_path)
                else:
                    loader = UnstructuredFileLoader(temp_path)
                
                all_documents.extend(loader.load())
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    
    # Process documents
    if all_documents:
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " "],
            chunk_size=1000,
            chunk_overlap=200
        )
        chunks = text_splitter.split_documents(all_documents)
        
        embeddings = OpenAIEmbeddings()
        vectorindex_openai = FAISS.from_documents(chunks, embeddings)
        vectorindex_openai.save_local("vectorindex_openai")
        return True
    return False

# Main chat interface
if os.path.exists("vectorindex_openai"):
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "sources" in message and message["sources"]:
                with st.expander("Sources", expanded=False):
                    for source in message["sources"]:
                        st.caption(source)
    
    # Upload section - centered pill shape without icon
    with st.expander("Add Documents"):
        urls_input = st.text_area("URLs (one per line):", height=80, key="urls")
        uploaded_files = st.file_uploader(
            "Upload files:",
            type=["pdf", "txt", "csv"],
            accept_multiple_files=True,
            key="files"
        )
        
        if st.button("Process Documents", use_container_width=True):
            with st.spinner("Processing..."):
                if process_documents(urls_input, uploaded_files):
                    st.success("✓ Processed!")
                    st.rerun()
                else:
                    st.warning("No documents")
    
    # Chat input (centered)
    prompt = st.chat_input("Ask me anything about your documents...")
    
    # Handle chat input
    if prompt:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                llm = OpenAI(temperature=0.7, max_tokens=200)
                embeddings = OpenAIEmbeddings()
                vectorstore = FAISS.load_local("vectorindex_openai", embeddings, allow_dangerous_deserialization=True)
                chain = RetrievalQAWithSourcesChain.from_llm(llm=llm, retriever=vectorstore.as_retriever())
                result = chain({"question": prompt}, return_only_outputs=True)
                
                answer = result["answer"]
                st.write(answer)
                
                # Handle sources
                sources_list = []
                sources = result.get("sources", "")
                if sources:
                    sources_list = [s.strip() for s in sources.replace('\n', ',').split(',') if s.strip()]
                    with st.expander("Sources", expanded=False):
                        for source in sources_list:
                            st.caption(source)
                
                # Save assistant message
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources_list
                })
else:
    # Spacer to center the welcome content
    st.markdown('<div style="height: calc(50vh - 350px); min-height: 50px;"></div>', unsafe_allow_html=True)
    
    st.info("Add documents to get started")
    st.markdown("""
    ### How to use:
    1. Click **📎 Add Documents** below
    2. Enter URLs or upload files (PDF, TXT, CSV)
    3. Click **Process Documents**
    4. Start asking questions
    """)
    
    # Upload section on welcome screen - centered pill shape without icon
    with st.expander("Add Documents", expanded=True):
        urls_input = st.text_area("URLs (one per line):", height=80, key="welcome_urls")
        uploaded_files = st.file_uploader(
            "Upload files:",
            type=["pdf", "txt", "csv"],
            accept_multiple_files=True,
            key="welcome_files"
        )
        
        if st.button("Process Documents", use_container_width=True, key="welcome_process"):
            with st.spinner("Processing..."):
                if process_documents(urls_input, uploaded_files):
                    st.success("✓ Processed!")
                    st.rerun()
                else:
                    st.warning("No documents")
