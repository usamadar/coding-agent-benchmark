import sys
from pathlib import Path
_base = Path(__file__).parent.parent
sys.path.insert(0, str(_base))
if (_base / "repo").exists():
    sys.path.insert(0, str(_base / "repo"))

from math_utils import add


def test_add_positive():
    assert add(2, 3) == 5


def test_add_zero():
    assert add(0, 5) == 5
