import logging
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Stores and searches transcript segments using ChromaDB with sentence-transformer embeddings.
    """

    def __init__(
        self,
        persist_directory: str = "chroma_data",
        collection_name: str = "transcripts",
        embedding_model: str = "all-MiniLM-L6-v2",
    ):
        self.embedding_fn = SentenceTransformerEmbeddingFunction(model_name=embedding_model)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn,
        )
        logger.info(f"VectorStore ready (collection='{collection_name}', embeddings='{embedding_model}')")

    def store_transcript(self, video_id: str, segments: List[Dict[str, Any]]) -> int:
        """
        Upsert transcript segments for a video.

        Uses deterministic IDs ({video_id}_{index}) so re-ingestion is idempotent.

        Returns:
            Number of segments stored.
        """
        if not segments:
            logger.warning(f"No segments to store for video '{video_id}'")
            return 0

        ids = [f"{video_id}_{i}" for i in range(len(segments))]
        documents = [seg["text"] for seg in segments]
        metadatas = [
            {
                "video_id": video_id,
                "start": seg["start"],
                "end": seg["end"],
            }
            for seg in segments
        ]

        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        logger.info(f"Stored {len(segments)} segments for video '{video_id}'")
        return len(segments)

    def search(
        self, query: str, n_results: int = 5, video_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Semantic search over stored transcript segments.

        Args:
            query: Search query text.
            n_results: Max number of results to return.
            video_id: Optional filter to search within a single video.

        Returns:
            List of dicts with keys: text, video_id, start, end, distance.
        """
        where = {"video_id": video_id} if video_id else None
        results = self.collection.query(query_texts=[query], n_results=n_results, where=where)

        out = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            out.append({
                "text": doc,
                "video_id": meta["video_id"],
                "start": meta["start"],
                "end": meta["end"],
                "distance": dist,
            })
        return out

    def get_video_ids(self) -> List[str]:
        """Return a sorted list of all stored video IDs."""
        all_meta = self.collection.get(include=["metadatas"])["metadatas"]
        return sorted({m["video_id"] for m in all_meta})

    def delete_video(self, video_id: str) -> None:
        """Delete all segments belonging to a video."""
        self.collection.delete(where={"video_id": video_id})
        logger.info(f"Deleted all segments for video '{video_id}'")
