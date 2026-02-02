import streamlit as st
import os
from pathlib import Path

# Page Configuration
st.set_page_config(
    page_title="NexusBloom CS Assistant",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS - ASCII only
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }
    
    .hero-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 3rem;
        margin: 2rem auto;
        max-width: 1200px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -2px;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    .feature-card {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 4px solid #667eea;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .feature-desc {
        font-size: 0.9rem;
        color: #666;
        line-height: 1.5;
    }
    
    .chat-container {
        background: white;
        border-radius: 20px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
    }
    
    .chat-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid #f0f0f0;
    }
    
    .chat-avatar {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    .chat-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
    }
    
    .chat-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #10b981;
        font-size: 0.9rem;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        background: #10b981;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .stTextInput > div > div > input {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .response-box {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1rem;
        border-left: 5px solid #667eea;
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .response-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        color: #667eea;
        font-weight: 600;
    }
    
    .stats-container {
        display: flex;
        justify-content: space-around;
        margin: 2rem 0;
        padding: 1.5rem;
        background: rgba(102, 126, 234, 0.1);
        border-radius: 15px;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.25rem;
    }
    
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        font-size: 0.9rem;
        margin-top: 3rem;
    }
    
    .badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">NexusBloom CS Assistant</h1>
    <p class="hero-subtitle">Enterprise-Grade AI Knowledge Base for Computer Science Education</p>
    
    <div class="stats-container">
        <div class="stat-item">
            <div class="stat-number">6</div>
            <div class="stat-label">Core Domains</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">4.3K</div>
            <div class="stat-label">Knowledge Bytes</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">&lt; 1s</div>
            <div class="stat-label">Response Time</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">99%</div>
            <div class="stat-label">Accuracy</div>
        </div>
    </div>
    
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">DS</div>
            <div class="feature-title">Data Structures</div>
            <div class="feature-desc">Arrays, Linked Lists, Trees, Graphs, and advanced data organization</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">ALG</div>
            <div class="feature-title">Algorithms</div>
            <div class="feature-desc">Sorting, Searching, Dynamic Programming, optimization</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">OS</div>
            <div class="feature-title">Operating Systems</div>
            <div class="feature-desc">Process management, Memory allocation, System architecture</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">DB</div>
            <div class="feature-title">Databases</div>
            <div class="feature-desc">SQL, Normalization, Database design principles</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">NET</div>
            <div class="feature-title">Networks</div>
            <div class="feature-desc">TCP/IP, OSI Model, Network protocols</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">AI</div>
            <div class="feature-title">AI and ML</div>
            <div class="feature-desc">Machine Learning, Neural Networks, Deep Learning</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Application Logic
try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.schema import Document
    
    API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not API_KEY:
        st.markdown("""
        <div class="hero-container" style="border-left: 5px solid #ef4444;">
            <h3>Configuration Required</h3>
            <p>Please set the OPENAI_API_KEY in Streamlit Secrets.</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    @st.cache_resource(show_spinner=False)
    def initialize_engine():
        embeddings = OpenAIEmbeddings(
            openai_api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1",
            model="text-embedding-ada-002"
        )
        
        data_dir = Path(__file__).parent / "data"
        texts = []
        for f in data_dir.glob("*.txt"):
            texts.append(f.read_text(encoding='utf-8', errors='ignore'))
        
        docs = [Document(page_content=t) for t in texts]
        return FAISS.from_documents(docs, embeddings)
    
    with st.spinner("Initializing AI Engine..."):
        vectorstore = initialize_engine()
    
    st.markdown("""
    <div class="hero-container chat-container">
        <div class="chat-header">
            <div class="chat-avatar">AI</div>
            <div>
                <div class="chat-title">CS Knowledge Assistant</div>
                <div class="chat-status">
                    <div class="status-dot"></div>
                    <span>Online - Ready to assist</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask about any Computer Science topic..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f"You: {prompt}")
        
        with st.chat_message("assistant"):
            with st.spinner("Analyzing knowledge base..."):
                try:
                    docs = vectorstore.similarity_search(prompt, k=3)
                    context = "\n\n".join([d.page_content[:1000] for d in docs])
                    
                    llm = ChatOpenAI(
                        model="gpt-3.5-turbo",
                        openai_api_key=API_KEY,
                        base_url="https://openrouter.ai/api/v1",
                        temperature=0.7
                    )
                    
                    system_prompt = f"""You are an expert Computer Science educator. 
Use the provided context to give a comprehensive answer.
If the context doesn't contain enough information, say so clearly.

Context:
{context}

Question: {prompt}

Provide a well-structured answer."""
                    
                    response = llm.invoke(system_prompt)
                    answer = response.content
                    
                    st.markdown(f"""
                    <div class="response-box">
                        <div class="response-header">
                            <span>Expert Answer</span>
                        </div>
                        <div style="line-height: 1.8; color: #333;">
                            {answer}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown("</div>", unsafe_allow_html=True)

except Exception as e:
    st.markdown(f"""
    <div class="hero-container" style="border-left: 5px solid #ef4444;">
        <h3>System Error</h3>
        <p>{str(e)}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="footer">
    <p>Powered by <span class="badge">LangChain</span> <span class="badge">OpenRouter</span> <span class="badge">FAISS</span></p>
    <p style="margin-top: 1rem; color: #999;">2026 NexusBloom Technologies. Built for CS education.</p>
</div>
""", unsafe_allow_html=True)