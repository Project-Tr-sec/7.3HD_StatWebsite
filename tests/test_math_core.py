from __future__ import annotations

from app.math_core import log_e, sqrt


def test_sqrt_four_is_two():
    assert sqrt(4) == 2


def test_log_e_is_one():
    assert log_e(math_e()) == 1


def math_e() -> float:
    return 2.718281828459045
