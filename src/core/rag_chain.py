"""RAG chain with OpenRouter."""
import os
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnableLambda
from operator import itemgetter
from src.core.vectorstore import VectorStoreManager

# HARD CODE API KEY HERE FOR RENDER DEPLOYMENT
OPENROUTER_API_KEY = "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"

class RAGAssistant:
    def __init__(self):
        self.vector_manager = VectorStoreManager()
        
        # Use hardcoded key - this will definitely work
        self.llm = ChatOpenAI(
            model="google/gemini-flash-1.5",
            temperature=0.0,
            openai_api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://rag-assistant.onrender.com",
                "X-Title": "RAG Assistant"
            }
        )
        
        self.memories: Dict[str, ConversationBufferMemory] = {}
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a precise document assistant. Use the context to answer."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}")
        ])
    
    def get_memory(self, session_id: str):
        if session_id not in self.memories:
            self.memories[session_id] = ConversationBufferMemory(return_messages=True, memory_key="history")
        return self.memories[session_id]
    
    def format_docs(self, docs) -> str:
        return "\n\n".join([f"[{i+1}] {d.page_content}" for i, d in enumerate(docs)])
    
    async def query(self, question: str, session_id: str = "default") -> Dict:
        if not self.vector_manager.load_index():
            raise ValueError("No documents ingested")
        
        memory = self.get_memory(session_id)
        retriever = self.vector_manager.get_retriever()
        
        chain = (
            {
                "context": RunnableLambda(lambda x: retriever.get_relevant_documents(x["question"])) | self.format_docs,
                "question": itemgetter("question"),
                "history": RunnableLambda(lambda x: memory.load_memory_variables({})["history"])
            }
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
        
        response = chain.invoke({"question": question})
        memory.save_context({"question": question}, {"output": response})
        
        return {"answer": response, "session_id": session_id, "status": "success"}
    
    def clear_memory(self, session_id: str):
        if session_id in self.memories:
            del self.memories[session_id]
