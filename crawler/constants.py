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
DEFAULT_THROTTLE_DELAY = 5

email_re_pattern = re.compile(r"([a-zA-Z0-9._-]+@([a-zA-Z0-9_-]+\.)+[a-zA-Z0-9_-]+)")
