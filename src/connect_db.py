import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def create_database(db_config: dict) -> bool:
    """
    Create PostgreSQL database if it doesn't exist.

    Args:
        db_config (dict): Database configuration with host, port, database, user, password.

    Returns:
        bool: True if database created or already exists, False otherwise.
    """
    try:
        # Connect to default 'postgres' database to create new database
        conn_params = db_config.copy()
        conn_params['database'] = 'postgres'
        
        conn = psycopg2.connect(**conn_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{db_config['database']}'")
            exists = cursor.fetchone()
            
            if not exists:
                cursor.execute(f"CREATE DATABASE {db_config['database']}")
                print(f"База данных {db_config['database']} создана.")
            else:
                print(f"База данных {db_config['database']} уже существует.")
                
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"Ошибка при создании базы данных: {e}")
        return False


def create_tables(conn):
    """
    Create employers and vacancies tables in the database.

    Args:
        conn: PostgreSQL connection object.
    """
    create_employers_table = """
    CREATE TABLE IF NOT EXISTS employers (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        hh_id INTEGER UNIQUE NOT NULL,
        url VARCHAR(500)
    )
    """
    
    create_vacancies_table = """
    CREATE TABLE IF NOT EXISTS vacancies (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        salary_from INTEGER,
        salary_to INTEGER,
        url VARCHAR(500),
        employer_id INTEGER REFERENCES employers(id),
        requirement TEXT,
        responsibility TEXT
    )
    """
    
    try:
        with conn.cursor() as cursor:
            cursor.execute(create_employers_table)
            cursor.execute(create_vacancies_table)
            conn.commit()
            print("Таблицы созданы.")
    except psycopg2.Error as e:
        print(f"Ошибка при создании таблиц: {e}")
        conn.rollback()