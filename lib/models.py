## lib/models.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    email: str
    password: str  # plain by request
    role: str      # 'admin' | 'customer'

@dataclass
class Product:
    id: int
    name: str
    category: str
    price: float
    currency: str
    stock: int
    image_url: str
    active: bool