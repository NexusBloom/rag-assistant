import streamlit as st
import os
from pathlib import Path
import sys

st.set_page_config(page_title="RAG Assistant", layout="wide")
st.title("?? RAG Assistant")

# DEBUG: Show system info
st.subheader("Debug Info")
st.write(f"Python version: {sys.version}")
st.write(f"Current directory: {os.getcwd()}")
st.write(f"File location: {__file__}")

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.schema import Document
    
    API_KEY = os.getenv("OPENAI_API_KEY")
    st.write(f"API Key exists: {bool(API_KEY)}")
    
    if not API_KEY:
        st.error("? OPENAI_API_KEY not set!")
        st.stop()
    
    # Check data folder
    base_dir = Path(__file__).parent
    data_dir = base_dir / "data"
    
    st.write(f"Base dir: {base_dir}")
    st.write(f"Data dir: {data_dir}")
    st.write(f"Data dir exists: {data_dir.exists()}")
    
    if data_dir.exists():
        files = list(data_dir.iterdir())
        st.write(f"Files in data dir: {[str(f) for f in files]}")
        
        for f in files:
            if f.is_file():
                st.write(f"File: {f.name}, Size: {f.stat().st_size} bytes")
                try:
                    content = f.read_text(encoding='utf-8', errors='ignore')
                    st.success(f"? Read {f.name}: {len(content)} chars")
                except Exception as e:
                    st.error(f"? Error reading {f.name}: {e}")
    
    # Simple RAG
    class SimpleRAG:
        def __init__(self):
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=API_KEY,
                base_url="https://openrouter.ai/api/v1",
                model="text-embedding-ada-002"
            )
            self.vectorstore = None
            
        def load_builtin(self):
            texts = []
            if data_dir.exists():
                for f in data_dir.glob("*.txt"):
                    try:
                        texts.append(f.read_text(encoding='utf-8', errors='ignore'))
                    except:
                        pass
            if texts:
                docs = [Document(page_content=t) for t in texts]
                self.vectorstore = FAISS.from_documents(docs, self.embeddings)
                return True
            return False
        
        def query(self, q):
            if not self.vectorstore:
                return "No documents"
            docs = self.vectorstore.similarity_search(q, k=2)
            context = "\n".join([d.page_content[:500] for d in docs])
            
            llm = ChatOpenAI(
                model="google/gemini-flash-1.5",
                openai_api_key=API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )
            return llm.invoke(f"Context: {context}\n\nQuestion: {q}").content
    
    rag = SimpleRAG()
    if rag.load_builtin():
        st.success("? Knowledge loaded!")
        
        q = st.text_input("Ask about CS:")
        if q:
            st.write(rag.query(q))
    else:
        st.error("Failed to load knowledge")

except Exception as e:
    st.error(f"Error: {e}")
    import traceback
    st.code(traceback.format_exc())
