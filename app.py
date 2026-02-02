import streamlit as st
import os
from pathlib import Path

st.set_page_config(page_title="CS RAG Assistant", page_icon="??", layout="wide")

st.title("?? Computer Science RAG Assistant")
st.markdown("Ask questions about Data Structures, Algorithms, OS, Databases, Networks, and AI!")

try:
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain.schema import Document
    
    API_KEY = os.getenv("OPENAI_API_KEY")
    if not API_KEY:
        st.error("?? OPENAI_API_KEY not set!")
        st.stop()
    
    # Initialize
    @st.cache_resource
    def load_knowledge():
        embeddings = OpenAIEmbeddings(
            openai_api_key=API_KEY,
            base_url="https://openrouter.ai/api/v1",
            model="text-embedding-ada-002"
        )
        
        data_dir = Path(__file__).parent / "data"
        texts = []
        for f in data_dir.glob("*.txt"):
            texts.append(f.read_text(encoding='utf-8', errors='ignore'))
        
        if texts:
            docs = [Document(page_content=t) for t in texts]
            return FAISS.from_documents(docs, embeddings)
        return None
    
    vectorstore = load_knowledge()
    
    if vectorstore:
        st.success("? Knowledge loaded!")
        
        question = st.text_input("Ask about Computer Science:", placeholder="e.g., What is a binary tree?")
        
        if question:
            with st.spinner("?? Thinking..."):
                # Retrieve
                docs = vectorstore.similarity_search(question, k=3)
                context = "\n\n".join([d.page_content[:800] for d in docs])
                
                # IMPORTANT: Use gpt-3.5-turbo, NOT google/gemini-flash-1.5
                llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    openai_api_key=API_KEY,
                    base_url="https://openrouter.ai/api/v1",
                    temperature=0.7
                )
                
                prompt = f"""Answer this Computer Science question using the context.

Context:
{context}

Question: {question}

Answer:"""
                
                response = llm.invoke(prompt)
                st.markdown(f"**Answer:** {response.content}")
    else:
        st.error("Failed to load knowledge base")

except Exception as e:
    st.error(f"Error: {e}")
    import traceback
    st.code(traceback.format_exc())
