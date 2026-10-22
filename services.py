"""Каталог услуг: добавление, поиск, фильтрация и сортировка."""

from collections.abc import Iterator

from utils import money, positive_int, text


def add_service(services: dict[int, dict], name: str, price: float,
                duration: int) -> dict:
    """Добавить услугу с уникальным ID и длительностью в часах."""
    name = text(name, "Название")
    price = money(price)
    positive_int(duration, "Длительность")
    if duration > 10:
        raise ValueError("Услуга не помещается в рабочий день")
    if any(s["name"].casefold() == name.casefold()
           for s in services.values()):
        raise ValueError("Услуга с таким названием уже существует")
    service_id = max(services, default=0) + 1
    service = {"id": service_id, "name": name, "price": price,
               "duration": duration}
    services[service_id] = service
    return service


def find_services(services: dict[int, dict], query: str) -> list[dict]:
    """Найти услуги по подстроке без учёта регистра."""
    query = query.strip().casefold()
    return [s for s in services.values() if query in s["name"].casefold()]


def filter_services(services: dict[int, dict], budget: float
                    ) -> Iterator[dict]:
    """Постепенно выдавать услуги, укладывающиеся в бюджет."""
    budget = money(budget)
    for service in services.values():
        if service["price"] <= budget:
            yield service


def sort_services(services: dict[int, dict]) -> list[dict]:
    """Вернуть новый список услуг по цене, затем по названию."""
    return sorted(services.values(),
                  key=lambda s: (s["price"], s["name"].casefold()))
