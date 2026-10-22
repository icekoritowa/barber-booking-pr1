"""ПР1: расчёт и подтверждение одной записи в барбершоп."""

from datetime import date


def is_slot_available(booking_date, start_hour, duration_hours, is_busy,
                      today=None):
    """Проверить дату, занятость и часы работы с 10:00 до 20:00."""
    if today is None:
        today = date.today()
    return (booking_date >= today and not is_busy
            and duration_hours > 0 and start_hour >= 10
            and start_hour + duration_hours <= 20)


def calculate_price(base_price, is_student):
    """Рассчитать стоимость в рублях со скидкой студенту 10%."""
    if base_price < 0:
        raise ValueError("Стоимость не может быть отрицательной")
    discount = 0.10 if is_student else 0.0
    final_price = round(base_price * (1 - discount), 2)
    return final_price


def get_booking_status(client_name, is_available):
    """Сформировать результат проверки записи."""
    if not client_name.strip():
        return "Запись отклонена: не указано имя клиента."
    if not is_available:
        return "Запись отклонена: выбранное время недоступно."
    return f"Запись подтверждена для клиента {client_name.strip()}."


def main():
    """Выполнить законченный демонстрационный сценарий."""
    client_name = "Алексей"
    service_name = "Мужская стрижка"
    booking_date = date.today()
    start_hour = int("14")
    duration_hours = 1
    base_price = float("1500.00")
    is_student = True
    is_busy = False

    is_available = is_slot_available(
        booking_date, start_hour, duration_hours, is_busy,
    )
    final_price = calculate_price(base_price, is_student)
    status = get_booking_status(client_name, is_available)

    print("Barber Booking — запись в барбершоп")
    print(f"Услуга: {service_name}")
    print(f"Дата: {booking_date:%d.%m.%Y}")
    print(f"Время: {start_hour}:00–{start_hour + duration_hours}:00")
    print(f"Базовая стоимость: {base_price:.2f} руб.")
    print(f"Стоимость со скидкой: {final_price:.2f} руб.")
    print(status)


if __name__ == "__main__":
    main()
