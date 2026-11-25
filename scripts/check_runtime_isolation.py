"""Verify the opt-in Chromium profile inside a restricted Linux container."""

import os
import tempfile
from pathlib import Path
from time import monotonic, sleep

from prospector_engine.browser import BrowserRuntime


def browser_processes():
    processes = {}
    for process in Path("/proc").glob("[0-9]*"):
        try:
            command = (process / "cmdline").read_bytes().split(b"\0")
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            continue
        if command and (b"chrome-headless-shell" in command[0] or b"run-driver" in command):
            processes[process.name] = command
    return processes


def main():
    assert os.getuid() == os.getgid() == 10001
    assert os.environ.get("PROSPECTOR_CHROMIUM_SANDBOX") == "1"
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines())
    assert status["NoNewPrivs"].strip() == "1"
    assert status["Seccomp"].strip() == "2"
    assert int(status["CapEff"].strip(), 16) == 0
    mounts = [line.split() for line in Path("/proc/self/mountinfo").read_text().splitlines()]
    assert any(row[4] == "/" and "ro" in row[5].split(",") for row in mounts)
    assert any(
        row[4] == "/tmp"
        and row[row.index("-") + 1] == "tmpfs"
        and {"nosuid", "nodev"} <= set(row[5].split(","))
        for row in mounts
    )
    assert tempfile.gettempdir() == "/tmp"
    assert {interface.name for interface in Path("/sys/class/net").iterdir()} == {"lo"}

    prior = browser_processes()
    runtime = BrowserRuntime(channel=None, headless=True)
    with runtime:
        page = runtime.new_page()
        page.goto("data:text/html,<title>Controlled sandbox fixture</title>")
        assert page.title() == "Controlled sandbox fixture"
        owned = {pid: cmd for pid, cmd in browser_processes().items() if pid not in prior}
        commands = list(owned.values())
        assert any(b"run-driver" in cmd for cmd in commands)
        assert any(b"chrome-headless-shell" in cmd[0] for cmd in commands)
        assert all(b"--no-sandbox" not in cmd for cmd in commands)
    assert page.is_closed()
    deadline = monotonic() + 3
    while set(owned) & browser_processes().keys() and monotonic() < deadline:
        sleep(0.05)
    assert not set(owned) & browser_processes().keys(), "owned browser process survived"
    leftover_profiles = list(Path("/tmp").glob("playwright*"))
    assert not leftover_profiles, "temporary Playwright profiles survived"
    print("Chromium sandbox requested, container restrictions and process cleanup verified")


if __name__ == "__main__":
    main()
