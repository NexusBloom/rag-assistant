"""Document ingestion."""
from pathlib import Path
from typing import List, Union
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema import Document

class DocumentIngester:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_document(self, file_path: Union[str, Path]) -> List[Document]:
        path = Path(file_path)
        ext = path.suffix.lower()
        if ext == ".pdf":
            loader = PyPDFLoader(str(path))
        elif ext == ".txt":
            loader = TextLoader(str(path), encoding="utf-8")
        else:
            raise ValueError(f"Unsupported format: {ext}")
        return loader.load()
    
    def process_documents(self, file_paths: List[Union[str, Path]]) -> List[Document]:
        all_docs = []
        for path in file_paths:
            docs = self.load_document(path)
            chunks = self.text_splitter.split_documents(docs)
            for chunk in chunks:
                chunk.metadata.update({"source_file": str(path), "file_type": Path(path).suffix})
            all_docs.extend(chunks)
        return all_docs

