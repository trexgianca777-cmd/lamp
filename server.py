#!/usr/bin/env python3
"""Legal Lights demo server. Python standard library only.

Serves the project directory and two API routes that run the real pipeline:
  POST /api/verdict  {"clause": "..."} -> one verdict.json
  POST /api/document {"text": "..."}   -> one panel.json
Launch with the swarm key in the environment (vault-loaded shell):
  source ~/workspace/freellmapi/vault/vault.sh && swarm_vault_load
  python3 server.py [port, default 8000]
Then open http://localhost:8000/
"""
import json, os, subprocess, sys, tempfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))


class H(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception as e:
            return self._send({"error": f"bad request: {e}"}, 400)
        try:
            with tempfile.TemporaryDirectory() as tmp:
                if self.path == "/api/verdict":
                    out = os.path.join(tmp, "v")
                    subprocess.run([sys.executable,
                                    os.path.join(HERE, "verdict.py"),
                                    "--clause", data["clause"], "--out", out],
                                   check=True, capture_output=True, text=True,
                                   timeout=300)
                    with open(os.path.join(out, "verdict.json")) as f:
                        return self._send(json.load(f))
                if self.path == "/api/document":
                    doc = os.path.join(tmp, "doc.txt")
                    with open(doc, "w") as f:
                        f.write(data["text"])
                    panel = os.path.join(tmp, "panel.json")
                    subprocess.run([sys.executable,
                                    os.path.join(HERE, "run_document.py"),
                                    "--doc", doc, "--out", panel],
                                   check=True, capture_output=True, text=True,
                                   timeout=900)
                    with open(panel) as f:
                        return self._send(json.load(f))
            return self._send({"error": "unknown route"}, 404)
        except subprocess.TimeoutExpired:
            return self._send({"error": "model call timed out"}, 504)
        except subprocess.CalledProcessError as e:
            return self._send({"error": "pipeline failed",
                               "detail": (e.stderr or "")[-500:]}, 500)
        except Exception as e:
            return self._send({"error": str(e)}, 500)


if __name__ == "__main__":
    os.chdir(HERE)
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
