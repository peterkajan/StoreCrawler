from typing import AsyncGenerator

from aiocsv import AsyncReader
from aiofiles.threadpool.text import AsyncTextIOWrapper
from bs4 import BeautifulSoup

from crawler import utils
from crawler.constants import email_re_pattern
from crawler.models import Product, DomainData, is_product_empty, Config


async def get_domains_from_stream(
    input_stream: AsyncTextIOWrapper,
) -> AsyncGenerator[str, None]:
    first = True
    async for row in AsyncReader(input_stream):
        # skip first row
        if first:
            first = False
        else:
            yield row[0]


def extract_product_links(page: str, product_count: int) -> list[str]:
    soup = BeautifulSoup(page, "html.parser")
    product_list = soup.find("div", class_="product-list")

    return (
        [
            product_link["href"]
            for product_link in soup.select(".product-list .product-item > a")[
                :product_count
            ]
        ]
        if product_list
        else []
    )


def extract_product_data(product_dict: dict) -> Product:
    # be robust, return some default values
    try:
        image_url = product_dict["images"][0]
    except (IndexError, KeyError):
        image_url = ""

    return Product(title=product_dict.get("title", ""), image_url=image_url)


async def get_domain_data(domain, config):
    domain_data = DomainData()
    contact_urls = utils.get_urls(domain, config.contact_paths)
    async for page in utils.get_pages(contact_urls, config.throttle_delay):
        domain_data.emails.extend(
            [match[0] for match in email_re_pattern.findall(page)]
        )
        # TODO twitter, facebook

    product_page = await utils.get_page(domain, config.product_list_path)
    if product_page:
        product_links = extract_product_links(product_page, config.product_count)

        domain_data.products = list(
            filter(
                utils.negate(is_product_empty),
                [
                    extract_product_data(product_json)
                    async for product_json in utils.get_pages(
                        product_links, config.throttle_delay, as_json=True
                    )
                ],
            )
        )

    return domain_data


async def serialize_domain_data(domain_data):
    # TODO
    print(domain_data)


async def store_domain_data(domain: str, config: Config):
    return serialize_domain_data(await get_domain_data(domain, config))
