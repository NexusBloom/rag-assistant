import streamlit as st
import os
import sys

# Set page config FIRST
st.set_page_config(page_title="RAG Assistant", page_icon="📚")

st.title("📚 RAG Assistant")
st.write("Status: Initializing...")

try:
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from src.core.vectorstore import VectorStoreManager
    from src.ingestion.loader import DocumentIngester
    
    # Set API key
    os.environ["OPENROUTER_API_KEY"] = "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"
    
    # Create directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("vectorstore", exist_ok=True)
    
    st.write("Status: ✅ System ready")
    
    # Sidebar for uploads
    with st.sidebar:
        st.header("📁 Documents")
        files = st.file_uploader("Upload PDF/TXT", type=["pdf", "txt"])
        
        if files:
            with st.spinner("Processing..."):
                try:
                    save_path = f"data/{files.name}"
                    with open(save_path, "wb") as f:
                        f.write(files.getvalue())
                    
                    ingester = DocumentIngester()
                    docs = ingester.process_documents([save_path])
                    
                    vs = VectorStoreManager()
                    if vs.load_index():
                        vs.add_documents(docs)
                    else:
                        vs.create_index(docs)
                    
                    st.success(f"✅ Added {len(docs)} chunks!")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # Main chat area
    st.subheader("💬 Chat")
    question = st.text_input("Ask something...")
    
    if question:
        with st.spinner("Thinking..."):
            try:
                vs = VectorStoreManager()
                if not vs.load_index():
                    st.warning("⚠️ Please upload a document first!")
                else:
                    # Get relevant docs
                    retriever = vs.get_retriever()
                    docs = retriever.get_relevant_documents(question)
                    context = "\n\n".join([d.page_content for d in docs[:3]])
                    
                    # Query LLM
                    llm = ChatOpenAI(
                        model="google/gemini-flash-1.5",
                        temperature=0,
                        openai_api_key=os.environ["OPENROUTER_API_KEY"],
                        base_url="https://openrouter.ai/api/v1",
                        default_headers={
                            "HTTP-Referer": "https://rag-assistant.onrender.com",
                            "X-Title": "RAG"
                        }
                    )
                    
                    prompt = f"""Answer based on context:
{context}

Question: {question}
Answer:"""
                    
                    response = llm.invoke(prompt)
                    st.markdown("**Answer:**")
                    st.write(response.content)
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.code(str(e))

except Exception as e:
    st.error(f"❌ Failed to initialize: {str(e)}")
    st.code(str(e))
