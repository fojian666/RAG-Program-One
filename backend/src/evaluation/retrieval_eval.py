from src.evaluation.datasets import RetrievalExample
from src.evaluation.metrics import precision_at_k, recall_at_k


class RetrievalEvaluator:
    def evaluate(
        self,
        examples: list[RetrievalExample],
        predictions: dict[str, list[str]],
        k: int = 10,
    ):
        rows = []
        for example in examples:
            ranked_ids = predictions.get(example.query, [])
            rows.append(
                {
                    "query": example.query,
                    "precision_at_k": precision_at_k(example.relevant_image_ids, ranked_ids, k),
                    "recall_at_k": recall_at_k(example.relevant_image_ids, ranked_ids, k),
                }
            )
        return rows
