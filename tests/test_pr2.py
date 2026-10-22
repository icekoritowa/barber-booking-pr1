"""Проверки ПР2: коллекции, интервалы, JSON и все пункты меню."""

from copy import deepcopy
from datetime import date, timedelta
import json
from pathlib import Path

import pytest

from bookings import (booking_statistics, cancel_booking, create_booking,
                      is_available)
from main import main
from services import add_service, filter_services, find_services, sort_services
from storage import load_bookings, load_json, load_services, save_json

DAY = date(2030, 1, 10)


@pytest.fixture
def services():
    """Каталог с короткой и длинной услугой."""
    result = {}
    add_service(result, "Стрижка", 1500, 1)
    add_service(result, "Комплекс", 2200, 2)
    return result


def test_add_search_sort_filter(services):
    add_service(services, "Борода", 900, 1)
    assert find_services(services, "СТРИ") == [services[1]]
    assert find_services(services, "нет") == []
    assert [s["id"] for s in sort_services(services)] == [3, 1, 2]
    assert [s["id"] for s in filter_services(services, 1500)] == [1, 3]
    assert list(services) == [1, 2, 3]


@pytest.mark.parametrize("name,price,duration", [
    ("", 1, 1), ("Стрижка", 1, 1), ("X", -1, 1),
    ("X", float("nan"), 1), ("X", float("inf"), 1),
    ("X", 1, 0), ("X", 1, 11), ("X", 1, True),
])
def test_invalid_service_does_not_mutate(services, name, price, duration):
    before = deepcopy(services)
    with pytest.raises(ValueError):
        add_service(services, name, price, duration)
    assert services == before


def test_booking_discount_and_overlap(services):
    bookings = []
    booking = create_booking(bookings, services, 2, "Анна", DAY, 12, True,
                             today=DAY)
    assert booking["price"] == 1980
    for hour, duration in ((11, 2), (12, 1), (13, 2), (10, 6)):
        assert not is_available(bookings, DAY, hour, duration, DAY)
    assert is_available(bookings, DAY, 10, 2, DAY)
    assert is_available(bookings, DAY, 14, 2, DAY)
    assert is_available(bookings, DAY + timedelta(days=1), 12, 2, DAY)
    with pytest.raises(ValueError, match="недоступно"):
        create_booking(bookings, services, 1, "Борис", DAY, 13, False, DAY)
    assert len(bookings) == 1


def test_cancel_frees_time_preserves_ids(services):
    bookings = []
    create_booking(bookings, services, 1, "Анна", DAY, 12, True, DAY)
    cancel_booking(bookings, 1)
    assert is_available(bookings, DAY, 12, 1, DAY)
    second = create_booking(bookings, services, 1, "Анна", DAY, 12,
                            False, DAY)
    assert second["id"] == 2
    with pytest.raises(ValueError, match="уже отменена"):
        cancel_booking(bookings, 1)
    with pytest.raises(ValueError, match="не найдена"):
        cancel_booking(bookings, 99)
    assert booking_statistics(bookings) == {
        "total": 2, "active": 1, "cancelled": 1, "clients": 1,
        "amount": 1500,
    }


@pytest.mark.parametrize("service_id,name,day,hour", [
    (99, "Анна", DAY, 12), (1, " ", DAY, 12),
    (1, "Анна", DAY - timedelta(days=1), 12),
    (2, "Анна", DAY, 19), (1, "Анна", DAY, 9),
])
def test_invalid_booking(services, service_id, name, day, hour):
    bookings = []
    with pytest.raises(ValueError):
        create_booking(bookings, services, service_id, name, day,
                       hour, False, DAY)
    assert bookings == []


def test_json_round_trip(tmp_path, services):
    bookings = []
    create_booking(bookings, services, 1, "Анна", DAY, 12, True, DAY)
    save_json(tmp_path / "services.json", list(services.values()))
    save_json(tmp_path / "bookings.json", bookings)
    restored = load_services(tmp_path / "services.json")
    assert restored == services
    assert load_bookings(tmp_path / "bookings.json", restored) == bookings
    assert load_json(tmp_path / "missing.json") == []


@pytest.mark.parametrize("payload", [
    "{", "{}", "[1]", '[{"id":1},{"id":1}]', '[{"id":true}]',
    '[{"id":1,"name":"X","price":-1,"duration":1}]',
])
def test_corrupt_catalog_is_rejected(tmp_path, payload):
    path = tmp_path / "services.json"
    path.write_text(payload)
    with pytest.raises(ValueError):
        load_services(path)
    assert path.read_text() == payload


def test_corrupt_booking_schema(tmp_path, services):
    rows = []
    create_booking(rows, services, 1, "Анна", DAY, 12, False, DAY)
    for key, value in (("service_id", 99), ("date", "2030-02-30"),
                       ("price", -1), ("status", "unknown"),
                       ("start_hour", 20), ("client_name", None)):
        changed = deepcopy(rows)
        changed[0][key] = value
        save_json(tmp_path / "bookings.json", changed)
        with pytest.raises(ValueError):
            load_bookings(tmp_path / "bookings.json", services)
    rows.append({**rows[0], "id": 2})
    save_json(tmp_path / "bookings.json", rows)
    with pytest.raises(ValueError, match="пересекающиеся"):
        load_bookings(tmp_path / "bookings.json", services)


def test_atomic_save_failure_keeps_previous_data(tmp_path, monkeypatch):
    path = tmp_path / "data.json"
    save_json(path, [{"id": 1}])

    def fail_replace(self, target):
        raise PermissionError("read-only")

    monkeypatch.setattr(Path, "replace", fail_replace)
    with pytest.raises(PermissionError):
        save_json(path, [{"id": 2}])
    assert load_json(path) == [{"id": 1}]
    assert list(tmp_path.iterdir()) == [path]


def test_all_menu_items_and_restart(tmp_path, monkeypatch, capsys, services):
    save_json(tmp_path / "services.json", list(services.values()))
    day = (date.today() + timedelta(days=1)).isoformat()
    answers = iter([
        "1", "2", "Борода", "900", "1", "3", "стриж", "4", "1500",
        "5", "6", "1", day, "12", "7", "1", day, "12", "Анна", "да",
        "6", "1", day, "12", "9", "10", "8", "1", "11", "0",
    ])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert main(tmp_path) == 0
    output = capsys.readouterr().out
    for expected in ("Добавлена услуга #3", "Время свободно",
                     "Время недоступно", "1350.00", "Анна", "active",
                     "Всего: 1", "Запись отменена", "Алексей"):
        assert expected in output
    assert len(load_services(tmp_path / "services.json")) == 3
    answers = iter(["9", "0"])
    assert main(tmp_path) == 0
    assert "cancelled" in capsys.readouterr().out


def test_bad_input_retries_and_unknown_option(tmp_path, monkeypatch, capsys,
                                              services):
    save_json(tmp_path / "services.json", list(services.values()))
    answers = iter(["???", "7", "bad", "1", "bad", "2026-02-30",
                    date.today().isoformat(), "14", "Анна", "?", "нет",
                    "2", "X", "nan", "1", "0"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert main(tmp_path) == 0
    output = capsys.readouterr().out
    for expected in ("Неизвестный пункт", "Введите целое", "существующую",
                     "Введите да или нет", "Ошибка:"):
        assert expected in output
    assert len(load_services(tmp_path / "services.json")) == 2


def test_file_error_does_not_change_memory(tmp_path, monkeypatch, services):
    from main import execute

    answers = iter(["X", "1", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    def fail_save(*args):
        raise PermissionError("read-only")

    monkeypatch.setattr("main.save_json", fail_save)
    with pytest.raises(PermissionError):
        execute("2", services, [], tmp_path)
    assert len(services) == 2


def test_bad_file_exits_without_overwrite(tmp_path, capsys):
    path = tmp_path / "services.json"
    path.write_text("not JSON")
    assert main(tmp_path) == 1
    assert path.read_text() == "not JSON"
    assert "Файлы не изменены" in capsys.readouterr().out


def test_eof_is_clean_exit(tmp_path, monkeypatch):
    def eof(prompt):
        raise EOFError

    monkeypatch.setattr("builtins.input", eof)
    assert main(tmp_path) == 0


def test_fixture_files_are_valid():
    root = Path(__file__).resolve().parents[1] / "data"
    services = load_services(root / "services.json")
    load_bookings(root / "bookings.json", services)
    assert json.loads((root / "bookings.json").read_text()) == []
