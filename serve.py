# serve.py - small server for the CNC digital twin
# Run: python serve.py   then open http://localhost:8000
import argparse
import http.server
import os
import urllib.error
import urllib.request

parser = argparse.ArgumentParser()
# MTConnect agent we read the data from (another agent can be used with --agent)
parser.add_argument("--agent", default="https://demo.metalogi.io")
parser.add_argument("--port", type=int, default=8000)
args = parser.parse_args()
AGENT = args.agent.rstrip("/")
HERE = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def do_GET(self):
        if not self.path.startswith("/mtc/"):
            return super().do_GET()  # normal files: index.html

        # The agent does not allow other websites to read its data (no CORS).
        # So the page asks this server (/mtc/...) and the server asks the agent,
        # e.g. /mtc/probe -> https://demo.metalogi.io/probe
        url = AGENT + self.path[len("/mtc"):]
        req = urllib.request.Request(url, headers={"Accept": self.headers.get("Accept", "*/*")})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body, status, ctype = r.read(), r.status, r.headers.get("Content-Type", "application/json")
        except urllib.error.HTTPError as e:
            body, status, ctype = e.read(), e.code, e.headers.get("Content-Type", "application/json")
        except Exception as e:
            body, status, ctype = str(e).encode(), 502, "text/plain"

        # Send the agent answer back to the page (same address, so the browser accepts it)
        try:
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the browser tab was closed

    def log_message(self, fmt, *a):
        if not self.path.startswith("/mtc/") or " 200 " not in (fmt % a):
            super().log_message(fmt, *a)


if __name__ == "__main__":
    print(f"Twin:  http://localhost:{args.port}/")
    print(f"Agent: {AGENT}")
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError:
        # Port busy: the server is already running (Codespaces starts it automatically)
        print(f"Port {args.port} is already in use, so the server is already running.")
        print(f"Open http://localhost:{args.port}/  (Codespaces: Ports tab -> globe icon)")
        raise SystemExit(1)
    server.serve_forever()
