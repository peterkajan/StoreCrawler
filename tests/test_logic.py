import aiofiles
import pytest
from asynctest import mock

from crawler.constants import (
    DEFAULT_CONTACT_PATHS,
    DEFAULT_PRODUCT_LIST_PATH,
    DEFAULT_PRODUCT_COUNT,
    DEFAULT_THROTTLE_DELAY,
)
from crawler.logic import (
    extract_product_links,
    extract_product_data,
    get_domains_from_stream,
    get_domain_data,
)
from crawler.models import Product, Config, DomainData


@pytest.mark.asyncio
async def test_get_domains_from_stream():
    async with aiofiles.open("data/stores_small.csv", mode="r") as input_file:
        assert [url async for url in get_domains_from_stream(input_file)] == [
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


def get_generator_mock(return_value):
    generator_mock = mock.MagicMock()
    generator_mock.__aiter__.return_value = return_value
    return generator_mock


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
