# Система производственного планирования

Учебный проект: планирование заказов (ASAP, сортировка по сроку) с учётом сотрудников и станков.

## Структура
- `main.py` — программа (tkinter), проект прошлого семестра
- `sql/create_database.sql` — создание базы и пользователя
- `sql/create_tables.sql` — создание таблиц
- `sql/insert_data.sql` — тестовые данные
- `sql/queries.sql` — шесть запросов
- `sql/check_constraints.sql` — проверка ограничений (обе команды должны дать ошибку)
- `docs/er_diagram.png` — схема базы данных
- `db_config.example.py` — пример настроек подключения (пароль храним в `db_config.py`, он в `.gitignore`)

## Как развернуть базу
1. В pgAdmin под пользователем postgres выполнить `sql/create_database.sql` (подставить свой пароль).
2. Подключиться к базе `production_planning` и выполнить по очереди `create_tables.sql` и `insert_data.sql`.
3. Скопировать `db_config.example.py` в `db_config.py` и вписать пароль.
