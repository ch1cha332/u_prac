# Пример файла настроек подключения к базе данных.
# 1. Скопируйте этот файл под именем db_config.py
# 2. Впишите свой пароль в db_config.py
# Файл db_config.py находится в .gitignore и в GitHub не попадает.

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "production_planning",
    "user": "planner_user",
    "password": "ВАШ_ПАРОЛЬ",
}
