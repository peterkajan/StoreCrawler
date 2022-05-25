import asyncio
import logging
import operator
from typing import AsyncGenerator, Callable
from urllib.parse import urlunparse, ParseResult, urlparse

import aiohttp
import funcy

logger = logging.getLogger(__name__)


def negate(func: Callable) -> Callable:
    return funcy.compose(operator.not_, func)


async def get_page(
    url: str, session: aiohttp.ClientSession, as_json=False
) -> dict | str | None:
    try:
        async with session.get(url) as response:
            logger.info("Getting page %s, response - %d", url, response.status)
            if response.ok:
                return await response.json() if as_json else await response.text()
    except aiohttp.ClientConnectorError:
        pass

    return None


def get_url(domain: str, path: str, scheme="https") -> str:
    return urlunparse(
        ParseResult(
            scheme=scheme,
            netloc=domain,
            path=path,
            params="",
            query="",
            fragment="",
        )
    )


def convert_to_absolute_url(
    link: str, default_domain: str, default_scheme="https"
) -> str:
    parse_result = urlparse(link, scheme=default_scheme)
    if not parse_result.netloc:
        parse_result = parse_result._replace(netloc=default_domain)
    return urlunparse(parse_result)


def get_urls(domain: str, paths: list[str], scheme="https") -> list[str]:
    return [get_url(domain, path, scheme) for path in paths]


async def get_pages(
    urls: list[str], session: aiohttp.ClientSession, throttle_delay: int, as_json=False
) -> AsyncGenerator[str | dict, None]:
    for url in urls:
        try:
            page = await get_page(url, session, as_json)
            if page:
                yield page
            await asyncio.sleep(throttle_delay)
        except aiohttp.ClientConnectorError:
            pass


def url_to_json_url(url: str) -> str:
    return f"{url.rstrip('/')}.json"
