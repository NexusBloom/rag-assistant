import streamlit as st
import os
from pathlib import Path

# Page setup
st.set_page_config(page_title="RAG Assistant", layout="wide")
st.title("📚 RAG Assistant")

# Check if we can load dependencies
st.info("Loading system...")

try:
    # Imports
    from langchain_openai import ChatOpenAI
    from langchain_community.vectorstores import FAISS
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain_community.document_loaders import TextLoader, PyPDFLoader
    
    st.success("✅ All dependencies loaded!")
    
    # API Key
    API_KEY = "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"
    
    # Simple RAG class (no external files)
    class SimpleRAG:
        def __init__(self):
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            self.store_path = Path("./vectorstore")
            self.store_path.mkdir(exist_ok=True)
            self.vectorstore = None
            
        def load_index(self):
            try:
                if not (self.store_path / "index.faiss").exists():
                    return False
                self.vectorstore = FAISS.load_local(
                    str(self.store_path), 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                return True
            except:
                return False
        
        def create_index(self, texts):
            documents = [Document(page_content=t, metadata={"source": "upload"}) for t in texts]
            self.vectorstore = FAISS.from_documents(documents, self.embeddings)
            self.vectorstore.save_local(str(self.store_path))
            return True
        
        def query(self, question):
            if not self.vectorstore:
                if not self.load_index():
                    return "Please upload documents first!"
            
            docs = self.vectorstore.similarity_search(question, k=3)
            context = "\n\n".join([d.page_content for d in docs])
            
            llm = ChatOpenAI(
                model="google/gemini-flash-1.5",
                openai_api_key=API_KEY,
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://rag-assistant.onrender.com",
                    "X-Title": "RAG Assistant"
                }
            )
            
            prompt = f"""Based on this context:
{context}

Answer this question: {question}"""
            
            response = llm.invoke(prompt)
            return response.content
    
    # Initialize
    rag = SimpleRAG()
    
    # Sidebar
    with st.sidebar:
        st.header("📁 Upload")
        file = st.file_uploader("Choose file", type=["txt", "pdf"])
        
        if file:
            with st.spinner("Processing..."):
                try:
                    # Save file
                    save_path = f"./uploaded_{file.name}"
                    with open(save_path, "wb") as f:
                        f.write(file.getvalue())
                    
                    # Load based on type
                    if file.name.endswith(".pdf"):
                        from langchain_community.document_loaders import PyPDFLoader
                        loader = PyPDFLoader(save_path)
                        docs = loader.load()
                        texts = [d.page_content for d in docs]
                    else:
                        text = file.getvalue().decode("utf-8")
                        texts = [text]
                    
                    # Create index
                    rag.create_index(texts)
                    st.success("✅ Document indexed!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Chat
    st.subheader("💬 Chat")
    question = st.text_input("Ask about your document:")
    
    if question:
        with st.spinner("Thinking..."):
            try:
                answer = rag.query(question)
                st.markdown(f"**Answer:** {answer}")
            except Exception as e:
                st.error(f"Error: {e}")
                st.code(str(e))

except Exception as e:
    st.error(f"❌ System Error: {e}")
    st.code(str(e))
    import traceback
    st.code(traceback.format_exc())
