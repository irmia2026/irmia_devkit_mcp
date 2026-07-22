"""
http_download — 二进制文件下载。
用 urllib 下载文件到本地，自动处理重定向、进度、覆盖确认。
"""

import urllib.request
import urllib.error
import time
import tempfile
from pathlib import Path

from ._http_utils import check_url, make_opener
from ._file_utils import human_size

def _resolve_sandbox() -> Path:
    """返回下载沙箱路径，HOME 不可用时回退到插件目录或临时目录。"""
    try:
        return Path.home() / ".irmia" / "downloads"
    except RuntimeError:
        return Path(tempfile.gettempdir()) / ".irmia" / "downloads"


_DOWNLOAD_SANDBOX = _resolve_sandbox()
_MAX_DOWNLOAD_SIZE = 500 * 1024 * 1024  # H5: 500MB 上限


def _resolve_path(path: str) -> Path:
    """解析保存路径。绝对路径直接使用，相对路径相对于当前目录。
    路径穿越（..）被拒绝。无路径时使用默认沙箱。"""
    if not path or not path.strip():
        sandbox = _DOWNLOAD_SANDBOX.resolve()
        sandbox.mkdir(parents=True, exist_ok=True)
        return sandbox / "download"
    if ".." in path.replace("\\", "/").split("/"):
        raise ValueError("路径包含 .. 穿越，已被拒绝")
    if Path(path).is_absolute():
        return Path(path).resolve()
    return (Path.cwd() / path).resolve()


def download(url: str, path: str, overwrite: bool = False, timeout: int = 60) -> dict:
    """下载文件到本地。

    Args:
        url: 下载地址
        path: 保存路径（含文件名，路径遍历会被沙箱过滤）
        overwrite: 是否覆盖已有文件
        timeout: 超时秒数

    Returns:
        {"ok": True, "path": ..., "size": ..., "elapsed_s": ...} 或 {"ok": False, "error": ...}
    """
    err = check_url(url)
    if err:
        return err

    try:
        safe_path = _resolve_path(path)
    except ValueError as e:
        return {"ok": False, "error": str(e)}
    safe_path.parent.mkdir(parents=True, exist_ok=True)

    if safe_path.exists() and not overwrite:
        return {
            "ok": False,
            "error": f"文件已存在: {safe_path}，设 overwrite=True 覆盖",
        }

    start = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "IrmiaDevKit/2.7.2"})
        with make_opener().open(req, timeout=timeout) as resp:
            size = int(resp.headers.get("Content-Length", 0))
            if size > _MAX_DOWNLOAD_SIZE:
                return {
                    "ok": False,
                    "error": f"文件大小 {size // 1024 // 1024}MB 超过上限 {_MAX_DOWNLOAD_SIZE // 1024 // 1024}MB",
                }
            content_type = resp.headers.get("Content-Type", "unknown")

            downloaded = 0
            with open(safe_path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    if downloaded + len(chunk) > _MAX_DOWNLOAD_SIZE:
                        downloaded += len(chunk)
                        break
                    downloaded += len(chunk)
                    f.write(chunk)
            if downloaded > _MAX_DOWNLOAD_SIZE:
                safe_path.unlink(missing_ok=True)
                return {
                    "ok": False,
                    "error": f"实际下载大小超过上限 {_MAX_DOWNLOAD_SIZE // 1024 // 1024}MB",
                }

        elapsed = round(time.time() - start, 2)
        actual_size = safe_path.stat().st_size
        return {
            "ok": True,
            "path": str(safe_path),
            "size": actual_size,
            "size_human": human_size(actual_size),
            "content_type": content_type,
            "elapsed_s": elapsed,
        }
    except urllib.error.HTTPError as e:
        safe_path.unlink(missing_ok=True)
        return {"ok": False, "error": f"HTTP {e.code}: {e.reason}", "url": url}
    except urllib.error.URLError as e:
        safe_path.unlink(missing_ok=True)
        return {"ok": False, "error": f"连接失败: {e.reason}", "url": url}
    except Exception as e:
        safe_path.unlink(missing_ok=True)
        return {"ok": False, "error": str(e), "url": url}
