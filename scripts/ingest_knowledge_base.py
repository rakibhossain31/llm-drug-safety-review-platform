#!/usr/bin/env python
import json
from safetyreview_ai.core.database import initialize_database
from safetyreview_ai.rag.ingestion import ingest_guidance

if __name__ == "__main__":
    initialize_database()
    print(json.dumps(ingest_guidance(), indent=2))
