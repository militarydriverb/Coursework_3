import psycopg2
from psycopg2.extras import RealDictCursor

class DBManager:
    """Class for managing database operations with PostgreSQL."""

    def __init__(self, db_config: dict):
        """
        Initialize DBManager with database configuration.

        Args:
            db_config (dict): Database configuration dictionary with keys:
                host, port, database, user, password
        """
        self.db_config = db_config
        self.conn = None

    def _connect(self):
        """Establish connection to PostgreSQL database."""
        try:
            self.conn = psycopg2.connect(
                host=self.db_config["host"],
                port=self.db_config["port"],
                database=self.db_config["database"],
                user=self.db_config["user"],
                password=self.db_config["password"]
            )
            return True
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return False

    def _execute_query(self, query: str, params=None):
        """Execute a SELECT query and return results."""
        if not self.conn:
            if not self._connect():
                return []

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                results = cur.fetchall()
                return results
        except psycopg2.Error as e:
            print(f"Error executing query: {e}")
            return []

    def get_companies_and_vacancies_count(self):
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        Returns:
            List of dictionaries with company name and vacancies count.
        """
        query = """
        SELECT e.name, COUNT(v.id) as vacancies_count
        FROM employers e
        LEFT JOIN vacancies v ON e.id = v.employer_id
        GROUP BY e.id, e.name
        ORDER BY vacancies_count DESC
        """
        return self._execute_query(query)

    def get_all_vacancies(self):
        """
        Получает список всех вакансий с указанием названия компании, названия вакансии и зарплаты и ссылки на вакансию.

        Returns:
            List of dictionaries with vacancy details.
        """
        query = """
        SELECT e.name as company_name, v.name, v.salary_from, v.salary_to, v.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.id
        ORDER BY v.salary_from DESC
        """
        return self._execute_query(query)

    def get_avg_salary(self):
        """
        Получает среднюю зарплату по вакансиям.

        Returns:
            Average salary (arithmetic mean of salary_from).
        """
        query = """
        SELECT AVG(salary_from) as avg_salary
        FROM vacancies
        WHERE salary_from > 0
        """
        result = self._execute_query(query)
        if result and result[0]["avg_salary"]:
            return float(result[0]["avg_salary"])
        return 0.0

    def get_vacancies_with_higher_salary(self):
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.

        Returns:
            List of vacancies with salary above average.
        """
        avg_salary = self.get_avg_salary()
        query = """
        SELECT e.name as company_name, v.name, v.salary_from, v.salary_to, v.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.id
        WHERE v.salary_from > %s
        ORDER BY v.salary_from DESC
        """
        return self._execute_query(query, (avg_salary,))

    def get_vacancies_with_keyword(self, keyword: str):
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова.

        Args:
            keyword (str): Keyword to search for in vacancy names.

        Returns:
            List of vacancies matching the keyword.
        """
        query = """
        SELECT e.name as company_name, v.name, v.salary_from, v.salary_to, v.url
        FROM vacancies v
        JOIN employers e ON v.employer_id = e.id
        WHERE LOWER(v.name) LIKE LOWER(%s)
        ORDER BY v.salary_from DESC
        """
        return self._execute_query(query, (f"%{keyword}%",))

    def close_connection(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None