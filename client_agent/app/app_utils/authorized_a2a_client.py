import os
from collections.abc import Callable, Generator
from urllib.parse import urlparse

import httpx
from google.auth.transport.requests import Request
from google.oauth2 import id_token

_TRUE_VALUES = {"1", "true", "t", "yes", "y", "on"}
_LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value.strip().lower() in _TRUE_VALUES


def _is_local_url(url: str) -> bool:
    return (urlparse(url).hostname or "").lower() in _LOCAL_HOSTS


class _GoogleIdTokenProvider:
    """Lazily mint ID tokens for a private Cloud Run audience."""

    def __init__(self, audience: str):
        self._audience = audience
        self._request = Request()
        self._credentials = None

    def __call__(self) -> str:
        if self._credentials is None:
            self._credentials = id_token.fetch_id_token_credentials(
                self._audience,
                request=self._request,
            )

        if not self._credentials.valid:
            self._credentials.refresh(self._request)

        token = self._credentials.token
        if not token:
            raise RuntimeError("Unable to obtain an ID token for the main agent.")
        return token


class _StaticTokenProvider:
    def __init__(self, token: str):
        self._token = token

    def __call__(self) -> str:
        return self._token


class _BearerTokenAuth(httpx.Auth):
    def __init__(self, token_provider: Callable[[], str]):
        self._token_provider = token_provider

    def auth_flow(
        self,
        request: httpx.Request,
    ) -> Generator[httpx.Request, httpx.Response, None]:
        request.headers["Authorization"] = f"Bearer {self._token_provider()}"
        yield request


def build_main_agent_httpx_client(base_url: str) -> httpx.AsyncClient | None:
    """Return an authenticated client for private Cloud Run, or None for local/public."""

    static_token = os.getenv("MAIN_AGENT_AUTH_TOKEN", "").strip()
    require_auth = _env_flag(
        "MAIN_AGENT_REQUIRE_AUTH",
        default=not _is_local_url(base_url),
    )

    if not static_token and (_is_local_url(base_url) or not require_auth):
        return None

    if static_token:
        token_provider = _StaticTokenProvider(static_token)
    else:
        audience = os.getenv("MAIN_AGENT_AUDIENCE", "").strip() or base_url
        token_provider = _GoogleIdTokenProvider(audience)

    return httpx.AsyncClient(
        auth=_BearerTokenAuth(token_provider),
        timeout=httpx.Timeout(600.0),
    )
