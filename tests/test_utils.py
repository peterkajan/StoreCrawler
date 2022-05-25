import pytest

from crawler import utils


def test_negate():
    neg_bool = utils.negate(bool)
    assert neg_bool(False)


@pytest.mark.parametrize(
    "domain, paths, expected_result",
    [
        [
            "sufio.com",
            ["/", "/about"],
            ["https://sufio.com/", "https://sufio.com/about"],
        ],
        ["sufio.com", [], []],
    ],
)
def test_get_urls(domain, paths, expected_result):
    assert utils.get_urls(domain, paths) == expected_result
