import math
import app.math_core as mc 

def test_log_e_is_one():
    assert abs(mc.log(math.e) - 1.0) < 1e-12

def test_sqrt_four_is_two():
    assert mc.sqrt(4) == 2
