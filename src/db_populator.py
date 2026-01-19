import requests
from vacancy import Vacancy


class DBPopulator:
    """
    Class for populating the database with data from HeadHunter API.
    """

    def __init__(self, conn):
        """
        Initialize DBPopulator with database connection.

        Args:
            conn: PostgreSQL connection object.
        """
        self.conn = conn

    def get_employer_data(self, employer_id: int):
        """
        Get employer data from HeadHunter API by employer ID.

        Args:
            employer_id (int): ID of the employer.

        Returns:
            Dictionary with employer data or None if request failed.
        """


        url = f"https://api.hh.ru/employers/{employer_id}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": data.get("name", "Unknown"),
                    "hh_id": data.get("id"),
                    "url": f"https://hh.ru/employer/{data.get('id')}"
                }
        except Exception as e:
            print(f"Error fetching employer data: {e}")
        return None

    def get_employer_vacancies(self, employer_id: int):
        """
        Get vacancies for a specific employer from HeadHunter API.

        Args:
            employer_id (int): ID of the employer.

        Returns:
            List of vacancy dictionaries.
        """
        url = "https://api.hh.ru/vacancies"
        params = {
            "employer_id": employer_id,
            "per_page": 100
        }
        vacancies = []  
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
            	data = response.json()
            	if "items" in data:
            		for item in data["items"]:
            			if item.get("salary"):
            				vacancy = {
            					"name": item.get("name", "No name"),
            					"salary_from": item.get("salary", {}).get("from"),
            					"salary_to": item.get("salary", {}).get("to"),
            					"url": item.get("alternate_url", "No URL"),
            					"requirement": item.get("snippet", {}).get("requirement", "No requirement"),
            					"responsibility": item.get("snippet", {}).get("responsibility", "No responsibility")
            				}
            				vacancies.append(vacancy)
        except Exception as e:
            print(f"Error fetching vacancies: {e}")
        
        return vacancies

    def populate_database(self, employer_ids: list):
        """
        Populate the database with employers and their vacancies.

        Args:
            employer_ids (list): List of employer IDs to fetch data for.
        """
        with self.conn.cursor() as cursor:
            for employer_id in employer_ids:
                # Get employer data
                employer_data = self.get_employer_data(employer_id)
                if not employer_data:
                    print(f"Не удалось получить данные о работодателе с ID {employer_id}")
                    continue
                
                # Insert employer
                try:
                    cursor.execute(
                        "INSERT INTO employers (name, hh_id, url) VALUES (%s, %s, %s) ON CONFLICT (hh_id) DO NOTHING",
                        (employer_data["name"], employer_data["hh_id"], employer_data["url"])
                    )
                except Exception as e:
                    print(f"Ошибка при добавлении работодателя {employer_data['name']}: {e}")
                    continue
                
                # Get employer ID from database
                cursor.execute("SELECT id FROM employers WHERE hh_id = %s", (employer_id,))
                result = cursor.fetchone()
                if not result:
                    print(f"Не удалось получить ID работодателя {employer_data['name']} из базы данных")
                    continue
                
                db_employer_id = result[0]
                
                # Get and insert vacancies
                vacancies = self.get_employer_vacancies(employer_id)
                for vacancy in vacancies:
                    try:
                        cursor.execute(
                            "INSERT INTO vacancies (name, salary_from, salary_to, url, employer_id, requirement, responsibility) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (vacancy["name"], vacancy["salary_from"], vacancy["salary_to"], vacancy["url"], db_employer_id, vacancy["requirement"], vacancy["responsibility"])
                        )
                    except Exception as e:
                        print(f"Ошибка при добавлении вакансии {vacancy['name']}: {e}")
                        continue
                
                print(f"Добавлено вакансий для {employer_data['name']}: {len(vacancies)}")
