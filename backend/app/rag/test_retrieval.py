from app.rag.ingest import build_vector_store


def test_retrieval():
    vector_store = build_vector_store()

    queries = [
        "What is the refund approval threshold?",
        "What is the return policy for electronics?",
        "How long does standard shipping take?",
        "What should I do if my package is delayed?",
    ]

    for query in queries:
        print("\n" + "=" * 70)
        print(f"QUERY: {query}")
        print("=" * 70)

        results = vector_store.similarity_search(query, k=2)

        for i, doc in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Source: {doc.metadata.get('source')}")
            print(doc.page_content)


if __name__ == "__main__":
    test_retrieval()