import asyncio

import aiofiles

from crawler.constants import (
    DEFAULT_CONTACT_PATHS,
    DEFAULT_PRODUCT_LIST_PATH,
    DEFAULT_PRODUCT_COUNT,
    DEFAULT_THROTTLE_DELAY,
)
from crawler.logic import get_domains_from_stream, store_domain_data
from crawler.models import Config


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


if __name__ == "__main__":
    asyncio.run(main())
