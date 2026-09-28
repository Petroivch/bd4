# Домашнее задание по MongoDB и PyMongo

Проект демонстрирует работу с MongoDB через официальную библиотеку PyMongo на
примере коллекции заказов интернет-магазина.

## Что реализовано

- коллекция `orders` со сложными вложенными документами;
- данные покупателя и адрес, массив товаров с характеристиками, оплата,
  доставка и история изменения статуса;
- идемпотентное наполнение коллекции демонстрационными данными;
- пять индексов для поиска и аналитики;
- специализированный класс `OrderRepository` с CRUD-методами;
- атомарное обновление статуса заказа и истории через `$set` и `$push`;
- четыре аналитических aggregation pipeline;
- проверка фактического использования индекса через `explain`.

## Структура документа

Сокращённый пример одного заказа:

```javascript
{
  order_number: "ORD-2026-001",
  status: "delivered",
  customer: {
    name: "Анна Петрова",
    email: "anna@example.com",
    address: { country: "Россия", city: "Москва", street: "..." }
  },
  items: [
    {
      product: {
        sku: "NB-001",
        name: "Ноутбук Orion 14",
        category: "Электроника",
        attributes: { memory_gb: 16, storage_gb: 512, color: "серый" }
      },
      quantity: 1,
      unit_price: 89990,
      discount_percent: 5
    }
  ],
  payment: { method: "card", currency: "RUB", transaction_id: "TX-10001" },
  delivery: {
    service: "CDEK",
    tracking_number: "CDEK-900001",
    estimated_at: ISODate("2026-08-07T12:00:00Z"),
    delivered_at: ISODate("2026-08-06T12:00:00Z")
  },
  totals: { subtotal: 92980, discount: 4499.5, delivery: 0, grand_total: 88480.5 },
  tracking_history: [
    { status: "paid", changed_at: ISODate("2026-08-03T10:00:00Z") }
  ]
}
```

## Индексы

Метод `create_indexes()` создаёт:

| Индекс | Поля | Назначение |
|---|---|---|
| `uq_order_number` | `order_number` | быстрый поиск заказа, уникальность номера |
| `idx_customer_email_created_at` | `customer.email`, `created_at DESC` | история заказов покупателя |
| `idx_status_created_at` | `status`, `created_at DESC` | выборка и аналитика по статусу и периоду |
| `idx_category_created_at` | `items.product.category`, `created_at DESC` | аналитика по категории товара |
| `uq_tracking_number` | `delivery.tracking_number` | поиск отправления, уникальность трек-номера |

Начальные стадии `$match` в аналитических запросах соответствуют составным
индексам. Метод `explain_status_aggregation()` позволяет проверить план
выполнения; демонстрационный запуск выводит имя выбранного индекса.

## Аналитические запросы

- `sales_by_category()` — количество товаров, заказов, выручка и средняя цена
  по категориям;
- `top_customers()` — рейтинг покупателей по сумме завершённых заказов;
- `popular_products()` — наиболее продаваемые товары выбранной категории;
- `delivery_statistics()` — среднее отклонение от плановой даты и количество
  опозданий по городам.

В запросах используются стадии `$match`, `$unwind`, `$set`, `$group`,
`$project`, `$sort` и `$limit`, а также операторы `$dateDiff`, `$round`,
`$addToSet` и `$cond`.

## Запуск MongoDB

Если MongoDB не установлена локально, запустите контейнер:

```powershell
docker compose up -d
```

## Подготовка Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

По умолчанию проект использует:

```text
mongodb://localhost:27017
```

Для другого подключения задайте переменные окружения:

```powershell
$env:MONGODB_URI="mongodb://USER:PASSWORD@HOST:PORT"
$env:MONGODB_DATABASE="online_store"
```

## Демонстрация

```powershell
python main.py
```

Скрипт создаёт индексы, наполняет коллекцию, выполняет поиск, CRUD и все
аналитические запросы. Повторный запуск безопасен: исходные заказы обновляются
по уникальному полю `order_number`, поэтому дубликаты не создаются.
