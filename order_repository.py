"""Специализированный класс для работы с коллекцией заказов."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import Any

from pymongo import ASCENDING, DESCENDING, IndexModel
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.results import DeleteResult, InsertOneResult, UpdateResult


class OrderRepositoryError(RuntimeError):
    """Ошибка операции с коллекцией заказов."""


class OrderNotFoundError(OrderRepositoryError):
    """Заказ с указанным номером не найден."""


class OrderRepository:
    """CRUD, индексы и аналитика для коллекции ``orders``."""

    def __init__(self, database: Database) -> None:
        self.collection: Collection = database["orders"]

    def create_indexes(self) -> list[str]:
        """Создать индексы под основные операции и аналитические запросы."""
        indexes = [
            IndexModel(
                [("order_number", ASCENDING)],
                name="uq_order_number",
                unique=True,
            ),
            IndexModel(
                [("customer.email", ASCENDING), ("created_at", DESCENDING)],
                name="idx_customer_email_created_at",
            ),
            IndexModel(
                [("status", ASCENDING), ("created_at", DESCENDING)],
                name="idx_status_created_at",
            ),
            IndexModel(
                [("items.product.category", ASCENDING), ("created_at", DESCENDING)],
                name="idx_category_created_at",
            ),
            IndexModel(
                [("delivery.tracking_number", ASCENDING)],
                name="uq_tracking_number",
                unique=True,
                sparse=True,
            ),
        ]
        return self.collection.create_indexes(indexes)

    def seed(self, orders: Iterable[Mapping[str, Any]]) -> int:
        """Идемпотентно загрузить набор заказов по полю order_number."""
        processed = 0
        try:
            for order in orders:
                self.collection.replace_one(
                    {"order_number": order["order_number"]},
                    dict(order),
                    upsert=True,
                )
                processed += 1
        except PyMongoError as error:
            raise OrderRepositoryError(
                f"Не удалось наполнить коллекцию: {error}"
            ) from error
        return processed

    def create(self, order: Mapping[str, Any]) -> InsertOneResult:
        """Добавить новый заказ."""
        try:
            return self.collection.insert_one(dict(order))
        except DuplicateKeyError as error:
            raise OrderRepositoryError(
                "Заказ с таким номером уже существует"
            ) from error
        except PyMongoError as error:
            raise OrderRepositoryError(f"Не удалось создать заказ: {error}") from error

    def get_by_number(self, order_number: str) -> dict[str, Any] | None:
        """Найти заказ по уникальному номеру."""
        return self.collection.find_one({"order_number": order_number})

    def find_by_customer(self, email: str, *, limit: int = 20) -> list[dict[str, Any]]:
        """Получить последние заказы покупателя."""
        cursor = (
            self.collection.find({"customer.email": email})
            .sort("created_at", DESCENDING)
            .limit(limit)
        )
        return list(cursor)

    def find_by_status(
        self,
        status: str,
        *,
        created_from: datetime | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """Получить заказы в заданном статусе за период."""
        query: dict[str, Any] = {"status": status}
        if created_from is not None:
            query["created_at"] = {"$gte": created_from}
        cursor = self.collection.find(query).sort("created_at", DESCENDING).limit(limit)
        return list(cursor)

    def update_status(
        self,
        order_number: str,
        new_status: str,
        changed_at: datetime,
        comment: str,
    ) -> UpdateResult:
        """Изменить статус и атомарно дописать событие в историю."""
        try:
            result = self.collection.update_one(
                {"order_number": order_number},
                {
                    "$set": {"status": new_status},
                    "$push": {
                        "tracking_history": {
                            "status": new_status,
                            "changed_at": changed_at,
                            "comment": comment,
                        }
                    },
                },
            )
        except PyMongoError as error:
            raise OrderRepositoryError(
                f"Не удалось обновить статус: {error}"
            ) from error
        if result.matched_count == 0:
            raise OrderNotFoundError(f"Заказ {order_number} не найден")
        return result

    def delete(self, order_number: str) -> DeleteResult:
        """Удалить заказ по номеру."""
        try:
            result = self.collection.delete_one({"order_number": order_number})
        except PyMongoError as error:
            raise OrderRepositoryError(f"Не удалось удалить заказ: {error}") from error
        if result.deleted_count == 0:
            raise OrderNotFoundError(f"Заказ {order_number} не найден")
        return result

    @staticmethod
    def _period_match(
        status: str,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> dict[str, Any]:
        match: dict[str, Any] = {"status": status}
        if date_from is not None or date_to is not None:
            created_at: dict[str, datetime] = {}
            if date_from is not None:
                created_at["$gte"] = date_from
            if date_to is not None:
                created_at["$lt"] = date_to
            match["created_at"] = created_at
        return match

    def sales_by_category(
        self,
        *,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict[str, Any]]:
        """Посчитать продажи, выручку и среднюю цену по категориям."""
        pipeline = [
            {"$match": self._period_match("delivered", date_from, date_to)},
            {"$unwind": "$items"},
            {
                "$set": {
                    "line_revenue": {
                        "$multiply": [
                            "$items.unit_price",
                            "$items.quantity",
                            {
                                "$subtract": [
                                    1,
                                    {"$divide": ["$items.discount_percent", 100]},
                                ]
                            },
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": "$items.product.category",
                    "units_sold": {"$sum": "$items.quantity"},
                    "revenue": {"$sum": "$line_revenue"},
                    "average_unit_price": {"$avg": "$items.unit_price"},
                    "orders": {"$addToSet": "$order_number"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "category": "$_id",
                    "units_sold": 1,
                    "orders_count": {"$size": "$orders"},
                    "revenue": {"$round": ["$revenue", 2]},
                    "average_unit_price": {"$round": ["$average_unit_price", 2]},
                }
            },
            {"$sort": {"revenue": -1}},
        ]
        return list(self.collection.aggregate(pipeline))

    def top_customers(self, *, limit: int = 5) -> list[dict[str, Any]]:
        """Найти покупателей с наибольшей суммой завершённых заказов."""
        pipeline = [
            {"$match": {"status": "delivered"}},
            {
                "$group": {
                    "_id": "$customer.email",
                    "name": {"$first": "$customer.name"},
                    "city": {"$first": "$customer.address.city"},
                    "orders_count": {"$sum": 1},
                    "total_spent": {"$sum": "$totals.grand_total"},
                    "average_order": {"$avg": "$totals.grand_total"},
                }
            },
            {"$sort": {"total_spent": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "email": "$_id",
                    "name": 1,
                    "city": 1,
                    "orders_count": 1,
                    "total_spent": {"$round": ["$total_spent", 2]},
                    "average_order": {"$round": ["$average_order", 2]},
                }
            },
        ]
        return list(self.collection.aggregate(pipeline))

    def popular_products(
        self, category: str, *, limit: int = 5
    ) -> list[dict[str, Any]]:
        """Найти самые продаваемые товары выбранной категории."""
        pipeline = [
            {
                "$match": {
                    "items.product.category": category,
                    "status": "delivered",
                }
            },
            {"$unwind": "$items"},
            {"$match": {"items.product.category": category}},
            {
                "$group": {
                    "_id": {
                        "sku": "$items.product.sku",
                        "name": "$items.product.name",
                    },
                    "units_sold": {"$sum": "$items.quantity"},
                    "orders_count": {"$sum": 1},
                }
            },
            {"$sort": {"units_sold": -1, "orders_count": -1}},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "sku": "$_id.sku",
                    "name": "$_id.name",
                    "units_sold": 1,
                    "orders_count": 1,
                }
            },
        ]
        return list(self.collection.aggregate(pipeline))

    def delivery_statistics(self) -> list[dict[str, Any]]:
        """Рассчитать среднее отклонение от срока доставки по городам."""
        pipeline = [
            {
                "$match": {
                    "status": "delivered",
                    "delivery.delivered_at": {"$ne": None},
                }
            },
            {
                "$set": {
                    "delay_days": {
                        "$dateDiff": {
                            "startDate": "$delivery.estimated_at",
                            "endDate": "$delivery.delivered_at",
                            "unit": "day",
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$delivery.address.city",
                    "deliveries_count": {"$sum": 1},
                    "average_delay_days": {"$avg": "$delay_days"},
                    "late_deliveries": {
                        "$sum": {"$cond": [{"$gt": ["$delay_days", 0]}, 1, 0]}
                    },
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "city": "$_id",
                    "deliveries_count": 1,
                    "late_deliveries": 1,
                    "average_delay_days": {"$round": ["$average_delay_days", 2]},
                }
            },
            {"$sort": {"average_delay_days": -1}},
        ]
        return list(self.collection.aggregate(pipeline))

    def explain_status_aggregation(self) -> dict[str, Any]:
        """Вернуть план выполнения аналитики по статусу для проверки индекса."""
        command = {
            "aggregate": self.collection.name,
            "pipeline": [
                {"$match": {"status": "delivered"}},
                {"$group": {"_id": "$customer.address.city", "orders": {"$sum": 1}}},
            ],
            "cursor": {},
        }
        return self.collection.database.command(
            "explain",
            command,
            verbosity="executionStats",
        )
