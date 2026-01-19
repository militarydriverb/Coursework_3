from typing import List

from vacancy import Vacancy


def filter_vacancies(vacancies: List[Vacancy], filter_words: List[str]) -> List[Vacancy]:
    """
    Filter vacancies by keywords in name and description.

    Args:
        vacancies (List[Vacancy]): List of vacancy objects.
        filter_words (List[str]): List of keywords to filter by.

    Returns:
        List of filtered vacancy objects.
    """
    if not filter_words:
        return vacancies

    seen_urls = set()
    result = []
    filter_words_lower = [word.lower().strip() for word in filter_words]

    result = []
    seen_urls = set()
    filter_words_lower = [word.lower().strip() for word in filter_words]

    for vacancy in vacancies:
        text_to_search = f"{vacancy.name} {vacancy.description}".lower()
        # Check if any filter word is present in the text
        if any(word in text_to_search for word in filter_words_lower):
            # Use URL as unique identifier to avoid duplicates
            if vacancy.url not in seen_urls:
                seen_urls.add(vacancy.url)
                result.append(vacancy)

    return result


def get_vacancies_by_salary(vacancies: List[Vacancy], salary_range: str) -> List[Vacancy]:
    """
    Filter vacancies by salary range.

    Args:
        vacancies (List[Vacancy]): List of vacancy objects.
        salary_range (str): Salary range in format "min - max".

    Returns:
        List of filtered vacancy objects.
    """
    try:
        # Parse salary range
        if not salary_range or "-" not in salary_range:
            return vacancies

        min_salary_str, max_salary_str = salary_range.split("-")
        min_salary = int(min_salary_str.strip().replace(" ", ""))
        max_salary = int(max_salary_str.strip().replace(" ", ""))

        filtered = []
        for vacancy in vacancies:
            salary_from = vacancy.salary["from"]
            if min_salary <= salary_from <= max_salary:
                filtered.append(vacancy)
            # No additional conditions

        return filtered

    except (ValueError, AttributeError) as e:
        print(f"Error parsing salary range: {e}")
        return vacancies


def sort_vacancies(vacancies: List[Vacancy]) -> List[Vacancy]:
    """
    Sort vacancies by salary (descending).

    Args:
        vacancies (List[Vacancy]): List of vacancy objects.

    Returns:
        List of sorted vacancy objects.
    """
    return sorted(vacancies, reverse=True)


def get_top_vacancies(vacancies: List[Vacancy], top_n: int) -> List[Vacancy]:
    """
    Get top N vacancies from the list.

    Args:
        vacancies (List[Vacancy]): List of vacancy objects.
        top_n (int): Number of top vacancies to return.

    Returns:
        List of top N vacancy objects.
    """
    if top_n <= 0:
        return []
    return vacancies[:top_n]


def print_vacancies(vacancies: List[Vacancy]):
    """
    Print vacancies in a user-friendly format.

    Args:
        vacancies (List[Vacancy]): List of vacancy objects.
    """
    if not vacancies:
        print("No vacancies found.")
        return

    for i, vacancy in enumerate(vacancies, 1):
        print(f"\n{i}. {vacancy}")
