"""Base module for services."""
import os
from http import HTTPStatus

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class BasicServices:
    """Basic external service interface."""
    def __init__(self, url,
                 max_retry=10,
                 backoff_factor=0.1,
                 method_whitelist=None,
                 adapter=None):
        self.url = url
        self.max_retry = max_retry
        self.backoff_factor = backoff_factor
        if not method_whitelist:
            method_whitelist = frozenset([
                'HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE'
            ])
        self.method_whitelist = method_whitelist
        self.adapter = adapter

    @property
    def session(self):
        """
        Returns:
            requests.Session
        """
        if not hasattr(self, "_session"):
            session = requests.Session()
            retries = Retry(
                self.max_retry,
                allowed_methods=self.method_whitelist,
                status_forcelist=[
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                    HTTPStatus.BAD_GATEWAY,
                    HTTPStatus.SERVICE_UNAVAILABLE,
                    HTTPStatus.GATEWAY_TIMEOUT,
                ],
                backoff_factor=self.backoff_factor,
            )
            adapter = self.adapter
            if not adapter:
                adapter = HTTPAdapter(
                    pool_connections=(os.cpu_count() or 1) * 5,
                    pool_maxsize=(os.cpu_count() or 1) * 5,
                    max_retries=retries
                )
            session.mount("http://", adapter)
            session.mount("https://", adapter)
            setattr(self, "_session", session)
        return getattr(self, "_session")
