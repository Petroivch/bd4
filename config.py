"""Настройка подключения к MongoDB."""

from __future__ import annotations

import os

from pymongo import MongoClient
from pymongo.database import Database


DEFAULT_MONGODB_URI = "mongodb://localhost:27017"
DEFAULT_DATABASE_NAME = "online_store"


def get_client(uri: str | None = None) -> MongoClient:
    """Создать клиент MongoDB и проверить доступность сервера."""
    client = MongoClient(
        uri or os.getenv("MONGODB_URI", DEFAULT_MONGODB_URI),
        serverSelectionTimeoutMS=5_000,
    )
    client.admin.command("ping")
    return client


def get_database(client: MongoClient) -> Database:
    """Получить базу данных приложения."""
    database_name = os.getenv("MONGODB_DATABASE", DEFAULT_DATABASE_NAME)
    return client[database_name]
