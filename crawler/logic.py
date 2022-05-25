import asyncio
import logging
from itertools import chain
from typing import AsyncGenerator, Coroutine, cast, Iterable

import aiohttp
from aiocsv import AsyncReader, AsyncWriter
from bs4 import BeautifulSoup

from crawler import utils
from crawler.constants import email_re_pattern, OUTPUT_HEADER, HTTP_TIMEOUT
from crawler.models import Product, DomainData, is_product_empty, Config

logger = logging.getLogger(__name__)


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
        image_url = product_dict["product"]["images"][0]["src"]
    except (IndexError, KeyError):
        image_url = ""

    return Product(
        title=product_dict.get("product", {}).get("title", ""), image_url=image_url
    )


def get_product_json_urls(page: str, domain: str, product_count: int) -> list[str]:
    return [
        utils.url_to_json_url(utils.convert_to_absolute_url(link, domain))
        for link in extract_product_links(cast(str, page), product_count)
    ]


def extract_emails(string: str) -> list[str]:
    return [
        match[0]
        for match in email_re_pattern.findall(cast(str, string))
        if utils.is_valid_email_domain(match[0])
    ]


async def get_product_data(domain: str, config: Config, session: aiohttp.ClientSession):
    try:
        product_list_url = utils.get_url(domain, config.product_list_path)
        product_page = await utils.get_page(product_list_url, session)
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.info("Getting products page %s failed: %s", product_list_url, e)
        return []

    product_urls = get_product_json_urls(
        cast(str, product_page), domain, config.product_count
    )

    return list(
        filter(
            utils.negate(is_product_empty),
            [
                extract_product_data(cast(dict, product_json))
                async for product_json in utils.get_pages(
                    product_urls, session, config.throttle_delay, as_json=True
                )
            ],
        )
    )


async def get_domain_data(domain: str, config: Config) -> DomainData:
    logger.info("Getting domain data for %s", domain)
    domain_data = DomainData()
    contact_urls = utils.get_urls(domain, config.contact_paths)
    async with aiohttp.ClientSession(read_timeout=HTTP_TIMEOUT) as session:
        async for page in utils.get_pages(contact_urls, session, config.throttle_delay):
            domain_data.emails.extend(extract_emails(cast(str, page)))
            # TODO twitter, facebook

        domain_data.products = await get_product_data(domain, config, session)

    logger.debug("Got domain data for %s: %s", domain, domain_data)
    return domain_data


def get_header_row(product_count: int) -> chain[str]:
    return chain(
        OUTPUT_HEADER,
        *([f"title {i}", f"image {i}"] for i in range(1, product_count + 1)),
    )


def list_to_cell(list_: Iterable) -> str:
    return ", ".join(list_)


def domain_data_to_row(domain: str, domain_data: DomainData) -> chain:
    return chain(
        [
            domain,
            list_to_cell(domain_data.emails),
            list_to_cell(domain_data.facebooks),
            list_to_cell(domain_data.twitters),
        ],
        *([product.title, product.image_url] for product in domain_data.products),
    )


def serialize_domain_data(
    domain: str, domain_data: DomainData, writer: AsyncWriter
) -> Coroutine:
    logger.info("Serializing domain data for %s", domain)
    return writer.writerow(domain_data_to_row(domain, domain_data))


async def store_domain_data(domain: str, config: Config, writer: AsyncWriter):
    try:
        await serialize_domain_data(
            domain, await get_domain_data(domain, config), writer
        )
    except Exception as e:
        logger.exception(e)
        raise
