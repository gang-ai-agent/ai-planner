from app.services.rag.ingestion import ingest_documents


def main() -> None:
    count = ingest_documents()
    print(f"Ingested {count} documents")


if __name__ == "__main__":
    main()
