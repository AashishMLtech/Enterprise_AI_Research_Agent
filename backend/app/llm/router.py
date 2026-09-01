from dataclasses import dataclass


@dataclass(frozen=True)
class ModelRoute:
    tier: int
    model: str


def route_task(task: str) -> ModelRoute:
    if task in {"classification", "extraction", "rewrite"}:
        return ModelRoute(1, "fast")
    return ModelRoute(2, "strong")
