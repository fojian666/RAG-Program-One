from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    name: str

    @abstractmethod
    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    def append_error(self, state: dict[str, Any], message: str) -> dict[str, Any]:
        errors = list(state.get("errors", []))
        errors.append(f"{self.name}: {message}")
        return {"errors": errors}

