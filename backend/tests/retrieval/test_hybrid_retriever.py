import pytest

from src.retrieval.hybrid_retriever import HybridRetriever


class FakeVectorRetriever:
    async def search_image_vectors(self, query_text, top_k, filters):
        return [
            {
                "image_id": "img-1",
                "score": 0.9,
                "source": "image_vector",
                "payload": {"metadata": {"objects": ["cat"]}},
            }
        ]

    async def search_caption_vectors(self, query_text, top_k, filters):
        return [
            {
                "image_id": "img-1",
                "score": 0.8,
                "source": "caption_vector",
                "payload": {"caption": "A cat on a sofa."},
            }
        ]


class FakeMetadataRetriever:
    async def search(self, filters, top_k):
        return [
            {
                "image_id": "img-2",
                "score": 0.7,
                "source": "metadata",
                "payload": {"metadata": {"objects": ["cat"], "scene": ["home"]}},
            }
        ]


class FakeCaptionRetriever:
    async def search(self, query_text, top_k):
        return []


@pytest.mark.asyncio
async def test_hybrid_retriever_merges_duplicate_candidates():
    retriever = HybridRetriever(
        vector_retriever=FakeVectorRetriever(),
        metadata_retriever=FakeMetadataRetriever(),
        caption_retriever=FakeCaptionRetriever(),
    )

    items = await retriever.retrieve(
        query="猫",
        intent={},
        expanded_query={"positive_text": "猫 cat pet"},
        plan={
            "top_k": 10,
            "metadata_filters": {},
            "recall_routes": ["image_vector", "caption_vector", "metadata", "caption_text"],
        },
    )

    assert len(items) == 2
    assert items[0]["image_id"] == "img-1"
    assert items[0]["component_scores"]["image_vector"] == 0.9
    assert items[0]["component_scores"]["caption_vector"] == 0.8

