from weather.calcul_normale_itn import compute_normale_itn, normale_itn
from weather.itn.gateway_tests import ReadTemperaturesTests

NAN = float("nan")


# == compute_normale_itn =============================================


def test_compute_normale_itn():
    result = compute_normale_itn(ReadTemperaturesTests)
    print(result)
    assert 1 == 1, "Test in progress"


# == normale_itn =====================================================


def test_normale_itn():
    result = normale_itn(read_protocol=ReadTemperaturesTests)
    print(result)
    assert 1 == 1, "Test in progress"
