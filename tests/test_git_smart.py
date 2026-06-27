"""Tests for git_smart — commit guards and structured output."""

import os
import tempfile
import subprocess
import pytest
from tools.git_smart import commit, status


@pytest.fixture
def git_repo():
    d = tempfile.mkdtemp()
    subprocess.run(["git", "init"], cwd=d, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"], cwd=d, capture_output=True
    )
    subprocess.run(["git", "config", "user.name", "Test"], cwd=d, capture_output=True)
    # Create initial commit
    with open(os.path.join(d, "README.md"), "w") as f:
        f.write("# test\n")
    subprocess.run(["git", "add", "."], cwd=d, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=d, capture_output=True)
    yield d
    import shutil

    shutil.rmtree(d, ignore_errors=True)


class TestGitSmart:
    def test_status_clean(self, git_repo):
        s = status(git_repo)
        assert s["ok"] is True
        assert s["clean"] is True

    def test_commit_success(self, git_repo):
        with open(os.path.join(git_repo, "main.py"), "w") as f:
            f.write("print('hello')\n")
        result = commit(git_repo, "feat: add main.py")
        assert result["ok"] is True
        assert result["files_committed"] == 1

    def test_commit_no_changes(self, git_repo):
        result = commit(git_repo, "should fail")
        assert result["ok"] is False
        assert "没有可提交" in result["error"]

    def test_commit_many_files_blocked(self, git_repo):
        for i in range(15):
            with open(os.path.join(git_repo, f"file_{i}.py"), "w") as f:
                f.write(f"# file {i}\n")
        result = commit(git_repo, "too many")
        assert result["ok"] is False
        assert "过多" in result["error"] or "文件" in result.get("proposal", "")
