"""
Pure Python math implementations
No NumPy/SciPy dependencies - works on all systems!
"""

import math
from typing import List


def dot_product(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate dot product of two vectors"""
    return sum(a * b for a, b in zip(vec_a, vec_b))


def magnitude(vec: List[float]) -> float:
    """Calculate magnitude (length) of a vector"""
    return math.sqrt(sum(x * x for x in vec))


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Calculate cosine similarity (0-1, higher is more similar)
    Pure Python implementation
    """
    try:
        dot = dot_product(vec_a, vec_b)
        mag_a = magnitude(vec_a)
        mag_b = magnitude(vec_b)
        
        if mag_a == 0 or mag_b == 0:
            return 0.0
        
        similarity = dot / (mag_a * mag_b)
        return max(0.0, min(1.0, similarity))  # Clamp to [0, 1]
    except:
        return 0.0


def euclidean_distance(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate Euclidean distance"""
    try:
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(vec_a, vec_b)))
    except:
        return 0.0


def euclidean_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Convert Euclidean distance to similarity (0-1)"""
    distance = euclidean_distance(vec_a, vec_b)
    return 1 / (1 + distance)


def manhattan_distance(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate Manhattan (L1) distance"""
    try:
        return sum(abs(a - b) for a, b in zip(vec_a, vec_b))
    except:
        return 0.0


def manhattan_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Convert Manhattan distance to similarity (0-1)"""
    distance = manhattan_distance(vec_a, vec_b)
    return 1 / (1 + distance)


def mean(values: List[float]) -> float:
    """Calculate mean of a list"""
    if not values:
        return 0.0
    return sum(values) / len(values)


def variance(values: List[float]) -> float:
    """Calculate variance of a list"""
    if not values:
        return 0.0
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / len(values)


def normalize_vector(vec: List[float], min_val: float = 0.0, max_val: float = 1.0) -> List[float]:
    """Normalize vector to [min_val, max_val] range"""
    vec_min = min(vec)
    vec_max = max(vec)
    
    if vec_max == vec_min:
        return [0.5] * len(vec)
    
    normalized = []
    for x in vec:
        norm = (x - vec_min) / (vec_max - vec_min)
        scaled = norm * (max_val - min_val) + min_val
        normalized.append(scaled)
    
    return normalized












