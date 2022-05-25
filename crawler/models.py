""" Module containing models and model related functions. """
from dataclasses import dataclass, field


@dataclass
class Product:
    """ Model containing relevant Product attributes """

    title: str
    image_url: str


def is_product_empty(product: Product) -> bool:
    return not product.title and not product.image_url


@dataclass
class DomainData:
    """ Model containing relevant Domain data """

    domain: str
    emails: set[str] = field(default_factory=set)
    facebooks: set[str] = field(default_factory=set)
    twitters: set[str] = field(default_factory=set)
    products: list[Product] = field(default_factory=list)


@dataclass
class Config:
    """ Model containing crawler's configurable attributes """

    input_column: str
    contact_paths: list[str]
    product_list_path: str
    product_count: int
    throttle_delay: float
