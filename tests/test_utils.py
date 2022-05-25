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


@pytest.mark.parametrize(
    "link, default_domain, expected_result",
    [
        ["/abcd", "sufio.com", "https://sufio.com/abcd"],
        ["no_slash", "sufio.com", "https://sufio.com/no_slash"],
        ["https://sufio.com/abcd", "guestcloud.net", "https://sufio.com/abcd"],
        ["", "sufio.com", "https://sufio.com"],
        ["", "", "https://"],
    ],
)
def test_convert_to_absolute_url(link, default_domain, expected_result):
    assert utils.convert_to_absolute_url(link, default_domain) == expected_result


@pytest.mark.parametrize(
    "url, expected_result",
    [
        ["https://sufio.com/abcd", "https://sufio.com/abcd.json"],
        ["https://sufio.com/abcd/", "https://sufio.com/abcd.json"],
        ["", ".json"],
    ],
)
def test_url_to_json_url(url, expected_result):
    assert utils.url_to_json_url(url) == expected_result
