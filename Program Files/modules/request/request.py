import requests

from .exceptions import RequestError


def get(url: str, attemps: int = 3) -> requests.Response:
    if attemps < 0:
        raise RequestError(f"GET request failed: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response

    except Exception as e:
        get(url, attemps-1)