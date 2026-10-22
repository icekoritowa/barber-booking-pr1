# Отладка ПР2: соседние интервалы

Эксперимент выполнен в стандартном отладчике pdb на временных копиях
`bookings.py` и `utils.py`. Основной код не подменялся ошибочной версией.
Исходные условия: запись 12:00–14:00, запрос следующей записи 14:00–15:00.
Ожидается доступность, поскольку интервалы соседние, а не пересекающиеся.

В экспериментальную копию внесена ошибка: первое `<` в проверке пересечения
заменено на `<=`. Отладчик остановлен перед условием; просмотрены
`start_hour = 14` и конец существующей записи `12 + 2 = 14`.
С `<=` программа ошибочно возвращает False, с `<` — True.
Команды `n` и `r` выполняют шаг и переход до возврата функции.
Проверка соседних интервалов включена в pytest-тест
`test_booking_discount_and_overlap`.

## Повторение в VS Code

1. Открыть корень проекта и выбрать интерпретатор `.venv`.
2. Убедиться, что установлены расширения Python и Python Debugger.
3. Поставить breakpoint в `bookings.is_available` на условии пересечения.
4. Запустить конфигурацию «ПР1: отладка main.py» (подходит и для ПР2).
5. Через меню добавить услугу длительностью 2 часа и запись на будущую
   дату с началом в 12:00. Проверить доступность часовой услуги в 14:00.
6. В точке останова посмотреть `start_hour`, `duration`, `booking`;
   выполнить Step Over и проследить результат функции.
7. Временно заменить `<` на `<=`, повторить эксперимент, вернуть `<`
   и запустить тесты.

Демонстрация в IDE в этой сессии не выполнялась; ниже реальный вывод pdb.

## Ошибка: <= вместо <

```text
> /private<temporary-directory>/debug_case.py(1)<module>()
-> from datetime import date
(Pdb) Breakpoint 1 at /private<temporary-directory>/bookings.py:49
(Pdb) > /private<temporary-directory>/bookings.py(49)is_available()
-> if (start_hour <= booking["start_hour"] + booking["duration"]
(Pdb) 14
(Pdb) 14
(Pdb) > /private<temporary-directory>/bookings.py(50)is_available()
-> and booking["start_hour"] < start_hour + duration):
(Pdb) --Return--
> /private<temporary-directory>/bookings.py(51)is_available()->False
-> return False
(Pdb) False
(Pdb) Adjacent slot available: False
The program finished and will be restarted
> /private<temporary-directory>/debug_case.py(1)<module>()
-> from datetime import date
(Pdb) ```

## Исправлено: <

```text
> /private<temporary-directory>/debug_case.py(1)<module>()
-> from datetime import date
(Pdb) Breakpoint 1 at /private<temporary-directory>/bookings.py:49
(Pdb) > /private<temporary-directory>/bookings.py(49)is_available()
-> if (start_hour < booking["start_hour"] + booking["duration"]
(Pdb) 14
(Pdb) 14
(Pdb) > /private<temporary-directory>/bookings.py(44)is_available()
-> for booking in bookings:
(Pdb) --Return--
> /private<temporary-directory>/bookings.py(52)is_available()->True
-> return True
(Pdb) True
(Pdb) Adjacent slot available: True
The program finished and will be restarted
> /private<temporary-directory>/debug_case.py(1)<module>()
-> from datetime import date
(Pdb) ```
