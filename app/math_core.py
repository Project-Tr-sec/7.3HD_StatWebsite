from __future__ import annotations

import math
from typing import Iterable, List


def sqrt(x: float) -> float:
    return math.sqrt(float(x))


def log_e(x: float) -> float:
    return math.log(float(x))


def mean(values: Iterable[float]) -> float:
    vals: List[float] = [float(v) for v in values]
    if not vals:
        raise ValueError("No values provided for mean")
    return sum(vals) / len(vals)


def variance(values: Iterable[float], sample: bool = True) -> float:
    """
    Variance with sample=True giving sample variance (ddof=1),
    and sample=False giving population variance (ddof=0).
    """
    vals: List[float] = [float(v) for v in values]
    n = len(vals)
    if n == 0:
        raise ValueError("No values provided for variance")
    m = mean(vals)
    ss = sum((v - m) ** 2 for v in vals)
    ddof = 1 if sample else 0
    if n - ddof <= 0:
        raise ValueError("Not enough values for sample variance")
    return ss / (n - ddof)
