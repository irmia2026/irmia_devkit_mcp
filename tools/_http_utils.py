"""
_http_utils — HTTP 安全校验共享代码。
供 http_get / http_download 内部使用，不作为独立工具暴露。
"""

import ipaddress
import http.client
import socket
import ssl
import urllib.error
import urllib.request
from urllib.parse import urlparse


def _is_blocked_ip(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Return True if the address is private, loopback, link-local, multicast, reserved, or unspecified."""
    return (
        ip.is_private or ip.is_loopback or ip.is_link_local
        or ip.is_multicast or ip.is_reserved or ip.is_unspecified
    )


def _resolve_public_ips(hostname: str) -> list[str]:
    """Resolve once and reject the whole hostname if any answer is unsafe."""
    try:
        literal = ipaddress.ip_address(hostname)
        candidates = [str(literal)]
    except ValueError:
        try:
            candidates = list(dict.fromkeys(
                addr[4][0]
                for addr in socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
            ))
        except socket.gaierror as exc:
            raise ValueError(f"主机名解析失败: {hostname}") from exc
    if not candidates:
        raise ValueError(f"主机名解析失败: {hostname}")
    for ip_str in candidates:
        ip = ipaddress.ip_address(ip_str)
        mapped = getattr(ip, "ipv4_mapped", None)
        if _is_blocked_ip(ip) or (mapped and _is_blocked_ip(mapped)):
            raise ValueError(f"禁止访问内网地址: {hostname} 解析到 {ip_str}")
    return candidates


def validate_url(url: str) -> dict | None:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return {
            "ok": False,
            "error": f"不支持的协议: {parsed.scheme}，仅允许 http/https",
        }
    hostname = parsed.hostname
    if not hostname:
        return {"ok": False, "error": "URL 缺少有效主机名"}
    try:
        _resolve_public_ips(hostname)
    except ValueError as exc:
        return {"ok": False, "error": str(exc)}
    return None


class _PinnedConnectionMixin:
    """Connect only to addresses resolved and validated during construction."""

    def _pin_addresses(self) -> None:
        self._pinned_ips = _resolve_public_ips(self.host)

    def _open_pinned_socket(self):
        last_error = None
        for ip in self._pinned_ips:
            try:
                return socket.create_connection(
                    (ip, self.port), self.timeout, self.source_address,
                )
            except OSError as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        raise OSError("no validated address available")


class PinnedHTTPConnection(_PinnedConnectionMixin, http.client.HTTPConnection):
    def __init__(self, host, *args, **kwargs):
        super().__init__(host, *args, **kwargs)
        self._pin_addresses()

    def connect(self):
        self.sock = self._open_pinned_socket()


class PinnedHTTPSConnection(_PinnedConnectionMixin, http.client.HTTPSConnection):
    def __init__(self, host, *args, **kwargs):
        super().__init__(host, *args, **kwargs)
        self._pin_addresses()

    def connect(self):
        self.sock = self._open_pinned_socket()
        self.sock = self._context.wrap_socket(self.sock, server_hostname=self.host)


class PinnedHTTPHandler(urllib.request.HTTPHandler):
    def http_open(self, req):
        return self.do_open(PinnedHTTPConnection, req)


class PinnedHTTPSHandler(urllib.request.HTTPSHandler):
    def __init__(self):
        super().__init__(context=ssl.create_default_context())

    def https_open(self, req):
        return self.do_open(PinnedHTTPSConnection, req, context=self._context)


class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """每次 HTTP 重定向前重新走 SSRF 校验，防止 302→127.0.0.1 绕过。"""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        err = validate_url(newurl)
        if err:
            raise urllib.error.URLError(f"重定向目标被拦截: {err['error']}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def make_opener():
    """Create an opener that pins validated DNS answers for every redirect."""
    return urllib.request.build_opener(
        urllib.request.ProxyHandler({}),
        PinnedHTTPHandler(),
        PinnedHTTPSHandler(),
        SafeRedirectHandler(),
    )


def check_url(url: str) -> dict | None:
    """SSRF 校验的便捷封装。"""
    return validate_url(url)
