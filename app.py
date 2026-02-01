import streamlit as st
import uuid
import asyncio
import requests
import os
from urllib.parse import urlparse
from src.core.rag_chain import RAGAssistant
from src.ingestion.loader import DocumentIngester
from src.core.vectorstore import VectorStoreManager

os.environ["GOOGLE_API_KEY"] = "AIzaSyAR_8kLhCSIHy2CYt7uXalMDHzit3h6-nQ"

st.set_page_config(page_title="RAG Assistant", page_icon=":books:", layout="wide")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []
if "assistant" not in st.session_state:
    st.session_state.assistant = RAGAssistant()

st.title("Production RAG Assistant")
st.caption("Session: " + st.session_state.session_id)

DEFAULT_AI_DOCUMENT = """Artificial Intelligence: A Comprehensive Overview

Introduction to Artificial Intelligence
Artificial Intelligence (AI) refers to the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving.

Key Concepts in AI:
Machine Learning (ML) is a subset of AI that focuses on the use of data and algorithms to imitate the way that humans learn, gradually improving its accuracy. Deep Learning is a type of ML that uses neural networks with many layers (hence "deep") to analyze various factors in large amounts of data.

Natural Language Processing (NLP) allows computers to understand, interpret, and generate human language. Computer Vision enables machines to interpret and make decisions based on visual data from the world.

Types of AI:
Narrow AI (Weak AI) is designed to perform a narrow task (e.g., facial recognition, internet searches, driving a car). It operates under a limited set of constraints and cannot perform beyond its specific programming.
Artificial General Intelligence (AGI) is the hypothesized ability of an intelligent agent to understand or learn any intellectual task that a human being can. This remains theoretical as of 2024.

Applications of AI:
Healthcare: AI is used for diagnosis, drug discovery, personalized medicine, and medical imaging analysis.
Finance: Algorithmic trading, fraud detection, risk assessment, and customer service automation.
Transportation: Self-driving vehicles, traffic optimization, and route planning.
Education: Personalized learning experiences, automated grading, and intelligent tutoring systems.
Entertainment: Content recommendation, game playing (Chess, Go), and content generation.

Ethics and Challenges:
Bias in AI systems can lead to unfair outcomes. Privacy concerns arise from data collection. Job displacement is a significant economic concern. The black box problem makes it difficult to understand how AI makes decisions.

Future of AI:
Researchers are working toward more explainable AI (XAI), quantum machine learning, and eventually AGI. The integration of AI with robotics, IoT, and edge computing will continue to transform industries.

Computer Science Fundamentals
Computer Science is the study of algorithmic processes, computational machines, and information. It spans both theoretical and practical aspects.

Core Areas:
Algorithms and Data Structures form the foundation of efficient computing. Theory of Computation deals with what can be computed and the resources required. Computer Architecture involves the design of computer systems. Software Engineering covers systematic approaches to software development.

Programming Paradigms:
Object-Oriented Programming organizes code into objects containing data and methods. Functional Programming treats computation as the evaluation of mathematical functions. Procedural Programming uses procedures or routines to perform operations."""

def load_default_document():
    """Load the built-in AI knowledge base"""
    try:
        # Save default content to file
        default_path = "./data/default_ai_knowledge.txt"
        os.makedirs("./data", exist_ok=True)
        
        if not os.path.exists(default_path):
            with open(default_path, "w", encoding="utf-8") as f:
                f.write(DEFAULT_AI_DOCUMENT)
        
        # Ingest if vector store is empty
        vs = VectorStoreManager()
        if vs.load_index() is None:
            ingester = DocumentIngester()
            docs = ingester.process_documents([default_path])
            vs.create_index(docs)
            return True
        return False
    except Exception as e:
        st.error("Error loading default knowledge: " + str(e))
        return False

def load_from_url(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    parsed = urlparse(url)
    path = parsed.path.lower()
    if path.endswith('.pdf'):
        ext = '.pdf'
    elif path.endswith('.txt'):
        ext = '.txt'
    else:
        ext = '.txt'
    temp_path = "./data/url_doc" + ext
    with open(temp_path, 'wb') as f:
        f.write(response.content)
    return temp_path

# Auto-load default document on startup
if "default_loaded" not in st.session_state:
    loaded = load_default_document()
    st.session_state.default_loaded = True
    if loaded:
        st.success("Loaded built-in AI/Computer Science knowledge base!")

with st.sidebar:
    st.header("Document Sources")
    
    st.info("AI knowledge base is pre-loaded! You can chat immediately below.")
    
    st.subheader("Add More Documents")
    
    uploaded_files = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"], accept_multiple_files=True)
    
    if uploaded_files and st.button("Process Files"):
        with st.spinner("Processing..."):
            paths = []
            for file in uploaded_files:
                path = "./data/" + file.name
                with open(path, "wb") as f:
                    f.write(file.getvalue())
                paths.append(path)
            ingester = DocumentIngester()
            docs = ingester.process_documents(paths)
            vs = VectorStoreManager()
            if vs.load_index():
                vs.add_documents(docs)
                st.success("Added " + str(len(docs)) + " chunks!")
            else:
                vs.create_index(docs)
                st.success("Created index with " + str(len(docs)) + " chunks!")
    
    url = st.text_input("Or enter Document URL", placeholder="https://example.com/doc.pdf")
    
    if url and st.button("Load URL"):
        with st.spinner("Downloading..."):
            try:
                path = load_from_url(url)
                ingester = DocumentIngester()
                docs = ingester.process_documents([path])
                vs = VectorStoreManager()
                if vs.load_index():
                    vs.add_documents(docs)
                    st.success("Added from URL!")
                else:
                    vs.create_index(docs)
                    st.success("Created index from URL!")
            except Exception as e:
                st.error(str(e))
    
    if st.button("Reset to Default Knowledge"):
        st.session_state.assistant.clear_memory(st.session_state.session_id)
        st.session_state.messages = []
        try:
            vs = VectorStoreManager()
            if vs.vectorstore:
                import shutil
                shutil.rmtree("./vectorstore", ignore_errors=True)
            load_default_document()
            st.success("Reset to AI knowledge base!")
            st.rerun()
        except Exception as e:
            st.error(str(e))
    
    if st.button("Clear Chat Only"):
        st.session_state.assistant.clear_memory(st.session_state.session_id)
        st.session_state.messages = []
        st.success("Chat cleared!")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about AI, Computer Science, or your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = asyncio.run(st.session_state.assistant.query(prompt, st.session_state.session_id))
                st.markdown(result["answer"])
                st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
            except Exception as e:
                st.error("Error: " + str(e))
