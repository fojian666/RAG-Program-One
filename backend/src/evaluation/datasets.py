from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievalExample:
    query: str
    relevant_image_ids: set[str]

