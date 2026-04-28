#!/usr/bin/env python3

from __future__ import annotations

import atexit
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
RUNTIME_DIR = ROOT_DIR / ".runtime"
PID_FILE = RUNTIME_DIR / "launcher.pid"
STATUS_FILE = RUNTIME_DIR / "launcher-status.json"
LOG_FILE = RUNTIME_DIR / "launcher.log"
PORT = int(os.getenv("STREAMLIT_PORT", "8501"))
URL = f"http://127.0.0.1:{PORT}"
HEALTH_URL = f"{URL}/_stcore/health"
HEARTBEAT_SECONDS = int(os.getenv("LAUNCHER_HEARTBEAT_SECONDS", "5"))
RESTART_DELAY_SECONDS = int(os.getenv("LAUNCHER_RESTART_DELAY_SECONDS", "2"))
MAX_RESTARTS = int(os.getenv("LAUNCHER_MAX_RESTARTS", "10"))


streamlit_process: subprocess.Popen[str] | None = None
stop_requested = False


def run_git(args: list[str], cwd: Path, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=check,
    )


def log_line(message: str) -> None:
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line, flush=True)
    with LOG_FILE.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def write_status(status: str, **extra: object) -> None:
    payload: dict[str, object] = {
        "status": status,
        "port": PORT,
        "url": URL,
        "pid": os.getpid(),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    payload.update(extra)
    STATUS_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def remove_runtime_files() -> None:
    PID_FILE.unlink(missing_ok=True)
    STATUS_FILE.unlink(missing_ok=True)


def ensure_runtime() -> None:
    RUNTIME_DIR.mkdir(exist_ok=True)
    PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
    atexit.register(remove_runtime_files)


def is_port_open() -> bool:
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=2) as response:
            return response.read().decode("utf-8").strip() == "ok"
    except (urllib.error.URLError, TimeoutError):
        return False


def browser_open() -> None:
    try:
        webbrowser.open(URL)
    except Exception as exc:  # pragma: no cover - best effort only
        log_line(f"browser open skipped: {exc}")


def get_repo_root() -> Path | None:
    override = os.getenv("APP_UPDATE_REPO_ROOT", "").strip()
    if override:
        path = Path(override).expanduser()
        return path if path.exists() else None

    result = run_git(["rev-parse", "--show-toplevel"], cwd=ROOT_DIR)
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip())


def repo_is_clean(repo_root: Path) -> bool:
    result = run_git(["status", "--porcelain"], cwd=repo_root)
    return result.returncode == 0 and result.stdout.strip() == ""


def get_remote_name() -> str:
    return os.getenv("APP_UPDATE_REMOTE", "origin").strip() or "origin"


def get_target_branch(repo_root: Path) -> str:
    explicit = os.getenv("APP_UPDATE_BRANCH", "").strip()
    if explicit:
        return explicit

    result = run_git(["branch", "--show-current"], cwd=repo_root)
    return result.stdout.strip() if result.returncode == 0 else ""


def repo_has_remote(repo_root: Path, remote_name: str) -> bool:
    result = run_git(["remote", "get-url", remote_name], cwd=repo_root)
    return result.returncode == 0 and bool(result.stdout.strip())


def maybe_update() -> None:
    repo_root = get_repo_root()
    if repo_root is None:
        log_line("update skipped: no git repository found for launcher workspace")
        return

    remote_name = get_remote_name()
    if not repo_has_remote(repo_root, remote_name):
        log_line(f"update skipped: no git remote '{remote_name}' configured for {repo_root}")
        return

    if not repo_is_clean(repo_root):
        log_line(f"update skipped: working tree is not clean in {repo_root}")
        return

    fetch = run_git(["fetch", remote_name], cwd=repo_root)
    if fetch.returncode != 0:
        log_line(f"update fetch failed: {fetch.stderr.strip()}")
        return

    current_branch = get_target_branch(repo_root)
    if not current_branch or current_branch == "HEAD":
        log_line("update skipped: detached or unknown HEAD")
        return

    behind = run_git(
        ["rev-list", "--count", f"HEAD..{remote_name}/{current_branch}"],
        cwd=repo_root,
    )
    if behind.returncode != 0:
        log_line(f"update check failed: {behind.stderr.strip()}")
        return

    behind_count = int((behind.stdout or "0").strip() or "0")
    if behind_count == 0:
        log_line("update check: already up to date")
        return

    pull = run_git(
        ["pull", "--ff-only", remote_name, current_branch],
        cwd=repo_root,
    )
    if pull.returncode != 0:
        log_line(f"update pull failed: {pull.stderr.strip()}")
        return

    log_line(f"updated successfully from {remote_name}/{current_branch}")


def start_streamlit() -> subprocess.Popen[str]:
    python_bin = ROOT_DIR / ".venv" / "bin" / "python"
    command = [
        str(python_bin),
        "-m",
        "streamlit",
        "run",
        str(ROOT_DIR / "app.py"),
        "--server.headless",
        "true",
        "--server.port",
        str(PORT),
    ]
    log_line(f"starting streamlit on port {PORT}")
    return subprocess.Popen(command, cwd=ROOT_DIR, text=True)


def wait_until_healthy() -> bool:
    for _ in range(30):
        if is_port_open():
            return True
        time.sleep(1)
    return False


def terminate_child() -> None:
    global streamlit_process
    if streamlit_process and streamlit_process.poll() is None:
        streamlit_process.terminate()
        try:
            streamlit_process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            streamlit_process.kill()
            streamlit_process.wait(timeout=5)
    streamlit_process = None


def handle_stop(signum: int, _frame: object) -> None:
    global stop_requested
    stop_requested = True
    log_line(f"received signal {signum}, stopping launcher")
    terminate_child()
    remove_runtime_files()
    raise SystemExit(0)


def install_signal_handlers() -> None:
    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)


def main() -> int:
    global streamlit_process

    ensure_runtime()
    install_signal_handlers()
    write_status("booting")
    maybe_update()

    if is_port_open():
        log_line(f"service already available at {URL}")
        write_status("running", note="existing service detected")
        browser_open()
        return 0

    restart_count = 0
    browser_opened = False

    while not stop_requested:
        streamlit_process = start_streamlit()
        write_status("starting", child_pid=streamlit_process.pid, restarts=restart_count)

        if wait_until_healthy():
            if not browser_opened:
                browser_open()
                browser_opened = True
            write_status(
                "running", child_pid=streamlit_process.pid, restarts=restart_count
            )
            log_line(f"service healthy at {URL}")
        else:
            log_line("service failed to become healthy within timeout")

        while streamlit_process.poll() is None and not stop_requested:
            if not is_port_open():
                log_line("heartbeat failed, restarting streamlit")
                terminate_child()
                break
            write_status(
                "running", child_pid=streamlit_process.pid, restarts=restart_count
            )
            time.sleep(HEARTBEAT_SECONDS)

        if stop_requested:
            break

        exit_code = streamlit_process.returncode if streamlit_process else None
        restart_count += 1
        if restart_count > MAX_RESTARTS:
            log_line("maximum restart count reached, exiting launcher")
            write_status("failed", restarts=restart_count, exit_code=exit_code)
            return 1

        log_line(
            f"streamlit exited with code {exit_code}, restart {restart_count}/{MAX_RESTARTS}"
        )
        write_status("restarting", restarts=restart_count, exit_code=exit_code)
        time.sleep(RESTART_DELAY_SECONDS)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
