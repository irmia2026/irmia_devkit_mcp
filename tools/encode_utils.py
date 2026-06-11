"""
encode_utils — 编解码工具箱。
base64/URL/hex，纯标准库，三个函数覆盖 90% 日常编码需求。
"""

import base64
import binascii
import urllib.parse


# ─── base64 ──────────────────────────────────────
def b64_encode(data: str, as_uri: bool = False) -> dict:
    """字符串 → Base64。as_uri=True 则返回 data: URI。"""
    try:
        b = data.encode("utf-8")
        encoded = base64.b64encode(b).decode("ascii")
        result = encoded
        if as_uri:
            result = f"data:text/plain;base64,{encoded}"
        return {"ok": True, "result": result}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def b64_decode(data: str, strip_uri: bool = False) -> dict:
    """Base64 → 原始字符串。strip_uri=True 则自动剥离 data: URI 前缀。"""
    try:
        if strip_uri and "," in data:
            data = data.split(",", 1)[-1]
        decoded = base64.b64decode(data).decode("utf-8")
        return {"ok": True, "result": decoded}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ─── URL ─────────────────────────────────────────
def url_encode(data: str) -> dict:
    """URL 编码。"""
    try:
        return {"ok": True, "result": urllib.parse.quote(data, safe="")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def url_decode(data: str) -> dict:
    """URL 解码。"""
    try:
        return {"ok": True, "result": urllib.parse.unquote(data)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ─── hex ─────────────────────────────────────────
def hex_encode(data: str) -> dict:
    """字符串 → 十六进制。"""
    try:
        return {
            "ok": True,
            "result": binascii.hexlify(data.encode("utf-8")).decode("ascii"),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}


def hex_decode(data: str) -> dict:
    """十六进制 → 原始字符串。"""
    try:
        return {"ok": True, "result": binascii.unhexlify(data).decode("utf-8")}
    except Exception as e:
        return {"ok": False, "error": str(e)}
