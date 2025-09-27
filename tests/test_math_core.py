import math
import pytest
from app.math_core import log, sqrt

def test_log_e_is_one():
    assert abs(log(math.e) - 1.0) < 1e-12

def test_sqrt_four_is_two():
    assert sqrt(4) == 2
