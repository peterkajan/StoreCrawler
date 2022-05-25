import re

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

email_re_pattern = re.compile(r"([a-zA-Z0-9._-]+@([a-zA-Z0-9_-]+\.)+[a-zA-Z0-9_-]{2,})")

OUTPUT_HEADER = ["url", "email", "facebook", "twitter"]
