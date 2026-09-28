"""Демонстрационные заказы со вложенной структурой данных."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def dt(year: int, month: int, day: int, hour: int = 12) -> datetime:
    """Создать дату в UTC для тестового набора."""
    return datetime(year, month, day, hour, tzinfo=UTC)


SAMPLE_ORDERS: list[dict[str, Any]] = [
    {
        "order_number": "ORD-2026-001",
        "created_at": dt(2026, 8, 3, 10),
        "status": "delivered",
        "customer": {
            "name": "Анна Петрова",
            "email": "anna@example.com",
            "phone": "+7-900-111-22-33",
            "address": {
                "country": "Россия",
                "city": "Москва",
                "street": "ул. Тверская, 12",
                "postal_code": "125009",
            },
        },
        "items": [
            {
                "product": {
                    "sku": "NB-001",
                    "name": "Ноутбук Orion 14",
                    "category": "Электроника",
                    "brand": "Orion",
                    "attributes": {
                        "memory_gb": 16,
                        "storage_gb": 512,
                        "color": "серый",
                    },
                },
                "quantity": 1,
                "unit_price": 89990.0,
                "discount_percent": 5,
            },
            {
                "product": {
                    "sku": "ACC-101",
                    "name": "Беспроводная мышь",
                    "category": "Аксессуары",
                    "brand": "Click",
                    "attributes": {"color": "чёрный", "connection": "Bluetooth"},
                },
                "quantity": 1,
                "unit_price": 2990.0,
                "discount_percent": 0,
            },
        ],
        "payment": {"method": "card", "currency": "RUB", "transaction_id": "TX-10001"},
        "delivery": {
            "service": "CDEK",
            "tracking_number": "CDEK-900001",
            "estimated_at": dt(2026, 8, 7),
            "delivered_at": dt(2026, 8, 6),
            "address": {"city": "Москва", "pickup_point": "MSK-104"},
        },
        "totals": {
            "subtotal": 92980.0,
            "discount": 4499.5,
            "delivery": 0.0,
            "grand_total": 88480.5,
        },
        "tracking_history": [
            {
                "status": "paid",
                "changed_at": dt(2026, 8, 3, 10),
                "comment": "Оплата получена",
            },
            {
                "status": "shipped",
                "changed_at": dt(2026, 8, 4, 9),
                "comment": "Передан в службу доставки",
            },
            {
                "status": "delivered",
                "changed_at": dt(2026, 8, 6, 15),
                "comment": "Заказ получен",
            },
        ],
    },
    {
        "order_number": "ORD-2026-002",
        "created_at": dt(2026, 8, 8, 14),
        "status": "delivered",
        "customer": {
            "name": "Иван Соколов",
            "email": "ivan@example.com",
            "phone": "+7-921-222-33-44",
            "address": {
                "country": "Россия",
                "city": "Санкт-Петербург",
                "street": "Невский проспект, 35",
                "postal_code": "191025",
            },
        },
        "items": [
            {
                "product": {
                    "sku": "BOOK-201",
                    "name": "Проектирование баз данных",
                    "category": "Книги",
                    "brand": "ТехЛит",
                    "attributes": {"language": "ru", "pages": 640, "cover": "твёрдая"},
                },
                "quantity": 1,
                "unit_price": 2490.0,
                "discount_percent": 10,
            },
            {
                "product": {
                    "sku": "BOOK-202",
                    "name": "Python на практике",
                    "category": "Книги",
                    "brand": "ТехЛит",
                    "attributes": {"language": "ru", "pages": 512, "cover": "мягкая"},
                },
                "quantity": 2,
                "unit_price": 1890.0,
                "discount_percent": 10,
            },
        ],
        "payment": {"method": "sbp", "currency": "RUB", "transaction_id": "TX-10002"},
        "delivery": {
            "service": "Boxberry",
            "tracking_number": "BOX-900002",
            "estimated_at": dt(2026, 8, 12),
            "delivered_at": dt(2026, 8, 13),
            "address": {"city": "Санкт-Петербург", "pickup_point": "SPB-021"},
        },
        "totals": {
            "subtotal": 6270.0,
            "discount": 627.0,
            "delivery": 350.0,
            "grand_total": 5993.0,
        },
        "tracking_history": [
            {
                "status": "paid",
                "changed_at": dt(2026, 8, 8, 14),
                "comment": "Оплата получена",
            },
            {
                "status": "shipped",
                "changed_at": dt(2026, 8, 9, 11),
                "comment": "Заказ отправлен",
            },
            {
                "status": "delivered",
                "changed_at": dt(2026, 8, 13, 18),
                "comment": "Выдан в пункте",
            },
        ],
    },
    {
        "order_number": "ORD-2026-003",
        "created_at": dt(2026, 8, 15, 9),
        "status": "delivered",
        "customer": {
            "name": "Анна Петрова",
            "email": "anna@example.com",
            "phone": "+7-900-111-22-33",
            "address": {
                "country": "Россия",
                "city": "Москва",
                "street": "ул. Тверская, 12",
                "postal_code": "125009",
            },
        },
        "items": [
            {
                "product": {
                    "sku": "HOME-301",
                    "name": "Настольная лампа Luna",
                    "category": "Дом",
                    "brand": "Luna",
                    "attributes": {"color": "белый", "power_w": 12, "dimmable": True},
                },
                "quantity": 2,
                "unit_price": 4590.0,
                "discount_percent": 0,
            }
        ],
        "payment": {"method": "card", "currency": "RUB", "transaction_id": "TX-10003"},
        "delivery": {
            "service": "CDEK",
            "tracking_number": "CDEK-900003",
            "estimated_at": dt(2026, 8, 18),
            "delivered_at": dt(2026, 8, 18),
            "address": {"city": "Москва", "pickup_point": "MSK-104"},
        },
        "totals": {
            "subtotal": 9180.0,
            "discount": 0.0,
            "delivery": 0.0,
            "grand_total": 9180.0,
        },
        "tracking_history": [
            {
                "status": "paid",
                "changed_at": dt(2026, 8, 15, 9),
                "comment": "Оплата получена",
            },
            {
                "status": "delivered",
                "changed_at": dt(2026, 8, 18, 16),
                "comment": "Заказ получен",
            },
        ],
    },
    {
        "order_number": "ORD-2026-004",
        "created_at": dt(2026, 9, 1, 16),
        "status": "shipped",
        "customer": {
            "name": "Мария Орлова",
            "email": "maria@example.com",
            "phone": "+7-903-555-66-77",
            "address": {
                "country": "Россия",
                "city": "Казань",
                "street": "ул. Баумана, 18",
                "postal_code": "420111",
            },
        },
        "items": [
            {
                "product": {
                    "sku": "PHONE-401",
                    "name": "Смартфон Nova X",
                    "category": "Электроника",
                    "brand": "Nova",
                    "attributes": {"memory_gb": 256, "color": "синий", "sim_count": 2},
                },
                "quantity": 1,
                "unit_price": 64990.0,
                "discount_percent": 7,
            }
        ],
        "payment": {"method": "card", "currency": "RUB", "transaction_id": "TX-10004"},
        "delivery": {
            "service": "Russian Post",
            "tracking_number": "RU-900004",
            "estimated_at": dt(2026, 9, 8),
            "delivered_at": None,
            "address": {"city": "Казань", "pickup_point": None},
        },
        "totals": {
            "subtotal": 64990.0,
            "discount": 4549.3,
            "delivery": 490.0,
            "grand_total": 60930.7,
        },
        "tracking_history": [
            {
                "status": "paid",
                "changed_at": dt(2026, 9, 1, 16),
                "comment": "Оплата получена",
            },
            {
                "status": "shipped",
                "changed_at": dt(2026, 9, 2, 10),
                "comment": "Заказ отправлен",
            },
        ],
    },
    {
        "order_number": "ORD-2026-005",
        "created_at": dt(2026, 9, 4, 11),
        "status": "delivered",
        "customer": {
            "name": "Иван Соколов",
            "email": "ivan@example.com",
            "phone": "+7-921-222-33-44",
            "address": {
                "country": "Россия",
                "city": "Санкт-Петербург",
                "street": "Невский проспект, 35",
                "postal_code": "191025",
            },
        },
        "items": [
            {
                "product": {
                    "sku": "ACC-102",
                    "name": "Механическая клавиатура",
                    "category": "Аксессуары",
                    "brand": "Click",
                    "attributes": {
                        "color": "белый",
                        "layout": "RU/EN",
                        "switches": "brown",
                    },
                },
                "quantity": 1,
                "unit_price": 7990.0,
                "discount_percent": 0,
            },
            {
                "product": {
                    "sku": "ACC-103",
                    "name": "Коврик для мыши XL",
                    "category": "Аксессуары",
                    "brand": "Click",
                    "attributes": {
                        "color": "чёрный",
                        "width_cm": 90,
                        "waterproof": True,
                    },
                },
                "quantity": 1,
                "unit_price": 1990.0,
                "discount_percent": 0,
            },
        ],
        "payment": {"method": "cash", "currency": "RUB", "transaction_id": "TX-10005"},
        "delivery": {
            "service": "Courier",
            "tracking_number": "CUR-900005",
            "estimated_at": dt(2026, 9, 6),
            "delivered_at": dt(2026, 9, 6),
            "address": {"city": "Санкт-Петербург", "pickup_point": None},
        },
        "totals": {
            "subtotal": 9980.0,
            "discount": 0.0,
            "delivery": 500.0,
            "grand_total": 10480.0,
        },
        "tracking_history": [
            {
                "status": "paid",
                "changed_at": dt(2026, 9, 4, 11),
                "comment": "Заказ подтверждён",
            },
            {
                "status": "delivered",
                "changed_at": dt(2026, 9, 6, 13),
                "comment": "Передан получателю",
            },
        ],
    },
    {
        "order_number": "ORD-2026-006",
        "created_at": dt(2026, 9, 10, 13),
        "status": "paid",
        "customer": {
            "name": "Олег Власов",
            "email": "oleg@example.com",
            "phone": "+7-917-888-99-00",
            "address": {
                "country": "Россия",
                "city": "Самара",
                "street": "Московское шоссе, 41",
                "postal_code": "443080",
            },
        },
        "items": [
            {
                "product": {
                    "sku": "BOOK-203",
                    "name": "MongoDB для разработчиков",
                    "category": "Книги",
                    "brand": "Data Press",
                    "attributes": {"language": "ru", "pages": 480, "cover": "твёрдая"},
                },
                "quantity": 1,
                "unit_price": 2790.0,
                "discount_percent": 0,
            }
        ],
        "payment": {"method": "sbp", "currency": "RUB", "transaction_id": "TX-10006"},
        "delivery": {
            "service": "Boxberry",
            "tracking_number": "BOX-900006",
            "estimated_at": dt(2026, 9, 15),
            "delivered_at": None,
            "address": {"city": "Самара", "pickup_point": "SAM-012"},
        },
        "totals": {
            "subtotal": 2790.0,
            "discount": 0.0,
            "delivery": 290.0,
            "grand_total": 3080.0,
        },
        "tracking_history": [
            {
                "status": "paid",
                "changed_at": dt(2026, 9, 10, 13),
                "comment": "Оплата получена",
            }
        ],
    },
]
