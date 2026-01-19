import logging

import requests

from abc_classes import JobSiteAPI

logger = logging.getLogger(__name__)


class HeadHunterAPI(JobSiteAPI):
    """
    Class for interacting with HeadHunter API.
    """

    def __init__(self):
        """Initialize HeadHunterAPI with base URL and headers."""
        self._base_url = "https://api.hh.ru/vacancies"
        self._headers = {"User-Agent": "HH-User-Agent"}
        self.params = {"text": "", "page": 0, "per_page": 100}
        self.vacancies = []

    def _make_request(self, params: dict):
        """
        Make a request to the HeadHunter API with proper error handling.

        Args:
            params (dict): Parameters for the request.

        Returns:
            Response object or None if request failed.
        """
        try:
            response = requests.get(self._base_url, params=params, headers=self._headers, timeout=10)
            # Don't raise_for_status - let calling code handle different status codes
            return response
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None

    def connect_to_api(self):
        """
        Establish connection to the HeadHunter API.

        Returns:
            bool: True if connection successful, False otherwise.
        """
        try:
            response = self._make_request({})
            if response is None:
                return False
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to HeadHunter API: {e}")
            return False

    def get_vacancies(self, search_text: str):
        """
        Get vacancies from HeadHunter API by search text.

        
        Args:
            search_text (str): The search query for vacancies.
            
        Returns:
            List of vacancies in dictionary format.
        """
        # Check connection first
        if not self.connect_to_api():
            logger.error("Cannot get vacancies - failed to connect to API")
            return []
            
        params = {
            "text": search_text,
            "search_field": "name",
            "area": 1,
            "period": 1,
            "only_with_salary": True,
            "per_page": 100,
            "page": 0,
        }

        vacancies = []
        max_pages = 10  # Safety limit to prevent infinite loops
        pages_retrieved = 0
        
        while pages_retrieved < max_pages:
            response = self._make_request(params)
            if response is None:
                logger.error("Failed to make request to get vacancies")
                break

            # Handle non-200 status codes
            if response.status_code != 200:
                logger.error(f"API request failed with status {response.status_code}: {response.text}")
                break

            try:
                data = response.json()
                if not data or "items" not in data:
                    logger.error("Invalid response structure: missing items field")
                    break
                
                items = data.get("items", [])
                vacancies += items

                # Check if we've reached the last page
                if data.get("pages") is None or data.get("pages") <= params["page"]:
                    break
                
                params["page"] += 1
                pages_retrieved += 1
            except (ValueError, AttributeError) as e:
                logger.error(f"Failed to parse JSON response: {e}")
                break

        # Remove duplicates based on URL
        seen_urls = set()
        unique_vacancies = []
        for vacancy in vacancies:
            url = vacancy.get("alternate_url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_vacancies.append(vacancy)
            
        result = []
        for vacancy in unique_vacancies:
            vacancy_data = {
                "name": vacancy.get("name", "No name"),
                "salary": vacancy.get("salary", {"from": 0, "to": 0}),
                "url": vacancy.get("alternate_url", "No URL"),
                "description": vacancy.get("snippet", {}).get("requirement", "No description"),
            }
            result.append(vacancy_data)

        logger.info(f"Found {len(result)} vacancies")
        return result
