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

HTTP_TIMEOUT = 5  # seconds

email_re_pattern = re.compile(r"([\w.-]+@([\w-]+\.)+[\w-]{2,})")
facebook_re_pattern = re.compile(r"((https:\/\/)?(www\.)?facebook\.com\/[\w\.-]+)")
twitter_re_pattern = re.compile(r"((https:\/\/)?(www\.)?twitter\.com\/[\w\.-]+)")

OUTPUT_HEADER = ["url", "email", "facebook", "twitter"]
