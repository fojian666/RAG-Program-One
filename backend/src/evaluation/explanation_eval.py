class ExplanationEvaluator:
    def has_evidence(self, explanation: dict) -> bool:
        return bool(explanation.get("reasons")) and bool(explanation.get("evidence") is not None)

