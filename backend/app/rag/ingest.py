from pathlib import Path

from sentence_transformers import SentenceTransformer
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma


# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[3]

DOCUMENTS_DIR = PROJECT_ROOT / "data" / "documents"
CHROMA_DIR = PROJECT_ROOT / "data" / "chroma_db"

COLLECTION_NAME = "company_policies"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class SentenceTransformerEmbeddings:
    """
    Small adapter that lets Chroma use Sentence Transformers
    without requiring an external embeddings API.
    """

    def __init__(self, model_name: str):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
        )
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )
        return embedding.tolist()


def load_documents() -> list[Document]:
    """Load all .txt policy documents."""

    documents = []

    for file_path in sorted(DOCUMENTS_DIR.glob("*.txt")):
        text = file_path.read_text(encoding="utf-8")

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "source": file_path.name,
                },
            )
        )

    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    """Split documents into smaller chunks for retrieval."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
    )

    return splitter.split_documents(documents)


def build_vector_store() -> Chroma:
    """Create the Chroma vector store from the policy documents."""

    documents = load_documents()

    if not documents:
        raise RuntimeError(
            f"No documents found in {DOCUMENTS_DIR}"
        )

    chunks = split_documents(documents)

    embeddings = SentenceTransformerEmbeddings(
        EMBEDDING_MODEL
    )

    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
    )

    print(f"Loaded documents: {len(documents)}")
    print(f"Created chunks: {len(chunks)}")
    print(f"Vector database: {CHROMA_DIR}")

    for document in documents:
        print(
            f"  - {document.metadata['source']}"
        )

    return vector_store


if __name__ == "__main__":
    build_vector_store()



_vector_store_instance = None


def get_vector_store() -> Chroma:
    """
    Loads the ALREADY-PERSISTED Chroma vector store from disk, without
    re-ingesting or re-embedding documents. Use this everywhere EXCEPT
    the one-time ingestion step (build_vector_store, run manually via
    `python -m app.rag.ingest`).

    Caches the instance at module level so repeated calls within the same
    process reuse the same connection instead of reopening the DB each time.
    """
    global _vector_store_instance

    if _vector_store_instance is not None:
        return _vector_store_instance

    if not CHROMA_DIR.exists():
        raise RuntimeError(
            f"Vector store not found at {CHROMA_DIR}. "
            "Run `python -m app.rag.ingest` once to build it first."
        )

    embeddings = SentenceTransformerEmbeddings(EMBEDDING_MODEL)

    _vector_store_instance = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    return _vector_store_instance    