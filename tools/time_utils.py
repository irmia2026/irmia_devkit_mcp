"""
time_utils — 时间工具。
时间戳/ISO互转、当前时间、时差计算。纯 datetime 标准库。
"""

from datetime import datetime


def now() -> dict:
    """当前时间：ISO 字符串 + Unix 时间戳。"""
    dt = datetime.now()
    return {
        "ok": True,
        "iso": dt.isoformat(),
        "timestamp": int(dt.timestamp()),
        "timestamp_ms": int(dt.timestamp() * 1000),
    }


def ts_to_iso(ts: int, ms: bool = False) -> dict:
    """时间戳 → ISO 字符串。"""
    try:
        if ms:
            ts = ts / 1000.0
        dt = datetime.fromtimestamp(ts)
        return {"ok": True, "iso": dt.isoformat()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def iso_to_ts(iso: str) -> dict:
    """ISO 字符串 → 时间戳。支持 "2026-05-20T23:00:00" 及其变体。"""
    try:
        dt = datetime.fromisoformat(iso)
        return {"ok": True, "timestamp": int(dt.timestamp()), "iso": dt.isoformat()}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def time_diff(iso1: str, iso2: str) -> dict:
    """计算两个 ISO 时间的差值（秒、分、时）。"""
    try:
        t1 = datetime.fromisoformat(iso1)
        t2 = datetime.fromisoformat(iso2)
        delta = t2 - t1
        return {
            "ok": True,
            "delta_seconds": int(delta.total_seconds()),
            "delta_minutes": round(delta.total_seconds() / 60, 1),
            "delta_hours": round(delta.total_seconds() / 3600, 2),
        }
    except Exception as e:
        return {"ok": False, "error": str(e)}
