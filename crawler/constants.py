import re

DEFAULT_INPUT_COLUMN = "url"
DEFAULT_CONTACT_PATHS = [
    "/",
    "/pages/about",
    "/pages/about-us",
    "/pages/contact",
    "/pages/contact-us",
]
DEFAULT_PRODUCT_LIST_PATH = "/collections/all"
DEFAULT_PRODUCT_COUNT = 5
DEFAULT_THROTTLE_DELAY = 1  # seconds

HTTP_TIMEOUT = 5  # Timeout of http request for given URL in seconds

# precompiled regexps for extracting data from pages
email_re_pattern = re.compile(r"([\w.-]+@([\w-]+\.)+[\w-]{2,})")
facebook_re_pattern = re.compile(r"((https:\/\/)?(www\.)?facebook\.com\/[\w\.-]+)")
twitter_re_pattern = re.compile(r"((https:\/\/)?(www\.)?twitter\.com\/[\w\.-]+)")

# selectors for extracting the product links
PRODUCT_SELECTORS = [
    "a.grid-product__link",
    ".product-grid-item > a",
    ".product-item > a"
    # TODO add more selectors to cover all known cases
]
OUTPUT_HEADER = ["url", "email", "facebook", "twitter"]
