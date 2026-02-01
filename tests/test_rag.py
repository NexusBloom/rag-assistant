""Unit tests.""
import pytest
from src.core.vectorstore import VectorStoreManager
from src.ingestion.loader import DocumentIngester

@pytest.fixture
def sample_doc(tmp_path):
    doc = tmp_path / ""test.txt""
    doc.write_text(""RAG stands for Retrieval-Augmented Generation."")
    return str(doc)

def test_ingestion(sample_doc):
    ingester = DocumentIngester()
    docs = ingester.load_document(sample_doc)
    assert len(docs) > 0
