from typing import List, Tuple

def calculate_confidence(distances: List[float]) -> Tuple[float, str]:
    """
    ChromaDB cosine distances: 0 = identical, 2 = completely opposite.
    We convert to similarity: similarity = 1 - (distance / 2).
    Then compute a weighted average (top results weighted more).
    """
    if not distances:
        return 0.0, "Low"
    similarities = [max(0.0, 1.0 - (d / 2)) for d in distances]
    weights = [1.0 / (i + 1) for i in range(len(similarities))]
    total_weight = sum(weights)
    score = sum(s * w for s, w in zip(similarities, weights)) / total_weight
    if score >= 0.75:
        label = "High"
    elif score >= 0.50:
        label = "Medium"
    else:
        label = "Low"
    return round(score, 3), label

def distance_to_similarity(distance: float) -> float:
    return round(max(0.0, 1.0 - (distance / 2)), 3)