import streamlit as st
import os
from pathlib import Path

# Page setup
st.set_page_config(page_title="RAG Assistant", layout="wide")
st.title("?? RAG Assistant")

# Check if we can load dependencies
st.info("Loading system...")

try:
    # Imports
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain_community.document_loaders import TextLoader, PyPDFLoader
    
    st.success("? All dependencies loaded!")
    
    # API Key - Read from environment variable OPENAI_API_KEY
    API_KEY = os.getenv("OPENAI_API_KEY")
    
    if not API_KEY:
        st.error("? OPENAI_API_KEY environment variable not set!")
        st.stop()
    
    # Simple RAG class (no external files)
    class SimpleRAG:
        def __init__(self):
            # Use OpenAI embeddings instead of HuggingFace to avoid PyTorch issues
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=API_KEY,
                base_url="https://openrouter.ai/api/v1",
                model="text-embedding-ada-002"
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
            except Exception as e:
                st.warning(f"Could not load existing index: {e}")
                return False
        
        def create_index(self, texts, source="upload"):
            documents = [Document(page_content=t, metadata={"source": source}) for t in texts]
            if self.vectorstore:
                self.vectorstore.add_documents(documents)
            else:
                self.vectorstore = FAISS.from_documents(documents, self.embeddings)
            self.vectorstore.save_local(str(self.store_path))
            return True
        
        def load_builtin_documents(self):
            """Load documents from data folder on startup"""
            base_dir = Path(__file__).parent
            data_dir = base_dir / "data"
            
            if not data_dir.exists():
                st.warning("?? No data folder found")
                return False
            
            all_texts = []
            loaded_files = []
            
            for file_path in data_dir.glob("*.txt"):
                try:
                    loader = TextLoader(str(file_path), encoding='utf-8')
                    docs = loader.load()
                    texts = [d.page_content for d in docs]
                    all_texts.extend(texts)
                    loaded_files.append(file_path.name)
                except Exception as e:
                    st.warning(f"Could not load {file_path.name}: {e}")
            
            if all_texts:
                self.create_index(all_texts, source="builtin")
                st.success(f"?? Loaded built-in knowledge: {', '.join(loaded_files)}")
                return True
            return False
        
        def query(self, question):
            if not self.vectorstore:
                if not self.load_index():
                    return "Please upload documents first! No built-in knowledge loaded."
            
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
    
    # Load built-in documents on startup
    with st.spinner("?? Loading knowledge base..."):
        if not rag.load_index():
            rag.load_builtin_documents()
    
    # Sidebar
    with st.sidebar:
        st.header("?? Upload")
        file = st.file_uploader("Choose file", type=["txt", "pdf"])
        
        if file:
            with st.spinner("Processing..."):
                try:
                    save_path = f"./uploaded_{file.name}"
                    with open(save_path, "wb") as f:
                        f.write(file.getvalue())
                    
                    if file.name.endswith(".pdf"):
                        from langchain_community.document_loaders import PyPDFLoader
                        loader = PyPDFLoader(save_path)
                        docs = loader.load()
                        texts = [d.page_content for d in docs]
                    else:
                        text = file.getvalue().decode("utf-8")
                        texts = [text]
                    
                    rag.create_index(texts)
                    st.success("? Document indexed!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Chat
    st.subheader("?? Chat")
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
    st.error(f"? System Error: {e}")
    st.code(str(e))
    import traceback
    st.code(traceback.format_exc())

