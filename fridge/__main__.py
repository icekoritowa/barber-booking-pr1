"""Запуск: python -m fridge --help."""

import argparse
from pathlib import Path

from fridge.inventory import add, find, get_expired, load_goods, save_goods


def main() -> int:
    """Добавить продукт или показать содержимое JSON-холодильника."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=Path(__file__).resolve()
                        .parents[1] / "data" / "fridge.json")
    commands = parser.add_subparsers(dest="command", required=True)
    adding = commands.add_parser("add", help="Добавить партию")
    adding.add_argument("title")
    adding.add_argument("amount", type=float)
    adding.add_argument("--expires", help="Срок годности ГГГГ-ММ-ДД")
    listing = commands.add_parser("list", help="Показать партии")
    listing.add_argument("--query", default="")
    expired = commands.add_parser("expired", help="Истекающие сроки")
    expired.add_argument("--days", type=int, default=0)
    args = parser.parse_args()
    try:
        goods = load_goods(args.file)
        if args.command == "add":
            add(goods, args.title, args.amount, args.expires)
            save_goods(args.file, goods)
            print("Продукт добавлен.")
        elif args.command == "list":
            titles = find(goods, args.query)
            if not titles:
                print("Продукты не найдены.")
            for title in titles:
                for batch in goods[title]:
                    expiry = batch["expiration_date"] or "не указан"
                    print(f"{title}: {batch['amount']}; срок: {expiry}")
        else:
            print(get_expired(goods, args.days))
    except (OSError, ValueError, TypeError, OverflowError) as error:
        print(f"Ошибка: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
