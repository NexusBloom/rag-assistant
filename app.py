import streamlit as st
import os
from pathlib import Path
import hashlib

# Page Configuration
st.set_page_config(
    page_title="NexusBloom CS Assistant",
    page_icon="N",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Minimal CSS
st.markdown("""
<style>
.hero { text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px; margin-bottom: 2rem; }
.stats { display: flex; justify-content: space-around; margin: 2rem 0; }
.stat { text-align: center; }
.stat-num { font-size: 2rem; font-weight: bold; }
.features { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 2rem 0; }
.feature { background: white; padding: 1rem; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
.chat-box { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }
.status { color: #10b981; font-size: 0.9rem; }
.response { background: #f0f4ff; padding: 1rem; border-radius: 10px; margin-top: 1rem; border-left: 4px solid #667eea; }
</style>
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
    <div class="feature"><h4>ALG</h4><p>Sorting, DP, Searching</p></div>
    <div class="feature"><h4>OS</h4><p>Processes, Memory</p></div>
    <div class="feature"><h4>DB</h4><p>SQL, Normalization</p></div>
    <div class="feature"><h4>NET</h4><p>TCP/IP, OSI Model</p></div>
    <div class="feature"><h4>AI</h4><p>ML, Neural Networks</p></div>
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
    
    # Use FAISS native save/load instead of pickle
    @st.cache_resource(show_spinner=False)
    def get_vectorstore():
        cache_dir = Path("./vectorstore_cache")
        cache_dir.mkdir(exist_ok=True)
        
        hash_file = cache_dir / "data.hash"
        faiss_file = cache_dir / "index.faiss"
        data_file = Path("./data/default_ai_knowledge.txt")
        
        # Calculate current hash
        current_hash = hashlib.md5(data_file.read_bytes()).hexdigest()
        
        # Check if cache exists and matches
        if hash_file.exists() and faiss_file.exists():
            cached_hash = hash_file.read_text().strip()
            if cached_hash == current_hash:
                st.success("Loaded from cache!")
                embeddings = OpenAIEmbeddings(
                    openai_api_key=API_KEY,
                    base_url="https://openrouter.ai/api/v1",
                    model="text-embedding-ada-002"
                )
                return FAISS.load_local(str(cache_dir), embeddings, allow_dangerous_deserialization=True)
        
        # Build new vectorstore
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
            
            # Save using FAISS native method
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
            st.markdown(msg["content"])
    
    if q := st.chat_input("Ask about CS..."):
        st.session_state.chat.append({"role": "user", "content": q})
        with st.chat_message("user"):
            st.markdown(q)
        
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
                
                st.markdown(f'<div class="response">{answer}</div>', unsafe_allow_html=True)
                st.session_state.chat.append({"role": "assistant", "content": answer})
    
    st.markdown('</div>', unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error: {e}")
    import traceback
    st.code(traceback.format_exc())