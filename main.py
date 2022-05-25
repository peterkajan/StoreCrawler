#!/usr/bin/env python
import argparse
import asyncio
import logging

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

logger = logging.getLogger(__name__)


def setup_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extracts relevant data (emails, facebook, product info...) from domains given from input file "
        "and serializes them to CSV output file.\n"
        "Example usage:\n\n"
        "\t./main.py data/stores_small.csv output.csv",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("in_file", type=str, help="Input file")
    parser.add_argument("out_file", type=str, help="Output file")
    parser.add_argument(
        "--product-count",
        type=int,
        nargs="?",
        default=DEFAULT_PRODUCT_COUNT,
        help=f"Number of products to be extracted (default {DEFAULT_PRODUCT_COUNT})",
    )
    parser.add_argument(
        "--throttle",
        type=float,
        nargs="?",
        default=DEFAULT_THROTTLE_DELAY,
        help=f"Delay between requests to the same domain (in seconds, default {DEFAULT_THROTTLE_DELAY})",
    )
    return parser


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )


async def main() -> None:
    setup_logging()
    parser = setup_argument_parser()
    args = parser.parse_args()

    config = Config(
        contact_paths=DEFAULT_CONTACT_PATHS,
        product_list_path=DEFAULT_PRODUCT_LIST_PATH,
        product_count=args.product_count,
        throttle_delay=args.throttle,
    )
    logger.info("Starting script with %s", config)

    tasks = []
    async with aiofiles.open(args.in_file, mode="r") as input_file:
        async with aiofiles.open(args.out_file, mode="w") as output_file:
            reader = AsyncReader(input_file)
            writer = AsyncWriter(output_file)
            await writer.writerow(get_header_row(config.product_count))
            async for domain in get_domains_from_reader(reader):
                tasks.append(
                    asyncio.create_task(store_domain_data(domain, config, writer))
                )

            await asyncio.gather(*tasks, return_exceptions=True)


if __name__ == "__main__":
    asyncio.run(main())
