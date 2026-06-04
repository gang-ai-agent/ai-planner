from app.schemas.rag import RetrievedDocument


def rerank(documents: list[RetrievedDocument]) -> list[RetrievedDocument]:
    return sorted(documents, key=lambda doc: doc.score, reverse=True)
