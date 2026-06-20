"""Tests for _http_utils.validate_url — SSRF protection."""

import socket

from tools._http_utils import validate_url


class TestValidateUrl:
    def test_blocks_localhost_ip(self):
        err = validate_url("http://127.0.0.1/secret")
        assert err is not None
        assert err["ok"] is False
        assert "127.0.0.1" in err["error"]

    def test_blocks_private_10(self):
        err = validate_url("http://10.0.0.1/admin")
        assert err is not None
        assert "10.0.0.1" in err["error"]

    def test_blocks_private_192(self):
        err = validate_url("http://192.168.1.1/config")
        assert err is not None
        assert "192.168.1.1" in err["error"]

    def test_blocks_private_172(self):
        err = validate_url("http://172.16.0.1/api")
        assert err is not None

    def test_allows_public_ip(self):
        assert validate_url("http://8.8.8.8/") is None

    def test_blocks_file_protocol(self):
        err = validate_url("file:///etc/passwd")
        assert err is not None
        assert "不支持的协议" in err["error"]

    def test_blocks_empty_hostname(self):
        err = validate_url("http:///path")
        assert err is not None
        assert "缺少有效主机名" in err["error"]

    def test_allows_public_domain(self, monkeypatch):
        def fake_getaddrinfo(hostname, *args, **kwargs):
            assert hostname == "github.com"
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("140.82.112.3", 443))]

        monkeypatch.setattr(socket, "getaddrinfo", fake_getaddrinfo)
        assert validate_url("https://github.com/") is None

    def test_blocks_dns_rebind_to_localhost(self):
        err = validate_url("http://localhost/")
        assert err is not None
        assert "127.0.0.1" in err["error"] or "::1" in err["error"]
