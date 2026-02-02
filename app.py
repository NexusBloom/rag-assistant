import streamlit as st
import os

# Page setup
st.set_page_config(page_title="RAG", layout="centered")
st.title("RAG Assistant")

# Show we're alive
st.success("App is running!")

# Set API key
os.environ["OPENROUTER_API_KEY"] = "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"

# Try imports with error display
try:
    from langchain_openai import ChatOpenAI
    st.write("✅ langchain_openai loaded")
except Exception as e:
    st.error(f"❌ langchain_openai failed: {e}")

try:
    from src.core.vectorstore import VectorStoreManager
    st.write("✅ vectorstore loaded")
except Exception as e:
    st.error(f"❌ vectorstore failed: {e}")

try:
    from src.ingestion.loader import DocumentIngester
    st.write("✅ loader loaded")
except Exception as e:
    st.error(f"❌ loader failed: {e}")

# Simple chat
st.subheader("Test Chat")
msg = st.text_input("Type something:")

if msg:
    try:
        llm = ChatOpenAI(
            model="google/gemini-flash-1.5",
            openai_api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://openrouter.ai/api/v1"
        )
        response = llm.invoke(msg)
        st.write("Response:", response.content)
    except Exception as e:
        st.error(f"Chat error: {e}")
        st.code(str(e))
