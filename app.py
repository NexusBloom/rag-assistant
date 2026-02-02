import streamlit as st
import os
from pathlib import Path
import hashlib

# Page Configuration - Mobile friendly
st.set_page_config(
    page_title="NexusBloom CS Assistant",
    page_icon="N",
    layout="centered",  # Better for mobile
    initial_sidebar_state="collapsed"
)

# CSS - High contrast, mobile optimized
st.markdown("""
<style>
    /* Dark text on light backgrounds for visibility */
    body { color: #333333 !important; }
    
    .hero { 
        text-align: center; 
        padding: 1.5rem; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        color: white !important; 
        border-radius: 15px; 
        margin-bottom: 1rem; 
    }
    .hero h1 { color: white !important; font-size: 1.8rem; }
    .hero p { color: #f0f0f0 !important; }
    
    .stats { display: flex; justify-content: space-around; margin: 1rem 0; }
    .stat { text-align: center; }
    .stat-num { font-size: 1.5rem; font-weight: bold; color: white !important; }
    .stat div { color: #f0f0f0 !important; font-size: 0.8rem; }
    
    .features { 
        display: grid; 
        grid-template-columns: repeat(2, 1fr); 
        gap: 0.5rem; 
        margin: 1rem 0; 
    }
    .feature { 
        background: #f8f9fa; 
        padding: 0.8rem; 
        border-radius: 10px; 
        border: 1px solid #e0e0e0;
    }
    .feature h4 { color: #333333 !important; margin: 0 0 0.3rem 0; font-size: 0.9rem; }
    .feature p { color: #666666 !important; margin: 0; font-size: 0.75rem; line-height: 1.3; }
    
    .chat-box { 
        background: white; 
        padding: 1rem; 
        border-radius: 15px; 
        border: 2px solid #e0e0e0;
        margin-top: 1rem;
    }
    .status { color: #10b981 !important; font-size: 0.9rem; font-weight: bold; }
    
    /* CRITICAL: Dark text for responses */
    .response { 
        background: #f0f4ff !important; 
        padding: 1rem; 
        border-radius: 10px; 
        margin-top: 1rem; 
        border-left: 4px solid #667eea;
        color: #333333 !important;
    }
    .response p, .response div, .response span { 
        color: #333333 !important; 
        line-height: 1.6;
    }
    
    /* Streamlit chat message colors */
    .stChatMessage { 
        background: white !important; 
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        margin-bottom: 0.5rem;
    }
    .stChatMessage p { color: #333333 !important; }
    
    /* Input styling */
    .stTextInput > div > div > input {
        color: #333333 !important;
        background: white !important;
        border: 2px solid #667eea;
        border-radius: 10px;
    }
    
    /* Loading spinner */
    .stSpinner > div { color: #667eea !important; }
    
    /* Error messages */
    .stError { color: #dc3545 !important; }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .hero { padding: 1rem; }
        .hero h1 { font-size: 1.5rem; }
        .features { grid-template-columns: 1fr; }
        .stat-num { font-size: 1.2rem; }
    }
</style>
""", unsafe_allow_html=True)

# Wake up message for cold start
st.markdown("""
<div style="text-align: center; padding: 1rem; background: #fff3cd; border-radius: 10px; margin-bottom: 1rem; border: 1px solid #ffc107;">
    <p style="margin: 0; color: #856404; font-size: 0.9rem;">
        First load may take 30-60 seconds. Please wait...
    </p>
</div>
""", unsafe_allow_html=True)

# Hero
st.markdown("""
<div class="hero">
    <h1>NexusBloom CS Assistant</h1>
    <p>Enterprise AI Knowledge Base</p>
    <div class="stats">
        <div class="stat"><div class="stat-num">6</div><div>Domains</div></div>
        <div class="stat"><div class="stat-num">4K+</div><div>Bytes</div></div>
        <div class="stat"><div class="stat-num">Fast</div><div>Response</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Features
st.markdown("""
<div class="features">
    <div class="feature"><h4>DS</h4><p>Arrays, Trees, Graphs</p></div>
    <div class="feature"><h4>ALG</h4><p>Sorting, DP, Search</p></div>
    <div class="feature"><h4>OS</h4><p>Processes, Memory</p></div>
    <div class="feature"><h4>DB</h4><p>SQL, Normalization</p></div>
    <div class="feature"><h4>NET</h4><p>TCP/IP, OSI Model</p></div>
    <div class="feature"><h4>AI</h4><p>ML, Neural Nets</p></div>
</div>
""", unsafe_allow_html=True)

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.schema import Document
    
    API_KEY = os.getenv("OPENAI_API_KEY")
    if not API_KEY:
        st.error("API Key not configured")
        st.stop()
    
    @st.cache_resource(show_spinner=False)
    def get_vectorstore():
        cache_dir = Path("./vectorstore_cache")
        cache_dir.mkdir(exist_ok=True)
        
        hash_file = cache_dir / "data.hash"
        faiss_file = cache_dir / "index.faiss"
        data_file = Path("./data/default_ai_knowledge.txt")
        
        current_hash = hashlib.md5(data_file.read_bytes()).hexdigest()
        
        if hash_file.exists() and faiss_file.exists():
            cached_hash = hash_file.read_text().strip()
            if cached_hash == current_hash:
                embeddings = OpenAIEmbeddings(
                    openai_api_key=API_KEY,
                    base_url="https://openrouter.ai/api/v1",
                    model="text-embedding-ada-002"
                )
                return FAISS.load_local(str(cache_dir), embeddings, allow_dangerous_deserialization=True)
        
        with st.spinner("Building knowledge base (one-time)..."):
            embeddings = OpenAIEmbeddings(
                openai_api_key=API_KEY,
                base_url="https://openrouter.ai/api/v1",
                model="text-embedding-ada-002"
            )
            
            texts = []
            for f in Path("./data").glob("*.txt"):
                texts.append(f.read_text(encoding='utf-8', errors='ignore'))
            
            docs = [Document(page_content=t) for t in texts]
            vs = FAISS.from_documents(docs, embeddings)
            vs.save_local(str(cache_dir))
            hash_file.write_text(current_hash)
            return vs
    
    vectorstore = get_vectorstore()
    
    st.markdown('<div class="chat-box">', unsafe_allow_html=True)
    st.markdown('<p class="status">Online - Ready</p>', unsafe_allow_html=True)
    
    # Chat
    if "chat" not in st.session_state:
        st.session_state.chat = []
    
    for msg in st.session_state.chat:
        with st.chat_message(msg["role"]):
            st.markdown(f'<div style="color: #333333;">{msg["content"]}</div>', unsafe_allow_html=True)
    
    if q := st.chat_input("Ask about CS..."):
        st.session_state.chat.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(f'<div style="color: #333333;"><b>You:</b> {q}</div>', unsafe_allow_html=True)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                docs = vectorstore.similarity_search(q, k=2)
                ctx = "\n".join([d.page_content[:500] for d in docs])
                
                llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    openai_api_key=API_KEY,
                    base_url="https://openrouter.ai/api/v1",
                    temperature=0.7,
                    max_tokens=500
                )
                
                resp = llm.invoke(f"Context: {ctx}\n\nQ: {q}\nA:")
                answer = resp.content
                
                # CRITICAL: Wrap in dark text div
                st.markdown(f'<div class="response" style="color: #333333 !important;"><b>Answer:</b><br>{answer}</div>', unsafe_allow_html=True)
                st.session_state.chat.append({"role": "assistant", "content": answer})
    
    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Tip: If this is first load, please wait 30-60 seconds and refresh.")