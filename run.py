"""CLI interface for RAG Assistant."""
import argparse
import asyncio
from src.core.rag_chain import RAGAssistant
from src.ingestion.loader import DocumentIngester
from src.core.vectorstore import VectorStoreManager

async def interactive_mode():
    print("RAG Assistant initialized. Type 'exit' to quit.")
    assistant = RAGAssistant()
    session_id = "cli-session"
    
    while True:
        query = input("\nYou: ").strip()
        if query.lower() == 'exit':
            break
        
        try:
            result = await assistant.query(query, session_id)
            print(f"\nAssistant: {result['answer']}")
        except Exception as e:
            print(f"Error: {e}")

def ingest_files(paths):
    ingester = DocumentIngester()
    docs = ingester.process_documents(paths)
    vs = VectorStoreManager()
    if vs.load_index():
        vs.add_documents(docs)
    else:
        vs.create_index(docs)
    print(f"Indexed {len(docs)} chunks")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG Assistant")
    parser.add_argument("--ingest", nargs="+", help="Files to ingest")
    parser.add_argument("--interactive", action="store_true", help="Chat mode")
    args = parser.parse_args()
    
    if args.ingest:
        ingest_files(args.ingest)
    elif args.interactive:
        asyncio.run(interactive_mode())
    else:
        print("Use --interactive for chat mode or --ingest <files> to add documents")
