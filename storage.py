"""JSON-хранилище: проверка данных и атомарная запись одного файла."""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

from utils import money, parse_date, positive_int, text


def load_json(path: Path) -> list[dict]:
    """Прочитать массив JSON; отсутствие файла означает пустые данные."""
    try:
        with path.open(encoding="utf-8") as stream:
            data = json.load(stream)
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, UnicodeError) as error:
        raise ValueError(f"Повреждён JSON: {path.name}") from error
    if not isinstance(data, list):
        raise ValueError(f"{path.name}: ожидается список объектов")
    ids = set()
    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"{path.name}: ожидается объект")
        identifier = positive_int(item.get("id"), "ID")
        if identifier in ids:
            raise ValueError(f"{path.name}: повторяющийся ID")
        ids.add(identifier)
    return data


def save_json(path: Path, data: list[dict]) -> None:
    """Заменить файл только после успешной сериализации и записи."""
    payload = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(mode="w", encoding="utf-8",
                                dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(payload + "\n")
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_services(path: Path) -> dict[int, dict]:
    """Проверить каталог и восстановить целочисленные ключи словаря."""
    services = {}
    names = set()
    for item in load_json(path):
        name = text(item.get("name"), "Название")
        money(item.get("price"))
        positive_int(item.get("duration"), "Длительность")
        if item["duration"] > 10 or name.casefold() in names:
            raise ValueError("Некорректная длительность или дубль услуги")
        names.add(name.casefold())
        services[item["id"]] = {**item, "name": name}
    return services


def load_bookings(path: Path, services: dict[int, dict]) -> list[dict]:
    """Проверить записи, ссылки на услуги и отсутствие конфликтов."""
    bookings = load_json(path)
    for item in bookings:
        positive_int(item.get("service_id"), "ID услуги")
        if item["service_id"] not in services:
            raise ValueError("Запись ссылается на неизвестную услугу")
        text(item.get("client_name"))
        if not isinstance(item.get("date"), str):
            raise ValueError("Отсутствует дата записи")
        parse_date(item["date"])
        positive_int(item.get("start_hour"), "Час начала")
        positive_int(item.get("duration"), "Длительность")
        if (item["start_hour"] < 10
                or item["start_hour"] + item["duration"] > 20):
            raise ValueError("Запись вне рабочих часов")
        money(item.get("price"))
        if type(item.get("is_student")) is not bool:
            raise ValueError("Признак студента должен быть bool")
        if item.get("status") not in ("active", "cancelled"):
            raise ValueError("Неизвестный статус записи")
    active = sorted((b for b in bookings if b["status"] == "active"),
                    key=lambda b: (b["date"], b["start_hour"]))
    for previous, current in zip(active, active[1:]):
        if (previous["date"] == current["date"]
                and previous["start_hour"] + previous["duration"]
                > current["start_hour"]):
            raise ValueError("В файле есть пересекающиеся записи")
    return bookings
