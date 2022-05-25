from itertools import chain
from typing import AsyncGenerator, Coroutine, cast

import aiohttp
from aiocsv import AsyncReader, AsyncWriter
from bs4 import BeautifulSoup

from crawler import utils
from crawler.constants import email_re_pattern, OUTPUT_HEADER
from crawler.models import Product, DomainData, is_product_empty, Config


async def get_domains_from_reader(
    reader: AsyncReader,
) -> AsyncGenerator[str, None]:
    first = True
    async for row in reader:
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


async def get_domain_data(domain: str, config: Config) -> DomainData:
    domain_data = DomainData()
    contact_urls = utils.get_urls(domain, config.contact_paths)
    async with aiohttp.ClientSession() as session:
        async for page in utils.get_pages(contact_urls, session, config.throttle_delay):
            domain_data.emails.extend(
                [match[0] for match in email_re_pattern.findall(cast(str, page))]
            )
            # TODO twitter, facebook

        product_page = await utils.get_page(domain, session, config.product_list_path)
        if product_page:
            product_links = extract_product_links(
                cast(str, product_page), config.product_count
            )

            domain_data.products = list(
                filter(
                    utils.negate(is_product_empty),
                    [
                        extract_product_data(cast(dict, product_json))
                        async for product_json in utils.get_pages(
                            product_links, session, config.throttle_delay, as_json=True
                        )
                    ],
                )
            )

    return domain_data


def get_header_row(product_count: int) -> chain[str]:
    return chain(
        OUTPUT_HEADER,
        *([f"title {i}", f"image {i}"] for i in range(1, product_count + 1)),
    )


def domain_data_to_row(domain: str, domain_data: DomainData) -> chain:
    return chain(
        [
            domain,
            domain_data.emails,
            domain_data.facebooks,
            domain_data.twitters,
        ],
        *([product.title, product.image_url] for product in domain_data.products),
    )


def serialize_domain_data(
    domain: str, domain_data: DomainData, writer: AsyncWriter
) -> Coroutine:
    return writer.writerow(domain_data_to_row(domain, domain_data))


async def store_domain_data(
    domain: str, config: Config, writer: AsyncWriter
) -> Coroutine:
    return serialize_domain_data(domain, await get_domain_data(domain, config), writer)
