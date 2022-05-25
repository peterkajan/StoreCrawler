#!/usr/bin/env python
import argparse
import asyncio
import logging

from crawler.constants import (
    DEFAULT_CONTACT_PATHS,
    DEFAULT_PRODUCT_LIST_PATH,
    DEFAULT_PRODUCT_COUNT,
    DEFAULT_THROTTLE_DELAY,
    DEFAULT_INPUT_COLUMN,
)
from crawler.logic import (
    read_domains,
    get_domain_data,
    write_domain_data,
)
from crawler.models import Config, DomainData

logger = logging.getLogger(__name__)


def setup_argument_parser() -> argparse.ArgumentParser:
    """Setup parsing of script's console arguments"""
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
        "--input-column",
        type=str,
        nargs="?",
        default=DEFAULT_INPUT_COLUMN,
        help=f"Column in input file containing domains (default '{DEFAULT_INPUT_COLUMN}')",
    )
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
    parser.add_argument(
        "--log",
        type=str,
        nargs="?",
        default="INFO",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        help="Log level (default INFO)",
    )
    return parser


def setup_logging(log_level: int) -> None:
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )


async def main() -> None:
    parser = setup_argument_parser()
    args = parser.parse_args()
    setup_logging(logging.getLevelName(args.log))

    config = Config(
        input_column=args.input_column,
        contact_paths=DEFAULT_CONTACT_PATHS,
        product_list_path=DEFAULT_PRODUCT_LIST_PATH,
        product_count=args.product_count,
        throttle_delay=args.throttle,
    )
    logger.info("Starting script with %s", config)

    # read domains from input file
    # file is read synchronously, therefore run it in executor
    loop = asyncio.get_running_loop()
    domains = await loop.run_in_executor(
        None, read_domains, args.in_file, config.input_column
    )

    # concurrently get data for each domain
    tasks = []
    for domain in domains:
        tasks.append(asyncio.create_task(get_domain_data(domain, config)))

    domain_data_list = [
        domain_data
        for domain_data in await asyncio.gather(*tasks, return_exceptions=True)
        if isinstance(domain_data, DomainData)
    ]

    # output data to file
    # writing is done synchronously, therefore run it in executor
    await loop.run_in_executor(
        None, write_domain_data, domain_data_list, args.out_file, config.product_count
    )


if __name__ == "__main__":
    asyncio.run(main())
