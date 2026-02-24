"""
One-time ingestion script: loads corpus/*.txt → embeds → inserts into knowledge_chunks.

Run once after DB migration:
    python -m src.knowledge.ingest

Requirements:
    - DATABASE_URL env variable (or .env file)
    - psql extension vector enabled (see migrations/add_knowledge_chunks.sql)
    - sentence-transformers, pgvector, sqlalchemy installed
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text

load_dotenv()

CORPUS_DIR = Path(__file__).parent / "corpus"
DATABASE_URL = os.environ["DATABASE_URL"]

# Category is inferred from filename prefix: sleep_01.txt → 'sleep'
VALID_CATEGORIES = {"sleep", "exercise", "nutrition", "stress"}


def ingest() -> None:
    """Load all corpus/*.txt files, embed them, and insert into knowledge_chunks."""
    engine = create_engine(DATABASE_URL)
    model = SentenceTransformer("all-MiniLM-L6-v2")

    corpus_files = sorted(CORPUS_DIR.glob("*.txt"))
    if not corpus_files:
        print(f"No .txt files found in {CORPUS_DIR}")
        return

    print(f"Found {len(corpus_files)} corpus files — embedding and inserting...")

    with engine.begin() as conn:
        # Clear existing data to allow safe re-ingestion
        conn.execute(text("DELETE FROM knowledge_chunks"))

        for filepath in corpus_files:
            # Infer category from filename (e.g. sleep_03.txt → 'sleep')
            category = filepath.stem.split("_")[0]
            if category not in VALID_CATEGORIES:
                print(f"  SKIP {filepath.name} — unknown category '{category}'")
                continue

            content = filepath.read_text(encoding="utf-8").strip()
            if not content:
                print(f"  SKIP {filepath.name} — empty file")
                continue

            # Source is stored in last line if it starts with "Source:"
            lines = content.splitlines()
            source = ""
            if lines[-1].startswith("Source:"):
                source = lines[-1].removeprefix("Source:").strip()
                content = "\n".join(lines[:-1]).strip()

            embedding: list[float] = model.encode(content).tolist()

            conn.execute(
                text(
                    """
                    INSERT INTO knowledge_chunks (category, content, embedding, source)
                    VALUES (:category, :content, CAST(:embedding AS vector), :source)
                    """
                ),
                {
                    "category": category,
                    "content": content,
                    "embedding": str(embedding),
                    "source": source,
                },
            )
            print(f"  OK  {filepath.name} [{category}]")

    print(f"\nIngestion complete — {len(corpus_files)} files processed.")


if __name__ == "__main__":
    ingest()
