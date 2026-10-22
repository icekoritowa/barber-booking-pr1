"""Словарь продуктов и партий с количеством и сроком годности."""

from datetime import date, timedelta
from math import isfinite
from pathlib import Path

from storage import load_json, save_json
from utils import parse_date, text


def add(goods: dict[str, list[dict]], title: str, amount: float,
        expiration_date: str | None = None) -> None:
    """Добавить партию продукта; количество может быть дробным."""
    title = text(title, "Продукт").casefold()
    if (type(amount) not in (int, float) or not isfinite(amount)
            or amount <= 0):
        raise ValueError("Количество должно быть конечным числом больше 0")
    if expiration_date is not None:
        parse_date(expiration_date)
    goods.setdefault(title, []).append({
        "amount": amount, "expiration_date": expiration_date,
    })


def find(goods: dict[str, list[dict]], query: str) -> list[str]:
    """Найти названия по подстроке без учёта регистра."""
    return [title for title in goods if query.strip().casefold() in title]


def get_amount(goods: dict[str, list[dict]], query: str) -> float:
    """Суммировать количество всех партий найденных продуктов."""
    return sum(batch["amount"] for title in find(goods, query)
               for batch in goods[title])


def get_expired(goods: dict[str, list[dict]], in_advance_days: int = 0,
                today: date | None = None) -> list[tuple[str, float]]:
    """Найти партии со сроком до выбранного дня включительно."""
    if type(in_advance_days) is not int or in_advance_days < 0:
        raise ValueError("Количество дней должно быть целым и неотрицательным")
    deadline = (today or date.today()) + timedelta(days=in_advance_days)
    result = []
    for title, batches in goods.items():
        amount = sum(b["amount"] for b in batches
                     if b["expiration_date"] is not None
                     and parse_date(b["expiration_date"]) <= deadline)
        if amount:
            result.append((title, amount))
    return result


def save_goods(path: Path, goods: dict[str, list[dict]]) -> None:
    """Сохранить партии в JSON через атомарное хранилище проекта."""
    rows = []
    for title, batches in goods.items():
        for batch in batches:
            rows.append({"id": len(rows) + 1, "title": title, **batch})
    save_json(path, rows)


def load_goods(path: Path) -> dict[str, list[dict]]:
    """Восстановить словарь продуктов и проверить содержимое файла."""
    goods = {}
    for row in load_json(path):
        add(goods, row.get("title"), row.get("amount"),
            row.get("expiration_date"))
    return goods
