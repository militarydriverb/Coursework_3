import configparser
from src.hh_api import HeadHunterAPI
from json_saver import JSONSaver
from logger import setup_logging
from utils import filter_vacancies, get_top_vacancies, get_vacancies_by_salary, print_vacancies, sort_vacancies
from vacancy import Vacancy
import psycopg2
from src.db_manager import DBManager
from src.connect_db import create_database, create_tables
from src.db_populator import DBPopulator

logger = setup_logging()


def user_interaction():
    """
    Function for user interaction.
    """
    # Create API instance
    hh_api = HeadHunterAPI()

    # Create file manager instance
    json_saver = JSONSaver("data/vacancies.json")

    # Get search query from user
    search_query = input("Введите поисковый запрос: ")

    # Get vacancies from API
    print(f"Ищем вакансии по запросу '{search_query}'...")
    hh_vacancies = hh_api.get_vacancies(search_query)

    # Convert to Vacancy objects
    vacancies_list = []
    for item in hh_vacancies:
        try:
            vacancy = Vacancy(
                name=item["name"],
                url=item["url"],
                salary=item["salary"],
                description=item["description"],
            )
            vacancies_list.append(vacancy)

            # Save to file
            json_saver.add_vacancy(item)

        except ValueError as e:
            print(f"Ошибка при создании вакансии: {e}")
            continue

    if not vacancies_list:
        print("Не найдено вакансий по данному запросу.")
        return

    # Get number of top vacancies to display
    while True:
        try:
            top_n = int(input("Введите количество вакансий для вывода в топ N: "))
            if top_n > 0:
                break
            else:
                print("Введите положительное число.")
        except ValueError:
            print("Введите корректное число.")

    # Get filter words
    filter_words_input = input("Введите ключевые слова для фильтрации вакансий (через пробел): ")
    filter_words = filter_words_input.split() if filter_words_input.strip() else []

    # Get salary range
    salary_range = input("Введите диапазон зарплат (например, 100000 - 150000): ")

    # Apply filters and sorting
    filtered_vacancies = filter_vacancies(vacancies_list, filter_words)
    ranged_vacancies = get_vacancies_by_salary(filtered_vacancies, salary_range)
    sorted_vacancies = sort_vacancies(ranged_vacancies)
    top_vacancies = get_top_vacancies(sorted_vacancies, top_n)

    # Display results
    print(f"\nНайдено {len(vacancies_list)} вакансий")
    print(f"После фильтрации найдено {len(filtered_vacancies)} вакансий")
    print(f"После фильтрации по зарплате найдено {len(ranged_vacancies)} вакансий")
    print(f"Топ {top_n} вакансий по зарплате:\n")

    print_vacancies(top_vacancies)


def main():
    """Main function to run the application."""
    # Read database configuration from file
    config = configparser.ConfigParser()
    config.read('database.ini')
    db_config = dict(config['postgresql'])
    
    # Employer IDs from task
    employer_ids = [
        1740,    # Яндекс
        3529,    # Сбербанк
        78638,   # Т-Банк
        638037,  # EFT GROUP
        895945,  # Правительство Москвы
        3363490, # Анвио Парк
        9352463, # X5 Tech
        128680840, # ИП Фомин Сергей Александрович
        129275087, # ООО Антара
        129530149  # Красное & Белое
    ]
    
    # Create database
    if not create_database(db_config):
        print("Не удалось создать базу данных")
        return
    
    # Connect to database
    try:
        conn = psycopg2.connect(**db_config)
        print("Подключение к базе данных установлено")
    except psycopg2.Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return
    
    # Create tables
    create_tables(conn)
    
    # Populate database
    db_populator = DBPopulator(conn)
    db_populator.populate_database(employer_ids)
    
    # Create DBManager instance
    db_manager = DBManager(db_config)
    
    # Demonstrate DBManager methods
    print("\n--- Список компаний и количество вакансий ---")
    companies = db_manager.get_companies_and_vacancies_count()
    for company in companies:
        print(f"{company['name']}: {company['vacancies_count']} вакансий")
    
    print("\n--- Все вакансии ---")
    all_vacancies = db_manager.get_all_vacancies()
    for vacancy in all_vacancies[:5]:  # Show first 5
        print(f"{vacancy['company_name']} - {vacancy['name']} ({vacancy['salary_from']}-{vacancy['salary_to']} руб.) {vacancy['url']}")
    
    print("\n--- Средняя зарплата ---")
    avg_salary = db_manager.get_avg_salary()
    print(f"Средняя зарплата: {avg_salary:.0f} руб.")
    
    print("\n--- Вакансии с зарплатой выше средней ---")
    higher_salary_vacancies = db_manager.get_vacancies_with_higher_salary()
    for vacancy in higher_salary_vacancies[:5]:  # Show first 5
        print(f"{vacancy['company_name']} - {vacancy['name']} ({vacancy['salary_from']}-{vacancy['salary_to']} руб.) {vacancy['url']}")
    
    print("\n--- Вакансии с ключевым словом 'python' ---")
    python_vacancies = db_manager.get_vacancies_with_keyword('python')
    for vacancy in python_vacancies:
        print(f"{vacancy['company_name']} - {vacancy['name']} ({vacancy['salary_from']}-{vacancy['salary_to']} руб.) {vacancy['url']}")
    
    # Close connections
    db_manager.close_connection()
    conn.close()
    
    # Run original user interaction
    user_interaction()


if __name__ == "__main__":
    logger = setup_logging()
    logger.info("Application starts....")
    
    main()
    
    logger.info("Application finished")
