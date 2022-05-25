import asyncio

import aiofiles
from aiocsv import AsyncWriter, AsyncReader

from crawler.constants import (
    DEFAULT_CONTACT_PATHS,
    DEFAULT_PRODUCT_LIST_PATH,
    DEFAULT_PRODUCT_COUNT,
    DEFAULT_THROTTLE_DELAY,
)
from crawler.logic import get_domains_from_reader, store_domain_data, get_header_row
from crawler.models import Config


async def main() -> None:
    # TODO load from arguments
    input_path = "data/stores_small.csv"
    output_path = "data/output.csv"

    config = Config(
        contact_paths=DEFAULT_CONTACT_PATHS,
        product_list_path=DEFAULT_PRODUCT_LIST_PATH,
        product_count=DEFAULT_PRODUCT_COUNT,
        throttle_delay=DEFAULT_THROTTLE_DELAY,
    )
    tasks = []
    async with aiofiles.open(input_path, mode="r") as input_file:
        async with aiofiles.open(output_path, mode="w") as output_file:
            reader = AsyncReader(input_file)
            writer = AsyncWriter(output_file)
            await writer.writerow(get_header_row(config.product_count))
            async for domain in get_domains_from_reader(reader):
                tasks.append(
                    asyncio.create_task(store_domain_data(domain, config, writer))
                )

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
