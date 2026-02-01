"""Streamlit UI for RAG Assistant."""
import streamlit as st
import requests
import uuid

st.set_page_config(page_title="RAG Assistant", page_icon="??")
API_URL = "http://localhost:8000"

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8]
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("?? RAG Assistant")
st.caption(f"Session: {st.session_state.session_id}")

with st.sidebar:
    st.header("Upload Documents")
    uploaded_files = st.file_uploader("Select files", type=["pdf", "txt"], accept_multiple_files=True)
    
    if uploaded_files and st.button("Process"):
        with st.spinner("Processing..."):
            paths = []
            for file in uploaded_files:
                path = f"./data/{file.name}"
                with open(path, "wb") as f:
                    f.write(file.getvalue())
                paths.append(path)
            requests.post(f"{API_URL}/ingest", json=paths)
            st.success("Done!")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about your documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            resp = requests.post(
                f"{API_URL}/query",
                json={"question": prompt, "session_id": st.session_state.session_id}
            ).json()
            st.markdown(resp["answer"])
            st.session_state.messages.append({"role": "assistant", "content": resp["answer"]})

