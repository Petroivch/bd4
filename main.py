"""Заполнение коллекции, демонстрация CRUD и аналитических запросов."""

from __future__ import annotations

from datetime import UTC, datetime
from pprint import pprint
from typing import Any

from pymongo.errors import PyMongoError

from config import get_client, get_database
from order_repository import OrderRepository, OrderRepositoryError
from sample_data import SAMPLE_ORDERS


def find_index_names(value: Any) -> set[str]:
    """Рекурсивно извлечь названия использованных индексов из explain."""
    found: set[str] = set()
    if isinstance(value, dict):
        index_name = value.get("indexName")
        if isinstance(index_name, str):
            found.add(index_name)
        for nested in value.values():
            found.update(find_index_names(nested))
    elif isinstance(value, list):
        for nested in value:
            found.update(find_index_names(nested))
    return found


def run_demo() -> None:
    """Выполнить все части домашнего задания."""
    with get_client() as client:
        repository = OrderRepository(get_database(client))

        print("СОЗДАННЫЕ ИНДЕКСЫ:")
        pprint(repository.create_indexes())

        processed = repository.seed(SAMPLE_ORDERS)
        print(f"\nНАПОЛНЕНИЕ: обработано заказов — {processed}")

        order = repository.get_by_number("ORD-2026-001")
        print("\nПОИСК ПО НОМЕРУ:")
        pprint(
            {
                "order_number": order["order_number"],
                "customer": order["customer"]["name"],
                "items_count": len(order["items"]),
            }
            if order
            else None
        )

        print("\nЗАКАЗЫ ПОКУПАТЕЛЯ:")
        pprint(
            [
                item["order_number"]
                for item in repository.find_by_customer("anna@example.com")
            ]
        )

        print("\nПРОДАЖИ ПО КАТЕГОРИЯМ:")
        pprint(repository.sales_by_category())

        print("\nЛУЧШИЕ ПОКУПАТЕЛИ:")
        pprint(repository.top_customers())

        print("\nПОПУЛЯРНЫЕ АКСЕССУАРЫ:")
        pprint(repository.popular_products("Аксессуары"))

        print("\nСТАТИСТИКА ДОСТАВКИ:")
        pprint(repository.delivery_statistics())

        used_indexes = find_index_names(repository.explain_status_aggregation())
        print("\nИНДЕКСЫ В ПЛАНЕ АГРЕГАЦИИ:", sorted(used_indexes))

        # Временный документ показывает операции создания, обновления и удаления.
        demo_order = dict(SAMPLE_ORDERS[-1])
        demo_order["order_number"] = "ORD-DEMO-CRUD"
        demo_order["delivery"] = dict(demo_order["delivery"])
        demo_order["delivery"]["tracking_number"] = "DEMO-TRACKING-001"
        repository.collection.delete_one({"order_number": demo_order["order_number"]})
        repository.create(demo_order)
        repository.update_status(
            demo_order["order_number"],
            "shipped",
            datetime.now(UTC),
            "Демонстрация обновления",
        )
        updated = repository.get_by_number(demo_order["order_number"])
        print(
            "\nCRUD: статус после обновления —", updated["status"] if updated else None
        )
        repository.delete(demo_order["order_number"])
        print(
            "CRUD: документ после удаления —",
            repository.get_by_number(demo_order["order_number"]),
        )


if __name__ == "__main__":
    try:
        run_demo()
    except (OrderRepositoryError, PyMongoError) as error:
        print(f"Ошибка: {error}")
        raise SystemExit(1) from error
