from __future__ import annotations

import random
from time import sleep
from typing import Literal

try:
    from typing import Unpack
except ImportError:
    from typing_extensions import Unpack

# curl-cffi: Response/Session are in curl_cffi.requests for all supported versions
from curl_cffi.requests import Response, Session

try:
    from curl_cffi.requests import RequestsError
except ImportError:
    from curl_cffi import CurlError as RequestsError

try:
    from curl_cffi.requests.session import RequestParams
except ImportError:
    pass

from .exceptions import NetworkError


class CustomSession(Session):
    """Custom curl_cffi session with retries"""

    def __init__(self, max_retries: int = 3, initial_retry_delay: int = 1, backoff_factor: int = 2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_retries = max_retries
        self.initial_retry_delay = initial_retry_delay
        self.backoff_factor = backoff_factor

    def custom_request(self, method: Literal["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "TRACE", "PATCH", "QUERY"], url: str, *args, **kwargs) -> Response:
        """request wrapper with retries"""
        attempt = 0
        while True:
            try:
                return super().request(method, url, *args, **kwargs)
            except RequestsError as e:
                attempt += 1
                if attempt >= self.max_retries:
                    raise NetworkError from e
                # Calculate the backoff delay
                backoff_delay = self.initial_retry_delay * (self.backoff_factor ** (attempt - 1))
                backoff_delay += random.uniform(0, 1)  # Adding randomness for jitter
                sleep(backoff_delay)  # Wait before retrying

    def head(self, url: str, **kwargs: Unpack[RequestParams]):
        return self.custom_request(method="HEAD", url=url, **kwargs)

    def get(self, url: str, **kwargs: Unpack[RequestParams]):
        return self.custom_request(method="GET", url=url, **kwargs)

    def post(self, url: str, **kwargs: Unpack[RequestParams]):
        return self.custom_request(method="POST", url=url, **kwargs)

    def put(self, url: str, **kwargs: Unpack[RequestParams]):
        return self.custom_request(method="PUT", url=url, **kwargs)

    def patch(self, url: str, **kwargs: Unpack[RequestParams]):
        return self.custom_request(method="PATCH", url=url, **kwargs)

    def delete(self, url: str, **kwargs: Unpack[RequestParams]):
        return self.custom_request(method="DELETE", url=url, **kwargs)

    def options(self, url: str, **kwargs: Unpack[RequestParams]):
        return self.custom_request(method="OPTIONS", url=url, **kwargs)

    def trace(self, url: str, **kwargs: Unpack[RequestParams]):
        return self.custom_request(method="TRACE", url=url, **kwargs)

    def query(self, url: str, **kwargs: Unpack[RequestParams]):
        return self.custom_request(method="QUERY", url=url, **kwargs)
