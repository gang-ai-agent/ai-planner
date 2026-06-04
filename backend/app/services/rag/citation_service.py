from app.schemas.rag import RetrievedDocument, SourceCitation


def citations_from_documents(documents: list[RetrievedDocument]) -> list[SourceCitation]:
    return [
        SourceCitation(
            document_id=doc.id,
            source_url=doc.source_url or "",
            title=doc.title,
            claim=doc.snippet[:160],
        )
        for doc in documents
        if doc.source_url
    ]
