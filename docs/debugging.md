# Отладка расчёта стоимости

## Выполненный эксперимент

Проверка выполнена в стандартном отладчике Python `pdb`.
Для эксперимента создана временная копия `main.py`: в формуле скидки
`1 - discount` заменено на `1 + discount`. В основном файле сохранена
исправленная формула. Ниже приведён реальный вывод двух запусков.

Команды: `b 21` — breakpoint перед расчётом; `c` — продолжить до него;
`p base_price` и `p discount` — посмотреть переменные; `n` — шаг;
`p final_price` — проверить результат; `q` — закончить.

Ошибка даёт 1650 рублей вместо 1350: скидка прибавляется к цене.
Исправление: вычесть долю скидки из единицы. Тест `test_student_discount`
проверяет результат 1350. Демонстрация в IDE в этой сессии не выполнялась.

## Как повторить в VS Code

1. Открыть папку проекта, установить расширения Python и Python Debugger.
2. Выбрать интерпретатор `.venv` через Python: Select Interpreter.
3. Поставить breakpoint на строке 21 файла `main.py`.
4. Запустить конфигурацию «ПР1: отладка main.py» клавишей F5.
5. Посмотреть `base_price = 1500.0`, `discount = 0.1` в Variables.
6. Выполнить Step Over: `final_price` должен стать `1350.0`.
7. Временно заменить минус на плюс, повторить и получить `1650.0`.
8. Вернуть минус и повторно запустить тесты.

## buggy

```text
> /private<temporary-directory>/buggy.py(1)<module>()
-> """ПР1: расчёт и подтверждение одной записи в барбершоп."""
(Pdb) Breakpoint 1 at /private<temporary-directory>/buggy.py:21
(Pdb) > /private<temporary-directory>/buggy.py(21)calculate_price()
-> final_price = round(base_price * (1 + discount), 2)
(Pdb) 1500.0
(Pdb) 0.1
(Pdb) > /private<temporary-directory>/buggy.py(22)calculate_price()
-> return final_price
(Pdb) 1650.0
(Pdb) ```

## fixed

```text
> /private<temporary-directory>/fixed.py(1)<module>()
-> """ПР1: расчёт и подтверждение одной записи в барбершоп."""
(Pdb) Breakpoint 1 at /private<temporary-directory>/fixed.py:21
(Pdb) > /private<temporary-directory>/fixed.py(21)calculate_price()
-> final_price = round(base_price * (1 - discount), 2)
(Pdb) 1500.0
(Pdb) 0.1
(Pdb) > /private<temporary-directory>/fixed.py(22)calculate_price()
-> return final_price
(Pdb) 1350.0
(Pdb) ```
