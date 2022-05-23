import asyncio
import operator
from urllib.parse import urlunparse, ParseResult

import aiohttp
import funcy


def negate(func):
    return funcy.compose(operator.not_, func)


async def get_page(
    url: str, session: aiohttp.ClientSession, as_json=False
) -> dict | str | None:
    try:
        async with session.get(url) as response:
            # TODO 200, logging
            print(f"{url} {response.status}")
            if response.status == 200:
                return await response.json() if as_json else await response.text()
    except aiohttp.ClientConnectorError:
        pass

    return None


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
