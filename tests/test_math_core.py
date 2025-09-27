from app.math_core import log_e_is_one, sqrt_four_is_two

def test_log_e_is_one():
    assert round(log_e_is_one(), 6) == 1.0

def test_sqrt_four_is_two():
    assert sqrt_four_is_two() == 2.0
