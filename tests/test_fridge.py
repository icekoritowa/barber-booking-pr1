"""Проверки локального проекта «Холодильник»."""

from datetime import date

import pytest

from fridge.inventory import (add, find, get_amount, get_expired,
                              load_goods, save_goods)


def test_batches_search_and_quantity():
    goods = {}
    add(goods, "Молоко", 1.5, "2030-01-10")
    add(goods, " молоко ", 2, "2030-01-20")
    add(goods, "Яйца", 10)
    assert find(goods, "МОЛ") == ["молоко"]
    assert get_amount(goods, "мол") == 3.5
    assert get_amount(goods, "нет") == 0
    assert get_expired(goods, today=date(2030, 1, 10)) == [("молоко", 1.5)]
    assert get_expired(goods, 10, date(2030, 1, 10)) == [("молоко", 3.5)]


@pytest.mark.parametrize("amount,expiry", [
    (0, None), (-1, None), (float("nan"), None), (float("inf"), None),
    (1, "2030-02-30"), (1, "20300101"),
])
def test_invalid_product(amount, expiry):
    goods = {}
    with pytest.raises(ValueError):
        add(goods, "Молоко", amount, expiry)
    assert goods == {}


def test_fridge_persistence(tmp_path):
    goods = {}
    add(goods, "Молоко", 1.5, "2030-01-10")
    add(goods, "Соль", 1)
    path = tmp_path / "fridge.json"
    save_goods(path, goods)
    assert load_goods(path) == goods
    assert load_goods(tmp_path / "missing.json") == {}
