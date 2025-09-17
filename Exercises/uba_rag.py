import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, WikipediaLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from config import load_embeddings, load_google_llm
import os
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="University of Bamenda Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #2a5298;
        background-color: #f8f9fa;
    }
    
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #1976d2;
    }
    
    .assistant-message {
        background-color: #f3e5f5;
        border-left-color: #7b1fa2;
    }
    
    .info-box {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4caf50;
        margin-bottom: 1rem;
    }
    
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        width: 100%;
        background-color: #2a5298;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #1e3c72;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_system():
    """Initialize the document loading and vector database system"""
    try:
        with st.spinner("🔄 Loading documents and initializing system..."):
            embeddings = load_embeddings()
            
            # PDF
            pdf_loader = PyPDFLoader('./data/university_of_bamenda.pdf')
            pdf_docs = pdf_loader.load()
            
            # Web
            urls_data = ["https://uniba.cm/"]
            web_loader = WebBaseLoader(urls_data)
            web_docs = web_loader.load()
            
            # Wikipedia
            about_loader = WikipediaLoader(query="University of Bamenda About", load_max_docs=1)
            about_docs = about_loader.load()
            
            history_loader = WikipediaLoader(query="University of Bamenda History", load_max_docs=1)
            history_docs = history_loader.load()
            
            home_loader = WikipediaLoader(query="University of Bamenda", load_max_docs=1)
            home_docs = home_loader.load()
            
            all_docs = pdf_docs + web_docs + about_docs + history_docs + home_docs
            
            # Text splitting
            text_splitter = CharacterTextSplitter(
                separator="\n\n",
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                is_separator_regex=False
            )
            
            page_contents = [doc.page_content for doc in all_docs]
            chunks = text_splitter.create_documents(page_contents)
            
            # Vector database
            vector_db = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_uba")
            retriever = vector_db.as_retriever(search_kwargs={"k": 3})
            
            return retriever, len(all_docs), len(chunks)
    
    except Exception as e:
        st.error(f"❌ Error initializing system: {str(e)}")
        return None, 0, 0

def is_uba_question(question: str) -> bool:
    """Check if the question is related to University of Bamenda"""
    keywords = [
        "bamenda", "university of bamenda", "uba", "uniba",
        "prof.", "dr.", "campus", "faculty", "department",
        "admission", "courses", "tuition", "fees", "library",
        "research", "students", "staff", "programs",
        "scholarships", "events"
    ]
    q = question.lower()
    return any(keyword in q for keyword in keywords)

def answer_question(question: str, retriever):
    """Generate answer for the given question"""
    if not is_uba_question(question):
        return "⚠️ I only answer questions about the University of Bamenda.", "warning"
    
    try:
        docs = retriever.get_relevant_documents(question)
        
        if not docs:
            return "⚠️ I don't know from the available documents.", "warning"
        
        context = "\n\n".join([f"[Source {i+1}]\n{doc.page_content}" for i, doc in enumerate(docs)])
        prompt = f"""
You are an AI assistant for the University of Bamenda. Use the following context to answer the question. 
If the answer is not in the context, say "I don't know from the available documents."

Context: {context}

Question: {question}

Answer (with sources if possible):
"""
        llm = load_google_llm()
        response = llm.invoke(prompt)
        
        return str(response), "success"
    
    except Exception as e:
        return f"❌ Error processing question: {str(e)}", "error"

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 University of Bamenda Assistant</h1>
        <p>Your AI-powered guide to information about the University of Bamenda</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "system_initialized" not in st.session_state:
        st.session_state.system_initialized = False
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Information")
        
        # System initialization
        if not st.session_state.system_initialized:
            if st.button("🚀 Initialize System"):
                retriever, doc_count, chunk_count = initialize_system()
                if retriever:
                    st.session_state.retriever = retriever
                    st.session_state.doc_count = doc_count
                    st.session_state.chunk_count = chunk_count
                    st.session_state.system_initialized = True
                    st.success("✅ System initialized successfully!")
                    st.rerun()
        
        if st.session_state.system_initialized:
            st.markdown(f"""
            <div class="info-box">
                <strong>📊 System Status:</strong><br>
                ✅ Documents loaded: {st.session_state.doc_count}<br>
                ✅ Text chunks: {st.session_state.chunk_count}<br>
                ✅ Ready to answer questions
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Sample questions
        st.subheader("💡 Sample Questions")
        sample_questions = [
            "What is the University of Bamenda?",
            "Tell me about UBA's history",
            "What faculties are available?",
            "How can I apply for admission?",
            "What are the tuition fees?",
            "Tell me about the campus facilities"
        ]
        
        for question in sample_questions:
            if st.button(question, key=f"sample_{question}"):
                if st.session_state.system_initialized:
                    st.session_state.messages.append({"role": "user", "content": question})
                    st.rerun()
        
        st.markdown("---")
        
        # Clear chat
        if st.button("🗑️ Clear Chat"):
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        
        # About
        st.subheader("ℹ️ About")
        st.markdown("""
        This assistant helps you find information about the University of Bamenda using:
        - Official university documents
        - Website content
        - Wikipedia articles
        - AI-powered search and retrieval
        """)
    
    # Main content
    if not st.session_state.system_initialized:
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ System Not Initialized</strong><br>
            Please click "Initialize System" in the sidebar to load documents and start asking questions.
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Chat interface
    st.subheader("💬 Chat with the University Assistant")
    
    # Display chat messages
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>🧑‍🎓 You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                message_type = message.get("type", "success")
                icon = "🤖" if message_type == "success" else "⚠️" if message_type == "warning" else "❌"
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>{icon} Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    
    # Question input
    with st.form("question_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_question = st.text_input(
                "Ask your question:",
                placeholder="e.g., What programs does University of Bamenda offer?",
                label_visibility="collapsed"
            )
        with col2:
            submit_button = st.form_submit_button("Send 📤")
    
    # Process question
    if submit_button and user_question.strip():
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_question})
        
        # Generate response
        with st.spinner("🤔 Thinking..."):
            response, response_type = answer_question(user_question, st.session_state.retriever)
        
        # Add assistant message
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response, 
            "type": response_type
        })
        
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        <small>🎓 University of Bamenda Assistant • Powered by AI • Built with Streamlit</small>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()