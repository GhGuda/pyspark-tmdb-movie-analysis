import types

import requests

from app.extraction import fetch_api_data
from app.configs import settings


class DummyResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP {self.status_code}")

    def json(self):
        return self._payload


def test_fetch_movie_data_success(monkeypatch):
    payload = {"id": 123, "title": "Test"}

    def fake_get(url, params, timeout):
        assert params["api_key"] == "dummy"
        assert "credits" in params["append_to_response"]
        assert url.endswith("123")
        return DummyResponse(payload)

    monkeypatch.setattr(settings, "TMDB_API_KEY", "dummy")
    monkeypatch.setattr(settings, "TMDB_BASE_URL", "https://example.org/movie/")
    monkeypatch.setattr(requests, "get", fake_get)

    result = fetch_api_data.fetch_movie_data(123, retries=1, timeout=1)
    assert result == payload


def test_fetch_movie_data_retry(monkeypatch):
    payload = {"id": 456, "title": "Retry Movie"}
    calls = {"count": 0}

    def fake_get(url, params, timeout):
        calls["count"] += 1
        if calls["count"] == 1:
            raise requests.exceptions.RequestException("temporary")
        return DummyResponse(payload)

    monkeypatch.setattr(settings, "TMDB_API_KEY", "dummy")
    monkeypatch.setattr(settings, "TMDB_BASE_URL", "https://example.org/movie/")
    monkeypatch.setattr(requests, "get", fake_get)
    monkeypatch.setattr(fetch_api_data.time, "sleep", lambda *_: None)

    result = fetch_api_data.fetch_movie_data(456, retries=2, timeout=1)
    assert result == payload
    assert calls["count"] == 2
