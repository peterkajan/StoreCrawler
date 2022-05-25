import pytest
from asynctest import mock

from crawler.constants import (
    DEFAULT_CONTACT_PATHS,
    DEFAULT_PRODUCT_LIST_PATH,
    DEFAULT_PRODUCT_COUNT,
    DEFAULT_THROTTLE_DELAY,
    OUTPUT_HEADER,
)
from crawler.logic import (
    extract_product_links,
    extract_product_data,
    get_domains_from_reader,
    get_domain_data,
    get_header_row,
    domain_data_to_row,
)
from crawler.models import Product, Config, DomainData
from tests.utils import get_generator_mock


@pytest.mark.asyncio
async def test_get_domains_from_reader():
    reader = get_generator_mock(
        [
            ["url", "something"],
            ["dwb-online.com", "blah blah"],
            ["lakanto-usa.myshopify.com", "bleh bleh"],
            ["skulls-unlimited-international-inc.myshopify.com"],
        ]
    )
    assert [url async for url in get_domains_from_reader(reader)] == [
        "dwb-online.com",
        "lakanto-usa.myshopify.com",
        "skulls-unlimited-international-inc.myshopify.com",
    ]


product_page = """
    <html>
        <body>
            <div class="product-list">
                <div class="product-item">
                    <a href="link1"></a>
                    <a href="link2"></a>
                    <a href="link3"></a>
                    <a href="link4"></a>
                    <a href="link5"></a>
                </div>
            </div>
        </body>
    </hmtl>
"""


@pytest.mark.parametrize(
    "string, count, expected_result",
    [
        ["", 5, []],
        [product_page, 0, []],
        [product_page, 3, ["link1", "link2", "link3"]],
    ],
)
def test_extract_product_links(string, count, expected_result):
    assert extract_product_links(string, count) == expected_result


product_dict1 = {"title": "some title", "images": ["image_link"]}
product_dict2 = {"title": "some title2", "images": ["image_link2"]}


@pytest.mark.parametrize(
    "product_dict, expected_result",
    [
        [{}, Product(title="", image_url="")],
        [
            {"title": "some title", "images": []},
            Product(title="some title", image_url=""),
        ],
        [
            product_dict1,
            Product(title="some title", image_url="image_link"),
        ],
    ],
)
def test_extract_product_data(product_dict, expected_result):
    assert extract_product_data(product_dict) == expected_result


contact_page1 = """
    <html>
        Some contact jozo.hossa@sufio.com
    </html>
"""
contact_page2 = """
    <html>
        Some contact marian.gaborik@sufio.com
    </html>
"""


@pytest.mark.asyncio
@mock.patch("crawler.utils.get_pages")
@mock.patch("crawler.utils.get_page")
async def test_get_domain_data(get_page_mock, get_pages_mock):
    get_page_mock.return_value = product_page
    get_pages_mock.side_effect = [
        get_generator_mock(
            [contact_page1, contact_page2, ""]
        ),  # result of getting contact pages
        get_generator_mock(
            [product_dict1, product_dict2, {}]
        ),  # result of getting product jsons
    ]

    assert await get_domain_data(
        "www.sufio.com",
        Config(
            contact_paths=DEFAULT_CONTACT_PATHS,
            product_list_path=DEFAULT_PRODUCT_LIST_PATH,
            product_count=DEFAULT_PRODUCT_COUNT,
            throttle_delay=DEFAULT_THROTTLE_DELAY,
        ),
    ) == DomainData(
        emails=["jozo.hossa@sufio.com", "marian.gaborik@sufio.com"],
        products=[
            Product(title="some title", image_url="image_link"),
            Product(title="some title2", image_url="image_link2"),
        ],
    )


@pytest.mark.parametrize(
    "product_count, expected_result",
    [
        [
            3,
            OUTPUT_HEADER
            + ["title 1", "image 1", "title 2", "image 2", "title 3", "image 3"],
        ],
        [0, OUTPUT_HEADER],
        [-1, OUTPUT_HEADER],
    ],
)
def test_get_header_row(product_count, expected_result):
    assert list(get_header_row(product_count)) == expected_result


@pytest.mark.parametrize(
    "domain_data, expected_result",
    [
        [
            DomainData(
                emails=["jozo.hossa@sufio.com", "marian.gaborik@sufio.com"],
                facebooks=["https://facebook.com/sufio"],
                twitters=["http://twitter.com/sufio"],
                products=[
                    Product(title="some title", image_url="image_link"),
                    Product(title="some title2", image_url="image_link2"),
                ],
            ),
            [
                "sufio.com",
                ["jozo.hossa@sufio.com", "marian.gaborik@sufio.com"],
                ["https://facebook.com/sufio"],
                ["http://twitter.com/sufio"],
                "some title",
                "image_link",
                "some title2",
                "image_link2",
            ],
        ],
        [DomainData(), ["sufio.com", [], [], []]],
    ],
)
def test_domain_data_to_row(domain_data, expected_result):
    assert list(domain_data_to_row("sufio.com", domain_data)) == expected_result
