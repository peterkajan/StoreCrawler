import asyncio
import operator
import re
from dataclasses import dataclass, field
from typing import AsyncGenerator, Any
from urllib.parse import urlunparse, ParseResult

import aiofiles
import aiohttp
import funcy
from aiocsv import AsyncReader
from aiofiles.base import AiofilesContextManager
from aiofiles.threadpool.text import AsyncTextIOWrapper

DEFAULT_CONTACT_PATHS = [
    "/",
    "/pages/about",
    "/pages/about-us",
    "/pages/contact",
    "/pages/contact-us",
]
DEFAULT_PRODUCT_LIST_PATH = "/collections/all"
DEFAULT_PRODUCT_COUNT = 5
DEFAULT_THROTTLE_DELAY = 5

email_re_pattern = re.compile(r"([a-zA-Z0-9._-]+@([a-zA-Z0-9_-]+\.)+[a-zA-Z0-9_-]+)")


async def get_domains_from_stream(
    input_stream: AsyncTextIOWrapper,
) -> AsyncGenerator[str, None]:
    async for row in AsyncReader(input_stream):
        yield row[0]


@dataclass
class Product:
    title: str
    image_url: str


def is_product_empty(product: Product) -> bool:
    return not product.title and not product.image_url


@dataclass
class DomainData:
    emails: list[str] = field(default_factory=list)
    facebooks: list[str] = field(default_factory=list)
    twitters: list[str] = field(default_factory=list)
    products: list[Product] = field(default_factory=list)


@dataclass
class Config:
    contact_paths: list[str]
    product_list_path: str
    product_count: int
    throttle_delay: int


def negate(func):
    return funcy.compose(operator.not_, func)


async def get_page(url: str, session: aiohttp.ClientSession, as_json=False):
    try:
        async with session.get(url) as response:
            # TODO 200, logging
            print(f"{url} {response.status}")
            if response.status == 200:
                return await response.json() if as_json else await response.text()
    except aiohttp.ClientConnectorError:
        pass


def get_urls(domain, paths):
    return [
        urlunparse(
            ParseResult(
                scheme="https",
                netloc=domain,
                path=path,
                params="",
                query="",
                fragment="",
            )
        )
        for path in paths
    ]


async def get_pages(urls: list[str], throttle_delay: int, as_json=False):
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                page = await get_page(url, session, as_json)
                if page:
                    yield page
                await asyncio.sleep(throttle_delay)
            except aiohttp.ClientConnectorError:
                pass


def extract_product_links(page, product_count):
    # TODO
    return []


def extract_product_data(product_json) -> Product:
    # be robust, return some default values
    try:
        image_url = product_json["images"][0]
    except (IndexError, AttributeError):

        image_url = ""
    return Product(title=product_json.get("title", ""), image_url=image_url)


async def get_domain_data(domain, config):
    domain_data = DomainData()
    contact_urls = get_urls(domain, config.contact_paths)
    async for page in get_pages(contact_urls, config.throttle_delay):
        domain_data.emails = [match[0] for match in email_re_pattern.findall(page)]
        # TODO twitter, facebook

    product_page = await get_page(domain, config.product_list_path)
    if product_page:
        product_links = extract_product_links(product_page, config.product_count)

        domain_data.products = filter(
            negate(is_product_empty),
            [
                extract_product_data(product_json)
                async for product_json in get_pages(
                    product_links, config.throttle_delay, as_json=True
                )
            ],
        )

    return domain_data


async def serialize_domain_data(domain_data):
    # TODO
    print(domain_data)


async def store_domain_data(domain: str, config: Config):
    return serialize_domain_data(await get_domain_data(domain, config))


async def main() -> None:
    # TODO load from arguments
    input_path = "data/stores_small.csv"
    config = Config(
        contact_paths=DEFAULT_CONTACT_PATHS,
        product_list_path=DEFAULT_PRODUCT_LIST_PATH,
        product_count=DEFAULT_PRODUCT_COUNT,
        throttle_delay=DEFAULT_THROTTLE_DELAY,
    )
    tasks = []
    async with aiofiles.open(input_path, mode="r") as input_file:
        async for domain in get_domains_from_stream(input_file):
            tasks.append(asyncio.create_task(store_domain_data(domain, config)))

    await asyncio.gather(*tasks)


asyncio.run(main())
