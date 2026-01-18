class Vacancy:
    """
    Class representing a job vacancy.
    """

    __slots__ = ["_name", "_url", "_salary", "_description"]

    def __init__(self, name: str, url: str, salary, description: str):
        """
        Initialize a Vacancy instance.

        Args:
            name (str): Name of the vacancy.
            url (str): URL of the vacancy.
            salary: Salary information (int, str, or dict with 'from' and 'to' keys).
            description (str): Description of the vacancy.
        """
        self._name = self._validate_name(name)
        self._url = self._validate_url(url)
        self._salary = self._validate_salary(salary)
        self._description = description

    @staticmethod
    def _validate_name(name: str) -> str:
        """
        Validate the name of the vacancy.

        Args:
            name (str): Name to validate.

        Returns:
            Validated name.
        """
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Vacancy name must be a non-empty string.")
        return name.strip()

    @staticmethod
    def _validate_url(url: str) -> str:
        """
        Validate the URL of the vacancy.

        Args:
            url (str): URL to validate.

        Returns:
            Validated URL.
        """
        if not isinstance(url, str) or not url.startswith("http"):
            raise ValueError("URL must be a valid string starting with 'http'.")
        return url

    @staticmethod
    def _validate_salary(salary) -> dict:
        """
        Validate and normalize salary data.

        Args:
            salary: Raw salary data.

        Returns:
            Dictionary with 'from' and 'to' keys.
        """
        if salary is None:
            return {"from": 0, "to": 0}

        if isinstance(salary, dict):
            from_val = salary.get("from")
            to_val = salary.get("to")
            return {"from": from_val if from_val is not None else 0, "to": to_val if to_val is not None else 0}

        if isinstance(salary, str):
            # Handle string like '100 000-150 000 руб.'
            try:
                cleaned = salary.replace(" ", "").replace("руб.", "").replace("USD", "").replace("$", "")
                if "-" in cleaned:
                    parts = cleaned.split("-")
                    return {
                        "from": int(parts[0]) if parts[0].isdigit() else 0,
                        "to": int(parts[1]) if parts[1].isdigit() else 0,
                    }
                elif cleaned.isdigit():
                    return {"from": int(cleaned), "to": int(cleaned)}
            except Exception:
                pass

        # Default fallback
        return {"from": 0, "to": 0}

    @property
    def name(self) -> str:
        """Get the name of the vacancy."""
        return self._name

    @property
    def url(self) -> str:
        """Get the URL of the vacancy."""
        return self._url

    @property
    def salary(self) -> dict:
        """Get the salary of the vacancy."""
        return self._salary

    @property
    def description(self) -> str:
        """Get the description of the vacancy."""
        return self._description

    def __lt__(self, other) -> bool:
        """Less than comparison based on salary 'from' value."""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._salary["from"] < other._salary["from"]

    def __le__(self, other) -> bool:
        """Less than or equal comparison based on salary 'from' value."""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._salary["from"] <= other._salary["from"]

    def __gt__(self, other) -> bool:
        """Greater than comparison based on salary 'from' value."""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._salary["from"] > other._salary["from"]

    def __ge__(self, other) -> bool:
        """Greater than or equal comparison based on salary 'from' value."""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._salary["from"] >= other._salary["from"]

    def __eq__(self, other) -> bool:
        """Equality comparison based on salary 'from' value."""
        if not isinstance(other, Vacancy):
            return NotImplemented
        return self._salary["from"] == other._salary["from"]

    def __str__(self) -> str:
        """String representation of the vacancy."""
        salary_from = self._salary["from"]
        salary_to = self._salary["to"]
        salary_str = f"{salary_from}-{salary_to} руб." if salary_from != 0 or salary_to != 0 else "Зарплата не указана"
        return f"{self._name}\nЗарплата: {salary_str}\nСсылка: {self._url}\n" f"Описание: {self._description[:100]}..."

    def __repr__(self) -> str:
        """Developer-friendly representation of the vacancy."""
        return (
            f"Vacancy(name='{self._name}', url='{self._url}', "
            f"salary={self._salary}, description='{self._description}')"
        )
