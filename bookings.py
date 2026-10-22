"""Бронирования одного мастера; развитие функций ПР1."""

from datetime import date

from utils import money, positive_int, text


def is_slot_available(booking_date: date, start_hour: int,
                      duration_hours: int, is_busy: bool,
                      today: date | None = None) -> bool:
    """Проверить дату, занятость и рабочие часы с 10:00 до 20:00."""
    if today is None:
        today = date.today()
    return (booking_date >= today and not is_busy
            and type(start_hour) is int and type(duration_hours) is int
            and duration_hours > 0 and start_hour >= 10
            and start_hour + duration_hours <= 20)


def calculate_price(base_price: float, is_student: bool) -> float:
    """Сохранить правило ПР1: студентам скидка 10%."""
    base_price = money(base_price)
    discount = 0.10 if is_student else 0.0
    final_price = round(base_price * (1 - discount), 2)
    return final_price


def get_booking_status(client_name: str, is_available: bool) -> str:
    """Сформировать подтверждение или отказ, как в ПР1."""
    if not client_name.strip():
        return "Запись отклонена: не указано имя клиента."
    if not is_available:
        return "Запись отклонена: выбранное время недоступно."
    return f"Запись подтверждена для клиента {client_name.strip()}."


def is_available(bookings: list[dict], booking_date: date,
                 start_hour: int, duration: int,
                 today: date | None = None) -> bool:
    """Проверить пересечение интервалов всех услуг одного мастера."""
    if not is_slot_available(booking_date, start_hour, duration, False,
                             today):
        return False
    for booking in bookings:
        if booking["status"] != "active":
            continue
        if booking["date"] != booking_date.isoformat():
            continue
        if (start_hour < booking["start_hour"] + booking["duration"]
                and booking["start_hour"] < start_hour + duration):
            return False
    return True


def create_booking(bookings: list[dict], services: dict[int, dict],
                   service_id: int, client_name: str, booking_date: date,
                   start_hour: int, is_student: bool,
                   today: date | None = None) -> dict:
    """Проверить запрос и добавить запись с сохранёнными ценой и временем."""
    positive_int(service_id, "ID услуги")
    if service_id not in services:
        raise ValueError("Услуга не найдена")
    client_name = text(client_name)
    service = services[service_id]
    if not is_available(bookings, booking_date, start_hour,
                        service["duration"], today):
        raise ValueError("Выбранное время недоступно")
    booking = {
        "id": max((b["id"] for b in bookings), default=0) + 1,
        "service_id": service_id, "client_name": client_name,
        "date": booking_date.isoformat(), "start_hour": start_hour,
        "duration": service["duration"], "is_student": is_student,
        "price": calculate_price(service["price"], is_student),
        "status": "active",
    }
    bookings.append(booking)
    return booking


def cancel_booking(bookings: list[dict], booking_id: int) -> None:
    """Отменить запись, сохранив историю и уникальность её ID."""
    for booking in bookings:
        if booking["id"] == booking_id:
            if booking["status"] == "cancelled":
                raise ValueError("Запись уже отменена")
            booking["status"] = "cancelled"
            return
    raise ValueError("Запись не найдена")


def booking_statistics(bookings: list[dict]) -> dict:
    """Посчитать записи, уникальных клиентов и сумму активных записей."""
    active = [b for b in bookings if b["status"] == "active"]
    return {
        "total": len(bookings), "active": len(active),
        "cancelled": len(bookings) - len(active),
        "clients": len({b["client_name"].casefold() for b in active}),
        "amount": round(sum(b["price"] for b in active), 2),
    }
