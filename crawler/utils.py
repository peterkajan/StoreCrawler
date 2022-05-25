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
) -> dict | str:
    async with session.get(url) as response:
        logger.info("Getting page %s, response - %d", url, response.status)
        response.raise_for_status()
        return await response.json() if as_json else await response.text()


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
    urls: list[str],
    session: aiohttp.ClientSession,
    throttle_delay: float,
    as_json=False,
) -> AsyncGenerator[str | dict, None]:
    for url in urls:
        try:
            yield await get_page(url, session, as_json)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            logger.info("Getting page %s failed: %s", url, e)
        # throttle even if the request fails
        await asyncio.sleep(throttle_delay)


def url_to_json_url(url: str) -> str:
    return f"{url.rstrip('/')}.json"


def is_valid_email_domain(email: str) -> bool:
    # FIX ME: here should be more sophisticated check,
    # e.g. by using this lib https://github.com/nexb/python-publicsuffix2
    return not email.endswith(".png") and not email.endswith(".jpg")
