import json
import logging
import os

from abc_classes import FileManager

logger = logging.getLogger(__name__)


class JSONSaver(FileManager):
    """
    Class for saving and managing vacancies in a JSON file.
    """

    def __init__(self, filename: str = "data/vacancies.json"):
        """
        Initialize JSONSaver with a filename.

        Args:
            filename (str): Name of the JSON file to store vacancies.
        """
        self._filename = filename
        self._create_file_if_not_exists()

    def _create_file_if_not_exists(self):
        """Create the JSON file if it doesn't exist."""
        if not os.path.exists(self._filename):
            with open(self._filename, "w", encoding="utf-8") as file:
                json.dump([], file, ensure_ascii=False, indent=4)
            logger.info(f"Created new file: {self._filename}")

    def add_vacancy(self, vacancy: dict):
        """
        Add a vacancy to the JSON file.

        Args:
            vacancy (dict): Vacancy data to add.
        """
        try:
            # Read existing data
            with open(self._filename, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Check for duplicates based on URL
            if any(v["url"] == vacancy["url"] for v in data):
                logger.info(f"Vacancy with URL {vacancy['url']} already exists, skipping")
                return

            # Add new vacancy
            data.append(vacancy)

            # Write back to file
            with open(self._filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            logger.info(f"Added vacancy: {vacancy['name']}")

        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error adding vacancy to {self._filename}: {e}")

    def get_vacancies(self, criteria=None):
        """
        Get vacancies from the JSON file by criteria.

        Args:
            criteria: Optional criteria for filtering vacancies.

        Returns:
            List of vacancies.
        """
        try:
            with open(self._filename, "r", encoding="utf-8") as file:
                data = json.load(file)

            # If no criteria, return all
            if not criteria:
                return data

            # Filter by criteria (simple implementation)
            filtered = []
            for vacancy in data:
                if isinstance(criteria, str):
                    # Search in name and description
                    if (
                        criteria.lower() in vacancy.get("name", "").lower()
                        or criteria.lower() in vacancy.get("description", "").lower()
                    ):
                        filtered.append(vacancy)
                elif callable(criteria):
                    if criteria(vacancy):
                        filtered.append(vacancy)

            return filtered

        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error reading vacancies from {self._filename}: {e}")
            return []

    def delete_vacancy(self, vacancy: dict):
        """
        Delete a vacancy from the JSON file.

        Args:
            vacancy (dict): Vacancy data to delete.
        """
        try:
            with open(self._filename, "r", encoding="utf-8") as file:
                data = json.load(file)

            # Find and remove vacancy by URL
            initial_count = len(data)
            data = [v for v in data if v["url"] != vacancy["url"]]

            if len(data) == initial_count:
                logger.info(f"Vacancy with URL {vacancy['url']} not found, nothing to delete")
                return

            # Write back to file
            with open(self._filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            logger.info(f"Deleted vacancy: {vacancy['name']}")

        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Error deleting vacancy from {self._filename}: {e}")

    def get_all_vacancies(self):
        """
        Get all vacancies from the file.

        Returns:
            List of all vacancies.
        """
        return self.get_vacancies()
