"""Консольный интерфейс Barber Booking, практическая работа № 2."""

import argparse
from copy import deepcopy
from datetime import date
from pathlib import Path

from bookings import (booking_statistics, calculate_price, cancel_booking,
                      create_booking, get_booking_status, is_available)
from services import add_service, filter_services, find_services, sort_services
from storage import load_bookings, load_services, save_json
from utils import input_bool, input_date, input_int

MENU = """
=== Barber Booking ===
1. Показать услуги
2. Добавить услугу
3. Найти услугу
4. Подобрать услуги по бюджету
5. Отсортировать услуги по цене
6. Проверить доступность
7. Создать запись
8. Отменить запись
9. Показать записи
10. Статистика
11. Демонстрация сценария ПР1
0. Выход
"""


def show_services(services: list[dict]) -> None:
    """Вывести каталог или результат поиска."""
    if not services:
        print("Услуги не найдены.")
    for service in services:
        print(f"#{service['id']} {service['name']}: "
              f"{service['price']:.2f} руб., {service['duration']} ч.")


def show_bookings(bookings: list[dict]) -> None:
    """Показать записи вместе с отменёнными."""
    if not bookings:
        print("Записей нет.")
    for booking in bookings:
        print(f"#{booking['id']} {booking['client_name']}, "
              f"услуга #{booking['service_id']}, {booking['date']} "
              f"{booking['start_hour']}:00, {booking['duration']} ч., "
              f"{booking['price']:.2f} руб., {booking['status']}")


def demo() -> None:
    """Повторить ПР1 на коллекциях без записи в пользовательские файлы."""
    services = {}
    service = add_service(services, "Мужская стрижка", 1500.0, 1)
    booking = create_booking([], services, service["id"], "Алексей",
                             date.today(), 14, True)
    print(f"Стоимость со скидкой: {calculate_price(1500, True):.2f} руб.")
    print(get_booking_status(booking["client_name"], True))


def execute(choice: str, services: dict[int, dict], bookings: list[dict],
            data_dir: Path) -> None:
    """Обработать пункт меню; менять память только после записи на диск."""
    if choice == "1":
        show_services(list(services.values()))
    elif choice == "2":
        name = input("Название: ")
        price = float(input("Стоимость: "))
        duration = input_int("Длительность, часов: ")
        updated = deepcopy(services)
        service = add_service(updated, name, price, duration)
        save_json(data_dir / "services.json", list(updated.values()))
        services.update(updated)
        print(f"Добавлена услуга #{service['id']}.")
    elif choice == "3":
        show_services(find_services(services, input("Поиск: ")))
    elif choice == "4":
        budget = float(input("Бюджет: "))
        show_services(list(filter_services(services, budget)))
    elif choice == "5":
        show_services(sort_services(services))
    elif choice in ("6", "7"):
        service_id = input_int("ID услуги: ")
        if service_id not in services:
            raise ValueError("Услуга не найдена")
        booking_date = input_date("Дата (ГГГГ-ММ-ДД): ")
        hour = input_int("Час начала (10–19): ")
        if choice == "6":
            available = is_available(bookings, booking_date, hour,
                                     services[service_id]["duration"])
            print("Время свободно." if available else "Время недоступно.")
        else:
            client = input("Имя клиента: ")
            student = input_bool("Студент (да/нет): ")
            updated = deepcopy(bookings)
            booking = create_booking(updated, services, service_id, client,
                                     booking_date, hour, student)
            save_json(data_dir / "bookings.json", updated)
            bookings[:] = updated
            print(get_booking_status(client, True))
            print(f"Запись #{booking['id']}: {booking['price']:.2f} руб.")
    elif choice == "8":
        booking_id = input_int("ID записи: ")
        updated = deepcopy(bookings)
        cancel_booking(updated, booking_id)
        save_json(data_dir / "bookings.json", updated)
        bookings[:] = updated
        print("Запись отменена.")
    elif choice == "9":
        show_bookings(bookings)
    elif choice == "10":
        stats = booking_statistics(bookings)
        print(f"Всего: {stats['total']}; активных: {stats['active']}; "
              f"отменено: {stats['cancelled']}; клиентов: {stats['clients']}")
        print(f"Сумма активных записей: {stats['amount']:.2f} руб.")
    elif choice == "11":
        demo()
    else:
        print("Неизвестный пункт меню.")


def main(data_dir: Path | None = None) -> int:
    """Загрузить данные и выполнять меню до выхода или окончания ввода."""
    if data_dir is None:
        data_dir = Path(__file__).resolve().parent / "data"
    try:
        services = load_services(data_dir / "services.json")
        bookings = load_bookings(data_dir / "bookings.json", services)
    except (OSError, ValueError) as error:
        print(f"Не удалось загрузить данные: {error}. Файлы не изменены.")
        return 1
    try:
        while True:
            print(MENU)
            choice = input("Выберите действие: ").strip()
            if choice == "0":
                break
            try:
                execute(choice, services, bookings, data_dir)
            except (ValueError, OSError) as error:
                print(f"Ошибка: {error}. Изменения не сохранены.")
    except (EOFError, KeyboardInterrupt):
        print("\nВвод завершён.")
    print("До свидания!")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path,
                        help="Каталог JSON; по умолчанию data рядом с main.py")
    parser.add_argument("--demo", action="store_true", help="Сценарий ПР1")
    args = parser.parse_args()
    if args.demo:
        demo()
    else:
        raise SystemExit(main(args.data_dir))
