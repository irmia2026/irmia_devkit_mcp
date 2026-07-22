"""Tests for http_get — HTTP GET/POST requests.

Tests error paths (invalid URLs, private IPs) without real network.
Use monkeypatch to avoid actual HTTP calls."""

from tools.http_get import get, post
from tools import _http_utils


class TestHttpGet:
    def test_invalid_url_scheme(self):
        r = get("ftp://example.com")
        assert r["ok"] is False
        assert "error" in r

    def test_missing_hostname(self):
        r = get("http://")
        assert r["ok"] is False

    def test_private_ip_blocked(self):
        r = get("http://127.0.0.1/test")
        assert r["ok"] is False

    def test_private_ip_10_dot(self):
        r = get("http://10.0.0.1/test")
        assert r["ok"] is False

    def test_private_ip_192_168(self):
        r = get("http://192.168.1.1/test")
        assert r["ok"] is False

    def test_invalid_url_format(self):
        r = get("not a url")
        assert r["ok"] is False

    def test_empty_url(self):
        r = get("")
        assert r["ok"] is False

    def test_post_without_url(self):
        r = post("")
        assert r["ok"] is False


class TestHttpPost:
    def test_invalid_url(self):
        r = post("http://10.0.0.1/api")
        assert r["ok"] is False

    def test_post_dict_data_no_network(self):
        # POST to example.com - may work depending on network
        r = post("http://example.com/api", data={"key": "value"})
        # Should return ok: False (either validation or network error)
        assert r["ok"] is False


class TestPinnedDns:
    def test_dns_failure_is_rejected(self, monkeypatch):
        import socket

        def fail(*_args, **_kwargs):
            raise socket.gaierror("missing")

        monkeypatch.setattr(_http_utils.socket, "getaddrinfo", fail)
        err = _http_utils.validate_url("https://missing.example/path")
        assert err is not None
        assert "解析失败" in err["error"]

    def test_connection_uses_the_validated_ip(self, monkeypatch):
        answers = [(2, 1, 6, "", ("93.184.216.34", 0))]
        connected = []

        monkeypatch.setattr(_http_utils.socket, "getaddrinfo", lambda *_args, **_kwargs: answers)
        monkeypatch.setattr(
            _http_utils.socket,
            "create_connection",
            lambda address, *_args, **_kwargs: connected.append(address) or object(),
        )
        conn = _http_utils.PinnedHTTPConnection("example.com", timeout=1)
        conn.connect()
        assert connected == [("93.184.216.34", 80)]
