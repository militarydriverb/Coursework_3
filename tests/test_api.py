import sys
import os

# Добавляем корневую директорию проекта в путь (где лежит папка src/)
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


from src.db_populator import DBPopulator

# Создаём экземпляр, передавая conn=None (он не нужен для get_employer_data)
db_populator = DBPopulator(conn=None)

# Тестируем получение данных о работодателях
print("Сбер:")
print(db_populator.get_employer_data(3529))
print("\nЯндекс:")
print(db_populator.get_employer_data(1455))

# Тестируем вакансии
print("\nВакансии Сбера (первые 2):")
vacancies = db_populator.get_employer_vacancies(3529)
print(vacancies[:2])