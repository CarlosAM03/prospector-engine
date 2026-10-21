"""Controlled browser smoke without contacting Google Maps or public websites."""

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from .browser import BrowserRuntime


def browser_smoke(*, channel: str | None = None) -> None:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            body = b"<html><head><title>Prospector controlled smoke</title></head><body>OK</body></html>"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    runtime = BrowserRuntime(headless=True, channel=channel)
    try:
        with runtime:
            page = runtime.new_page()
            response = page.goto(f"http://127.0.0.1:{server.server_port}/", timeout=10000)
            assert response is not None and response.status == 200
            assert page.title() == "Prospector controlled smoke"
            browser = runtime.browser
        assert page.is_closed() and not browser.is_connected()
        assert runtime.browser is None and runtime._playwright_context is None
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browser", action="store_true")
    parser.add_argument("--channel", choices=["chromium", "msedge"], default="chromium")
    args = parser.parse_args()
    if args.browser:
        browser_smoke(channel="msedge" if args.channel == "msedge" else None)
    print("Prospector Engine installed-package smoke PASS")


if __name__ == "__main__":
    main()
