import streamlit as st
import os
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from src.core.vectorstore import VectorStoreManager
from src.ingestion.loader import DocumentIngester

# MUST be first Streamlit command
st.set_page_config(page_title="RAG", layout="wide")

st.title("RAG Assistant")

# API Key
os.environ["OPENROUTER_API_KEY"] = "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"

# Sidebar
with st.sidebar:
    st.header("Upload Document")
    files = st.file_uploader("Choose PDF/TXT", type=["pdf","txt"])
    if files:
        with open(f"data/{files.name}", "wb") as f:
            f.write(files.getvalue())
        docs = DocumentIngester().process_documents([f"data/{files.name}"])
        vs = VectorStoreManager()
        vs.create_index(docs) if not vs.load_index() else vs.add_documents(docs)
        st.success("Processed!")

# Initialize LLM
llm = ChatOpenAI(
    model="google/gemini-flash-1.5",
    openai_api_key=os.environ["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# Chat
question = st.text_input("Ask a question:")
if question:
    vs = VectorStoreManager()
    if vs.load_index():
        docs = vs.get_retriever().get_relevant_documents(question)
        context = "\n".join([d.page_content for d in docs[:3]])
        prompt = f"Context: {context}\n\nQuestion: {question}\nAnswer:"
        response = llm.invoke(prompt)
        st.write("Answer:", response.content)
    else:
        st.error("Please upload a document first!")
