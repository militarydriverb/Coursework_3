from abc import ABC, abstractmethod


class JobSiteAPI(ABC):
    """
    Abstract base class for job site APIs.
    """

    @abstractmethod
    def connect_to_api(self):
        """Establish connection to the API."""
        pass

    @abstractmethod
    def get_vacancies(self, search_text: str):
        """
        Get vacancies from the API by search text.

        Args:
            search_text (str): The search query for vacancies.

        Returns:
            List of vacancies in dictionary format.
        """
        pass


class FileManager(ABC):
    """
    Abstract base class for file managers.
    """

    @abstractmethod
    def add_vacancy(self, vacancy):
        """Add a vacancy to the storage."""
        pass

    @abstractmethod
    def get_vacancies(self, criteria=None):
        """
        Get vacancies from storage by criteria.

        Args:
            criteria: Optional criteria for filtering vacancies.

        Returns:
            List of vacancies.
        """
        pass

    @abstractmethod
    def delete_vacancy(self, vacancy):
        """Delete a vacancy from storage."""
        pass
