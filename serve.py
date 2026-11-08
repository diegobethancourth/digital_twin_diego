"""
Tiny local server for the CNC digital twin.

- Serves index.html from this folder.
- Forwards /mtc/<anything> to the MTConnect agent, so the browser sees one origin
  (many agents, including the Metalogi demo, do not send CORS headers).

Usage:
    python serve.py                                   # demo agent, port 8000
    python serve.py --agent http://192.168.1.50:5000  # any other agent
    python serve.py --port 8080

Then open http://localhost:8000/  (add ?device=NAME to pick a device).
Standard library only, no pip install needed.
"""
import argparse
import http.server
import os
import urllib.error
import urllib.request

parser = argparse.ArgumentParser(description="CNC twin server + MTConnect proxy")
parser.add_argument("--agent", default="https://demo.metalogi.io", help="MTConnect agent base URL")
parser.add_argument("--port", type=int, default=8000)
args = parser.parse_args()
AGENT = args.agent.rstrip("/")
HERE = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=HERE, **kw)

    def do_GET(self):
        if not self.path.startswith("/mtc/"):
            return super().do_GET()
        url = AGENT + self.path[len("/mtc"):]
        # pass the browser's Accept header (JSON for MTConnect requests, anything for CAD files)
        req = urllib.request.Request(url, headers={"Accept": self.headers.get("Accept", "*/*")})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                body, status, ctype = r.read(), r.status, r.headers.get("Content-Type", "application/json")
        except urllib.error.HTTPError as e:  # MTConnect errors still carry a JSON body
            body, status, ctype = e.read(), e.code, e.headers.get("Content-Type", "application/json")
        except Exception as e:
            body, status, ctype = str(e).encode(), 502, "text/plain"
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *a):  # keep the console quiet except for errors
        if not self.path.startswith("/mtc/") or " 200 " not in (fmt % a):
            super().log_message(fmt, *a)


if __name__ == "__main__":
    print(f"Twin:  http://localhost:{args.port}/")
    print(f"Agent: {AGENT}  (proxied at /mtc)")
    try:
        server = http.server.ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    except OSError:
        # Port busy: usually the server is already running (Codespaces starts it automatically)
        print(f"\nPort {args.port} is already in use, so the server is probably already running.")
        print(f"Just open http://localhost:{args.port}/  (in Codespaces: Ports tab -> globe icon on {args.port})")
        print(f"Or start another one with: python serve.py --port {args.port + 1}")
        raise SystemExit(1)
    server.serve_forever()
