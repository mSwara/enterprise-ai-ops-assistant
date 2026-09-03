import pytest
from app.rag.ingest import get_vector_store
from tests.rag_dataset import RAG_TEST_CASES


@pytest.mark.parametrize("question,expected_source", RAG_TEST_CASES)
def test_retrieval_finds_correct_source(question, expected_source):
    vector_store = get_vector_store()
    results = vector_store.similarity_search(question, k=3)

    retrieved_sources = [doc.metadata.get("source") for doc in results]

    assert expected_source in retrieved_sources, (
        f"Expected '{expected_source}' to appear in top-3 results for "
        f"'{question}', but got: {retrieved_sources}"
    )