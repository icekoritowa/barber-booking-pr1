"""Проверка значений и безопасный ввод данных из консоли."""

from datetime import date
from math import isfinite


def positive_int(value: int, label: str) -> int:
    """Проверить положительное целое число, исключая bool."""
    if type(value) is not int or value <= 0:
        raise ValueError(f"{label}: требуется положительное целое число")
    return value


def money(value: float) -> float:
    """Проверить конечную неотрицательную стоимость."""
    if type(value) not in (int, float) or not isfinite(value) or value < 0:
        raise ValueError("Стоимость должна быть конечным числом не меньше 0")
    return round(value, 2)


def text(value: str, label: str = "Имя") -> str:
    """Убрать внешние пробелы и запретить пустую строку."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} не может быть пустым")
    return value.strip()


def parse_date(value: str) -> date:
    """Прочитать дату строго в формате ГГГГ-ММ-ДД."""
    result = date.fromisoformat(value)
    if result.isoformat() != value:
        raise ValueError("Дата должна быть в формате ГГГГ-ММ-ДД")
    return result


def input_int(prompt: str) -> int:
    """Повторять ввод до получения целого числа."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Введите целое число.")


def input_date(prompt: str) -> date:
    """Повторять ввод до получения корректной даты."""
    while True:
        try:
            return parse_date(input(prompt).strip())
        except ValueError:
            print("Введите существующую дату в формате ГГГГ-ММ-ДД.")


def input_bool(prompt: str) -> bool:
    """Принять только явный ответ да или нет."""
    while True:
        value = input(prompt).strip().casefold()
        if value in ("да", "д"):
            return True
        if value in ("нет", "н"):
            return False
        print("Введите да или нет.")
