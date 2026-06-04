from pydantic import BaseModel, Field


class RetrievedDocument(BaseModel):
    id: str
    source_url: str | None = None
    title: str | None = None
    snippet: str
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    qdrant_point_id: str | None = None
    metadata: dict[str, str] = {}


class SourceCitation(BaseModel):
    document_id: str
    source_url: str
    title: str | None = None
    claim: str
