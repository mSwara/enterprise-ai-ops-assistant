from langchain.agents import create_agent
from langchain_core.tools import tool
from app.llm.client import get_llm
from app.rag.ingest import get_vector_store


@tool
def search_knowledge_base(query: str) -> dict:
    """
    Search company policy documents (return policy, refund policy, shipping
    policy, product policy, customer support FAQ) for information relevant
    to the query. Returns the most relevant text chunks along with their
    source document names.
    """
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=3)

    if not results:
        return {"found": False, "chunks": []}

    return {
        "found": True,
        "chunks": [
            {"source": doc.metadata.get("source", "unknown"), "content": doc.page_content}
            for doc in results
        ],
    }


knowledge_agent = create_agent(
    model=get_llm(),
    tools=[search_knowledge_base],
    system_prompt=(
        "You are the Knowledge Agent. You answer questions about company "
        "policies (returns, refunds, shipping, products) and FAQs using "
        "ONLY the search_knowledge_base tool.\n\n"
        "Rules:\n"
        "1. Always call search_knowledge_base first — never answer from "
        "general knowledge.\n"
        "2. Base your answer ONLY on the retrieved chunk content. Do not "
        "add information, numbers, or policy details that are not "
        "explicitly present in the retrieved chunks.\n"
        "3. Always cite the source document name(s) for any claim you "
        "make, e.g. '(Source: refund_policy.txt)'.\n"
        "4. If the retrieved chunks do not contain enough information to "
        "answer the question, say so explicitly — for example: 'I don't "
        "have enough grounded information to answer that.' Never guess "
        "or fill gaps with assumptions."
    ),
)