from dataclasses import dataclass, field


@dataclass
class Product:
    title: str
    image_url: str


def is_product_empty(product: Product) -> bool:
    return not product.title and not product.image_url


@dataclass
class DomainData:
    emails: list[str] = field(default_factory=list)
    facebooks: list[str] = field(default_factory=list)
    twitters: list[str] = field(default_factory=list)
    products: list[Product] = field(default_factory=list)


@dataclass
class Config:
    contact_paths: list[str]
    product_list_path: str
    product_count: int
    throttle_delay: int
