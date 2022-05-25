""" Module containing business logic """
import asyncio
import csv
import logging
import re
from itertools import chain
from typing import cast, Iterable

import aiohttp
from bs4 import BeautifulSoup

from crawler import utils
from crawler.constants import (
    email_re_pattern,
    OUTPUT_HEADER,
    HTTP_TIMEOUT,
    facebook_re_pattern,
    twitter_re_pattern,
    PRODUCT_SELECTORS,
)
from crawler.models import Product, DomainData, is_product_empty, Config

logger = logging.getLogger(__name__)


def read_domains(file_path: str, input_column: str) -> list[str]:
    """
    Read domains from CSV file
    :param file_path: path to file
    :param input_column: header (column name) of column containing domains

    :return: list of domains
    """
    logger.info("Reading domain data from %s", file_path)
    with open(file_path, mode="r") as in_file:
        reader = csv.DictReader(in_file)
        return [row[input_column] for row in reader]


def extract_product_links(page: str, product_count: int) -> list[str]:
    """
    Extract links to products from HTML page

    :param page: HTML page
    :param product_count: Number of product links to be extracted

    :return: list of product links
    """
    soup = BeautifulSoup(page, "html.parser")

    product_link_elements = []
    for selector in PRODUCT_SELECTORS:
        product_link_elements = soup.select(selector)[:product_count]
        # do not try further selectors if some products found
        if product_link_elements:
            break

    return [product_link["href"] for product_link in product_link_elements]


def extract_product_data(product_dict: dict) -> Product:
    """
    Get needed attributes from product json

    :param product_dict: product JSON
    :return: Product model containing needed attributes (or defaults in case that the attribute is not found)
    """
    # be robust, return some default values
    try:
        image_url = product_dict["product"]["images"][0]["src"]
    except (IndexError, KeyError):
        image_url = ""

    return Product(
        title=product_dict.get("product", {}).get("title", ""), image_url=image_url
    )


def get_product_json_urls(page: str, domain: str, product_count: int) -> list[str]:
    """
    Get urls from given page to products' data in json

    :param page: HTML page
    :param domain: domain of the page
    :param product_count: Number of product links to be extracted

    :return: list of URLs to products' JSONs
    """
    return [
        utils.url_to_json_url(utils.convert_to_absolute_url(link, domain))
        for link in extract_product_links(cast(str, page), product_count)
    ]


def normalize(string: str) -> str:
    """Normalize string to be able to identify duplicates."""
    return string.lower()


def extract_emails(string: str) -> set[str]:
    """Extract emails from string. Note that duplicates are removed."""
    return set(
        normalize(match[0])
        for match in email_re_pattern.findall(cast(str, string))
        if utils.is_valid_email_domain(match[0])
    )


async def get_product_data(
    domain: str, config: Config, session: aiohttp.ClientSession
) -> list[Product]:
    """Get products attributes from given domain"""
    product_list_url = utils.get_url(domain, config.product_list_path)
    try:
        product_page = await utils.get_page(product_list_url, session)
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        logger.info("Getting products page %s failed: %s", product_list_url, e)
        return []
    await asyncio.sleep(config.throttle_delay)

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


def extract_by_re_pattern(string: str, re_pattern: re.Pattern) -> set[str]:
    """Extract and deduplicate data from string by given regex"""
    return set(normalize(match[0]) for match in re_pattern.findall(string))


async def get_domain_data(domain: str, config: Config) -> DomainData:
    """
    Get relevant data for given domain.

    :param domain: web domain, e.g. sufio.com
    :param config: configuration object, see model.Config
    :return: relevant data from given domain, see model.Domain
    """
    try:
        logger.info("Getting domain data for %s", domain)
        domain_data = DomainData(domain)
        contact_urls = utils.get_urls(domain, config.contact_paths)
        async with aiohttp.ClientSession(read_timeout=HTTP_TIMEOUT) as session:
            async for page in utils.get_pages(
                contact_urls, session, config.throttle_delay
            ):
                page = cast(str, page)
                domain_data.emails |= extract_emails(page)
                domain_data.facebooks |= extract_by_re_pattern(
                    page, facebook_re_pattern
                )
                domain_data.twitters |= extract_by_re_pattern(page, twitter_re_pattern)

            domain_data.products = await get_product_data(domain, config, session)

        logger.debug("Got domain data for %s: %s", domain, domain_data)
        return domain_data
    except Exception as e:
        logger.exception(e)
        raise


def get_header_row(product_count: int) -> chain[str]:
    """Return header row of output file"""
    return chain(
        OUTPUT_HEADER,
        *([f"title {i}", f"image {i}"] for i in range(1, product_count + 1)),
    )


def iterable_to_cell(iterable: Iterable) -> str:
    return ", ".join(iterable)


def domain_data_to_row(domain_data: DomainData) -> chain:
    return chain(
        [
            domain_data.domain,
            iterable_to_cell(domain_data.emails),
            iterable_to_cell(domain_data.facebooks),
            iterable_to_cell(domain_data.twitters),
        ],
        *([product.title, product.image_url] for product in domain_data.products),
    )


def write_domain_data(
    domain_data_list: list[DomainData], file_path: str, product_count: int
):
    """
    Serialize data to output CSV file

    :param domain_data_list: list of domains' data
    :param file_path: output file path
    :param product_count: number of products to be listed in header
    """
    logger.info("Writing domain data to %s", file_path)
    with open(file_path, "w") as out_file:
        writer = csv.writer(out_file)
        writer.writerow(get_header_row(product_count))
        for domain_data in domain_data_list:
            writer.writerow(domain_data_to_row(domain_data))
