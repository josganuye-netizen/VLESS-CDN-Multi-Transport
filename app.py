import json, os, subprocess, uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

CONFIG_PATH = "/app/config.json"
DOMAIN = os.environ.get("DOMAIN", "wokcandy.vall.cc.cd")

def load_clients():
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    return data["inbounds"][0]["settings"]["clients"]

def save_and_reload(clients):
    with open(CONFIG_PATH, "r") as f:
        data = json.load(f)
    for ib in data["inbounds"]:
        ib["settings"]["clients"] = clients
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)
    subprocess.run(["pkill", "xray"])
    subprocess.Popen(["xray", "run", "-c", CONFIG_PATH])

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        clients = load_clients()
        rows = ""
        for c in clients:
            uid = c["id"]
            name = c.get("email", "user")
            l_xhttp = f"vless://{uid}@{DOMAIN}:443?encryption=none&security=tls&sni={DOMAIN}&type=xhttp&host={DOMAIN}&path=%2Fxhttp&mode=auto#{name}-XHTTP"
            l_httpup = f"vless://{uid}@{DOMAIN}:443?encryption=none&security=tls&sni={DOMAIN}&type=httpupgrade&host={DOMAIN}&path=%2Fhttpup#{name}-HTTPUp"
            l_ws = f"vless://{uid}@{DOMAIN}:443?encryption=none&security=tls&sni={DOMAIN}&type=ws&host={DOMAIN}&path=%2Fvless#{name}-WS"
            rows += f"""
            <div class="card">
              <div class="top"><b>{name}</b><form method="POST" action="/delete" style="margin:0">
              <input type="hidden" name="id" value="{uid}"><button class="del">Hapus</button></form></div>
              <small>{uid}</small>
              <div class="btns">
                <button onclick="copy('{l_xhttp}')">Copy XHTTP</button>
                <button onclick="copy('{l_httpup}')">Copy HTTPUp</button>
                <button onclick="copy('{l_ws}')">Copy WS</button>
              </div>
            </div>"""

        html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
        <style>body{{background:#0f172a;color:#f8fafc;font-family:sans-serif;padding:16px;max-width:540px;margin:auto}}
        .box{{background:#1e293b;padding:16px;border-radius:12px;margin-bottom:16px}}
        input{{width:68%;padding:10px;border-radius:8px;border:none}}
        .add{{width:29%;padding:10px;border-radius:8px;border:none;background:#22c55e;color:#fff;font-weight:bold}}
        .card{{background:#1e293b;padding:14px;border-radius:12px;margin-bottom:10px}}
        .top{{display:flex;justify-content:space-between;align-items:center}}
        small{{color:#94a3b8;word-break:break-all;display:block;margin:6px 0}}
        .btns{{display:flex;gap:6px}}.btns button{{flex:1;padding:8px;border:none;border-radius:6px;background:#3b82f6;color:#fff;font-size:12px}}
        .del{{background:#ef4444;color:#fff;border:none;padding:5px 10px;border-radius:6px;font-size:12px}}</style></head>
        <body><h3>Xray Simple UI ({DOMAIN})</h3>
        <div class="box"><form method="POST" action="/add">
        <input type="text" name="name" placeholder="Nama akun (misal: hp1)" required>
        <button class="add" type="submit">+ Buat</button></form></div>
        {rows}
        <script>function copy(t){{navigator.clipboard.writeText(t);alert('Link berhasil disalin!');}}</script>
        </body></html>"""
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = parse_qs(self.rfile.read(length).decode())
        clients = load_clients()
        if self.path == "/add":
            name = body.get("name", ["user"])[0].strip() or "user"
            clients.append({"id": str(uuid.uuid4()), "email": name})
            save_and_reload(clients)
        elif self.path == "/delete":
            uid = body.get("id", [""])[0]
            clients = [c for c in clients if c["id"] != uid]
            save_and_reload(clients)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

HTTPServer(("0.0.0.0", 2053), Handler).serve_forever()
