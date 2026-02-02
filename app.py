"""Simplified RAG App for Render - Synchronous Version"""
import streamlit as st
import uuid
import os
import requests
from urllib.parse import urlparse
from pathlib import Path

# Set API key directly
os.environ["OPENROUTER_API_KEY"] = "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"

from src.core.vectorstore import VectorStoreManager
from src.ingestion.loader import DocumentIngester
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Page config
st.set_page_config(page_title="RAG Assistant", page_icon=":books:", layout="wide")

# Initialize session
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("Production RAG Assistant")
st.caption(f"Session: {st.session_state.session_id}")

# Initialize LLM
@st.cache_resource
def get_llm():
    return ChatOpenAI(
        model="google/gemini-flash-1.5",
        temperature=0.0,
        openai_api_key=os.environ["OPENROUTER_API_KEY"],
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://rag-assistant.onrender.com",
            "X-Title": "RAG Assistant"
        }
    )

# Load default AI knowledge
def load_default():
    try:
        vs = VectorStoreManager()
        if vs.load_index() is None:
            default_text = """Artificial Intelligence (AI) is the simulation of human intelligence in machines.
Machine Learning is a subset of AI that uses data and algorithms to improve performance.
Deep Learning uses neural networks with many layers.
Natural Language Processing allows computers to understand human language.
Computer Vision enables machines to interpret visual data."""
            
            os.makedirs("data", exist_ok=True)
            with open("data/default.txt", "w") as f:
                f.write(default_text)
            
            ingester = DocumentIngester()
            docs = ingester.process_documents(["data/default.txt"])
            vs.create_index(docs)
            return True
    except Exception as e:
        st.error(f"Error loading default: {e}")
    return False

# Load on startup
if "loaded" not in st.session_state:
    if load_default():
        st.session_state.loaded = True
        st.success("AI knowledge base loaded!")

# Sidebar
with st.sidebar:
    st.header("Add Documents")
    
    uploaded_files = st.file_uploader("Upload files", type=["pdf", "txt"], accept_multiple_files=True)
    if uploaded_files and st.button("Process Files"):
        with st.spinner("Processing..."):
            try:
                paths = []
                for file in uploaded_files:
                    path = f"./data/{file.name}"
                    with open(path, "wb") as f:
                        f.write(file.getvalue())
                    paths.append(path)
                
                ingester = DocumentIngester()
                docs = ingester.process_documents(paths)
                vs = VectorStoreManager()
                if vs.load_index():
                    vs.add_documents(docs)
                else:
                    vs.create_index(docs)
                st.success(f"Added {len(docs)} chunks!")
            except Exception as e:
                st.error(f"Error: {e}")
    
    url = st.text_input("Or enter URL")
    if url and st.button("Load URL"):
        with st.spinner("Downloading..."):
            try:
                resp = requests.get(url, timeout=30)
                path = "./data/url_doc.txt"
                with open(path, "wb") as f:
                    f.write(resp.content)
                ingester = DocumentIngester()
                docs = ingester.process_documents([path])
                vs = VectorStoreManager()
                if vs.load_index():
                    vs.add_documents(docs)
                else:
                    vs.create_index(docs)
                st.success("Added from URL!")
            except Exception as e:
                st.error(f"Error: {e}")

# Chat interface
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about AI or your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                vs = VectorStoreManager()
                if not vs.load_index():
                    st.error("No documents loaded!")
                else:
                    retriever = vs.get_retriever()
                    docs = retriever.get_relevant_documents(prompt)
                    context = "\n\n".join([d.page_content for d in docs])
                    
                    llm = get_llm()
                    template = """Answer based on context:
{context}

Question: {question}
Answer:"""
                    prompt_template = ChatPromptTemplate.from_template(template)
                    chain = prompt_template | llm
                    
                    response = chain.invoke({
                        "context": context,
                        "question": prompt
                    })
                    
                    answer = response.content if hasattr(response, 'content') else str(response)
                    st.markdown(answer)
                    st.session_state.messages.append({"role": "assistant", "content": answer})
            except Exception as e:
                st.error(f"Error: {str(e)}")
